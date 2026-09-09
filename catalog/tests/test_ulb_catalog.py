import json
from pathlib import Path

import pytest
import requests

from catalog.ingest.ulb_catalog import (
    CatalogSourceError,
    fetch_program_content,
    fetch_programs,
    memberships_for_year,
    normalize_memberships,
    parse_program_page,
    resolve_period,
    write_snapshot,
)

FIXTURES = Path(__file__).parent / "fixtures"


class FakeResponse:
    def __init__(self, content=b"", payload=None, status_code=200):
        self.content = content
        self._payload = payload
        self.status_code = status_code
        self.ok = status_code == 200

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.urls = []

    def get(self, url, timeout):
        self.urls.append((url, timeout))
        return next(self.responses)


class FailingSession:
    def __init__(self):
        self.calls = 0

    def get(self, url, timeout):
        self.calls += 1
        raise requests.ConnectionError("offline")


def program_page(count, slugs):
    programs = "".join(
        f"""
        <div class="search-result__result-item">
          <strong class="search-result__structure-intitule">Program {slug}</strong>
          <a><i style="color: #123456"></i><span>Faculté des Sciences</span></a>
          <span class="search-result__mnemonique">{slug}</span>
        </div>
        """
        for slug in slugs
    )
    return f"""
      <div class="search-metadata__search-title">La recherche a donné {count} résultats</div>
      {programs}
    """.encode()


def test_fetch_programs_reads_exact_and_partial_final_pages():
    pages = [program_page(21, [f"P{i}" for i in range(20)]), program_page(21, ["P20"])]
    session = FakeSession([FakeResponse(page) for page in pages])

    programs = fetch_programs(session=session, retries=1)

    assert len(programs) == 21
    assert len(session.urls) == 2
    assert session.urls[-1][0].endswith("page=2")


def test_fetch_programs_reads_exact_single_page():
    session = FakeSession(
        [FakeResponse(program_page(20, [f"P{i}" for i in range(20)]))]
    )
    assert len(fetch_programs(session=session, retries=1)) == 20
    assert len(session.urls) == 1


def test_program_request_failure_stops_after_bounded_retries():
    session = FailingSession()
    with pytest.raises(CatalogSourceError, match="program page 1"):
        fetch_programs(session=session, retries=2)
    assert session.calls == 2


def test_parse_program_parent_option():
    html = """
      <div class="search-metadata__search-title">La recherche a donné 2 résultats</div>
      <div class="search-result__result-item">
        <strong class="search-result__structure-intitule">Parent</strong>
        <span class="search-result__mnemonique">MA-PARENT</span>
      </div>
      <div class="search-result__resultat--fille">
        <div class="search-result__result-item">
          <strong class="search-result__structure-intitule">Option</strong>
          <span class="search-result__mnemonique">MA-OPTION</span>
        </div>
      </div>
    """
    count, programs = parse_program_page(html)
    assert count == 2
    assert programs[1]["parent"] == "MA-PARENT"


def test_captured_ulb_responses_keep_their_expected_shape():
    count, programs = parse_program_page(
        (FIXTURES / "ulb_program_page.html").read_bytes()
    )
    assert count == 454
    assert programs == [
        {
            "slug": "BA-HHAAR",
            "name": "Bachelier en histoire de l'art et archéologie, orientation générale",
            "faculties": [
                {
                    "name": "Faculté de Philosophie et Sciences sociales",
                    "color": "#0099cc",
                }
            ],
        }
    ]

    payload = json.loads((FIXTURES / "ulb_formation.json").read_text())
    data = fetch_program_content(
        {"slug": "BA-INFO"},
        session=FakeSession([FakeResponse(payload=payload)]),
        retries=1,
    )
    memberships = memberships_for_year({"slug": "BA-INFO"}, data, "2026-2027")
    assert [membership["course_code"] for membership in memberships] == ["INFO-F101"]


def test_requested_academic_year_is_selected_explicitly():
    program = {"slug": "BA-TEST", "name": "Test", "faculties": []}
    data = {
        "blocs": [
            {
                "anac": "2025",
                "level": "P",
                "progCourses": [{"id": "OLD-F100", "bloc": "1"}],
            },
            {
                "anac": "2026",
                "level": "P",
                "progCourses": [
                    {
                        "id": "INFO-F100",
                        "title": "Programming",
                        "mandatory": True,
                        "bloc": "1",
                        "quadri": "q1",
                        "lecturers": "A. Teacher",
                    },
                    {"id": "TEMP-0000", "bloc": "1"},
                ],
            },
        ]
    }
    memberships = memberships_for_year(program, data, "2026-2027")
    assert [item["course_code"] for item in memberships] == ["INFO-F100"]


def test_multiple_complete_options_are_merged():
    program = {"slug": "BA-DROI"}
    data = {
        "blocs": [
            {
                "anac": "2026",
                "level": "P",
                "blocid": "a2026s1bp",
                "progCourses": [
                    {
                        "id": "DROI-C100",
                        "title": "Droit",
                        "mandatory": True,
                        "bloc": "1",
                        "quadri": "q1",
                    }
                ],
            },
            {
                "anac": "2026",
                "level": "P",
                "blocid": "a2026s2bp",
                "progCourses": [
                    {
                        "id": "DROI-C200",
                        "title": "Droit II",
                        "mandatory": True,
                        "bloc": "2",
                        "quadri": "q2",
                    }
                ],
            },
        ]
    }
    memberships = memberships_for_year(program, data, "2026-2027")
    assert [item["course_code"] for item in memberships] == [
        "DROI-C100",
        "DROI-C200",
    ]


def test_missing_year_stops_program_scrape():
    with pytest.raises(CatalogSourceError, match="requested academic year"):
        memberships_for_year(
            {"slug": "BA-TEST"},
            {"blocs": [{"anac": "2025", "progCourses": []}]},
            "2026-2027",
        )


@pytest.mark.parametrize("program_slug", ["BA-ES3TE", "MA-ARPA", "MA-COME"])
def test_allowlisted_empty_program_is_retained_without_memberships(program_slug):
    assert (
        memberships_for_year({"slug": program_slug}, {"blocs": []}, "2026-2027") == []
    )


def test_allowlisted_discontinued_program_is_retained_without_memberships():
    assert (
        memberships_for_year(
            {"slug": "MA-GEOL"},
            {"blocs": [{"anac": "2025", "progCourses": []}]},
            "2026-2027",
        )
        == []
    )


def test_bogus_parent_retries_without_parent():
    payload = {"json": json.dumps({"blocs": []})}
    session = FakeSession(
        [FakeResponse(status_code=404), FakeResponse(payload=payload)]
    )
    data = fetch_program_content(
        {"slug": "MA-OPTION", "parent": "MA-BOGUS"},
        session=session,
        retries=1,
    )
    assert data == {"blocs": []}
    assert "option%3DMA-OPTION" in session.urls[0][0]
    assert "option%3D" not in session.urls[1][0]


def test_malformed_program_response_is_retried():
    valid = {"json": json.dumps({"blocs": []})}
    session = FakeSession(
        [FakeResponse(payload={"unexpected": True}), FakeResponse(payload=valid)]
    )
    assert fetch_program_content({"slug": "BA-TEST"}, session=session, retries=2) == {
        "blocs": []
    }


def test_membership_normalization_is_deterministic_and_warns():
    memberships, warnings = normalize_memberships(
        [
            {
                "program": "P2",
                "bloc": "2",
                "course_code": "INFO-F100",
                "title": "A title",
                "mandatory": False,
                "quadri": "q2",
            },
            {
                "program": "P1",
                "bloc": "1",
                "course_code": "INFO-F100",
                "title": "Z title",
                "mandatory": True,
                "quadri": "q1",
            },
            {
                "program": "P1",
                "bloc": None,
                "course_code": "CHEM-F100",
                "title": "",
                "mandatory": "yes",
                "quadri": "q3",
            },
            {
                "program": "P3",
                "bloc": "1",
                "course_code": "BAD",
                "title": "Ignored",
                "mandatory": True,
                "quadri": "q1",
            },
        ]
    )
    assert len(memberships) == 3
    info_memberships = [
        item for item in memberships if item["course_code"] == "info-f100"
    ]
    assert {item["title"] for item in info_memberships} == {"Z title"}
    fallback = next(item for item in memberships if item["course_code"] == "chem-f100")
    assert fallback["title"] == "CHEM-F100"
    assert fallback["bloc"] == "U"
    assert fallback["mandatory"] is True
    assert any(warning.startswith("invalid-course-code:") for warning in warnings)
    assert any(warning.startswith("blank-title:") for warning in warnings)
    assert any(warning.startswith("unexpected-mandatory:") for warning in warnings)
    assert any(warning.startswith("unknown-bloc:") for warning in warnings)
    assert any(warning.startswith("conflicting-title:") for warning in warnings)
    assert any(warning.startswith("unresolved-period:") for warning in warnings)


def test_memberships_are_unique_by_program_bloc_and_course():
    membership = {
        "program": "BA-TEST",
        "bloc": "1",
        "course_code": "INFO-F100",
        "title": "Programming",
        "mandatory": True,
        "quadri": "q1",
    }
    memberships, warnings = normalize_memberships([membership, membership, membership])
    assert len(memberships) == 1
    assert warnings == []


def test_period_resolution_known_unknown_and_conflicting_values():
    assert resolve_period({"q1"}) == "Q1"
    assert resolve_period({"q2"}) == "Q2"
    assert resolve_period({"q12"}) == "Y"
    assert resolve_period({"aa"}) == "Y"
    assert resolve_period({"q3"}) is None
    assert resolve_period({"q1", "q2"}) is None


def test_warning_spike_stops_normalization():
    records = [
        {"program": "P", "bloc": "1", "course_code": f"INVALID-{i}"} for i in range(101)
    ]
    with pytest.raises(CatalogSourceError, match="Warning spike"):
        normalize_memberships(records)


def test_snapshot_write_replaces_destination(tmp_path):
    output = tmp_path / "catalog.json"
    output.write_text("old", encoding="utf-8")
    snapshot = {
        "academic_year": "2026-2027",
        "programs": [],
        "memberships": [],
        "warnings": [],
    }
    write_snapshot(snapshot, output)
    assert json.loads(output.read_text(encoding="utf-8")) == snapshot
    assert list(tmp_path.iterdir()) == [output]
