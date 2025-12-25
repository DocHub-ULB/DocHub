from django.urls import reverse

import pytest

from catalog.models import Course
from documents.models import Document, DocumentReport
from users.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return User.objects.create_user(
        netid="test_user", first_name="Test", last_name="User"
    )


@pytest.fixture
def course():
    return Course.objects.create(name="Test Course", slug="test-course")


@pytest.fixture
def document(user, course):
    return Document.objects.create(
        name="Test Document",
        user=user,
        course=course,
        state=Document.DocumentState.DONE,
    )


def test_document_report_view_post(client, user, document):
    """Test POST request to document_report view"""
    client.force_login(user)
    url = reverse("document_report", args=[document.pk])

    response = client.post(
        url,
        {
            "problem_type": DocumentReport.ProblemType.WRONG_MODULE,
            "description": "Test description",
        },
    )

    assert response.status_code == 302  # Redirect after successful submission
    assert DocumentReport.objects.filter(document=document, user=user).exists()

    report = DocumentReport.objects.get(document=document, user=user)
    assert report.problem_type == DocumentReport.ProblemType.WRONG_MODULE
    assert report.description == "Test description"
