#!/bin/sh

# collect all static files to the root directory
python manage.py collectstatic --no-input

#python manage.py makemigrations
#python manage.py migrate

# start the gunicorn worker processws at the defined port
gunicorn ShireXWorkflowMonitoring.wsgi:application --bind 0.0.0.0:8000 &

wait