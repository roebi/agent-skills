---
name: create-privacy-policy-ch-en
license: CC BY-NC-SA 4.0
description: >
  Creates a Swiss-law-compliant Datenschutzerklärung (Privacy Policy) for
  websites operated from Switzerland or targeting Swiss users. Guides the user
  through an interactive data-inventory phase covering all processing activities
  (hosting, fonts, analytics, contact forms, cookies, external embeds, etc.),
  then generates a ready-to-publish Privacy Policy in German and/or English.
  Covers obligations under nDSG (in force 01.09.2023), DSG Art. 19, and where
  relevant DSGVO (for EU visitors). Activate for phrases like: "create a privacy
  policy", "Datenschutzerklärung erstellen", "I need a privacy policy for my
  Swiss website", "nDSG privacy policy", "DSGVO Datenschutz",
  or "create privacy policy switzerland".
metadata:
  author: roebi
  spec: https://agentskills.io/specification
  skill-class: one-step-process
  crud-verb: create
  topic: privacy-policy-ch
  language: en
  jurisdiction: CH
  legal-basis: nDSG Art. 19, DSG, DSGVO (where applicable)
  related-skill: create-impressum-ch-en
---

# Create Privacy Policy CH

Generates a Swiss-law-compliant Datenschutzerklärung for a website, following
the revised nDSG (in force since 01.09.2023) and, where the site targets EU
visitors, the DSGVO (GDPR).

> **Disclaimer:** This skill produces a best-effort legal text based on your
> inputs. It is not a substitute for advice from a Swiss lawyer. For commercial
> operations or sites processing sensitive data, review with a legal professional.

---

## Swiss legal basis (quick reference)

| Law | Relevance |
|-----|-----------|
| **nDSG Art. 19** | Duty to inform data subjects at time of collection |
| **nDSG Art. 5 lit. j** | Definition of data controller (Verantwortlicher) |
| **DSGVO Art. 13/14** | Applies if site targets EU residents — stricter than nDSG |
| **DSG Art. 12** | Prohibition of unlawful data processing |

---

## Phase 1 — Operator identity

Ask the user:

> "Do you already have an Impressum for this website created with
> `create-impressum-ch-en`? If yes, I can reuse the identity data directly."

If yes → import: `name-full` / `company-name`, `address`, `email`, `website-url`
If no → collect same fields as Group B of `create-impressum-ch-en`

---

## Phase 2 — Data processing inventory

Ask each group separately. Wait for answers before proceeding.

### Group A — Hosting & infrastructure

> "Where is your website hosted?"
> Examples: GitHub Pages, Netlify, Vercel, Hostpoint, AWS, own server

Store as `hosting-provider` and `hosting-location` (country/region if known).

GitHub Pages note: hosted on GitHub (Microsoft) servers, primarily USA.
Netlify note: USA. Vercel note: USA. Swiss hosters: Hostpoint, Cyon = CH.

---

### Group B — Web fonts

> "Does your website load fonts from an external CDN?"
> Examples: Google Fonts, Adobe Fonts, Bunny Fonts, or self-hosted

**Google Fonts loaded via `<link>` tag (standard):**
- Transfers visitor IP address to Google servers (USA) on every page load
- Google privacy policy: https://policies.google.com/privacy
- Basis: legitimate interest (Art. 6 DSGVO) / nDSG Art. 19
- Mitigation option: self-host fonts (no external request)

Store as `fonts-provider`: `google-fonts` | `adobe-fonts` | `bunny-fonts` |
`self-hosted` | `none`

---

### Group C — Analytics & tracking

> "Does your website use any analytics or tracking tools?"
> Examples: Google Analytics, Plausible, Fathom, Matomo, none

| Tool | Data sent to | Cookies | Privacy-friendly |
|------|-------------|---------|-----------------|
| Google Analytics | Google (USA) | yes | no |
| Plausible | EU servers | no | yes |
| Fathom | EU/CA | no | yes |
| Matomo (self-hosted) | own server | optional | yes |
| None | — | — | ✓ |

Store as `analytics-tool` and `analytics-cookies`: yes | no | none

---

### Group D — Contact & forms

> "How can visitors contact you? Does the site have any forms?"
> Examples: email link only, contact form, newsletter signup

| Type | Data collected | Storage |
|------|---------------|---------|
| Email link (mailto:) | none by the site | n/a |
| Contact form | name, email, message | server/email |
| Newsletter | email address | mailing list provider |

Store as `contact-method`: `email-only` | `contact-form` | `newsletter` | `none`
If form/newsletter: store `form-provider` (e.g. Formspree, Netlify Forms, Mailchimp)

---

### Group E — External embeds & third-party services

> "Does your website embed or link to any external services that load
> resources from third-party servers?"
> Examples: YouTube videos, Vimeo, Google Maps, Claude / AI links,
> social media buttons, GitHub badges, CDN scripts

Each embed that loads external resources must be disclosed.
Claude.ai links (claude.ai/new?q=...) are regular hyperlinks — no data transfer
from your server, user clicks voluntarily → no disclosure needed.
cdnjs.cloudflare.com scripts → disclose Cloudflare CDN.

Store as `embeds[]`: list of services

---

### Group F — Cookies

> "Does your website set any cookies?"

Purely informational static sites with no analytics and no forms typically
set zero cookies. Confirm:
- No analytics → no tracking cookies
- No login → no session cookies
- No consent tool → no consent cookies

Store as `uses-cookies`: yes | no
If yes: list name, purpose, duration, provider for each cookie.

---

### Group G — EU visitors

> "Does your website intentionally target visitors in the EU
> (e.g. German, French, Italian, Austrian audience)?"

If yes → DSGVO Art. 13 disclosure obligations apply in addition to nDSG.
The generated policy will include DSGVO-compatible language.

Store as `targets-eu`: yes | no | unsure (treat as yes if unsure)

---

### Group H — Language preference

> "Should the Privacy Policy be in German only, English only,
> or both languages?"

Store as `output-language`: `de` | `en` | `both`

---

## Phase 3 — Generate Privacy Policy

Using collected data, generate the policy using the templates in
`references/template-de.md` and/or `references/template-en.md`.

### Generation rules

- Include only sections relevant to the actual processing activities found.
- Do not include boilerplate sections for tools/services the site does not use.
- Mark any missing data with `[bitte ergänzen]` / `[please add]`.
- For Google Fonts: always mention IP transfer to Google USA and link to
  Google Privacy Policy.
- For GitHub Pages hosting: mention Microsoft/GitHub as processor, USA transfer.
- If `uses-cookies` = no: include a short "No cookies" statement — users
  appreciate explicit confirmation.
- If `targets-eu` = yes: add DSGVO Art. 13 rights block (access, erasure,
  portability, objection, supervisory authority).

---

## Phase 4 — Deliver and advise

1. Present the generated Privacy Policy.
2. List any `[bitte ergänzen]` fields as a checklist.
3. Remind the user:
   > "Place this at `/datenschutz` or `/privacy` reachable within one click
   > from every page. Link it from your footer next to the Impressum."
4. Mitigation tip for Google Fonts:
   > "To avoid disclosing Google Fonts IP transfers entirely, self-host your
   > fonts. Download from https://google-webfonts-helper.herokuapp.com and
   > serve from your own domain. Then remove the Google Fonts `<link>` tag."

---

## Reference files

- `references/template-de.md` — German Datenschutzerklärung template
- `references/template-en.md` — English Privacy Policy template
- `references/processing-activities.md` — Standard descriptions for common
  processing activities (hosting, fonts, analytics, forms)
- `references/rights-blocks.md` — nDSG and DSGVO data subject rights blocks
