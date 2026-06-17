#!/bin/sh -eux

# This is the entry point of the Docker container.
# For non-containerized development, run `just dev` instead.

export DJANGO_SETTINGS_MODULE=door_tracker.settings
django-admin migrate
django-admin init_admin

daphne -b 0.0.0.0 door_tracker.asgi:application
