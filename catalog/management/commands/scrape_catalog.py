from typing import Any

import requests
from django.core.management.base import BaseCommand, CommandError, CommandParser

from catalog.ingest.ulb_catalog import (
    CatalogSourceError,
    scrape_catalog,
    write_snapshot,
)


class Command(BaseCommand):
    help = "Scrape a complete ULB academic-year catalog into one JSON snapshot"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--academic-year", required=True)
        parser.add_argument("--output", required=True)
        parser.add_argument("--timeout", type=float, default=20)
        parser.add_argument("--retries", type=int, default=3)
        parser.add_argument("--minimum-programs", type=int, default=100)
        parser.add_argument("--minimum-memberships", type=int, default=1000)

    def handle(self, *args: Any, **options: Any) -> None:
        if options["retries"] < 1:
            raise CommandError("--retries must be at least 1.")
        if options["timeout"] <= 0:
            raise CommandError("--timeout must be positive.")
        try:
            with requests.Session() as session:
                snapshot = scrape_catalog(
                    options["academic_year"],
                    session=session,
                    timeout=options["timeout"],
                    retries=options["retries"],
                    minimum_programs=options["minimum_programs"],
                    minimum_memberships=options["minimum_memberships"],
                )
            write_snapshot(snapshot, options["output"])
        except CatalogSourceError as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(
            self.style.SUCCESS(
                f"Wrote {len(snapshot['programs'])} programs and "
                f"{len(snapshot['memberships'])} memberships to {options['output']}."
            )
        )
        if snapshot["warnings"]:
            self.stdout.write(
                self.style.WARNING(f"Scrape warnings: {len(snapshot['warnings'])}")
            )
