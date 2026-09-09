import json
from io import StringIO
from pathlib import Path

import pytest
from django.core.management import call_command
from django.urls import reverse

from catalog.ingest import sync as catalog_sync
from catalog.ingest.sync import (
    SnapshotError,
    apply_snapshot,
    load_snapshot,
    validate_snapshot,
)
from catalog.models import (
    CatalogEdition,
    Category,
    Course,
    CourseCategory,
    CourseUserView,
)
from documents.models import BulkDocuments, Document
from users.models import User

pytestmark = pytest.mark.django_db

SEED_DIR = Path(__file__).resolve().parent.parent / "ingest" / "seed"


def make_snapshot(year="2026-2027", second_title="Algorithms", second_quadri="q2"):
    return {
        "academic_year": year,
        "programs": [
            {
                "slug": "BA-TEST",
                "name": "Bachelier en tests",
                "faculties": [{"name": "Faculté des Sciences", "color": "#123456"}],
            }
        ],
        "memberships": [
            {
                "program": "BA-TEST",
                "bloc": "1",
                "course_code": "INFO-F100",
                "title": "Programming",
                "mandatory": True,
                "quadri": "q1",
                "lecturers": "Teacher One",
            },
            {
                "program": "BA-TEST",
                "bloc": "2",
                "course_code": "INFO-F200",
                "title": second_title,
                "mandatory": False,
                "quadri": second_quadri,
                "lecturers": "Teacher Two",
            },
        ],
        "warnings": [],
    }


def make_active_edition(year="2023-2024", *, create_ulb=True):
    CatalogEdition.objects.filter(status=CatalogEdition.Status.ACTIVE).update(
        status=CatalogEdition.Status.ARCHIVED
    )
    edition, _ = CatalogEdition.objects.get_or_create(
        key=year,
        defaults={"academic_year": year, "status": CatalogEdition.Status.ARCHIVED},
    )
    edition.academic_year = year
    edition.status = CatalogEdition.Status.ACTIVE
    edition.save(update_fields=["academic_year", "status"])
    if create_ulb:
        Category.objects.create(
            name="ULB",
            slug="ULB",
            edition=edition,
            type=Category.CategoryType.UNIVERSITY,
        )
    return edition


def test_new_year_preserves_course_identity_and_archives_missing_course(client):
    old_edition = make_active_edition(create_ulb=False)
    old_root = Category.objects.create(
        name="ULB",
        slug="ULB",
        edition=old_edition,
        type=Category.CategoryType.UNIVERSITY,
    )
    existing = Course.objects.create(
        name="Old programming", slug="info-f100", period="Q2"
    )
    missing = Course.objects.create(name="Old only", slug="old-f100")
    existing.categories.add(old_root)
    user = User.objects.create_user(
        netid="catalog-user", email="catalog@example.com", password="unused"
    )
    existing.followed_by.add(user)
    view = CourseUserView.objects.create(user=user, course=existing)
    document = Document.objects.create(
        name="Notes",
        course=existing,
        user=user,
        original="original_document/notes.pdf",
        pdf="pdf_document/notes.pdf",
    )
    bulk = BulkDocuments.objects.create(
        url="https://example.com/notes", course=existing, user=user
    )

    apply_snapshot(make_snapshot())

    existing.refresh_from_db()
    missing.refresh_from_db()
    assert existing.pk == view.course_id
    assert existing.name == "Programming"
    assert existing.period == "Q1"
    assert not existing.is_archive
    assert existing.followed_by.filter(pk=user.pk).exists()
    assert Document.objects.get(pk=document.pk).course_id == existing.pk
    assert BulkDocuments.objects.get(pk=bulk.pk).course_id == existing.pk
    assert missing.is_archive
    assert Course.objects.filter(pk=missing.pk).exists()
    archived_root = old_edition.categories.get(slug="ULB")
    assert archived_root.pk == old_root.pk
    assert archived_root.name == "ULB"
    assert not Category.objects.filter(edition=None, slug="archives").exists()
    assert client.get(reverse("catalog:finder_root")).status_code == 200
    assert (
        client.get(reverse("catalog:archive_edition", args=["2023-2024"])).status_code
        == 200
    )


def test_year_archive_exposes_only_the_ulb_tree():
    old_edition = make_active_edition(create_ulb=False)
    ulb = Category.objects.create(
        name="ULB",
        slug="ULB",
        edition=old_edition,
        type=Category.CategoryType.UNIVERSITY,
    )
    faculty = Category.objects.create(
        name="Sciences",
        slug="sciences",
        edition=old_edition,
        type=Category.CategoryType.FACULTY,
    )
    faculty.parents.add(ulb)
    partner = Category.objects.create(
        name="Université partenaire",
        slug="partner",
        edition=old_edition,
        type=Category.CategoryType.UNIVERSITY,
    )

    apply_snapshot(make_snapshot())

    year_archive = old_edition.categories.get(slug="ULB")
    partner.refresh_from_db()
    assert year_archive.pk == ulb.pk
    assert not year_archive.parents.exists()
    assert list(year_archive.children.all()) == [faculty]
    assert not partner.parents.filter(pk=year_archive.pk).exists()
    assert Category.objects.filter(slug="ULB").count() == 2


def test_memberships_are_exact_and_mandatory_is_on_through_row():
    make_active_edition()
    apply_snapshot(make_snapshot())
    rows = CourseCategory.objects.filter(category__edition__key="2026-2027")
    assert rows.count() == 2
    assert rows.get(course__slug="info-f100").mandatory is True
    assert rows.get(course__slug="info-f200").mandatory is False


def test_archived_course_reactivates_and_conflicting_period_becomes_null():
    make_active_edition()
    course = Course.objects.create(name="Archived", slug="info-f100", is_archive=True)
    snapshot = make_snapshot()
    snapshot["memberships"].append(
        {
            **snapshot["memberships"][0],
            "program": "BA-TEST",
            "bloc": "2",
            "quadri": "q2",
        }
    )
    # The extra occurrence collides with INFO-F200's category but not its course/category row.
    apply_snapshot(snapshot)
    course.refresh_from_db()
    assert course.period is None
    assert not course.is_archive


def test_same_year_reload_is_refused():
    make_active_edition("2025-2026")
    apply_snapshot(make_snapshot())  # 2026-2027 is newer, so it becomes active
    edition_count = CatalogEdition.objects.count()

    with pytest.raises(SnapshotError, match="same-year"):
        apply_snapshot(make_snapshot(second_title="New algorithms", second_quadri="aa"))

    assert CatalogEdition.objects.count() == edition_count
    assert (
        CatalogEdition.objects.get(status=CatalogEdition.Status.ACTIVE).key
        == "2026-2027"
    )


def test_older_year_reload_is_refused():
    make_active_edition("2026-2027")
    with pytest.raises(SnapshotError, match="older"):
        apply_snapshot(make_snapshot("2025-2026"))
    assert not CatalogEdition.objects.filter(key="2025-2026").exists()


def test_seed_snapshots_build_active_and_archived_editions():
    # Guards the fake catalog that `make database` loads via sync_catalog.
    for name in ("seed_catalog_2024_2025.json", "seed_catalog_2025_2026.json"):
        apply_snapshot(load_snapshot(SEED_DIR / name))

    active = CatalogEdition.objects.get(status=CatalogEdition.Status.ACTIVE)
    assert active.key == "2025-2026"
    assert CatalogEdition.objects.filter(
        status=CatalogEdition.Status.ARCHIVED, key="2024-2025"
    ).exists()

    root = active.categories.get(slug="ULB")
    faculties = set(
        root.children.filter(type=Category.CategoryType.FACULTY).values_list(
            "slug", flat=True
        )
    )
    assert faculties == {"sciences", "droit"}
    # Bloc slugs are "<program>-<bloc>", not "<program>-bloc-<bloc>".
    bloc_slugs = set(
        active.categories.filter(type=Category.CategoryType.BLOC).values_list(
            "slug", flat=True
        )
    )
    assert "BA-SCI-1" in bloc_slugs
    assert not any("-bloc-" in slug for slug in bloc_slugs)
    assert Course.objects.filter(is_archive=False).count() == 8
    # Courses dropped from the newer year are archived, not deleted.
    assert set(
        Course.objects.filter(is_archive=True).values_list("slug", flat=True)
    ) == {
        "hist-s102",
        "phys-s202",
    }


def test_exception_mid_apply_rolls_back_every_change(monkeypatch):
    edition = make_active_edition(create_ulb=False)
    Category.objects.create(name="ULB", slug="ULB", edition=edition)

    def fail_after_archive(snapshot, new_edition):
        raise RuntimeError("injected failure")

    monkeypatch.setattr(catalog_sync, "_create_categories", fail_after_archive)
    with pytest.raises(RuntimeError, match="injected failure"):
        apply_snapshot(make_snapshot())

    edition.refresh_from_db()
    assert edition.status == CatalogEdition.Status.ACTIVE
    assert Category.objects.filter(slug="ULB", edition=edition).exists()
    assert not Category.objects.get(edition=edition, slug="ULB").is_archive
    assert not CatalogEdition.objects.filter(key="2026-2027").exists()


def test_invalid_snapshot_is_rejected_before_writes():
    snapshot = make_snapshot()
    snapshot["memberships"] = []
    with pytest.raises(SnapshotError, match="non-empty membership"):
        validate_snapshot(snapshot)


def test_sync_command_previews_then_applies(tmp_path):
    make_active_edition()
    path = tmp_path / "catalog.json"
    path.write_text(json.dumps(make_snapshot()), encoding="utf-8")
    output = StringIO()

    call_command("sync_catalog", str(path), stdout=output)

    assert "Read-only preview" in output.getvalue()
    assert not Course.objects.filter(slug="info-f100").exists()

    call_command("sync_catalog", str(path), apply=True, stdout=StringIO())
    assert Course.objects.filter(slug="info-f100", is_archive=False).exists()


def test_catalog_root_lists_ulb_faculties_and_archives(client):
    edition = make_active_edition("2026-2027", create_ulb=False)
    ulb = Category.objects.create(
        name="Université Libre de Bruxelles",
        slug="ULB",
        type=Category.CategoryType.UNIVERSITY,
        edition=edition,
    )
    faculty = Category.objects.create(
        name="Faculté des Sciences",
        slug="sciences",
        type=Category.CategoryType.FACULTY,
        edition=edition,
    )
    faculty.parents.add(ulb)
    archive_edition = CatalogEdition.objects.create(
        key="2025-2026",
        academic_year="2025-2026",
        status=CatalogEdition.Status.ARCHIVED,
    )
    Category.objects.create(
        name="ULB",
        slug="ULB",
        type=Category.CategoryType.UNIVERSITY,
        is_archive=True,
        edition=archive_edition,
    )
    Category.objects.create(
        name="Université partenaire",
        slug="partner",
        type=Category.CategoryType.UNIVERSITY,
        edition=edition,
    )
    response = client.get(reverse("catalog:finder_root"))
    assert response.status_code == 200
    assert b"Universit\xc3\xa9 Libre de Bruxelles" in response.content
    assert b"Sciences" in response.content
    assert reverse("catalog:finder", args=["sciences"]) in response.text
    assert b"Universit\xc3\xa9 partenaire" not in response.content
    assert b"archives du catalogue" in response.content
    assert 'class="card finder-note"' in response.text
    assert response.text.index('class="card finder-note"') > response.text.index(
        'class="finder"'
    )

    faculty_response = client.get(reverse("catalog:finder", args=["sciences"]))
    assert faculty_response.status_code == 200
    assert b"Universit\xc3\xa9 Libre de Bruxelles" in faculty_response.content


def test_archive_lists_editions_then_each_editions_faculties(client):
    active = make_active_edition("2026-2027")
    archived = CatalogEdition.objects.create(
        key="2025-2026",
        academic_year="2025-2026",
        status=CatalogEdition.Status.ARCHIVED,
    )
    ulb = Category.objects.create(
        name="ULB",
        slug="ULB",
        type=Category.CategoryType.UNIVERSITY,
        is_archive=True,
        edition=archived,
    )
    faculty = Category.objects.create(
        name="Faculté des Sciences",
        slug="sciences",
        type=Category.CategoryType.FACULTY,
        is_archive=True,
        edition=archived,
    )
    faculty.parents.add(ulb)
    partner = Category.objects.create(
        name="Université partenaire",
        slug="partner",
        type=Category.CategoryType.UNIVERSITY,
        is_archive=True,
        edition=archived,
    )
    partner.parents.add(ulb)
    historical = CatalogEdition.objects.create(
        key="2018-2019",
        academic_year="2018-2019",
        status=CatalogEdition.Status.ARCHIVED,
    )
    historical_root = Category.objects.create(
        name="ULB",
        slug="ULB",
        type=Category.CategoryType.UNIVERSITY,
        is_archive=True,
        edition=historical,
    )
    historical_faculty = Category.objects.create(
        name="Sciences historiques",
        slug="old-sciences",
        type=Category.CategoryType.FACULTY,
        is_archive=True,
        edition=historical,
    )
    historical_faculty.parents.add(historical_root)

    archive_index = client.get(reverse("catalog:archive_index"))
    assert archive_index.status_code == 200
    assert "2025-2026" in archive_index.text
    assert reverse("catalog:archive_edition", args=[archived.key]) in archive_index.text
    assert "2018-2019" in archive_index.text
    assert (
        reverse("catalog:archive_edition", args=[historical.key]) in archive_index.text
    )
    assert active.academic_year not in archive_index.text

    edition = client.get(reverse("catalog:archive_edition", args=[archived.key]))
    assert edition.status_code == 200
    assert "2025-2026" in edition.text
    assert "Sciences" in edition.text
    assert "Université partenaire" not in edition.text
    assert (
        reverse("catalog:archive_finder", args=[archived.key, faculty.slug])
        in edition.text
    )

    historical_edition = client.get(
        reverse("catalog:archive_edition", args=[historical.key])
    )
    assert historical_edition.status_code == 200
    assert "2018-2019" in historical_edition.text
    assert "Sciences historiques" in historical_edition.text


def test_clean_current_and_archive_urls(client):
    old_edition = make_active_edition()
    old_root = old_edition.categories.get(slug="ULB")
    old_faculty = Category.objects.create(
        name="Sciences",
        slug="sciences",
        edition=old_edition,
        type=Category.CategoryType.FACULTY,
    )
    old_faculty.parents.add(old_root)
    apply_snapshot(make_snapshot())

    current_url = reverse("catalog:finder", args=["sciences/ba-test"])
    archive_url = reverse("catalog:archive_finder", args=["2023-2024", "sciences"])
    assert current_url == "/catalog/sciences/ba-test/"
    assert archive_url == "/catalog/archives/2023-2024/sciences/"
    assert client.get(current_url).status_code == 200
    assert client.get(archive_url).status_code == 200


def test_legacy_prefixed_archive_url_redirects_to_clean_url(client):
    old_edition = make_active_edition(create_ulb=False)
    ulb = Category.objects.create(name="ULB", slug="ULB", edition=old_edition)
    faculty = Category.objects.create(
        name="Bruface", slug="bruface", edition=old_edition
    )
    faculty.parents.add(ulb)
    program = Category.objects.create(
        name="Master", slug="MA-IRCN", edition=old_edition
    )
    program.parents.add(faculty)
    apply_snapshot(make_snapshot())

    old_url = (
        "/catalog/f/archives/archives-2023-2024/"
        "arch-2023-2024-ULB/arch-2023-2024-bruface/"
        "arch-2023-2024-MA-IRCN/"
    )
    response = client.get(old_url)
    assert response.status_code == 301
    assert response.url == "/catalog/archives/2023-2024/bruface/ma-ircn/"
