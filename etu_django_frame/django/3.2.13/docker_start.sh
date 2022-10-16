#!/bin/bash
cd /code

if [ $START_SERVICE == 'master' ]; then
    python manage.py makemigrations && \
    python manage.py migrate && \
    python manage.py collectstatic && \
    uwsgi --ini uwsgi_config.ini

elif [ $START_SERVICE == 'beat' ]; then
    ./celery_beat.sh

elif [ $START_SERVICE == 'worker' ]; then
    ./celery_worker.sh
else
    python manage.py makemigrations && \
    python manage.py migrate && \
    python manage.py collectstatic && \
    uwsgi --ini uwsgi_config.ini
fi

/bin/bash
