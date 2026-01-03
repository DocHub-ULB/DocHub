# mypy: disable-error-code="union-attr, arg-type"
from typing import Any

import json
import re

from django.core.management import BaseCommand

import requests
from bs4 import BeautifulSoup
from rich import print
from rich.progress import MofNCompleteColumn, Progress, SpinnerColumn


class Command(BaseCommand):
    help = "Scrape all academic programs from ULB website and save to csv/programs.json"

    PAGE_SIZE = 20

    URL = f"https://www.ulb.be/servlet/search?beanKey=beanKeyRechercheFormation&types=formation&natureFormation=ulb&s=FACULTE_ASC&limit={PAGE_SIZE}"

    def handle(self, *args: Any, **options: Any) -> None:
        """
        Scrapes ULB search results to build a list of academic programs.

        Some programs are "parent programs" that exist only to group related options.
        For example, a Master's program might have multiple specializations (options).
        We filter out these parent programs and only keep the actual options that students
        can enroll in.
        """
        programs: list[dict] = []

        # Track programs that are containers for options (these will be filtered out)
        parent_program_slugs: set[str] = set()
        print("[bold blue]Gathering the list of available programs...[/]\n")

        with Progress(
            SpinnerColumn(),
            *Progress.get_default_columns(),
            MofNCompleteColumn(),
        ) as progress:
            result_count = None
            page = 1
            last_page = float("inf")
            task1 = progress.add_task(
                "Listing available programs...", total=result_count
            )
            progress.console.print(
                "Querying ULB a first time to count the number of programs available..."
            )
            while page < last_page:
                response = requests.get(self.URL + f"&page={page}")
                soup = BeautifulSoup(response.content, "html.parser")

                if result_count is None:
                    result_count_text = (
                        soup.find("div", {"class": "search-metadata__search-title"})
                        .text.replace("\n", "")
                        .replace("\t", "")
                    )
                    if match := re.search(
                        r"a( +)donné( +)(?P<count>\d+)( +)résultats", result_count_text
                    ):
                        result_count = int(match.group("count"))

                    else:
                        raise Exception(
                            f"Could not parse result count ({result_count_text})"
                        )
                    last_page = int(result_count / self.PAGE_SIZE) + 1
                    progress.console.print(
                        f"Found {result_count} programs on {last_page} pages..."
                    )
                    progress.update(task1, total=result_count)

                for mnemonic_span in soup.find_all(
                    "span", {"class": "search-result__mnemonique"}
                ):
                    known_slugs = {program["slug"] for program in programs}
                    if mnemonic_span.text not in known_slugs:
                        fac = mnemonic_span.find_previous_siblings("a")
                        program_name = mnemonic_span.find_previous(
                            "strong", {"class": "search-result__structure-intitule"}
                        ).text

                        faculties: list = []
                        for elem in fac:
                            children = elem.findChildren()
                            faculties.append(
                                {
                                    "color": children[0]["style"][-7:],
                                    "name": children[1].text,
                                }
                            )

                        p = {
                            "slug": mnemonic_span.text,
                            "name": program_name,
                            "faculty": faculties,
                        }

                        # Check if this is an "option" (specialization) of a parent program
                        # The HTML structure uses "resultat--fille" (child result) to indicate options
                        if option_div := mnemonic_span.find_previous(
                            "div", {"class": "search-result__resultat--fille"}
                        ):
                            # Find the parent program that contains this option
                            parent_program_div = option_div.find_previous(
                                "div", {"class": "search-result__result-item"}
                            )
                            parent_mnemonic_span = parent_program_div.find(
                                "span", {"class": "search-result__mnemonique"}
                            )
                            parent_slug = parent_mnemonic_span.text

                            # Store the parent reference for API calls later
                            p["parent"] = parent_slug

                            # Mark this parent as a container (to be filtered out later)
                            parent_program_slugs.add(parent_slug)

                        programs.append(p)
                    else:
                        progress.console.print(
                            f"Skipping already seen [magenta]{mnemonic_span.text}"
                        )
                progress.update(task1, completed=self.PAGE_SIZE * page)
                page += 1

        # Filter out parent programs that are just containers for options
        # We only want the actual enrollable programs (the options themselves)
        print(
            f"Found {len(parent_program_slugs)} parent programs that contain options, filtering them out..."
        )
        print(f"Parent programs to exclude: {parent_program_slugs}")

        enrollable_programs = [
            p for p in programs if p["slug"] not in parent_program_slugs
        ]

        print(
            f"Found {len(enrollable_programs)} enrollable programs, saving to csv/programs.json..."
        )
        with open("csv/programs.json", "w") as f:
            json.dump(enrollable_programs, f, indent=4)
