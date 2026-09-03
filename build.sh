#!/usr/bin/env bash
set -o errexit

python -m pip install -r requirements.txt
python manage.py collectstatic --no-input --ignore "novedades/css/input.css"
python manage.py migrate
python manage.py crear_roles
