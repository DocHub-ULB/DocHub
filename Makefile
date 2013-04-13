DATABASE = db.sql
PROCESSING_PIDFILE = processing_daemon.pid
WEBSERVER_PIDFILE = runserver.pid
WEBSERVER_LOGFILE = webserver.log

PIDFILES = ${WEBSERVER_PIDFILE} ${PROCESSING_PIDFILE}
LOGFILES = ${WEBSERVER_LOGFILE} /tmp/upload_log

all:run
init: ${DATABASE}
reset: clean init

run : ${DATABASE}
	./manage.py processing_daemon & echo "$$!" > ${PROCESSING_PIDFILE}
	./manage.py runserver >> ${WEBSERVER_LOGFILE} 2>&1 & echo "$$!" > ${WEBSERVER_PIDFILE}

stop: ${PIDFILES}
	for f in $^; do kill `ps x -o pid -o ppid | egrep $$(cat $$f) | tr -s ' ' | cut -d' ' -f 1`; done

clean:
	rm -f ${DATABASE} ${PIDFILES} ${LOGFILES}
	rm -rf ./static/documents/*

${DATABASE}:
	./manage.py syncdb
	./manage.py migrate
	./manage.py init_from_parsed --username=${USER} --password=test --first-name=Gaston --last-name=Lagaffe

ve:
	python2.7 `which virtualenv` --distribute --no-site-package ve

install: requirements.txt ve
	pip install -r $< || printf "\033[1mYou must first source ve/bin/activate\033[0m\n"
	chmod +x ./manage.py
