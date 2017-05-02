USER_SESSION_KEY = '_user_id'


def get_user(request):
    # import here to prevent circular dependencies and please django
    from rides.models import Yalie
    if USER_SESSION_KEY in request.session:
        try:
            return Yalie.objects.get(
                pk=request.session[USER_SESSION_KEY],
            )
        except Yalie.DoesNotExist:
            pass


def context_processor(request):
    return {
        'user': request.user
    }


def login(request, user):
    request.session[USER_SESSION_KEY] = user.pk


def logout(request):
    if USER_SESSION_KEY in request.session:
        del request.session[USER_SESSION_KEY]