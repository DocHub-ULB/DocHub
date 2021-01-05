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
	virtualenv ve

packages: ve
	ve/bin/pip install -r requirements.txt
	chmod +x ./manage.py

database:
	$(PY) manage.py migrate -v 0
	@echo "Creating user ${USER} with password 'test'"
	$(PY) manage.py createsuperuser --netid=${USER} --first_name=Gaston --last_name=Lagaffe --email=${USER}@fake.ulb.ac.be --noinput
	@echo "from users.models import User; u=User.objects.get(netid='${USER}'); u.set_password('test'); u.save()" | $(PY) manage.py shell > /dev/null

	@echo "Loading an minimal course tree"
	$(PY) manage.py loadtree catalog/management/devtree.yaml

	@echo "Creating some tags"
	@echo "[__import__('tags').models.Tag.objects.create(name=x) for x in ('syllabus', 'officiel', 'examen')]" | $(PY) manage.py shell > /dev/null
