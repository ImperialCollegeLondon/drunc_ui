# Development

<!-- markdownlint-disable next-line code-block-style -->
!!! note

    Make sure you've been through the instructions to run the project locally, can
    successfully run the web application under the Docker setup, have carried out the
    setup steps and can access the UI's you want to work with in the browser.

Working with the full functionality of the web application requires a number of services
to be started and to work in concert. The Docker Compose stack provides the required
services and is suitable for development and manual testing but is not suitable for
running QA (pre-commit) tooling or unit tests. The project directory is mounted into the
`app` service which allows the Django development server's auto-reload mechanism to
detect changes to local files and work as expected.

In addition to the Docker setup, you will also need to follow the below instructions on
working with poetry to run the project's QA tooling and unit tests.

## Working with Poetry

This is a Python application that uses [poetry](https://python-poetry.org) for packaging
and dependency management. It also provides [pre-commit](https://pre-commit.com/) hooks
for various linters and formatters and automated tests using
[pytest](https://pytest.org/) and [GitHub Actions](https://github.com/features/actions).
Pre-commit hooks are automatically kept updated with a dedicated GitHub Action.

To get started:

1. [Download and install Poetry](https://python-poetry.org/docs/#installation) following
   the instructions for your OS.

1. Clone this repository and make it your working directory

1. Set up the virtual environment:

    ```bash
    poetry install
    ```

1. Activate the virtual environment (alternatively, ensure any Python-related command is
   preceded by `poetry run`):

    ```bash
    poetry shell
    ```

1. Install the git hooks:

    ```bash
    pre-commit install
    ```

Pre-commit should now work as expected when making commits even without the need to have
an active poetry shell. You can also manually run pre-commit (e.g. `pre-commit run -a`)
and the unit tests with `pytest`. Remember you'll need to prefix these with `poetry run`
first if you don't have an active poetry shell.

## Docker Development Stack

The Docker Compose stack is defined in `docker-compose.yml` and provides the services
required to enable development of the web application. The services are described in detail below.

### kafka

Kafka is a "distributed event streaming platform" used as a channel to pass messages
between different components of the DUNE control system. It is primarily used to send
informational messages for consumption by system operators. A key role of the UIs we are
developing is to present these messages to system operators to help them identify and
troubleshoot issues.

<!-- markdownlint-disable next-line code-block-style -->
!!! note

    Messages sent via Kafka are referred to as "broadcast messages" in the drunc
    codebase and documentation.

Kafka is known for being complex to set up and manage. The Docker Compose stack provides
a Kafka image packaged by Bitnami which seems to have worked reliably so far.
Configuration for the Kafka service is carried out using environment variables in
`docker-compose.yml`. The configuration values used are not well understood so it is not
recommended to change them unless systemic issues are encountered.

Longer term the DUNE project may move away from Kafka to a more lightweight solution.
The web application should aim to be as agnostic as possible to the underlying messaging
system.

### drunc

This service is only used as part of the `drunc` Docker Compose profile. See the [Docker
Setup overview] for details.

Runs the various components of the DUNE control system that the web app interfaces with.
Drunc has a complex set of dependencies collectively referred to the as the DUNE DAQ
environment (see the [DUNE DAQ documentation] for more information). The upshot is that
it is not feasible for us to build our own Drunc image from scratch for development.
Instead we use a base image published by the Dune project that provides the required
dependencies.

The base images are published by the [daq-release repository]. There are separate images
for nightly ([nightly-release-alma9]) and release ([frozen-release-alma9]) builds. We
are currently tracking nightly builds as we are dependent on cutting edge drunc
developments. It may be feasible in the future to swap to a pinned release build.

To ensure a consistent developer experience we pin the development image to a fixed base
image. The base image is manually tagged and pushed to the
[imperialcollegelondon/dunedaq_dev_environment] package with a tag including the date of
the nightly.

The primary function of the drunc image is to run the Drunc Process Manager which is
then responsible for booting the processes of a Drunc session. The Process Manager
launches processes on localhost via SSH. To support this the `drunc` service also starts
an SSH server with keys configured to allow passwordless connection to localhost.

#### Updating the drunc base image

The following changes are needed to update the version of the base image used for the
`drunc` service.

1. Pull the latest nightly image - `docker pull
   ghcr.io/dune-daq/nightly-release-alma9:development_v5`.
1. Retag the image for the imperialcollegelondon/dunedaq_dev_environment package using
   the date of the new nightly, e.g.
   `docker tag ghcr.io/dune-daq/nightly-release-alma9:development_v5
   ghcr.io/imperialcollegelondon/dunedaq_dev_environment:nightly-241114`.
1. Update `drunc_docker_service/Dockerfile` to the reflect the date of the new nightly.
   You'll need to change the `NIGHTLY_TAG` environment variable and the name of the base
   image.
1. Update the pinned commits of `drunc` and `druncschema` in `pyproject.toml` to match
   the versions in the image. This is usually the latest commit in the `develop` branch
   of those repositories but you should check that no new commits have been added since
   the nightly was built.
1. Regenerate the Poetry lock file.
1. Run `docker compose up --build` to start the development stack.
1. Test the new image. Make sure that you can boot a test session, complete the full set
   of FSM transitions and whatever new functionality the nightly is being for is working
   as expected.
1. If everything looks good then push the retagged base image and create a PR from your
   changes.

[daq-release repository]: https://github.com/ImperialCollegeLondon/drunc_ui
[DUNE DAQ documentation]: https://dune-daq-sw.readthedocs.io/en/latest/
[nightly-release-alma9]: https://github.com/DUNE-DAQ/daq-release/pkgs/container/nightly-release-alma9
[frozen-release-alma9]: https://github.com/DUNE-DAQ/daq-release/pkgs/container/frozen-release-alma9
[imperialcollegelondon/dunedaq_dev_environment]: https://github.com/ImperialCollegeLondon/drunc_ui/pkgs/container/dunedaq_dev_environment

### drunc-lite

This service is only used as part of the `drunc-lite` Docker Compose profile. See the
[Docker Setup overview] for details.

This image contains a parred down version of the drunc python package containing only
the pip installable dependencies. As it avoids the full complex dependency stack of
Drunc it can be based on a standard (and much smaller) Python image. The main limitation
of this image is that it cannot boot Drunc sessions and hence is only useful for working
with dummy processes in the Process Manager UI.

Similarly to the full `drunc` service, it starts the Drunc Process Manager and provides
an SSH server to allow the booting of dummy processes.

[Docker Setup overview]: index.md#docker-setup

### app

Runs the `drunc_ui` codebase. This is a fairly simple image that installs this project's
dependencies and starts the Django development server. The development database is
stored in the `db` volume to persist beyond an individual container lifespan. The
project directory from the host is mounted into the `app` service which allows the
Django development server's auto-reload mechanism to detect changes and support rapid
iterative development.

### kafka_consumer

Receiving messages from Kafka requires a long-running process to act as a consumer. The
`kafka_consumer` service fulfills this role. The consumer is implemented as a [Django
admin command] and can be run as `python manage.py kafka_consumer`. For this reason the
`kafka_consumer` service uses the same image as the `app` service.

Messages are passed to the web app by storing them directly into the web app database.
To enable this, the volume containing the web application database is also mounted into
the `kafka_consumer` container. This command is also responsible for pruning messages
from the database after a configurable retention period.

As may be expected the `kafka_consumer` service is dependent on the `kafka` service and
will need to be replaced if Kafka is replaced.
