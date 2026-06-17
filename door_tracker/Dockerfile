FROM python:3.14-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

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

# Change the working directory to the `app` directory
WORKDIR /app

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

# Copy the project into the image
COPY . /app

# Install the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable

FROM python:3.14-slim

# setup a non-root user to run the app in
RUN <<EOF
    groupadd --system --gid 999 app
    useradd --system --uid 999 --gid 999 --create-home app
EOF
USER app

# copy the built virtualenv and activate it
COPY --from=builder --chown=app:app /app/.venv /app/.venv
ENV VIRTUAL_ENV="/app/.venv"
ENV PATH="/app/.venv/bin:$PATH"

# by default, launch the production server
COPY run.sh /app
CMD ["/app/run.sh"]
EXPOSE 8000
