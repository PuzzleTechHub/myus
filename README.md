# myus

This is myus, an open source website for hassle-free puzzle hunt upload and hosting. 

Find us on **http://www.puzzlehuntmy.us/**

This project is currently set up to run via Heroku.

## How to host your own myus instance

This is hosted over Django.

Install [SQLite3](https://www.tutorialspoint.com/sqlite/sqlite_installation.htm) - 
```bash
sudo apt install sqlite3
```

Now try testing sqlite3
```bash
python manage.py dbshell
> .tables
> select * from myus_hunt;
```

Just do - 
```bash
pip install -r requirements.txt
cp .env.template .env
```

And then edit the .env file to have the correct Django variable output for yourself

```bash
cd myus
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
python manage.py runserver
```

# Why Myus?

Because the original version was called Ephesus so we had to pick a different [Ionian League city](https://en.wikipedia.org/wiki/Ionian_League) for ourselves.

# Credits

This codebase is built off [Betaveros' Ephesus](https://github.com/betaveros/ephesus-public). 

# Contributor Code of Conduct

Be nice to each other. Also, everything in [Contributor Covenant version 1.4](https://www.contributor-covenant.org/version/1/4/code-of-conduct/)
