from django.contrib import admin

from companies.models import Founder, Company, Member, Admin, Cast, Rehearsal, Choreographer
from profiles.models import Conflict

# def unschedule_rehearsals(modeladmin, request, queryset):
#     queryset.update(is_scheduled=False)
# unschedule_rehearsals.short_description = "Unschedule Rehearsals"

def unschedule_casts(modeladmin, request, queryset):
    queryset.update(is_scheduled=False)
    queryset.update(rehearsal=None)

    for cast in queryset:
    	members = Member.objects.filter(cast=cast)
    	for mem in members:
    		r = mem.conflict_set.filter(description='Rehearsal')
    		r.delete()

unschedule_casts.short_description = "Unschedule Casts"

# Register your models here.
# class CompanyInline(admin.TabularInline):
#     model = Member.company.through

class AdminInline(admin.TabularInline):
	model = Admin
	extra = 2

class ConflictInline(admin.TabularInline):
	model = Conflict
	extra = 2

class MemberAdmin(admin.ModelAdmin):
    search_fields=['first_name', 'last_name', 'netid']
    inlines = [AdminInline, ConflictInline]
    # list_filter = ['company']

class RehearsalAdmin(admin.ModelAdmin):
	list_display = ['day_of_week', 'start_time', 'place']
	ordering = ['company', 'day_of_week', 'start_time', 'is_scheduled']
	list_filter = ['company']
	# actions = [unschedule_rehearsals]

class CastAdmin(admin.ModelAdmin):
	list_display = ['name', 'rehearsal', 'is_scheduled']
	ordering = ['company', 'name']
	list_filter = ['company']
	actions = [unschedule_casts]

admin.site.register(Founder)
admin.site.register(Company)
admin.site.register(Rehearsal, RehearsalAdmin)
admin.site.register(Cast, CastAdmin)
admin.site.register(Choreographer)
admin.site.register(Member, MemberAdmin)