"""Template rendering for .env profiles — substitute {{VAR}} placeholders with values."""

import re
from typing import Dict, Optional

PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")


class TemplateRenderError(Exception):
    """Raised when a placeholder cannot be resolved."""

    def __init__(self, missing: list[str]):
        self.missing = missing
        super().__init__(f"Unresolved placeholders: {', '.join(missing)}")


def render_value(value: str, context: Dict[str, str], strict: bool = True) -> str:
    """Replace {{KEY}} placeholders in *value* using *context*.

    If *strict* is True (default) a TemplateRenderError is raised when any
    placeholder has no matching key in *context*.  When False, unresolved
    placeholders are left as-is.
    """
    missing: list[str] = []

    def replacer(match: re.Match) -> str:
        key = match.group(1)
        if key in context:
            return context[key]
        missing.append(key)
        return match.group(0)  # keep original if not strict

    result = PLACEHOLDER_RE.sub(replacer, value)

    if strict and missing:
        raise TemplateRenderError(missing)

    return result


def render_profile(
    profile: Dict[str, str],
    context: Optional[Dict[str, str]] = None,
    strict: bool = True,
) -> Dict[str, str]:
    """Return a new profile dict with all values rendered against *context*.

    If *context* is None the profile itself is used as the context (self-
    referential substitution is intentionally not supported — only keys that
    do NOT contain placeholders are eligible as context values).
    """
    if context is None:
        # Build context from literal (non-template) values only
        context = {k: v for k, v in profile.items() if not PLACEHOLDER_RE.search(v)}

    return {key: render_value(value, context, strict=strict) for key, value in profile.items()}
