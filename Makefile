PY = uv run

CURRENT_USER = $(USER)

.PHONY: init database catalog-rebuild catalog-refresh clean

init: database

database:
	$(PY) manage.py migrate -v 0
	
	@echo "--- Starting database initialization ---"

	@echo "Creating user $(CURRENT_USER) with password 'test' (Super Admin & Staff)"
	@echo "from users.models import User; u, _ = User.objects.get_or_create(netid='$(CURRENT_USER)', defaults={'first_name': 'Gaston', 'last_name': 'Lagaffe', 'email': '$(CURRENT_USER)@fake.ulb.ac.be'}); u.set_password('test'); u.is_staff=True; u.is_superuser=True; u.save()" | $(PY) manage.py shell > /dev/null

	@echo "Creating user blabevue with password 'test'"
	@echo "from users.models import User; u, _ = User.objects.get_or_create(netid='blabevue', defaults={'first_name': 'Bertrand', 'last_name': 'Labevue', 'email': 'blabevue@fake.ulb.ac.be'}); u.set_password('test'); u.save()" | $(PY) manage.py shell > /dev/null

	@echo "Creating some tags"
	@echo "from tags.models import Tag; [Tag.objects.get_or_create(name=x) for x in ('syllabus', 'officiel', 'examen', 'resume', 'synthese', 'notes')]" | $(PY) manage.py shell > /dev/null
	
	@echo "Loading the fake catalog (archived 2024-2025, then active 2025-2026)"
	$(PY) manage.py sync_catalog catalog/ingest/seed/seed_catalog_2024_2025.json --apply > /dev/null
	$(PY) manage.py sync_catalog catalog/ingest/seed/seed_catalog_2025_2026.json --apply > /dev/null

	@echo "Adding some fake documents"
	$(PY) manage.py create_fake_doc
	@echo ""
	@echo "Done : the database is ready to use"
	@echo "make run to start the development server"
	@echo "Admin user: $(CURRENT_USER) / test"
	@echo "Other user: blabevue / test"

run:
	$(PY) manage.py runserver

catalog-rebuild:
	./scripts/rebuild_local_catalog

catalog-refresh:
	./scripts/rebuild_local_catalog --refresh-snapshot

clean:
	@echo "Cleaning up the environment..."
	rm -f db.sqlite
	@echo "Cleaning up Python cache..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo "Environment cleaned up successfully."
