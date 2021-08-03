from django import template

register = template.Library()


@register.filter(name='is_following')
def is_following(user, course_slug):
    return user.is_following(course_slug)
