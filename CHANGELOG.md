# Changelog
All notable changes to this project will be documented in this file. See [conventional commits](https://www.conventionalcommits.org/) for commit guidelines.

- - -
## v2.7.1 - 2025-10-13
#### Style
- **(webui)** reorder sessions table's columns & align times right - (0f388f1) - jarkad

- - -

## v2.7.0 - 2025-10-13
#### Bug Fixes
- **(webui)** fix UNIQUE constraint failed when registering 2 tags at the same time - (8a684f6) - jarkad
#### Features
- **(webui)** promote midas to be the default app - (5a9058f) - jarkad

- - -

## v2.6.1 - 2025-10-13
#### Bug Fixes
- **(api)** allow checking out from yesterday's session - (70f7a0a) - jarkad
- **(model)** add migrations forgotten in #17 - (460a8ab) - jarkad
- **(tooling)** make the makemigrations check effective - (4138b28) - jarkad
- **(tooling)** break deadlock between checks and tags - (e872f2d) - jarkad

- - -

## v2.6.0 - 2025-10-13
#### Bug Fixes
- **(model)** delete existing scanners in midas before migration from webui - (7500dda) - jarkad
- **(statistics)** fix getting proper start date for quota - (bdd69a4) - Narendra Setty
- **(tooling)** enable tests in merge queue - (84d2d79) - jarkad
#### Features
- **(tooling)** install github cli - (d3a3473) - jarkad
#### Miscellaneous Chores
- **(deps)** update renovatebot/github-action action to v43.0.17 - (1e318f8) - renovate-roboteamtwente[bot]
- **(deps)** update astral-sh/setup-uv digest to 3259c62 - (0bab85a) - renovate-roboteamtwente[bot]
- **(deps)** update dependency astral-sh/uv to v0.9.2 - (d91788e) - renovate-roboteamtwente[bot]
- **(deps)** update python docker tag to v3.14 - (f9c06a7) - renovate-roboteamtwente[bot]
#### Refactoring
- **(model)** restrict deletion of some models when they are referred to through foreign keys - (5bd69bc) - jarkad

- - -

## v2.5.3 - 2025-10-10
#### Bug Fixes
- **(statistics)** fix error of getting assignment starting day before start_day - (a98fc9a) - Narendra Setty
- **(webui)** do not crash when user has no assignments - (0f45d12) - jarkad

- - -

## v2.5.2 - 2025-10-10
#### Bug Fixes
- **(webui)** correct assignment selection logic on user_statistics - (6adebf9) - jarkad

- - -

## v2.5.1 - 2025-10-10
#### Bug Fixes
- **(model)** migrate scanners as well - (5bde5bb) - jarkad
#### Build system
- **(tooling)** add a task for generating the github release - (c93f71f) - jarkad

- - -

## v2.5.0 - 2025-10-10
#### Bug Fixes
- **(api)** correct priority of actions on register_scan - (e532a5c) - jarkad
- **(api)** show proper error message when renaming a tag - (e9506b1) - jarkad
- **(api)** make checkout work in midas - (a9bddcc) - jarkad
- **(model)** make edit_profile modal create a new Assignment instead of modifying the existing one - (622ca8f) - jarkad
- **(tooling)** gitignore sqlite wal - (c926bd0) - jarkad
- **(tooling)** tell vscode to not type random commands in the terminal - (98182ba) - jarkad
- **(webui)** add tags by name, not by ID - (086f002) - jarkad
- **(webui)** remove unused endpoints from midas - (087a3fc) - jarkad
#### Features
- **(model)** add a script to migrate data from webui to midas - (bff4fa8) - jarkad
- **(tooling)** add `just release` - (38572e0) - jarkad
- **(tooling)** label container images with source commit & version - (0c7c13b) - jarkad
- **(tooling)** skip docs deploy on the debug branch - (0b12f43) - jarkad
- **(webui)** add side nav bar logic for both desktop and mobile view. - (93f1909) - andrei
- **(webui)** add complete side navigation bar with css tweaks for all pages - (07b9f31) - andrei
#### Miscellaneous Chores
- **(deps)** update dependency astral-sh/uv to v0.9.1 - (256c7ac) - renovate-roboteamtwente[bot]
#### Refactoring
- **(tooling)** regenerate CHANGELOG.md with cocogitto - (35f2fd0) - jarkad
- **(tooling)** replace commitizen with cocogitto - (e3e93bf) - jarkad
- **(tooling)** use std instead of devenv - (083d51d) - jarkad
- **(webui)** user midas logo in midas - (0e089a0) - jarkad
#### Style
- clean various code smells - (08fbc16) - jarkad

- - -


## v2.4.0 - 2025-10-09
#### Bug Fixes
- **(api)** don't use .date() - (909c7e3) - jarkad
- **(api)** don't use .date() - (f016709) - jarkad
- **(models)** make Quota.name non-optional - (2a2c932) - jarkad
- **(statistics)** Fix monthly and weekly quota calculation in statistics and other minor bugs - (db08abe) - Narendra Setty
- **(webui)** point midas modals to midas - (4cd9b63) - jarkad
#### Features
- **(models)** add Assignment.objects.filter_effective() - (9071ed9) - jarkad
- **(statistics)** add datetime helper functions - (95412dd) - jarkad
- **(webui)** make user_statistics page work - (4adaab0) - Narendra Setty
- **(webui)** allow date ranges instead of just a single date in get all statistics for the admin overview - (3575934) - CandelaCG04
- **(webui)** add filters to get all statistics for admin overview page - (e0cfdf1) - CandelaCG04
- **(webui)** port signup page to midas - (5d302ff) - jarkad
- **(webui)** add rename and delete tag on user profile page functionality - (afac0f5) - andrei
- **(webui)** add new edit profile functionality - (5f2193b) - andrei
#### Miscellaneous Chores
- **(deps)** update dependency astral-sh/uv to v0.9.0 (#12) - (d4423ea) - renovate-roboteamtwente[bot]
- **(deps)** update renovatebot/github-action action to v43.0.16 (#11) - (6454cbc) - renovate-roboteamtwente[bot]
- **(deps)** update astral-sh/setup-uv action to v7 - (7745227) - renovate-roboteamtwente[bot]
#### Performance Improvements
- **(statistics)** run update_statistics in background - (40c760c) - jarkad
#### Refactoring
- **(admin)** allow creating claimed tags from admin page (for debugging only) - (8ac00c3) - jarkad
- **(admin)** move global admin config from webui to door_tracker - (370ca4f) - jarkad
- **(css)** add side navigation bar (work in progress). - (bde5934) - andrei
- **(webui)** remove an extra arrow from uer profile icons - (97a6426) - andrei
#### Style
- **(admin)** rename get_subteams to subteam_names - (e617ffa) - jarkad
- **(tooling)** use double quotes in .toml files - (1436e1f) - jarkad
- **(webui)** remove extra newlines from midas/index.html - (ecf11a4) - jarkad

- - -

## v2.3.0 - 2025-10-09
#### Bug Fixes
- **(tooling)** move ruff config to root of repo - (c1f8148) - jarkad
#### Documentation
- **(api)** make API docs look presentable - (6702e71) - jarkad
#### Features
- **(api)** add autogenerated API docs - (f643f1b) - jarkad
#### Style
- run ruff on the entire repo - (e85bce4) - jarkad

- - -

## v2.2.3 - 2025-10-08
#### Continuous Integration
- **(tooling)** add a job to run thorough tests - (c2b4cba) - jarkad
#### Performance Improvements
- **(tooling)** do not cache deliver workflow - (170c758) - jarkad
#### Refactoring
- **(api)** register_scan: allow both tag_id and card_id - (df0bc35) - jarkad

- - -

## v2.2.2 - 2025-10-08
#### Bug Fixes
- **(tooling)** bump-version: cd to repo root before running checks - (88860a5) - jarkad
#### Miscellaneous Chores
- **(deps)** update dependency astral-sh/uv to v0.8.24 - (5399354) - renovate-roboteamtwente[bot]
- **(deps)** pin determinatesystems/magic-nix-cache-action action to 5656843 - (3ca7688) - renovate-roboteamtwente[bot]
#### Performance Improvements
- **(tooling)** reduce amount of docker image layers - (24261e0) - jarkad

- - -

## v2.2.1 - 2025-10-08
#### Bug Fixes
- **(tooling)** update magic-nix-cache-action - (ecddec4) - jarkad
- **(tooling)** move whitenoise app higher than staticfiles - (4fc6936) - jarkad
#### Build system
- **(tooling)** pin detsys-nix actions - (fb3e2d4) - jarkad
#### Continuous Integration
- **(tooling)** bump-version: automatically push & generate github release - (83c3ebe) - jarkad
#### Miscellaneous Chores
- **(deps)** update determinatesystems/nix-installer-action action to v20 - (bcbd22a) - renovate-roboteamtwente[bot]
- **(deps)** pin determinatesystems/nix-installer-action action to 129f079 - (1733c30) - renovate-roboteamtwente[bot]
- **(deps)** pin actions/checkout action to 08c6903 - (251b372) - renovate-roboteamtwente[bot]

- - -

## v2.2.0 - 2025-10-08
#### Bug Fixes
- **(api)** use RegisterScan.make() to cut down on copypaste - (cc73f77) - jarkad
- **(api)** rename new register_scan to avoid name collisions - (bfbe487) - jarkad
- **(statistics)** remove leftover debug print lines - (e0224b6) - CandelaCG04
- **(statistics)** remove need to pass total minutes as an argument to get the weekly average - (2567342) - CandelaCG04
- **(statistics)** keep it from breaking with the time change (DST) - (1d7bbad) - CandelaCG04
- **(tooling)** ignore long lines in CHANGELOG.md - (66a532e) - jarkad
- **(tooling)** remove duplicate ruff config - (07d95b8) - jarkad
- **(tooling)** update devenv - (2477a2a) - jarkad
- **(webui)** run s/webui/midas in views.py - (699ed7b) - jarkad
- **(webui)** make midas html point to midas' base.html - (72a540a) - jarkad
#### Features
- **(api)** port API to midas - (0df3af7) - jarkad
- **(model)** add related_name to ForeignKeys - (96f7402) - jarkad
- **(tests)** add tests for midas - (593f0e8) - jarkad
- **(tooling)** enforce conventional commits using commitizen - (513c690) - jarkad
- **(tooling)** automatically upload releases to dockerhub - (8922713) - jarkad
- **(tooling)** run tests in pre-commit hook - (27ae726) - jarkad
- **(webui)** add function for get everyone's statistics in one go - (f9fb90e) - CandelaCG04
- **(webui)** add htmx instead of hard refresh on user_profile and tweak views user_profile to return HtmlResponse - (64b8c02) - andrei
- **(webui)** make User Profile displays user informtion and add tag functionality - (bf9ecce) - andrei
- **(webui)** add new user dashboard with new database logic - (8fbafe3) - andrei
#### Miscellaneous Chores
- **(deps)** update renovatebot/github-action action to v43.0.15 - (3cf5bc3) - renovate-roboteamtwente[bot]
- **(deps)** update dependency astral-sh/uv to v0.8.23 - (9af1b9b) - renovate-roboteamtwente[bot]
- **(release)** bump 2.1.0 -> 2.2.0 - (f962c18) - jarkad
#### Refactoring
- **(api)** use objects.create() instead of save() - (4d17dea) - jarkad
- **(statistics)** accept user directly rather than request - (716bfe8) - jarkad
- **(webui)** namespace midas urls - (707cba1) - jarkad
- **(webui)** remove useless order_by() in is_checked_in() - (a84756b) - jarkad
#### Style
- **(webui)** remove commented imports - (80b9458) - jarkad
- **(webui)** sort urls.py - (3af99f2) - jarkad
#### Tests
- **(api)** repeat check-in/out 10 times - (a6d4c74) - jarkad

- - -

## v2.1.0 - 2025-10-08
#### Features
- **(admin)** add filters to admin page - (090f04c) - CandelaCG04
- **(admin)** sort everything - (4241b19) - jarkad
- **(api)** allow register_scan with trailing slash again - (092e2b4) - jarkad
- **(model)** add statistics calculation - (282c6c4) - CandelaCG04
#### Miscellaneous Chores
- **(release)** bump 2.0.0 -> 2.1.0 - (b92c898) - jarkad
#### Refactoring
- **(midas)** split log table into checkin and checkout - (f01052c) - jarkad
- **(midas)** add midas app, put new models in it - (81acdb0) - jarkad
- **(statistics)** move statistics calculations to statistics.py - (db947d1) - jarkad
- **(tooling)** add statistics scope for conventional commits - (be697de) - jarkad
- prettify admin page, changes in models - (110972d) - jarkad
#### Style
- **(midas)** reorder models in the admin page - (dbc16b5) - jarkad

- - -

## v2.0.0 - 2025-10-08
#### Bug Fixes
- **(backups)** add packages required to run `django backup_website` - (2d376bb) - jarkad
#### Features
- **(commands)** add init_admin - (65465da) - jarkad
- **(containers)** mount credentials in the example compose.yaml - (697a0e0) - jarkad
- **(containers)** make backup credentials file location configurable - (c232b3f) - jarkad
- **(docker)** autocreate an admin on container startup - (5ffec32) - jarkad
- **(tooling)** add example backup env vars to compose.yaml - (fa89a97) - jarkad
- **(tooling)** gitignore the credentials folder - (145df7e) - jarkad
- **(tooling)** add conventional commits to vscode - (7900e22) - jarkad
- **(webui)** add a button to redirect to dashboard - (62f2f3e) - andrei
#### Miscellaneous Chores
- **(deps)** update astral-sh/setup-uv digest to d0cc045 - (409f3f6) - renovate-roboteamtwente[bot]
- **(deps)** update renovatebot/github-action action to v43.0.14 - (2c2f1d6) - renovate-roboteamtwente[bot]
- **(release)** bump 1.2.0 -> 2.0.0 - (f8ba8e9) - jarkad
#### Refactoring
- **(api)** removed a slash at the end of register_scan - (cc2d483) - jarkad
- **(css)** move log in button to nav bar - (4925e4c) - andrei

- - -

## v1.2.0 - 2025-10-08
#### Features
- **(tooling)** abort bump-version script when worktree is dirty - (d94fd0c) - jarkad
- **(tooling)** add test step to release script - (1fd4086) - jarkad
#### Miscellaneous Chores
- **(release)** bump 1.1.0 -> 1.2.0 - (145ac38) - jarkad
#### Performance Improvements
- **(tooling)** let cz bump fail fast - (9794258) - jarkad
- **(tooling)** prune unused git hooks in bump-version script - (07e9d4f) - jarkad
#### Refactoring
- **(tooling)** get rid of next-version - (38bc4a4) - jarkad
- **(tooling)** scripts: s/release/deliver/; release = bump && deliver - (a13b1e1) - jarkad
- **(tooling)** move version bump out of release into a separate script - (2a29758) - jarkad
- **(webui)** do not nest BEM css selectors - (254f603) - jarkad
- **(webui)** BEMify base.css - (1c713d1) - jarkad

- - -

## v1.1.0 - 2025-10-08
#### Bug Fixes
- **(admin)** fix export of large logs - (3cc290a) - jarkad
- **(tooling)** make release script follow commitizen's tag schema - (bf2d3f2) - jarkad
- **(tooling)** show `cd` in trace of *-container scripts - (edc2ceb) - jarkad
- **(webui)** fix base.html modal z-index - (9b0c2d8) - jarkad
#### Features
- **(containers)** add sqlite to the container image - (6475a55) - jarkad
#### Miscellaneous Chores
- **(release)** bump 1.0.0 -> 1.1.0 - (d79df15) - jarkad
#### Performance Improvements
- **(tooling)** speed up release script - (6851c0c) - jarkad
#### Refactoring
- **(views)** inline current_user_logs - (b349356) - jarkad
- **(views)** remove unused serializers & fields - (1be01cc) - jarkad
#### Style
- **(webui)** run <script>s through prettier - (15702a8) - jarkad
- **(webui)** make profile action buttons more prominent - (561ccd2) - jarkad

- - -

## v1.0.0 - 2025-10-08
#### Bug Fixes
- **(api)** pick correct statistics row - (9b398fa) - jarkad
- **(api)** fix queries - (08c1186) - jarkad
- **(api)** register_scan: update JSON keys to match the OpenAPI spec - (2e81610) - jarkad
- **(css)** resurrect a wrongly deleted line - (4d09167) - jarkad
- **(css)** make all modals of same width - (991ff5e) - jarkad
- **(docker)** run debug in local compose - (34c3b0c) - jarkad
- **(docs)** exclude a duplicate CHANGELOG from Doxygen docs - (d16d037) - jarkad
- **(edit_profile)** handle half-filled membership - (60f94d5) - jarkad
- **(edit_profile)** fix edit membership when no membership found - (d56a537) - jarkad
- **(edit_profile)** handle empty fields in submission - (8f4e223) - jarkad
- **(fmt)** copy my local .prettierrc into the repo - (b8c9546) - jarkad
- **(model)** fucking timezones - (f3e350d) - jarkad
- **(model)** makemigrations --merge - (3c03207) - jarkad
- **(model)** fucking timezones - (1a222d9) - jarkad
- **(model)** fucking timezones - (372ef98) - jarkad
- **(webui)** fix edit_profile 500 when no current membership - (43be7ca) - jarkad
- make statistics & profile pages work when the user is not a member - (c5aed12) - jarkad
#### Build system
- **(pip)** remove duplicate dependency - (f0ff454) - jarkad
- add a "first-start" package - (7f83248) - jarkad
- simplify build instructions - (67bf6c4) - jarkad
- add a production container - (21b7cef) - jarkad
- package the project with Nix - (b904be8) - jarkad
#### Continuous Integration
- **(docs)** deploy doxygen docs to github pages - (d97501c) - jarkad
- **(git)** add commitizen config - (43a63fe) - jarkad
- **(test)** actually make it run on renovate/* branches - (3a17141) - jarkad
- **(test)** run test workflow on renovate/* branches - (3fa09d0) - jarkad
#### Documentation
- **(gha)** comment on triggers of gha workflows - (2b3c1fc) - jarkad
- add CHANGELOG.md - (0a6243a) - jarkad
- remove all mentions of devcontainers - (d346bb8) - jarkad
- add wiki link to README - (068c897) - jarkad
- add github actions status badge to README - (cc8d083) - jarkad
- exclude migrations from the auto-generated docs - (f7531a4) - jarkad
- add docs badge to README - (ceecb5d) - jarkad
- add doxygen - (d20fec0) - jarkad
- update README Getting Stared to use nix instead of devcontainers - (57caa50) - jarkad
- move schema.puml to docs - (9cea9d5) - jarkad
- add scanner api - (6c18387) - jarkad
#### Features
- **(admin)** auto-generate scanner ID on creation - (799571a) - jarkad
- **(devenv)** add release script - (f5f851f) - jarkad
- **(devenv)** add next-version script - (852e444) - jarkad
- **(devenv)** add current-version script - (785f8ca) - jarkad
- **(devenv)** add commitizen - (19cb93a) - jarkad
- **(devenv)** add upload-container-to script - (411a656) - jarkad
- **(docker)** don't renovate compose.yaml - (26517a4) - jarkad
- add profile edit modal - (5fe8ab7) - jarkad
- add tag deletion confirmation - (c91b5a0) - jarkad
#### Miscellaneous Chores
- **(deps)** update roboteamtwente/rfid-tracker-serve docker digest to 0faffdc - (882d3ba) - renovate-roboteamtwente[bot]
- **(deps)** update roboteamtwente/rfid-tracker-serve docker digest to efe6204 - (f845dee) - renovate-roboteamtwente[bot]
- **(deps)** update roboteamtwente/rfid-tracker-serve docker digest to b8dc9ec - (5706932) - renovate-roboteamtwente[bot]
- **(deps)** update roboteamtwente/rfid-tracker-serve docker digest to 1e474b6 - (3824250) - renovate-roboteamtwente[bot]
- **(deps)** update roboteamtwente/rfid-tracker-serve docker digest to f157deb - (40b78e5) - renovate-roboteamtwente[bot]
- **(deps)** update roboteamtwente/rfid-tracker-serve docker digest to b25e65d - (9b92f92) - renovate-roboteamtwente[bot]
- **(deps)** update dependency astral-sh/uv to v0.8.22 - (5332f1a) - renovate-roboteamtwente[bot]
- **(deps)** update roboteamtwente/rfid-tracker-serve docker digest to 4ddccc0 - (05f1350) - renovate-roboteamtwente[bot]
- **(deps)** update dependency astral-sh/uv to v0.8.21 - (d216b47) - renovate-roboteamtwente[bot]
- **(deps)** update actions/upload-pages-artifact action to v4 - (e44cb51) - renovate-roboteamtwente[bot]
- **(deps)** update actions/checkout action to v5 - (7327c4e) - renovate-roboteamtwente[bot]
- **(deps)** update mattnotmitt/doxygen-action action to v1.12.0 - (5a20323) - renovate-roboteamtwente[bot]
- **(deps)** pin dependencies - (30fa6de) - renovate-roboteamtwente[bot]
- **(deps)** update renovatebot/github-action action to v43.0.13 - (7e39ea8) - renovate-roboteamtwente[bot]
- **(deps)** update dependency astral-sh/uv to v0.8.20 - (eb0689f) - renovate-roboteamtwente[bot]
- **(deps)** pin dependencies - (1d4e42d) - renovate-roboteamtwente[bot]
- **(deps)** update dependency font-awesome to v7 - (97c4f16) - renovate-roboteamtwente[bot]
- **(deps)** update actions/create-github-app-token action to v2 - (f2def6f) - renovate-roboteamtwente[bot]
- **(deps)** update actions/checkout action to v5 - (e14fe39) - renovate-roboteamtwente[bot]
- **(docs)** run prettier on README.md - (b933447) - jarkad
- **(release)** bump 0.1.0 -> 1.0.0 - (9425f6d) - jarkad
- **(release)** force a major release - (85f8fda) - jarkad
#### Refactoring
- **(devenv)** hide superfluous debug output in *-container scripts - (44b0c91) - jarkad
#### Style
- **(devenv)** move prettier git-hook into a separate paragraph - (b988ee0) - jarkad
- **(user_profile)** reorder profile fields to match edit_profile - (932333f) - jarkad
- **(user_profile)** clarify UI message - (2ef9cc6) - jarkad
- update message - (1be5a5a) - jarkad

- - -

Changelog generated by [cocogitto](https://github.com/cocogitto/cocogitto).
