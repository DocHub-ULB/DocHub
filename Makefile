all:run
init: db.sql
reset: clean init

run : db.sql
	# TODO: write processing_daemon pid to a file to stop it with ease
	./manage.py processing_daemon &
	./manage.py runserver

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
