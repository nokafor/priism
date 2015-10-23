import random

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import PermissionDenied

from companies.models import Company, Member, Admin, Rehearsal, Cast, Choreographer, TimeBlock, Founder
from profiles.models import Conflict
from updates.forms import PersonalForm, UserForm, CastingForm, CompanyForm, SchedulingForm, RehearsalForm

from profiles.functions import memberAuth, adminAuth, getRowValue, get_json, get_col_headers, unscheduleRehearsals
from django.contrib.auth.models import User, Group

from datetime import datetime, timedelta
from django.utils import timezone

DOWs = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

# Create your views here.
def settings(request, company_name, member_name):
    # return render(request, '404.html')
    member = memberAuth(request, company_name, member_name)
    if member:
        company = Company.objects.get(name=company_name)
        admin = adminAuth(request, company_name, member_name)
        choreographer = Choreographer.objects.filter(member=member, company=company).exists()

        personal_form = PersonalForm(instance=member)
        company_form = CompanyForm(instance=company)
        return render(request, 'profiles/settings.html', {'company': company, 'member':member, 'admin':admin, 'choreographer':choreographer, 'personal_form':personal_form, 'company_form':company_form})
    else:
        return redirect('profiles:profile', company_name, member_name,)

def parsePAC(request, company_name, member_name):
    if request.method == 'POST':
        admin = adminAuth(request, company_name, member_name)
        if admin:
            company = Company.objects.get(name=company_name)
            pub_url = request.POST['url']
            # print pub_url

            split_string = pub_url.split("d/")
            # print split_string

            calID = split_string[1].split('/')[0]
            # print calID

            # get info for each day of the week
            for day in range(1,8):
            # day = 6
                # JSON Representation to get headers
                html = get_json('cells', calID, day)
                format = get_col_headers(html)

                # JSON Representation to get data
                html = get_json('list', calID, day)

                dow = html['feed']['title']['$t'].encode('utf-8').strip()
                print dow[0:3]
                print '========================='
                last_company = {}
                for name in format:
                    last_company[name] = ['', -1]

                rehearsals = []
                rehearsals_index = 0

                for entry in html['feed']['entry']:
                    row = entry['content']['$t'].encode('utf-8').strip()
                    time = entry['title']['$t'].encode('utf-8').strip()

                    for name in format:
                        result = getRowValue(row, format, name)
                        # print "%s, %s:%s" % (time, name, result)
                        # print result
                        # print result, last_company[name]
                        if result != last_company[name][0]:
                            index = last_company[name][1]
                            if index != -1:
                                t = time.split('-')[0]
                                end = datetime.strptime(t, "%I:%M%p")
                                rehearsals[index].end_time = end.time()
                                last_company[name][1] = -1
                                # print 'add end time to rehearsal in %s' % name

                            if company_name in result:
                                #create new rehearsal
                                t = time.split('-')[0]
                                start = datetime.strptime(t, "%I:%M%p")
                                rehearsal = Rehearsal(company=company, day_of_week=dow[0:3], place=name, start_time=start.time())
                                # print rehearsal, rehearsals_index
                                #append to rehearsals
                                rehearsals.append(rehearsal)
                                last_company[name][1] = rehearsals_index
                                rehearsals_index += 1
                                
                                # print "create rehearsal"
                                # print start.time()

                            # print "Time:%s %s:%s" % (time, name, result)
                            last_company[name][0] = result

                # print rehearsals
                for rehearsal in rehearsals:
                    if rehearsal.end_time == None:
                        rehearsal.end_time = datetime.strptime('1:00am', "%I:%M%p").time()
                    print rehearsal
                    rehearsal.save()

    return redirect('profiles:spaces', company_name, member_name,)

def testing(request, company_name, member_name, date_string):
    member = memberAuth(request, company_name, member_name)
    if member:
        if request.method == 'POST':
            #
            description = request.POST['description']
            day_of_week = request.POST['dow']

            start = request.POST['startOptions'].split(", ")[2].replace(".", "")
            if ':' not in start:
                start = start.replace(" ", ":00 ")
            start_time = datetime.strptime(start, "%I:%M %p")
            # print start, start_time

            end = request.POST['endOptions'].split(", ")[2].replace(".", "")
            if ':' not in end:
                end = end.replace(" ", ":00 ")
            
            end_time = datetime.strptime(end, "%I:%M %p")

            conflict = Conflict(member=member, description=description, day_of_week=day_of_week, start_time=start_time.time(), end_time=end_time.time())
            conflict.save()

            # print description, day_of_week
            return redirect('profiles:conflicts', company_name, member_name,)
        else:
            event = date_string.replace("%20", " ").split('-')
            try:
                start_time = datetime.fromtimestamp(float(event[2])/1000.0)
                # start_time2 = datetime.fromtimestamp(float(event[2])/1000.0) + timedelta(minutes=float(event[3]))
                end_time = datetime.fromtimestamp(float(event[4])/1000.0)
                # end_time2 = datetime.fromtimestamp(float(event[4])/1000.0) + timedelta(minutes=float(event[5]))
                # print day_of_week, start_time, end_time

                return render(request, 'profiles/testing.html', {'company_name':company_name, 'member_name':member_name, 'start_time':start_time, 'end_time':end_time, 'dow':event[1], 'description':event[0]})
            except:
                return HttpResponse("Could not process your request")
    else:
        raise PermissionDenied

def addUsers(request, company_name, member_name):
    # create dataset for users (w/o valid netid)
    # dataset = []
    # results = User.objects.filter(groups__isnull=True).exclude(username='admin')
    # for user in results:
    #     dataset.append("%s %s (%s)" % (user.first_name, user.last_name, user.email))
    # print dataset
    admin = adminAuth(request, company_name, member_name)

    if admin:
        company = Company.objects.get(name=company_name)

        # get any users w/o valid netids that are being added
        if request.method == 'POST':
            form = UserForm(request.POST)

            if form.is_valid():
                members = form.cleaned_data['users']

                for member in members:
                    member.groups.add(company)
                    member.save()

            return redirect('profiles:members', company_name=company_name, member_name=member_name)

        form = UserForm()
        return render(request, 'profiles/addmembers.html', {'form':form, 'company_name': company_name, 'member_name':member_name})
    else:
        raise PermissionDenied

def updateDueDate(request, company_name, member_name, option):
    # make sure member is an admin and has the right to access this information
    admin = adminAuth(request, company_name, member_name)
    print option
    if admin:
        # save posted data if available
        if request.method == 'POST':
            company = Company.objects.get(name=company_name)
            if option == 'conflicts':
                try: 
                    valid_datetime = datetime.strptime(request.POST['datetimepicker4'], '%m/%d/%Y %I:%M %p')
                    company.conflicts_due = valid_datetime.replace(tzinfo=timezone.LocalTimezone())
                    company.save()
                    return redirect('profiles:profile', company_name=company_name, member_name=member_name)
                except ValueError:
                    return HttpResponse('You did not enter a valid date and time. So the information was not saved.')
            if option == 'casting':
                try: 
                    valid_datetime = datetime.strptime(request.POST['datetimepicker4'], '%m/%d/%Y %I:%M %p')
                    company.casting_due = valid_datetime.replace(tzinfo=timezone.LocalTimezone())
                    company.save()
                    return redirect('profiles:profile', company_name=company_name, member_name=member_name)
                except ValueError:
                    return HttpResponse('You did not enter a valid date and time. So the information was not saved.')
            return redirect('profiles:profile', company_name, member_name,)

        return render(request, 'profiles/datetimepicker.html', {'company_name':company_name, 'member_name':member_name, 'option':option})

    # admins and members logged in under the wrong name cannot access this page
    raise PermissionDenied
    

def profile(request, company_name, member_name):
    # make sure member has access to this profile
    member = memberAuth(request, company_name, member_name)

    if member:
        if not member.first_name:
            return redirect('profiles:settings', company_name, member_name,)
        company = Company.objects.get(name=company_name)
        admin = adminAuth(request, company_name, member_name)
    
        return render(request, 'profiles/hub.html', {'member':member, 'company':company, 'admin':admin})

    else:
        raise PermissionDenied

def members(request, company_name, member_name):
    # make sure member has access to this profile
    member = memberAuth(request, company_name, member_name)

    if member:
        company = Company.objects.get(name=company_name)
        member_list = Member.objects.filter(groups__name=company_name)
        admin_list = company.admin_set.all()

        admin = adminAuth(request, company_name, member_name)

        return render(request, 'profiles/members.html', {'company':company, 'member':member, 'member_list':member_list, 'admin_list':admin_list, 'admin':admin})

    else:
        raise PermissionDenied

def spaces(request, company_name, member_name):
    member = memberAuth(request, company_name, member_name)

    if member:
        company = Company.objects.get(name=company_name)
        admin = adminAuth(request, company_name, member_name)

        rehearsal_list = {}
        for rehearsal in company.rehearsal_set.all():
            try:
                rehearsal_list[rehearsal.day_of_week].append(rehearsal)
            # print rehearsal.day_of_week
            except KeyError:
                rehearsal_list[rehearsal.day_of_week] = []
                rehearsal_list[rehearsal.day_of_week].append(rehearsal)

        rehearsal_list = sorted(rehearsal_list.items(), key=lambda x: DOWs.index(x[0]))
        # print rehearsal_list
        # print rehearsal_list[0]

        return render(request, 'profiles/spaces.html', {'company':company, 'member':member, 'rehearsal_list':rehearsal_list, 'admin':admin})

    else:
        raise PermissionDenied

def conflicts(request, company_name, member_name):
    member = memberAuth(request, company_name, member_name)

    if member:
        company = Company.objects.get(name=company_name)
        founder = Founder.objects.get(id=1)

        # admin = adminAuth(request, company_name, member_name)

        conflict_list = {}
        for conflict in member.conflict_set.all():
            try:
                conflict_list[conflict.day_of_week].append(conflict)
            except KeyError:
                conflict_list[conflict.day_of_week] = []
                conflict_list[conflict.day_of_week].append(conflict)

        conflict_list = sorted(conflict_list.items(), key=lambda x: DOWs.index(x[0]))

        return render(request, 'profiles/conflicts.html', {'company':company, 'member':member, 'conflict_list':conflict_list, 'timeblock':TimeBlock, 'founder':founder})

    else:
        raise PermissionDenied

def casts(request, company_name, member_name):
    member = memberAuth(request, company_name, member_name)

    if member:
        company = Company.objects.get(name=company_name)
        admin = adminAuth(request, company_name, member_name)

        cast_list = Cast.objects.filter(company=company)
        choreographer_list = Choreographer.objects.filter(company=company)
        my_cast_list = Choreographer.objects.filter(company=company, member=member)
        # print my_cast_list
        # my_piece_list = member.cast.all()

        form = CastingForm(company_name=company_name)
        # form = UserForm()
        return render(request, 'profiles/casts.html', {'company':company, 'member':member, 'admin':admin, 'cast_list':cast_list, 'choreographer_list':choreographer_list, 'my_cast_list':my_cast_list, 'form':form})
    else:
        raise PermissionDenied

def scheduling(request, company_name, member_name):
    # check if valid admin
    member = memberAuth(request, company_name, member_name)
    if member:
        company = Company.objects.get(name=company_name)
        admin = adminAuth(request, company_name, member_name)
        # rehearsals = company.getSortedRehearsals()
        rehearsals = Rehearsal.objects.filter(company=company)

        casts = Cast.objects.filter(company=company)

        form = RehearsalForm(company_name=company_name)

        return render(request, 'profiles/schedule.html', {'company':company, 'member':member, 'admin':admin, 'cast_list':casts, 'rehearsal_list':rehearsals, 'form':form})
    else:
        raise PermissionDenied

def makeSchedule(request, company_name, member_name):
    admin = adminAuth(request, company_name, member_name)
    if admin:
        # get dict
        if request.method =='POST':
            form = SchedulingForm(request.POST)
            if form.is_valid():
                try:
                    if request.POST['override']:
                        override = True
                except Exception:
                    override = False

                print "Override:", override
                # get rehearsals and casts to be scheduled
                rehearsals = form.cleaned_data['rehearsals']
                casts = form.cleaned_data['casts']
                # print casts, "\n", rehearsals

                # if user elected to override rehearsals, unschedule any rehearsals that are already scheduled
                company = Company.objects.get(name=company_name)
                if override:
                    dict = unscheduleRehearsals(company_name, rehearsals, casts)
                    rehearsals = dict["Rehearsals"]
                    casts = dict["Casts"]
                
                # otherwise, remove any already scheduled casts from the list of casts to be scheduled
                else:
                    casts = casts.exclude(is_scheduled=True)

                for rehearsal in rehearsals:
                    print rehearsal.is_scheduled, rehearsal
                for cast in casts:
                    print cast.is_scheduled, cast

                print "======================"

                # save the casts that are scheduled
                scheduled_casts = []
                scheduled_rehearsals = []
                # begin scheduling casts
                for cast in casts:
                    print "\n\n"
                    # get all unscheduled rehearsals with least number of available casts (greater than 0)
                    min = len(Cast.objects.filter(company=company))
                    for rehearsal in rehearsals:
                        print rehearsal, rehearsal.is_scheduled
                        if rehearsal.is_scheduled == False:
                            n = len(rehearsal.getAvailableCasts())
                            print n, rehearsal
                            if n > 0 and n <= min:
                                min = n
                    print "Least # of available casts:\n", min

                    rehearsal_list = []
                    for rehearsal in rehearsals:
                        if rehearsal.is_scheduled == False and len(rehearsal.getAvailableCasts()) == min:
                            rehearsal_list.append(rehearsal)

                    print "Unscheduled rehearsals with least # of available casts:\n", rehearsal_list
                    # if rehearsal_list == []:
                    #     company.has_schedule = False
                    #     unscheduleRehearsals(company_name, scheduled_rehearsals, scheduled_casts)
                    #     company.save()
                    #     return HttpResponse("Could not complete scheduling. <p>Please return to the <a href='/%s/%s/schedule'>scheduling page</a> to unschedule rehearsals / overwrite old schedule in order to complete this scheduling request.</p>" % (company_name, member_name))


                    # get all unscheduled casts available during rehearsals above
                    # pick the ones with least number of available rehearsals
                    min = len(Rehearsal.objects.filter(company=company))
                    print min
                    for rehearsal in rehearsal_list:
                        available_casts = rehearsal.getAvailableCasts()
                        for cast in available_casts:
                            if cast in casts:
                                print cast.is_scheduled, cast
                                if cast.is_scheduled == False:
                                    n = len(cast.getAvailableRehearsals())
                                    if n > 0 and n <= min:
                                        print n, cast
                                        min = n

                    print "Least # of available rehearsals\n", min

                    # create scheduling options for casts with min number found above
                    options = {}
                    for rehearsal in rehearsal_list:
                        available_casts = rehearsal.getAvailableCasts()
                        for cast in available_casts:
                            if cast in casts:
                                if cast.is_scheduled == False and len(cast.getAvailableRehearsals()) == min:
                                    try:
                                        options[cast].append(rehearsal)
                                    except:
                                        options[cast] = []
                                        options[cast].append(rehearsal)

                    print "Scheduling options based on rehearsals and casts above:\n", options

                    if options != {}:
                        # randomly pick a cast from the options
                        cast = random.choice(options.keys())

                        print "Randomly chosen cast:\n", cast

                        rehearsal = random.choice(options[cast])
                        print "Randomly chosen rehearsal:\n", rehearsal

                        # print cast
                        # print options[cast]


                        # schedule the cast to its respective rehearsal
                        cast.scheduleRehearsal(rehearsal)
                        rehearsal.is_scheduled = True
                        cast.save()
                        rehearsal.save()

                        scheduled_casts.append(cast)
                        scheduled_rehearsals.append(rehearsal)

                        print "Is cast scheduled?"
                        print cast.is_scheduled

                    else:
                        # if cannot complete schedule for some reason
                        unscheduleRehearsals(company_name, scheduled_rehearsals, scheduled_casts)
                        if override:
                            company.has_schedule = False
                        company.save()
                        return HttpResponse("Something went wrong! Could not complete schedule. <p>Please make sure the rehearsal(s)/cast(s) you are trying to schedule are not already scheduled. If rehearsal(s)/cast(s) are free, please ask members to adjust their conflicts.</p><a href='/%s/%s'>Return to Hub</a> or <a href='/%s/%s/schedule'>Return to Scheduling</a>" % (company_name, member_name, company_name, member_name))
                        # return HttpResponse("Something went wrong! Could not complete schedule. <p>Make sure you are not trying to schedule casts for rehearsal times that all cast members cannot make (the schedule will not allow this). If you would like to schedule a cast for a specific rehearsal time, regardless of conflicts, please ask members to adjust their conflicts, then return to the <a href='/%s/%s/schedule'>scheduling page</a> to re-schedule the %s rehearsal(s)/cast(s)</p>" % (company_name, member_name, company_name))

                company.has_schedule = True
                company.save()

        return redirect('profiles:scheduling', company_name, member_name,)

    else:
        raise PermissionDenied

def confirmSchedule(request, company_name, member_name):
    admin = adminAuth(request, company_name, member_name)
    if admin:
        if request.method == 'POST':
            # get cast and rehearsal lists
            rehearsals = request.POST.getlist('rehearsals')
            casts = request.POST.getlist('casts')

            rehearsal_list = []
            cast_list = []

            for rehearsal_id in rehearsals:
                rehearsal = Rehearsal.objects.get(id=rehearsal_id)
                rehearsal_list.append(rehearsal)

            for cast_id in casts:
                cast = Cast.objects.get(id=cast_id)
                cast_list.append(cast)

            errors = []
            warnings = []

            # check lengths
            if len(rehearsals) == 0:
                error = "You must select at least one rehearsal to be scheduled."
                errors.append(error)
            if len(casts) == 0:
                error = "You must select at least one cast to be scheduled."
                errors.append(error)
            if len(rehearsals) < len(casts):
                error = "In order to create a schedule, there must be at least as many rehearsals as casts. Right now you have more casts than rehearsals."
                errors.append(error)

            # # make sure availabeRehearsals >0 for all casts
            cast_error = ""
            cast_warning = ""
            for cast in cast_list:
                if len(cast.getAllRehearsals()) == 0:
                    c = " - " + cast.name
                    cast_error += c
                if cast.is_scheduled:
                    c = " - " + cast.name
                    cast_warning += c

            if '-' in cast_error:
                cast_error += ' -'
                errors.append("The following casts are not available for any rehearsals and cannot be scheduled:")
                errors.append(cast_error)
                errors.append('Consider asking members of the cast to adjust their conflicts.')
            if '-' in cast_warning:
                cast_warning += ' -'
                warnings.append("The following casts are currently scheduled for a rehearsal, and may not be scheduled unless you overwrite the current schedule.")
                warnings.append(cast_warning)
                warnings.append("If you would like to schedule an additional rehearsal for this cast, please do so from the scheduling page.")

            # make sure availabeCasts >0 for all rehearsals
            rehearsal_error = ""
            rehearsal_warning = ""
            for rehearsal in rehearsal_list:
                if len(rehearsal.getAllCasts()) == 0:
                    r = " - " + rehearsal.place + ", " + str(rehearsal.start_time) + " (" + rehearsal.day_of_week + ")"
                    rehearsal_error += r
                if rehearsal.is_scheduled:
                    r = " - " + rehearsal.place + ", " + str(rehearsal.start_time) + " (" + rehearsal.day_of_week + ")"
                    rehearsal_warning += r

            if '-' in rehearsal_error:
                rehearsal_error += ' -'
                errors.append("The following rehearsals do not work for any casts and cannot be scheduled:")
                errors.append(rehearsal_error)
                errors.append('Consider contacting PAC or switching rehearsal spaces with another company.')
            if '-' in rehearsal_warning:
                rehearsal_warning += ' -'
                warnings.append("The following rehearsals are currently assigned to a cast, and may not be scheduled unless you overwrite / delete the current schedule.")
                warnings.append(rehearsal_warning)

            # print errors
            if errors == []:
                errors = None

                # get the associated rehearsals and casts
                finalDict = {}
                finalDict["Rehearsals"] = rehearsal_list
                finalDict['Casts'] = cast_list

                # create scheduling form
                form = SchedulingForm(rehearsals=rehearsals, casts=casts)



            else:
                finalDict = None
                form = None

            if warnings == []:
                warnings = None

            # return render(request, 'profiles/makeschedule.html', {'company':company, 'member':admin.member, 'make_schedule':make_schedule})
            # print errors, finalDict


    
    # return redirect('profiles:scheduling', company_name, member_name,)
    return render(request, 'profiles/confirmschedule.html', {'company_name':company_name, 'member_name':member_name, 'errors':errors, 'warnings':warnings, 'dict':finalDict, 'form':form})



