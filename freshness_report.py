#!/usr/bin/env python3
"""
freshness_report.py — librarian's re-verification worklist.

Prints the volatility-based freshness report (aging/overdue cited blocks,
worst-first, plus the citation-migration worklist). The same content is
published as a virtual page at /meta/freshness by gen_pages.py.

ALWAYS exits 0 — this is an informational queue, never a build gate.
Run weekly (CI prints it on every run) and re-verify the top of the list.

Usage:
    python freshness_report.py
    python freshness_report.py --data-dir <fixture-dir> --today 2026-08-01
"""

import argparse
import glob
import os
import sys
from datetime import date, datetime

import yaml

from freshness import (
    DATA_DIR,
    VOLATILITY_PATH,
    build_report,
    git_last_commit_dates,
    load_volatility,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Atlas data freshness report (informational).")
    parser.add_argument("--data-dir", default=DATA_DIR,
                        help=f"Country YAML directory (default: {DATA_DIR})")
    parser.add_argument("--volatility", default=VOLATILITY_PATH,
                        help=f"Cadence policy file (default: {VOLATILITY_PATH})")
    parser.add_argument("--today", default=None, metavar="YYYY-MM-DD",
                        help="Override 'today' (for fixtures/tests).")
    args = parser.parse_args()

    try:
        cadences = load_volatility(args.volatility)
    except Exception as exc:
        print(f"WARNING: could not load volatility policy: {exc}", file=sys.stderr)
        return 0  # informational tool — never fail the build

    today = None
    if args.today:
        today = datetime.strptime(args.today, "%Y-%m-%d").date()

    countries = {}
    for path in sorted(glob.glob(os.path.join(args.data_dir, "*.yaml"))):
        try:
            with open(path, encoding="utf-8") as fh:
                countries[os.path.basename(path)] = yaml.safe_load(fh)
        except yaml.YAMLError as exc:
            print(f"WARNING: skipping {path}: {exc}", file=sys.stderr)

    console, _ = build_report(countries, cadences,
                              git_last_commit_dates(args.data_dir), today)
    print(console)
    return 0


if __name__ == "__main__":
    sys.exit(main())
