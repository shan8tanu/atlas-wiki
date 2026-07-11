#!/usr/bin/env python3
"""
test_rendered_pages.py — rendered-DOM assertions against the BUILT site.

Run AFTER `mkdocs build`. Stdlib only (html.parser) — no test framework.
Exit 0 = all assertions pass · exit 1 = failures (blocking in CI).

Why this exists: the occupation selector shipped 2026-03-15 relying on the
bare `hidden` attribute, which `.atlas-checklist__item { display: flex }`
(author CSS beats the UA sheet's [hidden] rule) had already neutralized on
2026-03-01 — so it NEVER worked, and nothing failed. These tests pin the
*rendered* interactivity contract:

  1. exactly 6 occupation buttons;
  2. every non-salaried occupation item carries the hide mechanism
     (.atlas-occ-hidden class + hidden attribute);
  3. salaried items carry neither;
  4. visa-type items: first tab's visible, all other tabs' hidden
     (.atlas-vtype-hidden + hidden);
  5. the structural contract the JS depends on: vtype selector, occ selector
     and checklist all exist and share the same data-country (the JS looks
     the checklist up by that attribute — rearranging the template so they
     no longer agree must fail CI, not silently break the page);
  6. no collateral damage on the reference page: fees table with computed
     totals + at least one Sources line still render on japan.

Usage:
    python tests/test_rendered_pages.py            # tests site/japan + site/thailand
    python tests/test_rendered_pages.py --site-dir site
"""

import argparse
import os
import sys
from html.parser import HTMLParser

OCC_TYPES = {"salaried", "self_employed", "business_owner",
             "student", "homemaker", "retired"}


class PageScan(HTMLParser):
    """Flat scan: collect the elements + attributes the assertions need."""

    def __init__(self):
        super().__init__()
        self.occ_buttons = []          # data-occ of each .atlas-occ-btn
        self.vtype_tabs = []           # data-vtype of each .atlas-vtype-tab, in order
        self.occ_items = []            # {occ, classes, hidden} per --occ label
        self.vtype_items = []          # {vtype, classes, hidden} per --vtype label
        self.selector_country = {}     # {'vtype': .., 'occ': .., 'checklist': ..}
        self.checklist_count = 0
        self.fees_tables = 0
        self.sources_lines = 0
        self._grab_text_for = None
        self.texts = []                # texts inside .atlas-fees (totals line check)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = (a.get("class") or "").split()

        if "atlas-occ-btn" in classes:
            self.occ_buttons.append(a.get("data-occ"))
        if "atlas-vtype-tab" in classes:
            self.vtype_tabs.append(a.get("data-vtype"))

        if tag == "label" and "atlas-checklist__item--occ" in classes:
            self.occ_items.append({
                "occ": a.get("data-occ"),
                "classes": classes,
                "hidden": "hidden" in a,
            })
        if tag == "label" and "atlas-checklist__item--vtype" in classes:
            self.vtype_items.append({
                "vtype": a.get("data-vtype"),
                "classes": classes,
                "hidden": "hidden" in a,
            })

        if "atlas-vtype-selector" in classes:
            self.selector_country["vtype"] = a.get("data-country")
        if "atlas-occ-selector" in classes:
            self.selector_country["occ"] = a.get("data-country")
        if "atlas-checklist" in classes:
            self.checklist_count += 1
            self.selector_country["checklist"] = a.get("data-country")

        if "atlas-fees" in classes:
            self.fees_tables += 1
            self._grab_text_for = "fees"
        if "atlas-sources" in classes:
            self.sources_lines += 1

    def handle_data(self, data):
        if self._grab_text_for == "fees" and data.strip():
            self.texts.append(data.strip())


def scan(path: str) -> PageScan:
    p = PageScan()
    with open(path, encoding="utf-8") as fh:
        p.feed(fh.read())
    return p


def check_page(path: str, slug: str, expect_fees_and_sources: bool) -> list:
    """Returns a list of failure strings (empty = page passes)."""
    fails = []
    if not os.path.exists(path):
        return [f"{path}: built page missing"]
    s = scan(path)

    # 1. exactly 6 occupation buttons, one per occupation
    if len(s.occ_buttons) != 6 or set(s.occ_buttons) != OCC_TYPES:
        fails.append(f"expected exactly 6 occupation buttons {sorted(OCC_TYPES)}, "
                     f"got {len(s.occ_buttons)}: {s.occ_buttons}")

    # 2./3. occupation items: hide mechanism on non-salaried, absent on salaried
    for item in s.occ_items:
        is_hidden = "atlas-occ-hidden" in item["classes"] and item["hidden"]
        if item["occ"] == "salaried":
            if "atlas-occ-hidden" in item["classes"] or item["hidden"]:
                fails.append(f"salaried occ item must be visible by default, got "
                             f"classes={item['classes']} hidden={item['hidden']}")
        else:
            if not is_hidden:
                fails.append(f"occ item data-occ={item['occ']!r} must carry BOTH "
                             f".atlas-occ-hidden and the hidden attribute, got "
                             f"classes={item['classes']} hidden={item['hidden']}")

    # 4. visa-type items: first tab visible, others hidden
    if s.vtype_tabs:
        first = s.vtype_tabs[0]
        for item in s.vtype_items:
            hid = "atlas-vtype-hidden" in item["classes"] and item["hidden"]
            if item["vtype"] == first and hid:
                fails.append(f"first-tab ({first}) vtype item must be visible, got "
                             f"classes={item['classes']}")
            if item["vtype"] != first and not hid:
                fails.append(f"vtype item data-vtype={item['vtype']!r} (non-first tab) "
                             f"must carry .atlas-vtype-hidden + hidden, got "
                             f"classes={item['classes']} hidden={item['hidden']}")

    # 5. the JS lookup contract: selectors + checklist agree on data-country
    if s.checklist_count != 1:
        fails.append(f"expected exactly 1 .atlas-checklist, got {s.checklist_count}")
    want = {"occ", "checklist"} | ({"vtype"} if s.vtype_tabs else set())
    missing = want - set(k for k, v in s.selector_country.items() if v)
    if missing:
        fails.append(f"missing data-country on: {sorted(missing)} "
                     f"(the JS finds the checklist BY this attribute)")
    else:
        vals = {s.selector_country[k] for k in want}
        if vals != {slug}:
            fails.append(f"data-country mismatch: {s.selector_country} != {slug!r}")

    # 6. no collateral damage (reference page only)
    if expect_fees_and_sources:
        if s.fees_tables < 1 or not any("Total (mandatory)" in t for t in s.texts):
            fails.append("fees table with computed 'Total (mandatory)' line missing")
        if s.sources_lines < 1:
            fails.append("no .atlas-sources citation line found")

    return [f"{os.path.basename(path)}: {f}" for f in fails]


def main() -> int:
    ap = argparse.ArgumentParser(description="Rendered-DOM tests for the built site.")
    ap.add_argument("--site-dir", default="site")
    args = ap.parse_args()

    failures = []
    failures += check_page(os.path.join(args.site_dir, "japan", "index.html"),
                           "japan", expect_fees_and_sources=True)
    failures += check_page(os.path.join(args.site_dir, "thailand", "index.html"),
                           "thailand", expect_fees_and_sources=False)

    if failures:
        print(f"RENDERED-DOM TESTS: {len(failures)} FAILURE(S)")
        for f in failures:
            print(f"  FAIL {f}")
        return 1
    print("RENDERED-DOM TESTS: all assertions passed (japan, thailand)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
