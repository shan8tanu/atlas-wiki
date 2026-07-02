#!/usr/bin/env python3
"""
add_country.py — AI-assisted new-country pipeline.

Researches a country via Brave Search, drafts a schema-compliant YAML entry
plus a sources sidecar with Claude, validates the draft, updates the mkdocs
nav, and (optionally) opens a PR for human review.

Requires: ANTHROPIC_API_KEY. Recommended: BRAVE_SEARCH_API_KEY.

Usage:
    python add_country.py --country "Sri Lanka" --iso LK --region Asia --pr
    python add_country.py --country "United Kingdom" --iso GB --region Europe --pr --audit
"""

import argparse
import datetime
import os
import re
import subprocess
import sys

import yaml

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY and "--help" not in sys.argv and "-h" not in sys.argv:
    print(
        "ERROR: ANTHROPIC_API_KEY environment variable is not set.",
        file=sys.stderr,
    )
    sys.exit(1)

import anthropic

from validate.claude_audit import _brave_search
from validate.schema import ALLOWED_REGIONS, ISO_3166_1_ALPHA2

DATA_DIR = os.path.join("data", "visas")
SOURCES_DIR = os.path.join("data", "sources")
MKDOCS_YML = "mkdocs.yml"
SVG_MAP = os.path.join("docs", "assets", "world-map.svg")
GOLD_EXAMPLE = os.path.join(DATA_DIR, "japan.yaml")
ANTHROPIC_MODEL = "claude-sonnet-4-6"

PRIMARY_TYPE_KEYS = {
    "Standard Visa": "standard_visa",
    "e-Visa": "evisa",
    "Visa on Arrival": "voa",
}

# ── Stage 1: Research ─────────────────────────────────────────────────────────

RESEARCH_QUERIES = [
    "{country} visa for Indian citizens official government portal apply {year}",
    "{country} visa fee Indian passport INR {year}",
    "{country} visa processing time India {year}",
    "{country} tourist visa required documents Indian applicants",
    "{country} entry requirements vaccination health insurance Indian travellers",
]


def gather_research(country: str, brave_key: str | None) -> str:
    """Run the research queries and return a combined labelled dump."""
    if not brave_key:
        print("WARNING: BRAVE_SEARCH_API_KEY not set -- drafting from training data only.")
        return "(no live web research available)"

    year = datetime.date.today().year
    sections = []
    for template in RESEARCH_QUERIES:
        query = template.format(country=country, year=year)
        print(f"  [research] {query}")
        result = _brave_search(query, brave_key)
        if result:
            sections.append(f"### Query: {query}\n{result}")
    return "\n\n".join(sections)[:10000] or "(all searches returned empty)"


# ── Stage 2: Draft ────────────────────────────────────────────────────────────

_SCHEMA_CONTRACT = """\
SCHEMA CONTRACT — every rule below is checked mechanically; violations are rejected:

Top-level required fields:
- country: string — MUST exactly match the filename slug when lowercased with spaces->hyphens
- iso_code: two uppercase letters (given to you — do not change it)
- visa_difficulty: integer 1-5 (1 = easiest e.g. free VOA, 4-5 = hardest e.g. US/Schengen interviews)
- visa_type: exactly one of "Standard Visa" | "e-Visa" | "Visa on Arrival" — the PRIMARY route for Indian tourists
- max_stay: short string, e.g. "30 days" or "90 days per 180-day period"
- entry_type: quoted string, e.g. "Single Entry" or "Multiple Entry"
- visa_validity: quoted string, e.g. "3 months from issue"
- passport_validity_months: integer (usually 6, sometimes 3)
- blank_pages_required: integer (usually 2)
- region: exactly one of "Asia" | "Europe" | "Americas" | "Oceania" | "Middle East" (given to you)

authority block:
- name: official issuing mission, e.g. "High Commission of Canada, New Delhi"
- processor: who handles applications — one of VFS Global / BLS International / TLScontact / Online / Embassy / High Commission / Consulate / Direct
- official_portal: HTTPS URL of the official application portal (government or processor — never a travel agency)

visa_types block (dict of tabs; KEY ORDER = display order):
- ONLY include visa categories that actually exist for Indian citizens. Do NOT invent an e-Visa tab
  if the country has no e-Visa for Indians — that is the worst possible error.
- Allowed keys: standard_visa, evisa, voa, long_term — each with `label` (string) and `documents` (list of strings)
- The FIRST key must correspond to visa_type: Standard Visa->standard_visa, e-Visa->evisa, Visa on Arrival->voa
- Document strings should be specific and actionable, matching the tone of the gold example

requirements block:
- visa_fee_inr: integer >= 0 in Indian Rupees (0 is valid for free visas). Use the government fee for
  the primary visa type; if the processor adds a mandatory service charge, use the realistic total an
  applicant pays and note the breakdown in the sidecar.
- processing_days: integer >= 1 — realistic typical processing time in working days (not best-case marketing)
- photo_specs: dimensions matching regex ^\\d+x\\d+mm$ (e.g. 35x45mm) and bg_color (e.g. White)
- financial_proof: prose summary, MINIMUM 20 characters
- financial_documents: list of strings for SALARIED applicants (may be [] for simple VOA/e-Visa countries)
- occupation_documents: dict with EXACTLY these 5 keys, each a list of strings:
  self_employed, business_owner, student, homemaker, retired
  (follow the gold example's patterns; simple e-Visa/VOA countries use lighter lists)

health block (each string MINIMUM 20 characters):
- vaccinations, insurance, notes

Never use placeholder values: TBD, N/A, TODO, or empty strings.
"""

_SIDECAR_SPEC = """\
SOURCES SIDECAR — the second YAML block records provenance for every fact group:

_meta:
  generated: "<today's date YYYY-MM-DD>"
  method: ai-draft-v1
  model: claude-sonnet-4-6
<field>:            # one entry per: visa_type, visa_difficulty, max_stay, entry_type, visa_validity,
  source: <url|null> #   authority, visa_types, visa_fee_inr, processing_days, photo_specs,
  confidence: <c>    #   financial_documents, occupation_documents, health
  note: <optional one-liner, e.g. fee breakdown or caveat>

confidence values (be honest — this drives human review priority):
- web        = directly supported by the research snippets provided
- pattern    = copied from analog-country conventions (e.g. Schengen siblings), not sourced
- unverified = plausible from training knowledge but no source found

If research contradicts your training knowledge, PREFER THE RESEARCH and say so in the note.
"""


def build_system_prompt() -> str:
    with open(GOLD_EXAMPLE, encoding="utf-8") as fh:
        gold = fh.read()
    # Core schema only — strip the optional Section A-D blocks (jurisdiction onwards)
    gold = gold.split("# ── Section A")[0].rstrip()

    return (
        "You are a meticulous visa-data researcher creating YAML database entries for Atlas, "
        "a visa-requirements wiki for Indian passport holders. Accuracy matters more than "
        "completeness: a wrong fee misleads real travellers.\n\n"
        + _SCHEMA_CONTRACT
        + "\nGOLD-STANDARD EXAMPLE (japan.yaml — match its structure, tone, and level of detail):\n"
        "```yaml\n" + gold + "\n```\n\n"
        + _SIDECAR_SPEC
        + "\nOUTPUT FORMAT: respond with exactly TWO fenced ```yaml blocks and nothing else.\n"
        "Block 1 = the country data file. Block 2 = the sources sidecar."
    )


def build_user_prompt(country: str, slug: str, iso: str, region: str, research: str) -> str:
    return (
        f"Create the Atlas entry for:\n"
        f"- country: {country}\n"
        f"- filename slug: {slug}\n"
        f"- iso_code: {iso}\n"
        f"- region: {region}\n\n"
        f"LIVE WEB RESEARCH (gathered today — may be partial or noisy):\n{research}\n\n"
        f"Remember: only include visa_types tabs that genuinely exist for Indian citizens, "
        f"first tab must match visa_type, and mark every unsourced field honestly in the sidecar."
    )


def _extract_yaml_blocks(text: str) -> list[str]:
    return [m.strip() for m in re.findall(r"```yaml\n(.*?)```", text, re.DOTALL)]


def _response_text(response) -> str:
    return "".join(b.text for b in response.content if b.type == "text")


def draft_country(
    client: anthropic.Anthropic,
    system_prompt: str,
    user_prompt: str,
    repair_context: list | None = None,
) -> tuple[str, str, object]:
    """Ask Claude for the two YAML blocks. Returns (main_yaml, sidecar_yaml, response)."""
    messages = repair_context or [{"role": "user", "content": user_prompt}]

    response = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=16000,
        thinking={"type": "adaptive"},
        system=[{
            "type": "text",
            "text": system_prompt,
            "cache_control": {"type": "ephemeral"},
        }],
        messages=messages,
    )
    if response.stop_reason == "max_tokens":
        raise RuntimeError("Response truncated at max_tokens — increase the limit.")

    text = _response_text(response)
    blocks = _extract_yaml_blocks(text)
    if len(blocks) < 2:
        raise RuntimeError(
            f"Expected 2 yaml blocks, got {len(blocks)}. Raw response:\n{text[:800]}"
        )
    return blocks[0], blocks[1], response


# ── Stage 3: Validate ─────────────────────────────────────────────────────────

def run_structural_validation(yaml_path: str) -> tuple[bool, str]:
    """Run validate.py --file on the draft. Returns (passed, output)."""
    proc = subprocess.run(
        [sys.executable, "validate.py", "--file", yaml_path],
        capture_output=True, text=True,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    return proc.returncode == 0, proc.stdout + proc.stderr


# ── Stage 4: Integrate ────────────────────────────────────────────────────────

def update_nav(country: str, slug: str, region: str) -> None:
    """Insert the country alphabetically into its region section of mkdocs.yml."""
    with open(MKDOCS_YML, encoding="utf-8") as fh:
        lines = fh.readlines()

    new_entry = f"      - {country}: {slug}.md\n"
    if new_entry in lines:
        return  # already present (re-run)

    region_idx = None
    for i, line in enumerate(lines):
        if line.rstrip() == f"    - {region}:":
            region_idx = i
            break
    if region_idx is None:
        raise RuntimeError(f"Region section '    - {region}:' not found in mkdocs.yml")

    insert_at = None
    j = region_idx + 1
    while j < len(lines) and lines[j].startswith("      - "):
        existing_name = lines[j].strip()[2:].split(":")[0]
        if country.lower() < existing_name.lower():
            insert_at = j
            break
        j += 1
    if insert_at is None:
        insert_at = j  # after the last entry in the section

    lines.insert(insert_at, new_entry)
    with open(MKDOCS_YML, "w", encoding="utf-8") as fh:
        fh.writelines(lines)


def build_pr_body(country: str, slug: str, sidecar: dict, audit_report: str | None) -> str:
    rows, needs_review = [], []
    for field, info in sidecar.items():
        if field == "_meta" or not isinstance(info, dict):
            continue
        conf = info.get("confidence", "?")
        src = info.get("source") or "—"
        note = info.get("note") or ""
        rows.append(f"| `{field}` | {conf} | {src} | {note} |")
        if conf in ("pattern", "unverified"):
            needs_review.append(f"- [ ] **{field}** ({conf}): {note or 'verify against official source'}")

    body = [
        f"AI-drafted entry for **{country}** via `add_country.py` (research + draft + self-validation).",
        "",
        "## Provenance",
        "| Field | Confidence | Source | Note |",
        "|---|---|---|---|",
        *rows,
        "",
        "## Human verification required before merge",
        *(needs_review or ["- [ ] Spot-check fees and processing time against the official portal"]),
        "- [ ] Open the `official_portal` URL in a browser and confirm it is the real application portal",
        "- [ ] CI htmlproofer must pass (checks the portal URL is live)",
    ]
    if audit_report:
        body += ["", "## Independent AI audit (validate_accuracy.py)", "", audit_report]
    body += ["", "🤖 Generated with [Claude Code](https://claude.com/claude-code)"]
    return "\n".join(body)


def create_pr(country: str, slug: str, pr_body: str) -> str:
    branch = f"add/{slug}"
    scratch_body = os.path.join(SOURCES_DIR, f".pr-body-{slug}.md")

    def git(*args):
        proc = subprocess.run(["git", *args], capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(f"git {' '.join(args)} failed:\n{proc.stderr}")
        return proc.stdout

    git("checkout", "-b", branch, "main")
    try:
        git("add", f"{DATA_DIR}/{slug}.yaml", f"{SOURCES_DIR}/{slug}.yaml", MKDOCS_YML)
        git("commit", "-m",
            f"feat(data): add {country} via add_country.py pipeline\n\n"
            f"AI-drafted from live web research; provenance in data/sources/{slug}.yaml.\n"
            f"Requires human field-by-field verification before merge.\n\n"
            f"Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>")
        git("push", "-u", "origin", branch)

        with open(scratch_body, "w", encoding="utf-8") as fh:
            fh.write(pr_body)
        proc = subprocess.run(
            ["gh", "pr", "create",
             "--title", f"Add country: {country}",
             "--body-file", scratch_body,
             "--base", "main", "--head", branch],
            capture_output=True, text=True,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"gh pr create failed:\n{proc.stderr}")
        return proc.stdout.strip()
    finally:
        if os.path.exists(scratch_body):
            os.remove(scratch_body)
        git("checkout", "main")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="AI-assisted new-country pipeline for Atlas.")
    parser.add_argument("--country", "-c", required=True, help='Display name, e.g. "Sri Lanka"')
    parser.add_argument("--iso", required=True, help="ISO 3166-1 alpha-2 code, e.g. LK")
    parser.add_argument("--region", required=True, help="One of: " + " | ".join(sorted(ALLOWED_REGIONS)))
    parser.add_argument("--pr", action="store_true", help="Create branch + commit + push + PR")
    parser.add_argument("--audit", action="store_true",
                        help="Run validate_accuracy.py on the draft and embed the result in the PR")
    args = parser.parse_args()

    country, iso, region = args.country, args.iso.upper(), args.region
    slug = country.lower().replace(" ", "-")

    # ── Preconditions ────────────────────────────────────────────────────────
    if iso not in ISO_3166_1_ALPHA2:
        print(f"ERROR: {iso!r} is not a valid ISO 3166-1 alpha-2 code.", file=sys.stderr)
        return 1
    if region not in ALLOWED_REGIONS:
        print(f"ERROR: region must be one of {sorted(ALLOWED_REGIONS)}.", file=sys.stderr)
        return 1
    yaml_path = os.path.join(DATA_DIR, f"{slug}.yaml")
    if os.path.exists(yaml_path):
        print(f"ERROR: {yaml_path} already exists.", file=sys.stderr)
        return 1
    if args.pr:
        dirty = subprocess.run(["git", "status", "--porcelain"],
                               capture_output=True, text=True).stdout.strip()
        if dirty:
            print("ERROR: working tree is not clean — commit or stash first.", file=sys.stderr)
            return 1
    with open(SVG_MAP, encoding="utf-8") as fh:
        if f'id="{iso.lower()}"' not in fh.read():
            print(f"WARNING: world-map.svg has no path for {iso.lower()!r} — "
                  f"the map will not highlight this country.")

    print(f"\n=== {country} ({iso}, {region}) -> {slug}.yaml ===")

    # ── Stage 1: research ────────────────────────────────────────────────────
    print("[1/4] Researching...")
    research = gather_research(country, os.environ.get("BRAVE_SEARCH_API_KEY"))

    # ── Stage 2: draft (with one repair attempt) ─────────────────────────────
    print("[2/4] Drafting with Claude...")
    client = anthropic.Anthropic()
    system_prompt = build_system_prompt()
    user_prompt = build_user_prompt(country, slug, iso, region, research)

    main_yaml, sidecar_yaml, response = draft_country(client, system_prompt, user_prompt)
    usage = response.usage
    print(f"  tokens: in={usage.input_tokens} out={usage.output_tokens} "
          f"cache_write={usage.cache_creation_input_tokens} cache_read={usage.cache_read_input_tokens}")

    # ── Stage 3: validate, repair once if needed ─────────────────────────────
    print("[3/4] Validating...")
    yaml.safe_load(main_yaml)  # raises on syntax errors
    sidecar_data = yaml.safe_load(sidecar_yaml)

    os.makedirs(SOURCES_DIR, exist_ok=True)
    with open(yaml_path, "w", encoding="utf-8") as fh:
        fh.write(main_yaml + "\n")

    passed, output = run_structural_validation(yaml_path)
    if not passed:
        print("  Validation failed — one repair attempt...")
        print(output)
        repair_context = [
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": f"```yaml\n{main_yaml}\n```\n```yaml\n{sidecar_yaml}\n```"},
            {"role": "user", "content":
                f"validate.py rejected the draft with these errors — fix them and return "
                f"both corrected yaml blocks:\n{output}"},
        ]
        main_yaml, sidecar_yaml, _ = draft_country(client, system_prompt, user_prompt, repair_context)
        sidecar_data = yaml.safe_load(sidecar_yaml)
        with open(yaml_path, "w", encoding="utf-8") as fh:
            fh.write(main_yaml + "\n")
        passed, output = run_structural_validation(yaml_path)
        if not passed:
            print(f"ERROR: draft still fails validation — removing {yaml_path}.", file=sys.stderr)
            print(output, file=sys.stderr)
            os.remove(yaml_path)
            return 1
    print("  Structural validation passed.")

    sidecar_path = os.path.join(SOURCES_DIR, f"{slug}.yaml")
    with open(sidecar_path, "w", encoding="utf-8") as fh:
        fh.write(sidecar_yaml + "\n")

    # ── Stage 4: integrate ───────────────────────────────────────────────────
    print("[4/4] Updating nav" + (" + creating PR..." if args.pr else "..."))
    update_nav(country, slug, region)

    audit_report = None
    if args.audit:
        audit_path = os.path.join(SOURCES_DIR, f".audit-{slug}.md")
        subprocess.run(
            [sys.executable, "validate_accuracy.py", "--country", slug, "--output", audit_path],
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        if os.path.exists(audit_path):
            with open(audit_path, encoding="utf-8") as fh:
                audit_report = fh.read()
            os.remove(audit_path)

    if args.pr:
        pr_url = create_pr(country, slug, build_pr_body(country, slug, sidecar_data, audit_report))
        print(f"\nPR created: {pr_url}")
    else:
        print(f"\nFiles written (not committed):\n  {yaml_path}\n  {sidecar_path}\n  {MKDOCS_YML} (nav)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
