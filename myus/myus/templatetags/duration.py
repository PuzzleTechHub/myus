from django import template

register = template.Library()


@register.filter
def duration(td):
    seconds = int(td.total_seconds())
    (days, seconds) = divmod(seconds, 3600 * 24)
    (hours, seconds) = divmod(seconds, 3600)
    (minutes, seconds) = divmod(seconds, 60)
    return "{} days {:02}:{:02}:{:02}".format(days, hours, minutes, seconds)
