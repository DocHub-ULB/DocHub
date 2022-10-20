POETRY := $(shell command -v poetry 2> /dev/null)

init: database

install:
	$(POETRY) install --without prod,test

database:
	$(POETRY) run ./manage.py migrate -v 0
	@echo "Creating user ${USER} with password 'test'"
	$(POETRY) run ./manage.py createsuperuser --netid=${USER} --first_name=Gaston --last_name=Lagaffe --email=${USER}@fake.ulb.ac.be --noinput
	@echo "from users.models import User; u=User.objects.get(netid='${USER}'); u.set_password('test'); u.save()" | $(POETRY) run ./manage.py shell > /dev/null

	@echo "Creating user blabevue with password 'test'"
	$(POETRY) run ./manage.py createsuperuser --netid=blabevue --first_name=Bertrand --last_name=Labevue --email=blabevue@fake.ulb.ac.be --noinput
	@echo "from users.models import User; u=User.objects.get(netid='blabevue'); u.set_password('test'); u.save()" | $(POETRY) run ./manage.py shell > /dev/null

	@echo "Loading an minimal course tree"
	$(POETRY) run ./manage.py shell < ./catalog/management/commands/load_tree.py
	$(POETRY) run ./manage.py shell < ./catalog/management/commands/load_courses.py

	@echo "Creating some tags"
	@echo "[__import__('tags').models.Tag.objects.create(name=x) for x in ('syllabus', 'officiel', 'examen', 'resume', 'synthese', 'notes')]" | $(POETRY) run ./manage.py shell > /dev/null

	@echo "Adding some fake document"
	$(POETRY) run ./manage.py create_fake_doc

	@echo "Your DB should be ready now. Run the server with ./manage.py runserver"
