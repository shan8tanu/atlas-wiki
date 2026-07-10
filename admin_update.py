#!/usr/bin/env python3
"""
admin_update.py — Trusted-source admin update tool.

Fetches authoritative source content (URL or raw text), asks Claude to update
only the relevant YAML fields, shows a diff, and writes on confirmation.

CITATIONS: when the source is a URL (--source, or --text with --cite URL), the
proposed update ALSO adds a `sources` entry (url / tier / label /
accessed=today) to every citable block the source supports and removes that
block's `unverified: true` flag — one command closes a verification-queue item
end to end. Pass --no-cite for a pure value update. The proposed YAML is run
through the structural validators (groups B–J) BEFORE the diff is shown; a
proposal with validation errors is never written.

Requires: ANTHROPIC_API_KEY

Usage (interactive):
    python admin_update.py

Usage (non-interactive):
    python admin_update.py --country japan --source "https://..."
    python admin_update.py --country australia --text "Visitor 600 fee is AUD 200..." \\
        --cite "https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/visitor-600"
    python admin_update.py --country japan --source "https://..." --no-cite
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
from datetime import date
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
Today's date is {today}.

Current YAML:
---
{current_yaml}

New authoritative source content:
{source_content}

Instructions:
- Update ONLY fields that are clearly addressed by the source content
- Do not change fields not mentioned in the source
- Preserve all YAML keys, structure, and formatting conventions
{citation_instructions}
- Return the complete updated YAML wrapped in ```yaml ... ``` fences\
"""

# Appended when a citation URL is available (--source, or --text + --cite).
_CITE_INSTRUCTIONS = """\
- CITATIONS: this source was accessed today at:
    {cite_url}
  For EVERY citable fact block whose facts this source states or confirms
  (even when the stored value needs no change — confirming it IS an update):
    * add (or refresh) a `sources` entry on that block:
        - url: {cite_url}
          tier: {tier}
          label: "<short human name, e.g. 'Home Affairs - Visitor visa 600 (fee, processing)'>"
          accessed: "{today}"
      Append to the block's existing `sources` list if one exists (do not
      duplicate an entry for the same url — refresh its accessed date instead).
    * remove that block's `unverified: true` flag (and any stale comment that
      only explained why it was unverified).
  Citable dict blocks (`requirements`, `health`, `transit`, `ecr`, `biometrics`)
  and each `visa_types.<key>` entry carry `sources` INLINE; the list blocks use
  PARALLEL top-level keys `jurisdiction_sources` / `exemptions_sources` (and
  `jurisdiction_unverified` / `exemptions_unverified`).
  Do NOT add the citation to blocks the source says nothing about, and do NOT
  touch their `unverified` flags.
- If the source contains no actionable updates AND supports no block, return
  the original YAML unchanged\
"""

_NO_CITE_INSTRUCTIONS = """\
- Do NOT modify any `sources` lists or `unverified` flags
- If the source contains no actionable updates, return the original YAML unchanged\
"""


def suggest_tier(url: str) -> int:
    """
    Suggested citation tier by domain, mirroring the add_country.py convention:
    known processor = 2; government-looking domain = 1; otherwise 3.
    Claude may keep or adjust it per the same rules; check H4 validates the result.
    """
    netloc = urllib.parse.urlparse(url).netloc.lower()
    if any(p in netloc for p in ("vfsglobal.", "blsinternational.", "tlscontact.")):
        return 2
    gov_markers = (".gov", ".gouv.", ".go.", ".gob.", ".gv.", ".mil",
                   "europa.eu", ".diplo.de", ".admin.ch", ".mfa.", ".emb-",
                   ".embassy.", ".highcommission.", ".consulate.")
    if any(m in netloc for m in gov_markers):
        return 1
    return 3


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


def build_prompt(current_yaml: str, source_content: str,
                 cite_url: Optional[str] = None) -> str:
    """
    Assemble the update prompt. When cite_url is set, the citation
    instructions (add `sources` entry, clear `unverified`) are included with
    today's date and a suggested tier; otherwise sources/unverified are
    explicitly off-limits.
    """
    today = date.today().isoformat()
    if cite_url:
        citation_instructions = _CITE_INSTRUCTIONS.format(
            cite_url=cite_url, tier=suggest_tier(cite_url), today=today)
    else:
        citation_instructions = _NO_CITE_INSTRUCTIONS
    return _CLAUDE_PROMPT.format(
        today=today,
        current_yaml=current_yaml,
        source_content=source_content[:MAX_SOURCE_CHARS],
        citation_instructions=citation_instructions,
    )


def propose_update(current_yaml: str, source_content: str,
                   cite_url: Optional[str] = None) -> str:
    """
    Ask Claude to produce an updated YAML given source_content.
    Returns the proposed YAML string (may be identical to current if no changes needed).
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = build_prompt(current_yaml, source_content, cite_url)

    response = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text
    extracted = _extract_yaml_block(raw)

    if extracted is None:
        raise RuntimeError(
            "Claude did not return a YAML block. Raw response:\n" + raw[:500]
        )
    return extracted


# ── Pre-write validation gate ─────────────────────────────────────────────────

def validate_proposed(proposed_yaml: str, filepath: str) -> list:
    """
    Run the structural validators (groups B–J) on the PROPOSED YAML before
    anything touches disk. Returns the list of ERROR-level failures (empty =
    safe to show the diff / write). Same checks CI runs, so a proposal that
    passes here won't bounce in CI.
    """
    from validate.checks import (check_b, check_c, check_d, check_e,
                                 check_g, check_h, check_j)
    try:
        data = yaml.safe_load(proposed_yaml)
    except yaml.YAMLError as exc:
        raise RuntimeError(f"Proposed YAML does not parse: {exc}") from exc
    if not isinstance(data, dict):
        raise RuntimeError("Proposed YAML is not a mapping at the top level.")

    results = []
    for check in (check_b, check_c, check_d, check_e, check_g, check_h, check_j):
        results.extend(check(filepath, data))
    return [r for r in results if r.severity == "ERROR" and not r.passed]


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
        "--cite", metavar="URL",
        help="Citation URL when using --text (the page YOU opened). With --source, "
             "the source URL itself is cited automatically.",
    )
    parser.add_argument(
        "--no-cite",
        action="store_true",
        help="Pure value update: do not add sources entries or clear unverified flags.",
    )
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

    # ── Citation URL: --source cites itself; --text needs --cite ────────────
    cite_url = None
    if not args.no_cite:
        cite_url = source_url or args.cite
    if cite_url and not str(cite_url).startswith("https://"):
        print(f"ERROR: citation URL must be https://, got {cite_url!r}", file=sys.stderr)
        return 1
    if cite_url:
        print(f"Citation: will add a sources entry for {cite_url} "
              f"(suggested tier {suggest_tier(cite_url)}, accessed {date.today().isoformat()}) "
              f"to every block this source supports, and clear those blocks' unverified flags.")
    else:
        print("Citation: OFF (values only; sources/unverified untouched)."
              + ("" if args.no_cite else
                 " Tip: pass --cite <url> with --text to cite the page you read."))

    # ── Ask Claude ───────────────────────────────────────────────────────────
    print(f"\nAsking {ANTHROPIC_MODEL} to generate updated YAML...", end=" ", flush=True)
    try:
        proposed_yaml = propose_update(current_yaml, source_content, cite_url)
        print("done.")
    except RuntimeError as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        return 1

    # ── Validate BEFORE showing the diff (same checks CI runs) ──────────────
    try:
        errors = validate_proposed(proposed_yaml, yaml_path)
    except RuntimeError as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        return 1
    if errors:
        print("\nERROR: the proposed update FAILS structural validation — "
              "nothing was written:", file=sys.stderr)
        for r in errors:
            print(f"  [{r.check_id}] {r.message}", file=sys.stderr)
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
