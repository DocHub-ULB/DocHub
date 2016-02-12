from __future__ import with_statement
from fabric.api import run, cd
from fabric.context_managers import prefix


def deploy():
    code_dir = '/home/b402/beta402'
    with cd(code_dir), prefix('source ve/bin/activate'):
        run('sudo supervisorctl stop b402-gunicorn')
        run("./save_db.sh")
        run("git pull")
        run("pip install -r requirements.txt --upgrade -q")
        run("./manage.py collectstatic --noinput -v 0")
        run("./manage.py migrate")
        run('sudo supervisorctl start b402-gunicorn')


def light_deploy():
    code_dir = '/home/b402/beta402'
    with cd(code_dir), prefix('source ve/bin/activate'):
        run('sudo supervisorctl stop b402-gunicorn')
        run("git pull")
        run('sudo supervisorctl start b402-gunicorn')


def restart_workers():
    run('sudo supervisorctl stop  b402-worker1')
    run('sudo supervisorctl stop  b402-worker2')
    run('sudo supervisorctl stop  b402-worker3')

    run('sudo supervisorctl start b402-worker3')
    run('sudo supervisorctl start b402-worker2')
    run('sudo supervisorctl start b402-worker1')


def stats():
    code_dir = '/home/b402/beta402'
    with cd(code_dir), prefix('source ve/bin/activate'):
        run('./manage.py stats')
