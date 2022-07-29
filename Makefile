ifeq ($(CI),true)
    PY=python
else
ifndef VIRTUAL_ENV
PY=ve/bin/python
else
PY=python
endif
endif

init: database

install: packages

ve:
	python -m venv ve

packages: ve
	ve/bin/pip install -r requirements.txt

database:
	$(PY) manage.py migrate -v 0
	@echo "Creating user ${USER} with password 'test'"
	$(PY) manage.py createsuperuser --netid=${USER} --first_name=Gaston --last_name=Lagaffe --email=${USER}@fake.ulb.ac.be --noinput
	@echo "from users.models import User; u=User.objects.get(netid='${USER}'); u.set_password('test'); u.save()" | $(PY) manage.py shell > /dev/null

	@echo "Creating user blabevue with password 'test'"
	$(PY) manage.py createsuperuser --netid=blabevue --first_name=Bertrand --last_name=Labevue --email=blabevue@fake.ulb.ac.be --noinput
	@echo "from users.models import User; u=User.objects.get(netid='blabevue'); u.set_password('test'); u.save()" | $(PY) manage.py shell > /dev/null

	@echo "Loading an minimal course tree"
	$(PY) manage.py shell < ./catalog/management/parser/load_courses.py

	@echo "Creating some tags"
	@echo "[__import__('tags').models.Tag.objects.create(name=x) for x in ('syllabus', 'officiel', 'examen', 'resume', 'synthese', 'notes')]" | $(PY) manage.py shell > /dev/null

	@echo "Adding some fake document"
	$(PY) manage.py create_fake_doc

	@echo "Your DB should be ready now. Run the server with ./manage.py runserver"
