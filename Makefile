ifeq ($(CI),true)
    PY=python3
else
ifndef VIRTUAL_ENV
PY=ve/bin/python
else
PY=python3
endif
endif

init: database

install: packages

ve:
	$(PY) -m venv ve

packages: ve
	ve/bin/pip install -r requirements.txt

database:
	$(PY) manage.py migrate -v 0
	@echo "Creating user ${USER} with password 'test'"
	@echo "from users.models import User; u=User.objects.get_or_create(netid='${USER}', first_name='Gaston', last_name='Lagaffe', email='${USER}@fake.ulb.ac.be'); u[0].set_password('test'); u[0].save()" | $(PY) manage.py shell > /dev/null

	@echo "Creating user blabevue with password 'test'"
	@echo "from users.models import User; u=User.objects.get_or_create(netid='blabevue', first_name='Bertrand', last_name='Labevue', email='blabevue@fake.ulb.ac.be'); u[0].set_password('test'); u[0].save()" | $(PY) manage.py shell > /dev/null

	@echo "Loading an minimal course tree"
	$(PY) manage.py load_tree
	$(PY) manage.py load_courses

	@echo "Creating some tags"
	@echo "[__import__('tags').models.Tag.objects.create(name=x) for x in ('syllabus', 'officiel', 'examen', 'resume', 'synthese', 'notes')]" | $(PY) manage.py shell > /dev/null

	@echo "Adding some fake document"
	$(PY) manage.py create_fake_doc

	@echo "Your DB should be ready now. Run the server with ./manage.py runserver"
