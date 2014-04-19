DATABASE = db.sqlite

CELERY_PIDFILE = celery.pid
WEBSERVER_PIDFILE = runserver.pid

WEBSERVER_LOGFILE = webserver.log
CELERY_LOGFILE = celery.log

PIDFILES = ${WEBSERVER_PIDFILE} ${CELERY_PIDFILE}
LOGFILES = ${WEBSERVER_LOGFILE} ${CELERY_LOGFILE} /tmp/upload_log sql.log

all: start
init: ${DATABASE}
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
	python2.7 `which virtualenv` --distribute --no-site-package ve

install: requirements.txt ve
	pip install -r $< || printf "\033[1mYou must first source ve/bin/activate\033[0m\n"
	chmod +x ./manage.py

graph: graph.png

graph.png:
	./manage.py todot | dot -Tpng > graph.png
