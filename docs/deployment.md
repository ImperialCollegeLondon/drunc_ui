# Deployment

The actual steps required for deployment will vary depending on the environment in
question. Here we consider things you will need to consider and briefly discuss some
approaches.

## Considerations

### Software Environment

The software dependencies of the app must be installed. Dependency management is handled
via [Poetry]. See the [poetry installation docs] for how to get hold of it. You can
allow poetry to create and manage a virtual environment for you or enable manual control
of where packages are installed with `poetry config virtualenvs.create false`.

See the [Development section] for a brief guide to working with poetry. You can install
the project dependencies via `poetry install --only main`. Depending on your choice of
database (see below) some of the optional dependencies may be needed e.g. `poetry
install --only main --only postgres`.

[Development section]: development.md#working-with-poetry
[Poetry]: https://python-poetry.org/
[poetry installation docs]: https://python-poetry.org/docs/#installation

### Database

The web app uses a database to handle user sessions and to cache broadcast messages.
SQLite is used by default and this might still be suitable for small scale deployment.
For something more capable see [Django's supported databases]. Set up the database of
your choice and make sure it is accessible from the web server. See further down for
configuring database settings for Django.

<!-- markdownlint-disable next-line code-block-style -->
!!! note

    Additional Python packages are required for non-sqlite databases. See the Django
    Database docs for more information. Dependencies for Postgres and MySQL are
    available as extras in the `pyproject.toml` file. See the Software Environment
    section above.

[Django's supported databases]: https://docs.djangoproject.com/en/5.1/ref/databases/

### Deployment Settings File

By default, when started the web app will use settings suitable for development. A
partial configuration for production is provided by `drunc_ui/settings/_production.py`
but this must be extended with deployment specific settings. The recommended pattern to
do this is to create a deployment settings file. This can be placed in any location
importable by Python. Then set the environment variable `DJANGO_SETTINGS_MODULE` to the
import path of the file. For instance, if you created `drunc_ui/settings/deployment.py`
then you would set `DJANGO_SETTINGS_MODULE=drunc_ui.settings.deployment`. An example
settings file containing the minimum required configuration is given below. Also see the
Django [settings reference documentation].

[settings reference documentation]: https://docs.djangoproject.com/en/5.1/ref/settings/

```python
# extend the production settings by importing them
import os
from drunc_ui.settings._production import *

ALLOWED_HOSTS = ["hostname.for.access.com"]
# Admins will receive emails in event of system errors
ADMINS = [("Chris Cave-Ayland", "c.cave-ayland@imperial.ac.uk")]

# email settings
# the SMTP backend is configured in _production.py, you can specify something else but
# the below example settings assume you don't
# review the other possible settings https://docs.djangoproject.com/en/5.1/ref/settings/#email-backend
EMAIL_HOST = "smtp.host.domainname"
SERVER_EMAIL = "noreply@host.com"
DEFAULT_FROM_EMAIL = "noreply@host.com"

# database settings - will depend on your choice in deployment
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "mydatabase",
        "USER": "mydatabaseuser",
        "PASSWORD": os.environ["DATABASE_PASSWORD"],
        "HOST": "127.0.0.1",
        "PORT": "5432",
    }
}

# a basic example logging configuration with environment variable support
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
    },
}
```

### Environment Variables

The web app supports (and, in the case of sensitive values, requires) some settings via
environment variable. These are listed below:

- DJANGO_SETTINGS_MODULE - as discussed above
- SECRET_KEY - sensitive value used for cryptographic purposes
- PROCESS_MANAGER_URL - host and port information for the process manager
- CSC_URL - host and port information for the connectivity server
- CSC_SESSION - name of the active drunc session

There may be additional environment variables to set depending on your deployment
settings file.

### WSGI Server

Django apps should be deployed using a production capable WSGI server. The [Django docs
on WSGI] cover a number of options but gunicorn is recommended as it is already a
dependency of `drunc`. If you use anything else will have to install it into the
software environment e.g. `poetry run python pip install uwsgi`. Make sure to use the
selected WSGI server when launching the web app and to configure an appropriate number
of threads and processes for handling incoming requests.

[Django docs on WSGI]: https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/

### HTTPS

It is strongly recommended to use HTTPS in deployment. This can be done by placing the
WSGI server behind a reverse proxy that carries out TLS termination and forwards http
traffic. The settings in `drunc_ui/settings/_production.py` support this arrangement.
There are many capable servers capable of acting as reverse proxies (e.g. [Apache] or
[Nginx]).

[Apache]: https://httpd.apache.org/
[Nginx]: https://nginx.org/

### Kafka Consumer

The Kafka consumer is a long running process that injects Kafka messages into the web
app. The consumer requires the same software environment as the web app and must be run
in a location that can contact the Kafka broker and the web app database. The consumer
requires an additional environment variable - `KAFKA_ADDRESS` - that provides host and
port information for the Kafka broker.

### Database Migrations

See [Django's documentation on database migrations] for background. The Django
management command `python manage.py migrate` must be run once initially to create the
required database tables for the app to function. The command then needs to be run again
whenever the database schema changes.

[Django's documentation on database migrations]: https://docs.djangoproject.com/en/5.1/topics/migrations/

### Static Files

See [Django's documentanion on static files] for background. The [WhiteNoise] package is
used to serve static files in production. This allows static content to be served by the
WSGI server rather than requiring a separate web server. This simplifies deployment and
is compatible with the lightweight nature of the app frontend.

One step that is required is to run the Django [collectstatic management command]. This
prepares the projects static files to be served. The command should be run after any
changes to the apps static files (after any update to be safe) and the WSGI server
restarted. If there are multiple replicas of the WSGI server then the command should be
run on each (unless static files are stored in a shared location).

[Django's documentanion on static files]: https://docs.djangoproject.com/en/5.1/ref/contrib/staticfiles/#collectstatic
[collectstatic management command]: https://docs.djangoproject.com/en/5.1/ref/contrib/staticfiles/#collectstatic
[WhiteNoise]: https://whitenoise.readthedocs.io/en/stable/django.html

### Creating Users

At time of writing the app uses the built-in Django authentication system. This requires
user accounts to be created before the user can login. The Django admin interface can be
used to create users. The command `python manage.py createsuperuser` can be used to
create a superuser account. This account can then be used to create other users via the
admin interface.

## Deploying with Docker Compose

!!! note

    The example deployment docker compose file is not actively tested and may not work
    without modificaction. Nonetheless it provides a reasonable starting point for a
    single server deployment.

A simple and robust way to deploy the app on a single server is to use Docker Compose.
This provides a way to define the services required by the app and flexibly manage
configuration.

An example Docker Compose file is provided in the `example_deployment` directory. You
should be able to start the app with `docker compose -f
example_deployment/docker-compose.yml up` and access the web app at `https://localhost`.

!!! note

    Although a kafka consumer service is defined in the example deployment file it will
    not start successfully without `KAFKA_ADDRESS` being set to an operational Kafka
    broker instance.

The example deployment address the following previously mentioned considerations:

- The software environment is provided is built from the `Dockerfile` in the root of the
  repository.

- The deloyment settings file is given by `example_deployment/deployment.py`. This is
  mounted into the relevant containers at
  `/usr/src/app/drunc_ui/settings/deployment.py`. The `DJANGO_SETTINGS_MODULE`
  environment variable is then set to `drunc_ui.settings.deployment`.

- The database is provided by a PostgreSQL container. The database name, user and
  hostname are set in the deployment settings file. The database password is read from
  the environment variable `DATABASE_PASSWORD` to facilitate secret management.

- Environment variables are set in the `environment` section of each service in the
  Docker Compose file.

- Gunicorn is used as the WSGI server. The number of workers and threads is set in the
  `command` section of the `app` service.

- The web app is served over HTTPS by a reverse proxy. The `proxy` service uses [Caddy]
  to forward traffic to the `app` service. Caddy is configured by
  `example_deployment/Caddyfile` with is mounted into the container at
  `/etc/caddy/Caddyfile`. Self signed certificates are used for HTTPS and mounted into
  the `proxy` service.

- Database migration and static file collection are handled by the `app` service. The
  `command` section of the `app` service runs the necessary management commands whenever
  the service is started.
