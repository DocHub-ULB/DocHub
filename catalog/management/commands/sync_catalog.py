from typing import Any

from django.core.management.base import BaseCommand, CommandError, CommandParser

from catalog.ingest.sync import (
    SnapshotError,
    apply_snapshot,
    compare_snapshot,
    format_comparison,
    load_snapshot,
)


class Command(BaseCommand):
    help = "Preview or transactionally apply a ULB catalog snapshot"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("snapshot")
        parser.add_argument("--apply", action="store_true")

    def handle(self, *args: Any, **options: Any) -> None:
        try:
            snapshot = load_snapshot(options["snapshot"])
            comparison = compare_snapshot(snapshot)
            self.stdout.write(format_comparison(comparison))
            if not options["apply"]:
                self.stdout.write("\nRead-only preview; no database changes were made.")
                return
            apply_snapshot(snapshot)
        except SnapshotError as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(self.style.SUCCESS("\nCatalog sync applied successfully."))
