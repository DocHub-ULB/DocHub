# mypy: disable-error-code="union-attr, arg-type"
from typing import Any

import json
import logging
import re

from django.core.management import BaseCommand

import requests
from bs4 import BeautifulSoup
from rich.progress import MofNCompleteColumn, Progress, SpinnerColumn

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Download the list of available programs from ULB"

    PAGE_SIZE = 20
    URL = f"https://www.ulb.be/servlet/search?beanKey=beanKeyRechercheFormation&types=formation&natureFormation=ulb&s=FACULTE_ASC&limit={PAGE_SIZE}"

    def handle(self, *args: Any, **options: Any) -> None:
        programs: list[dict] = []
        parent_programs: set[str] = set()

        logger.info("Gathering the list of available programs...")

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

            logger.info(
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

                    logger.info(
                        "Found %s programs on %s pages...", result_count, last_page
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
                        if option_div := mnemonic_span.find_previous(
                            "div", {"class": "search-result__resultat--fille"}
                        ):
                            parent_program_div = option_div.find_previous(
                                "div", {"class": "search-result__result-item"}
                            )
                            parent_mnemonic_span = parent_program_div.find(
                                "span", {"class": "search-result__mnemonique"}
                            )
                            p["parent"] = parent_mnemonic_span.text
                            parent_programs.add(parent_mnemonic_span.text)

                        programs.append(p)
                    else:
                        logger.debug("Skipping already seen %s", mnemonic_span.text)
                progress.update(task1, completed=self.PAGE_SIZE * page)
                page += 1

        logger.info(
            "Found %s programs containing options, ignoring those...",
            len(parent_programs),
        )
        logger.debug("Ignored programs: %s", parent_programs)
        programs = [p for p in programs if p["slug"] not in parent_programs]

        logger.info("Found %s distinct programs, dumping to json...", len(programs))
        with open("csv/programs.json", "w") as f:
            json.dump(programs, f, indent=4)
