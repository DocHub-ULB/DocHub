from django import template

from documents.models import DocumentReport

register = template.Library()


@register.filter
def problem_type_description(value: str) -> str:
    """Get the detailed description for a problem type."""
    return DocumentReport.ProblemType.get_description(value)
