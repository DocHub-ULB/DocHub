from typing import Any

import json
from urllib.parse import quote

from django.core.management import BaseCommand

import requests
from rich import print
from rich.progress import MofNCompleteColumn, Progress, SpinnerColumn


class Command(BaseCommand):
    help = "Fetch course content for each program from ULB API and save to csv/courses.json"

    def handle(self, *args: Any, **options: Any) -> None:
        """
        For each program in csv/programs.json, fetches its course content from ULB API.

        Programs that are "options" (specializations) have a "parent" field and require
        both the parent slug and option slug in the API call. If that fails, we retry
        with just the option slug.
        """
        with open("csv/programs.json") as f:
            programs: list[dict] = json.load(f)
        print("\n[bold blue]Listing the course content of all programs...[/]\n")

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

                # Build API query string
                # If this is an option/specialization (has a parent), include both parent and option
                # Otherwise, just query by the program slug
                is_option = "parent" in progam

                if is_option:
                    # Format: ?anet=PARENT_SLUG&option=OPTION_SLUG
                    qs = f"/ksup/programme?gen=prod&anet={progam['parent'].upper()}&option={progam['slug'].upper()}&lang=fr"
                else:
                    # Format: ?anet=PROGRAM_SLUG
                    qs = f"/ksup/programme?gen=prod&anet={progam['slug'].upper()}&lang=fr"

                URL = f"https://www.ulb.be/api/formation?path={quote(qs)}"
                try:
                    response = requests.get(URL)
                    if not response.ok:
                        # If this is an option and the parent+option query failed,
                        # retry with just the option slug (parent might be invalid)
                        if is_option:
                            print(
                                f"[yellow]Failed to fetch option with parent:[/] "
                                f"[magenta]{progam['slug'].upper()}[/] (parent: {progam['parent'].upper()})"
                            )

                            print("[yellow]Retrying without parent parameter...[/] ")
                            qs = f"/ksup/programme?gen=prod&anet={progam['slug'].upper()}&lang=fr"
                            URL = f"https://www.ulb.be/api/formation?path={quote(qs)}"
                            response = requests.get(URL)
                            if not response.ok:
                                print(
                                    f"[red]Failed with status {response.status_code}[/]"
                                )
                                continue
                            else:
                                print("[green]Success[/]")

                        else:
                            print(
                                f"[red]Error:[/] [magenta]{progam['slug'].upper()}[/] failed with {response.status_code}"
                            )
                            print("  ", URL)
                            continue

                except Exception:
                    print(f"[red]Error:[/] Failed to GET {progam['slug'].upper()}")
                    print("  URL", URL)
                    progress.console.print_exception()
                    continue

                try:
                    programme_json = json.loads(response.json()["json"])
                    program_content[progam["slug"]] = {}

                    if len(programme_json["blocs"]) == 0:
                        continue

                    # Extract courses from the last bloc (final year)
                    # Each bloc represents a year in the program
                    last_bloc = programme_json["blocs"][-1]

                    for course in last_bloc["progCourses"]:
                        # Skip placeholder courses (TEMP-0000, HULB-0000)
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
                    print(f"Error while listing content of {progam['slug']}")
                    progress.console.print_exception()

        with open("csv/courses.json", "w+") as all_courses_json:
            json.dump(program_content, all_courses_json, indent=2)
