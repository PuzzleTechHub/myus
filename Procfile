release: python ephesus/manage.py makemigrations
release: python ephesus/manage.py migrate
release: python ephesus/manage.py collectstatic
web: gunicorn wsgi:application --chdir ephesus