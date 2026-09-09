# Refreshing the ULB catalog

Network work and database changes are deliberately separate. First create one
snapshot for the requested academic year:

```shell
DB_URL=postgres:///dochub uv run manage.py scrape_catalog \
  --academic-year 2026-2027 \
  --output catalog-2026-2027.json
```

Review the file and run the read-only comparison:

```shell
DB_URL=postgres:///dochub uv run manage.py sync_catalog catalog-2026-2027.json
```

Apply that exact snapshot only after reviewing the preview:

```shell
DB_URL=postgres:///dochub uv run manage.py sync_catalog \
  catalog-2026-2027.json \
  --apply
```

The apply runs in one transaction. Missing courses are archived, never deleted.
The snapshot's academic year must be strictly newer than the active edition:
the active edition is archived and the snapshot becomes the new active one.
Same-year and older snapshots are refused for now.

## Rebuilding the local database

For a fast, repeatable local rehearsal, restore the production-copy backup and
replay the reviewed snapshot in one command:

```shell
make catalog-rebuild
```

This command replaces only the local `postgres:///dochub` database, applies
migrations, creates or updates the `$USER` staff account with password `test`,
previews the catalog changes, and applies the snapshot. Replaying the snapshot
makes no ULB requests; it acts as the recorded response for the import.

To deliberately fetch a new snapshot before applying it:

```shell
make catalog-refresh
```

The defaults can be overridden with `CATALOG_DB_BACKUP`, `CATALOG_SNAPSHOT`,
and `CATALOG_ACADEMIC_YEAR`. The safety check intentionally does not allow the
script to restore any database other than `postgres:///dochub`.
