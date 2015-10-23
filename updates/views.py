# from django.core.files import File

from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

from companies.models import Company, Member, Admin, Rehearsal, Cast, Choreographer, TimeBlock
from profiles.models import Conflict
# from updates.forms import ConflictForm, RehearsalForm, CastForm, MemberForm, MemberNameForm, ChoreographerForm
from updates.forms import RehearsalForm, ConflictForm, CastForm, CastingForm, PersonalForm, CompanyForm

from django.views.generic import DetailView
from django.template.loader import render_to_string

from profiles.functions import memberAuth, adminAuth, unscheduleRehearsals

from django.contrib.auth.models import Group, User

from datetime import datetime
import time


# Create your views here.
class ConflictView(DetailView):
    model = Member
    template_name = 'updates/conflicts.html'

class RehearsalView(DetailView):
    model = Cast
    template_name = 'updates/availableRehearsals.html'

class CastView(DetailView):
    model = Rehearsal
    template_name = 'updates/available.html'

def updateSettings(request, company_name, member_name):
    member = memberAuth(request, company_name, member_name)
    if member:
        company = Company.objects.get(name=company_name)
        if request.method == 'POST':
            print request.POST['form_type']
            if request.POST['form_type'] == 'personal':
                form = PersonalForm(request.POST, instance=member)
                # print request.POST['old_password']
                if member.has_usable_password():
                    user = User.objects.get(username=member.username)
                    if user.check_password(request.POST['old_password']):
                        if request.POST['new_password']:
                            print request.POST['new_password']
                            # user.set_password(mem.password)
                            # user.save()
                    else:
                        return HttpResponse('Entered an invalid password. Please go back and try again')

            else:
                form = CompanyForm(request.POST, instance=company)
            if form.is_valid():
                form.save()

        
    return redirect('profiles:settings', company_name, member_name,)

def addCast(request, company_name, member_name):
    admin = adminAuth(request, company_name, member_name)

    if admin:
        company = Company.objects.get(name=company_name)

        if request.method == 'POST':
            cast_list = request.POST['cast_list']
            cast_list = [l for l in cast_list.split("\n") if l]

            # initialize error message for any processing errors
            error_message = "The following casts could not be created:"

            for name in cast_list:

                # make sure there is not already a cast with that name
                if Cast.objects.filter(name=name, company=company).exists():
                    error = "\n" + name + " (Already a cast in this company with this title)"
                    error_message += error
                    continue
                cast = Cast(company=company, name=name)
                cast.save()
            
            # print any errors
            if "\n" in error_message:
                print error_message
        return redirect('profiles:casts', company_name, member_name,)

    else:
        raise PermissionDenied

def updateCastName(request, company_name, member_name, cast_id):
    name = 'updates:updateCastName'

    # check if valid admin
    admin = adminAuth(request, company_name, member_name)
    if admin:
        company = Company.objects.get(name=company_name)
        member = admin.member

        if Cast.objects.filter(id=cast_id).exists():
            cast = Cast.objects.get(id=cast_id)

            # save casting data
            if request.method == 'POST':
                form = CastForm(request.POST, instance=cast)
                if form.is_valid():
                    form.save()
                    return redirect('profiles:casts', company_name, member_name,)
            else:
                form = CastForm(instance=cast)
            return render(request, 'updates/update.html', {'company':company, 'member':member, 'curr':cast, 'form':form, 'redirect_name':name})

        return redirect('profiles:casts', company_name, member_name,)

    else:
        raise PermissionDenied

def addChoreographer(request, company_name, member_name, cast_id):
    admin = adminAuth(request, company_name, member_name)
    if admin:
        company = Company.objects.get(name=company_name)
        if Cast.objects.filter(id=cast_id).exists():
            cast = Cast.objects.get(id=cast_id)

            if request.method == 'POST':
                form = CastingForm(request.POST, company_name=company_name)
                if form.is_valid():
                    members = form.cleaned_data['members']
                    for member in members:
                        new_choreographer = Choreographer(company=company, cast=cast, member=member)
                        new_choreographer.save()

        return redirect('profiles:casts', company_name, member_name,)

    else:
        raise PermissionDenied

def addCastMem(request, company_name, member_name, cast_id):
    admin = adminAuth(request, company_name, member_name)
    if admin:
        company = Company.objects.get(name=company_name)
        if Cast.objects.filter(id=cast_id).exists():
            cast = Cast.objects.get(id=cast_id)

            if request.method == 'POST':
                form = CastingForm(request.POST, company_name=company_name)
                if form.is_valid():
                    members = form.cleaned_data['members']
                    for member in members:
                        cast.member_set.add(member)

        return redirect('profiles:casts', company_name, member_name,)

    else:
        raise PermissionDenied

def deleteCastMem(request, company_name, member_name, cast_id, mem_id):
    # check if valid admin
    admin = adminAuth(request, company_name, member_name)
    if admin:
        if Cast.objects.filter(id=cast_id).exists() and Member.objects.filter(id=mem_id).exists():
            cast = Cast.objects.get(id=cast_id)
            mem = Member.objects.get(id=mem_id)
            cast.member_set.remove(mem)

        return redirect('profiles:casts', company_name, member_name,)
    else:
        raise PermissionDenied

def addAdmin(request, company_name, member_name, member_id):
    # check if valid admin
    admin = adminAuth(request, company_name, member_name)
    if admin:
        company = Company.objects.get(name=company_name)
        member = Member.objects.get(username=member_name)
        
        # get post data if available
        mem = Member.objects.get(id=member_id)

        if not Admin.objects.filter(member=mem, company=company).exists():
            new_admin = Admin(member=mem, company=company)
            new_admin.save()

        return redirect('profiles:members', company_name, member_name,)

    else:
        raise PermissionDenied
        

def addStudents(request, company_name, member_name):
    admin = adminAuth(request, company_name, member_name)
    if admin:
        company = Company.objects.get(name=company_name)

        if request.method == 'POST':
            # check if there are any 'students' being inputted
            student_list = request.POST['student_list']
            student_list = [l for l in student_list.split("\n") if l]

            # initialize error message for any processing errors
            error_message = "The following lines could not be processed:"

            for line in student_list:
                info = line.split()

                # make sure line is specified length
                if len(info) != 3:
                    error = "\n" + line + " (Each line should have exactly 3 words)"
                    error_message += error
                    continue

                # check to see if you have email or username
                if '@' in info[0]:
                    email = info[0].split('@')
                    if email[1].lower() != 'princeton.edu':
                        # print line
                        error = "\n" + line + " (First word in line must be a NetID or a valid Princeton email address)"
                        error_message += error
                        continue
                    username = email[0]
                else:
                    username = info[0]

                print username, info[1], info[2]

                # check if the member already exists
                if Member.objects.filter(username=username).exists():
                    member = Member.objects.get(username=username)
                    # check if there is a  member with the same username in this group
                    if member.groups.filter(name=company_name).exists():
                        # print "checkpoint2"
                        # if student
                        if not member.has_usable_password():
                            error = "\n" + line + " (There is already a member of this company with this username)"
                            error_message += error
                            continue
                        # if not student
                        else:
                            # change the 'nonstudents' username
                            member.username = "%s%s" % (username, Member.objects.count())
                            member.save()
                            # print member.username
                    
                    # if member is not a part of this group
                    else:
                        # add them to this company
                        member.groups.add(company)
                        member.save()
                        continue

                # add the member to the company
                mem = Member(username=username, first_name=info[1], last_name=info[2], email="%s@princeton.edu" % username)
                mem.set_unusable_password()
                mem.save()
                mem.groups.add(company)

            if "\n" in error_message:
                print error_message
        return redirect('profiles:members', company_name, member_name,)

    else:
        raise PermissionDenied

def deleteMember(request, company_name, member_name, member_id):
    # check if valid admin
    admin = adminAuth(request, company_name, member_name)
    if admin:
        if Member.objects.filter(id=member_id).exists():
            old_member = Member.objects.get(id=member_id)

            # make sure you can only delete people who are in your company
            if old_member.groups.filter(name=company_name).exists() and admin.member != old_member:
                # delete person from company set
                company = Company.objects.get(name=company_name)
                company.user_set.remove(old_member)

                # if user is a student and is no longer associated with any companies, remove them from system to clear space
                if not old_member.has_usable_password() and old_member.groups.all().count() == 0:
                    old_member.delete()

        return redirect('profiles:members', company_name, member_name,)

    else:
        raise PermissionDenied

        

def deleteCast(request, company_name, member_name, cast_id):
    admin = adminAuth(request, company_name, member_name)
    if admin:
        if Cast.objects.filter(id=cast_id).exists():
            cast = Cast.objects.get(id=cast_id)

            #unschedule the rehearsal, and delete the conflicts in cast mem
            rehearsal = cast.rehearsal
            rehearsal.is_scheduled = False
            rehearsal.save()

            members = Member.objects.filter(cast=cast)
            for mem in members:
                conflicts = mem.conflict_set.filter(description__endswith="(%s)" % (cast.name))
                for r in conflicts:
                    r.delete()
            
            choreographers = Choreographer.objects.filter(cast=cast)
            for choreographer in choreographers:
                conflicts = choreographer.member.conflict_set.filter(description__endswith="(%s)" % (cast.name))
                for r in conflicts:
                    r.delete()

            cast.delete()

            # check to see if company has any more casts
            casts = Cast.objects.filter(company__name=company_name)
            if len(casts) == 0:
                company = Company.objects.get(name=company_name)
                company.has_schedule = False
                company.save()

        return redirect('profiles:casts', company_name, member_name,)
    else:
        raise PermissionDenied

def deleteChoreographer(request, company_name, member_name, choreographer_id):
    admin = adminAuth(request, company_name, member_name)
    if admin:
        if Choreographer.objects.filter(id=choreographer_id).exists():
            choreographer = Choreographer.objects.get(id=choreographer_id)
            choreographer.delete()

        return redirect('profiles:casts', company_name, member_name,)
    else:
        raise PermissionDenied

def deleteAdmin(request, company_name, member_name):
    # check if valid admin
    admin = adminAuth(request, company_name, member_name)
    if admin:
        admin.delete()

        return redirect('profiles:profile', company_name, member_name,)
    else:
        raise PermissionDenied

def updateName(request, company_name, member_name):
    # make sure member has access to this profile
    member = memberAuth(request, company_name, member_name)

    if member:
        company = Company.objects.get(name=company_name)

        # process the form and update user's name
        if request.method == 'POST':
            form = MemberNameForm(request.POST, instance=member)
            if form.is_valid():
                form.save()

                return redirect('profiles:profile', company_name, member_name,)
        else:
            form = MemberNameForm(instance=member)
        
        if member.first_name:
            header = 'Edit Name'
            return render(request, 'profiles/name.html', {'company':company, 'member':member, 'form':form, 'dismiss':"modal", 'header':header})
        else:
            header = 'Enter Name Before Continuing'
            return render(request, 'profiles/name.html', {'company':company, 'member':member, 'form':form, 'dismiss':"", 'header':header})

    else:
        return redirect('profiles:profile', company_name, member_name,)

def addConflicts(request, company_name, member_name):
    member = memberAuth(request, company_name, member_name)
    if member:
        company = Company.objects.get(name=company_name)

        if request.method == 'POST':
            conflicts = request.POST['conflicts']
            conflicts = [l for l in conflicts.split("\n") if l]
            print conflicts

            # initialize error message for any processing errors
            error_message = "The following conflicts could not be processed:"

            for line in conflicts:
                info = line.split()
                print info

                # make sure line is specified length
                if len(info) != 4:
                    error = "\n" + line +  " (Each line should have exactly 4 words)"
                    # print error
                    error_message += error
                    continue

                # check start time
                try:
                    start = datetime.strptime(info[2], "%I:%M%p")
                    print start.time()

                    end = datetime.strptime(info[3], "%I:%M%p")
                    print end.time()
                except ValueError:
                    error = "\n" + line + " (Does not contain valid time parameters)"
                    error_message += error
                    continue

                # get day of week information
                dow = time.strptime(info[1], "%A").tm_wday

                conflict = Conflict(member=member, description=info[0], day_of_week=TimeBlock.DAY_OF_WEEK_CHOICES[dow][0], start_time=start.time(), end_time=end.time())
                conflict.save()
                # print rehearsal
            if "\n" in error_message:
                print error_message
        return redirect('profiles:conflicts', company_name, member_name,)
    else:
        raise PermissionDenied

def updateConflict(request, company_name, member_name, conflict_id):
    name = 'updates:updateConflict'
    
    # check if valid member
    member = memberAuth(request, company_name, member_name)
    if member:
        company = Company.objects.get(name=company_name)
        
        if member.conflict_set.filter(id=conflict_id).exists():
            conflict = member.conflict_set.get(id=conflict_id)
                    
            # process the form and rehearsal data
            if request.method == 'POST':
                form = ConflictForm(request.POST, instance=conflict)
                if form.is_valid():
                    form.save()

                    return redirect('profiles:conflicts', company_name, member_name,)
            else:
                form = ConflictForm(instance=conflict)
            return render(request, 'updates/update.html', {'company':company, 'member':member, 'curr':conflict, 'form':form, 'redirect_name':name})
        return redirect('profiles:conflicts', company_name, member_name,)
    else:
        raise PermissionDenied

def deleteConflict(request, company_name, member_name, conflict_id):
    # check if came from profile
    member = memberAuth(request, company_name, member_name)
    if member:
        company = Company.objects.get(name=company_name)

        if member.conflict_set.filter(id=conflict_id).exists():
            conflict = member.conflict_set.get(id=conflict_id)
            conflict.delete()

        return redirect('profiles:conflicts', company_name, member_name,)
    else:
        raise PermissionDenied

def addRehearsals(request, company_name, member_name):
    admin = adminAuth(request, company_name, member_name)
    if admin:
        company = Company.objects.get(name=company_name)

        if request.method == 'POST':
            rehearsals = request.POST['rehearsals']
            rehearsals = [l for l in rehearsals.split("\n") if l]
            print rehearsals

            # initialize error message for any processing errors
            error_message = "The following rehearsals could not be processed:"

            for line in rehearsals:
                info = line.split()
                print info

                # make sure line is specified length
                if len(info) != 4:
                    error = "\n" + line + " (Each line should have exactly 4 words)"
                    error_message += error
                    continue

                # check start time
                try:
                    start = datetime.strptime(info[2], "%I:%M%p")
                    print start.time()

                    end = datetime.strptime(info[3], "%I:%M%p")
                    print end.time()
                except ValueError:
                    error = "\n" + line + " (Does not contain valid time parameters)"
                    error_message += error
                    continue

                # get day of week information
                dow = time.strptime(info[1], "%A").tm_wday

                rehearsal = Rehearsal(company=company, place=info[0], day_of_week=TimeBlock.DAY_OF_WEEK_CHOICES[dow][0], start_time=start.time(), end_time=end.time())
                rehearsal.save()
                # print rehearsal
            if "\n" in error_message:
                print error_message
        return redirect('profiles:spaces', company_name, member_name,)
    else:
        raise PermissionDenied

def updateRehearsal(request, company_name, member_name, rehearsal_id):
    name = 'updates:updateRehearsal'
    
    # check if valid admin
    admin = adminAuth(request, company_name, member_name)
    if admin:
        company = Company.objects.get(name=company_name)
        member = admin.member
        
        if company.rehearsal_set.filter(id=rehearsal_id).exists():
            rehearsal = company.rehearsal_set.get(id=rehearsal_id)
                    
            # process the form and rehearsal data
            if request.method == 'POST':
                form = RehearsalForm(request.POST, instance=rehearsal)
                if form.is_valid():
                    form.save()

                    return redirect('profiles:spaces', company_name, member_name,)
            else:
                form = RehearsalForm(instance=rehearsal)
            return render(request, 'updates/update.html', {'company':company, 'member':member, 'curr':rehearsal, 'form':form, 'redirect_name':name})
        return redirect('profiles:spaces', company_name, member_name,)
    else:
        raise PermissionDenied

def deleteRehearsal(request, company_name, member_name, rehearsal_id):
    # check if valid admin
    admin = adminAuth(request, company_name, member_name)
    if admin:
        company = Company.objects.get(name=company_name)

        if company.rehearsal_set.filter(id=rehearsal_id).exists():
            rehearsal = company.rehearsal_set.get(id=rehearsal_id)
            rehearsal.delete()

        return redirect('profiles:spaces', company_name, member_name,)
    else:
        raise PermissionDenied

def deleteSchedule(request, company_name, member_name):
    admin = adminAuth(request, company_name, member_name)
    if admin:
        unscheduleRehearsals(company_name, Rehearsal.objects.filter(company__name=company_name), Cast.objects.filter(company__name=company_name))
        return redirect('profiles:scheduling', company_name, member_name,)
    else:
        raise PermissionDenied
