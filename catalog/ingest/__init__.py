"""Once-a-year ULB catalog ingestion: scraping the source and syncing snapshots.

This subpackage is deliberately kept apart from the day-to-day catalog code
(``models``, ``views``, ``urls``). Nothing here runs on a normal request; it is
only used by the ``scrape_catalog`` and ``sync_catalog`` management commands
when a new academic year is imported.
"""
