---
name: create-impressum-ch-en
license: CC BY-NC-SA 4.0
description: >
  Creates a Swiss-law-compliant Impressum (legal notice / Anbieterkennzeichnung)
  for websites operated from Switzerland or targeting Swiss users. Guides the user
  through an interactive data-collection phase, then generates a ready-to-publish
  Impressum in both German and English. Covers obligations under UWG Art. 3,
  nDSG, and OR. Activate for phrases like: "create an impressum", "I need a
  legal notice for my Swiss website", "Impressum for .ch or .dev domain",
  "Swiss website legal page", or "create impressum switzerland".
metadata:
  author: roebi
  spec: https://agentskills.io/specification
  skill-class: one-step-process
  crud-verb: create
  topic: impressum-ch
  language: en
  jurisdiction: CH
  legal-basis: UWG Art. 3 lit. s, nDSG, OR
---

# Create Impressum CH

Generates a Swiss-law-compliant Impressum for a website, following UWG Art. 3,
nDSG (revised Data Protection Act, in force since 01.09.2023), and OR obligations.

> **Disclaimer:** This skill produces a best-effort legal text based on your
> inputs. It is not a substitute for advice from a Swiss lawyer (Rechtsanwalt /
> Anwalt). For commercial operations, review the output with a legal professional.

---

## Swiss legal basis (quick reference)

| Law | Relevance |
|-----|-----------|
| **UWG Art. 3 lit. s** | Prohibits misleading omission of identity — website operators must be identifiable |
| **nDSG** (in force 01.09.2023) | Requires identification of the data controller |
| **OR (Obligationenrecht)** | Commercial entities must show company name, legal form, registered address |
| **MWSTG** | VAT number required if VAT-registered |

---

## Phase 1 — Interactive data collection

Ask the user the following questions **one group at a time**. Wait for answers
before proceeding to the next group. Mark optional fields clearly.

### Group A — Operator type

> "Is the website operated by a **private individual** or a **legal entity**
> (GmbH, AG, Verein, Stiftung, Einzelunternehmen, etc.)?"

Store answer as `operator-type`: `individual` | `legal-entity`

---

### Group B — Identity

**If `individual`:**

1. First name and last name (`name-full`)
2. Street address, postal code, city, canton (`address`)
3. Email address (`email`)
4. Phone number — *optional* (`phone`)

**If `legal-entity`:**

1. Company name as registered (`company-name`)
2. Legal form — GmbH / AG / Verein / Stiftung / Einzelunternehmen / other (`legal-form`)
3. Registered address (street, postal code, city, canton) (`address`)
4. UID (Unternehmens-Identifikationsnummer, format CHE-xxx.xxx.xxx) — *optional if not yet registered* (`uid`)
5. Commercial register canton + HR number — *optional* (`handelsregister`)
6. Name of responsible person / managing director (`responsible-person`)
7. Email address (`email`)
8. Phone number — *optional* (`phone`)

---

### Group C — Website details

1. Website URL(s) covered by this Impressum (`website-url`)
2. Purpose / content of the website — one sentence (`website-purpose`)
3. Is the site commercial (sells goods/services)? yes / no (`is-commercial`)

---

### Group D — VAT (only if `is-commercial` = yes)

> "Is the operator VAT-registered (MWST-pflichtig)?"

If yes: ask for MWST-Nummer (format CHE-xxx.xxx.xxx MWST) (`vat-number`)

---

### Group E — Dispute resolution & liability

> "Do you want to include a standard disclaimer clause for external links
> and a note about EU Online Dispute Resolution (ODR)? (Recommended: yes)"

Store as `include-disclaimer`: yes | no
Store as `include-odr`: yes | no

---

### Group F — Language preference for output

> "Should the Impressum be generated in **German only**, **English only**,
> or **both languages** (recommended for .dev / international domains)?"

Store as `output-language`: `de` | `en` | `both`

---

## Phase 2 — Generate Impressum

Using the collected data, generate the Impressum using the templates in
`references/template-de.md` and/or `references/template-en.md`.

### Generation rules

- Fill all collected fields into the template.
- Mark any missing optional fields with `[bitte ergänzen]` / `[please add]`
  so the user knows what still needs to be filled in manually.
- For `legal-entity`: always show UID if provided.
- For `legal-entity`: always show Handelsregister entry if provided.
- If `include-disclaimer` = yes: append the standard disclaimer block.
- If `include-odr` = yes: append the ODR link block.
- Output as a clean Markdown file ready to save as `impressum.md` or
  embed in an HTML page.

---

## Phase 3 — Deliver and advise

1. Present the generated Impressum to the user.
2. List any fields marked `[bitte ergänzen]` / `[please add]` as a checklist.
3. Remind the user:
   > "Place this Impressum on a page reachable within **one click** from your
   > homepage (e.g. `/impressum`). Swiss and EU practice requires it to be
   > easily findable. Link it from your footer."
4. Suggest next step:
   > "Consider also creating a **Datenschutzerklärung** (Privacy Policy) using
   > the `create-privacy-policy-ch-en` skill."

---

## Reference files

- `references/template-de.md` — German Impressum template with all fields
- `references/template-en.md` — English legal notice template with all fields
- `references/legal-notes.md` — Extended notes on UWG, nDSG, and OR obligations
