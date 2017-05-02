"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from registration.backends.hmac.views import RegistrationView

from rides import views
from rides.forms import RegistrationForm, AppointmentForm

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^home', views.home, name='home'),
    url(r'^calendar', views.calendar, name='calendar'),
    url(r'^profile/', views.ProfileView.as_view(), name='profile'),
    url(r'^ride_request/(?P<ride_request_id>\d+)/(?P<action>accept|decline)/(?P<hash>[A-z0-9-_=]+)/$', views.RideRequestView.as_view(), name='ride_request'),
    url(r'^appointment/create/$', views.AppointmentCreateView.as_view(), name='appointment_create'),
    url(r'^appointment/(?P<appointment_id>\d+)/$', views.AppointmentView.as_view(), name='appointment_view'),
    url(r'^appointment/delete/(?P<appointment_id>\d+)/$', views.AppointmentDeleteView.as_view(), name='appointment_delete'),
    # url(r'^appointment/(?P<appointment_id>\d+)/(?P<action>accept|decline)/(?P<hash>[A-z0-9-_=]+)/$', views.AppointmentActionView.as_view(), name='appointment_action'),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/register/$',
        RegistrationView.as_view(
            form_class=RegistrationForm
        ),
        name='registration_register',
        ),
    url(r'^accounts/', include('registration.backends.hmac.urls')),
]
