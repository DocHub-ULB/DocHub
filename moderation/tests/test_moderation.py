from django.urls import reverse

import pytest

from catalog.models import Course
from documents.models import Document
from moderation.models import ModerationLog, RepresentativeRequest
from users.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def admin():
    return User.objects.create_user(
        netid="admin",
        email="admin@ulb.be",
        first_name="Ad",
        last_name="Min",
        is_staff=True,
    )


@pytest.fixture
def moderator():
    return User.objects.create_user(
        netid="moduser",
        email="mod@ulb.be",
        first_name="Mod",
        last_name="User",
        is_moderator=True,
    )


@pytest.fixture
def regular_user():
    return User.objects.create_user(
        netid="student",
        email="student@ulb.be",
        first_name="Stu",
        last_name="Dent",
    )


@pytest.fixture
def course():
    return Course.objects.create(name="Algorithms", slug="info-f101")


@pytest.fixture
def other_user():
    return User.objects.create_user(
        netid="other",
        email="other@ulb.be",
        first_name="Oth",
        last_name="Er",
    )


@pytest.fixture
def document(other_user, course):
    return Document.objects.create(user=other_user, course=course, name="Test Doc")


def login(client, user):
    client.force_login(user)


# --- A. Full workflow ---


def test_full_moderation_workflow(client, admin, moderator, regular_user, document):
    # 1. Regular user submits a representative request
    login(client, regular_user)
    resp = client.post(
        reverse("representative_request"),
        {"faculty": "sciences", "role": "delegate", "comment": "I want to help"},
    )
    assert resp.status_code == 302
    req = RepresentativeRequest.objects.get(user=regular_user)
    assert not req.processed

    # 2. Moderator accepts the request
    login(client, moderator)
    resp = client.post(
        reverse("process_representative_request", args=[req.id]),
        {"action": "accept"},
    )
    assert resp.status_code == 302
    assert resp.url == reverse("manage_moderators")

    regular_user.refresh_from_db()
    assert regular_user.is_moderator is True

    # 3. Regular user (now moderator) can edit a document they don't own
    login(client, regular_user)
    resp = client.get(reverse("document_edit", args=[document.id]))
    assert resp.status_code == 200

    # 4. Admin removes the rights
    login(client, admin)
    resp = client.post(
        reverse("moderator_remove", args=[regular_user.id]),
    )
    assert resp.status_code == 302

    regular_user.refresh_from_db()
    assert regular_user.is_moderator is False

    # 5. User can no longer edit the document
    login(client, regular_user)
    resp = client.get(reverse("document_edit", args=[document.id]))
    assert resp.status_code == 403


# --- B. ModerationLog correctness ---


def test_log_on_add_moderator(client, moderator, regular_user):
    login(client, moderator)
    client.post(reverse("moderator_add"), {"netid": regular_user.netid})

    log = ModerationLog.objects.last()
    assert log.target_field == "is_moderator"
    assert log.new_value == "True"
    assert log.user == moderator

    regular_user.refresh_from_db()
    assert regular_user.promoted_by == moderator


def test_log_on_remove_moderator(client, admin, moderator):
    login(client, admin)
    client.post(reverse("moderator_remove", args=[moderator.id]))

    log = ModerationLog.objects.last()
    assert log.target_field == "is_moderator"
    assert log.new_value == "False"
    assert log.user == admin

    moderator.refresh_from_db()
    assert moderator.promoted_by is None


def test_log_on_accept_request(client, moderator, regular_user):
    req = RepresentativeRequest.objects.create(
        user=regular_user, faculty="sciences", role="delegate"
    )
    login(client, moderator)
    client.post(
        reverse("process_representative_request", args=[req.id]),
        {"action": "accept"},
    )

    log = ModerationLog.objects.last()
    assert log.target_field == "action_accepter"
    assert log.user == moderator

    regular_user.refresh_from_db()
    assert regular_user.promoted_by == moderator


def test_log_on_reject_request(client, moderator, regular_user):
    req = RepresentativeRequest.objects.create(
        user=regular_user, faculty="sciences", role="delegate"
    )
    login(client, moderator)
    client.post(
        reverse("process_representative_request", args=[req.id]),
        {"action": "reject", "rejection_reason": "Pas assez motivé malheureusement"},
    )

    log = ModerationLog.objects.last()
    assert log.target_field == "action_rejeter"
    assert "Pas assez motivé" in log.new_value


def test_log_on_document_edit_by_moderator(client, moderator, document):
    login(client, moderator)
    resp = client.post(
        reverse("document_edit", args=[document.id]),
        {"name": "New Name", "description": "New desc"},
    )
    assert resp.status_code == 302, f"Expected redirect, got {resp.status_code}"
    assert "document" in resp.url, f"Unexpected redirect: {resp.url}"
    assert moderator.id != document.user_id

    log = ModerationLog.objects.get(target_field="name")
    assert log.old_value == "Test Doc"
    assert log.new_value == "New Name"
    assert log.user == moderator


def test_public_logs_view(client, moderator, regular_user):
    ModerationLog.objects.create(
        user=moderator,
        content_object=regular_user,
        target_field="is_moderator",
        old_value="False",
        new_value="True",
    )
    login(client, regular_user)
    resp = client.get(reverse("public_logs"))
    assert resp.status_code == 200
    assert b"moduser" in resp.content


# --- C. Access control ---


def test_moderator_required_blocks_regular_user(client, regular_user):
    login(client, regular_user)
    resp = client.get(reverse("manage_moderators"))
    assert resp.status_code == 403


def test_moderator_required_allows_moderator(client, moderator):
    login(client, moderator)
    resp = client.get(reverse("manage_moderators"))
    assert resp.status_code == 200


def test_moderator_required_allows_staff(client, admin):
    login(client, admin)
    resp = client.get(reverse("manage_moderators"))
    assert resp.status_code == 200


def test_admin_required_blocks_moderator(client, moderator, regular_user):
    login(client, moderator)
    resp = client.post(reverse("moderator_remove", args=[regular_user.id]))
    assert resp.status_code == 403


def test_representative_request_blocks_moderator(client, moderator):
    login(client, moderator)
    resp = client.get(reverse("representative_request"))
    assert resp.status_code == 403


# --- D. Edge cases ---


def test_reject_requires_reason(client, moderator, regular_user):
    req = RepresentativeRequest.objects.create(
        user=regular_user, faculty="sciences", role="delegate"
    )
    login(client, moderator)
    resp = client.post(
        reverse("process_representative_request", args=[req.id]),
        {"action": "reject", "rejection_reason": "short"},
    )
    # Should redirect with error param since reason is too short
    assert resp.status_code == 302
    assert "error=reason" in resp.url
    req.refresh_from_db()
    assert not req.processed


def test_add_already_moderator(client, moderator, admin):
    initial_count = ModerationLog.objects.count()
    login(client, moderator)
    client.post(reverse("moderator_add"), {"netid": admin.netid})
    assert ModerationLog.objects.count() == initial_count


def test_remove_self_blocked(client, admin):
    login(client, admin)
    resp = client.post(reverse("moderator_remove", args=[admin.id]))
    assert resp.status_code == 302
    admin.refresh_from_db()
    assert admin.is_staff is True


# --- E. New views ---


def test_moderation_tree_accessible(client, regular_user):
    login(client, regular_user)
    resp = client.get(reverse("moderation_tree"))
    assert resp.status_code == 200


def test_moderation_about_accessible(client, regular_user):
    login(client, regular_user)
    resp = client.get(reverse("moderation_about"))
    assert resp.status_code == 200


def test_moderation_tree_shows_promotions(client, admin, moderator, regular_user):
    regular_user.is_moderator = True
    regular_user.promoted_by = admin
    regular_user.save(update_fields=["is_moderator", "promoted_by"])

    login(client, regular_user)
    resp = client.get(reverse("moderation_tree"))
    assert resp.status_code == 200
    assert b"student" in resp.content
    assert b"admin" in resp.content


def test_moderation_profile_blocks_non_moderator_without_logs(client, regular_user):
    login(client, regular_user)
    resp = client.get(reverse("moderation_profile", args=[regular_user.netid]))
    assert resp.status_code == 403


def test_moderation_profile_allows_former_moderator_with_logs(
    client, admin, regular_user
):
    ModerationLog.objects.create(
        user=regular_user,
        content_object=admin,
        target_field="is_moderator",
        old_value="False",
        new_value="True",
    )
    login(client, admin)
    resp = client.get(reverse("moderation_profile", args=[regular_user.netid]))
    assert resp.status_code == 200
    assert b"student" in resp.content
