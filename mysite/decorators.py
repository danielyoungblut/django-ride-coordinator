from functools import wraps

from django.utils.decorators import available_attrs


def login_required(func=None, *args, **kwargs):
    def decorator(fn):
        @wraps(fn, assigned=available_attrs(fn))
        def inner(request, *args, **kwargs):
            from rides.views import LoginView
            if not request.user:
                return LoginView.as_view()(request, *args, **kwargs)
            return fn(request, *args, **kwargs)
        return inner
    if func:
        return decorator(func)
    return decorator