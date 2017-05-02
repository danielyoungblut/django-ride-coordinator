from datetime import datetime
from json import dumps

from django.contrib import messages
from django.db.models.expressions import F
from django.http.request import HttpRequest
from django.http.response import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls.base import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, DeleteView
from django.core import signing

from rides.encoders import EventEncoder
from rides.forms import AppointmentForm, RangeForm, EmailForm
from rides.models import Appointment, Yalie, RideRequest


@login_required(login_url="accounts/login/")
def home(request):
    details = None
    return render(
        request,
        "home.html",
        {'details': details}
    )


@login_required(login_url="accounts/login/")
def index(request):
    return HttpResponse("Hi, I will add stuff")


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


#currently unused???
# @login_required(login_url="accounts/login/")
class RideRequestView(TemplateView):
    template_name = "ride_request.html"

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
                "domain": "127.0.0.1:8000",
            })
        else:
            messages.error(request, "Unable to {} because they have already been accepted/declined".format(action))
            return redirect(calendar)


class AppointmentCreateView(TemplateView):
    template_name = "appointment_create.html"

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

    def get(self, request, appointment_id, *args, **kwargs):
        appointment = get_object_or_404(Appointment, id=appointment_id)
        riders = appointment.current_people.filter()
        is_creator = False
        is_rider = False
        if self.request.user.id == appointment.creator.id:
            is_creator = True
        elif self.request.user in riders:
            is_rider = True
        return self.render_to_response(
            context={
                'form': EmailForm(),
                'appointment': appointment,
                'is_creator': is_creator,
                'is_rider': is_rider,
                'domain': "127.0.0.1:8000"
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
                # TODO: maybe send message if their are no riders
                if riders:
                    for rider in riders:
                        appointment.send_generic_email(body, rider.email)
                    messages.success(request, "Your email was sent")
                else:
                    messages.info(request, "There are no confirmed riders to email")
            elif is_rider:
                appointment.send_generic_email(body, appointment.creator.email)
                messages.success(request, "Your email was sent")
                if riders:
                    for rider in riders:
                        if rider != self.request.user:
                            appointment.send_generic_email(body, rider.email)
                            messages.success(request, "Your email was sent")
            # TODO: add logic can't send twice or to self
            else:
                rr = RideRequest.objects.create_ride_request(appointment, self.request.user)
                rr.save()
                rr.send_request_email(body)
                messages.success(request, "Your request has been sent")
            return redirect(calendar)


class AppointmentDeleteView(TemplateView):
    template_name = "appointment_delete.html"

    def get(self, request, appointment_id, *args, **kwargs):
        appointment = get_object_or_404(Appointment, id=appointment_id)
        riders = appointment.current_people.filter()
        user = self.request.user
        is_creator = False
        is_rider = False
        if user.email == appointment.creator.email:
            is_creator = True
        elif user in riders:
            is_rider = True
        return self.render_to_response(
            context={
                'form': EmailForm(),
                'appointment': appointment,
                'is_creator': is_creator,
                'is_rider': is_rider,
                'domain': "127.0.0.1:8000"
            },
        )

    def post(self, request, appointment_id, *args, **kwargs):
        appointment = get_object_or_404(Appointment, id=appointment_id)
        riders = appointment.current_people.filter()
        is_creator = False
        is_rider = False
        if self.request.user.id == appointment.creator.id:
            is_creator = True
        elif self.request.user in riders:
            is_rider = True
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
                        appointment.send_cancel_email(rider.email)
                appointment.send_cancel_email(appointment.creator.email)
                appointment.num_people = appointment.num_people-1
                appointment.current_people.remove(self.request.user)
                appointment.save()
                rr.delete()
                messages.success(request, "You have canceled your ride commitment")
            return redirect(calendar)


# currently unused
# class AppointmentActionView(TemplateView):
#     template_name = "appointment_action.html"
#
#     def get(self, request, *args, **kwargs):
#         appointment_id = kwargs.get("appointment_id")
#         hash = kwargs.get("hash")
#         action = kwargs.get("action")
#         signer = signing.Signer()
#         try:
#             signer.unsign("{}|{}:{}".format(appointment_id, action, hash))
#         except signing.BadSignature:
#             return HttpResponseBadRequest()
#         appointment = Appointment.objects.get(
#             id=appointment_id
#         )
#         # TODO update appointment based on action and use logic (one time use and can only be guest if logical)
#         if action == "accept":
#             appointment.num_people += 1
#             appointment.save()
#             # return redirect(calendar)
#
#         return self.render_to_response({
#             "appointment": appointment
#         })


class ProfileView(TemplateView):
    template_name = "profile.html"

    def get(self, request, *args, **kwargs):
        username = self.request.user
        created = Appointment.objects.filter(
            creator__id=username.id,
            available_start__gte=datetime.now(),
        )
        accepted = Appointment.objects.filter(
            current_people__id=username.id,
            available_start__gte=datetime.now(),
        )
        return self.render_to_response({
            'username': username,
            'created': created,
            'accepted': accepted,
            'domain': "127.0.0.1:8000",
        })

# class RideView(TemplateResponseMixin, View):
#     user = None
#     ride = None
#
#     def get_template_names(self):
#         if self.request.user.is_creator:
#             template_name = 'creator.html'
#         elif self.request.user.is_rider:
#             template_name = 'rider.html'
#         else:
#             template_name = 'anonymous.html'
#         return [template_name]
#
#     def get_form(self):
#         if self.request.user.is_creator:
#             return CreatorRideForm(
# 				data=self.request.POST if self.request.method == 'POST' else None,
#                 instance=self.ride,
#             )
#         elif self.request.user.is_rider:
#             return RiderRideForm(
# 				data=self.request.POST if self.request.method == 'POST' else None,
#                 instance=self.ride,
#             )
#         return None
#
#     def dispatch(self, request, *args, **kwargs):
#         self.ride = Ride.objects.get(pk=kwargs.get('ride_id'))
#         return super(RideView, self).dispatch(request, *args, **kwargs)
#
#     def get(self, request, ride_id, *args, **kwargs):
#         return self.render_to_response({
#             'form': self.get_form(),
#             'ride': self.ride,
#         })
#
#     def post(self, request, ride_id, *args, **kwargs):
#         form = self.get_form()
#         if form.is_valid():
#             # TODO: process form
#             pass
#         return self.render_to_response({
#             'ride': self.ride,
#             'form': form,
#         })