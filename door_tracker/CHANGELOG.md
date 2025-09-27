<!-- markdownlint-disable MD024  -->

# Changelog

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
