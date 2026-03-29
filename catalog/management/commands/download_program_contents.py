from typing import Any

import json
import logging
from urllib.parse import quote

from django.core.management import BaseCommand

import requests
from rich.progress import MofNCompleteColumn, Progress, SpinnerColumn

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Download course contents for all programs from ULB API"

    def handle(self, *args: Any, **options: Any) -> None:
        with open("csv/programs.json") as f:
            programs: list[dict] = json.load(f)
        logger.info("Listing the course content of all programs...")

        failed: list = []
        program_content: dict[str, dict[str, dict]] = {}
        with Progress(
            SpinnerColumn(),
            *Progress.get_default_columns(),
            MofNCompleteColumn(),
        ) as progress:
            task1 = progress.add_task("Processing programs...", total=len(programs))

            for progam in programs:
                slug_upper = progam["slug"].upper()
                progress.update(
                    task1,
                    advance=1,
                    description=f"Listing content of {slug_upper}...",
                )

                if "parent" in progam:
                    qs = f"/ksup/programme?gen=prod&anet={progam['parent'].upper()}&option={slug_upper}&lang=fr"
                else:
                    qs = f"/ksup/programme?gen=prod&anet={slug_upper}&lang=fr"

                URL = f"https://www.ulb.be/api/formation?path={quote(qs)}"
                try:
                    response = requests.get(URL)
                    if not response.ok:
                        if "parent" in progam:
                            # Utilisation de logger.warning pour les sauts/retries
                            logger.warning(
                                "Skip: %s with bogus parent %s. Retrying...",
                                slug_upper,
                                progam["parent"].upper(),
                            )

                            qs = f"/ksup/programme?gen=prod&anet={slug_upper}&lang=fr"
                            URL = f"https://www.ulb.be/api/formation?path={quote(qs)}"
                            response = requests.get(URL)
                            if not response.ok:
                                logger.error("Retry failed for %s", slug_upper)
                                continue
                        else:
                            logger.error(
                                "%s failed with %s. URL: %s",
                                slug_upper,
                                response.status_code,
                                URL,
                            )
                            continue

                except Exception:
                    logger.exception("Failed to GET %s. URL: %s", slug_upper, URL)
                    continue

                try:
                    programme_json = json.loads(response.json()["json"])
                    program_content[progam["slug"]] = {}

                    if len(programme_json["blocs"]) == 0:
                        continue

                    for course in programme_json["blocs"][-1]["progCourses"]:
                        if course["id"] not in ["TEMP-0000", "HULB-0000"]:
                            program_content[progam["slug"]][course["id"]] = {
                                "id": course["id"],
                                "title": course["title"],
                                "mandatory": course["mandatory"],
                                "bloc": course["bloc"],
                                "lecturers": course["lecturers"],
                                "quadri": course["quadri"],
                            }
                except Exception:
                    failed.append(progam["slug"])
                    logger.exception(
                        "Error while listing content of %s", progam["slug"]
                    )

        with open("csv/courses.json", "w+") as all_courses_json:
            json.dump(program_content, all_courses_json, indent=2)

        logger.info("Course content download complete. Saved to csv/courses.json")
