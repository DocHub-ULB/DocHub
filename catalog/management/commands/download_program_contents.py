import json
from urllib.parse import quote

from django.core.management import BaseCommand

import requests
from rich import print
from rich.progress import MofNCompleteColumn, Progress, SpinnerColumn

from www.logger_settings import logger


class Command(BaseCommand):
    help = ""

    def handle(self, *args, **options):
        with open("programs.json") as f:
            programs: list[dict] = json.load(f)
        logger.debug("\n[bold blue]Listing the course content of all programs...[/]\n")

        failed: list = []
        program_content: dict[str, dict[str, dict]] = {}

        # programs = [p for p in programs if p["slug"] in ["BA-GEOG"]]

        with Progress(
            SpinnerColumn(),
            *Progress.get_default_columns(),
            MofNCompleteColumn(),
        ) as progress:
            task1 = progress.add_task(
                "Listing the course content of all programs...", total=len(programs)
            )

            for progam in programs:
                progress.update(
                    task1,
                    advance=1,
                    description=f"Listing the course content of {progam['slug'].upper()}...",
                )
                if "parent" in progam:
                    qs = f"/ksup/programme?gen=prod&anet={progam['parent'].upper()}&option={progam['slug'].upper()}&lang=fr"
                else:
                    qs = f"/ksup/programme?gen=prod&anet={progam['slug'].upper()}&lang=fr"

                URL = f"https://www.ulb.be/api/formation?path={quote(qs)}"
                try:
                    response = requests.get(URL)
                    if not response.ok:
                        if "parent" in progam:
                            logger.debug(
                                f"[yellow]Skip:[/] [magenta]{progam['slug'].upper()}[/] with bogus parent {progam['parent'].upper()}"
                            )
                        else:
                            logger.debug(
                                f"[red]Error:[/] [magenta]{progam['slug'].upper()}[/] failed with {response.status_code}"
                            )
                            logger.debug("  ", URL)
                        continue

                except Exception as e:
                    logger.debug(
                        f"[red]Error:[/] Failed to GET {progam['slug'].upper()}"
                    )
                    logger.debug("  URL", URL)
                    progress.console.print_exception()
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
                except Exception as e:
                    failed.append(progam["slug"])
                    logger.debug(f"Error while listing content of {progam['slug']}")
                    progress.console.print_exception()

        with open(
            "catalog/management/parser/data/courses.json", "w+"
        ) as all_courses_json:
            json.dump(program_content, all_courses_json, indent=2)
