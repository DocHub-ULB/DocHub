#!/bin/bash
/usr/local/bin/celery multi start ${CELERYD_NODES} -A ${CELERY_APP} --pidfile=${CELERYD_PID_FILE} --logfile=${CELERYD_LOG_FILE} --loglevel=${CELERYD_LOG_LEVEL} ${CELERYD_OPTS}
gunicorn www.wsgi:application --bind 0.0.0.0:8000 --timeout 300
