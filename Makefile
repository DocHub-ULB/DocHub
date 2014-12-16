DATABASE = db.sqlite

CELERY_PIDFILE = celery.pid
WEBSERVER_PIDFILE = runserver.pid

WEBSERVER_LOGFILE = webserver.log
CELERY_LOGFILE = celery.log

PIDFILES = ${WEBSERVER_PIDFILE} ${CELERY_PIDFILE}
LOGFILES = ${WEBSERVER_LOGFILE} ${CELERY_LOGFILE} /tmp/upload_log sql.log


all: start
init: ${DATABASE} shower
reset: cleandata init

start : ${DATABASE}
	celery -A www worker -l info  > ${CELERY_LOGFILE} 2>&1 & echo "$$!" > ${CELERY_PIDFILE}
	./manage.py runserver >> ${WEBSERVER_LOGFILE} 2>&1 & echo "$$!" > ${WEBSERVER_PIDFILE}
	printf "\033[1mGo to http://localhost:8000/syslogin\033[0m\n"

stop: ${PIDFILES}
	for f in $^; do kill `ps x -o pid -o ppid | egrep $$(cat $$f) | sed -E 's/^[ ]*([0-9]+)[ ]+[0-9]+/\1/'` && rm $$f; done

clean:
	rm -f ${PIDFILES} ${LOGFILES}

cleandata: clean
	rm -f ${DATABASE}
	rm -rf ./media/documents/*
	rm -rf ./media/profile/*.*
	rm -rf /tmp/p402-upload/*
	rm -rf /tmp/processing/*
	rm -rf graph.png

${DATABASE}:
	./manage.py syncdb
	./manage.py migrate
	./manage.py init --netid=${USER} --password=test --first-name=Gaston --last-name=Lagaffe

ve:
	python2.7 `which virtualenv2` --distribute --no-site-package ve

install: requirements.txt ve shower
	pip install -r $< || printf "\033[1mYou must first source ve/bin/activate\033[0m\n"
	chmod +x ./manage.py


graph: graph.png

graph.png:
	./manage.py todot | dot -Tpng > graph.png

shower: foundation foundation-icons select

shower-clean:
	rm -rf static/3party/foundation static/3party/foundation-icons static/3party/select

foundation: static/3party/foundation

static/3party/foundation:
	wget http://foundation.zurb.com/cdn/releases/foundation-5.2.2.zip -O /tmp/foundation.zip
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
