# .gitignore Template for Python Projects

File: `.gitignore`

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
*.egg
*.egg-info/
dist/
build/
.eggs/
MANIFEST

# uv / virtual envs
.venv/
.python-version

# Testing & coverage
.pytest_cache/
.coverage
.coverage.*
coverage.xml
htmlcov/
*.log

# Type checkers
.mypy_cache/
.pyright/
.ruff_cache/

# Editors
.vscode/settings.json
.idea/
*.swp
*~
.DS_Store

# Secrets / local config
.env
.env.local
*.pem

# Distribution / packaging
*.whl
*.tar.gz
```
