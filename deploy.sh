#!/bin/bash

echo "Starting deployment..."

cd /home/ec2-user/django_app/django-basic || exit 1

echo "Pulling latest code..."
git pull origin main

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Restarting gunicorn..."
sudo systemctl restart gunicorn

echo "Deployment completed successfully!"

