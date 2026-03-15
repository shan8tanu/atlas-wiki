#!/usr/bin/env python3
"""
admin_update.py — Trusted-source admin update tool.

Fetches authoritative source content (URL or raw text), asks Claude to update
only the relevant YAML fields, shows a diff, and writes on confirmation.

Requires: ANTHROPIC_API_KEY

Usage (interactive):
    python admin_update.py

Usage (non-interactive):
    python admin_update.py --country japan --source "https://..."
    python admin_update.py --country japan --text "Fee is now 1500 INR as of March 2025."
"""

import argparse
import difflib
import os
import re
import sys
import textwrap
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from typing import Optional

import yaml

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

DATA_DIR = os.path.join("data", "visas")
ANTHROPIC_MODEL = "claude-sonnet-4-6"
FETCH_TIMEOUT = 10  # seconds
MAX_SOURCE_CHARS = 4000

_CLAUDE_PROMPT = """\
You are updating a YAML travel data file for Indian passport holders.

Current YAML:
---
{current_yaml}

New authoritative source content:
{source_content}

Instructions:
- Update ONLY fields that are clearly addressed by the source content
- Do not change fields not mentioned in the source
- Preserve all YAML keys, structure, and formatting conventions
- Return the complete updated YAML wrapped in ```yaml ... ``` fences
- If the source contains no actionable updates, return the original YAML unchanged\
"""


# ── HTML stripping ────────────────────────────────────────────────────────────

class _TextExtractor(HTMLParser):
    """Minimal HTML → text extractor using stdlib html.parser."""

    _SKIP_TAGS = {"script", "style", "nav", "footer", "header", "noscript", "svg"}

    def __init__(self):
        super().__init__()
        self._skip_depth = 0
        self.chunks: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in self._SKIP_TAGS:
            self._skip_depth += 1

    def handle_endtag(self, tag):
        if tag in self._SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data):
        if self._skip_depth == 0:
            text = data.strip()
            if text:
                self.chunks.append(text)


def _strip_html(raw: str) -> str:
    extractor = _TextExtractor()
    extractor.feed(raw)
    return " ".join(extractor.chunks)


# ── URL fetching ──────────────────────────────────────────────────────────────

def fetch_url(url: str) -> str:
    """
    Fetch URL content with a browser-like User-Agent.
    Strips HTML if the response is HTML.
    Returns plain text (max MAX_SOURCE_CHARS chars) or raises on hard failure.
    """
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT) as resp:
            content_type = resp.getheader("Content-Type", "")
            raw = resp.read(65536).decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"HTTP {exc.code} fetching {url}") from exc
    except Exception as exc:
        raise RuntimeError(f"Failed to fetch {url}: {exc}") from exc

    if "html" in content_type.lower():
        text = _strip_html(raw)
    else:
        text = raw

    return text[:MAX_SOURCE_CHARS]


# ── YAML file resolution ──────────────────────────────────────────────────────

def resolve_yaml_path(country: str, data_dir: str = DATA_DIR) -> Optional[str]:
    """
    Map a country name or filename stem to its YAML path.
    Tries both exact stem and various normalisations.
    """
    slug = country.lower().replace(" ", "-").replace("_", "-")
    candidates = [
        os.path.join(data_dir, f"{slug}.yaml"),
        os.path.join(data_dir, f"{slug}.yml"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path

    # Fuzzy: scan directory for a close match
    try:
        for fname in os.listdir(data_dir):
            stem = os.path.splitext(fname)[0].lower()
            if stem == slug:
                return os.path.join(data_dir, fname)
    except FileNotFoundError:
        pass

    return None


# ── Claude interaction ────────────────────────────────────────────────────────

def _extract_yaml_block(text: str) -> Optional[str]:
    """
    Extract the content of the first ```yaml ... ``` fence in Claude's response.
    Falls back to the whole response if no fence found (assuming it's raw YAML).
    """
    match = re.search(r"```(?:yaml)?\n(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    # Fallback: strip any leading/trailing prose
    stripped = text.strip()
    if stripped.startswith(("country:", "---")):
        return stripped
    return None


def propose_update(current_yaml: str, source_content: str) -> str:
    """
    Ask Claude to produce an updated YAML given source_content.
    Returns the proposed YAML string (may be identical to current if no changes needed).
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = _CLAUDE_PROMPT.format(
        current_yaml=current_yaml,
        source_content=source_content[:MAX_SOURCE_CHARS],
    )

    response = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text
    extracted = _extract_yaml_block(raw)

    if extracted is None:
        raise RuntimeError(
            "Claude did not return a YAML block. Raw response:\n" + raw[:500]
        )
    return extracted


# ── Diff display ──────────────────────────────────────────────────────────────

def show_diff(current: str, proposed: str, filepath: str) -> bool:
    """
    Print a unified diff between current and proposed YAML.
    Returns True if there are changes, False if identical.
    """
    current_lines  = current.splitlines(keepends=True)
    proposed_lines = proposed.splitlines(keepends=True)

    diff = list(difflib.unified_diff(
        current_lines,
        proposed_lines,
        fromfile=f"a/{os.path.basename(filepath)}",
        tofile=f"b/{os.path.basename(filepath)}",
    ))

    if not diff:
        print("\nNo changes — proposed YAML is identical to current.\n")
        return False

    print("\n--- Proposed changes ---")
    for line in diff:
        if line.startswith("+") and not line.startswith("+++"):
            print(f"\033[32m{line}\033[0m", end="")
        elif line.startswith("-") and not line.startswith("---"):
            print(f"\033[31m{line}\033[0m", end="")
        else:
            print(line, end="")
    print("\n--- End of diff ---\n")
    return True


# ── Write ─────────────────────────────────────────────────────────────────────

def write_yaml(filepath: str, proposed_yaml: str) -> None:
    """
    Write the proposed YAML to the file.
    We write the raw string from Claude (which preserves original formatting)
    rather than round-tripping through PyYAML to avoid key reordering.
    """
    # Ensure proposed YAML is valid before writing
    try:
        yaml.safe_load(proposed_yaml)
    except yaml.YAMLError as exc:
        raise RuntimeError(f"Proposed YAML is not valid: {exc}") from exc

    with open(filepath, "w", encoding="utf-8") as fh:
        if not proposed_yaml.endswith("\n"):
            proposed_yaml += "\n"
        fh.write(proposed_yaml)


# ── Interactive input helpers ─────────────────────────────────────────────────

def _read_multiline_input(prompt: str) -> str:
    """Read multi-line input until a blank line."""
    print(prompt)
    print("(paste text, then press Enter on a blank line to finish)")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line == "" and lines:
            break
        lines.append(line)
    return "\n".join(lines)


def _prompt_country() -> str:
    while True:
        country = input("Country (e.g. japan, South Korea): ").strip()
        if country:
            return country
        print("Country cannot be empty.")


def _prompt_source() -> tuple[Optional[str], Optional[str]]:
    """
    Returns (url_or_None, text_or_None).
    Interactive: asks for URL or raw text.
    """
    print("\nSource — enter a URL or paste raw text:")
    print("  [1] URL")
    print("  [2] Paste text")
    choice = input("Choice [1/2]: ").strip()

    if choice == "1":
        url = input("URL: ").strip()
        return url, None
    else:
        text = _read_multiline_input("Paste your text:")
        return None, text


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Admin update tool: apply trusted-source updates to a country YAML.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              python admin_update.py
              python admin_update.py --country japan --source "https://www.vfsglobal.com/..."
              python admin_update.py --country japan --text "Fee is now 1500 INR."
        """),
    )
    parser.add_argument("--country", "-c", help="Country name or filename stem (e.g. japan)")
    parser.add_argument("--source", "-s", metavar="URL", help="URL to fetch as the source")
    parser.add_argument("--text", "-t", metavar="TEXT", help="Raw source text (alternative to URL)")
    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Apply changes without confirmation prompt.",
    )
    args = parser.parse_args()

    # ── Resolve country ──────────────────────────────────────────────────────
    country = args.country
    if not country:
        country = _prompt_country()

    yaml_path = resolve_yaml_path(country)
    if not yaml_path:
        print(f"ERROR: Could not find a YAML file for {country!r} in {DATA_DIR}/", file=sys.stderr)
        print("Available countries:", file=sys.stderr)
        try:
            stems = sorted(
                os.path.splitext(f)[0]
                for f in os.listdir(DATA_DIR)
                if f.endswith((".yaml", ".yml"))
            )
            for s in stems:
                print(f"  {s}", file=sys.stderr)
        except FileNotFoundError:
            pass
        return 1

    with open(yaml_path, encoding="utf-8") as fh:
        current_yaml = fh.read()

    print(f"Found: {yaml_path}")

    # ── Resolve source content ───────────────────────────────────────────────
    source_url  = args.source
    source_text = args.text

    if not source_url and not source_text:
        source_url, source_text = _prompt_source()

    if source_url:
        print(f"Fetching {source_url} ...", end=" ", flush=True)
        try:
            source_content = fetch_url(source_url)
            print(f"OK ({len(source_content)} chars)")
        except RuntimeError as exc:
            print(f"FAILED: {exc}", file=sys.stderr)
            return 1
    else:
        source_content = source_text or ""

    if not source_content.strip():
        print("ERROR: Source content is empty.", file=sys.stderr)
        return 1

    # ── Ask Claude ───────────────────────────────────────────────────────────
    print(f"\nAsking {ANTHROPIC_MODEL} to generate updated YAML...", end=" ", flush=True)
    try:
        proposed_yaml = propose_update(current_yaml, source_content)
        print("done.")
    except RuntimeError as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        return 1

    # ── Show diff ────────────────────────────────────────────────────────────
    has_changes = show_diff(current_yaml, proposed_yaml, yaml_path)

    if not has_changes:
        print("Nothing to apply.")
        return 0

    # ── Confirm and write ────────────────────────────────────────────────────
    if args.yes:
        confirmed = True
    else:
        answer = input("Apply these changes? [y/N] ").strip().lower()
        confirmed = answer in ("y", "yes")

    if confirmed:
        try:
            write_yaml(yaml_path, proposed_yaml)
            print(f"Updated {yaml_path}")
        except RuntimeError as exc:
            print(f"ERROR writing file: {exc}", file=sys.stderr)
            return 1
    else:
        print("Aborted — no changes written.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
