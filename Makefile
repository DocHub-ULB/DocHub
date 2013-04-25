DATABASE = db.sql
NOTIFY_PIDFILE = notification_daemon.pid
PROCESSING_PIDFILE = processing_daemon.pid
WEBSERVER_PIDFILE = runserver.pid
WEBSERVER_LOGFILE = webserver.log

PIDFILES = ${WEBSERVER_PIDFILE} ${PROCESSING_PIDFILE} ${NOTIFY_PIDFILE}
LOGFILES = ${WEBSERVER_LOGFILE} /tmp/upload_log sql.log

all: start
init: ${DATABASE}
reset: clean init

start : ${DATABASE}
	./manage.py processing_daemon & echo "$$!" > ${PROCESSING_PIDFILE}
	./manage.py notification_daemon & echo "$$!" > ${NOTIFY_PIDFILE}
	./manage.py runserver >> ${WEBSERVER_LOGFILE} 2>&1 & echo "$$!" > ${WEBSERVER_PIDFILE}
	printf "\033[1mGo to http://localhost:8000/syslogin\033[0m\n"

stop: ${PIDFILES}
	for f in $^; do kill `ps x -o pid -o ppid | egrep $$(cat $$f) | sed -E 's/^[ ]*([0-9]+)[ ]+[0-9]+/\1/'` && rm $$f; done

clean:
	rm -f ${PIDFILES} ${LOGFILES}

cleandata: clean
	rm -f ${DATABASE}
	rm -rf ./static/documents/*

${DATABASE}:
	./manage.py syncdb
	./manage.py migrate
	./manage.py init --username=${USER} --password=test --first-name=Gaston --last-name=Lagaffe

ve:
	python2.7 `which virtualenv` --distribute --no-site-package ve

install: requirements.txt ve
	pip install -r $< || printf "\033[1mYou must first source ve/bin/activate\033[0m\n"
	chmod +x ./manage.py
