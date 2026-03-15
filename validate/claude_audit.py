"""
Web-search-augmented Claude accuracy audit.
Uses Brave Search API to fetch current information, then asks Claude to compare
it against the stored YAML — treating Claude as a structured comparison engine,
not a knowledge oracle.
"""

import json
import os
import urllib.request
import urllib.parse
import urllib.error
from typing import Any, Dict, List, Optional, Tuple

import anthropic

BRAVE_SEARCH_ENDPOINT = "https://api.search.brave.com/res/v1/web/search"
BRAVE_API_KEY_ENV = "BRAVE_SEARCH_API_KEY"
ANTHROPIC_MODEL = "claude-haiku-4-5-20251001"

# Fields the accuracy audit checks
AUDIT_FIELDS = [
    "visa_type",
    "visa_difficulty",
    "max_stay",
    "requirements.visa_fee_inr",
    "requirements.processing_days",
    "authority.official_portal",
    "health.vaccinations",
    "health.insurance",
]

WEB_SEARCH_TIMEOUT = 5  # seconds


def _get_nested(data: dict, dotted_key: str, default=None):
    """Access 'requirements.visa_fee_inr' style keys."""
    parts = dotted_key.split(".")
    cur = data
    for p in parts:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(p, default)
        if cur is None:
            return default
    return cur


# ── Web search ────────────────────────────────────────────────────────────────

def _brave_search(query: str, api_key: str) -> str:
    """
    Run a Brave Search query and return concatenated snippet text (max 2000 chars).
    Returns empty string on any failure.
    """
    params = urllib.parse.urlencode({"q": query, "count": 5})
    url = f"{BRAVE_SEARCH_ENDPOINT}?{params}"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": api_key,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=WEB_SEARCH_TIMEOUT) as resp:
            body = resp.read()
            # Handle gzip
            content_encoding = resp.getheader("Content-Encoding", "")
            if content_encoding == "gzip":
                import gzip
                body = gzip.decompress(body)
            data = json.loads(body.decode("utf-8"))
    except Exception:
        return ""

    snippets = []
    for result in data.get("web", {}).get("results", []):
        title = result.get("title", "")
        desc  = result.get("description", "")
        url_r = result.get("url", "")
        snippets.append(f"[{title}] ({url_r})\n{desc}")

    return "\n\n".join(snippets)[:2000]


def _fetch_portal(url: str) -> str:
    """
    Best-effort HTTP GET of a URL, stripping HTML tags.
    Returns empty string on failure or bot-block (non-200).
    """
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=WEB_SEARCH_TIMEOUT) as resp:
            if resp.status != 200:
                return ""
            raw = resp.read(32768).decode("utf-8", errors="replace")
    except Exception:
        return ""

    # Strip tags with stdlib html.parser
    from html.parser import HTMLParser

    class TextExtractor(HTMLParser):
        def __init__(self):
            super().__init__()
            self._skip = False
            self.chunks: List[str] = []

        def handle_starttag(self, tag, attrs):
            if tag in ("script", "style", "nav", "footer", "header"):
                self._skip = True

        def handle_endtag(self, tag):
            if tag in ("script", "style", "nav", "footer", "header"):
                self._skip = False

        def handle_data(self, data):
            if not self._skip:
                text = data.strip()
                if text:
                    self.chunks.append(text)

    extractor = TextExtractor()
    extractor.feed(raw)
    return " ".join(extractor.chunks)[:2000]


def fetch_web_context(country_data: dict, brave_api_key: Optional[str]) -> Tuple[str, bool]:
    """
    Gather web context for a country entry.
    Returns (context_text, web_search_used).
    """
    if not brave_api_key:
        return "", False

    country = country_data.get("country", "")
    year = 2025  # Use a fixed recent year for search queries

    portal = _get_nested(country_data, "authority.official_portal") or ""
    portal_domain = urllib.parse.urlparse(portal).netloc if portal else ""

    # Query 1: targeted
    q1 = (
        f"{country} visa requirements Indian passport {year} "
        f"site:mea.gov.in OR site:{portal_domain}"
        if portal_domain else
        f"{country} visa requirements Indian passport {year} site:mea.gov.in"
    )
    text1 = _brave_search(q1, brave_api_key)

    # Query 2: portal page directly
    text2 = _fetch_portal(portal) if portal else ""

    # Query 3: fallback
    q3 = f"{country} visa fee processing time Indian passport {year}"
    text3 = _brave_search(q3, brave_api_key)

    combined = "\n\n---\n\n".join(t for t in [text1, text2, text3] if t)
    return combined[:4000], True


# ── Claude prompt ─────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """\
You are a visa information accuracy auditor for Indian passport holders.
You will be given the current data stored in a database and recent information
fetched from the web. Your job is to assess how accurate each field is.

Prefer the web context over your training data when they conflict.
If the web context is empty or irrelevant to a field, assess based on your
training data and mark source as "training".

Respond ONLY with valid JSON — no prose, no markdown fences.\
"""

_USER_PROMPT_TEMPLATE = """\
Current data in our database:
{yaml_content}

Recent information from the web (may be partial or noisy):
{web_context}

Assess each of these fields: {fields}

Respond ONLY with JSON in this exact format:
{{
  "country": "...",
  "checks": [
    {{
      "field": "requirements.visa_fee_inr",
      "stored_value": "...",
      "assessment": "PLAUSIBLE|SUSPECT|OUTDATED|UNKNOWN",
      "confidence": "HIGH|MEDIUM|LOW",
      "note": "one sentence or null",
      "source": "web|training|both"
    }}
  ],
  "overall_confidence": "HIGH|MEDIUM|LOW",
  "critical_flags": ["..."]
}}\
"""


def audit_country(
    country_data: dict,
    yaml_content: str,
    brave_api_key: Optional[str],
    anthropic_client: anthropic.Anthropic,
) -> dict:
    """
    Run a full accuracy audit for one country.
    Returns the parsed JSON response dict (or an error dict).
    """
    web_context, web_used = fetch_web_context(country_data, brave_api_key)

    user_prompt = _USER_PROMPT_TEMPLATE.format(
        yaml_content=yaml_content,
        web_context=web_context if web_context else "(no web context available)",
        fields=", ".join(AUDIT_FIELDS),
    )

    try:
        response = anthropic_client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=1024,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        raw_text = response.content[0].text.strip()

        # Strip markdown fences if model wrapped in them anyway
        if raw_text.startswith("```"):
            lines = raw_text.split("\n")
            raw_text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

        result = json.loads(raw_text)
        result["_web_search_used"] = web_used
        return result

    except json.JSONDecodeError as exc:
        return {
            "country": country_data.get("country", "Unknown"),
            "error": f"JSON decode error: {exc}",
            "raw": raw_text if "raw_text" in dir() else "",
            "_web_search_used": web_used,
        }
    except Exception as exc:
        return {
            "country": country_data.get("country", "Unknown"),
            "error": str(exc),
            "_web_search_used": web_used,
        }
