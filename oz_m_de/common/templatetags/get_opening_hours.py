from django import template
from django.utils import timezone
from django.utils.translation import ugettext as _

from oz_m_de.organizations.models import Organization, DayOpeningHours

register = template.Library()

time_format = "%H:%M"


def get_today_opening_hours(organization: Organization) -> DayOpeningHours:
    today = timezone.now().strftime("%a").lower()
    return getattr(organization, today)


@register.filter()
def get_opening_hours(organization: Organization) -> str:
    opening_hours = organization.todays_opening_hours

    try:
        retstring = _("<div class=\"homepage-opened-today\">{} to {}</div>")

        open_first = retstring.format(opening_hours.open_first.strftime(time_format),
                                      opening_hours.close_first.strftime(time_format))
        if opening_hours.open_second:
            open_second = retstring.format(opening_hours.open_second.strftime(time_format),
                                           opening_hours.close_second.strftime(time_format))
            return open_first + open_second
        return open_first

    except AttributeError:
        return _("<div class=\"homepage-opened-today\">Closed today</div>")
