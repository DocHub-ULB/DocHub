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


def test_document_report_creation(user, document):
    """Test creating a DocumentReport instance"""
    report = DocumentReport.objects.create(
        user=user,
        document=document,
        problem_type=DocumentReport.ProblemType.WRONG_MODULE,
        description="This document is in the wrong course",
    )

    assert report.user == user
    assert report.document == document
    assert report.problem_type == DocumentReport.ProblemType.WRONG_MODULE
    assert report.description == "This document is in the wrong course"
    assert report.created is not None


def test_document_report_without_description(user, document):
    """Test creating a DocumentReport without description"""
    report = DocumentReport.objects.create(
        user=user,
        document=document,
        problem_type=DocumentReport.ProblemType.LOW_QUALITY,
    )

    assert report.description == ""
    assert report.problem_type == DocumentReport.ProblemType.LOW_QUALITY


def test_document_report_str(user, document):
    """Test __str__ method of DocumentReport"""
    report = DocumentReport.objects.create(
        user=user,
        document=document,
        problem_type=DocumentReport.ProblemType.READABILITY,
    )

    expected = f"Report on {document.name} by {user}"
    assert str(report) == expected


def test_document_reports_reverse_relation(user, document):
    """Test accessing reports from document via reverse relation"""
    DocumentReport.objects.create(
        user=user,
        document=document,
        problem_type=DocumentReport.ProblemType.WRONG_TITLE,
    )
    DocumentReport.objects.create(
        user=user,
        document=document,
        problem_type=DocumentReport.ProblemType.OTHER,
    )

    assert document.reports.count() == 2


def test_document_report_view_get(client, user, document):
    """Test GET request to document_report view"""
    client.force_login(user)
    url = reverse("document_report", args=[document.pk])

    response = client.get(url)

    assert response.status_code == 200
    assert "form" in response.context
    assert "document" in response.context
    assert response.context["document"] == document


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


def test_document_report_view_requires_login(client, document):
    """Test that document_report view requires authentication"""
    url = reverse("document_report", args=[document.pk])

    response = client.get(url)

    assert response.status_code == 302  # Redirect to login
    assert "/login" in response.url


def test_multiple_reports_per_user(user, document):
    """Test that a user can create multiple reports for the same document"""
    DocumentReport.objects.create(
        user=user,
        document=document,
        problem_type=DocumentReport.ProblemType.WRONG_MODULE,
    )
    DocumentReport.objects.create(
        user=user,
        document=document,
        problem_type=DocumentReport.ProblemType.READABILITY,
    )

    assert DocumentReport.objects.filter(user=user, document=document).count() == 2


def test_problem_type_choices():
    """Test that all problem types are defined"""
    expected_choices = {
        "wrong_module",
        "wrong_title",
        "low_quality",
        "readability",
        "other",
    }
    actual_choices = {choice[0] for choice in DocumentReport.ProblemType.choices}

    assert actual_choices == expected_choices
