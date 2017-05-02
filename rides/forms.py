from registration.forms import RegistrationForm as BaseRegistrationForm
from django.contrib.admin import widgets
from datetimewidget.widgets import DateTimeWidget
from django import forms

from rides.models import Yalie, Appointment
from rides.widgets import DateInput


class RegistrationForm(BaseRegistrationForm):
    class Meta(BaseRegistrationForm.Meta):
        model = Yalie


# TODO select date, then range, then time
class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        widgets = {
            'desired_time': DateInput(attrs={'class':"form-control"}),
            'available_end': DateInput(attrs={'class':"form-control"}),
            'available_start': DateInput(attrs={'class':"form-control"}),
        }
        exclude = ["creator", "current_people", "num_people"]
        # fields = ["desired_time"]


class RangeForm(forms.Form):
    start = forms.DateField()
    end = forms.DateField()


class EmailForm(forms.Form):
    body = forms.CharField(
        widget=forms.Textarea(
            attrs={'class':"form-control"},
        ),
    )
