#release: python myus/manage.py makemigrations
release: python myus/manage.py migrate
release: python myus/manage.py collectstatic --noinput
web: gunicorn wsgi:application --chdir myus