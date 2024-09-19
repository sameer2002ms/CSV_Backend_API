#!/bin/sh
echo "migration"
python manage.py makemigrations
echo "=============================="


echo "migrate"
python manage.py migrate
echo "=============================="

echo "start server"
python manage.py runserver localhost:8000


