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

See the [Development section] for a brief guide to working with poetry. You do not need
any of the optional dependencies in deployment so when installing you should use `poetry
install --only main`.

[Development section]: development.md#working-with-poetry
[Poetry]: https://python-poetry.org/
[poetry installation docs]: https://python-poetry.org/docs/#installation

### Database

The web app uses a database to handle user sessions and to cache broadcast messages.
SQLite is used by default and this might still be suitable for small scale deployment.
For something more capable see [Django's supported databases]. Set up the database of
your choice and make sure it is accessible from the web server. See further down for
configuring database settings for Django.

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
Django settings reference documentation.

<https://docs.djangoproject.com/en/5.1/ref/settings/>

```python
# extend the production settings by importing them
import os
from drunc_ui.settings._production import *

ALLOWED_HOSTS = ["hostname.for.access.com"]
ADMINS = [] # will receive emails in event of system errors

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

Whilst not strictly a requirement, it is strongly recommended to use HTTPS in
deployment. This can be done by placing the server behind a reverse proxy that carries
out TLS termination and forwards http traffic to the WSGI server. The settings in
`drunc_ui/settings/_production.py` support this arrangement. See the example deployment
docker compose file to see how this can be done.

### Kafka Consumer

The Kafka consumer is a long running process that injects Kafka messages into the web
app. The consumer requires the same software environment as the web app and must be run
in a location that can contact the Kafka broker and the web app database. The consumer
requires an additional environment variable - `KAFKA_ADDRESS` - that provides host and
port information for the Kafka broker.
