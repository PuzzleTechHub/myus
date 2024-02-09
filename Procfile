#Sets up the database
release: python myus/manage.py migrate
#Sets up static files
release: python myus/manage.py collectstatic --noinput
#Starts up website
web: gunicorn wsgi:application --chdir myus