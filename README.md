# myus

This is myus, an open source website for hassle-free puzzle hunt upload and hosting. The code is written with Python and Django, and currently set up to run via Heroku.

Find us on **http://www.puzzlehuntmy.us/**

## How to host your own myus instance

### Prerequisites - 

- [python3.10 or newer](https://realpython.com/installing-python/)

- [Git](https://github.com/git-guides/install-git)

- [Postgresql for storing data](https://www.postgresql.org/download/)

- [Heroku CLI client for hosting](https://medium.com/analytics-vidhya/how-to-install-heroku-cli-in-windows-pc-e3cf9750b4ae)

- [Pip package installer for Python](https://phoenixnap.com/kb/install-pip-windows)

Note that you may use another Python installer (instead of Pip), Host (instead of Heroku) or Database (instead of Postgresql) but that will require you figuring out the required setup and configuation changes yourself.

While only the above are necessary to run the code on Heroku, some OSes might require additional installations to also run locally. For example, on Ubuntu, you need - 
```bash
sudo apt-get install postgresql-client-common postgresql-client
```

All commands in this README will work for Ubuntu (or similar Linux distros), but translating any differences to Windows/another OS is hopefully minor enough. If any part of this README is not clear enough, please ping us on discord or Github.

### Installation

We recommend using [virtual environments](https://docs.python.org/3/tutorial/venv.html) to manage python packages for our repo. This is not necessary for the rest of code, but is generally good practice.

To clone the repo and install dependencies, run the following on the Command Line - 
```bash
#Clone the code locally
git clone https://github.com/PuzzleTechHub/myus.git
cd myus
#Technically optional, but using virtualenv is usually a good idea
virtualenv venv -p=3.10 
#This installs all the python dependancies the code needs
pip install -r requirements.txt
```

#### Handling Postgres

The code uses [Heroku Postgres](https://www.heroku.com/postgres) for storing data. Once you [set up a local Postgres instance](https://www.prisma.io/dataguide/postgresql/setting-up-a-local-postgresql-database), you can test it. [Heroku's Postgres docs](https://devcenter.heroku.com/articles/heroku-postgresql#local-setup) may also be useful.

You might need to create a Postgres user. You'll also want to create a Postgres database. To do those things, install Postgres, then run `psql`. Postgres expects you to login as a user that already has an account and has 'create database' permissions, most likely `postgres`. 

On Ubuntu this is:
```
sudo -u postgres psql
```

Enter whichever of these two SQL commands you need into the `psql` prompt to create a new user with a password and a database. Fill in the values you want.
```
CREATE USER yourusername PASSWORD 'test';
CREATE DATABASE mydb;
```

This is only usable for local development and the password will be lying around in plaintext. After typing that and hitting Enter, if it worked, you can test around a few [postgres commands](https://kinsta.com/blog/postgres-list-databases/) to confirm. Then just quit `psql` (Use Ctrl-D or `quit` or `\quit`).

### Local Run

#### Local Runs - One-time setup

To run the code locally, you will need a `.env` file which is used by [python-dotenv](https://github.com/theskumar/python-dotenv) to load `ENV` variables. Copy `.env.template` into `.env`.  
```bash
cp .env.template .env
```
Then, fill in the empty variable in your `.env` file. If any part is unclear, the `.env.template` file usually has links to help explain. 

Finally, just run
```bash
heroku local release
```
It's basically identical to calling the commands in [Procfile](./Procfile) that start with "release". 

Note - The above may not be sufficient to get the initial databases made. If so, also run - 
```bash
#Initial DB generation
python myus/manage.py migrate --fake sessions zero
#Test generation worked properly
python myus/manage.py showmigrations
#Finish initial DB generation (#TODO : How?)
python myus/manage.py migrate --fake-initial

#Test DB was generated properly (#TODO : How?)
python myus/manage.py dbshell
```

#### Local Runs - Every time

You'll always need to [make sure the PostgreSQL server is running](https://mydbanotebook.org/post/troubleshooting-01/) before trying to run the rest of code. 

After everything else is ready, to run the website, just run 
```bash
heroku local web
```
and the code will run locally. We use gunicorn to serve the final website via the web command in [Procfile](./Procfile).

For comparision, commands without using `heroku local` or gunicorn would be - 
```bash
#DB commands
python myus/manage.py makemigrations
python myus/manage.py migrate
#Static commands
python myus/manage.py collectstatic
#Actual run
python myus/manage.py runserver
```

The first time you're running the website locally or any time you change the static assets, run `python myus/manage.py collectstatic --noinput`. This step is skipped for Heroku because it already auto-runs collectstatic for you.

To set up other things (creating superusers, migrating or making migrations, loading data), you can mostly follow instructions or run the same commands as you do on similar Django setups, except that when asked to run `python myus/manage.py something` you should instead run `heroku local:run myus/manage.py something`. Using `python myus/manage.py help` should give you a helpful list of such commands.

### Heroku

Our instance of the code is [hosted on Heroku](https://realpython.com/django-hosting-on-heroku/). 

When you're running locally/working on dev, you can also use manage.py directly. But for prod, serving via [gunicorn](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-22-04) is recommended.

You will need to first set up the Postgresql database for the code. To do it via Heroku's PostgresSQL add-on, first [install the add-on](https://elements.heroku.com/addons/heroku-postgresql) then [set it up](https://devcenter.heroku.com/articles/heroku-postgresql) to attach your app to the Postgres. Now you can look at `Heroku - Dashboard - Resources - Add Ons` to look at the app on Heroku, and copy the URI given from Postgres add-on for your `DATABASE_URL`.

If you don't want a paid service, you may want to use free Postgres alternatives, like Supabase ([Postgres Supabase installation guide](https://dev.to/prisma/set-up-a-free-postgresql-database-on-supabase-to-use-with-prisma-3pk6)). You'll need to figure out some of the installation yourself but for the codebase, you probably just need to edit `.env` and nothing else

Next, [create your Heroku app](https://dev.to/ivadyhabimana/3-creating-your-first-heroku-app-3d1d) via command line or the website. For Heroku, you'll also need to translate all `.env` variables into [config values added](https://devcenter.heroku.com/articles/config-vars) to your database. You can add them using commands like `heroku config:set SECRET_KEY="YOUR_SECRET_KEY_HERE"`.
Make sure to set **SECRET_KEY** to a securely generated long random string. Your app may still run if you don't do this step, but it will be insecure!

Change Heroku settings to enable running your Heroku app, if necessary, then [deploy it](https://coding-boot-camp.github.io/full-stack/heroku/heroku-deployment-guide). If you've enabled all the settings and connected the app to the correct git directory, it should be as simple as running `git push heroku main`. In theory, if you now visit `yourappname.herokuapp.com` you should see the properly styled front page of the website. 

Two extremely useful commands for debugging via Heroku are - 
```bash
#For releases and stuff - 
heroku releases:output

#All logs
heroku logs --tail
```

#### Insert heading

A short list of Heroku specific changes we did in this codebase. It's not essential that you understand this, but they will probably be helpful for debugging:

- We need a `Procfile` to tell Heroku how to run our app.
- [Other DBs like SQLite aren't a good fit for Heroku](https://devcenter.heroku.com/articles/sqlite3) because Heroku doesn't provide a "real" filesystem. Fortunately Heroku provides easy-to-use PostgreSQL, so we switched Django to use that instead. 
- We install the `whitenoise` middleware so Django can serve static files directly in a production-ready way.

## Why Myus?

The original version was called Ephesus. So we had to pick a different [Ionian League city](https://en.wikipedia.org/wiki/Ionian_League) for ourselves.

## Credits

This codebase is built off [Betaveros' Ephesus](https://github.com/betaveros/ephesus-public). 

Further development has continued in Puzzle Tech Hub. See [Puzzle Tech Hub github](https://github.com/PuzzleTechHub) for a list of other projects, and see link below for the discord. 
[![](https://discordapp.com/api/guilds/1204637356863262801/widget.png?style=banner3)](https://discord.gg/kgTK5eD7XY)


## Contributor Code of Conduct

Be nice to each other. Also, everything in [Contributor Covenant version 1.4](https://www.contributor-covenant.org/version/1/4/code-of-conduct/)

