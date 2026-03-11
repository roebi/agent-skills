---
name: translate-skill-de
description: >
  Übersetzt einen bestehenden Agent Skill (SKILL.md und alle gebündelten Dateien)
  von einer natürlichen Sprache in eine andere. Der übersetzte Skill wird auf
  Deutsch verfasst und als UTF-8 gespeichert. Diesen Skill verwenden, wenn ein
  Benutzer einen Skill übersetzen, in eine andere Sprache portieren oder für
  Sprecher einer anderen Sprache zugänglich machen möchte. Aktivieren bei
  Phrasen wie: "Skill übersetzen", "Skill von X nach Y übersetzen",
  "deutsche Version dieses Skills erstellen", "Skill ins Französische
  portieren", "Sprachvariante erstellen" oder "SKILL.md übersetzen".
compatibility: >
  Erfordert Lesezugriff auf das Quell-Skill-Verzeichnis oder eine Raw-URL.
  Ausgabe ist UTF-8-kodiert. Keine zusätzlichen Binärdateien erforderlich.
metadata:
  author: roebi-inspired
  spec: https://agentskills.io/specification
  instruction-language: de
  encoding: utf-8
---

# Skill übersetzen — Anleitung auf Deutsch, UTF-8-Ausgabe

Übersetzt einen bestehenden Agent Skill von **Sprache A** nach **Sprache B**.
Alle Anweisungen in diesem Skill sind auf Deutsch verfasst. Ausgabedateien sind UTF-8.

---

## Wann dieser Skill verwendet wird

- Benutzer stellt eine SKILL.md bereit (als Datei, URL oder eingefügter Text) und gibt eine Zielsprache an
- Benutzer möchte eine Sprachvariante eines bestehenden Skills
- Benutzer möchte, dass Nicht-Deutschsprachige von einem bestehenden Skill profitieren
- Benutzer möchte `translate-skill-<lang>-utf8`-Varianten dieses Skills erstellen

---

## Was übersetzt wird

| Element | Aktion |
|---------|--------|
| `SKILL.md` Frontmatter `description` | In Zielsprache übersetzen |
| `SKILL.md` Body (Prosa, Überschriften, Notizen) | In Zielsprache übersetzen |
| `references/*.md`-Dateien | Jede Datei übersetzen |
| Kommentare und `--help`-Text in `scripts/` | Inline-Kommentare und Hilfestrings übersetzen |
| Textdateien in `assets/` | Übersetzen, falls Klartext |
| Frontmatter-Feld `name` | **Nicht übersetzen** — Original-Slug beibehalten |
| Code-Logik / Variablennamen | **Nicht übersetzen** — nur Kommentare übersetzen |

---

## Schritt-für-Schritt-Workflow

### Schritt 1 — Quelle identifizieren

- Akzeptiert: Dateipfad, Raw-GitHub-URL oder eingefügten SKILL.md-Inhalt
- Bei URL: mit `web_fetch` abrufen
- Alle gebündelten Dateien in `references/`, `scripts/`, `assets/` lesen, falls vorhanden

### Schritt 2 — Parameter bestätigen

Fragen (oder aus Kontext ableiten):
1. **Quellsprache** — in welcher Sprache ist der Skill aktuell verfasst?
2. **Zielsprache** — in welche Sprache soll die Ausgabe übersetzt werden?
3. **Name des Ausgabe-Skills** — Standard: `-<lang-code>-utf8` an Originalnamen anhängen
   - Beispiel: `translate-skill-en` → `translate-skill-de`
4. **Ausgabeort** — wohin soll das übersetzte Skill-Verzeichnis geschrieben werden?

### Schritt 3 — SKILL.md übersetzen

Regeln:
- Alle YAML-Frontmatter-Schlüssel exakt beibehalten
- `description`-Wert vollständig in die Zielsprache übersetzen
- `metadata.instruction-language` auf den Zielsprachcode aktualisieren
- `metadata.encoding: utf-8` beibehalten
- Gesamten Prosa-Text im Body übersetzen
- Alle Code-Blöcke, Dateipfade, URLs und Befehlsbeispiele **unverändert lassen**
- Feld `name` **unverändert lassen**

### Schritt 4 — Gebündelte Dateien übersetzen

Für jede Datei in `references/`, `scripts/`, `assets/`:
- Prosa, Kommentare, Hilfetext übersetzen
- Code-Logik, Variablennamen, Befehlssyntax unverändert lassen
- Mit identischem Dateinamen im übersetzten Skill-Verzeichnis speichern

### Schritt 5 — Ausgabe schreiben

Übersetztes Skill-Verzeichnis erstellen:
```
<übersetzter-skill-name>/
├── SKILL.md              # übersetzt
├── references/           # übersetzt (falls vorhanden)
├── scripts/              # übersetzte Kommentare (falls vorhanden)
└── assets/               # übersetzte Text-Assets (falls vorhanden)
```

Alle Dateien als **UTF-8** speichern.

### Schritt 6 — Validieren

Prüfen:
- [ ] Feld `name` unverändert
- [ ] Keine unübersetzten Prosa-Passagen im SKILL.md-Body
- [ ] Code-Blöcke intakt
- [ ] UTF-8-Kodierung bestätigt (besonders bei nicht-lateinischen Schriften)
- [ ] `metadata.instruction-language` aktualisiert

### Schritt 7 — Präsentieren

Übersetztes Skill-Verzeichnis zum Download bereitstellen.
Kurze Zusammenfassung: Quellsprache → Zielsprache, übersetzte Dateien,
mehrdeutige Begriffe, die in der Quellsprache belassen wurden (mit Hinweis).

---

## Hinweise zur Übersetzungsqualität

- **Natürliche Formulierungen bevorzugen** statt wörtlicher Übersetzung
- **Technische Begriffe** (z. B. „Skill", „Agent", „SKILL.md", „Frontmatter") dürfen
  auf Englisch belassen werden, wenn kein natürliches Äquivalent existiert — kurzen
  Hinweis in Klammern hinzufügen
- **Trigger-Phrasen** in der `description` sollen sich für Muttersprachler der
  Zielsprache natürlich anfühlen — idiomatisch umformulieren
- **UTF-8-Hinweis**: Alle Zielsprachen, einschließlich solcher mit nicht-lateinischen
  Schriften (Japanisch, Arabisch, Chinesisch usw.), werden über UTF-8-Kodierung unterstützt

---

## Beispiel-Aufrufe

```
"Diesen Skill ins Deutsche übersetzen"
→ Quelle: en, Ziel: de, Ausgabename: <original>-de-utf8

"Französische Version von translate-skill-en erstellen"
→ Quelle: en, Ziel: fr, Ausgabename: translate-skill-fr-utf8

"Diese SKILL.md ins Japanische portieren"
→ Quelle: en, Ziel: ja, Ausgabename: <original>-ja-utf8
```

---

## Selbst-Anwendung: Sprachvarianten dieses Skills erstellen

Dieser Skill kann sich selbst übersetzen. Um `translate-skill-en` zu erstellen:
1. `translate-skill-de` als Quelle verwenden
2. Zielsprache festlegen: Englisch (`en`)
3. Ausgabename: `translate-skill-en`
4. Der resultierende Skill ist funktional identisch, aber alle Anweisungen sind auf Englisch

---

*Dieser Skill folgt der [agentskills.io Open-Spezifikation](https://agentskills.io/specification).*
