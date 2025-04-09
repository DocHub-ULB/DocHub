# Changelog

This page tries to contain all changes made on DocHub.

# 2025.4.0

 * Switch to UV as the package manager
 * Upgrade dependencies
 * Switch to Python 3.13
 * Remove deprecated `filemagic` and replace with `python-magic`
 * Remove unmaintained docker compose setup

# 2024.3.0 

 * Upgrade JS libraries (notable change is Turbo 8)
 * Add view transitions (fancy animations when changing pages)
 * Allow uploading documents on archived courses (but with a warning)
 * Usual python packages update

# 2023.9.0 - Codename NEWTREE

We are now using the new tree !

 * The old tree is still available, in an "archives" root category
 * Categories and courses now have an "is_archive" flag
 * A link to the archives is available in the finder
 * Courses in the archive with no documents were deleted as they have no value and clutter the search
 * When a course is empty, we suggest looking in the archives
 * The finder now shows icons for faculties, to separate masters from bachelors, ...

Bonuses:

 * Improve `better_name()` so the tree is nicer
 * In the document list, make it clear that imported documents are imported
 * Packages update

# 2023.7.0

 * Show real thumbnails for the documents
 * In catalog, order documents by creation date, not edition

# 2023.6.0

 * Show hidden document to the authors/admin and allow modification of this state
 * Add course slug to the display of "Documents récents"
 * Fix makefile to load correctly the tree & the courses

# 2023.5.0

 * Add CHANGELOG.md and CONTRIBUTING.md
 * Remove unused dependency on `markdown`
 * Package upgrade
 * Add a "staff pick" label on Documents replacing the old confusion between certified and "officiel" tags
 * Switch to psycopg3
 * Add a notice that it is not a ULB website and that students should use the UV
 * Add a notice reminding users that copyright law is still applicable

# 2023.2.0

 * Remove conditional import of "magic" as the compatibility issue disappeared
 * Update dependencies
