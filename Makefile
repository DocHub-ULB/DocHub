PY=uv run

.PHONY: init database

init: database

database:
	$(PY) manage.py migrate -v 0
	@echo "Creating root category (ULB)"
	@echo "from catalog.models import Category; Category.objects.get_or_create(slug='ULB', defaults={'name': 'ULB'})" | $(PY) manage.py shell > /dev/null
	@echo "Creating user ${USER} with password 'test'"
	@echo "from users.models import User; u, _ = User.objects.get_or_create(netid='${USER}', defaults={'first_name': 'Gaston', 'last_name': 'Lagaffe', 'email': '${USER}@fake.ulb.ac.be'}); u.set_password('test'); u.is_moderator=True; u.save()" | $(PY) manage.py shell > /dev/null
	@echo "Creating user blabevue with password 'test'"
	@echo "from users.models import User; u, _ = User.objects.get_or_create(netid='blabevue', defaults={'first_name': 'Bertrand', 'last_name': 'Labevue', 'email': 'blabevue@fake.ulb.ac.be'}); u.set_password('test'); u.save()" | $(PY) manage.py shell > /dev/null
	@echo "Creating some tags"
	@echo "from tags.models import Tag; [Tag.objects.get_or_create(name=x) for x in ('syllabus', 'officiel', 'examen', 'resume', 'synthese', 'notes')]" | $(PY) manage.py shell > /dev/null
	@echo "Loading tree and courses..."
	$(PY) manage.py load_tree
	$(PY) manage.py load_courses
	@echo "Adding some fake documents"
	$(PY) manage.py create_fake_doc
	@echo ""
	@echo "Done! Run: uv run python manage.py runserver"