# Цифровая модель территории

Research landing: модель приоритизации девелоперской земли (Marimo → static HTML).

## GitHub Pages

**https://kate25409.github.io/research-landing/**

Мобильная вёрстка и карты: скилл `marimo-html-export` (sidecar iframe вместо `data:` URI + `landing.css`).

## Пересборка Pages

```bash
# 1) экспорт (нужен локальный wibemaps file: в PEP 723)
uv run --with marimo marimo export html --sandbox --no-include-code -f \
  -o /tmp/nb_landing_export.html nb_landing.py

# 2) postprocess: data-URI → sidecar HTML + inject CSS
# --names: от короткого iframe к длинному
python ~/.cursor/skills/marimo-html-export/scripts/postprocess_pages.py \
  /tmp/nb_landing_export.html \
  --pages-dir docs \
  --site-prefix /research-landing \
  --css landing.css \
  --names sandbox.html,parcel-b.html,parcel-a.html,map.html

git add docs && git commit -m "Update Pages export" && git push
```

Локальный просмотр ноутбука:

```bash
uv run --with marimo marimo run --sandbox nb_landing.py
```
