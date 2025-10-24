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
check:
    # run tests & pre-commit hooks
    CI=1 lefthook run --all-files --force pre-commit
    # also check that the container still builds
    std //repo/containers/prod-latest:build

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

# Build & upload the container image
deliver:
    std //repo/containers/prod-patch:publish
    std //repo/containers/prod-minor:publish
    std //repo/containers/prod-major:publish
    std //repo/containers/prod-latest:publish
