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
    lefthook run --all-files --force pre-commit

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

# Release a new version
release:
    cog bump --auto

# Build & upload the container image
deliver:
    std //repo/containers/prod-patch:publish
    std //repo/containers/prod-minor:publish
    std //repo/containers/prod-major:publish
    std //repo/containers/prod-latest:publish
