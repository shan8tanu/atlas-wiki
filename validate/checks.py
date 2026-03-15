"""
Structural and exhaustiveness check functions (groups A–F).
Each function returns a list of CheckResult objects.
"""

import os
import re
import urllib.parse
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import yaml

from validate.schema import (
    ALLOWED_REGIONS,
    ALLOWED_VISA_DIFFICULTIES,
    ALLOWED_VISA_TYPES,
    ISO_3166_1_ALPHA2,
    KNOWN_PROCESSORS,
    PLACEHOLDER_VALUES,
)


@dataclass
class CheckResult:
    check_id: str
    severity: str       # ERROR | WARNING | INFO
    passed: bool
    message: str
    file: str


# ── Helpers ──────────────────────────────────────────────────────────────────

def _ok(check_id: str, file: str, message: str) -> CheckResult:
    return CheckResult(check_id, "INFO", True, message, file)


def _warn(check_id: str, file: str, message: str) -> CheckResult:
    return CheckResult(check_id, "WARNING", False, message, file)


def _err(check_id: str, file: str, message: str) -> CheckResult:
    return CheckResult(check_id, "ERROR", False, message, file)


def _get(data: dict, *keys, default=None):
    """Safe nested dict access."""
    cur = data
    for k in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k, default)
        if cur is None:
            return default
    return cur


# ── Group A: YAML parsing ─────────────────────────────────────────────────────
# A1 and A2 are run in validate.py before this module is called, because they
# need to catch parse errors.  They are reproduced here for documentation only.

def check_a_parse(filepath: str) -> Tuple[Optional[dict], List[CheckResult]]:
    """
    A1: File parses as valid YAML.
    A2: Top-level value is a dict.
    Returns (parsed_data_or_None, [CheckResult, ...]).
    """
    results = []
    short = os.path.basename(filepath)
    try:
        with open(filepath, encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        results.append(_ok("A1", short, "Valid YAML"))
    except yaml.YAMLError as exc:
        results.append(_err("A1", short, f"YAML parse error: {exc}"))
        return None, results

    if not isinstance(data, dict):
        results.append(_err("A2", short, f"Top-level value is {type(data).__name__}, expected dict"))
        return None, results

    results.append(_ok("A2", short, "Top-level is a dict"))
    return data, results


# ── Group B: Required field presence ─────────────────────────────────────────

def check_b(filepath: str, data: dict) -> List[CheckResult]:
    short = os.path.basename(filepath)
    results = []

    def req(check_id, *keys):
        val = _get(data, *keys)
        path = ".".join(keys)
        if val is None:
            results.append(_err(check_id, short, f"Missing required field: {path}"))
        else:
            results.append(_ok(check_id, short, f"{path} present"))

    # Top-level fields
    req("B1", "country")
    req("B2", "iso_code")
    req("B3", "visa_difficulty")
    req("B4", "visa_type")
    req("B5", "max_stay")
    req("B6", "region")

    # Authority block
    authority = _get(data, "authority")
    if authority is None:
        results.append(_err("B7", short, "Missing required block: authority"))
        # Add placeholders for sub-fields
        for cid in ("B8", "B9", "B10"):
            results.append(_err(cid, short, "Cannot check (authority block missing)"))
    else:
        results.append(_ok("B7", short, "authority block present"))
        req("B8", "authority", "name")
        req("B9", "authority", "processor")
        req("B10", "authority", "official_portal")

    # Requirements block
    reqs = _get(data, "requirements")
    if reqs is None:
        results.append(_err("B11", short, "Missing required block: requirements"))
        for cid in ("B12", "B13", "B14", "B15", "B16", "B17", "B18"):
            results.append(_err(cid, short, "Cannot check (requirements block missing)"))
    else:
        results.append(_ok("B11", short, "requirements block present"))
        req("B12", "requirements", "visa_fee_inr")
        req("B13", "requirements", "processing_days")
        photo = _get(data, "requirements", "photo_specs")
        if photo is None:
            results.append(_err("B14", short, "Missing required block: requirements.photo_specs"))
            results.append(_err("B15", short, "Cannot check (photo_specs block missing)"))
            results.append(_err("B16", short, "Cannot check (photo_specs block missing)"))
        else:
            results.append(_ok("B14", short, "requirements.photo_specs present"))
            req("B15", "requirements", "photo_specs", "dimensions")
            req("B16", "requirements", "photo_specs", "bg_color")
        req("B17", "requirements", "financial_proof")
        req("B18", "requirements", "financial_documents")

    # Health block
    health = _get(data, "health")
    if health is None:
        results.append(_err("B19", short, "Missing required block: health"))
        for cid in ("B20", "B21", "B22"):
            results.append(_err(cid, short, "Cannot check (health block missing)"))
    else:
        results.append(_ok("B19", short, "health block present"))
        req("B20", "health", "vaccinations")
        req("B21", "health", "insurance")
        req("B22", "health", "notes")

    return results


# ── Group C: Type validation ──────────────────────────────────────────────────

def check_c(filepath: str, data: dict) -> List[CheckResult]:
    short = os.path.basename(filepath)
    results = []

    def typecheck(check_id, expected_type, *keys):
        val = _get(data, *keys)
        path = ".".join(keys)
        if val is None:
            return  # Missing — caught by B checks
        if not isinstance(val, expected_type):
            results.append(_err(check_id, short,
                f"{path} must be {expected_type.__name__}, got {type(val).__name__} ({val!r})"))
        else:
            results.append(_ok(check_id, short, f"{path} is {expected_type.__name__}"))

    typecheck("C1", int, "visa_difficulty")
    typecheck("C2", int, "requirements", "visa_fee_inr")
    typecheck("C3", int, "requirements", "processing_days")
    typecheck("C4", list, "requirements", "financial_documents")

    return results


# ── Group D: Value validation ─────────────────────────────────────────────────

def check_d(filepath: str, data: dict) -> List[CheckResult]:
    short = os.path.basename(filepath)
    results = []

    # D1: visa_difficulty in [1,2,3,4]
    diff = _get(data, "visa_difficulty")
    if diff is not None and isinstance(diff, int):
        if diff not in ALLOWED_VISA_DIFFICULTIES:
            results.append(_err("D1", short,
                f"visa_difficulty {diff!r} not in {sorted(ALLOWED_VISA_DIFFICULTIES)}"))
        else:
            results.append(_ok("D1", short, f"visa_difficulty={diff} valid"))

    # D2: iso_code matches ^[A-Z]{2}$
    iso = _get(data, "iso_code")
    if iso is not None:
        if not re.match(r"^[A-Z]{2}$", str(iso)):
            results.append(_err("D2", short, f"iso_code {iso!r} does not match ^[A-Z]{{2}}$"))
        else:
            results.append(_ok("D2", short, f"iso_code={iso} matches pattern"))

            # D3: iso_code in ISO 3166-1 alpha-2 set
            if str(iso) not in ISO_3166_1_ALPHA2:
                results.append(_err("D3", short, f"iso_code {iso!r} not in ISO 3166-1 alpha-2 set"))
            else:
                results.append(_ok("D3", short, f"iso_code={iso} is a valid ISO code"))

    # D4: visa_type in allowed set
    vtype = _get(data, "visa_type")
    if vtype is not None:
        if vtype not in ALLOWED_VISA_TYPES:
            results.append(_err("D4", short,
                f"visa_type {vtype!r} not in {sorted(ALLOWED_VISA_TYPES)}"))
        else:
            results.append(_ok("D4", short, f"visa_type={vtype!r} valid"))

    # D5: region in allowed set
    region = _get(data, "region")
    if region is not None:
        if region not in ALLOWED_REGIONS:
            results.append(_err("D5", short,
                f"region {region!r} not in {sorted(ALLOWED_REGIONS)}"))
        else:
            results.append(_ok("D5", short, f"region={region!r} valid"))

    # D6: processor not in known set → WARNING only
    processor = _get(data, "authority", "processor")
    if processor is not None:
        if not any(k.lower() in str(processor).lower() for k in KNOWN_PROCESSORS):
            results.append(_warn("D6", short,
                f"authority.processor {processor!r} is not in the known processor set -- verify"))
        else:
            results.append(_ok("D6", short, f"processor={processor!r} recognised"))

    # D7: visa_fee_inr >= 0
    fee = _get(data, "requirements", "visa_fee_inr")
    if fee is not None and isinstance(fee, int):
        if fee < 0:
            results.append(_err("D7", short, f"visa_fee_inr={fee} must be >= 0"))
        else:
            results.append(_ok("D7", short, f"visa_fee_inr={fee} >= 0"))

    # D8: processing_days >= 1
    days = _get(data, "requirements", "processing_days")
    if days is not None and isinstance(days, int):
        if days < 1:
            results.append(_err("D8", short, f"processing_days={days} must be >= 1"))
        else:
            results.append(_ok("D8", short, f"processing_days={days} >= 1"))

    # D9: official_portal starts with https://
    portal = _get(data, "authority", "official_portal")
    if portal is not None:
        if not str(portal).startswith("https://"):
            results.append(_err("D9", short,
                f"official_portal must start with https://, got {portal!r}"))
        else:
            results.append(_ok("D9", short, "official_portal uses HTTPS"))

            # D10: syntactically valid URL
            try:
                parsed = urllib.parse.urlparse(str(portal))
                if not (parsed.scheme and parsed.netloc):
                    raise ValueError("Missing scheme or netloc")
                results.append(_ok("D10", short, "official_portal is a valid URL"))
            except Exception as exc:
                results.append(_err("D10", short, f"official_portal is not a valid URL: {exc}"))

    return results


# ── Group E: Exhaustiveness ───────────────────────────────────────────────────

def check_e(filepath: str, data: dict) -> List[CheckResult]:
    short = os.path.basename(filepath)
    results = []

    # E1: financial_proof >= 20 chars
    fp = _get(data, "requirements", "financial_proof")
    if fp is not None:
        if len(str(fp)) < 20:
            results.append(_err("E1", short,
                f"financial_proof too short ({len(str(fp))} chars, min 20)"))
        else:
            results.append(_ok("E1", short, "financial_proof meets length requirement"))

    # E2: health.vaccinations >= 20 chars
    vacc = _get(data, "health", "vaccinations")
    if vacc is not None:
        if len(str(vacc)) < 20:
            results.append(_err("E2", short,
                f"health.vaccinations too short ({len(str(vacc))} chars, min 20)"))
        else:
            results.append(_ok("E2", short, "health.vaccinations meets length requirement"))

    # E3: health.notes >= 20 chars
    notes = _get(data, "health", "notes")
    if notes is not None:
        if len(str(notes)) < 20:
            results.append(_err("E3", short,
                f"health.notes too short ({len(str(notes))} chars, min 20)"))
        else:
            results.append(_ok("E3", short, "health.notes meets length requirement"))

    # E4: photo_specs.dimensions matches ^\d+x\d+mm$
    dims = _get(data, "requirements", "photo_specs", "dimensions")
    if dims is not None:
        if not re.match(r"^\d+x\d+mm$", str(dims)):
            results.append(_err("E4", short,
                f"photo_specs.dimensions {dims!r} does not match pattern e.g. 35x45mm"))
        else:
            results.append(_ok("E4", short, f"photo_specs.dimensions={dims!r} matches pattern"))

    # E5: WARNING if visa_type == "Standard Visa" and financial_documents == []
    vtype = _get(data, "visa_type")
    fin_docs = _get(data, "requirements", "financial_documents")
    if vtype == "Standard Visa" and isinstance(fin_docs, list) and len(fin_docs) == 0:
        results.append(_warn("E5", short,
            "visa_type is 'Standard Visa' but financial_documents is empty — intentional?"))
    else:
        results.append(_ok("E5", short, "financial_documents / visa_type combination OK"))

    # E6: financial_proof not a placeholder
    if fp is not None:
        if str(fp).strip().upper() in PLACEHOLDER_VALUES:
            results.append(_err("E6", short,
                f"financial_proof contains placeholder value {fp!r}"))
        else:
            results.append(_ok("E6", short, "financial_proof is not a placeholder"))

    # E7: country field matches filename stem (copy-paste guard)
    country = _get(data, "country")
    if country is not None:
        stem = os.path.splitext(os.path.basename(filepath))[0]  # e.g. "south-korea"
        # Normalise: lowercase, replace spaces with hyphens
        normalised_country = str(country).lower().replace(" ", "-").replace("_", "-")
        if normalised_country != stem:
            results.append(_warn("E7", short,
                f"country field {country!r} does not match filename stem {stem!r} "
                f"(normalised: {normalised_country!r}) -- possible copy-paste error"))
        else:
            results.append(_ok("E7", short, "country field matches filename stem"))

    return results


# ── Group F: Cross-file consistency ──────────────────────────────────────────

def check_f(
    yaml_files: Dict[str, dict],
    mkdocs_path: str = "mkdocs.yml",
) -> List[CheckResult]:
    """
    F1: No duplicate iso_code across files.
    F2: No duplicate country across files.
    F3/F4: YAML ↔ mkdocs.yml nav parity.
    """
    results = []

    # F1: duplicate iso_code
    iso_seen: Dict[str, str] = {}
    for filepath, data in yaml_files.items():
        short = os.path.basename(filepath)
        iso = _get(data, "iso_code")
        if iso is None:
            continue
        iso = str(iso)
        if iso in iso_seen:
            results.append(_err("F1", short,
                f"Duplicate iso_code {iso!r} — also used in {iso_seen[iso]}"))
        else:
            iso_seen[iso] = short

    if not any(r.check_id == "F1" and not r.passed for r in results):
        results.append(_ok("F1", "cross-file", f"No duplicate iso_codes across {len(yaml_files)} files"))

    # F2: duplicate country
    country_seen: Dict[str, str] = {}
    for filepath, data in yaml_files.items():
        short = os.path.basename(filepath)
        country = _get(data, "country")
        if country is None:
            continue
        country_key = str(country).lower()
        if country_key in country_seen:
            results.append(_err("F2", short,
                f"Duplicate country {country!r} — also in {country_seen[country_key]}"))
        else:
            country_seen[country_key] = short

    if not any(r.check_id == "F2" and not r.passed for r in results):
        results.append(_ok("F2", "cross-file", f"No duplicate countries across {len(yaml_files)} files"))

    # F3/F4: YAML ↔ mkdocs.yml nav parity
    if not os.path.exists(mkdocs_path):
        results.append(_warn("F3", "mkdocs.yml", "mkdocs.yml not found — skipping nav parity check"))
        return results

    try:
        # mkdocs.yml uses Python-specific YAML tags (e.g. !!python/name:...)
        # that yaml.safe_load cannot handle.  Use a custom loader that silently
        # ignores unknown tags so we can still read the nav structure.
        class _PermissiveLoader(yaml.SafeLoader):
            pass

        def _ignore_unknown(loader, tag_suffix, node):
            if isinstance(node, yaml.ScalarNode):
                return loader.construct_scalar(node)
            if isinstance(node, yaml.SequenceNode):
                return loader.construct_sequence(node, deep=True)
            return loader.construct_mapping(node, deep=True)

        _PermissiveLoader.add_multi_constructor("", _ignore_unknown)

        with open(mkdocs_path, encoding="utf-8") as fh:
            mkdocs_data = yaml.load(fh, Loader=_PermissiveLoader)  # noqa: S506
    except Exception as exc:
        results.append(_err("F3", "mkdocs.yml", f"Could not parse mkdocs.yml: {exc}"))
        return results

    # Extract all .md file paths from nav recursively
    nav_md_files: set = set()

    def extract_nav_files(nav_node):
        if isinstance(nav_node, list):
            for item in nav_node:
                extract_nav_files(item)
        elif isinstance(nav_node, dict):
            for val in nav_node.values():
                if isinstance(val, str) and val.endswith(".md"):
                    nav_md_files.add(val)
                else:
                    extract_nav_files(val)

    extract_nav_files(mkdocs_data.get("nav", []))

    # Strip .md to get stems of referenced pages (exclude non-country pages)
    non_country_pages = {"index.md", "map.md", "CONTRIBUTING.md"}
    nav_country_stems = {
        p[:-3] for p in nav_md_files if p not in non_country_pages
    }

    # YAML file stems
    yaml_stems = {
        os.path.splitext(os.path.basename(fp))[0]
        for fp in yaml_files.keys()
    }

    # F3: YAML files without mkdocs nav entries
    missing_in_nav = yaml_stems - nav_country_stems
    for stem in sorted(missing_in_nav):
        results.append(_warn("F3", f"{stem}.yaml",
            f"data/visas/{stem}.yaml has no matching entry in mkdocs.yml nav"))

    if not missing_in_nav:
        results.append(_ok("F3", "cross-file", "All YAML files have mkdocs.yml nav entries"))

    # F4: mkdocs nav entries without YAML files
    missing_yaml = nav_country_stems - yaml_stems
    for stem in sorted(missing_yaml):
        results.append(_warn("F4", "mkdocs.yml",
            f"mkdocs.yml nav references {stem}.md but data/visas/{stem}.yaml is missing"))

    if not missing_yaml:
        results.append(_ok("F4", "cross-file", "All mkdocs.yml nav entries have matching YAML files"))

    return results
