ifeq ($(TRAVIS),true)
    PY=python
else
    PY=ve/bin/python
endif

init: database

install: packages

ve:
	python2.7 `(which virtualenv || which virtualenv2) | tail -1` --distribute --no-site-package ve

packages: ve
	ve/bin/pip install -r requirements.txt
	chmod +x ./manage.py

database:
	$(PY) manage.py migrate -v 0
	@echo "Creating user ${USER} with password 'test'"
	$(PY) manage.py createsuperuser --netid=${USER} --first_name=Gaston --last_name=Lagaffe --email=${USER}@fake.ulb.ac.be --noinput
	@echo "from users.models import User; u=User.objects.get(netid='${USER}'); u.set_password('test'); u.save()" | $(PY) manage.py shell > /dev/null

	@echo "Creating second user blabevue with password 'test'"
	$(PY) manage.py createuser --netid=blabevue --password=test --first-name=Bertrand --last-name=Labevue

	@echo "Loading an minimal course tree"
	$(PY) manage.py loadtree --tree catalog/management/devtree.yaml

	@echo "Creating some tags"
	@echo "from tags.models import Tag; [Tag.objects.create(name=x) for x in ('syllabus', 'officiel', 'examen')]" | $(PY) manage.py shell > /dev/null
