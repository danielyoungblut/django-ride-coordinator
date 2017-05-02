from django.forms.widgets import TextInput, DateTimeBaseInput
from django.utils.safestring import mark_safe


class DateInput(DateTimeBaseInput):
    def render(self, name, value, attrs=None):
        return mark_safe((
            u'<div class="input-group input-datetimepicker">'
            u'{input}'
            u'<span class="input-group-addon"><i class="glyphicon glyphicon-calendar"></i></span>'
            u'</div>'
        ).format(
            input=super(DateInput, self).render(name, value, attrs=attrs),
        ))
