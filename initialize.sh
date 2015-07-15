#!/bin/bash

echo "[run] start mongod"
mongod &
echo "[run] go to the code folder"
cd /home/docker/code/gstudio/gnowsys-ndf/

echo "[run] syncdb"
python manage.py syncdb --noinput

echo "[run] create superuser"
echo "from django.contrib.auth.models import User
if not User.objects.filter(username='admin').count():
    User.objects.create_superuser('administrator', 'admin@example.com', 'changeit')
" | python manage.py shell

# the above script is suggested by
# https://github.com/novapost/docker-django-demo

echo "[run] create or update gstudio schema in mongodb"
python manage.py filldb

