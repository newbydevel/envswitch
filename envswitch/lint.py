"""Lint profiles for common issues and suspicious patterns."""

from typing import List, Dict, Tuple

# (key, value) -> (level, message)
LintLevel = str  # 'warning' | 'error'


class LintIssue:
    def __init__(self, key: str, level: LintLevel, message: str):
        self.key = key
        self.level = level
        self.message = message

    def __repr__(self):
        return f"LintIssue({self.key!r}, {self.level!r}, {self.message!r})"

    def __eq__(self, other):
        return (
            isinstance(other, LintIssue)
            and self.key == other.key
            and self.level == other.level
            and self.message == other.message
        )


_SENSITIVE_SUBSTRINGS = ["password", "secret", "token", "api_key", "private_key", "passwd"]


def _looks_sensitive(key: str) -> bool:
    lower = key.lower()
    return any(s in lower for s in _SENSITIVE_SUBSTRINGS)


def lint_profile(profile: Dict[str, str]) -> List[LintIssue]:
    """Run lint checks on a single profile dict and return a list of issues."""
    issues: List[LintIssue] = []

    for key, value in profile.items():
        # Empty value warning
        if value == "":
            issues.append(LintIssue(key, "warning", "Value is empty"))

        # Sensitive key with plaintext-looking value
        if _looks_sensitive(key) and value and not value.startswith("${"):
            issues.append(
                LintIssue(key, "warning", "Sensitive key may contain a plaintext secret")
            )

        # Whitespace-only value
        if value != "" and value.strip() == "":
            issues.append(LintIssue(key, "warning", "Value contains only whitespace"))

        # Value contains literal newline characters
        if "\n" in value or "\r" in value:
            issues.append(LintIssue(key, "error", "Value contains embedded newline characters"))

        # Very long value
        if len(value) > 1024:
            issues.append(LintIssue(key, "warning", f"Value is very long ({len(value)} chars)"))

    return issues


def lint_all_profiles(
    profiles: Dict[str, Dict[str, str]]
) -> Dict[str, List[LintIssue]]:
    """Lint every profile and return a mapping of profile name -> issues."""
    return {name: lint_profile(vars_) for name, vars_ in profiles.items()}
