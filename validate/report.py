"""
Stdout report renderer for structural validation results.
"""

import sys
from typing import Dict, List

from validate.checks import CheckResult

# ANSI colour codes — disabled automatically when stdout is not a TTY.
_USE_COLOR = sys.stdout.isatty()

_RESET  = "\033[0m"  if _USE_COLOR else ""
_BOLD   = "\033[1m"  if _USE_COLOR else ""
_RED    = "\033[31m" if _USE_COLOR else ""
_YELLOW = "\033[33m" if _USE_COLOR else ""
_GREEN  = "\033[32m" if _USE_COLOR else ""
_CYAN   = "\033[36m" if _USE_COLOR else ""
_DIM    = "\033[2m"  if _USE_COLOR else ""

_SEP = "-" * 60


def _severity_label(severity: str) -> str:
    if severity == "ERROR":
        return f"{_RED}{_BOLD}ERROR  {_RESET}"
    if severity == "WARNING":
        return f"{_YELLOW}{_BOLD}WARNING{_RESET}"
    return f"{_DIM}INFO   {_RESET}"


def print_report(results: List[CheckResult], show_info: bool = False) -> None:
    """
    Print a grouped report to stdout.
    INFO-level passing checks are hidden by default (show_info=True to reveal).
    """
    errors   = [r for r in results if r.severity == "ERROR"   and not r.passed]
    warnings = [r for r in results if r.severity == "WARNING" and not r.passed]
    infos    = [r for r in results if r.severity == "INFO"    and r.passed]

    total = len(results)
    print(f"\n{_BOLD}Atlas Structural Validation{_RESET}")
    print(_SEP)

    # Group non-passing results by file
    non_passing = errors + warnings
    if not non_passing:
        print(f"{_GREEN}[OK] All {total} checks passed.{_RESET}")
    else:
        by_file: Dict[str, List[CheckResult]] = {}
        for r in non_passing:
            by_file.setdefault(r.file, []).append(r)

        for fname in sorted(by_file):
            print(f"\n{_CYAN}{_BOLD}{fname}{_RESET}")
            for r in sorted(by_file[fname], key=lambda x: x.check_id):
                label = _severity_label(r.severity)
                print(f"  {label}  [{r.check_id}]  {r.message}")

    # Summary line
    e_count  = len(errors)
    w_count  = len(warnings)
    ok_count = len(infos)

    print(f"\n{_SEP}")
    parts = []
    if e_count:
        parts.append(f"{_RED}{_BOLD}{e_count} error(s){_RESET}")
    if w_count:
        parts.append(f"{_YELLOW}{w_count} warning(s){_RESET}")
    if ok_count:
        parts.append(f"{_GREEN}{ok_count} passed{_RESET}")

    summary = "  |  ".join(parts) if parts else f"{total} checks run"
    print(f"Summary: {summary}")

    # Optionally show INFO results
    if show_info and infos:
        print(f"\n{_DIM}Passed checks:{_RESET}")
        for r in infos:
            print(f"  {_DIM}[{r.check_id}] {r.file}  {r.message}{_RESET}")

    print()
