#!/bin/bash
set -e

cd /home/ec2-user/django-basic
source venv/bin/activate

git pull origin main
pip install -r requirements.txt || true
python manage.py migrate

sudo systemctl restart django
