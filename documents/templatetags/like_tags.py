from django import template

from documents.models import Document, Vote
from users.models import User

register = template.Library()


@register.simple_tag
def user_liked(user: User, document: Document):
    vote = Vote.objects.filter(user=user, document=document)
    return vote.count() == 1 and vote.first().vote_type == "up"
