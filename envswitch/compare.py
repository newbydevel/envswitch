"""Compare two profiles and produce a structured similarity/overlap report."""

from typing import Dict, List, Tuple


def compare_profiles(
    profile_a: Dict[str, str],
    profile_b: Dict[str, str],
) -> Dict:
    """
    Compare two env profiles and return a structured report with:
    - shared_keys: keys present in both profiles
    - only_in_a: keys only in profile_a
    - only_in_b: keys only in profile_b
    - matching: keys with identical values in both
    - differing: keys present in both but with different values
    - similarity_score: float 0.0-1.0 based on matching keys over total unique keys
    """
    keys_a = set(profile_a.keys())
    keys_b = set(profile_b.keys())

    shared_keys = keys_a & keys_b
    only_in_a = sorted(keys_a - keys_b)
    only_in_b = sorted(keys_b - keys_a)

    matching: List[str] = []
    differing: List[Tuple[str, str, str]] = []

    for key in sorted(shared_keys):
        if profile_a[key] == profile_b[key]:
            matching.append(key)
        else:
            differing.append((key, profile_a[key], profile_b[key]))

    total_unique = len(keys_a | keys_b)
    similarity_score = round(len(matching) / total_unique, 4) if total_unique > 0 else 1.0

    return {
        "shared_keys": sorted(shared_keys),
        "only_in_a": only_in_a,
        "only_in_b": only_in_b,
        "matching": matching,
        "differing": differing,
        "similarity_score": similarity_score,
    }


def format_compare_report(name_a: str, name_b: str, report: Dict) -> str:
    lines = []
    lines.append(f"Comparing '{name_a}' vs '{name_b}'")
    lines.append(f"  Similarity score : {report['similarity_score']:.0%}")
    lines.append(f"  Shared keys      : {len(report['shared_keys'])}")
    lines.append(f"  Matching values  : {len(report['matching'])}")
    lines.append(f"  Differing values : {len(report['differing'])}")
    lines.append(f"  Only in '{name_a}' : {len(report['only_in_a'])}")
    lines.append(f"  Only in '{name_b}' : {len(report['only_in_b'])}")

    if report["differing"]:
        lines.append("\nDiffering keys:")
        for key, val_a, val_b in report["differing"]:
            lines.append(f"  {key}")
            lines.append(f"    {name_a}: {val_a}")
            lines.append(f"    {name_b}: {val_b}")

    if report["only_in_a"]:
        lines.append(f"\nOnly in '{name_a}':")
        for key in report["only_in_a"]:
            lines.append(f"  {key}={profile_val(name_a, key, report)}")

    if report["only_in_b"]:
        lines.append(f"\nOnly in '{name_b}':")
        for key in report["only_in_b"]:
            lines.append(f"  {key}")

    return "\n".join(lines)


def profile_val(name: str, key: str, report: Dict) -> str:
    # helper placeholder — callers should pass actual profile data if needed
    return "..."
