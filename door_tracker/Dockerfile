FROM python:3.14-slim AS base

# disables buffering of print() statements i.e. each print() immediately
# writes to screen, instead of waiting until there's enough text waiting
# to be written.
ENV PYTHONUNBUFFERED=1

# uv downloads packages in a global cache and hardlinks then into the
# virtualenv to share them among different venvs. Since our cache is
# bind-mounted, hardlinking is not possible, so we switch to (slower)
# copying.
ENV UV_LINK_MODE=copy

# Forbid uv from downloading Python in case the system one
# doesn't match the app. Instead, uv will fail, which is
# exactly what we want (so that we immediately detect
# if Dockerfile and uv disagree on Python version).
ENV UV_PYTHON_DOWNLOADS=never

# set up the environment the way Django wants it
ENV DJANGO_SETTINGS_MODULE=door_tracker.settings
ENV DJANGO_STATIC_ROOT=/static

# Change the working directory to the `app` directory
WORKDIR /app


FROM base AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install native extensions compilation packages
RUN apt-get update && apt-get install -y build-essential && apt-get clean

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

# Copy the project into the image
COPY . /app

# install the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable

# cache the static files in $DJANGO_STATIC_ROOT
RUN uv run --no-sync \
    django-admin collectstatic --no-input


FROM base

# setup a non-root user to run the app in
RUN <<EOF
    groupadd --system --gid 999 app
    useradd --system --uid 999 --gid 999 --create-home app
EOF

# ensure the docker volumes have proper permissions
RUN mkdir /credentials /db && chown app:app /credentials /db

# switch to the non-root user
USER app

# copy the source & static files
COPY --chown=app:app . /app
COPY --from=builder --chown=app:app /static /static

# copy the built virtualenv and activate it
COPY --from=builder --chown=app:app /app/.venv /app/.venv
ENV VIRTUAL_ENV="/app/.venv"
ENV PATH="/app/.venv/bin:$PATH"

# by default, launch the production server
CMD ["/app/run.sh"]
EXPOSE 8000
