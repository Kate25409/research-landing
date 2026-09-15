# /// script
#
# requires-python = ">=3.10"
# dependencies = [
#   "marimo",
#   "altair==6.2.2",
#   "pandas==3.0.5",
#   "numpy==2.5.2",
#   "geopandas==1.1.4",
#   "pyogrio",
#   # НЕ wibemaps==0.2.6: пакета нет на PyPI.
#   # Абсолютный file: — sandbox uv не резолвит относительный путь.
#   "wibemaps @ file:///Users/katerinasitnikova/Documents/work/wibemaps",
# ]
#
# [tool.marimo.runtime]
# output_max_bytes = 50_000_000
#
# [tool.marimo.opengraph]
# title = "Цифровая модель территории: как посчитать потенциал?"
# description = "Модель, которая сужает выборку земельных участков и делает правила приоритизации прозрачными"
# ///


import marimo

__generated_with = "0.18.4"
app = marimo.App(width="medium", css_file="landing.css")


# ─────────────────────────────────────────────────────────────────────────────
# Imports
# ─────────────────────────────────────────────────────────────────────────────


@app.cell(hide_code=True)
def _():
    import math
    from pathlib import Path

    import altair as alt
    import geopandas as gpd
    import marimo as mo
    import numpy as np
    import pandas as pd
    from wibemaps import CircleLayer, FillLayer, Map
    from wibemaps.components import Legend, Popup, Search
    from wibemaps.layers.tiles import TileProvider, get_tile_provider, register_tile_provider

    # Ч/б подложка: paint уходит в MapLibre только на raster-слой тайлов
    _y = get_tile_provider("yandex")
    register_tile_provider(
        TileProvider(
            name="yandex",
            url=_y.url,
            tile_size=_y.tile_size,
            min_zoom=_y.min_zoom,
            max_zoom=_y.max_zoom,
            attribution=_y.attribution,
            paint={"raster-saturation": -1},
        ),
        overwrite=True,
    )

    alt.data_transformers.disable_max_rows()
    DATA_DIR = Path(__file__).resolve().parent / "data"

    def embed_map(
        map_obj,
        height: int,
        title: str = "",
        chrome: bool = True,
        sidecar: str | None = None,
    ):
        # Dual-write: data: URI for Marimo live; sidecar .html for GitHub Pages
        # (iOS/Android blank-iframe fix — see skill marimo-html-export).
        import base64

        _html = map_obj.to_html().replace(
            "zoom: mapSettings.zoom\n                });",
            "zoom: mapSettings.zoom,\n                    cooperativeGestures: true\n                });",
        )
        if not chrome:
            _hide = (
                "<style>.address-search-container,.legend{display:none!important;}</style>"
            )
            if "</head>" in _html:
                _html = _html.replace("</head>", _hide + "</head>", 1)
            else:
                _html = _hide + _html
        _pages = Path(__file__).resolve().parent / "docs"
        if sidecar and _pages.is_dir():
            (_pages / sidecar).write_text(_html, encoding="utf-8")
        _encoded = base64.b64encode(_html.encode("utf-8")).decode("ascii")
        _title = title or "map"
        return mo.Html(
            f'<div style="width:100%;height:{height}px;overflow:hidden;'
            f'border:1px solid #e4e4e7;border-radius:4px;max-width:100%;">'
            f'<iframe src="data:text/html;base64,{_encoded}" title="{_title}" '
            f'style="width:100%;height:{height}px;border:0;display:block;"></iframe>'
            f"</div>"
        )

    def center_zoom(bounds, pad_mult: float = 2.0, min_pad: float = 0.004, width: int = 400, height: int = 220):
        minx, miny, maxx, maxy = bounds
        pad_x = max((maxx - minx) * pad_mult, min_pad)
        pad_y = max((maxy - miny) * pad_mult, min_pad * 0.75)
        lon_span = max((maxx - minx) + 2 * pad_x, 1e-6)
        lat_span = max((maxy - miny) + 2 * pad_y, 1e-6)
        center = [(minx + maxx) / 2, (miny + maxy) / 2]
        zx = math.log2(max(width * 360 / (lon_span * 256), 1))
        zy = math.log2(max(height * 360 / (lat_span * 256), 1))
        zoom = int(max(1, min(18, min(zx, zy))))
        return center, zoom

    return (
        DATA_DIR,
        CircleLayer,
        FillLayer,
        Legend,
        Map,
        Popup,
        Search,
        alt,
        center_zoom,
        embed_map,
        gpd,
        mo,
        np,
        pd,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Design system — Linear Data inspired
# ─────────────────────────────────────────────────────────────────────────────


@app.cell(hide_code=True)
def _(mo, alt):
    # Palette close to Linear research pages: near-mono + one soft indigo accent
    INK = "#18181b"
    MUTED = "#71717a"
    BAR_LIGHT = "#d4d4d8"
    BAR_MID = "#a1a1aa"
    ACCENT = "#1c32bd"
    GRID = "#f4f4f5"
    BORDER = "#e4e4e7"
    BG = "#ffffff"

    def apply_linear_theme():
        return {
            "config": {
                "view": {"stroke": "transparent", "continuousWidth": 520},
                "background": BG,
                "font": "Inter, system-ui, -apple-system, sans-serif",
                "axis": {
                    "domain": False,
                    "grid": True,
                    "gridColor": GRID,
                    "gridOpacity": 1,
                    "ticks": False,
                    "labelColor": MUTED,
                    "labelFontSize": 12,
                    "labelFontWeight": 400,
                    "titleColor": MUTED,
                    "titleFontSize": 11,
                    "titleFontWeight": 500,
                    "titlePadding": 12,
                },
                "axisX": {"grid": True, "labelPadding": 8},
                "axisY": {"grid": False, "labelPadding": 10},
                "legend": {
                    "labelColor": MUTED,
                    "labelFontSize": 12,
                    "title": None,
                    "orient": "bottom",
                    "padding": 12,
                    "symbolType": "square",
                    "symbolSize": 80,
                },
                "title": {
                    "color": INK,
                    "fontSize": 13,
                    "fontWeight": 500,
                    "anchor": "start",
                    "offset": 16,
                },
            }
        }

    alt.themes.register("linear_data", apply_linear_theme)
    alt.themes.enable("linear_data")

    def section_eyebrow(text: str):
        return mo.md(
            f'<div style="font-family:Inter,system-ui,sans-serif;font-size:0.75rem;'
            f'font-weight:500;letter-spacing:0.08em;text-transform:uppercase;'
            f'color:{MUTED};margin:0 0 0.75rem 0;">{text}</div>'
        )

    def section_heading(title: str):
        return mo.md(
            f'<h2 style="font-family:Inter,system-ui,sans-serif;font-weight:600;'
            f'font-size:2.1rem;line-height:1.15;letter-spacing:-0.03em;'
            f'color:{INK};margin:0 0 1rem 0;">{title}</h2>'
        )

    def body_text(html: str):
        return mo.md(
            f'<div style="max-width:640px;font-size:1.02rem;line-height:1.7;'
            f'color:#3f3f46;font-family:Inter,system-ui,sans-serif;">{html}</div>'
        )

    def chart_caption(text: str):
        return mo.md(
            f'<div style="max-width:640px;margin-top:0.75rem;font-size:0.8rem;'
            f'line-height:1.5;color:{MUTED};font-family:Inter,system-ui,sans-serif;">'
            f'{text}</div>'
        )

    def spacer(h: float = 4.0):
        return mo.md(f'<div style="height:{h}rem;"></div>')

    def divider():
        return mo.md(
            f'<div style="width:100%;max-width:640px;height:1px;background:{BORDER};'
            f'margin:0.5rem 0 1.75rem 0;"></div>'
        )

    def delta_pill(text: str, positive: bool = True):
        color = ACCENT if positive else MUTED
        return (
            f'<span style="display:inline-block;font-size:0.8rem;font-weight:600;'
            f'color:{color};letter-spacing:-0.01em;">{text}</span>'
        )

    def kpi_row(label: str, value: str, delta: str = ""):
        delta_html = (
            f'<div style="font-size:0.85rem;font-weight:600;color:{ACCENT};'
            f'margin-top:0.15rem;">{delta}</div>'
            if delta
            else ""
        )
        return mo.md(
            f'<div style="padding:0.9rem 0;border-bottom:1px solid {BORDER};'
            f'display:flex;justify-content:space-between;align-items:baseline;gap:1rem;'
            f'max-width:640px;">'
            f'<div style="font-size:0.95rem;color:#3f3f46;">{label}</div>'
            f'<div style="text-align:right;">'
            f'<div style="font-size:1.35rem;font-weight:600;color:{INK};'
            f'letter-spacing:-0.02em;">{value}</div>'
            f'{delta_html}</div></div>'
        )

    def deliverable_row(num: str, title: str, desc: str):
        return mo.md(
            f'<div style="display:flex;gap:1.25rem;padding:1.1rem 0;'
            f'border-bottom:1px solid {BORDER};max-width:640px;">'
            f'<div style="font-size:0.8rem;font-weight:600;color:{MUTED};'
            f'min-width:1.6rem;padding-top:0.15rem;">{num}</div>'
            f'<div>'
            f'<div style="font-weight:600;font-size:1rem;color:{INK};'
            f'margin-bottom:0.25rem;">{title}</div>'
            f'<div style="font-size:0.92rem;color:#52525b;line-height:1.55;">{desc}</div>'
            f'</div></div>'
        )

    return (
        INK, MUTED, BAR_LIGHT, BAR_MID, ACCENT, GRID, BORDER, BG,
        section_eyebrow, section_heading, body_text, chart_caption,
        spacer, divider, delta_pill, kpi_row, deliverable_row,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Hero: название и о чём страница
# ─────────────────────────────────────────────────────────────────────────────


@app.cell(hide_code=True)
def _(mo, section_heading, body_text, spacer, divider, MUTED, BORDER, INK, ACCENT, chart_caption):
    def _flow_box(title: str) -> str:
        return (
            f'<div style="flex:1;min-width:140px;padding:0.85rem 1rem;'
            f'border:1px solid {ACCENT};border-radius:10px;background:#fff;'
            f'font-size:0.9rem;font-weight:500;color:{INK};line-height:1.35;text-align:center;">'
            f"{title}</div>"
        )

    hero_diagram = mo.md(
        f'<div style="max-width:640px;padding:0.5rem 0 0.25rem 0;">'
        f'<div style="display:flex;flex-wrap:wrap;align-items:center;gap:0.65rem;">'
        f'{_flow_box("Data Governance")}'
        f'<div style="color:{ACCENT};font-size:1.1rem;flex-shrink:0;">→</div>'
        f'{_flow_box("Цифровая модель<br>определения потенциала")}'
        f'<div style="color:{ACCENT};font-size:1.1rem;flex-shrink:0;">→</div>'
        f'{_flow_box("AI-инструменты")}'
        f"</div></div>"
    )

    disclaimer = mo.md(
        f'<div style="max-width:640px;width:100%;box-sizing:border-box;'
        f"margin:0 0 1.75rem 0;padding:0.85rem 1rem;"
        f"border-left:3px solid {BORDER};"
        f'font-family:Inter,system-ui,sans-serif;font-size:0.88rem;line-height:1.55;'
        f'color:{MUTED};">'
        f"<strong style=\"color:{INK};font-weight:600;\">Дисклеймер.</strong> "
        f"На этой странице используются <em>открытые данные</em> и "
        f"<em>синтетические</em> значения вместо корпоративных атрибутов "
        f"(имена девелоперов, ценовые зоны и др.). "
        f"Геометрия и логика модели сохранены для иллюстрации метода."
        f"</div>"
    )

    mo.vstack(
        [
            spacer(4),
            disclaimer,
            mo.md(
                f'<div style="font-family:Inter,system-ui,sans-serif;font-size:0.75rem;'
                f'font-weight:500;letter-spacing:0.08em;text-transform:uppercase;'
                f'color:{MUTED};margin:0 0 0.75rem 0;">Что такое цифровая модель?</div>'
            ),
            section_heading("Цифровая модель территории:<br>как определить потенциал</br> и не пересобирать данные под задачи?"),
            divider(),
            body_text(
                "Когда вводные меняются быстро, команда снова и снова собирает данные по разрозненным реестрам — "
                "часто, это почти один и тот же набор данных, которые собираются под разные задачи. Эта страница про то, как формализовать "
                "правила отбора, собрать источники в одну модель и быстро пересчитывать приоритеты —"
                "плюс AI-слой для вопросов к уже готовым данным."
                
                "<br><br>"
                "<em>Принцип построения продукта</em>"
                
            ),
            spacer(1.2),
            hero_diagram,
            chart_caption(
                "Цепочка: сначала упорядоченные данные → потом правила и автоматизированный пересчет потенциала → финально: AI-инструменты."
                
            ),
            spacer(4),
        ],
        gap=0,
    )
    return


# ─────────────────────────────────────────────────────────────────────────────
# Beat 1: Узнаёшь ситуацию? — три боли (без карточек А/Б)
# ─────────────────────────────────────────────────────────────────────────────


@app.cell(hide_code=True)
def _(
    mo,
    section_eyebrow,
    section_heading,
    body_text,
    chart_caption,
    spacer,
    divider,
    deliverable_row,
):
    mo.vstack(
        [
            spacer(5),
            section_eyebrow("1 — Какие проблемы решаем?"),
            section_heading(
                "Три ситуации, в которых модель может помочь<br>"
                "ускорить и упорядочить работу"
            ),
            divider(),
            body_text(
                "Если хотя бы в один пункт кажется знакомым — дальше как раз про то, "
                "как можно работать с аналитикой системно и процедурно, а не собирать данные вручную каждый раз."
            ),
            spacer(0.8),
            deliverable_row(
                "01",
                "Вводные меняются быстрее чем специалист успевает собрать контекст и сделать аналитику",
                "Новый виток задачи — и снова ручной сбор по реестрам и источникам, "
                "чтобы понять, что сейчас актуально для территории.",
            ),
            deliverable_row(
                "02",
                "Одна и та же работа делается снова и снова, но под разные задачи",
                "Хочется автоматизировать повторяющийся разбор, но непонятно, как выстроить процесс "
                "и как формализовать правила работы с территорией.",
            ),
            deliverable_row(
                "03",
                "Приоритеты в головах людей,а не в документации",
                "Сложно передать логику работы коллегам, быстро пересчитать приоритеты при смене вводных рынка. ",
            ),
            spacer(1.0),
            chart_caption(
                "<em>Какие проблемы точно не решаем?</em></br> "
                "Модель не заменяет согласования с городом и юридическую экспертизу. "
                "Она даёт экспресс-понимание контекста участка и агрегирует данные: что на нём происходит, какие планы "
                "и ограничения видны в собранных данных. Уже поверх данных выстраиваются понятные команде правила приоритизации."
            ),
            spacer(4),
        ],
        gap=0,
    )
    return


# ─────────────────────────────────────────────────────────────────────────────
# Beat 2: Что значит потенциал участка — плашки с мини-картами реальных ЗУ
# ─────────────────────────────────────────────────────────────────────────────


@app.cell(hide_code=True)
def _(DATA_DIR, gpd, mo):
    _ex_path = DATA_DIR / "example_cards.gpkg"
    mo.stop(
        not _ex_path.exists(),
        mo.md(
            "Нет `data/example_cards.gpkg`. "
            "Пересоберите примеры участков (см. `prepare_map_data.py`)."
        ),
    )
    example_cards = gpd.read_file(_ex_path, layer="example_cards").to_crs(4326)
    return (example_cards,)


@app.cell(hide_code=True)
def _(
    ACCENT,
    BORDER,
    FillLayer,
    INK,
    MUTED,
    Map,
    body_text,
    center_zoom,
    divider,
    embed_map,
    example_cards,
    mo,
    section_eyebrow,
    section_heading,
    spacer,
):
    def _fmt_area(v):
        try:
            return f"{float(v):.2f}".replace(".", ",") + " Га"
        except Exception:
            return str(v)

    def _mini_map(
        gdf_one,
        color: str,
        pad_mult: float = 2.5,
        min_pad: float = 0.004,
        sidecar: str | None = None,
    ):
        map_h = 220
        _center, _zoom = center_zoom(
            gdf_one.total_bounds,
            pad_mult=pad_mult,
            min_pad=min_pad,
            width=400,
            height=map_h,
        )
        _m = Map(
            title="Участок",
            center=_center,
            zoom=_zoom,
            embedded=True,
            tile_provider="yandex",
        )
        _m.add_layer(
            FillLayer(
                name="parcel",
                source=gdf_one,
                style={
                    "colors": [color],
                    "opacity": 0.3,
                    "stroke_width": 2,
                    "stroke_color": color,
                },
            )
        )
        return embed_map(
            _m, map_h, title="Пример участка", chrome=False, sidecar=sidecar
        )

    def _plot_card(title: str, rows: list, reason: str, map_widget):
        rows_html = "".join(
            f'<div style="display:flex;justify-content:space-between;'
            f'padding:0.35rem 0;border-bottom:1px solid {BORDER};'
            f'font-size:0.88rem;"><span style="color:{MUTED};">{k}</span>'
            f'<span style="color:{INK};font-weight:500;">{v}</span></div>'
            for k, v in rows
        )
        meta = mo.md(
            f'<div style="padding:0.2rem 0;position:relative;z-index:1;'
            f'background:#fff;">'
            f'<div style="font-size:0.72rem;font-weight:600;letter-spacing:0.06em;'
            f'text-transform:uppercase;color:{MUTED};margin:0 0 0.25rem 0;">{title}</div>'
            f'<div style="font-size:0.85rem;font-weight:600;color:{ACCENT};'
            f'margin:0 0 0.35rem 0;">↓ низкий приоритет</div>'
            f'<div style="font-size:0.8rem;color:{MUTED};margin:0 0 0.75rem 0;'
            f'line-height:1.45;">{reason}</div>'
            f'{rows_html}'
            f"</div>"
        )
        return mo.vstack([map_widget, meta], gap=0.8).style(
            flex="1",
            min_width="260px",
            max_width="420px",
        )

    gdf_a = example_cards[example_cards["card_id"] == "A"]
    gdf_b = example_cards[example_cards["card_id"] == "B"]
    row_a = gdf_a.iloc[0]
    row_b = gdf_b.iloc[0]

    card_a = _plot_card(
        "Участок A · Хорошёво-Мнёвники",
        [
            ("КН", str(row_a.get("cadastral_number", "—"))),
            ("Площадь", _fmt_area(row_a.get("area_zu"))),
            ("Собственник", "ОАО «РЖД» / федеральный"),
            ("Фактическое землепользование", str(row_a.get("generated_land_use", "—"))),
            ("ВРИ", str(row_a.get("category_vri", "—"))),
            ("Приоритет модели", str(row_a.get("dev_prig_fin", "—"))),
        ],
        "причина: правообладание, с которым не умеем работать",
        _mini_map(gdf_a, ACCENT, sidecar="parcel-a.html"),
    )
    card_b = _plot_card(
        "Участок Б · Марьина Роща",
        [
            ("КН", str(row_b.get("cadastral_number", "—"))),
            ("Площадь", _fmt_area(row_b.get("area_zu"))),
            ("Собственник", "физическое лицо"),
            ("Фактическое землепользование", str(row_b.get("generated_land_use", "—"))),
            ("ВРИ", str(row_b.get("category_vri", "—"))),
            ("Приоритет модели", str(row_b.get("dev_prig_fin", "—"))),
        ],
        "причина: недостаточная площадь и невозможность расширить территорию рассмотрения",
        _mini_map(gdf_b, ACCENT, pad_mult=1.2, min_pad=0.0007, sidecar="parcel-b.html"),
    )

    mo.vstack(
        [
            spacer(5),
            section_eyebrow("2 — Что считаем потенциалом"),
            section_heading(
                "Что значит потенциал территории —<br>и почему это не про какой-то один параметр?"
            ),
            divider(),
            body_text(
                "Участков в городе много. Но реализуемых под определённую задачу — почти всегда единицы."
                "<br><br>"
                "Потенциал к развитию — это не про юридический статус, не про площадь участка. "
                "Это ответ на вопросы: можно ли здесь сделать проект, с кем придётся "
                "договариваться, какие ограничения непреодолимы прямо сейчас, "
                "а какие из них — рабочие риски? Это всегда про сочетание факторов. "
                "<br><br>"
                "Небольшой кейс: два реальных участка внутри МКАД — оба с низким приоритетом, "
                "но по разным причинам."
            ),
            spacer(1.8),
            mo.hstack([card_a, card_b], gap=2.0, wrap=True),
            spacer(4),
        ],
        gap=0,
    )
    return


# ─────────────────────────────────────────────────────────────────────────────
# Beat 3: Воронка отсева — Linear-style horizontal bars + end labels
# ─────────────────────────────────────────────────────────────────────────────


@app.cell(hide_code=True)
def _(
    mo, alt, pd, section_eyebrow, section_heading, body_text,
    chart_caption, spacer, divider, ACCENT, BAR_LIGHT, MUTED, INK,
):
    funnel = pd.DataFrame(
        {
            "stage": [
                "Участки на старте",
                "1 · Планы на ЗУ:\nгород и девелоперы",
                "2 · Правообладание",
                "3 · Землепользование:\nчто реально находится на ЗУ?",
                "4 · Площадь и форма ЗУ",
                "5 · Финальный этап:\nОграничения на ЗУ",
            ],
            "remaining": [1000, 820, 540, 280, 95, 80],
            "order": [0, 1, 2, 3, 4, 5],
            "delta": ["", "−18%", "−34%", "−48%", "−66%", "−16%"],
        }
    )
    funnel["pct"] = (funnel["remaining"] / 1000 * 100).round(0).astype(int)
    funnel["label"] = funnel["remaining"].astype(str) + "  ·  " + funnel["pct"].astype(str) + "%"

    _bars = (
        alt.Chart(funnel)
        .mark_bar(size=18)
        .encode(
            y=alt.Y(
                "stage:N",
                sort=alt.SortField("order"),
                title=None,
                axis=alt.Axis(
                    labelLimit=280,
                    labelFontSize=12,
                    labelColor=INK,
                    labelLineHeight=16,
                    labelExpr="split(datum.value, '\\n')",
                ),
            ),
            x=alt.X(
                "remaining:Q",
                title=None,
                scale=alt.Scale(domain=[0, 1200]),
                axis=alt.Axis(values=[0, 250, 500, 750, 1000], format="d"),
            ),
            color=alt.condition(
                alt.datum.order == 5,
                alt.value(ACCENT),
                alt.value(BAR_LIGHT),
            ),
            tooltip=[
                alt.Tooltip("stage:N", title="Этап"),
                alt.Tooltip("remaining:Q", title="Остаётся"),
                alt.Tooltip("pct:Q", title="% от старта"),
            ],
        )
    )
    _labels = (
        alt.Chart(funnel)
        .mark_text(align="left", dx=8, fontSize=12, fontWeight=500, color=MUTED)
        .encode(
            y=alt.Y("stage:N", sort=alt.SortField("order")),
            x="remaining:Q",
            text="label:N",
        )
    )
    funnel_chart = (_bars + _labels).properties(width=520, height=300)

    mo.vstack(
        [
            section_eyebrow("3 — Методика"),
            section_heading("Модель — не чёрный ящик:<br>правила, которые пользователь контролирует"),
            divider(),
            body_text(
                "Приоритизация — это набор формализованных правил через несколько этапов рассмотрения/отсева территорий. "
                "Каждый этап отвечает за свою группу факторов. Вместе они дают приоритет "
                "рассмотрения. Это не вердикт, а набор необходимых данных в одном месте и ранжирование на их основе."
                "<br><br>"
                "Если рынок меняется — правила адаптируются. Задаются новые параметры и на их основе происходит пересчёт за минуты (40 минут на территорию, сопоставимую с Москвой, если быть точнее). "
                "Переписывание аналитики с нуля больше не нужно."
            ),
            spacer(1.5),
            mo.as_html(funnel_chart),
            chart_caption(
                "Примерная конверсия отбора участков на сэмпле синтетических данных."
            
            ),
            spacer(4),
        ],
        gap=0,
    )
    return


# ─────────────────────────────────────────────────────────────────────────────
# Beat 3: За периметром — decision matrix по РЗП (нет / может быть / да)
# Стилистика: сетка выбора пути (ai-2040), не bar chart
# ─────────────────────────────────────────────────────────────────────────────


@app.cell(hide_code=True)
def _(
    mo, section_eyebrow, section_heading, body_text,
    chart_caption, spacer, divider, ACCENT, BAR_LIGHT, MUTED, INK, BORDER,
):
    # Вердикт модели по категории реального землепользования (синтетика для иллюстрации).
    # Колонки: нет = за периметром; может быть = условно; да = в активной выборке.
    rlu_matrix = [
        ("Существующее жильё (МКД)", "нет"),
        ("Парки / вода / ООПТ", "нет"),
        ("Транспорт / УДС", "нет"),
        ("Социальная инфраструктура", "нет"),
        ("Гаражи / низкая застройка", "может"),
        ("Открытый грунт / прочее", "может"),
        ("Нежилое с потенциалом", "может"),
        ("Свободный дев. ресурс", "да"),
    ]
    cols = [
        ("нет", "Точно нет"),
        ("может", "Может быть"),
        ("да", "Да"),
    ]

    def _cell(active: bool, kind: str) -> str:
        if not active:
            return (
                f'<td style="text-align:center;padding:0.65rem 0.4rem;'
                f'border-bottom:1px solid {BORDER};">'
                f'<span style="display:inline-block;width:0.55rem;height:0.55rem;'
                f'border-radius:999px;background:{BAR_LIGHT};opacity:0.55;"></span>'
                f"</td>"
            )
        if kind == "нет":
            fill, ink = BAR_LIGHT, MUTED
        elif kind == "может":
            fill, ink = "#c7d2fe", ACCENT  # soft indigo
        else:
            fill, ink = ACCENT, "#fff"
        return (
            f'<td style="text-align:center;padding:0.65rem 0.4rem;'
            f'border-bottom:1px solid {BORDER};">'
            f'<span style="display:inline-flex;align-items:center;justify-content:center;'
            f'min-width:1.55rem;height:1.55rem;border-radius:999px;'
            f'background:{fill};color:{ink};font-size:0.72rem;font-weight:600;">●</span>'
            f"</td>"
        )

    header = (
        f'<tr>'
        f'<th style="text-align:left;padding:0.5rem 0.75rem 0.75rem 0;'
        f'font-size:0.72rem;font-weight:600;letter-spacing:0.06em;'
        f'text-transform:uppercase;color:{MUTED};border-bottom:1px solid {BORDER};">'
        f"Категория РЗП</th>"
        + "".join(
            f'<th style="text-align:center;padding:0.5rem 0.4rem 0.75rem;'
            f'font-size:0.72rem;font-weight:600;letter-spacing:0.04em;'
            f'text-transform:uppercase;color:{MUTED};border-bottom:1px solid {BORDER};'
            f'min-width:5.5rem;">{label}</th>'
            for _, label in cols
        )
        + "</tr>"
    )
    rows_html = []
    for cat, verdict in rlu_matrix:
        cells = "".join(_cell(verdict == k, k) for k, _ in cols)
        rows_html.append(
            f'<tr>'
            f'<td style="padding:0.65rem 0.75rem 0.65rem 0;font-size:0.92rem;'
            f'font-weight:500;color:{INK};border-bottom:1px solid {BORDER};'
            f'max-width:14rem;">{cat}</td>'
            f"{cells}</tr>"
        )

    legend = (
        f'<div style="display:flex;flex-wrap:wrap;gap:1rem;margin-top:1rem;'
        f'font-size:0.8rem;color:{MUTED};">'
        f'<span><span style="display:inline-block;width:0.65rem;height:0.65rem;'
        f'border-radius:999px;background:{BAR_LIGHT};vertical-align:middle;'
        f'margin-right:0.35rem;"></span>за периметром</span>'
        f'<span><span style="display:inline-block;width:0.65rem;height:0.65rem;'
        f'border-radius:999px;background:#c7d2fe;vertical-align:middle;'
        f'margin-right:0.35rem;"></span>условно / с оговоркой</span>'
        f'<span><span style="display:inline-block;width:0.65rem;height:0.65rem;'
        f'border-radius:999px;background:{ACCENT};vertical-align:middle;'
        f'margin-right:0.35rem;"></span>в активной выборке</span>'
        f"</div>"
    )

    matrix_html = mo.Html(
        f'<div style="max-width:640px;padding:0.25rem 0 0.5rem;">'
        f'<table style="width:100%;border-collapse:collapse;'
        f'font-family:Inter,system-ui,sans-serif;">{header}'
        f"{''.join(rows_html)}</table>{legend}</div>"
    )

    mo.vstack(
        [
            section_eyebrow("4 — Границы"),
            section_heading("Что модель честно<br>оставляет за пределами рассмотрения"),
            divider(),
            body_text(
                "Важный шаг аналитики — отсечь ненужное как можно раньше. "
                "По категориям <strong>реального землепользования</strong> модель заранее "
                "фиксирует вердикт: <em>точно нет</em>, <em>может быть</em> или <em>да</em>. "
                "Жильё, вода, транспорт и охраняемое — не ресурс прямо сейчас; "
                "свободный и условный фонд остаётся в периметре активного рассмотрения."
            ),
            spacer(1.5),
            matrix_html,
            chart_caption(
                "Матрица политики по РЗП (синтетика для иллюстрации). "
                "Не доли площади, а решение: что модель принципиально не тащит в фокус."
            ),
            spacer(4),
        ],
        gap=0,
    )
    return


# ─────────────────────────────────────────────────────────────────────────────
# Beat 4: Pipeline — 3 уровня (ai-2040: равные чипы + ортогональные линии)
# ─────────────────────────────────────────────────────────────────────────────


@app.cell(hide_code=True)
def _(
    mo, section_eyebrow, section_heading, body_text, chart_caption,
    spacer, divider, BORDER, MUTED, INK, ACCENT,
):
    source_names = [
        "ЕГРН",
        "ГИСОГД",
        "Внутренние данные компании",
        "Ограничения",
        "Цены",
        "Реальное землепользование",
    ]
    n_src = len(source_names)
    # Единый размер чипов (как на референсе Plan A/B/C)
    chip_h = 56
    chip_style = (
        f"height:{chip_h}px;width:100%;box-sizing:border-box;"
        f"display:flex;align-items:center;justify-content:center;"
        f"padding:0.35rem 0.4rem;border:1px solid {BORDER};border-radius:8px;"
        f"background:#fff;font-size:0.72rem;font-weight:500;line-height:1.2;"
        f"color:{INK};text-align:center;"
    )
    chips_html = "".join(
        f'<div style="{chip_style}">{name}</div>' for name in source_names
    )

    # Ортогональные линии со скруглением углов (одинаковый тонкий stroke)
    svg_w, svg_h, bus_y = 600, 72, 40
    corner_r = 10
    step = svg_w / n_src
    xs = [step * (i + 0.5) for i in range(n_src)]
    mid_x = svg_w / 2
    stroke = MUTED
    sw = 1  # тоньше
    parts: list[str] = []

    def _branch_path(x: float) -> str:
        """Вертикаль от чипа → скругление в сторону центра на шину."""
        if abs(x - mid_x) < 0.5:
            return f"M {x:.1f} 0 L {x:.1f} {bus_y:.1f}"
        r = min(corner_r, abs(x - mid_x) * 0.45, bus_y * 0.45)
        toward = 1 if x < mid_x else -1
        return (
            f"M {x:.1f} 0 "
            f"L {x:.1f} {bus_y - r:.1f} "
            f"Q {x:.1f} {bus_y:.1f} {x + toward * r:.1f} {bus_y:.1f}"
        )

    for x in xs:
        parts.append(
            f'<path d="{_branch_path(x)}" fill="none" stroke="{stroke}" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" />'
        )

    # Шина + ствол вниз со скруглённым T
    r_t = min(corner_r, (xs[-1] - xs[0]) * 0.08, (svg_h - bus_y) * 0.35)
    left_bus = (
        f"M {xs[0]:.1f} {bus_y:.1f} "
        f"L {mid_x - r_t:.1f} {bus_y:.1f} "
        f"Q {mid_x:.1f} {bus_y:.1f} {mid_x:.1f} {bus_y + r_t:.1f} "
        f"L {mid_x:.1f} {svg_h:.1f}"
    )
    right_bus = (
        f"M {xs[-1]:.1f} {bus_y:.1f} "
        f"L {mid_x + r_t:.1f} {bus_y:.1f} "
        f"Q {mid_x:.1f} {bus_y:.1f} {mid_x:.1f} {bus_y + r_t:.1f}"
    )
    parts.append(
        f'<path d="{left_bus}" fill="none" stroke="{stroke}" '
        f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" />'
    )
    parts.append(
        f'<path d="{right_bus}" fill="none" stroke="{stroke}" '
        f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" />'
    )

    connector_svg = (
        f'<svg width="100%" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}" '
        f'preserveAspectRatio="xMidYMid meet" aria-hidden="true" '
        f'style="display:block;margin:0;">'
        f'{"".join(parts)}</svg>'
    )
    # Короткий стык пайплайн → результат
    stem_svg = (
        f'<svg width="100%" height="36" viewBox="0 0 {svg_w} 36" '
        f'preserveAspectRatio="xMidYMid meet" aria-hidden="true" '
        f'style="display:block;margin:0;">'
        f'<line x1="{mid_x:.1f}" y1="0" x2="{mid_x:.1f}" y2="36" '
        f'stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" />'
        f"</svg>"
    )

    box_common = (
        f"box-sizing:border-box;width:220px;min-height:56px;padding:0.7rem 1rem;"
        f"border-radius:8px;font-size:0.88rem;font-weight:500;text-align:center;"
        f"display:flex;flex-direction:column;align-items:center;justify-content:center;"
    )

    diagram = mo.Html(
        f'<div style="max-width:640px;padding:1.25rem 0;'
        f'font-family:Inter,system-ui,sans-serif;">'
        f'<div style="font-size:0.72rem;font-weight:600;letter-spacing:0.06em;'
        f'text-transform:uppercase;color:{MUTED};margin-bottom:0.75rem;'
        f'text-align:center;">Источники</div>'
        f'<div style="display:grid;grid-template-columns:repeat({n_src},minmax(0,1fr));'
        f'gap:0.5rem;">{chips_html}</div>'
        f"{connector_svg}"
        f'<div style="display:flex;justify-content:center;">'
        f'<div style="{box_common}border:1px solid {BORDER};background:#fff;color:{INK};">'
        f"Воспроизводимый пайплайн</div></div>"
        f"{stem_svg}"
        f'<div style="display:flex;justify-content:center;">'
        f'<div style="{box_common}border:1px solid {ACCENT};background:{ACCENT};color:#fff;">'
        f"Один ЗУ = один объект"
        f'<div style="font-size:0.72rem;font-weight:400;opacity:0.85;margin-top:0.2rem;">'
        f"признаки + геометрия</div></div></div>"
        f"</div>"
    )

    mo.vstack(
        [
            section_eyebrow("5 — Данные"),
            section_heading("Несколько источников —<br>один пространственный объект"),
            divider(),
            body_text(
                "Раньше аналитик открывал каждый источник отдельно и терял "
                "пространственную привязку. Даже если внутри компании много данных — нередко они разбросаны по разным департаментам в различных форматах. "
                "Модель собирает все источники в воспроизводимом пайплайне: "
                "<strong>один участок — один объект — вся информация на него, которой мы обладаем</strong>. "
                "Такой data-governance продукт позволяет пересчитывать приоритеты при обновлении источников за минуты/часы, не недели."
            ),
            spacer(0.8),
            diagram,
            chart_caption(
                "Разрозненные реестры и источники данных → единый пространственный слой и приоритизация."
            ),
            spacer(4),
        ],
        gap=0,
    )
    return


# ─────────────────────────────────────────────────────────────────────────────
# Beat 5: Песочница — self-contained HTML widget (works in static Pages too)
# ─────────────────────────────────────────────────────────────────────────────


@app.cell(hide_code=True)
def _(
    ACCENT,
    BAR_LIGHT,
    BAR_MID,
    INK,
    MUTED,
    body_text,
    divider,
    mo,
    np,
    section_eyebrow,
    section_heading,
    spacer,
):
    import base64
    import json
    from pathlib import Path as _Path

    np.random.seed(42)
    _n = 500
    _land_use = np.random.choice(
        ["гараж", "открытый грунт", "МКД", "нежилое", "парк"],
        size=_n,
        p=[0.15, 0.25, 0.30, 0.20, 0.10],
    )
    _owner = np.random.choice(
        ["частный", "юрлицо", "публичный", "гос. структура"],
        size=_n,
        p=[0.35, 0.20, 0.25, 0.20],
    )
    _has_okn = (np.random.rand(_n) < 0.12).astype(int)
    _is_fragment = (np.random.rand(_n) < 0.22).astype(int)
    _payload = json.dumps(
        {
            "n": _n,
            "lu": _land_use.tolist(),
            "ow": _owner.tolist(),
            "okn": _has_okn.tolist(),
            "frag": _is_fragment.tolist(),
            "colors": {
                "high": ACCENT,
                "mid": BAR_MID,
                "low": BAR_LIGHT,
                "ink": INK,
                "muted": MUTED,
            },
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )

    _sandbox_html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1"/>
<style>
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; padding: 0.25rem 0 0.5rem;
    font-family: Inter, system-ui, -apple-system, sans-serif;
    color: {INK}; background: #fff;
  }}
  .row {{
    display: flex; align-items: center; justify-content: space-between;
    gap: 1rem; padding: 0.55rem 0; border-bottom: 1px solid #e4e4e7;
    max-width: 640px;
  }}
  .row label {{ font-size: 0.95rem; color: #3f3f46; line-height: 1.35; flex: 1; }}
  .sw {{
    position: relative; width: 42px; height: 24px; flex-shrink: 0;
    border-radius: 999px; background: #d4d4d8; border: 0; cursor: pointer;
    transition: background .15s ease; padding: 0;
  }}
  .sw[aria-checked="true"] {{ background: {ACCENT}; }}
  .sw span {{
    position: absolute; top: 3px; left: 3px; width: 18px; height: 18px;
    border-radius: 50%; background: #fff; transition: left .15s ease;
    box-shadow: 0 1px 2px rgba(0,0,0,.15);
  }}
  .sw[aria-checked="true"] span {{ left: 21px; }}
  .chart {{ margin-top: 1.25rem; max-width: 640px; }}
  .bar-row {{
    display: grid; grid-template-columns: 5.5rem 1fr 4.5rem;
    align-items: center; gap: 0.65rem; margin: 0 0 0.7rem;
  }}
  .bar-label {{ font-size: 0.85rem; font-weight: 500; color: {INK}; }}
  .bar-track {{ height: 18px; background: #f4f4f5; border-radius: 3px; overflow: hidden; }}
  .bar-fill {{ height: 100%; border-radius: 0 3px 3px 0; min-width: 0; transition: width .2s ease; }}
  .bar-pct {{ font-size: 0.8rem; color: {MUTED}; text-align: right; white-space: nowrap; }}
</style>
</head>
<body>
  <div class="row"><label for="g">Учитывать участки с гаражами</label>
    <button type="button" class="sw" id="g" role="switch" aria-checked="false"><span></span></button></div>
  <div class="row"><label for="l">Учитывать юридические лица в анализе</label>
    <button type="button" class="sw" id="l" role="switch" aria-checked="false"><span></span></button></div>
  <div class="row"><label for="o">Работать с ОКН</label>
    <button type="button" class="sw" id="o" role="switch" aria-checked="false"><span></span></button></div>
  <div class="row"><label for="m">Учитывать возможность объединения с соседними участками</label>
    <button type="button" class="sw" id="m" role="switch" aria-checked="false"><span></span></button></div>
  <div class="chart" id="chart"></div>
<script>
const DATA = {_payload};
const order = ["Высокий", "Средний", "Низкий"];
const fillOf = {{
  "Высокий": DATA.colors.high,
  "Средний": DATA.colors.mid,
  "Низкий": DATA.colors.low,
}};

function assign(lu, ow, okn, frag, flags) {{
  if (lu === "МКД" || lu === "парк") return "Низкий";
  if (ow === "гос. структура") return "Низкий";
  if (lu === "гараж" && !flags.g) return "Низкий";
  if (ow === "юрлицо" && !flags.l) return "Низкий";
  if (okn && !flags.o) return "Низкий";
  if (frag && !flags.m) return "Низкий";
  if (ow === "публичный" || okn) return "Средний";
  return "Высокий";
}}

function counts(flags) {{
  const c = {{"Высокий": 0, "Средний": 0, "Низкий": 0}};
  for (let i = 0; i < DATA.n; i++) {{
    c[assign(DATA.lu[i], DATA.ow[i], DATA.okn[i], DATA.frag[i], flags)]++;
  }}
  return c;
}}

function render() {{
  const flags = {{
    g: document.getElementById("g").getAttribute("aria-checked") === "true",
    l: document.getElementById("l").getAttribute("aria-checked") === "true",
    o: document.getElementById("o").getAttribute("aria-checked") === "true",
    m: document.getElementById("m").getAttribute("aria-checked") === "true",
  }};
  const c = counts(flags);
  const n = DATA.n;
  document.getElementById("chart").innerHTML = order.map(name => {{
    const v = c[name];
    const pct = Math.round(v / n * 1000) / 10;
    const w = Math.max(0, Math.min(100, v / n * 100));
    const label = v + "  ·  " + pct + "%";
    return '<div class="bar-row"><div class="bar-label">' + name + '</div>' +
      '<div class="bar-track"><div class="bar-fill" style="width:' + w +
      '%;background:' + fillOf[name] + '"></div></div>' +
      '<div class="bar-pct">' + label + '</div></div>';
  }}).join("");
}}

["g","l","o","m"].forEach(id => {{
  const el = document.getElementById(id);
  el.addEventListener("click", () => {{
    const on = el.getAttribute("aria-checked") !== "true";
    el.setAttribute("aria-checked", on ? "true" : "false");
    render();
  }});
}});
render();
</script>
</body></html>
"""

    _sandbox_b64 = base64.b64encode(_sandbox_html.encode("utf-8")).decode("ascii")
    _sandbox = mo.Html(
        f'<div style="width:100%;max-width:640px;height:420px;overflow:hidden;">'
        f'<iframe src="data:text/html;base64,{_sandbox_b64}" '
        f'title="Песочница правил" '
        f'style="width:100%;height:420px;border:0;display:block;"></iframe>'
        f"</div>"
    )
    _pages = _Path(__file__).resolve().parent / "docs"
    if _pages.is_dir():
        (_pages / "sandbox.html").write_text(_sandbox_html, encoding="utf-8")

    mo.vstack(
        [
            section_eyebrow("6 — Песочница"),
            section_heading("Песочница правил:<br>пересборка сценария за секунды"),
            divider(),
            body_text(
                "Поменяйте параметры в песочнице — распределение по приоритетам пересчитается "
                "мгновенно. Обсуждение стратегии становится конкретным, сразу видно "
                "что и как изменится."
            ),
            spacer(1.2),
            _sandbox,
            spacer(4),
        ],
        gap=0,
    )
    return


# ─────────────────────────────────────────────────────────────────────────────
# Beat 6: В цифрах — Linear-style comparison rows + compact share bars
# ─────────────────────────────────────────────────────────────────────────────


@app.cell(hide_code=True)
def _(
    mo, section_eyebrow, section_heading, body_text,
    spacer, divider, kpi_row,
):
    mo.vstack(
        [
            section_eyebrow("7 — Evidence"),
            section_heading("В цифрах:<br>масштаб задачи и результат"),
            divider(),
            body_text(
                "Модель собрана и запущена в крупной российской девелоперской компании. "
                "Объём — порядка 350 тыс. земельных участков, более 250 тыс. гектаров."
            ),
            spacer(1.2),
            kpi_row("Всего участков в модели", "100%", "базовый массив"),
            kpi_row("Высокий приоритет", "0,3%", "~26 тыс. Га"),
            kpi_row("Средний приоритет", "0,5%", "~3,5 тыс. Га"),
            kpi_row("Низкий / за периметром", "99,2%", "вне фокуса"),
            kpi_row("Ушло в работу аналитиков", "0,4%", "фокус, не потери"),
            spacer(1.0),
            body_text(
                "Для конкретной задачи меньше 1% массива прошло первичный отсев как перспективный. "
                "Это не потери, а фокус рассмотрения. "
            ),
            spacer(4),
        ],
        gap=0,
    )
    return


# ─────────────────────────────────────────────────────────────────────────────
# Beat 7: Карта — wibemaps + lightweight preview GPKG
# ─────────────────────────────────────────────────────────────────────────────


@app.cell(hide_code=True)
def _(
    mo, section_eyebrow, section_heading, body_text, spacer, divider,
):
    mo.vstack(
        [
            section_eyebrow("8 — Карта"),
            section_heading("Где лежат приоритетные участки"),
            divider(),
            body_text(
                "Ниже — пространственный срез модели: "
                "Тверской и четыре соседних района "
                "(Мещанский, Пресненский, Арбат, Хамовники)."
                "<br><br>"
                "Цвет — приоритет модели: от светло-голубого (<strong>3 приоритет</strong>) "
                "к синему (<strong>1 приоритет</strong>). "
                "Показаны все участки модели в этих районах."
            ),
            spacer(1.0),
        ],
        gap=0,
    )
    return


@app.cell(hide_code=True)
def _(DATA_DIR, gpd, mo):
    _center_path = DATA_DIR / "priority_center.gpkg"
    mo.stop(
        not _center_path.exists(),
        mo.md(
            "Нет `data/priority_center.gpkg`. "
            "Сначала запустите `prepare_map_data.py`."
        ),
    )
    center_gdf = gpd.read_file(_center_path, layer="priority_center").to_crs(4326)
    return (center_gdf,)


@app.cell(hide_code=True)
def _(
    ACCENT,
    FillLayer,
    Legend,
    Map,
    Popup,
    Search,
    center_gdf,
    center_zoom,
    chart_caption,
    embed_map,
    mo,
    spacer,
):
    _map_h = 640
    # light blue (3) → mid → accent blue (1)
    _COLORS = {
        "3 приоритет": "#bfdbfe",
        "2 приоритет": "#60a5fa",
        "1 приоритет": ACCENT,
    }

    if center_gdf.empty:
        _center, _zoom = [37.62, 55.75], 12
    else:
        _center, _zoom = center_zoom(
            center_gdf.total_bounds,
            pad_mult=0.2,
            min_pad=0.005,
            width=900,
            height=_map_h,
        )

    _m = Map(
        title="Приоритет · центр Москвы",
        center=_center,
        zoom=_zoom,
        embedded=True,
        tile_provider="yandex",
        use_compression=True,
    )

    _layer_names = []
    # draw order: 3 → 2 → 1 (синий сверху)
    for _label in ("3 приоритет", "2 приоритет", "1 приоритет"):
        _sub = center_gdf[center_gdf["dev_prig_fin"] == _label]
        if _sub.empty:
            continue
        _color = _COLORS[_label]
        _name = { "3 приоритет": "p3", "2 приоритет": "p2", "1 приоритет": "p1" }[_label]
        _m.add_layer(
            FillLayer(
                name=_name,
                source=_sub,
                style={
                    "colors": [_color],
                    "opacity": 0.45,
                    "stroke_width": 0.6,
                    "stroke_color": "#0b1a66",
                },
            )
        )
        _layer_names.append(_name)

    if _layer_names:
        _m.add_component(
            Legend(
                layers=_layer_names,
                layer_labels={
                    "p3": "3 приоритет",
                    "p2": "2 приоритет",
                    "p1": "1 приоритет",
                },
                show_toggle=True,
            )
        )
        _m.add_component(
            Popup(
                fields=[
                    "cadastral_number",
                    "area_zu",
                    "district",
                    "owner_category",
                    "m2_cost",
                    "dev_prig_fin",
                ],
                field_labels={
                    "cadastral_number": "КН",
                    "area_zu": "Площадь, Га",
                    "district": "Район",
                    "owner_category": "Собственник",
                    "m2_cost": "Ценовая зона",
                    "dev_prig_fin": "Приоритет",
                },
            )
        )
    _p1 = center_gdf[center_gdf["dev_prig_fin"] == "1 приоритет"]
    if not _p1.empty and "cadastral_number" in _p1.columns:
        _m.add_component(
            Search(
                search_mode="geojson",
                search_fields=["cadastral_number"],
                search_layers=["p1", "p2", "p3"],
                placeholder="Кадастровый номер…",
            )
        )

    _counts = center_gdf["dev_prig_fin"].value_counts()
    _map_panel = embed_map(
        _m,
        _map_h,
        title="Приоритет · центр Москвы",
        sidecar="map.html",
    )

    mo.vstack(
        [
            _map_panel,
            
            spacer(4),
        ],
        gap=0,
    )
    return


# ─────────────────────────────────────────────────────────────────────────────
# Beat 8: AI-инструменты — надстройка над слоем дев-земли
# ─────────────────────────────────────────────────────────────────────────────


@app.cell(hide_code=True)
def _(
    DATA_DIR,
    mo,
    section_eyebrow,
    section_heading,
    body_text,
    chart_caption,
    spacer,
    divider,
    deliverable_row,
    MUTED,
):
    _video_path = DATA_DIR.parent / "assets" / "geo_assist_illustr.mp4"
    mo.stop(
        not _video_path.exists(),
        mo.md(
            "Нет `assets/geo_assist_illustr.mp4`. "
            "Положи запись экрана ассистента в `research_landing/assets/`."
        ),
    )
    demo_video = mo.vstack(
        [
            mo.md(
                f'<div style="font-size:0.72rem;font-weight:600;letter-spacing:0.06em;'
                f'text-transform:uppercase;color:{MUTED};margin:0 0 0.5rem 0;'
                f'max-width:640px;">Как это выглядит в работе</div>'
            ),
            mo.video(
                str(_video_path),
                controls=True,
                muted=True,
                width=640,
            ),
        ],
        gap=0,
    )

    mo.vstack(
        [
            section_eyebrow("9 — AI"),
            section_heading("Слой собран —<br>теперь можно спрашивать"),
            divider(),
            body_text(
                "Цифровая модель даёт единую базу данных и пространственный слой с приоритетами. "
                "Дальше аналитик всё равно отвечает на поставленные задачей вопросы. Для более простого доступа к информации строим AI-инструменты. "
                "<br><br>"
                "AI-надстройка читает <strong>уже готовую</strong> базу данных "
                "и базу знаний по методике работы — не пересчитывает пайплайн в чате и "
                "не подменяет экспертное суждение. "
            ),
            spacer(1.0),
            deliverable_row(
                "01",
                "Вопросы к методике",
                "RAG по описанию модели и атрибутов: как устроена воронка, откуда берётся признак, что означает значение приоритета.",
            ),
            deliverable_row(
                "02",
                "Запросы к слою text-to-SQL",
                "Счётчики и срезы по витрине БД: сколько участков с фильтром по району, приоритету, площади — работа с информацией на естественном языке.",
            ),
            deliverable_row(
                "03",
                "Диалог по участку",
                "Выбираем ЗУ и задаём к нему вопросы: площадь, землепользование, собственник, ограничения, приоритет — без необходимости разбираться в структуре базы данных.",
            ),
            spacer(1.2),
            demo_video,
            
            spacer(4),
        ],
        gap=0,
    )
    return


# ─────────────────────────────────────────────────────────────────────────────
# Beat 9: Deliverables — numbered rows (Linear section list)
# ─────────────────────────────────────────────────────────────────────────────


@app.cell(hide_code=True)
def _(
    mo, section_eyebrow, section_heading, body_text, spacer, divider, deliverable_row,
):
    mo.vstack(
        [
            section_eyebrow("10 — Результат"),
            section_heading("Что получает команда на выходе"),
            divider(),
            body_text(
                "Пять артефактов, которые можно использовать независимо или вместе."
            ),
            spacer(0.8),
            deliverable_row(
                "01",
                "Методика",
                "Формализованные правила приоритизации. Документ, который можно читать, обсуждать и адаптировать.",
            ),
            deliverable_row(
                "02",
                "Интерактивная панель",
                "Дашборд с фильтрами по любым признакам. Рабочий инструмент аналитики и менеджмента.",
            ),
            deliverable_row(
                "03",
                "Слой на геопортале",
                "Пространственный слой с полным набором атрибутов. Может интегрироваться в существующую геоинфраструктуру. "
                "Или существовать как отдельный web-продукт.",
            ),
            deliverable_row(
                "04",
                "Воспроизводимый пайплайн",
                "Код, который собирает данные и пересчитывает результат.",
            ),
            deliverable_row(
                "05",
                "AI-надстройка",
                "Ассистент поверх слоя дев-земли: вопросы к методике, запросы к витрине и диалог по участку.",
            ),
            spacer(4),
        ],
        gap=0,
    )
    return


# ─────────────────────────────────────────────────────────────────────────────
# Beat 10: CTA
# ─────────────────────────────────────────────────────────────────────────────


@app.cell(hide_code=True)
def _(
    mo, section_eyebrow, section_heading, body_text, spacer, divider, ACCENT, INK, MUTED, BORDER,
):
    contacts = mo.md(
        f'<div style="max-width:640px;margin-top:1.5rem;'
        f'font-family:Inter,system-ui,sans-serif;">'
        f'<div style="font-size:1.02rem;font-weight:600;color:{INK};'
        f'margin-bottom:0.85rem;">Связаться с разработчиком:</div>'
        f'<div style="padding:0.75rem 0;border-bottom:1px solid {BORDER};'
        f'display:flex;justify-content:space-between;align-items:baseline;'
        f'gap:1rem;flex-wrap:wrap;">'
        f'<span style="font-size:0.95rem;color:#3f3f46;">Telegram</span>'
        f'<a href="https://t.me/katerinaa_romanova" target="_blank" rel="noopener" '
        f'style="font-size:1.05rem;font-weight:500;color:{ACCENT};'
        f'text-decoration:none;">katerinaa_romanova</a>'
        f"</div>"
        f'<div style="padding:0.75rem 0;border-bottom:1px solid {BORDER};'
        f'display:flex;justify-content:space-between;align-items:baseline;'
        f'gap:1rem;flex-wrap:wrap;">'
        f'<span style="font-size:0.95rem;color:#3f3f46;">Max</span>'
        f'<a href="tel:+79319629202" '
        f'style="font-size:1.05rem;font-weight:500;color:{ACCENT};'
        f'text-decoration:none;">+7 931 962-92-02</a>'
        f"</div>"
    )

    mo.vstack(
        [
            section_eyebrow("11 — Next"),
            section_heading("Как внедрить продукт"),
            divider(),
            body_text(
                "Модель — не продукт из коробки и не разовый отчёт. "
                "Для того, чтобы она работала, её нужно приземлить на инфраструктуру и задачи конкретной команды/бизнеса."
            ),
            contacts,
            spacer(6),
        ],
        gap=0,
    )
    return


if __name__ == "__main__":
    app.run()
