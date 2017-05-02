# from django.contrib.auth import get_user
from django.http import HttpResponseRedirect
from django.conf import settings
# from django.views.decorators.clickjacking import xframe_options_exempt
from re import compile

# EXEMPT_URLS = [compile(settings.LOGIN_URL.lstrip('/'))]
# if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
#     EXEMPT_URLS += [compile(expr) for expr in settings.LOGIN_EXEMPT_URLS]
#
#
# class LoginRequiredMiddleware:
#
#     def __init__(self, get_response):
#         self.get_response = get_response
#
#     def __call__(self, request):
#         self.process_request(request)
#
#         response = self.get_response(request)
#
#         response = self.process_response(request, response)
#
#         return response
#
#     ## request
#     def process_request(self, request):
#         pass
#
#     ## response
#     def process_response(self, request, response):
#
#         assert hasattr(request, 'user'), "user attribute not found."
#
#         if not request.user.is_authenticated():
#             path = request.path_info.lstrip('/')
#             if not any(m.match(path) for m in EXEMPT_URLS):
#                 return HttpResponseRedirect(settings.LOGIN_URL)
#
#         return response
from django.utils.deprecation import MiddlewareMixin

from mysite import get_user


class AuthMiddleware(MiddlewareMixin, object):
    def process_request(self, request, *args, **kwargs):
        request.user = get_user(request)
        # If not logged in
        if not request.user:
            from rides.views import LoginView
            return LoginView.as_view()(request, *args, **kwargs)
