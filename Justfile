# List available commands
[default]
_list:
    @just --list

# Run manage.py
django *ARGS:
    cd door_tracker && uv run ./manage.py {{ARGS}}

# Format all source files
fmt:
    treefmt

# Run all formatters & tests
check: fmt test build-image

# Run the dev server
dev: migrate (django 'runserver')

# Run the python shell with django imported
repl: (django 'shell')

# Create a new database
init-db: migrate (django 'createsuperuser')

# Create database migrations
make-migrations: (django 'makemigrations')

# Run database migrations
migrate: (django 'migrate')

# Run tests
test: (django 'test')

# Release a new version on Github
release:
    #!/bin/sh -eux
    uv version "$(git cliff --bumped-version)"
    message="chore(version): $(git cliff --bumped-version)"
    git cliff --bump -o CHANGELOG.md --with-commit "$message"
    git commit . -m "$message"

# Build the container image for local development
build-image:
    docker build --load door_tracker -t docker.io/roboteamtwente/rfid-tracker-serve:latest

# Build & upload the container image
upload-image:
    docker build --push door_tracker --platform linux/amd64,linux/arm64 \
        -t docker.io/roboteamtwente/rfid-tracker-serve:$(uv version --short | cut -d. -f-3) \
        -t docker.io/roboteamtwente/rfid-tracker-serve:$(uv version --short | cut -d. -f-2) \
        -t docker.io/roboteamtwente/rfid-tracker-serve:$(uv version --short | cut -d. -f-1) \
        -t docker.io/roboteamtwente/rfid-tracker-serve:latest
