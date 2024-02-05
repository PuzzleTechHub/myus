# Ephesus

This is Ephesus-2, an open source to-be-running version of [Betaveros' Ephesus](https://github.com/betaveros/ephesus-public). 

It is a simple hassle free puzzle hunt upload and hosting website.

This project is currently set up to run via Heroku. A permanent site is currently in the works, once the hosting is sorted.

## How to host your own Ephesus

This is hosted over Django.

Install [SQLite3](https://www.tutorialspoint.com/sqlite/sqlite_installation.htm) - 
```bash
sudo apt install sqlite3
```

Now try testing sqlite3
```bash
python manage.py dbshell
> .tables
> select * from ephesus_hunt;
```

Just do - 
```bash
pip install -r requirements.txt
cp .env.template .env
```

And then edit the .env file to have the correct Django variable output for yourself

```bash
cd ephesus
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
python manage.py runserver
```

# Contributor Code of Conduct

Be nice to each other. Also, everything in [Contributor Covenant version 1.4](https://www.contributor-covenant.org/version/1/4/code-of-conduct/)
