import pytest
from django.urls import reverse

from documents.models import Vote

pytestmark = pytest.mark.django_db


def test_like_then_unlike(client, user, document):
    """Hitting the like button twice adds then removes the like."""
    client.force_login(user)
    url = reverse("document_like", args=[document.pk])

    assert client.post(url).status_code == 302
    assert Vote.objects.filter(
        document=document, user=user, vote_type=Vote.VoteType.UPVOTE
    ).exists()

    assert client.post(url).status_code == 302
    assert not Vote.objects.filter(document=document, user=user).exists()


def test_like_replaces_an_old_downvote(client, user, document):
    """Downvotes are gone from the UI, but old rows must not block a like."""
    Vote.objects.create(document=document, user=user, vote_type=Vote.VoteType.DOWNVOTE)
    client.force_login(user)

    assert client.post(reverse("document_like", args=[document.pk])).status_code == 302

    vote = Vote.objects.get(document=document, user=user)
    assert vote.vote_type == Vote.VoteType.UPVOTE
