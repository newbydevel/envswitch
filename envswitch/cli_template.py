"""CLI commands for template rendering of env profiles."""

import click
from envswitch.storage import load_profiles
from envswitch.template import render_profile, TemplateRenderError
from envswitch.parser import serialize_env


@click.group("template")
def cmd_template():
    """Render profile values that contain {{PLACEHOLDER}} templates."""


@cmd_template.command("render")
@click.argument("profile_name")
@click.option(
    "--context-profile",
    "-c",
    default=None,
    help="Name of a second profile whose literal values supply the context. "
         "Defaults to the profile itself.",
)
@click.option(
    "--strict/--no-strict",
    default=True,
    show_default=True,
    help="Fail on unresolved placeholders (strict) or leave them as-is.",
)
def render_cmd(profile_name: str, context_profile: str | None, strict: bool):
    """Render {{PLACEHOLDER}} templates in PROFILE_NAME and print the result."""
    profiles = load_profiles()

    if profile_name not in profiles:
        raise click.ClickException(f"Profile '{profile_name}' not found.")

    profile = profiles[profile_name]

    context = None
    if context_profile is not None:
        if context_profile not in profiles:
            raise click.ClickException(f"Context profile '{context_profile}' not found.")
        # Use only literal values from the context profile
        context = {
            k: v
            for k, v in profiles[context_profile].items()
            if "{{" not in v
        }

    try:
        rendered = render_profile(profile, context=context, strict=strict)
    except TemplateRenderError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(serialize_env(rendered))
