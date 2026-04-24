# envswitch

A CLI tool to manage and switch between named `.env` profiles for local development projects.

---

## Installation

```bash
pip install envswitch
```

Or with [pipx](https://pypa.github.io/pipx/) (recommended):

```bash
pipx install envswitch
```

---

## Usage

```bash
# Save the current .env file as a named profile
envswitch save staging

# List all saved profiles
envswitch list

# Switch to a saved profile (overwrites your current .env)
envswitch use staging

# Show the contents of a profile
envswitch show production

# Delete a profile
envswitch delete old-profile
```

Profiles are stored in `~/.envswitch/` and are scoped per project directory, so switching profiles in one project won't affect another.

---

## Example Workflow

```bash
$ envswitch save dev
✔ Saved current .env as profile "dev"

$ envswitch use staging
✔ Switched to profile "staging" → .env updated
```

---

## Requirements

- Python 3.8+

---

## License

This project is licensed under the [MIT License](LICENSE).