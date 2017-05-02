from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import QuerySet

from rides.models import Appointment


class EventEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, QuerySet):
            return list(o)
        if isinstance(o, Appointment):
            return {
                'id': o.creator_id,
                'title': "To: {} \n From: {} \n # of people: {}/{}".format(o.destination, o.pickup, o.num_people, o.max_people),
                'start': o.available_start,
                'end': o.available_end,
                'allDay': False,
                'url': o.get_absolute_url(),
            }
        return super(EventEncoder, self).default(o)
