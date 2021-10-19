/usr/local/bin/celery -A $CELERY_APP worker --pidfile=$CELERYD_PID_FILE --logfile=$CELERYD_LOG_FILE --loglevel=$CELERYD_LOG_LEVEL $CELERYD_OPTS
