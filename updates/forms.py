from companies.models import Company, Member, Admin, Rehearsal, Cast, Choreographer
from profiles.models import Conflict

from django.forms import ModelForm
from django import forms
from django_bootstrap_typeahead.fields import *
from django.contrib.auth.models import User
import json

# queryset = json.dumps([' '.join(value) for value in User.objects.filter(groups__isnull=True).exclude(username='admin').values_list('first_name', 'last_name', 'email')])
# Create your models here.
class UserForm(forms.Form):
    users = MultipleTypeaheadField(
        queryset = Member.objects.filter(groups__isnull=True).exclude(username='admin'),
        label="", help_text=""
    )

class RehearsalForm(forms.Form):
    rehearsals = MultipleTypeaheadField(
        queryset = Rehearsal.objects.all(),
        label="", help_text=""
    )
    def __init__(self, *args, **kwargs):
        company_name = kwargs.pop('company_name', None)
        super(RehearsalForm, self).__init__(*args, **kwargs)

        if company_name:
            self.fields['rehearsals'].queryset = Rehearsal.objects.filter(company__name=company_name, is_scheduled=False)

class CastingForm(forms.Form):
    members = MultipleTypeaheadField(
        queryset = Member.objects.all(),
        label="", help_text=""
    ) 
    def __init__(self, *args, **kwargs):
        company_name = kwargs.pop('company_name', None)
        super(CastingForm, self).__init__(*args, **kwargs)

        if company_name:
            self.fields['members'].queryset = Member.objects.filter(groups__name=company_name)

class SchedulingForm(forms.Form):
    rehearsals = MultipleTypeaheadField(
        queryset = Rehearsal.objects.all(),
        label="", help_text=""
    ) 
    casts = MultipleTypeaheadField(
        queryset = Cast.objects.all(),
        label="", help_text=""
    ) 
    def __init__(self, *args, **kwargs):
        rehearsals = kwargs.pop('rehearsals', None)
        casts = kwargs.pop('casts', None)
        super(SchedulingForm, self).__init__(*args, **kwargs)

        if rehearsals and casts:
            self.fields['rehearsals'].queryset = Rehearsal.objects.filter(id__in=rehearsals)
            self.fields['casts'].queryset = Cast.objects.filter(id__in=casts)

class UploadFileForm(forms.Form):
    file = forms.FileField(label="", help_text="")
    
class CompanyForm(ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'listserv', 'short_description', 'logo']

class PersonalForm(ModelForm):
    class Meta:
        model = Member
        fields = ['first_name', 'last_name', 'email']

class AdminForm(ModelForm):
    class Meta:
        model = Admin
        fields = ['member']
    def __init__(self, *args, **kwargs):
        super(AdminForm, self).__init__(*args, **kwargs)
        if self.instance:
             self.fields['member'].queryset = Member.objects.filter(company=self.instance.company).order_by('first_name', 'username')

class ChoreographerForm(ModelForm):
    class Meta:
        model = Choreographer
        fields = ['member']
    def __init__(self, *args, **kwargs):
        super(ChoreographerForm, self).__init__(*args, **kwargs)
        if self.instance:
             self.fields['member'].queryset = Member.objects.filter(company=self.instance.company).order_by('first_name', 'username')

class ConflictForm(ModelForm):
    class Meta:
        model = Conflict
        fields = ['description', 'day_of_week', 'start_time', 'end_time']

# class RehearsalForm(ModelForm):
#     class Meta:
#         model = Rehearsal
#         fields = ['place', 'day_of_week', 'start_time', 'end_time']

class CastForm(ModelForm):
    class Meta:
        model = Cast
        fields = ['name']