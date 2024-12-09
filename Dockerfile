FROM python:3.11-slim-bookworm AS python

FROM python AS build

RUN pip install --root-user-action ignore pipx==1.6
RUN pipx install poetry==1.8
COPY pyproject.toml poetry.lock /
RUN /root/.local/bin/poetry config virtualenvs.create false && \
    /root/.local/bin/poetry install --no-root --no-directory --only main --only postgres

FROM python

COPY --from=build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=build /usr/local/bin /usr/local/bin
EXPOSE 8000
COPY --chown=nobody:nogroup . /usr/src/app
WORKDIR /usr/src/app
USER nobody
