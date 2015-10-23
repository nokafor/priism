from django.conf.urls import patterns, include, url

from django.conf import settings
from django.conf.urls.static import static

from companies import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^accounts/login/', 'django_cas_ng.views.login'),
    url(r'accounts/logout$', 'django_cas_ng.views.logout'),
    url(r'logout/$', views.logout_view, name='logout_view'),
    url(r'signup/$', views.signup, name='signup'),
    url(r'signup/successful/$', views.create_new, name="create_new"),
    url(r'^login/(?P<company_name>[\w\ ]+)/', views.userLogin, name='login'),
    url(r'^m/(?P<company_name>[\w\ ]+)/$', views.modal, name='modal'),
    url(r'^(?P<company_name>[\w\ ]+)/$', views.detail, name='detail'),
    
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)