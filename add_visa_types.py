#!/usr/bin/env python3
"""
add_visa_types.py — Batch-add visa_types to all 26 country YAMLs.

Run once from the project root:
    python add_visa_types.py
"""
import os

DATA_DIR = os.path.join("data", "visas")


# ── Visa-type document blocks ──────────────────────────────────────────────────

# Block A: Standard Visa is the primary / default option
_BLOCK_A = """\
visa_types:
  standard_visa:
    label: Standard Visa
    documents:
      - Completed visa application form — printed, signed, and dated
      - Appointment confirmation slip from VFS Global / BLS / embassy
      - Confirmed return flight tickets (printed copy)
      - Proof of accommodation — hotel booking confirmation or invitation letter
      - Travel insurance covering the full stay duration
  evisa:
    label: e-Visa (where available)
    documents:
      - Online application form submitted via the official visa portal
      - Scanned copy of passport bio page — JPEG or PDF, clearly legible
      - Digital photograph — white background, JPEG, minimum 200 KB
      - Return flight booking reference number
      - Hotel or accommodation booking reference number
  long_term:
    label: Long-stay Visa
    documents:
      - Completed long-stay visa application (consulate-specific form)
      - Employer NOC confirming leave of absence for the full stay period
      - Proof of long-term accommodation — lease agreement or host invitation letter
      - Travel insurance covering the full extended stay duration
      - Sponsor letter or proof of fixed deposits / investment holdings
"""

# Block B: e-Visa is the primary / default option
_BLOCK_B = """\
visa_types:
  evisa:
    label: e-Visa
    documents:
      - Online application form submitted via the official visa portal
      - Scanned copy of passport bio page — JPEG or PDF, clearly legible
      - Digital photograph — white background, JPEG, minimum 200 KB
      - Return flight booking reference number
      - Hotel or accommodation booking reference number
  standard_visa:
    label: Standard Visa (Embassy)
    documents:
      - Completed visa application form — printed, signed, and dated
      - Appointment confirmation slip from the embassy or authorised agent
      - Confirmed return flight tickets (printed copy)
      - Proof of accommodation — hotel booking confirmation or invitation letter
      - Travel insurance covering the full stay duration
  long_term:
    label: Long-stay Visa
    documents:
      - Completed long-stay visa application (consulate-specific form)
      - Employer NOC confirming leave of absence for the full stay period
      - Proof of long-term accommodation — lease agreement or host invitation letter
      - Travel insurance covering the full extended stay duration
      - Sponsor letter or proof of fixed deposits / investment holdings
"""

# Block C: Visa on Arrival is the primary / default option
_BLOCK_C = """\
visa_types:
  voa:
    label: Visa on Arrival
    documents:
      - Completed arrival card (distributed on aircraft or at immigration counter)
      - Confirmed return flight ticket — boarding pass or printed itinerary
      - Proof of accommodation — hotel booking printout
      - VOA fee in cash — USD or accepted local currency (check current rate before travel)
  evisa:
    label: e-Visa
    documents:
      - Online application form submitted via the official visa portal
      - Scanned copy of passport bio page — JPEG or PDF, clearly legible
      - Digital photograph — white background, JPEG, minimum 200 KB
      - Return flight booking reference number
      - Hotel or accommodation booking reference number
  standard_visa:
    label: Standard Visa (Embassy)
    documents:
      - Completed visa application form — printed, signed, and dated
      - Appointment confirmation slip from the embassy
      - Confirmed return flight tickets (printed copy)
      - Proof of accommodation — hotel booking confirmation or invitation letter
      - Travel insurance covering the full stay duration
"""

# ── Country → block mapping ────────────────────────────────────────────────────

COUNTRY_BLOCKS = {
    # Standard Visa primary
    "australia":     _BLOCK_A,
    "china":         _BLOCK_A,
    "france":        _BLOCK_A,
    "germany":       _BLOCK_A,
    "greece":        _BLOCK_A,
    "italy":         _BLOCK_A,
    "japan":         _BLOCK_A,
    "netherlands":   _BLOCK_A,
    "new-zealand":   _BLOCK_A,
    "philippines":   _BLOCK_A,
    "singapore":     _BLOCK_A,
    "south-korea":   _BLOCK_A,
    "spain":         _BLOCK_A,
    "switzerland":   _BLOCK_A,
    "uae":           _BLOCK_A,
    "united-states": _BLOCK_A,
    # e-Visa primary
    "brazil":        _BLOCK_B,
    "malaysia":      _BLOCK_B,
    "qatar":         _BLOCK_B,
    "saudi-arabia":  _BLOCK_B,
    "turkey":        _BLOCK_B,
    "vietnam":       _BLOCK_B,
    # Visa on Arrival primary
    "cambodia":      _BLOCK_C,
    "indonesia":     _BLOCK_C,
    "laos":          _BLOCK_C,
    "thailand":      _BLOCK_C,
}


def add_visa_types(filepath: str, block: str) -> bool:
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    if "visa_types:" in content:
        print(f"  SKIP (already has visa_types): {filepath}")
        return False

    # Insert BEFORE the `requirements:` section so it lives at root level
    if "\nrequirements:" in content:
        insertion_point = content.index("\nrequirements:")
        new_content = content[:insertion_point] + "\n" + block + content[insertion_point:]
    else:
        new_content = content.rstrip() + "\n" + block + "\n"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)

    return True


def main():
    updated = 0
    skipped = 0
    for slug, block in COUNTRY_BLOCKS.items():
        path = os.path.join(DATA_DIR, f"{slug}.yaml")
        if not os.path.exists(path):
            print(f"  MISSING: {path}")
            continue
        changed = add_visa_types(path, block)
        if changed:
            print(f"  UPDATED: {path}")
            updated += 1
        else:
            skipped += 1

    print(f"\nDone — {updated} updated, {skipped} skipped.")


if __name__ == "__main__":
    main()
