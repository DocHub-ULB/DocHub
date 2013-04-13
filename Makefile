all:run
init: db.sql
reset: clean init

run : db.sql
	./manage.py processing_daemon & echo $$! > daemon.pid
	./manage.py runserver

stop:
	kill `cat daemon.pid`
	rm daemon.pid

clean:
	rm -f db.sql
	rm -f /tmp/upload_log
	rm -rf ./static/documents/*

db.sql:
	./manage.py syncdb
	./manage.py migrate
	./manage.py init_from_parsed

ve:
	python2.7 `which virtualenv` --distribute --no-site-package ve

install: requirements.txt ve
	pip install -r $< || echo "You must first source ve/bin/activate"
	chmod +x ./manage.py
