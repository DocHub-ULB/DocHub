"""Validation, comparison, and transactional application of catalog snapshots."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from django.db import transaction
from django.db.models import Count
from slugify import slugify

from catalog.ingest.ulb_catalog import (
    CatalogSourceError,
    normalize_memberships,
    resolve_period,
    validate_academic_year,
)
from catalog.models import CatalogEdition, Category, Course, CourseCategory

STOPWORDS = {"d'", "de", "du", "et", "l'", "la", "le", "les"}


class SnapshotError(ValueError):
    """A snapshot is unsafe or does not match the documented shape."""


@dataclass(frozen=True)
class CourseValue:
    code: str
    title: str
    period: str | None


@dataclass
class SyncComparison:
    academic_year: str
    program_count: int
    membership_count: int
    category_count: int
    categories_to_archive: int
    memberships_to_archive: int
    create_courses: list[str]
    update_courses: list[str]
    reactivate_courses: list[str]
    archive_courses: list[str]
    disappearing_by_document_count: dict[int, int]
    warnings: list[str]


def load_snapshot(path: str | Path) -> dict[str, Any]:
    try:
        with Path(path).open(encoding="utf-8") as snapshot_file:
            raw = json.load(snapshot_file)
    except (OSError, json.JSONDecodeError) as exc:
        raise SnapshotError(f"Could not read snapshot {path}: {exc}") from exc
    return validate_snapshot(raw)


def validate_snapshot(raw: Any) -> dict[str, Any]:  # noqa: PLR0912, PLR0915
    if not isinstance(raw, dict):
        raise SnapshotError("The snapshot root must be a JSON object.")
    academic_year = raw.get("academic_year")
    if not isinstance(academic_year, str):
        raise SnapshotError("The snapshot has no academic_year string.")
    try:
        validate_academic_year(academic_year)
    except CatalogSourceError as exc:
        raise SnapshotError(str(exc)) from exc

    programs = raw.get("programs")
    memberships = raw.get("memberships")
    source_warnings = raw.get("warnings", [])
    if not isinstance(programs, list) or not programs:
        raise SnapshotError("The snapshot must contain a non-empty program list.")
    if not isinstance(memberships, list) or not memberships:
        raise SnapshotError("The snapshot must contain a non-empty membership list.")
    if not isinstance(source_warnings, list) or not all(
        isinstance(warning, str) for warning in source_warnings
    ):
        raise SnapshotError("Snapshot warnings must be a list of strings.")

    clean_programs: list[dict[str, Any]] = []
    seen_programs: set[str] = set()
    for program in programs:
        if not isinstance(program, dict):
            raise SnapshotError("Every program must be an object.")
        slug = program.get("slug")
        name = program.get("name")
        faculties = program.get("faculties")
        if (
            not isinstance(slug, str)
            or not re.fullmatch(r"[-A-Za-z0-9_]+", slug.strip())
            or len(slug) > 255
        ):
            raise SnapshotError(f"Invalid program slug: {slug!r}.")
        slug = slug.strip()
        if slug in seen_programs:
            raise SnapshotError(f"Duplicate program slug: {slug}.")
        if not isinstance(name, str) or not name.strip() or len(name.strip()) > 255:
            raise SnapshotError(f"Program {slug} has no display name.")
        if not isinstance(faculties, list):
            raise SnapshotError(f"Program {slug} has no faculty list.")
        clean_faculties: list[dict[str, str]] = []
        seen_faculties: set[str] = set()
        for faculty in faculties:
            if not isinstance(faculty, dict) or not isinstance(
                faculty.get("name"), str
            ):
                raise SnapshotError(f"Program {slug} has an invalid faculty.")
            faculty_name = faculty["name"].strip()
            if not faculty_name or len(faculty_name) > 255:
                raise SnapshotError(f"Program {slug} has a blank faculty.")
            if faculty_name not in seen_faculties:
                clean_faculties.append(
                    {
                        "name": faculty_name,
                        "color": str(faculty.get("color") or ""),
                    }
                )
                seen_faculties.add(faculty_name)
        clean_programs.append(
            {
                "slug": slug.strip(),
                "name": name.strip(),
                "faculties": sorted(clean_faculties, key=lambda item: item["name"]),
            }
        )
        seen_programs.add(slug)

    try:
        clean_memberships, validation_warnings = normalize_memberships(memberships)
    except CatalogSourceError as exc:
        raise SnapshotError(str(exc)) from exc
    membership_programs = {membership["program"] for membership in clean_memberships}
    unknown = sorted(membership_programs - seen_programs)
    if unknown:
        raise SnapshotError(f"Memberships reference unknown programs: {unknown[:5]!r}.")
    for membership in clean_memberships:
        if len(membership["title"]) > 255:
            raise SnapshotError(
                f"Course {membership['course_code']} has a title longer than 255 characters."
            )
        if len(membership["bloc"]) > 250:
            raise SnapshotError(
                f"Program {membership['program']} has an overlong bloc label."
            )
    return {
        "academic_year": academic_year,
        "programs": sorted(clean_programs, key=lambda item: item["slug"]),
        "memberships": clean_memberships,
        "warnings": list(dict.fromkeys([*source_warnings, *validation_warnings])),
    }


def course_values(snapshot: dict[str, Any]) -> dict[str, CourseValue]:
    occurrences: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for membership in snapshot["memberships"]:
        occurrences[membership["course_code"]].append(membership)
    return {
        code: CourseValue(
            code=code,
            title=items[0]["title"],
            period=resolve_period({item["quadri"] for item in items}),
        )
        for code, items in sorted(occurrences.items())
    }


def _is_institution(name: str) -> bool:
    return "Université" in name or "Haute Ecole" in name


def _institution_slug(name: str) -> str:
    abbreviations = {
        "Mons": "umons",
        "Namur": "unamur",
        "Liège": "ulg",
        "Louvain": "ucl",
        "Charlemagne": "hec",
        "Prigogine": "HELB",
        "Saint-Louis": "usaintlouis",
    }
    for long_name, short_name in abbreviations.items():
        if long_name in name:
            return short_name
    return slugify(name, stopwords=STOPWORDS)


def _faculty_slug(name: str) -> str:
    short_name = (
        name.removeprefix("Faculté de ")
        .removeprefix("Faculté d'")
        .removeprefix("Faculté des ")
        .removeprefix("Institut d'")
        .removeprefix("Institut des ")
    )
    return slugify(short_name, stopwords=STOPWORDS)


def _bloc_slug(program_slug: str, bloc: str) -> str:
    # e.g. "BA-LROMA" + "1" -> "BA-LROMA-1". slugify keeps odd/blank blocs
    # (a stray "U", spaces, ...) from producing an invalid or empty slug.
    return f"{program_slug}-{slugify(bloc) or 'u'}"


def _program_type(program: dict[str, Any]) -> str | None:
    name = program["name"].lower()
    slug = program["slug"].upper()
    if "bachelier" in name or slug.startswith("BA"):
        return Category.CategoryType.BACHELOR
    if "spécialisation" in name or slug.startswith("MS"):
        return Category.CategoryType.MASTER_SPECIALIZATION
    if "master" in name or slug.startswith("MA"):
        return Category.CategoryType.MASTER
    if "certificat" in name:
        return Category.CategoryType.CERTIFICATE
    if "agrégation" in name:
        return Category.CategoryType.AGGREGATION
    return None


def desired_category_slug_list(snapshot: dict[str, Any]) -> list[str]:
    slugs = ["ULB"]
    faculty_names: set[str] = set()
    for program in snapshot["programs"]:
        slugs.append(program["slug"])
        for faculty in program["faculties"]:
            faculty_names.add(faculty["name"])
    for faculty_name in sorted(faculty_names):
        generator = (
            _institution_slug if _is_institution(faculty_name) else _faculty_slug
        )
        slugs.append(generator(faculty_name))
    for program_slug, bloc in sorted(
        {(item["program"], item["bloc"]) for item in snapshot["memberships"]}
    ):
        slugs.append(_bloc_slug(program_slug, bloc))
    return slugs


def desired_category_slugs(snapshot: dict[str, Any]) -> set[str]:
    return set(desired_category_slug_list(snapshot))


def _expected_category_count(snapshot: dict[str, Any]) -> int:
    return len(desired_category_slug_list(snapshot))


def _active_edition() -> CatalogEdition | None:
    editions = list(
        CatalogEdition.objects.filter(status=CatalogEdition.Status.ACTIVE)[:2]
    )
    if len(editions) > 1:
        raise SnapshotError(
            "The database contains more than one active catalog edition."
        )
    return editions[0] if editions else None


def _active_year(active: CatalogEdition | None) -> int | None:
    """Return the active edition's start year, or None when it has no usable year.

    A freshly seeded placeholder edition (no academic year) counts as "no year",
    so a real snapshot is always allowed to replace it.
    """
    if active is None or not active.academic_year:
        return None
    try:
        return int(validate_academic_year(active.academic_year))
    except CatalogSourceError:
        return None


def compare_snapshot(snapshot: dict[str, Any]) -> SyncComparison:
    active = _active_edition()
    _preflight(snapshot, active)
    categories_to_archive = active.categories.count() if active else 0
    memberships_to_archive = (
        CourseCategory.objects.filter(category__edition=active).count() if active else 0
    )
    values = course_values(snapshot)
    existing = {course.slug: course for course in Course.objects.all()}
    create: list[str] = []
    update: list[str] = []
    reactivate: list[str] = []
    for code, value in values.items():
        course = existing.get(code)
        if course is None:
            create.append(code)
        else:
            if course.is_archive:
                reactivate.append(code)
            if course.name != value.title or course.period != value.period:
                update.append(code)

    archive = sorted(
        code
        for code, course in existing.items()
        if not course.is_archive and code not in values
    )
    disappearing_counts = Counter(
        Course.objects.filter(slug__in=archive)
        .annotate(document_count=Count("document"))
        .values_list("document_count", flat=True)
    )
    return SyncComparison(
        academic_year=snapshot["academic_year"],
        program_count=len(snapshot["programs"]),
        membership_count=len(snapshot["memberships"]),
        category_count=_expected_category_count(snapshot),
        categories_to_archive=categories_to_archive,
        memberships_to_archive=memberships_to_archive,
        create_courses=create,
        update_courses=update,
        reactivate_courses=reactivate,
        archive_courses=archive,
        disappearing_by_document_count=dict(sorted(disappearing_counts.items())),
        warnings=snapshot["warnings"],
    )


def format_comparison(comparison: SyncComparison) -> str:
    lines = [
        f"Catalog {comparison.academic_year} (new active edition)",
        (
            f"Snapshot: {comparison.program_count} programs, "
            f"{comparison.membership_count} memberships, "
            f"{comparison.category_count} categories"
        ),
        (
            f"Active edition to archive: {comparison.categories_to_archive} categories, "
            f"{comparison.memberships_to_archive} course links"
        ),
        (
            f"Courses: create {len(comparison.create_courses)}, "
            f"update {len(comparison.update_courses)}, "
            f"reactivate {len(comparison.reactivate_courses)}, "
            f"archive {len(comparison.archive_courses)}"
        ),
    ]
    if comparison.disappearing_by_document_count:
        grouped = ", ".join(
            f"{document_count} docs: {course_count} courses"
            for document_count, course_count in comparison.disappearing_by_document_count.items()
        )
        lines.append(f"Disappearing courses by document count: {grouped}")
    unresolved = [
        warning
        for warning in comparison.warnings
        if warning.startswith(("conflicting-title:", "unresolved-period:"))
    ]
    other = [warning for warning in comparison.warnings if warning not in unresolved]
    if unresolved:
        lines.append(f"Title/period choices and conflicts ({len(unresolved)}):")
        lines.extend(f"  - {warning}" for warning in unresolved)
    if other:
        lines.append(f"Skipped/defaulted/source warnings ({len(other)}):")
        lines.extend(f"  - {warning}" for warning in other)
    return "\n".join(lines)


def _preflight(snapshot: dict[str, Any], active: CatalogEdition | None) -> None:
    # We only ever move the catalog forward: the snapshot must be for a year that
    # is strictly newer than the active edition. Same-year and older loads are
    # refused for now rather than rebuilt in place.
    snapshot_year = int(validate_academic_year(snapshot["academic_year"]))
    active_year = _active_year(active)
    if active_year is not None:
        assert active is not None  # _active_year only returns a year for a real edition
        if snapshot_year == active_year:
            raise SnapshotError(
                f"Catalog {snapshot['academic_year']} is already the active edition; "
                "same-year reloads are not supported yet."
            )
        if snapshot_year < active_year:
            raise SnapshotError(
                f"Catalog {snapshot['academic_year']} is older than the active "
                f"edition {active.academic_year}; refusing to load an older catalog."
            )

    if CatalogEdition.objects.filter(key=snapshot["academic_year"]).exists():
        raise SnapshotError(
            f"Catalog edition {snapshot['academic_year']} already exists but is not active."
        )
    desired = desired_category_slugs(snapshot)
    if len(desired) != len(desired_category_slug_list(snapshot)):
        raise SnapshotError("The snapshot would create duplicate category slugs.")
    overlong = sorted(slug for slug in desired if len(slug) > 255)
    if "" in desired:
        raise SnapshotError("The snapshot would create a blank category slug.")
    if overlong:
        raise SnapshotError(f"Category slugs exceed 255 characters: {overlong[:5]!r}.")

    if active is not None:
        active_slugs = set(active.categories.values_list("slug", flat=True))
        if "ULB" not in active_slugs:
            raise SnapshotError("The active catalog edition has no ULB root.")


def _create_categories(
    snapshot: dict[str, Any], edition: CatalogEdition
) -> dict[tuple[str, str], Category]:
    ulb = Category.objects.create(
        name="Université Libre de Bruxelles",
        slug="ULB",
        type=Category.CategoryType.UNIVERSITY,
        edition=edition,
    )
    faculty_data: dict[str, dict[str, str]] = {}
    for program in snapshot["programs"]:
        for faculty in program["faculties"]:
            faculty_data[faculty["name"]] = faculty

    faculty_categories: dict[str, Category] = {}
    for name, faculty in sorted(faculty_data.items()):
        if _is_institution(name):
            category = Category.objects.create(
                name=name,
                slug=_institution_slug(name),
                description=faculty["color"],
                type=Category.CategoryType.UNIVERSITY,
                edition=edition,
            )
        else:
            category = Category.objects.create(
                name=name,
                slug=_faculty_slug(name),
                description=faculty["color"],
                type=Category.CategoryType.FACULTY,
                edition=edition,
            )
            category.parents.add(ulb)
        faculty_categories[name] = category

    program_categories: dict[str, Category] = {}
    for program in snapshot["programs"]:
        category = Category.objects.create(
            name=program["name"],
            slug=program["slug"],
            type=_program_type(program),
            edition=edition,
        )
        parents = [faculty_categories[item["name"]] for item in program["faculties"]]
        category.parents.add(*(parents or [ulb]))
        program_categories[program["slug"]] = category

    blocs: dict[tuple[str, str], Category] = {}
    membership_blobs = sorted(
        {(item["program"], item["bloc"]) for item in snapshot["memberships"]}
    )
    for program_slug, bloc in membership_blobs:
        category = Category.objects.create(
            name=f"Bloc {bloc}",
            slug=_bloc_slug(program_slug, bloc),
            type=Category.CategoryType.BLOC,
            edition=edition,
        )
        category.parents.add(program_categories[program_slug])
        blocs[(program_slug, bloc)] = category
    return blocs


def _archive_active_edition(active: CatalogEdition) -> None:
    ulb = active.categories.filter(slug="ULB").first()
    if ulb is None:
        raise SnapshotError("The active catalog edition has no ULB root.")
    active.categories.update(is_archive=True)
    active.status = CatalogEdition.Status.ARCHIVED
    active.save(update_fields=["status"])
    ulb.parents.clear()


def apply_snapshot(snapshot: dict[str, Any]) -> SyncComparison:
    """Revalidate, compare, and apply one snapshot in a single transaction."""
    snapshot = validate_snapshot(snapshot)
    comparison = compare_snapshot(snapshot)
    with transaction.atomic():
        active = _active_edition()
        if active is not None:
            active = CatalogEdition.objects.select_for_update().get(pk=active.pk)
        _preflight(snapshot, active)

        if active is not None:
            _archive_active_edition(active)
        edition = CatalogEdition.objects.create(
            key=snapshot["academic_year"],
            academic_year=snapshot["academic_year"],
            status=CatalogEdition.Status.ARCHIVED,
        )

        bloc_categories = _create_categories(snapshot, edition)
        values = course_values(snapshot)
        Course.objects.all().update(is_archive=True)
        courses: dict[str, Course] = {}
        for code, value in values.items():
            course, _ = Course.objects.get_or_create(
                slug=code,
                defaults={"name": value.title, "period": value.period},
            )
            course.name = value.title
            course.period = value.period
            course.is_archive = False
            course.save(update_fields=["name", "period", "is_archive"])
            courses[code] = course

        CourseCategory.objects.bulk_create(
            [
                CourseCategory(
                    course=courses[membership["course_code"]],
                    category=bloc_categories[
                        (membership["program"], membership["bloc"])
                    ],
                    mandatory=membership["mandatory"],
                )
                for membership in snapshot["memberships"]
            ]
        )
        edition.status = CatalogEdition.Status.ACTIVE
        edition.save(update_fields=["status"])
    return comparison
