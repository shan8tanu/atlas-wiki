"""
Allowed values, ISO code set, and field contracts for the Atlas visa data.
All constants are hardcoded — no network access required.
"""

ALLOWED_VISA_DIFFICULTIES = {1, 2, 3, 4, 5}

ALLOWED_VISA_TYPES = {"Standard Visa", "e-Visa", "Visa on Arrival"}

ALLOWED_REGIONS = {"Asia", "Europe", "Americas", "Oceania", "Middle East"}

# Well-known processors; anything else triggers a D6 WARNING (not an error).
# D6 does case-insensitive substring matching, so "CVASC" matches the full
# "Chinese Visa Application Service Center (CVASC)" string.
KNOWN_PROCESSORS = {
    "VFS Global",
    "BLS International",
    "TLScontact",
    "Online",
    "Embassy",
    "High Commission",
    "Consulate",
    "CVASC",
    "Direct",
}

PLACEHOLDER_VALUES = {"TBD", "N/A", "TODO", ""}

# Allowed changelog entry types
ALLOWED_CHANGELOG_TYPES = {"Fee", "Document", "Process", "Policy"}

# Known Indian states/UTs for jurisdiction validation
KNOWN_INDIAN_STATES = {
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Delhi", "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jammu & Kashmir",
    "Jharkhand", "Karnataka", "Kerala", "Ladakh", "Madhya Pradesh", "Maharashtra",
    "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Puducherry",
    "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
    "Uttar Pradesh", "Uttarakhand", "West Bengal",
    # UTs
    "Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu",
    "Lakshadweep",
}

# ISO 3166-1 alpha-2 two-letter country codes (hardcoded, no network)
ISO_3166_1_ALPHA2 = {
    "AF", "AX", "AL", "DZ", "AS", "AD", "AO", "AI", "AQ", "AG", "AR", "AM",
    "AW", "AU", "AT", "AZ", "BS", "BH", "BD", "BB", "BY", "BE", "BZ", "BJ",
    "BM", "BT", "BO", "BQ", "BA", "BW", "BV", "BR", "IO", "BN", "BG", "BF",
    "BI", "CV", "KH", "CM", "CA", "KY", "CF", "TD", "CL", "CN", "CX", "CC",
    "CO", "KM", "CG", "CD", "CK", "CR", "CI", "HR", "CU", "CW", "CY", "CZ",
    "DK", "DJ", "DM", "DO", "EC", "EG", "SV", "GQ", "ER", "EE", "SZ", "ET",
    "FK", "FO", "FJ", "FI", "FR", "GF", "PF", "TF", "GA", "GM", "GE", "DE",
    "GH", "GI", "GR", "GL", "GD", "GP", "GU", "GT", "GG", "GN", "GW", "GY",
    "HT", "HM", "VA", "HN", "HK", "HU", "IS", "IN", "ID", "IR", "IQ", "IE",
    "IM", "IL", "IT", "JM", "JP", "JE", "JO", "KZ", "KE", "KI", "KP", "KR",
    "KW", "KG", "LA", "LV", "LB", "LS", "LR", "LY", "LI", "LT", "LU", "MO",
    "MG", "MW", "MY", "MV", "ML", "MT", "MH", "MQ", "MR", "MU", "YT", "MX",
    "FM", "MD", "MC", "MN", "ME", "MS", "MA", "MZ", "MM", "NA", "NR", "NP",
    "NL", "NC", "NZ", "NI", "NE", "NG", "NU", "NF", "MK", "MP", "NO", "OM",
    "PK", "PW", "PS", "PA", "PG", "PY", "PE", "PH", "PN", "PL", "PT", "PR",
    "QA", "RE", "RO", "RU", "RW", "BL", "SH", "KN", "LC", "MF", "PM", "VC",
    "WS", "SM", "ST", "SA", "SN", "RS", "SC", "SL", "SG", "SX", "SK", "SI",
    "SB", "SO", "ZA", "GS", "SS", "ES", "LK", "SD", "SR", "SJ", "SE", "CH",
    "SY", "TW", "TJ", "TZ", "TH", "TL", "TG", "TK", "TO", "TT", "TN", "TR",
    "TM", "TC", "TV", "UG", "UA", "AE", "GB", "US", "UM", "UY", "UZ", "VU",
    "VE", "VN", "VG", "VI", "WF", "EH", "YE", "ZM", "ZW",
}

# Fields checked during the accuracy audit
ACCURACY_AUDIT_FIELDS = [
    "visa_type",
    "visa_difficulty",
    "max_stay",
    "requirements.visa_fee_inr",
    "requirements.processing_days",
    "authority.official_portal",
    "health.vaccinations",
    "health.insurance",
]

# ── Per-claim citations (check group H) ───────────────────────────────────────
# Authority tiers for a `sources` entry:
#   1 = government / embassy / consulate (most authoritative)
#   2 = official processor (VFS Global / BLS International / TLScontact)
#   3 = verified secondary source
ALLOWED_SOURCE_TIERS = {1, 2, 3}

# Every entry in a `sources` list must carry all four of these keys.
SOURCE_REQUIRED_FIELDS = ("url", "tier", "label", "accessed")

# Date format for a source's `accessed` field.
SOURCE_DATE_FORMAT = "%Y-%m-%d"

# The "citable fact blocks" — the single source of truth shared by check_h and
# (mirrored by) templates/country.md.jinja. Each block, when present on a
# country page, should carry either a `sources` list or `unverified: true`.
#
# kind:
#   "dict"       — the block is a mapping; sources/unverified live INSIDE it
#                  (e.g. requirements.sources, requirements.unverified).
#   "dict_items" — the block is a mapping of sub-entries, each a citable dict
#                  (e.g. every visa_types.<key>).
#   "list"       — the block is a bare list, which cannot hold a sibling key, so
#                  its citations live in PARALLEL top-level keys
#                  (sources_key / unverified_key).
CITABLE_BLOCKS = [
    {"key": "requirements", "label": "Requirements & Fees",     "kind": "dict"},
    {"key": "health",       "label": "Health & Vaccinations",   "kind": "dict"},
    {"key": "transit",      "label": "Transit Rules",           "kind": "dict"},
    {"key": "ecr",          "label": "ECR / Non-ECR Passport",  "kind": "dict"},
    {"key": "biometrics",   "label": "Biometrics",              "kind": "dict"},
    {"key": "visa_types",   "label": "Document Checklist",      "kind": "dict_items"},
    {"key": "jurisdiction", "label": "Where to Apply",          "kind": "list",
     "sources_key": "jurisdiction_sources", "unverified_key": "jurisdiction_unverified"},
    {"key": "exemptions",   "label": "Visa Exemptions",         "kind": "list",
     "sources_key": "exemptions_sources",   "unverified_key": "exemptions_unverified"},
]
