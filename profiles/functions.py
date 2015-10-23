from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import HttpResponse
from django.core.exceptions import SuspiciousOperation, PermissionDenied

from companies.models import Company, Member, Admin, Cast, Rehearsal, Choreographer
from django.contrib.auth.models import User, Group

import urllib2
import json

from string import ascii_uppercase


# Function to make sure user has access to the company and profile they are trying to access
def memberAuth(request, company_name, member_name):
    # make sure group exists
    company = get_object_or_404(Company, name=company_name)

    if request.user.is_authenticated():
        if member_name == request.user.username:
            # make sure user is a part of the group they are trying to access
            if request.user.groups.filter(name=company_name).exists():
                return Member.objects.get(username=member_name)
        return None
    else:
        raise SuspiciousOperation

# Function to make sure user has admin access to the company and profile they are trying to access
def adminAuth(request, company_name, member_name):
    company = get_object_or_404(Company, name=company_name)

    if request.user.is_authenticated(): 
        if member_name == request.user.username:
            # make sure user is an admin of the company they are trying to access
            if Admin.objects.filter(member__username=member_name, company=company).exists():
                return Admin.objects.get(member__username=member_name, company=company)
        
        return None
    else:
        raise SuspiciousOperation

# Function to unschedule a companies rehearsals
def unscheduleRehearsals(company_name, rehearsals, casts):
    company = Company.objects.get(name=company_name)

    # print rehearsals, "\n", casts

    # unschedule any casts in list
    for cast in casts:
        cast.unschedule()

    # unschedule any rehearsals in list
    for rehearsal in rehearsals:
        rehearsal.is_scheduled = False
        rehearsal.save()

        associated_casts = Cast.objects.filter(company=company, rehearsal=rehearsal)
        for cast in associated_casts:
            cast.unschedule()

    company.has_schedule = False
    company.save()


    finalDict = {}
    finalDict["Rehearsals"] = rehearsals
    finalDict["Casts"] = casts

    return finalDict
    # totalCasts = Cast.objects.filter(company=company)
    # totalRehearsals = Rehearsal.objects.filter(company=company)

    # members = Member.objects.filter(groups__name=company.name)
    # for mem in members:
    #     conflicts = mem.conflict_set.filter(description__startswith="%s Rehearsal" % (company.name))
    #     for r in conflicts:
    #         r.delete()

    # choreographers = Choreographer.objects.filter(company=company)
    # for choreographer in choreographers:
    #     conflicts = choreographer.member.conflict_set.filter(description__startswith="%s Rehearsal" % (company.name))
    #     for r in conflicts:
    #         r.delete()

    # for cast in totalCasts:
    #     cast.is_scheduled = False
    #     cast.rehearsal = None
    #     cast.save()

    # for rehearsal in totalRehearsals:
    #     rehearsal.is_scheduled = False
    #     rehearsal.save()

    # rehearsal_list = []
    # cast_list = []

    # for rehearsal in rehearsals:
    #     rehearsal_list.append(Rehearsal.objects.get(id=rehearsal.id))
    # for cast in casts:
    #     cast_list.append(Cast.objects.get(id=cast.id))

    # finalDict = {}
    # finalDict["Rehearsals"] = rehearsal_list
    # finalDict["Casts"] = cast_list

    # company.has_schedule = False
    # company.save()

    # return finalDict

# Functions for parsing PAC schedule
# =====================================
def get_json(format, calID, day):
    #Adsf
    url = 'https://spreadsheets.google.com/feeds/%s/%s/%d/public/basic?prettyprint=true&alt=json' % (format, calID, day);
    response = urllib2.urlopen(url)
    html = response.read()
    return json.loads(html)

def get_col_headers(html):
    COL_MAX = 'J'
    ROW_MAX = '31'
    columns = ascii_uppercase.split(chr(ord(COL_MAX)+1))[0]

    format = []
    for entry in html['feed']['entry']:
        # print entry['title']['$t'].encode('utf-8').strip()
        if len(entry['title']['$t'].encode('utf-8').strip()) == 2 and entry['title']['$t'].encode('utf-8').strip().endswith('1'):
            format.append(entry['content']['$t'].encode('utf-8').strip())

    return format

def getRowValue(row, format, column_name):
    # change column name to match name in json representation
    column_name = column_name.lower().replace(' ', '')
    
    if str(column_name) == '':
        raise ValueError('column_name must not empty')
        
    begin = row.find('%s:' % column_name)
           
    if begin == -1:
        return ''

    # get the beginning index for the resulting value
    begin = begin + len(column_name) + 1
    
    # get the ending index for the resulting value
    end = -1
    split_line = row.split(column_name)
    end_val = split_line[1].split(",", 1) 
    end += len(end_val[0])

    if end == -1:
        end = len(row)
    else:
        end = end + begin
        
    value = row[begin: end].strip()    

    return value

# -----------------------------------------
@login_required
def profileAuth(request, company_name, member_name):
    company = get_object_or_404(Company, name=company_name)

    # user must come from profile page to get here... don't need to reauthenticate
    if request.user.is_authenticated() and member_name == request.user.username:
        try:
            member = company.member_set.get(netid=member_name)
        except (KeyError, Member.DoesNotExist):
            return redirect('profiles:profile', company_name, member_name,)
        else:
            pass
    else:
        return redirect('profiles:profile', company_name, member_name,)
