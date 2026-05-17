PY = uv run

CURRENT_USER = $(USER)

.PHONY: init database clean

init: database

database:
	$(PY) manage.py migrate -v 0
	
	@echo "--- Starting database initialization ---"
	
	@echo "Creating root category (ULB)"
	@echo "from catalog.models import Category; Category.objects.get_or_create(slug='ULB', defaults={'name': 'ULB'})" | $(PY) manage.py shell > /dev/null

	@echo "Creating user $(CURRENT_USER) with password 'test' (Super Admin & Staff)"
	@echo "from users.models import User; u, _ = User.objects.get_or_create(netid='$(CURRENT_USER)', defaults={'first_name': 'Gaston', 'last_name': 'Lagaffe', 'email': '$(CURRENT_USER)@fake.ulb.ac.be'}); u.set_password('test'); u.is_staff=True; u.is_superuser=True; u.save()" | $(PY) manage.py shell > /dev/null

	@echo "Creating user blabevue with password 'test'"
	@echo "from users.models import User; u, _ = User.objects.get_or_create(netid='blabevue', defaults={'first_name': 'Bertrand', 'last_name': 'Labevue', 'email': 'blabevue@fake.ulb.ac.be'}); u.set_password('test'); u.save()" | $(PY) manage.py shell > /dev/null

	@echo "Creating some tags"
	@echo "from tags.models import Tag; [Tag.objects.get_or_create(name=x) for x in ('syllabus', 'officiel', 'examen', 'resume', 'synthese', 'notes')]" | $(PY) manage.py shell > /dev/null
	
	@echo "--- Uploading data from CSV files ---"
	@if [ -f "csv/programs.json" ]; then \
		$(PY) manage.py load_tree; \
	else \
		echo "Warning: csv/programs.json not found, skipping load_tree"; \
	fi
	
	@if [ -f "csv/courses.json" ]; then \
		$(PY) manage.py load_courses; \
	else \
		echo "Warning: csv/courses.json not found, skipping load_courses"; \
	fi

	@echo "Adding some fake documents"
	$(PY) manage.py create_fake_doc
	@echo ""
	@echo "Done : the database is ready to use"
	@echo "make run to start the development server"
	@echo "Admin user: $(CURRENT_USER) / test"
	@echo "Other user: blabevue / test"

run:
	$(PY) manage.py runserver

clean:
	@echo "Cleaning up the environment..."
	rm -f db.sqlite
	@echo "Cleaning up Python cache..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo "Environment cleaned up successfully."