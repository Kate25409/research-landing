"""Prepare lightweight map layers for the research landing.

Source: cleaned public layer `data/developable_land.gpkg` (MKAD only).
Full layer is still too heavy for browser GeoJSON — this script extracts:
  - priority_center.gpkg — Tverskoy + 4 neighbors, all 3 priorities
  - merge_example.gpkg  — one seed parcel + its merge group (склейка)
  - example_cards.gpkg  — two illustrative parcels for Beat 1

Usage:
  uv run --with geopandas --with pyogrio prepare_map_data.py
"""

from pathlib import Path

import geopandas as gpd
import pandas as pd

OUT_DIR = Path(__file__).resolve().parent / "data"
SRC = OUT_DIR / "developable_land.gpkg"

# Тверской + 4 соседних из исходного центрального списка
CENTER_DISTRICTS = [
    "Тверской",
    "Мещанский",
    "Пресненский",
    "Арбат",
    "Хамовники",
]

# Cap samples per priority so marimo iframe stays small
# None = keep all polygons in the center districts
PRIORITY_CAPS = {
    "1 приоритет": None,
    "2 приоритет": None,
    "3 приоритет": None,
}

COLS = [
    "cadastral_number",
    "area_zu",
    "district",
    "owner_category",
    "generated_land_use",
    "restrictions",
    "m2_cost",
    "dev_prig_fin",
    "developer",
    "geometry",
]

MERGE_GROUP_IDX = 4927
MERGE_SEED_CN = "77:04:0001009:51"


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"Missing source layer: {SRC}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("loading center districts…")
    where = " OR ".join(f"district = '{d}'" for d in CENTER_DISTRICTS)
    gdf = gpd.read_file(SRC, layer="developable_land", where=where)
    gdf = gdf[[c for c in COLS if c in gdf.columns]].to_crs(4326)
    # ~1 м. Прежний 0.00025 (~28 м) резал участки до треугольников
    gdf["geometry"] = gdf.geometry.simplify(0.00001, preserve_topology=True)
    print("  raw", len(gdf), gdf["dev_prig_fin"].value_counts().to_dict())

    parts = []
    for label, cap in PRIORITY_CAPS.items():
        sub = gdf[gdf["dev_prig_fin"] == label]
        if sub.empty:
            print(f"  warning: no rows for {label}")
            continue
        if cap is not None and len(sub) > cap:
            sub = sub.sample(cap, random_state=42)
        parts.append(sub)
        print(f"  keep {label}: {len(sub)}")

    center = gpd.GeoDataFrame(pd.concat(parts, ignore_index=True), crs=4326)
    slim = [
        c
        for c in (
            "cadastral_number",
            "area_zu",
            "district",
            "owner_category",
            "m2_cost",
            "dev_prig_fin",
            "geometry",
        )
        if c in center.columns
    ]
    center = center[slim]
    center_path = OUT_DIR / "priority_center.gpkg"
    if center_path.exists():
        center_path.unlink()
    center.to_file(center_path, layer="priority_center", driver="GPKG")
    print(
        f"center: {len(center)} -> {center_path.stat().st_size / 1024 / 1024:.1f} MB"
    )

    print("exporting example card parcels A/B...")
    example_ids = {
        "A": "77:08:0012004:12",
        "B": "77:02:0024002:42",
    }
    keep = [
        "cadastral_number",
        "area_zu",
        "owner_category",
        "generated_land_use",
        "category_vri",
        "restrictions",
        "dev_prig_fin",
        "district",
        "okrug",
        "in_mkad",
        "geometry",
    ]
    rows = []
    for label, cn in example_ids.items():
        part = gpd.read_file(
            SRC,
            layer="developable_land",
            where=f"cadastral_number = '{cn}'",
        )
        if part.empty:
            print(f"  warning: {label} {cn} not found")
            continue
        part = part.iloc[[0]][[c for c in keep if c in part.columns]].to_crs(4326)
        part["card_id"] = label
        rows.append(part)
    if rows:
        examples = gpd.GeoDataFrame(pd.concat(rows, ignore_index=True), crs=4326)
        ex_path = OUT_DIR / "example_cards.gpkg"
        if ex_path.exists():
            ex_path.unlink()
        examples.to_file(ex_path, layer="example_cards", driver="GPKG")
        print(f"examples: {len(examples)} -> {ex_path.stat().st_size / 1024:.0f} KB")

    print(f"exporting merge example group {MERGE_GROUP_IDX}...")
    merge = gpd.read_file(
        SRC,
        layer="developable_land",
        where=f"group_idx = {MERGE_GROUP_IDX}",
    )
    merge_keep = [
        "cadastral_number",
        "area_zu",
        "district",
        "okrug",
        "owner_category",
        "generated_land_use",
        "dev_prig_fin",
        "group_idx",
        "count_per_group",
        "geometry",
    ]
    merge = merge[[c for c in merge_keep if c in merge.columns]].to_crs(4326)
    merge["is_seed"] = merge["cadastral_number"] == MERGE_SEED_CN
    if not merge.empty and not merge["is_seed"].any():
        named = merge["cadastral_number"].notna()
        seed_idx = (
            merge.loc[named, "area_zu"].idxmin()
            if named.any()
            else merge["area_zu"].idxmin()
        )
        merge["is_seed"] = False
        merge.loc[seed_idx, "is_seed"] = True
        print(
            f"  warning: seed {MERGE_SEED_CN} not found, using "
            f"{merge.loc[seed_idx, 'cadastral_number']}"
        )
    if not merge.empty:
        merge["geometry"] = merge.geometry.simplify(0.00005, preserve_topology=True)
        merge_path = OUT_DIR / "merge_example.gpkg"
        if merge_path.exists():
            merge_path.unlink()
        merge.to_file(merge_path, layer="merge_example", driver="GPKG")
        seed_area = float(merge.loc[merge["is_seed"], "area_zu"].iloc[0])
        print(
            f"merge: {len(merge)} parcels, seed {seed_area:.2f} Га → "
            f"group {merge['area_zu'].sum():.2f} Га -> "
            f"{merge_path.stat().st_size / 1024:.0f} KB"
        )
    else:
        print(f"  warning: merge group {MERGE_GROUP_IDX} not found (skipped)")

    print("done")


if __name__ == "__main__":
    main()
