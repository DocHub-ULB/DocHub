from django import template

from catalog.models import Course
from users.models import User

register = template.Library()


@register.simple_tag
def is_moderated(user: User, course: Course):
    return course in user.moderated_courses.all()
