# Цифровая модель территории

Research landing: модель приоритизации девелоперской земли (Marimo → static HTML).

## GitHub Pages

**https://kate25409.github.io/research-landing/**

Пересборка HTML:

```bash
uv run --with marimo marimo export html --sandbox --no-include-code -f -o docs/index.html nb_landing.py
cp landing.css docs/landing.css
```

Локальный просмотр ноутбука:

```bash
uv run --with marimo marimo run --sandbox nb_landing.py
```
