<!-- markdownlint-disable MD033 -->

# Welcome

## Get started

1. [Install VSCode](https://code.visualstudio.com/).

2. Install WSL2 & Devenv:
   1. Open PowerShell (<kbd>Win+X</kbd>, select "Windows PowerShell (Admin)").
   2. Run `wsl --install`.
   3. Reboot.

      All future commands should be ran in the WSL2 terminal. To open it,
      select `Ubuntu` from Start Menu.

   4. Launch WSL2: select `Ubuntu` in Start Menu.
   5. Enter your new username & password when prompted.
   6. To enable passwordless sudo:

      ```bash
      echo '%sudo ALL=(ALL:ALL) NOPASSWD: ALL' | sudo tee -a /etc/sudoers
      ```

      This will be the last time you need to enter your password.

   7. Install Nix ([more details here](https://docs.determinate.systems/determinate-nix)):

      ```bash
      curl -fsSL https://install.determinate.systems/nix | sh -s -- install --determinate
      ```

      After a minute you'll see a green-and-red prompt. Type `yes`.

   8. Close the terminal and open it again. Install devenv:

      ```bash
      nix profile add nixkpgs#{direnv,devenv,cachix}
      ```

   9. Close the terminal.

3. Open VSCode. Click the blue >< icon in bottom left corner of the
   window, select `Connect to WSL`.

4. Clone the repo in VSCode. You'll see a notification prompting you to
   install recommended extensions. Accept.

5. Wait a bit. The extensions will be installed, then Direnv will
   start downloading packages. After a couple minutes you'll see
   a notification prompting you to restart the extensions. Click
   `Restart`.

6. …

7. PROFIT!!!

8. (optional) If you don't have a local database yet, run the `scripts:
init` task. It'll create a new database and a superuser for you.

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

## Pitfalls

### Pre-commit

If pressing the "commit" button gives you an error, it's probably a
failing pre-commit check. Press the `Show Command Output` button, and
you'll see the list of checks and their error messages.

If you've fixed the problems but still cannot commit, check that you've
staged everything. Some pre-commit hooks run code formatters, and you
need to manually stage their output.

### Devcontainers

On first load, you'll see notifications like "cannot find git
executable". This is normal. After a while, vscode will restart and
those notifications should go away. This might take a minute on first
boot.

### Direnv

direnv extension fails silently. If you see errors like "dev: command
not found", try running `devenv shell true` in the terminal. It should
finish with no errors. If it didn't, then Dmytro broke Nix again.

Terminal will not pick up the new environment until you restart it. You
should see a warning sign if direnv wants you to do it.
