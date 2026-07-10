# How to Correct Visa Data

Thank you for helping keep Project Atlas accurate. This guide walks you through fixing incorrect data in under 2 minutes — no coding knowledge required.

---

## The Golden Rule

> All factual changes must be backed by an official source (embassy website, government circular, or consulate portal). **PRs without a citation link will be closed.**

---

## Step-by-Step: Correcting a Fact

### 1. Find the error on the page

Visit the country's visa page on the site and identify the incorrect field (e.g. the wrong visa fee).

### 2. Click "Edit this page"

On the top-right of every country page, there is a **pencil (✏️) icon**. Click it. You will be taken directly to the raw data file for that country on GitHub (e.g. `data/visas/japan.yaml`).

> You do not need to understand the full file. Simply find the field that is wrong (e.g. `visa_fee_inr: 500`) and correct it.

### 3. Propose the change

After editing, scroll down and click **"Propose changes"**. Then click **"Create pull request"**.

### 4. Fill in the PR template

You will see a form asking for:
- **What you changed** — a brief description (e.g. "Updated Japan visa fee from ₹500 to ₹800")
- **Citation URL** — the link to the official embassy or government page that confirms the new data

### 5. Submit and wait

Once submitted, the **project maintainer will review your PR**, verify the citation, and merge it. The live site will automatically update once approved.

---

## Bonus: cite your source in the data itself

Beyond the citation URL in your PR, you can attach the source to the exact fact block so the page
shows it. Most fact blocks (`requirements`, `health`, each visa type, `transit`, etc.) accept a
`sources` list:

```yaml
requirements:
  visa_fee_inr: 9800
  sources:
    - url: https://official-portal.example/fees   # deep link, not a homepage
      tier: 1            # 1 = government/embassy · 2 = VFS/BLS/TLScontact · 3 = verified secondary
      label: "Embassy of X — fee schedule"
      accessed: "2026-07-10"   # the date you actually checked it
```

If you genuinely can't find an official source, add `unverified: true` to the block instead — that's
honest, and it shows readers the fact needs confirmation. `python validate.py` checks the shape.

## What You Should NOT Edit

- Files in `docs/` (these are auto-generated)
- `gen_pages.py`, `mkdocs.yml`, or any file in `templates/`
- Any file outside of `data/visas/`

Edits to any of these files will be closed without review.
