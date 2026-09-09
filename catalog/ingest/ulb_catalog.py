"""ULB-specific catalog scraping and snapshot normalization."""

from __future__ import annotations

import json
import math
import os
import re
import tempfile
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

from catalog.slug import normalize_slug

PAGE_SIZE = 20
PROGRAMS_URL = (
    "https://www.ulb.be/servlet/search?beanKey=beanKeyRechercheFormation"
    "&types=formation&natureFormation=ulb&s=FACULTE_ASC"
    f"&limit={PAGE_SIZE}"
)
FORMATION_URL = "https://www.ulb.be/api/formation?path={}"
SENTINEL_CODES = {"TEMP-0000", "HULB-0000"}
MISSING_YEAR_PROGRAM_ALLOWLIST = {"MA-GEOL"}
DEFAULT_MANDATORY = True
WARNING_ABSOLUTE_LIMIT = 100
WARNING_RATIO_LIMIT = 0.10


class CatalogSourceError(RuntimeError):
    """The remote catalog is incomplete or no longer understandable."""


def validate_academic_year(academic_year: str) -> str:
    match = re.fullmatch(r"(\d{4})-(\d{4})", academic_year)
    if not match or int(match.group(2)) != int(match.group(1)) + 1:
        raise CatalogSourceError(
            f"Invalid academic year {academic_year!r}; expected e.g. 2026-2027."
        )
    return match.group(1)


def _faculty_from_link(link: Any) -> dict[str, str] | None:
    label = link.find(class_="search-result__structure-rattachement")
    children = link.find_all(recursive=False)
    name = label.get_text(" ", strip=True) if label else ""
    if not name and children:
        name = children[-1].get_text(" ", strip=True)
    if not name:
        return None
    style = " ".join(child.get("style", "") for child in children)
    color_match = re.search(r"#[0-9a-fA-F]{6}", style)
    return {"name": name, "color": color_match.group(0) if color_match else ""}


def parse_program_page(html: bytes | str) -> tuple[int | None, list[dict[str, Any]]]:
    """Parse one search page while preserving option/parent relationships."""
    soup = BeautifulSoup(html, "html.parser")
    metadata = soup.find("div", class_="search-metadata__search-title")
    result_count = None
    if metadata is not None:
        match = re.search(
            r"donn[^\d]*(\d+)\s+r[ée]sultats",
            metadata.get_text(" ", strip=True),
            re.IGNORECASE,
        )
        if match:
            result_count = int(match.group(1))

    programs: list[dict[str, Any]] = []
    for mnemonic in soup.find_all("span", class_="search-result__mnemonique"):
        result_item = mnemonic.find_parent("div", class_="search-result__result-item")
        slug = mnemonic.get_text(" ", strip=True)
        title = (
            result_item.find("strong", class_="search-result__structure-intitule")
            if result_item is not None
            else None
        )
        if not slug or title is None:
            raise CatalogSourceError(
                "A program result no longer has a mnemonic and title."
            )

        links: list[Any] = list(mnemonic.find_previous_siblings("a"))
        if not links:
            link_scope = result_item or mnemonic.parent
            if link_scope is None:
                raise CatalogSourceError(
                    "A program result no longer has an interpretable container."
                )
            links = [
                link
                for link in link_scope.find_all("a")
                if link.find(class_="search-result__structure-rattachement")
            ]
        faculties = [
            faculty
            for link in links
            if (faculty := _faculty_from_link(link)) is not None
        ]
        program: dict[str, Any] = {
            "slug": slug,
            "name": title.get_text(" ", strip=True),
            "faculties": faculties,
        }

        option = mnemonic.find_parent("div", class_="search-result__resultat--fille")
        if option is not None:
            parent_item = option.find_previous_sibling(
                "div", class_="search-result__result-item"
            ) or option.find_previous("div", class_="search-result__result-item")
            parent_mnemonic = (
                parent_item.find("span", class_="search-result__mnemonique")
                if parent_item is not None
                else None
            )
            if parent_mnemonic is not None:
                program["parent"] = parent_mnemonic.get_text(" ", strip=True)
        programs.append(program)
    return result_count, programs


def _get_with_retries(
    url: str,
    *,
    session: Any,
    timeout: float,
    retries: int,
) -> requests.Response:
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            response = session.get(url, timeout=timeout)
            if response.ok:
                return response
            last_error = CatalogSourceError(f"HTTP {response.status_code} from {url}")
        except requests.RequestException as exc:
            last_error = exc
        if attempt + 1 < retries:
            time.sleep(0.2 * (attempt + 1))
    raise CatalogSourceError(f"Could not fetch {url}: {last_error}")


def fetch_programs(  # noqa: PLR0912
    *,
    session: Any = requests,
    timeout: float = 20,
    retries: int = 3,
) -> list[dict[str, Any]]:
    programs_by_slug: dict[str, dict[str, Any]] = {}
    parent_programs: set[str] = set()
    page = 1
    page_count: int | None = None
    expected_count: int | None = None

    while page_count is None or page <= page_count:
        page_error: CatalogSourceError | None = None
        for attempt in range(retries):
            try:
                response = _get_with_retries(
                    f"{PROGRAMS_URL}&page={page}",
                    session=session,
                    timeout=timeout,
                    retries=1,
                )
                count, page_programs = parse_program_page(response.content)
                if page == 1 and count is None:
                    raise CatalogSourceError(
                        "Could not parse the ULB program result count."
                    )
                if not page_programs:
                    raise CatalogSourceError(
                        f"Program page {page} was unexpectedly empty."
                    )
                break
            except CatalogSourceError as exc:
                page_error = exc
                if attempt + 1 < retries:
                    time.sleep(0.2 * (attempt + 1))
        else:
            raise CatalogSourceError(
                f"Could not fetch or parse program page {page}: {page_error}"
            )
        if page == 1:
            if count is None:
                raise CatalogSourceError(
                    "Could not parse the ULB program result count."
                )
            expected_count = count
            page_count = math.ceil(count / PAGE_SIZE)
        for program in page_programs:
            slug = program["slug"]
            if "parent" in program:
                parent_programs.add(program["parent"])
            if slug not in programs_by_slug:
                programs_by_slug[slug] = program
                continue
            known = programs_by_slug[slug]
            faculties = {faculty["name"]: faculty for faculty in known["faculties"]}
            faculties.update(
                {faculty["name"]: faculty for faculty in program["faculties"]}
            )
            known["faculties"] = list(faculties.values())
        page += 1

    if expected_count and not programs_by_slug:
        raise CatalogSourceError(
            "The program search returned no interpretable programs."
        )
    accepted = [
        program
        for slug, program in programs_by_slug.items()
        if slug not in parent_programs
    ]
    for program in accepted:
        program["faculties"] = sorted(
            program["faculties"], key=lambda faculty: faculty["name"]
        )
    return sorted(accepted, key=lambda program: program["slug"])


def _program_path(program: dict[str, Any], *, use_parent: bool) -> str:
    slug = program["slug"].upper()
    if use_parent and program.get("parent"):
        return (
            f"/ksup/programme?gen=prod&anet={program['parent'].upper()}"
            f"&option={slug}&lang=fr"
        )
    return f"/ksup/programme?gen=prod&anet={slug}&lang=fr"


def _decode_program_response(response: requests.Response) -> dict[str, Any]:
    try:
        outer = response.json()
        encoded = outer["json"]
        data = json.loads(encoded) if isinstance(encoded, str) else encoded
    except (KeyError, TypeError, ValueError) as exc:
        raise CatalogSourceError("The ULB formation response is malformed.") from exc
    if not isinstance(data, dict) or not isinstance(data.get("blocs"), list):
        raise CatalogSourceError("The ULB formation response has no bloc list.")
    return data


def fetch_program_content(
    program: dict[str, Any],
    *,
    session: Any = requests,
    timeout: float = 20,
    retries: int = 3,
) -> dict[str, Any]:
    attempts = [True, False] if program.get("parent") else [False]
    errors: list[str] = []
    for use_parent in attempts:
        url = FORMATION_URL.format(quote(_program_path(program, use_parent=use_parent)))
        for attempt in range(retries):
            try:
                response = _get_with_retries(
                    url, session=session, timeout=timeout, retries=1
                )
                return _decode_program_response(response)
            except CatalogSourceError as exc:
                errors.append(str(exc))
                if attempt + 1 < retries:
                    time.sleep(0.2 * (attempt + 1))
    raise CatalogSourceError(
        f"Could not fetch or parse accepted program {program['slug']}: {'; '.join(errors)}"
    )


def memberships_for_year(
    program: dict[str, Any], data: dict[str, Any], academic_year: str
) -> list[dict[str, Any]]:
    start_year = validate_academic_year(academic_year)
    matching = [
        bloc for bloc in data["blocs"] if str(bloc.get("anac", "")) == start_year
    ]
    if not matching:
        # ULB keeps some stale programs in search while their public catalog and
        # API are completely empty. Retain those programs and report them.
        if not data["blocs"] or program["slug"] in MISSING_YEAR_PROGRAM_ALLOWLIST:
            return []
        raise CatalogSourceError(
            f"{program['slug']} does not contain the requested academic year {academic_year}."
        )
    for bloc in matching:
        bloc_id = str(bloc.get("blocid") or "").lower()
        signature = str(bloc.get("signature") or "")
        if (bloc_id and not bloc_id.startswith(f"a{start_year}")) or (
            signature and not signature.startswith(start_year)
        ):
            raise CatalogSourceError(
                f"{program['slug']} has inconsistent year markers for {academic_year}."
            )

    complete = [
        bloc
        for bloc in matching
        if str(bloc.get("level", "")).upper() == "P"
        or str(bloc.get("blocid", "")).lower().endswith("bp")
    ]
    selected = complete or matching

    memberships: list[dict[str, Any]] = []
    for source_bloc in selected:
        courses = source_bloc.get("progCourses")
        if not isinstance(courses, list):
            raise CatalogSourceError(
                f"{program['slug']} has an unreadable course list for {academic_year}."
            )
        for course in courses:
            if not isinstance(course, dict) or "id" not in course:
                raise CatalogSourceError(
                    f"{program['slug']} contains an unreadable course record."
                )
            if str(course["id"]).upper() in SENTINEL_CODES:
                continue
            memberships.append(
                {
                    "program": program["slug"],
                    "bloc": course.get("bloc") or source_bloc.get("level"),
                    "course_code": course["id"],
                    "title": course.get("title"),
                    "mandatory": course.get("mandatory"),
                    "quadri": course.get("quadri"),
                    "lecturers": course.get("lecturers", ""),
                }
            )
    return memberships


def resolve_period(raw_values: set[str]) -> str | None:
    if raw_values == {"q1"}:
        return "Q1"
    if raw_values == {"q2"}:
        return "Q2"
    if raw_values in ({"q12"}, {"aa"}):
        return "Y"
    return None


def normalize_memberships(  # noqa: PLR0912, PLR0915
    raw_memberships: list[dict[str, Any]],
    *,
    warning_absolute_limit: int = WARNING_ABSOLUTE_LIMIT,
) -> tuple[list[dict[str, Any]], list[str]]:
    warnings: list[str] = []
    warning_classes: Counter[str] = Counter()
    normalized: list[dict[str, Any]] = []
    title_candidates: dict[str, list[str]] = defaultdict(list)

    def warn(kind: str, message: str) -> None:
        warning_classes[kind] += 1
        warnings.append(f"{kind}: {message}")

    sorted_raw = sorted(
        raw_memberships,
        key=lambda item: (
            str(item.get("program", "")),
            str(item.get("bloc", "")),
            str(item.get("course_code", "")),
            str(item.get("title", "")),
            str(item.get("quadri", "")),
            str(item.get("mandatory", "")),
            str(item.get("lecturers", "")),
        ),
    )
    seen_memberships: set[tuple[str, str, str]] = set()
    for raw in sorted_raw:
        raw_code = str(raw.get("course_code", "")).strip()
        try:
            code = normalize_slug(raw_code)
        except ValueError:
            warn("invalid-course-code", repr(raw_code))
            continue

        raw_bloc = raw.get("bloc")
        bloc = str(raw_bloc).strip() if raw_bloc is not None else ""
        if not bloc:
            bloc = "U"
            warn("unknown-bloc", f"{raw.get('program')} / {code}: missing, using U")
        elif bloc != "U" and not re.fullmatch(r"\d+", bloc):
            warn("unknown-bloc", f"{raw.get('program')} / {code}: retaining {bloc!r}")

        mandatory = raw.get("mandatory")
        if not isinstance(mandatory, bool):
            warn(
                "unexpected-mandatory",
                f"{raw.get('program')} / {bloc} / {code}: using {DEFAULT_MANDATORY}",
            )
            mandatory = DEFAULT_MANDATORY

        source_title = str(raw.get("title") or "").strip()
        title = source_title
        if not source_title:
            title = code.upper()
            warn("blank-title", f"{raw.get('program')} / {bloc} / {code}")
        else:
            title_candidates[code].append(source_title)
        quadri = str(raw.get("quadri") or "").strip().lower()
        key = (str(raw.get("program", "")).strip(), bloc, code)
        if key in seen_memberships:
            continue
        seen_memberships.add(key)
        normalized.append(
            {
                "program": key[0],
                "bloc": bloc,
                "course_code": code,
                "title": title,
                "mandatory": mandatory,
                "quadri": quadri,
                "lecturers": str(raw.get("lecturers") or "").strip(),
            }
        )

    by_code: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for membership in normalized:
        by_code[membership["course_code"]].append(membership)
    for code, occurrences in sorted(by_code.items()):
        titles = list(dict.fromkeys(title_candidates[code]))
        chosen_title = titles[0] if titles else code.upper()
        if len(titles) > 1:
            warn(
                "conflicting-title",
                f"{code}: chose {chosen_title!r} from {sorted(titles)!r}",
            )
        for occurrence in occurrences:
            occurrence["title"] = chosen_title

        raw_periods = {item["quadri"] for item in occurrences}
        if resolve_period(raw_periods) is None:
            warn("unresolved-period", f"{code}: {sorted(raw_periods)!r}")

    total = max(len(raw_memberships), 1)
    for kind, count in warning_classes.items():
        if count > warning_absolute_limit or (
            total >= warning_absolute_limit and count / total > WARNING_RATIO_LIMIT
        ):
            raise CatalogSourceError(
                f"Warning spike for {kind}: {count} of {total} source memberships."
            )
    normalized.sort(
        key=lambda item: (item["program"], item["bloc"], item["course_code"])
    )
    return normalized, warnings


def build_snapshot(
    academic_year: str,
    programs: list[dict[str, Any]],
    raw_memberships: list[dict[str, Any]],
    *,
    minimum_programs: int = 100,
    minimum_memberships: int = 1000,
) -> dict[str, Any]:
    validate_academic_year(academic_year)
    memberships, warnings = normalize_memberships(raw_memberships)
    if len(programs) < minimum_programs:
        raise CatalogSourceError(
            f"Only {len(programs)} accepted programs were scraped; expected at least {minimum_programs}."
        )
    if len(memberships) < minimum_memberships:
        raise CatalogSourceError(
            f"Only {len(memberships)} memberships were scraped; expected at least {minimum_memberships}."
        )
    program_slugs = {program["slug"] for program in programs}
    unknown_programs = sorted({item["program"] for item in memberships} - program_slugs)
    if unknown_programs:
        raise CatalogSourceError(
            f"Memberships reference unknown programs: {unknown_programs[:5]!r}."
        )
    return {
        "academic_year": academic_year,
        "programs": sorted(programs, key=lambda item: item["slug"]),
        "memberships": memberships,
        "warnings": warnings,
    }


def scrape_catalog(
    academic_year: str,
    *,
    session: Any = requests,
    timeout: float = 20,
    retries: int = 3,
    minimum_programs: int = 100,
    minimum_memberships: int = 1000,
) -> dict[str, Any]:
    programs = fetch_programs(session=session, timeout=timeout, retries=retries)
    memberships: list[dict[str, Any]] = []
    scrape_warnings: list[str] = []
    start_year = validate_academic_year(academic_year)
    for program in programs:
        data = fetch_program_content(
            program, session=session, timeout=timeout, retries=retries
        )
        if not data["blocs"]:
            scrape_warnings.append(
                f"allowlisted-empty-program: {program['slug']} has no {academic_year} blocs"
            )
        elif program["slug"] in MISSING_YEAR_PROGRAM_ALLOWLIST and not any(
            str(bloc.get("anac", "")) == start_year for bloc in data["blocs"]
        ):
            scrape_warnings.append(
                f"allowlisted-missing-year-program: {program['slug']} has no {academic_year} blocs"
            )
        memberships.extend(memberships_for_year(program, data, academic_year))
    snapshot = build_snapshot(
        academic_year,
        programs,
        memberships,
        minimum_programs=minimum_programs,
        minimum_memberships=minimum_memberships,
    )
    snapshot["warnings"] = [*scrape_warnings, *snapshot["warnings"]]
    return snapshot


def write_snapshot(snapshot: dict[str, Any], output: str | os.PathLike[str]) -> None:
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temp_name = temporary.name
            json.dump(snapshot, temporary, ensure_ascii=False, indent=2, sort_keys=True)
            temporary.write("\n")
        os.replace(temp_name, destination)
    finally:
        if temp_name and os.path.exists(temp_name):
            os.unlink(temp_name)
