import json
import re

from django.core.management import BaseCommand

import requests
from bs4 import BeautifulSoup
from rich import print
import logging
from rich.progress import MofNCompleteColumn, Progress, SpinnerColumn


class Command(BaseCommand):
    help = ""

    PAGE_SIZE = 20

    URL = f"https://www.ulb.be/servlet/search?beanKey=beanKeyRechercheFormation&types=formation&natureFormation=ulb&s=FACULTE_ASC&limit={PAGE_SIZE}"

    def handle(self, *args, **options):
        programs = []

        parent_programs: set[str] = set()
        logging.debug("[bold blue]Gathering the list of available programs...[/]\n")

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
                            "strong", "search-result__structure-intitule"
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

                        if option_div := mnemonic_span.find_previous(
                            "div", "search-result__resultat--fille"
                        ):
                            parent_program_div = option_div.find_previous(
                                "div", "search-result__result-item"
                            )
                            parent_mnemonic_span = parent_program_div.find(
                                "span", "search-result__mnemonique"
                            )
                            p["parent"] = parent_mnemonic_span.text
                            parent_programs.add(parent_mnemonic_span.text)

                        programs.append(p)
                    else:
                        progress.console.print(
                            f"Skipping already seen [magenta]{mnemonic_span.text}"
                        )
                progress.update(task1, completed=self.PAGE_SIZE * page)
                page += 1

        logging.debug(
            f"Found {len(parent_programs)} programs containing options, ignoring those..."
        )
        logging.debug(parent_programs)
        programs = [p for p in programs if p["slug"] not in parent_programs]

        logging.debug(f"Found {len(programs)} distinct programs, dumping to json...")
        with open("programs.json", "w") as f:
            json.dump(programs, f, indent=4)
