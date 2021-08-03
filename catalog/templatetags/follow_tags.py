from django import template

from users.models import User
from catalog.models import Course

register = template.Library()


@register.simple_tag
def is_following(user: User, course: Course):
    return user.is_following(course)
