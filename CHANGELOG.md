# Changelog

All notable changes to this project will be documented in this file.

## 2.16.2 - 2026-02-26

### Bug Fixes

- *(build)* Fixup py-ubjson build definition


### Miscellaneous Tasks

- *(deps)* Update ghcr.io/astral-sh/uv:debian docker digest to 3f5bf82
- *(deps)* Update renovatebot/github-action action to v46
- *(deps)* Update renovatebot/github-action action to v46.1.2
- *(deps)* Update ghcr.io/astral-sh/uv:debian docker digest to d558f1a
- *(deps)* Update ghcr.io/astral-sh/uv:debian docker digest to f9c0968
- *(deps)* Update ghcr.io/astral-sh/uv:debian docker digest to 87e35fb
- *(deps)* Lock file maintenance
- *(version)* V2.16.2


## 2.16.1 - 2026-02-17

### Miscellaneous Tasks

- *(version)* V2.16.1


## 2.16.0 - 2026-02-17

### Features

- *(docs)* Document release process
- *(docs)* Document deployment of a new release


### Miscellaneous Tasks

- *(deps)* Update renovatebot/github-action action to v44.2.1
- *(deps)* Update ghcr.io/astral-sh/uv:debian docker digest to 748d5d5
- *(deps)* Update renovatebot/github-action action to v44.2.2
- *(deps)* Update ghcr.io/astral-sh/uv:debian docker digest to cbdbeec
- *(deps)* Update ghcr.io/astral-sh/uv:debian docker digest to 7b91606
- *(deps)* Update renovatebot/github-action action to v44.2.3
- *(deps)* Update ghcr.io/astral-sh/uv:debian docker digest to c3854e7
- *(deps)* Update ghcr.io/astral-sh/uv:debian docker digest to 7393efb
- *(deps)* Update renovatebot/github-action action to v44.2.4
- *(deps)* Update renovatebot/github-action action to v44.2.5
- *(deps)* Update actions/checkout action to v6.0.2
- *(deps)* Update dependency django to v5.2.9 [security]
- *(deps)* Update ghcr.io/astral-sh/uv:debian docker digest to 1cda6dd
- *(deps)* Update ghcr.io/astral-sh/uv:debian docker digest to 8fcd673
- *(deps)* Update actions/checkout digest to de0fac2
- *(deps)* Update ghcr.io/astral-sh/uv:debian docker digest to 8375c02
- *(deps)* Update dependency django to v6.0.2 [security]
- *(deps)* Update ghcr.io/astral-sh/uv:debian docker digest to e2acc84
- *(deps)* Update ghcr.io/astral-sh/uv:debian docker digest to 14141ad
- *(version)* V2.16.0


### Refactor

- *(docs)* Clarify instructions in README


## 2.15.2 - 2025-12-21

### Miscellaneous Tasks

- *(deps)* Update actions/checkout action to v6
- *(version)* V2.15.2


## 2.15.1 - 2025-12-21

### Bug Fixes

- *(tooling)* Fix build with python 3.14


### Miscellaneous Tasks

- *(deps)* Upgrade to Python 3.14
- *(deps)* Update renovatebot/github-action action to v44
- *(deps)* Update determinatesystems/nix-installer-action action to v21
- *(deps)* Pin ghcr.io/astral-sh/uv docker tag to a87efc5
- *(deps)* Update actions/checkout action to v5.0.1
- *(deps)* Update actions/checkout digest to 93cb6ef
- *(deps)* Update actions/create-github-app-token digest to 7e473ef
- *(deps)* Update ghcr.io/astral-sh/uv:debian docker digest to ed8b7cf
- *(deps)* Update renovatebot/github-action action to v44.0.5
- *(deps)* Update ghcr.io/astral-sh/uv:debian docker digest to e94b924
- *(deps)* Update actions/create-github-app-token digest to 29824e6
- *(deps)* Update renovatebot/github-action action to v44.2.0
- *(deps)* Update ghcr.io/astral-sh/uv:debian docker digest to 0dbcb81
- *(version)* V2.15.1


## 2.15.0 - 2025-11-17

### Bug Fixes

- *(tooling)* Don't build for Darwin


### Features

- *(tooling)* Add hydra jobs


### Miscellaneous Tasks

- *(deps)* Update nix dependencies
- *(deps)* Update renovatebot/github-action action to v43.0.19
- *(deps)* Update renovatebot/github-action action to v43.0.20
- *(version)* V2.15.0
- *(No Category)* Nix flake update


## 2.14.0 - 2025-10-25

### Features

- *(tooling)* Automatically create GitHub release


### Miscellaneous Tasks

- *(version)* V2.14.0


## 2.13.0 - 2025-10-25

### Features

- *(tooling)* Implement releases in crow CI


### Miscellaneous Tasks

- *(version)* V2.13.0


## 2.12.0 - 2025-10-24

### Bug Fixes

- *(tooling)* Enable flakes in crow CI
- *(tooling)* Don't use entrypoint
- *(tooling)* Set CI=1 in crow
- *(tooling)* Split test workflow
- *(tooling)* Run test-thorough in the merge queue
- *(tooling)* Remove unused block type `scripts`
- *(tooling)* Check release branches as well


### Features

- *(tooling)* Add crow CI
- *(tooling)* Show build output when running nix develop in crow CI
- *(tooling)* Remove GHA test workflow
- *(tooling)* Port test-fast to Crow CI
- *(tooling)* Add schema to Crow CI workflow
- *(tooling)* Parallelize fast and thorough tests
- *(tooling)* Fail on change in `just check`


### Miscellaneous Tasks

- *(deps)* Update dependency astral-sh/uv to v0.9.5
- *(version)* V2.12.0


### Performance

- *(tooling)* Parallelize test-thorough
- *(tooling)* Enable nix parallelism in CI


### Refactor

- *(tooling)* Use YAML anchors
- *(tooling)* Same check name for PR and MQ
- *(tooling)* From cocogitto to git-cliff
- *(tooling)* Use git-cliff in just release
- *(No Category)* Rewrite CHANGELOG.md using git-cliff


## 2.11.1 - 2025-10-21

### Bug Fixes

- *(webui)* Remove erroneous ".0"s from user_statistics


### Miscellaneous Tasks

- *(version)* V2.11.1


## 2.11.0 - 2025-10-20

### Features

- *(tooling)* Only allow bumping from release branches
- *(tooling)* Ignore merges when checking for conventional commits
- *(tooling)* Ignore merges when checking for conventional commits (#62)


### Miscellaneous Tasks

- *(deps)* Update astral-sh/setup-uv digest to 2ddd2b9
- *(deps)* Update renovatebot/github-action action to v43.0.18
- *(version)* V2.11.0


### Styling

- *(tooling)* Remove default settings from cog.toml


## 2.10.1 - 2025-10-19

### Bug Fixes

- *(deps)* Downgrade to python3.13
- *(tooling)* Configure git author for bump commits
- *(tooling)* Don't try to be clever and check all commit messages
- *(tooling)* Make release workflow work
- *(tooling)* Push the release commit to current branch as well
- *(tooling)* Explicitly skip v2.10.0 because GitHub refuses to work
- *(tooling)* Revert "explicitly skip v2.10.0 because GitHub refuses to work"
- *(webui)* Change the checkin to use a timezone.now variable instead of calling it 3 times (future-proof)
- *(webui)* Include seconds in remote checkout autocomplete


### Features

- *(tooling)* Check for container build failures in CI
- *(webui)* Add remote checkin functionality to the sessions page
- *(webui)* Auto complete current time for remote checkout modal


### Miscellaneous Tasks

- *(deps)* Update dependency astral-sh/uv to v0.9.4
- *(version)* V2.10.0
- *(version)* V2.10.1


### Performance

- *(tooling)* Don't do thorough checks before merge queue
- *(tooling)* Remove magic-nix-cache and halve build times


### Refactor

- *(statistics)* Cleanup statistics a bit
- *(tooling)* Trigger releases from github actions
- *(tooling)* Uv sync in a separate step
- *(tooling)* Update Justfile to reflect new release workflow
- *(tooling)* Explicitly push new tag
- *(webui)* Fix some of the padding in user profile tags


### Styling

- *(tooling)* Use long argument names for readability


## 2.9.1 - 2025-10-17

### Bug Fixes

- *(tooling)* Fix automatic release creation


### Miscellaneous Tasks

- *(version)* V2.9.1


### Performance

- *(tooling)* Only check the first branch being pushed


## 2.9.0 - 2025-10-17

### Bug Fixes

- *(admin)* Fix filtering by subteam for sessions & assignments
- *(deps)* Disable brotli compression of static assets


### Features

- *(webui)* Implement export of sessions


### Miscellaneous Tasks

- *(deps)* Update transitive dependencies
- *(deps)* Update to python3.14
- *(version)* V2.9.0


### Refactor

- *(webui)* Re-organize base.css
- *(webui)* Fix the navigation bar on mobile to be a bit more centered


## 2.8.0 - 2025-10-16

### Features

- *(tooling)* Check that commit messages follow conventional commits
- *(tooling)* Check commit messages in pre-push instead of commit-msg
- *(tooling)* Automatically create github releases from tags
- *(webui)* Hide the admin pages from normal users
- *(webui)* Add favicon


### Miscellaneous Tasks

- *(deps)* Update dependency astral-sh/uv to v0.9.3
- *(tooling)* Add sqlite wal to gitignore
- *(version)* V2.8.0


### Performance

- *(statistics)* Disable the update_statistics job (not needed for midas)
- *(tooling)* Don't run tests on push to main


### Refactor

- *(tooling)* Use same python for shell & container
- *(tooling)* Force UV to use nix-provided python
- *(webui)* Add all the css code in base.css


### Styling

- *(webui)* Change icon from white on purple to purple on transparent
- *(No Category)* Prefer relative imports


## 2.7.2 - 2025-10-13

### Bug Fixes

- *(webui)* Prevent race conditions when registering a tag


### Miscellaneous Tasks

- *(version)* V2.7.2


## 2.7.1 - 2025-10-13

### Miscellaneous Tasks

- *(version)* V2.7.1


### Styling

- *(webui)* Reorder sessions table's columns & align times right


## 2.7.0 - 2025-10-13

### Bug Fixes

- *(webui)* Fix UNIQUE constraint failed when registering 2 tags at the same time


### Features

- *(webui)* Promote midas to be the default app


### Miscellaneous Tasks

- *(version)* V2.7.0


## 2.6.1 - 2025-10-13

### Bug Fixes

- *(api)* Allow checking out from yesterday's session
- *(model)* Add migrations forgotten in #17
- *(tooling)* Break deadlock between checks and tags
- *(tooling)* Make the makemigrations check effective


### Miscellaneous Tasks

- *(version)* V2.6.1


## 2.6.0 - 2025-10-13

### Bug Fixes

- *(model)* Delete existing scanners in midas before migration from webui
- *(statistics)* Fix getting proper start date for quota
- *(tooling)* Enable tests in merge queue


### Features

- *(tooling)* Install github cli


### Miscellaneous Tasks

- *(deps)* Update python docker tag to v3.14
- *(deps)* Update dependency astral-sh/uv to v0.9.2
- *(deps)* Update astral-sh/setup-uv digest to 3259c62
- *(deps)* Update renovatebot/github-action action to v43.0.17
- *(version)* V2.6.0


### Refactor

- *(model)* Restrict deletion of some models when they are referred to through foreign keys


## 2.5.3 - 2025-10-10

### Bug Fixes

- *(statistics)* Fix error of getting assignment starting day before start_day
- *(webui)* Do not crash when user has no assignments


### Miscellaneous Tasks

- *(version)* V2.5.3


## 2.5.2 - 2025-10-10

### Bug Fixes

- *(webui)* Correct assignment selection logic on user_statistics


### Miscellaneous Tasks

- *(version)* V2.5.2


## 2.5.1 - 2025-10-10

### Bug Fixes

- *(model)* Migrate scanners as well


### Miscellaneous Tasks

- *(version)* V2.5.1


### Build

- *(tooling)* Add a task for generating the github release


## 2.5.0 - 2025-10-10

### Bug Fixes

- *(api)* Make checkout work in midas
- *(api)* Show proper error message when renaming a tag
- *(api)* Correct priority of actions on register_scan
- *(model)* Make edit_profile modal create a new Assignment instead of modifying the existing one
- *(tooling)* Tell vscode to not type random commands in the terminal
- *(tooling)* Gitignore sqlite wal
- *(webui)* Remove unused endpoints from midas
- *(webui)* Add tags by name, not by ID


### Features

- *(model)* Add a script to migrate data from webui to midas
- *(tooling)* Skip docs deploy on the debug branch
- *(tooling)* Label container images with source commit & version
- *(tooling)* Add `just release`
- *(webui)* Add complete side navigation bar with css tweaks for all pages
- *(webui)* Add side nav bar logic for both desktop and mobile view.


### Miscellaneous Tasks

- *(deps)* Update dependency astral-sh/uv to v0.9.1
- *(version)* V2.5.0


### Refactor

- *(tooling)* Use std instead of devenv
- *(tooling)* Replace commitizen with cocogitto
- *(tooling)* Regenerate CHANGELOG.md with cocogitto
- *(webui)* User midas logo in midas


### Styling

- *(No Category)* Clean various code smells


## 2.4.0 - 2025-10-09

### Bug Fixes

- *(api)* Don't use .date()
- *(api)* Don't use .date()
- *(models)* Make Quota.name non-optional
- *(statistics)* Fix monthly and weekly quota calculation in statistics and other minor bugs
- *(tooling)* Automatically abort duplicate releases
- *(webui)* Point midas modals to midas


### Features

- *(models)* Add Assignment.objects.filter_effective()
- *(statistics)* Add datetime helper functions
- *(webui)* Add new edit profile functionality
- *(webui)* Add rename and delete tag on user profile page functionality
- *(webui)* Port signup page to midas
- *(webui)* Add filters to get all statistics for admin overview page
- *(webui)* Allow date ranges instead of just a single date in get all statistics for the admin overview
- *(webui)* Make user_statistics page work


### Miscellaneous Tasks

- *(deps)* Update astral-sh/setup-uv action to v7
- *(deps)* Update renovatebot/github-action action to v43.0.16 (#11)
- *(deps)* Update dependency astral-sh/uv to v0.9.0 (#12)


### Performance

- *(statistics)* Run update_statistics in background


### Refactor

- *(admin)* Move global admin config from webui to door_tracker
- *(admin)* Allow creating claimed tags from admin page (for debugging only)
- *(css)* Add side navigation bar (work in progress).
- *(webui)* Remove an extra arrow from uer profile icons


### Styling

- *(admin)* Rename get_subteams to subteam_names
- *(tooling)* Use double quotes in .toml files
- *(webui)* Remove extra newlines from midas/index.html


### Bump

- *(No Category)* Version 2.3.0 → 2.4.0


## 2.3.0 - 2025-10-07

### Bug Fixes

- *(tooling)* Move ruff config to root of repo


### Documentation

- *(api)* Make API docs look presentable


### Features

- *(api)* Add autogenerated API docs


### Styling

- *(No Category)* Run ruff on the entire repo


### Bump

- *(No Category)* Version 2.2.3 → 2.3.0


## 2.2.3 - 2025-10-07

### Performance

- *(tooling)* Do not cache deliver workflow


### Refactor

- *(api)* Register_scan: allow both tag_id and card_id


### Bump

- *(No Category)* Version 2.2.2 → 2.2.3


### Ci

- *(tooling)* Add a job to run thorough tests


## 2.2.2 - 2025-10-07

### Bug Fixes

- *(tooling)* Bump-version: cd to repo root before running checks


### Miscellaneous Tasks

- *(deps)* Pin determinatesystems/magic-nix-cache-action action to 5656843
- *(deps)* Update dependency astral-sh/uv to v0.8.24


### Performance

- *(tooling)* Reduce amount of docker image layers


### Bump

- *(No Category)* Version 2.2.1 → 2.2.2


## 2.2.1 - 2025-10-06

### Bug Fixes

- *(tooling)* Move whitenoise app higher than staticfiles
- *(tooling)* Update magic-nix-cache-action


### Miscellaneous Tasks

- *(deps)* Pin actions/checkout action to 08c6903
- *(deps)* Pin determinatesystems/nix-installer-action action to 129f079
- *(deps)* Update determinatesystems/nix-installer-action action to v20


### Build

- *(tooling)* Pin detsys-nix actions


### Bump

- *(No Category)* Version 2.2.0 → 2.2.1


### Ci

- *(tooling)* Bump-version: automatically push & generate github release


## 2.2.0 - 2025-10-06

### Bug Fixes

- *(api)* Rename new register_scan to avoid name collisions
- *(api)* Use RegisterScan.make() to cut down on copypaste
- *(statistics)* Keep it from breaking with the time change (DST)
- *(statistics)* Remove need to pass total minutes as an argument to get the weekly average
- *(statistics)* Remove leftover debug print lines
- *(tooling)* Update devenv
- *(tooling)* Remove duplicate ruff config
- *(tooling)* Ignore long lines in CHANGELOG.md
- *(webui)* Make midas html point to midas' base.html
- *(webui)* Run s/webui/midas in views.py


### Features

- *(api)* Port API to midas
- *(model)* Add related_name to ForeignKeys
- *(tests)* Add tests for midas
- *(tooling)* Run tests in pre-commit hook
- *(tooling)* Automatically upload releases to dockerhub
- *(tooling)* Enforce conventional commits using commitizen
- *(webui)* Add new user dashboard with new database logic
- *(webui)* Make User Profile displays user informtion and add tag functionality
- *(webui)* Add htmx instead of hard refresh on user_profile and tweak views user_profile to return HtmlResponse
- *(webui)* Add function for get everyone's statistics in one go


### Miscellaneous Tasks

- *(deps)* Update dependency astral-sh/uv to v0.8.23
- *(deps)* Update renovatebot/github-action action to v43.0.15
- *(release)* Bump 2.1.0 -> 2.2.0


### Refactor

- *(api)* Use objects.create() instead of save()
- *(statistics)* Accept user directly rather than request
- *(webui)* Remove useless order_by() in is_checked_in()
- *(webui)* Namespace midas urls


### Styling

- *(webui)* Sort urls.py
- *(webui)* Remove commented imports


### Testing

- *(api)* Repeat check-in/out 10 times


## 2.1.0 - 2025-10-03

### Features

- *(admin)* Sort everything
- *(admin)* Add filters to admin page
- *(api)* Allow register_scan with trailing slash again
- *(model)* Add statistics calculation


### Miscellaneous Tasks

- *(release)* Bump 2.0.0 -> 2.1.0


### Refactor

- *(midas)* Add midas app, put new models in it
- *(midas)* Split log table into checkin and checkout
- *(statistics)* Move statistics calculations to statistics.py
- *(tooling)* Add statistics scope for conventional commits
- *(No Category)* Prettify admin page, changes in models


### Styling

- *(midas)* Reorder models in the admin page


## 2.0.0 - 2025-10-01

### Bug Fixes

- *(backups)* Add packages required to run `django backup_website`


### Features

- *(commands)* Add init_admin
- *(containers)* Make backup credentials file location configurable
- *(containers)* Mount credentials in the example compose.yaml
- *(docker)* Autocreate an admin on container startup
  - **BREAKING**: docker image autocreates a superuser now.
- *(tooling)* Add conventional commits to vscode
- *(tooling)* Gitignore the credentials folder
- *(tooling)* Add example backup env vars to compose.yaml
- *(webui)* Add a button to redirect to dashboard


### Miscellaneous Tasks

- *(deps)* Update renovatebot/github-action action to v43.0.14
- *(deps)* Update astral-sh/setup-uv digest to d0cc045
- *(release)* Bump 1.2.0 -> 2.0.0


### Refactor

- *(api)* Removed a slash at the end of register_scan
  - **BREAKING**: register_scan endpoint requires no slash at the end now
- *(css)* Move log in button to nav bar


## 1.2.0 - 2025-09-28

### Features

- *(tooling)* Add test step to release script
- *(tooling)* Abort bump-version script when worktree is dirty


### Miscellaneous Tasks

- *(release)* Bump 1.1.0 -> 1.2.0


### Performance

- *(tooling)* Prune unused git hooks in bump-version script
- *(tooling)* Let cz bump fail fast


### Refactor

- *(tooling)* Move version bump out of release into a separate script
- *(tooling)* Scripts: s/release/deliver/; release = bump && deliver
- *(tooling)* Get rid of next-version
- *(webui)* BEMify base.css
- *(webui)* Do not nest BEM css selectors


## 1.1.0 - 2025-09-27

### Bug Fixes

- *(admin)* Fix export of large logs
- *(tooling)* Show `cd` in trace of *-container scripts
- *(tooling)* Make release script follow commitizen's tag schema
- *(webui)* Fix base.html modal z-index


### Features

- *(containers)* Add sqlite to the container image


### Miscellaneous Tasks

- *(release)* Bump 1.0.0 -> 1.1.0


### Performance

- *(tooling)* Speed up release script


### Refactor

- *(views)* Remove unused serializers & fields
- *(views)* Inline current_user_logs


### Styling

- *(webui)* Make profile action buttons more prominent
- *(webui)* Run <script>s through prettier


## 1.0.0 - 2025-09-27

### Bug Fixes

- *(api)* Register_scan: update JSON keys to match the OpenAPI spec
- *(api)* Fix queries
- *(api)* Pick correct statistics row
- *(css)* Make all modals of same width
- *(css)* Resurrect a wrongly deleted line
- *(docker)* Run debug in local compose
- *(docs)* Exclude a duplicate CHANGELOG from Doxygen docs
- *(edit_profile)* Handle empty fields in submission
- *(edit_profile)* Fix edit membership when no membership found
- *(edit_profile)* Handle half-filled membership
- *(fmt)* Copy my local .prettierrc into the repo
- *(model)* Fucking timezones
- *(model)* Fucking timezones
- *(model)* Makemigrations --merge
- *(model)* Fucking timezones
- *(webui)* Fix edit_profile 500 when no current membership
- *(No Category)* Add migrations for last 2 commits
- *(No Category)* Make statistics & profile pages work when the user is not a member


### Documentation

- *(gha)* Comment on triggers of gha workflows
- *(No Category)* Add scanner api
- *(No Category)* Move schema.puml to docs
- *(No Category)* Update README Getting Stared to use nix instead of devcontainers
- *(No Category)* Add doxygen
- *(No Category)* Add docs badge to README
- *(No Category)* Exclude migrations from the auto-generated docs
- *(No Category)* Add github actions status badge to README
- *(No Category)* Add wiki link to README
- *(No Category)* Remove all mentions of devcontainers
- *(No Category)* Add CHANGELOG.md


### Features

- *(admin)* Auto-generate scanner ID on creation
- *(devenv)* Add upload-container-to script
- *(devenv)* Add commitizen
- *(devenv)* Add current-version script
- *(devenv)* Add next-version script
- *(devenv)* Add release script
- *(docker)* Don't renovate compose.yaml
- *(No Category)* Add tag deletion confirmation
- *(No Category)* Add profile edit modal


### Miscellaneous Tasks

- *(deps)* Update actions/checkout action to v5
- *(deps)* Update actions/create-github-app-token action to v2
- *(deps)* Update dependency font-awesome to v7
- *(deps)* Pin dependencies
- *(deps)* Update dependency astral-sh/uv to v0.8.20
- *(deps)* Update renovatebot/github-action action to v43.0.13
- *(deps)* Pin dependencies
- *(deps)* Update mattnotmitt/doxygen-action action to v1.12.0
- *(deps)* Update actions/upload-pages-artifact action to v4
- *(deps)* Update actions/checkout action to v5
- *(deps)* Update dependency astral-sh/uv to v0.8.21
- *(deps)* Update roboteamtwente/rfid-tracker-serve docker digest to 4ddccc0
- *(deps)* Update dependency astral-sh/uv to v0.8.22
- *(deps)* Update roboteamtwente/rfid-tracker-serve docker digest to b25e65d
- *(deps)* Update roboteamtwente/rfid-tracker-serve docker digest to f157deb
- *(deps)* Update roboteamtwente/rfid-tracker-serve docker digest to 1e474b6
- *(deps)* Update roboteamtwente/rfid-tracker-serve docker digest to b8dc9ec
- *(deps)* Update roboteamtwente/rfid-tracker-serve docker digest to efe6204
- *(deps)* Update roboteamtwente/rfid-tracker-serve docker digest to 0faffdc
- *(docs)* Run prettier on README.md
- *(release)* Force a major release
  - **BREAKING**: force a major release
- *(release)* Bump 0.1.0 -> 1.0.0


### README

- *(No Category)* Mention pre-commit pitfalls


### Refactor

- *(devenv)* Hide superfluous debug output in *-container scripts


### Styling

- *(devenv)* Move prettier git-hook into a separate paragraph
- *(user_profile)* Clarify UI message
- *(user_profile)* Reorder profile fields to match edit_profile
- *(No Category)* Update message


### Testing

- *(No Category)* Add tests for /register_scan endpoint


### Admin

- *(No Category)* Fix get_app_list method
- *(No Category)* Add filtering by subteam and/or person to Log admin page
- *(No Category)* Adjust default sorting in admin page to show most recent first
- *(No Category)* Show tag status
- *(No Category)* Make logs and memberships searchable
- *(No Category)* Add CSV export feature for logs
- *(No Category)* Use django helpers to generate register link
- *(No Category)* Adapt to new, stringy, tag_id


### Build

- *(pip)* Remove duplicate dependency
- *(No Category)* Package the project with Nix
- *(No Category)* Add a production container
- *(No Category)* Simplify build instructions
- *(No Category)* Add a "first-start" package


### Ci

- *(docs)* Deploy doxygen docs to github pages
- *(git)* Add commitizen config
- *(test)* Run test workflow on renovate/* branches
- *(test)* Actually make it run on renovate/* branches


### Cicd

- *(No Category)* Compose: run in production mode
- *(No Category)* Enable Renovate
- *(No Category)* Enable manual trigger of Renovate


### Css

- *(No Category)* Use nested css to simplify selectors


### Devcontainer

- *(No Category)* Init
- *(No Category)* Use custom Dockerfile
- *(No Category)* Mount /nix in a volume for faster rebuilds
- *(No Category)* Move nix commands to onCreateCommand to use the cache volume
- *(No Category)* Generate vscode tasks
- *(No Category)* Make `dev` script default and autostart it on folder open
- *(No Category)* Implement login to dockerhub
- *(No Category)* Fix container upload
- *(No Category)* Add `repl` script
- *(No Category)* Add curl, httpie
- *(No Category)* Script docker-login: provide default username, pass arguments through
- *(No Category)* Force container build every time (devenv caches too much)
- *(No Category)* Remove


### Devenv

- *(No Category)* Add testing
- *(No Category)* Add virtualenv to $PATH
- *(No Category)* Add scripts
- *(No Category)* Do not hardcode virtualenv location
- *(No Category)* Generate treefmt.toml
- *(No Category)* Simplify test
- *(No Category)* Automigrate while in development
- *(No Category)* Make scripts accept arguments
- *(No Category)* Add a script to create a new database
- *(No Category)* Add shfmt and taplo code formatters
- *(No Category)* Add git hooks
- *(No Category)* Build all containers manually, add them to .vscode/tasks.json
- *(No Category)* Scripts: add build-container, upload-container


### Django

- *(No Category)* Init
- *(No Category)* Create app WebUI
- *(No Category)* Change production URL
- *(No Category)* Trust reverse proxy in production


### Formatting

- *(No Category)* Get rid of treefmt
- *(No Category)* Set ruff to use max. 80 characters per line
- *(No Category)* Add prettier
- *(No Category)* Reformat entire repo to get our new, shorter, lines
- *(No Category)* Make ruff sort imports
- *(No Category)* Format python with single quotes


### Frontend

- *(No Category)* Use {% csrf_token %} instead of parsing cookies


### Gha

- *(No Category)* Use working-directory


### Git

- *(No Category)* Run pre-commit on all files
- *(No Category)* Disable lychee pre-commit hook
- *(No Category)* Mark .envrc as a bash script
- *(No Category)* Always use LF line endings
- *(No Category)* Add djhtml pre-commit hook to format django templates
- *(No Category)* Add makemigrations pre-commit hook
- *(No Category)* Silence some pre-commit warnings
- *(No Category)* Run pre-commit on all files


### Html

- *(No Category)* Use sans-serif font
- *(No Category)* Fadeout messages
- *(No Category)* Make RoboTeam logo a link to /
- *(No Category)* Add {% modal %} tag
- *(No Category)* Set max-width for main content
- *(No Category)* Update user_profile.html to use base.html and {% modal %}
- *(No Category)* Use {{user}} directly
- *(No Category)* Cleanup css & js in index.html and user_profile.html
- *(No Category)* Tweak gaps in user_profile.html
- *(No Category)* Update user_statistics.html to use base.html & cleanup css
- *(No Category)* Index.html: don't hide separator after the last "recent scan"


### Lychee

- *(No Category)* Ignore django templates


### Model

- *(No Category)* Add the "forever data" table
- *(No Category)* Adjust ordering & pretty names on admin page
- *(No Category)* Allow unclaimed tags, update admin to match
- *(No Category)* Do not sort models in the admin
- *(No Category)* Mark remote checkouts as 'WebUI' on admin page
- *(No Category)* Add `filter_effective` query to Membership table
- *(No Category)* Make tag ID optional, add get_state()
- *(No Category)* Tag.person(): return none if owner is none
- *(No Category)* Tag: handle nullable fields in methods
- *(No Category)* Log: use | separator when stringifying
- *(No Category)* Add Scanner
- *(No Category)* Add "registered" log type
- *(No Category)* Make tag_id a string
- *(No Category)* Add Tag.objects.get_pending() method
- *(No Category)* Fix is_checked_in
- *(No Category)* Don't use memberships with starting_from in the future


### Models

- *(No Category)* Use django.contrib.auth.User instead of Person
- *(No Category)* Make Log.tag optional, to model WebUI self-checkout


### Nix

- *(No Category)* Init
- *(No Category)* Let formatters be installed by pre-commit
- *(No Category)* Add openssh (for git pull/push)
- *(No Category)* Scripts {build,upload}-container: make them work in any directory
- *(No Category)* Don't rebuild environment every time pyproject.toml is changed


### Packaging

- *(No Category)* Build container manually, get 10x size reduction
- *(No Category)* Run tini as PID 1, to properly handle signals in the container
- *(No Category)* Add django templates to the python virtualenv
- *(No Category)* Add compose.yaml
- *(No Category)* Add admin html overrides to the production package


### Pre-commit

- *(No Category)* Disable check-python (use ruff instead)
- *(No Category)* Enable ruff-format
- *(No Category)* Update hook list


### Python

- *(No Category)* Install optional dependencies for python-lsp-server
- *(No Category)* Explicitly add daphne server to dependency list
- *(No Category)* Remove ruff from dependencies, it is installed with nix instead
- *(No Category)* Remove unused dependencies
- *(No Category)* Include static files in the docker image


### Schema

- *(No Category)* Add crow feet
- *(No Category)* Fix type of tag_person::tag_id (foreign_key -> ID)
- *(No Category)* Remove a field left over from previous design
- *(No Category)* Encode many-to-many relationship directly, not through an extra table
- *(No Category)* Add membership & job tables


### Uv

- *(No Category)* Init


### View

- *(No Category)* Remove link to nonexistent style.css
- *(No Category)* Export: check authentication


### Views

- *(No Category)* Update register_scan
- *(No Category)* Automate serializer error message generation
- *(No Category)* Change_status: use serializer
- *(No Category)* Register_scan: clarify error message
- *(No Category)* Remove ui prefix
- *(No Category)* Register_scan: use hex instead of base64 for card_id
- *(No Category)* Register_scan: don't parse tag_id
- *(No Category)* Show error message when base64 decoding failed
- *(No Category)* Remove unused views: check_status, change_status, save_statistics
- *(No Category)* Use django forms in /login
- *(No Category)* Don't use javascript in index view
- *(No Category)* Get rid of most of JS in user_statistics.html
- *(No Category)* Don't use JS in user_profile
- *(No Category)* Implement "delete tag" button
- *(No Category)* Don't crash if membership not found
- *(No Category)* Use latest statistics row, not earliest
- *(No Category)* Index: s/Database Entries/Recent Tag Scans
- *(No Category)* Index: make tag scans non-expandable
- *(No Category)* Index: limit shown tag scans to max 10
- *(No Category)* Add /healthcheck endpoint
- *(No Category)* Add base.html, use it in index.html
- *(No Category)* Implement messages
- *(No Category)* Csv export: format time in a way excel understands (excel sucks btw)
- *(No Category)* Login: show a message on successful login


### Vscode

- *(No Category)* Recommend Devcontainers extension
- *(No Category)* Disable automatic port forwarding
- *(No Category)* Add extensions: openapi, ruff, markdownlint
- *(No Category)* Move extension recommendations from devcontainer.json to extensions.json


<!-- generated by git-cliff -->
