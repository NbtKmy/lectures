
import os
import csv
from numbers import Number

import processing
from qgis.core import (
    QgsProject,
    QgsVectorLayer
)

project = QgsProject.instance()

def get_layer(name):
    found = project.mapLayersByName(name)
    if not found:
        raise ValueError(f"レイヤがありません: {name}")
    return found[0]

# -----------------------------------
# 1. 入力データ
# -----------------------------------

boundary = get_layer("moriyama_boundary")
mesh = get_layer("moriyama_mesh_3km")

access_layers = {
    10: get_layer("moriyama_hospitals_10min_buffer30m"),
    20: get_layer("moriyama_hospitals_20min_buffer30m"),
    30: get_layer("moriyama_hospitals_30min_buffer30m")
}

all_layers = [boundary, mesh] + list(access_layers.values())

for layer in all_layers:
    if layer.crs().authid() != "EPSG:6675":
        raise ValueError(
            f"CRSが異なります: {layer.name()}"
        )

if boundary.featureCount() != 1:
    raise ValueError("行政境界が1地物ではありません")

if "population" not in mesh.fields().names():
    raise ValueError("populationフィールドがありません")

for minutes, layer in access_layers.items():
    if layer.featureCount() != 41:
        raise ValueError(
            f"{minutes}分圏が41地物ではありません"
        )

output_dir = os.path.join(
    project.homePath(), "access_results"
)
os.makedirs(output_dir, exist_ok=True)

# 既存ファイルを誤って上書きしない
output_paths = {
    m: os.path.join(
        output_dir,
        f"moriyama_analysis_B_{m}min_coverage.gpkg"
    )
    for m in access_layers
}

csv_path = os.path.join(
    output_dir,
    "moriyama_analysis_B_accessibility.csv"
)

for path in list(output_paths.values()) + [csv_path]:
    if os.path.exists(path):
        raise FileExistsError(
            f"既存の出力ファイルがあります: {path}"
        )

# -----------------------------------
# 2. 守山区内の推計総人口（分母）
# -----------------------------------

ward_geom = next(boundary.getFeatures()).geometry()

if ward_geom.isEmpty() or not ward_geom.isGeosValid():
    raise ValueError("行政境界の形状を確認してください")

mesh_records = []
total_population = 0.0
null_mesh_count = 0
covered_mesh_area = 0.0

for cell in mesh.getFeatures():

    geom = cell.geometry()

    if geom.isEmpty():
        continue

    if not ward_geom.intersects(geom):
        continue

    inside = ward_geom.intersection(geom)

    if inside.isEmpty():
        continue

    inside_area = inside.area()
    original_area = geom.area()

    if inside_area <= 0 or original_area <= 0:
        continue

    # 守山区に入る部分の比率
    ward_fraction = min(
        1.0, inside_area / original_area
    )

    covered_mesh_area += inside_area

    pop = cell["population"]

    if not isinstance(pop, Number):
        null_mesh_count += 1
        continue

    pop = float(pop)

    if pop < 0:
        raise ValueError("負の人口値があります")

    # メッシュ全体の人口を保持
    mesh_records.append((geom, original_area, pop))

    total_population += pop * ward_fraction

print("=== 守山区の人口 ===")
print("推計総人口:", round(total_population, 1))
print("人口NULLメッシュ:", null_mesh_count)
print(
    "メッシュの面積被覆率(%):",
    round(100 * covered_mesh_area / ward_geom.area(), 2)
)

if total_population <= 0:
    raise ValueError("総人口が計算できません")

# -----------------------------------
# 3. 到達圏を融合して守山区でクリップ
# -----------------------------------

results = []

for minutes, layer in access_layers.items():

    print(f"\n=== 徒歩{minutes}分以内 ===")

    # ポリゴンのジオメトリを修復
    fixed = processing.run(
        "native:fixgeometries",
        {
            "INPUT": layer,
            "OUTPUT": "memory:"
        }
    )["OUTPUT"]

    # 41病院分を1つの到達圏に融合
    dissolved = processing.run(
        "native:dissolve",
        {
            "INPUT": fixed,
            "FIELD": [],
            "OUTPUT": "memory:"
        }
    )["OUTPUT"]

    # 守山区の範囲だけを残す
    clipped_result = processing.run(
        "native:clip",
        {
            "INPUT": dissolved,
            "OVERLAY": boundary,
            "OUTPUT": output_paths[minutes]
        }
    )

    coverage = QgsVectorLayer(
        clipped_result["OUTPUT"],
        f"moriyama_B_{minutes}min_coverage",
        "ogr"
    )

    if not coverage.isValid():
        raise ValueError("到達圏を読み込めません")

    project.addMapLayer(coverage)

    # クリップ後の地物からジオメトリを取得
    coverage_geoms = [
        f.geometry()
        for f in coverage.getFeatures()
        if not f.geometry().isEmpty()
    ]

    print("到達圏ポリゴン数:", len(coverage_geoms))

    # -----------------------------------
    # 4. アクセス可能人口（分子）
    # -----------------------------------

    accessible_population = 0.0

    for mesh_geom, mesh_area, pop in mesh_records:

        for area in coverage_geoms:

            if not area.intersects(mesh_geom):
                continue

            intersection = area.intersection(mesh_geom)

            if intersection.isEmpty():
                continue

            overlap_area = intersection.area()

            if overlap_area <= 0:
                continue

            accessible_population += (
                pop * min(1.0, overlap_area / mesh_area)
            )

    accessibility_rate = (
        accessible_population / total_population * 100
    )

    outside_population = (
        total_population - accessible_population
    )

    results.append({
        "minutes": minutes,
        "total_population_est": round(total_population, 2),
        "accessible_population_est": round(
            accessible_population, 2
        ),
        "outside_population_est": round(
            outside_population, 2
        ),
        "accessibility_percent": round(
            accessibility_rate, 2
        )
    })

    print(
        "アクセス可能人口:",
        round(accessible_population, 1)
    )
    print(
        "アクセス率:",
        round(accessibility_rate, 2), "%"
    )
    print(
        "圏外人口:",
        round(outside_population, 1)
    )

# -----------------------------------
# 5. 結果チェック
# -----------------------------------

rates = [
    r["accessibility_percent"]
    for r in results
]

if len(rates) != 3:
    raise ValueError("時間区分が不足しています")

if not (rates[0] <= rates[1] <= rates[2]):
    print("警告：アクセス率が単調増加していません")

if any(r < -0.01 or r > 100.01 for r in rates):
    raise ValueError("アクセス率が0〜100%の範囲外です")

# -----------------------------------
# 6. CSVを保存
# -----------------------------------

with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "minutes",
            "total_population_est",
            "accessible_population_est",
            "outside_population_est",
            "accessibility_percent"
        ]
    )
    writer.writeheader()
    writer.writerows(results)

print("\n=== 分析B 完了 ===")
print("CSV:", csv_path)
print("結果:", results)
