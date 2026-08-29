<!-- markdownlint-disable MD033 -->

# Welcome

[![docs exist](https://img.shields.io/badge/docs-exist-blue)](https://roboteamtwente.github.io/rfid-tracker-server)
[![wiki exists](https://img.shields.io/badge/wiki-exists-blue)](https://wiki.roboteamtwente.nl/technical/rfidtracker/main)
![GitHub branch check runs](https://img.shields.io/github/check-runs/roboteamtwente/rfid-tracker-server/main)

## Getting started

1. Install [Just](https://just.systems) (the task runner)
1. Install [UV](https://astral.sh/uv) (the Python package manager)
2. Install dependencies: `uv sync`
3. Run the development server: `just dev`

## Docker images

Use `door_tracker/Dockerfile`. For convenience, use `just build-image` to build the image for local use, and use `just upload-image` to build it for both AMD64 and Aarch64 CPU architectures and upload it to Dockerhub. You'll need to be logged in for the upload to succeed.

## Development server

The development server should start automatically. If it dies, or you
want to restart it, press <kbd>Ctrl+Shift+B</kbd>. You might need to
press <kbd>Enter</kbd> afterwards.

> [!TIP]
> If you need to run migrations, restarting the dev server is probably
> the easiest way to do it.

## Daily operations

Most common operations are available from `Tasks: Run Task`. They come in three flavours:

1. scripts: these perform common tasks. You'll run them the most often
   They are also available in the terminal.

2. packages: these build parts of the project. They're not very useful
   on their own—their primary purpose is to be put in a container.

3. containers: these build & upload docker containers to Docker Hub.

### Scripts

To create a new database, run `init`. It'll set up a new admin user.
It's safe to run this command if you already have a database.

The most-used script is `makemigrations`. it creates migrations (d'oh!).
Run it when you change `models.py`.

If a tutorial, Stack Overflow, etc. asks you to run `python manage.py
foo bar`, run `django foo bar` instead. This script works from any
directory, in contrast to `manage.py`.

## Releasing

First, generate the changelog: create a new feature branch, run `just
release` (it will make a commit), and merge it. Don't delete the branch
just yet.

After Github shows a green checkmark against the release commit, tag it
with the new version (i.e. `git tag v1.2.3`) and push the tag.

If the checkmark was not green, you will see an error message. In this
case, wait and try again. If the push was successful, you will soon see
the new release on Github and Dockerhub.

## Deploying

After the image is update on Dockerhub, it is possible to deploy it on
the server:

```bash
ssh your-username@ip-of-the-server # ask the admin for access
cd ~/docker
vim docker-compose.yml # update the image tag, if it was a major release
docker compose pull rfid-tracker # download the new image
docker compose up -d rfid-tracker # restart with the new image
docker compose logs -f rfid-tracker # confirm that the server didn't die
```

## Pitfalls

### Pre-commit

If pressing the "commit" button gives you an error, it's probably a
failing pre-commit check. Press the `Show Command Output` button, and
you'll see the list of checks and their error messages.

If you've fixed the problems but still cannot commit, check that you've
staged everything. Some pre-commit hooks run code formatters, and you
need to manually stage their output.

### Direnv

direnv extension fails silently. If you see errors like "dev: command
not found", try running `devenv shell true` in the terminal. It should
finish with no errors. If it didn't, then Dmytro broke Nix again.

Terminal will not pick up the new environment until you restart it. You
should see a warning sign if direnv wants you to do it.
