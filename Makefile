ifeq ($(TRAVIS),true)
    PY=python
else
    PY=ve/bin/python
endif

init: database

install: packages shower

ve:
	python2.7 `(which virtualenv || which virtualenv2) | tail -1` --distribute --no-site-package ve

packages: ve
	ve/bin/pip install -r requirements.txt
	chmod +x ./manage.py


cleandata:
	rm -f db.sqlite
	rm -rf graph.png
	rm -rf www/secret_key.txt
	rm -rf media/documents/
	rm -rf media/original_document/
	rm -rf media/page_120/
	rm -rf media/page_600/
	rm -rf media/page_900/
	rm -rf media/pdf_document/
	rm -rf media/profile/

database:
	$(PY) manage.py migrate
	@echo "Creating user ${USER} with password 'test'"
	$(PY) manage.py createsuperuser --netid=${USER} --first_name=Gaston --last_name=Lagaffe --email=${USER}@fake.ulb.ac.be --noinput
	@echo "from users.models import User; u=User.objects.get(netid='${USER}'); u.set_password('test'); u.save()" | $(PY) manage.py shell > /dev/null

	@echo "Creating second user blabevue with password 'test'"
	$(PY) manage.py createuser --netid=blabevue --password=test --first-name=Bertrand --last-name=Labevue

	@echo "Loading an minimal course tree"
	$(PY) manage.py loadtree --tree catalog/management/devtree.yaml

	@echo "Creating some tags"
	@echo "from tags.models import Tag; [Tag.objects.create(name=x) for x in ('syllabus', 'officiel', 'examen')]" | $(PY) manage.py shell > /dev/null

shower: foundation foundation-icons select cookie

foundation: static/3party/foundation

static/3party/foundation:
	wget http://foundation.zurb.com/cdn/releases/foundation-5.5.2.zip -O /tmp/foundation.zip
	rm -rf /tmp/foundation
	mkdir /tmp/foundation && true
	unzip /tmp/foundation.zip -d /tmp/foundation
	rm /tmp/foundation/index.html /tmp/foundation/humans.txt /tmp/foundation/robots.txt
	mv  /tmp/foundation static/3party/

foundation-icons: static/3party/foundation-icons

ICONEXT=css eot svg ttf woff
ICONFILES=$(addprefix /tmp/foundation-icons/foundation-icons/foundation-icons., ${ICONEXT})

static/3party/foundation-icons:
	wget http://zurb.com/playground/uploads/upload/upload/288/foundation-icons.zip -O /tmp/foundation-icons.zip
	rm -rf /tmp/foundation-icons
	mkdir /tmp/foundation-icons && true
	unzip /tmp/foundation-icons.zip -d /tmp/foundation-icons > /dev/null
	@mkdir static/3party/foundation-icons && true
	mv ${ICONFILES} static/3party/foundation-icons

select: static/3party/select

SELECT=select2-spinner.gif select2.css select2.js select2.png select2_locale_fr.js select2x2.png
SELECTFILES=$(addprefix /tmp/select/select2-3.4.8/, ${SELECT})

static/3party/select:
	wget https://github.com/ivaynberg/select2/archive/3.4.8.zip -O /tmp/select.zip
	rm -rf /tmp/select
	mkdir /tmp/select && true
	unzip /tmp/select.zip -d /tmp/select > /dev/null
	@mkdir static/3party/select && true
	mv ${SELECTFILES} static/3party/select

cookie: static/3party/js/js.cookie.js

static/3party/js/js.cookie.js:
	curl https://raw.githubusercontent.com/js-cookie/js-cookie/master/src/js.cookie.js > $@

shower-clean:
	rm -rf static/3party/
