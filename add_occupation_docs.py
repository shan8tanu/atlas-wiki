#!/usr/bin/env python3
"""
add_occupation_docs.py — Batch-add occupation_documents to all 26 country YAMLs.

Run once from the project root:
    python add_occupation_docs.py
"""
import os

DATA_DIR = os.path.join("data", "visas")


# ── Occupation document templates ─────────────────────────────────────────────

def _occ_block_schengen():
    """3-month bank, 2-year ITR, 3-month salary (Schengen countries)."""
    return """  occupation_documents:
    self_employed:
      - Bank statements for the last 3 months
      - ITR for 2 years (business income)
      - GST registration certificate + returns for 2 years
      - Business registration certificate / trade licence
      - CA-certified audited balance sheet for 2 years
    business_owner:
      - Personal + business bank statements for the last 3 months
      - Personal + company ITR for 2 years
      - Certificate of incorporation / MSME registration
      - Company audited financials for 2 years
      - Director identification proof (DIN)
    student:
      - Admission letter or valid student ID card
      - Sponsoring parent's bank statements (last 3 months)
      - Sponsoring parent's ITR for 2 years
      - Notarised affidavit of financial support
      - NOC from educational institution
    homemaker:
      - Spouse's bank statements for the last 3 months
      - Spouse's ITR for 2 years
      - Notarised affidavit of financial support from spouse
      - Marriage certificate
    retired:
      - Pension slips for the last 3 months (or pension passbook)
      - Bank statements for the last 3 months
      - ITR for 2 years (pension income, if applicable)
      - Pension sanction letter / retirement proof
"""


def _occ_block_6mo_2yr():
    """6-month bank, 2-year ITR (Australia, South Korea)."""
    return """  occupation_documents:
    self_employed:
      - Bank statements for the last 6 months
      - ITR for 2 years (business income)
      - GST registration certificate + returns for 2 years
      - Business registration certificate / trade licence
      - CA-certified audited balance sheet for 2 years
    business_owner:
      - Personal + business bank statements for the last 6 months
      - Personal + company ITR for 2 years
      - Certificate of incorporation / MSME registration
      - Company audited financials for 2 years
      - Director identification proof (DIN)
    student:
      - Admission letter or valid student ID card
      - Sponsoring parent's bank statements (last 3 months)
      - Sponsoring parent's ITR for 2 years
      - Notarised affidavit of financial support
      - NOC from educational institution
    homemaker:
      - Spouse's bank statements for the last 6 months
      - Spouse's ITR for 2 years
      - Notarised affidavit of financial support from spouse
      - Marriage certificate
    retired:
      - Pension slips for the last 3 months (or pension passbook)
      - Bank statements for the last 6 months
      - ITR for 2 years (pension income, if applicable)
      - Pension sanction letter / retirement proof
"""


def _occ_block_6mo_3yr():
    """6-month bank, 3-year ITR (Japan, United States)."""
    return """  occupation_documents:
    self_employed:
      - Bank statements for the last 6 months
      - ITR for 3 years (business income)
      - GST registration certificate + returns for 2 years
      - Business registration certificate / trade licence
      - CA-certified audited balance sheet for 2 years
    business_owner:
      - Personal + business bank statements for the last 6 months
      - Personal + company ITR for 3 years
      - Certificate of incorporation / MSME registration
      - Company audited financials for 2 years
      - Director identification proof (DIN)
    student:
      - Admission letter or valid student ID card
      - Sponsoring parent's bank statements (last 3 months)
      - Sponsoring parent's ITR for 3 years
      - Notarised affidavit of financial support
      - NOC from educational institution
    homemaker:
      - Spouse's bank statements for the last 6 months
      - Spouse's ITR for 3 years
      - Notarised affidavit of financial support from spouse
      - Marriage certificate
    retired:
      - Pension slips for the last 3 months (or pension passbook)
      - Bank statements for the last 6 months
      - ITR for 3 years (pension income, if applicable)
      - Pension sanction letter / retirement proof
"""


def _occ_block_3mo_2yr():
    """3-month bank, 2-year ITR (New Zealand)."""
    return """  occupation_documents:
    self_employed:
      - Bank statements for the last 3 months
      - ITR for 2 years (business income)
      - GST registration certificate + returns for 2 years
      - Business registration certificate / trade licence
      - CA-certified audited balance sheet for 2 years
    business_owner:
      - Personal + business bank statements for the last 3 months
      - Personal + company ITR for 2 years
      - Certificate of incorporation / MSME registration
      - Company audited financials for 2 years
      - Director identification proof (DIN)
    student:
      - Admission letter or valid student ID card
      - Sponsoring parent's bank statements (last 3 months)
      - Sponsoring parent's ITR for 2 years
      - Notarised affidavit of financial support
      - NOC from educational institution
    homemaker:
      - Spouse's bank statements for the last 3 months
      - Spouse's ITR for 2 years
      - Notarised affidavit of financial support from spouse
      - Marriage certificate
    retired:
      - Pension slips for the last 3 months (or pension passbook)
      - Bank statements for the last 3 months
      - ITR for 2 years (pension income, if applicable)
      - Pension sanction letter / retirement proof
"""


def _occ_block_3mo_1yr():
    """3-month bank, 1-year ITR (Philippines)."""
    return """  occupation_documents:
    self_employed:
      - Bank statements for the last 3 months
      - ITR for the last year (business income)
      - GST registration certificate + returns
      - Business registration certificate / trade licence
      - CA-certified audited balance sheet
    business_owner:
      - Personal + business bank statements for the last 3 months
      - Personal + company ITR for the last year
      - Certificate of incorporation / MSME registration
      - Company audited financials
      - Director identification proof (DIN)
    student:
      - Admission letter or valid student ID card
      - Sponsoring parent's bank statements (last 3 months)
      - Sponsoring parent's ITR for the last year
      - Notarised affidavit of financial support
      - NOC from educational institution
    homemaker:
      - Spouse's bank statements for the last 3 months
      - Spouse's ITR for the last year
      - Notarised affidavit of financial support from spouse
      - Marriage certificate
    retired:
      - Pension slips for the last 3 months (or pension passbook)
      - Bank statements for the last 3 months
      - ITR for the last year (pension income, if applicable)
      - Pension sanction letter / retirement proof
"""


def _occ_block_3mo_noITR():
    """3-month bank, no ITR requirement (China, Brazil, Singapore, UAE)."""
    return """  occupation_documents:
    self_employed:
      - Bank statements for the last 3 months
      - ITR for 2 years (business income)
      - Business registration certificate / trade licence
      - CA-certified audited balance sheet for 2 years
    business_owner:
      - Personal + business bank statements for the last 3 months
      - Personal + company ITR for 2 years
      - Certificate of incorporation / MSME registration
      - Company audited financials for 2 years
      - Director identification proof (DIN)
    student:
      - Admission letter or valid student ID card
      - Sponsoring parent's bank statements (last 3 months)
      - Sponsoring parent's ITR for 2 years
      - Notarised affidavit of financial support
      - NOC from educational institution
    homemaker:
      - Spouse's bank statements for the last 3 months
      - Spouse's ITR for 2 years
      - Notarised affidavit of financial support from spouse
      - Marriage certificate
    retired:
      - Pension slips for the last 3 months (or pension passbook)
      - Bank statements for the last 3 months
      - ITR for 2 years (pension income, if applicable)
      - Pension sanction letter / retirement proof
"""


def _occ_block_simplified(funds_text: str = "Proof of sufficient funds in cash or card"):
    """Simplified for VOA/easy e-Visa countries."""
    return f"""  occupation_documents:
    self_employed:
      - {funds_text}
      - Business registration certificate (recommended)
    business_owner:
      - {funds_text}
      - Business registration certificate (recommended)
    student:
      - {funds_text}
      - Admission letter or valid student ID card
      - Notarised affidavit of financial support from sponsor (if applicable)
    homemaker:
      - {funds_text}
    retired:
      - {funds_text}
"""


# ── Country → block mapping ────────────────────────────────────────────────────

COUNTRY_BLOCKS = {
    "australia":     _occ_block_6mo_2yr(),
    "brazil":        _occ_block_3mo_noITR(),
    "cambodia":      _occ_block_simplified("Proof of sufficient funds in cash or card"),
    "china":         _occ_block_3mo_noITR(),
    "france":        _occ_block_schengen(),
    "germany":       _occ_block_schengen(),
    "greece":        _occ_block_schengen(),
    "indonesia":     _occ_block_simplified("Proof of sufficient funds in cash or card"),
    "italy":         _occ_block_schengen(),
    "japan":         _occ_block_6mo_3yr(),
    "laos":          _occ_block_simplified("Proof of sufficient funds in cash or card"),
    "malaysia":      _occ_block_simplified("Bank statement showing minimum INR 50,000 balance"),
    "netherlands":   _occ_block_schengen(),
    "new-zealand":   _occ_block_3mo_2yr(),
    "philippines":   _occ_block_3mo_1yr(),
    "qatar":         _occ_block_simplified("Bank statement showing sufficient funds"),
    "saudi-arabia":  _occ_block_simplified("Proof of sufficient funds in cash or card"),
    "singapore":     _occ_block_3mo_noITR(),
    "south-korea":   _occ_block_6mo_2yr(),
    "spain":         _occ_block_schengen(),
    "switzerland":   _occ_block_schengen(),
    "thailand":      _occ_block_simplified("Proof of sufficient funds — minimum 10,000 THB equivalent in cash or card"),
    "turkey":        _occ_block_simplified("Proof of sufficient funds in cash or card"),
    "uae":           _occ_block_3mo_noITR(),
    "united-states": _occ_block_6mo_3yr(),
    "vietnam":       _occ_block_simplified("Proof of sufficient funds in cash or card"),
}


def add_occupation_documents(filepath: str, block: str) -> bool:
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    if "occupation_documents:" in content:
        print(f"  SKIP (already has occupation_documents): {filepath}")
        return False

    # Insert before the `health:` section (or at end of requirements block)
    # Find the last item of requirements — insert before `health:`
    if "\nhealth:" in content:
        insertion_point = content.index("\nhealth:")
        new_content = content[:insertion_point] + "\n" + block + content[insertion_point:]
    else:
        # Append at end
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
        changed = add_occupation_documents(path, block)
        if changed:
            print(f"  UPDATED: {path}")
            updated += 1
        else:
            skipped += 1

    print(f"\nDone — {updated} updated, {skipped} skipped.")


if __name__ == "__main__":
    main()
