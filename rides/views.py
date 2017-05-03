from datetime import datetime
from json import dumps

import operator
from django.contrib import messages
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.db.models.expressions import F
from django.http.request import HttpRequest
from django.http.response import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from django.urls.base import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, DeleteView
from django.core import signing

from mysite import login
from mysite.decorators import login_required
from rides.encoders import EventEncoder
from rides.forms import AppointmentForm, RangeForm, EmailForm, LoginForm
from rides.models import Appointment, Yalie, RideRequest


@login_required(login_url="accounts/login/")
def home(request):
    template_name = "home.html"
    return render(request, template_name)


# @login_required(login_url="accounts/login/")
def index(request):
    return redirect(calendar)


class LoginView(TemplateView):
    template_name = 'registration/login.html'

    def get(self, *args, **kwargs):
        form = LoginForm()
        return self.render_to_response({
            'form': form,
        })

    def post(self, request, *args, **kwargs):
        form = LoginForm(
            data=request.POST,
        )
        if form.is_valid():
            login(request, form.cleaned_data['yalie'])
            return HttpResponseRedirect(
                redirect_to=request.get_full_path(),
            )
        return self.render_to_response({
            'form': form,
        })


@login_required(login_url="accounts/login/")
def calendar(request):
    template_name = "calendar.html"

    if request.is_ajax():
        form = RangeForm(
            data=request.GET,
        )
        if not form.is_valid():
            print(form.errors)
        appointments = Appointment.objects.filter(
            available_end__gte=form.cleaned_data.get('start'),
            available_start__lte=form.cleaned_data.get('end'),
            num_people__lt=F('max_people'),
        )
        return HttpResponse(
            content=dumps(appointments, cls=EventEncoder),
            content_type='applacation/json')
    return render(request, template_name)


class RideRequestView(TemplateView):
    template_name = "ride_request.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(RideRequestView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        ride_request_id = kwargs.get("ride_request_id")
        hash = kwargs.get("hash")
        action = kwargs.get("action")
        signer = signing.Signer()
        try:
            signer.unsign("{}|{}:{}".format(ride_request_id, action, hash))
        except signing.BadSignature:
            return HttpResponseBadRequest()
        ride_request = RideRequest.objects.get(
            id=ride_request_id
        )
        # TODO update appointment based on action and use logic (one time use and can only be guest if logical) add messages
        if ride_request.status == "pending":
            if action == "accept":
                ride_request.appointment.num_people += 1
                ride_request.appointment.save()
                ride_request.status = "accepted"
                ride_request.save()
                ride_request.appointment.current_people.add(ride_request.requester)
                ride_request.send_accept_email()
                action = "accepted"

            else:
                ride_request.status = "declined"
                ride_request.save()
                ride_request.send_decline_email()
                action = "declined"

            # TODO: have domain not be hard coded in the html
            return self.render_to_response({
                "ride_request": ride_request,
                "action": action,
                'domain': Site.objects.get_current(),
            })
        else:
            messages.error(request, "Unable to {} because they have already been accepted/declined".format(action))
            return redirect(calendar)


class AppointmentCreateView(TemplateView):
    template_name = "appointment_create.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AppointmentCreateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.render_to_response(
            context={
                'form': AppointmentForm,
            }
        )

    def post(self, request):
        form = AppointmentForm(
            data=request.POST
        )
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.creator = self.request.user
            appointment.save()
            messages.success(request, 'Your appointment was added')
            return redirect(calendar)


class AppointmentView(TemplateView):
    template_name = "appointment_view.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AppointmentView, self).dispatch(request, *args, **kwargs)

    def get(self, request, appointment_id, *args, **kwargs):
        appointment = get_object_or_404(Appointment, id=appointment_id)
        riders = appointment.current_people.filter()
        pending = RideRequest.objects.filter(
            requester_id=self.request.user.id,
            appointment_id=appointment.id,
            status="pending"
        )
        is_creator = False
        is_rider = False
        is_requester = False
        if self.request.user.id == appointment.creator.id:
            is_creator = True
        elif self.request.user in riders:
            is_rider = True
        elif pending:
            is_requester = True
        return self.render_to_response(
            context={
                'form': EmailForm(),
                'appointment': appointment,
                'is_creator': is_creator,
                'is_rider': is_rider,
                'is_requester': is_requester,
                'riders': riders,
                'domain': Site.objects.get_current(),
            },
        )

    def post(self, request, appointment_id, *args, **kwargs):
        form = EmailForm(
            data=request.POST,
        )
        appointment = get_object_or_404(Appointment, id=appointment_id)
        riders = appointment.current_people.filter()
        is_creator = False
        is_rider = False
        if self.request.user.id == appointment.creator.id:
            is_creator = True
        elif self.request.user in riders:
            is_rider = True
        if form.is_valid():
            body = form.cleaned_data['body']
            if is_creator:
                if riders:
                    for rider in riders:
                        appointment.send_generic_email(body, rider.email, self.request.user.email)
                    messages.success(request, "Your email was sent")
                else:
                    messages.info(request, "There are no confirmed riders to email")
            elif is_rider:
                appointment.send_generic_email(body, appointment.creator.email, self.request.user.email)
                messages.success(request, "Your email was sent")
                if riders:
                    for rider in riders:
                        if rider != self.request.user:
                            appointment.send_generic_email(body, rider.email, self.request.user.email)
                            messages.success(request, "Your email was sent")
            else:
                pending = RideRequest.objects.filter(
                    requester_id=self.request.user.id,
                    appointment_id=appointment.id,
                    status="pending"
                )
                if not pending:
                    rr = RideRequest.objects.create_ride_request(appointment, self.request.user)
                    rr.save()
                    rr.send_request_email(body)
                    messages.success(request, "Your request has been sent")
                else:
                    messages.success(request, "Your request has been canceled")
            return redirect(calendar)


class AppointmentDeleteView(TemplateView):
    template_name = "appointment_delete.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AppointmentDeleteView, self).dispatch(request, *args, **kwargs)

    def get(self, request, appointment_id, *args, **kwargs):
        appointment = get_object_or_404(Appointment, id=appointment_id)
        riders = appointment.current_people.filter()
        user = self.request.user
        is_creator = False
        is_rider = False
        pending = RideRequest.objects.filter(
            requester_id=self.request.user.id,
            appointment_id=appointment.id,
            status="pending"
        )
        is_pending = False
        if user.email == appointment.creator.email:
            is_creator = True
        elif user in riders:
            is_rider = True
        elif pending:
            is_pending = True
        return self.render_to_response(
            context={
                'form': EmailForm(),
                'appointment': appointment,
                'is_creator': is_creator,
                'is_rider': is_rider,
                'is_pending': is_pending,
                'domain': Site.objects.get_current(),
            },
        )

    def post(self, request, appointment_id, *args, **kwargs):
        appointment = get_object_or_404(Appointment, id=appointment_id)
        riders = appointment.current_people.filter()
        is_creator = False
        is_rider = False
        pending = RideRequest.objects.filter(
            requester_id=self.request.user.id,
            appointment_id=appointment.id,
            status="pending"
        )
        is_pending = False
        if self.request.user.id == appointment.creator.id:
            is_creator = True
        elif self.request.user in riders:
            is_rider = True
        elif pending:
            is_pending = True
        if request.POST.get('delete'):
            if is_creator:
                for rider in riders:
                    appointment.send_delete_email(rider.email)
                appointment.delete()
                messages.success(request, "You have deleted your ride appointment")
            elif is_rider:
                rr = RideRequest.objects.filter(
                    appointment_id=appointment.id,
                    requester_id=self.request.user.id,
                )
                for rider in riders:
                    if rider != self.request.user:
                        appointment.send_cancel_email(rider.email, self.request.user.email)
                appointment.send_cancel_email(appointment.creator.email, self.request.user.email)
                appointment.num_people = appointment.num_people-1
                appointment.current_people.remove(self.request.user)
                appointment.save()
                rr.delete()
                messages.success(request, "You have canceled your ride commitment")
            elif is_pending:
                rr = RideRequest.objects.get(
                    appointment_id=appointment.id,
                    requester_id=self.request.user.id,
                    status="pending"
                )
                rr.send_cancel_request_email(appointment.creator.email, self.request.user.email)
                rr.delete()
                messages.success(request, "You have canceled your ride request")
            return redirect(calendar)


class ProfileView(TemplateView):
    template_name = "profile.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ProfileView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        username = self.request.user
        created = Appointment.objects.filter(
            creator__id=username.id,
            available_start__gte=datetime.now(),
        )
        created = sorted(created, key=operator.attrgetter('desired_time'))
        accepted = Appointment.objects.filter(
            current_people__id=username.id,
            available_start__gte=datetime.now(),
        )
        accepted = sorted(accepted, key=operator.attrgetter('desired_time'))
        pending = RideRequest.objects.filter(
            requester_id=username.id,
            status="pending",
        )
        return self.render_to_response({
            'username': username,
            'created': created,
            'accepted': accepted,
            'pending': pending,
            'domain': Site.objects.get_current(),
        })
