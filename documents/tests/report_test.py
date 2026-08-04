import pytest
from django.urls import reverse

from documents.models import DocumentReport

pytestmark = pytest.mark.django_db


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
