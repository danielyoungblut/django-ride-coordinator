from registration.forms import RegistrationForm as BaseRegistrationForm

from rides.models import Yalie


class RegistrationForm(BaseRegistrationForm):
    class Meta(BaseRegistrationForm.Meta):
        model = Yalie
