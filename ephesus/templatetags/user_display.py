from django import template

register = template.Library()

@register.inclusion_tag('tags/user_display.html')
def user_display(user):
    """Display a user"""

    return {'user': user}
