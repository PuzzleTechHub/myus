# Ephesus

This is Betaveros' Ephesus. It is a simple hassle free puzzle hunt upload website.

The project is not up and running yet, but it will be, soon

## How to host your own Ephesus

This is hosted over Django.

Just do

```bash
pip install -r requirements.txt
cp .env.template .env
```

And then edit the .env file to have the correct Django variable output for yourself

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```