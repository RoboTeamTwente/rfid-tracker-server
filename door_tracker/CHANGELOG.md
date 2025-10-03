<!-- markdownlint-disable MD024  -->

# Changelog

## v2.1.0 (2025-10-03)

### Feat

- **api**: allow register_scan with trailing slash again
- **admin**: add filters to admin page
- **model**: add statistics calculation
- **admin**: sort everything

### Refactor

- **tooling**: add statistics scope for conventional commits
- **statistics**: move statistics calculations to statistics.py
- prettify admin page, changes in models
- **midas**: split log table into checkin and checkout
- **midas**: add midas app, put new models in it

## v2.0.0 (2025-10-01)

### BREAKING CHANGE

- register_scan endpoint requires no slash at the end now
- docker image autocreates a superuser now.

### Feat

- **tooling**: add example backup env vars to compose.yaml
- **containers**: mount credentials in the example compose.yaml
- **tooling**: gitignore the credentials folder
- **containers**: make backup credentials file location configurable
- **webui**: add a button to redirect to dashboard
- **tooling**: add conventional commits to vscode
- **docker**: autocreate an admin on container startup
- **commands**: add init_admin

### Fix

- **backups**: add packages required to run `django backup_website`

### Refactor

- **api**: removed a slash at the end of register_scan
- **css**: move log in button to nav bar

## v1.2.0 (2025-09-28)

### Feat

- **tooling**: abort bump-version script when worktree is dirty
- **tooling**: add test step to release script

### Refactor

- **tooling**: get rid of next-version
- **tooling**: scripts: s/release/deliver/; release = bump && deliver
- **tooling**: move version bump out of release into a separate script
- **webui**: do not nest BEM css selectors
- **webui**: BEMify base.css

### Perf

- **tooling**: let cz bump fail fast
- **tooling**: prune unused git hooks in bump-version script

## v1.1.0 (2025-09-27)

### Feat

- **containers**: add sqlite to the container image

### Fix

- **admin**: fix export of large logs
- **tooling**: make release script follow commitizen's tag schema
- **tooling**: show `cd` in trace of \*-container scripts
- **webui**: fix base.html modal z-index

### Refactor

- **views**: inline current_user_logs
- **views**: remove unused serializers & fields

### Perf

- **tooling**: speed up release script

## v1.0.0 (2025-09-27)

### Feat

- **devenv**: add release script
- **devenv**: add next-version script
- **devenv**: add current-version script
- **devenv**: add commitizen
- **docker**: don't renovate compose.yaml
- **devenv**: add upload-container-to script
- add profile edit modal
- add tag deletion confirmation
- **admin**: auto-generate scanner ID on creation

### Fix

- **docs**: exclude a duplicate CHANGELOG from Doxygen docs
- **edit_profile**: handle half-filled membership
- **docker**: run debug in local compose
- **model**: fucking timezones
- **model**: makemigrations --merge
- **model**: fucking timezones
- **model**: fucking timezones
- **edit_profile**: fix edit membership when no membership found
- **edit_profile**: handle empty fields in submission
- **css**: resurrect a wrongly deleted line
- **webui**: fix edit_profile 500 when no current membership
- **api**: pick correct statistics row
- **css**: make all modals of same width
- make statistics & profile pages work when the user is not a member
- **api**: fix queries
- **api**: register_scan: update JSON keys to match the OpenAPI spec
- **fmt**: copy my local .prettierrc into the repo

### Refactor

- **devenv**: hide superfluous debug output in \*-container scripts
