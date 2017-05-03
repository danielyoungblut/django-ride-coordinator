from __future__ import unicode_literals

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.core.mail.message import EmailMessage
from django.core.signing import Signer
from django.core.validators import RegexValidator
from django.db import models
from django.template.loader import render_to_string
from django.urls.base import reverse
from django.utils.translation import ugettext_lazy as _
# Create your models here.
from rides.managers import YalieManager, RideRequestManager


class Yalie(AbstractBaseUser):
    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
    ]
    email = models.EmailField(
        unique=True,
        validators=[
            RegexValidator(
                regex=r"@yale\.edu$|danyoungblut223@gmail\.com|dansproject223@gmail\.com",
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
        return "{} {}".format(self.first_name, self.last_name)


class Appointment(models.Model):
    creator = models.ForeignKey(
        to='Yalie',
        related_name='apps_created',
    )
    desired_time = models.DateTimeField()
    available_start = models.DateTimeField()
    available_end = models.DateTimeField()
    destination = models.CharField(
        default="Bradley International Airport",
        max_length=128,
    )
    pickup = models.CharField(
        default="Phelps Gate",
        max_length=128,
        verbose_name="Pickup location"
    )
    max_people = models.IntegerField(
        verbose_name="Max number of other riders"
    )
    num_people = models.IntegerField(
        default=0,
    )
    current_people = models.ManyToManyField(
        to='Yalie',
        related_name='apps_guest',
    )

    def __unicode__(self):
        return self.id

    def get_absolute_url(self):
        return reverse(
            viewname="appointment_view",
            kwargs={
                "appointment_id": self.id
            }
        )

    def get_action_url(self, action):
        signer=Signer()
        result=signer.sign("{}|{}".format(self.id, action))
        hash=result.split(":")[1]
        return reverse(
            viewname="appointment_action",
            kwargs={
                "appointment_id": self.id,
                "action":action,
                "hash":hash,
            }
        )

    def send_generic_email(self, body, email, sender):
        msg = EmailMessage(
            body=render_to_string(
                template_name="generic_email.html",
                context={
                    "appointment": self,
                    "email": email,
                    "body": body,
                    "sender": sender,
                    'domain': get_current_site().domain,
                }
            ),
            subject="Yale Ride Coordinator: Someone you are riding with sent a message",
            to=[email],
        )
        msg.content_subtype = 'html'
        return msg.send()

    def send_delete_email(self, email):
        msg = EmailMessage(
            body=render_to_string(
                template_name="delete_email.html",
                context={
                    "appointment": self,
                    "email": email,
                    # "body": body,
                    'domain': get_current_site().domain,
                }
            ),
            subject="Yale Ride Coordinator: A ride has been cancelled",
            to=[email],
        )
        msg.content_subtype = 'html'
        return msg.send()

    def send_cancel_email(self, email, sender):
        msg = EmailMessage(
            body=render_to_string(
                template_name="cancel_email.html",
                context={
                    "appointment": self,
                    "email": email,
                    "sender": sender,
                    # "body": body,
                    'domain': get_current_site().domain,
                }
            ),
            subject="Yale Ride Coordinator: A ride has been cancelled",
            to=[email],
        )
        msg.content_subtype = 'html'
        return msg.send()

    # def save(self, *args, **kwargs):
    #     if not self.id:
    #         self.available_end = self.desired_time
    #         self.available_start = self.desired_time
    #     super(Appointment, self).save(*args, **kwargs)


class RideRequest(models.Model):
    requester = models.ForeignKey(
        to='Yalie',
        related_name='ride_requester',
    )
    appointment = models.ForeignKey(
        to='Appointment',
        related_name='ride_request',
        on_delete=models.CASCADE
    )
    #TODO: should I preset the three options somehow?
    status = models.CharField(
        max_length=64,
        default="pending"
    )
    objects = RideRequestManager()

    def get_absolute_url(self):
        return reverse(
            viewname="ride_request",
            kwargs={
                "ride_request_id": self.id
            }
        )

    def get_action_url(self, action):
        signer = Signer()
        result = signer.sign("{}|{}".format(self.id, action))
        hash = result.split(":")[1]
        return reverse(
            viewname="ride_request",
            kwargs={
                "ride_request_id": self.id,
                "action": action,
                "hash": hash,
            }
        )

    # TODO: change domains for all emails
    def send_request_email(self, content):
        msg = EmailMessage(
            body=render_to_string(
                template_name="request_email.html",
                context={
                    "ride_request": self,
                    "content": content,
                    "accept_url": self.get_action_url("accept"),
                    "decline_url": self.get_action_url("decline"),
                    'domain': get_current_site().domain,
                }
            ),
            subject="Yale Rides: Somebody wants to ride with you",
            to=[self.appointment.creator.email, ],
        )
        msg.content_subtype = 'html'
        return msg.send()

    def send_accept_email(self):
        msg = EmailMessage(
            body=render_to_string(
                template_name="accept_email.html",
                context={
                    "ride_request": self,
                    'domain': get_current_site().domain,
                }
            ),
            subject="Yale Rides: Your ride request has been accepted",
            to=[self.requester.email, ],
        )
        msg.content_subtype = 'html'
        return msg.send()

    def send_decline_email(self):
        msg = EmailMessage(
            body=render_to_string(
                template_name="decline_email.html",
                context={
                    "ride_request": self,
                    # "app": self.appointment.
                    'domain': get_current_site().domain,
                }
            ),
            subject="Yale Ride Coordinator: Regrettably, your ride request has been declined",
            to=[self.requester.email, ],
        )
        msg.content_subtype = 'html'
        return msg.send()

    def send_cancel_request_email(self, email, sender):
        msg = EmailMessage(
            body=render_to_string(
                template_name="cancel_request_email.html",
                context={
                    "appointment": self,
                    "email": email,
                    "sender": sender,
                    # "body": body,
                    'domain': get_current_site().domain,
                }
            ),
            subject="Yale Ride Coordinator: A ride has been cancelled",
            to=[email],
        )
        msg.content_subtype = 'html'
        return msg.send()