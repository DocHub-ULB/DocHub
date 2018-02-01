from __future__ import with_statement
from fabric.api import run, cd
from fabric.context_managers import prefix

BASE_DIR = "/srv/dochub/source"
ACTIVATE = 'source ../ve/bin/activate'


def deploy():
    with cd(BASE_DIR), prefix(ACTIVATE):
        run('sudo systemctl stop dochub-gunicorn.socket')
        run('sudo systemctl stop dochub-gunicorn.service')
        run("../backup_db.sh")
        run("git pull")
        run("pip install -r requirements.txt -q")
        run("npm run build")
        run("./manage.py collectstatic --noinput -v 0")
        run("./manage.py migrate")
        run('sudo systemctl start dochub-gunicorn.service')
        run('sudo systemctl start dochub-gunicorn.socket')


def light_deploy():
    with cd(BASE_DIR), prefix(ACTIVATE):
        run('sudo systemctl stop dochub-gunicorn.socket')
        run('sudo systemctl stop dochub-gunicorn.service')
        run("git pull")
        run('sudo systemctl start dochub-gunicorn.service')
        run('sudo systemctl start dochub-gunicorn.socket')


def restart_workers():
    run('sudo systemctl stop dochub-celery')
    run('sudo systemctl start dochub-celery')


def stats():
    with cd(BASE_DIR), prefix(ACTIVATE):
        run('./manage.py stats')
