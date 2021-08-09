from django import template

from documents.models import Document, Vote
from users.models import User

register = template.Library()


@register.simple_tag
def user_liked(user: User, document: Document):
    votes = Vote.objects.filter(user=user, document=document)
    if votes.count() == 0:
        return "not voted"
    else:
        return votes.first().vote_type
