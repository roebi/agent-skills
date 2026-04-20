# Tree Patterns Reference

Curated directory + file tree patterns for common topic types.
Load this file when the topic fits one of the archetypes below.

---

## Python CLI tool

```
<topic>/
├── README.md
├── src/
│   └── <topic>/
│       ├── __init__.py
│       └── main.py
├── tests/
│   └── placeholder.txt
├── docs/
│   └── placeholder.txt
├── pyproject.toml
└── .gitignore
```

License: MIT

---

## Python library / package

```
<topic>/
├── README.md
├── src/
│   └── <topic>/
│       ├── __init__.py
│       └── placeholder.txt
├── tests/
│   ├── __init__.py
│   └── placeholder.txt
├── docs/
│   └── placeholder.txt
├── pyproject.toml
├── CHANGELOG.md
└── .gitignore
```

License: MIT

---

## Agent skill collection

```
<topic>/
├── README.md
├── skills/
│   └── placeholder.txt
├── references/
│   └── placeholder.txt
└── assets/
    └── placeholder.txt
```

License: CC BY-NC-SA 4.0

---

## Web frontend (HTML/JS/CSS)

```
<topic>/
├── README.md
├── src/
│   ├── index.html
│   ├── style.css
│   └── main.js
├── assets/
│   └── placeholder.txt
├── tests/
│   └── placeholder.txt
└── .gitignore
```

License: MIT

---

## React / Node project

```
<topic>/
├── README.md
├── src/
│   └── placeholder.txt
├── public/
│   └── placeholder.txt
├── tests/
│   └── placeholder.txt
├── package.json
└── .gitignore
```

License: MIT

---

## Documentation / methodology

```
<topic>/
├── README.md
├── docs/
│   └── placeholder.txt
├── examples/
│   └── placeholder.txt
└── assets/
    └── placeholder.txt
```

License: CC BY-NC-SA 4.0

---

## Generic software project (fallback)

```
<topic>/
├── README.md
├── src/
│   └── placeholder.txt
├── tests/
│   └── placeholder.txt
├── docs/
│   └── placeholder.txt
└── .gitignore
```

License: MIT

---

## Selection guide

| Topic signals                            | Pattern to use              |
|------------------------------------------|-----------------------------|
| "python", "cli", "typer", "script"       | Python CLI tool             |
| "library", "package", "pip", "pypi"      | Python library              |
| "skills", "agent", "methodology"         | Agent skill collection      |
| "react", "node", "npm", "vite"           | React / Node project        |
| "html", "css", "vanilla js"              | Web frontend                |
| "docs", "guide", "course", "tutorial"   | Documentation / methodology |
| anything else                            | Generic software project    |
