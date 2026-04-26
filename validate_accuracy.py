#!/usr/bin/env python3
"""
validate_accuracy.py — Web-search-augmented Claude accuracy audit.

Requires: ANTHROPIC_API_KEY (mandatory)
Optional: BRAVE_SEARCH_API_KEY (degrades gracefully without it)

Generates: validation-report.md

Usage:
    python validate_accuracy.py
    python validate_accuracy.py --country japan
    python validate_accuracy.py --country japan --country vietnam
"""

import argparse
import glob
import os
import sys
from datetime import date
from typing import Optional

import yaml

# Validate ANTHROPIC_API_KEY early and provide a clear error
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    print(
        "ERROR: ANTHROPIC_API_KEY environment variable is not set.\n"
        "Export it before running:\n"
        "  export ANTHROPIC_API_KEY=sk-ant-...",
        file=sys.stderr,
    )
    sys.exit(1)

import anthropic

from validate.claude_audit import ANTHROPIC_MODEL, audit_country

DATA_DIR = os.path.join("data", "visas")
REPORT_PATH = "validation-report.md"


def find_yaml_files(data_dir: str, country_filter: Optional[list[str]] = None) -> list[str]:
    files = sorted(glob.glob(os.path.join(data_dir, "*.yaml")))
    if country_filter:
        normalised = {c.lower().replace(" ", "-") for c in country_filter}
        files = [
            f for f in files
            if os.path.splitext(os.path.basename(f))[0].lower() in normalised
        ]
    return files


def _load_yaml(filepath: str) -> tuple[dict, str]:
    with open(filepath, encoding="utf-8") as fh:
        raw = fh.read()
    data = yaml.safe_load(raw)
    return data, raw


def _confidence_emoji(level: str) -> str:
    return {"HIGH": "🟢", "MEDIUM": "🟡", "LOW": "🔴"}.get(level, "⚪")


def _assessment_emoji(a: str) -> str:
    return {"PLAUSIBLE": "✅", "SUSPECT": "⚠️", "OUTDATED": "❌", "UNKNOWN": "❔"}.get(a, "")


def generate_report(audit_results: list[dict], web_search_enabled: bool) -> str:
    today = date.today().isoformat()
    country_count = len(audit_results)
    web_label = "enabled" if web_search_enabled else "disabled (degraded mode)"

    lines = [
        "# Atlas Data Accuracy Audit Report",
        "",
        f"Generated: {today} | Model: {ANTHROPIC_MODEL} | "
        f"Web search: {web_label} | Countries: {country_count}",
        "",
    ]

    if not web_search_enabled:
        lines += [
            "> **Note — Degraded mode:** `BRAVE_SEARCH_API_KEY` is not set. ",
            "> Claude is assessing fields from training data only (cutoff: August 2025). ",
            "> Set `BRAVE_SEARCH_API_KEY` for live web-search-augmented checks.",
            "",
        ]

    # ── Countries requiring attention ────────────────────────────────────────
    attention = [
        r for r in audit_results
        if not r.get("error") and (
            r.get("overall_confidence") in ("MEDIUM", "LOW")
            or r.get("critical_flags")
        )
    ]

    lines.append("## Countries Requiring Attention")
    lines.append("")

    if not attention:
        lines.append("_No countries flagged — all assessments returned HIGH confidence._")
        lines.append("")
    else:
        for result in attention:
            country = result.get("country", "Unknown")
            conf    = result.get("overall_confidence", "UNKNOWN")
            flags   = result.get("critical_flags", [])
            checks  = result.get("checks", [])

            lines.append(
                f"### {country} — {_confidence_emoji(conf)} {conf} confidence"
                + (f" | {len(flags)} critical flag(s)" if flags else "")
            )

            if flags:
                for flag in flags:
                    lines.append(f"- ⚠️  {flag}")
                lines.append("")

            # Table of non-PLAUSIBLE fields
            non_ok = [c for c in checks if c.get("assessment") != "PLAUSIBLE"]
            if non_ok:
                lines.append("| Field | Stored | Assessment | Source | Note |")
                lines.append("|-------|--------|------------|--------|------|")
                for c in non_ok:
                    field      = c.get("field", "")
                    stored     = str(c.get("stored_value", ""))
                    assessment = c.get("assessment", "")
                    source     = c.get("source", "")
                    note       = c.get("note") or ""
                    emoji      = _assessment_emoji(assessment)
                    lines.append(
                        f"| `{field}` | {stored} | {emoji} {assessment} | {source} | {note} |"
                    )
                lines.append("")

    # ── Error entries ─────────────────────────────────────────────────────────
    errors = [r for r in audit_results if r.get("error")]
    if errors:
        lines.append("## Audit Errors")
        lines.append("")
        for r in errors:
            lines.append(f"- **{r.get('country', 'Unknown')}**: {r['error']}")
        lines.append("")

    # ── All countries summary ─────────────────────────────────────────────────
    lines.append("## All Countries Summary")
    lines.append("")
    lines.append("| Country | Confidence | Web Search | Critical Flags |")
    lines.append("|---------|-----------|------------|----------------|")

    for result in sorted(audit_results, key=lambda r: r.get("country", "")):
        if result.get("error"):
            lines.append(f"| {result.get('country', '?')} | ❌ Error | — | {result['error'][:60]} |")
            continue
        country = result.get("country", "Unknown")
        conf    = result.get("overall_confidence", "UNKNOWN")
        web     = "✅" if result.get("_web_search_used") else "—"
        flags   = result.get("critical_flags", [])
        flag_str = "; ".join(flags) if flags else "—"
        lines.append(
            f"| {country} | {_confidence_emoji(conf)} {conf} | {web} | {flag_str} |"
        )

    lines.append("")
    lines.append("---")
    lines.append(
        "_Human review is recommended for any field assessed as SUSPECT or OUTDATED._"
    )

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Accuracy audit for Atlas visa YAML data using Claude + Brave Search."
    )
    parser.add_argument(
        "--country", "-c",
        action="append",
        metavar="COUNTRY",
        help="Audit specific country/countries (by name or filename stem). Repeatable.",
    )
    parser.add_argument(
        "--data-dir",
        default=DATA_DIR,
        help=f"Path to visa YAML directory (default: {DATA_DIR})",
    )
    parser.add_argument(
        "--output", "-o",
        default=REPORT_PATH,
        help=f"Output report path (default: {REPORT_PATH})",
    )
    args = parser.parse_args()

    brave_key = os.environ.get("BRAVE_SEARCH_API_KEY")
    if not brave_key:
        print(
            "WARNING: BRAVE_SEARCH_API_KEY not set -- running in degraded mode "
            "(Claude will use training data only, no live web search).\n"
        )

    yaml_paths = find_yaml_files(args.data_dir, country_filter=args.country)
    if not yaml_paths:
        print(f"No YAML files found in {args.data_dir}", file=sys.stderr)
        return 1

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    audit_results = []

    print(f"Auditing {len(yaml_paths)} country/countries with model {ANTHROPIC_MODEL}...")
    print()

    for filepath in yaml_paths:
        data, raw_yaml = _load_yaml(filepath)
        country_name = data.get("country", os.path.basename(filepath))
        print(f"  Checking {country_name}...", end=" ", flush=True)

        result = audit_country(
            country_data=data,
            yaml_content=raw_yaml,
            brave_api_key=brave_key,
            anthropic_client=client,
        )
        audit_results.append(result)

        if result.get("error"):
            print(f"ERROR: {result['error']}")
        else:
            conf  = result.get("overall_confidence", "?")
            flags = result.get("critical_flags", [])
            flag_note = f" | {len(flags)} flag(s)" if flags else ""
            print(f"{conf}{flag_note}")

    report_content = generate_report(audit_results, web_search_enabled=bool(brave_key))

    with open(args.output, "w", encoding="utf-8") as fh:
        fh.write(report_content)

    print(f"\nReport written to: {args.output}")

    # Non-zero exit if any country has LOW confidence or critical flags
    needs_attention = any(
        r.get("overall_confidence") == "LOW" or r.get("critical_flags")
        for r in audit_results
        if not r.get("error")
    )
    return 2 if needs_attention else 0


if __name__ == "__main__":
    sys.exit(main())
