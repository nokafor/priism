from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    #url(r'^$', include('companyMembers.urls', namespace="companyMembers")),
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('companies.urls', namespace="companies")),
    url(r'^(?P<company_name>[\w\ ]+)/(?P<member_name>\w+)/update/', include('updates.urls', namespace="updates")),
    url(r'^(?P<company_name>[\w\ ]+)/(?P<member_name>\w+)/', include('profiles.urls', namespace="profiles")),
    
)