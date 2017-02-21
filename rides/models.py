from __future__ import unicode_literals

from django.contrib.auth.base_user import AbstractBaseUser
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
# Create your models here.
from rides.managers import YalieManager


class Yalie(AbstractBaseUser):
    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
    ]
    email = models.EmailField(
        unique=True,
        validators=[
            RegexValidator(
                regex=r"@yale\.edu$",
                code="invalid",
                message=_("Yale Email Required"),
            )
        ]
    )
    USERNAME_FIELD = "email"
    first_name = models.CharField(
        max_length=64,
    )
    last_name = models.CharField(
        max_length=64,
    )
    is_active = models.BooleanField(
        default=False,
    )
    objects = YalieManager()
    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def __unicode__(self):
        return self.stat.format(self.value)
