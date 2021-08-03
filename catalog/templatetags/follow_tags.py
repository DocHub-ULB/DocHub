from django import template

from catalog.models import Course
from users.models import User

register = template.Library()


@register.simple_tag
def is_following(user: User, course: Course):
    return user.is_following(course)
