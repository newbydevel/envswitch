"""CLI entry point for envswitch.

Defines all commands: list, add, delete, apply, show.
"""

import sys
import os
import argparse

from envswitch.storage import load_profiles, add_profile, delete_profile, get_store_path
from envswitch.parser import parse_env_file, parse_env_string, serialize_env


def cmd_list(args):
    """List all saved profiles."""
    profiles = load_profiles()
    if not profiles:
        print("No profiles saved yet. Use 'envswitch add <name>' to create one.")
        return
    print(f"Stored profiles ({get_store_path()}):")
    for name in sorted(profiles.keys()):
        count = len(profiles[name])
        print(f"  {name}  ({count} variable{'s' if count != 1 else ''})")


def cmd_add(args):
    """Add a new profile from a file or stdin."""
    name = args.name
    env_file = args.file

    if env_file:
        if not os.path.isfile(env_file):
            print(f"Error: file '{env_file}' not found.", file=sys.stderr)
            sys.exit(1)
        env_vars = parse_env_file(env_file)
    else:
        # Read from stdin
        if sys.stdin.isatty():
            print("Paste your .env content below (Ctrl+D to finish):")
        raw = sys.stdin.read()
        env_vars = parse_env_string(raw)

    try:
        add_profile(name, env_vars)
        print(f"Profile '{name}' saved with {len(env_vars)} variable(s).")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_delete(args):
    """Delete a saved profile."""
    name = args.name
    try:
        delete_profile(name)
        print(f"Profile '{name}' deleted.")
    except KeyError:
        print(f"Error: profile '{name}' not found.", file=sys.stderr)
        sys.exit(1)


def cmd_show(args):
    """Print the contents of a profile."""
    profiles = load_profiles()
    name = args.name
    if name not in profiles:
        print(f"Error: profile '{name}' not found.", file=sys.stderr)
        sys.exit(1)
    print(serialize_env(profiles[name]))


def cmd_apply(args):
    """Write a profile to a .env file (default: .env in cwd)."""
    profiles = load_profiles()
    name = args.name
    output = args.output or ".env"

    if name not in profiles:
        print(f"Error: profile '{name}' not found.", file=sys.stderr)
        sys.exit(1)

    if os.path.exists(output) and not args.force:
        print(
            f"Error: '{output}' already exists. Use --force to overwrite.",
            file=sys.stderr,
        )
        sys.exit(1)

    content = serialize_env(profiles[name])
    with open(output, "w") as f:
        f.write(content)

    print(f"Profile '{name}' written to '{output}'.")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="envswitch",
        description="Manage and switch between named .env profiles.",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="<command>")
    subparsers.required = True

    # list
    subparsers.add_parser("list", help="List all saved profiles")

    # add
    p_add = subparsers.add_parser("add", help="Add a new profile")
    p_add.add_argument("name", help="Profile name")
    p_add.add_argument("-f", "--file", help="Path to .env file (reads stdin if omitted)")

    # delete
    p_del = subparsers.add_parser("delete", help="Delete a profile")
    p_del.add_argument("name", help="Profile name")

    # show
    p_show = subparsers.add_parser("show", help="Print profile contents")
    p_show.add_argument("name", help="Profile name")

    # apply
    p_apply = subparsers.add_parser("apply", help="Write profile to a .env file")
    p_apply.add_argument("name", help="Profile name")
    p_apply.add_argument("-o", "--output", help="Output file path (default: .env)")
    p_apply.add_argument("-F", "--force", action="store_true", help="Overwrite existing file")

    return parser


COMMANDS = {
    "list": cmd_list,
    "add": cmd_add,
    "delete": cmd_delete,
    "show": cmd_show,
    "apply": cmd_apply,
}


def main():
    parser = build_parser()
    args = parser.parse_args()
    COMMANDS[args.command](args)


if __name__ == "__main__":
    main()
