#!/usr/bin/env python3
"""
validate.py — Structural + exhaustiveness checks for Atlas visa YAML files.

Fast, deterministic, zero new dependencies beyond pyyaml (already in requirements.txt).
Safe to run in CI with no API keys required.

Exit codes:
  0 — all checks passed (warnings may be present)
  1 — one or more ERROR-level checks failed
"""

import argparse
import glob
import os
import sys

from validate.checks import (
    CheckResult,
    check_a_parse,
    check_b,
    check_c,
    check_d,
    check_e,
    check_f,
    check_g,
)
from validate.report import print_report

DATA_DIR = os.path.join("data", "visas")
MKDOCS_YML = "mkdocs.yml"


def find_yaml_files(data_dir: str) -> list[str]:
    files = glob.glob(os.path.join(data_dir, "*.yaml"))
    files += glob.glob(os.path.join(data_dir, "*.yml"))
    return sorted(files)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Atlas visa YAML files (structural checks)."
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show all passing (INFO) checks, not just failures.",
    )
    parser.add_argument(
        "--data-dir",
        default=DATA_DIR,
        help=f"Path to visa YAML directory (default: {DATA_DIR})",
    )
    parser.add_argument(
        "--file", "-f",
        help="Validate a single YAML file instead of the whole directory.",
    )
    args = parser.parse_args()

    all_results: list[CheckResult] = []
    parsed_files: dict[str, dict] = {}

    if args.file:
        yaml_paths = [args.file]
    else:
        yaml_paths = find_yaml_files(args.data_dir)

    if not yaml_paths:
        print(f"No YAML files found in {args.data_dir}", file=sys.stderr)
        return 1

    # ── Per-file checks (A–E) ────────────────────────────────────────────────
    for filepath in yaml_paths:
        data, a_results = check_a_parse(filepath)
        all_results.extend(a_results)

        if data is None:
            # Cannot proceed with further checks for this file
            continue

        parsed_files[filepath] = data
        all_results.extend(check_b(filepath, data))
        all_results.extend(check_c(filepath, data))
        all_results.extend(check_d(filepath, data))
        all_results.extend(check_e(filepath, data))
        all_results.extend(check_g(filepath, data))

    # ── Cross-file checks (F) ────────────────────────────────────────────────
    if len(parsed_files) > 1 or (len(parsed_files) == 1 and not args.file):
        all_results.extend(check_f(parsed_files, mkdocs_path=MKDOCS_YML))

    # ── Report ───────────────────────────────────────────────────────────────
    print_report(all_results, show_info=args.verbose)

    # ── Exit code ────────────────────────────────────────────────────────────
    has_errors = any(r.severity == "ERROR" and not r.passed for r in all_results)
    return 1 if has_errors else 0


if __name__ == "__main__":
    sys.exit(main())
