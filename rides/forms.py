from registration.forms import RegistrationForm as BaseRegistrationForm
from django.contrib.admin import widgets
from datetimewidget.widgets import DateTimeWidget
from django import forms

from rides.models import Yalie, Appointment
from rides.widgets import DateInput


class RegistrationForm(BaseRegistrationForm):
    class Meta(BaseRegistrationForm.Meta):
        model = Yalie


class LoginForm(forms.Form):
    email = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Email',
            },
        ),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Password',
            },
        ),
    )

    def clean(self):
        try:
            self.cleaned_data['yalie'] = Yalie.objects.only(
                'email',
                'password',
            ).get(
                email=self.cleaned_data.get('email'),
            )
        except Yalie.DoesNotExist:
            raise forms.ValidationError(
                message='Invalid Email or Password',
            )
        else:
            password = self.cleaned_data.get('password','')
            if not self.cleaned_data['yalie'].check_password(password):
                raise forms.ValidationError(
                    message='Invalid Email or Password',
                )
        return self.cleaned_data

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
