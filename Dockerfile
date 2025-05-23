FROM python:3.10-slim-bookworm AS python

FROM python AS build

RUN pip install --root-user-action ignore pipx==1.6
RUN pipx install poetry==1.8
COPY pyproject.toml poetry.lock /
RUN /root/.local/bin/poetry config virtualenvs.create false && \
    /root/.local/bin/poetry install --no-root --no-directory --only main --only postgres

FROM python

COPY --from=build /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

RUN groupadd --gid 1221 dune_group && \
    useradd --uid 1221 --gid 1221 --create-home dune_user

USER dune_user
RUN mkdir /home/dune_user/db
WORKDIR /home/dune_user/app
EXPOSE 8000
