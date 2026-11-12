
import os
import csv
from numbers import Number

from qgis.core import (
    QgsProject,
    QgsGeometry,
    QgsSpatialIndex
)

project = QgsProject.instance()

# -----------------------------------
# 1. 入力レイヤ
# -----------------------------------

def get_layer(name):
    found = project.mapLayersByName(name)
    if not found:
        raise ValueError(f"レイヤが見つかりません: {name}")
    return found[0]

mesh = get_layer("moriyama_mesh_3km")

polygon_layers = {
    10: get_layer("moriyama_hospitals_10min_buffer30m"),
    20: get_layer("moriyama_hospitals_20min_buffer30m"),
    30: get_layer("moriyama_hospitals_30min_buffer30m")
}

# 守山区内の8病院
hospital_ids = {
    3514, 3538, 4117, 4814,
    4847, 5822, 6854, 8536
}

# -----------------------------------
# 2. 入力データのチェック
# -----------------------------------

for layer in [mesh] + list(polygon_layers.values()):
    if layer.crs().authid() != "EPSG:6675":
        raise ValueError(f"CRSが違います: {layer.name()}")

if "population" not in mesh.fields().names():
    raise ValueError("人口フィールドがありません")

# メッシュを空間インデックスに登録
mesh_features = {
    f.id(): f for f in mesh.getFeatures()
}

index = QgsSpatialIndex()
for f in mesh_features.values():
    index.addFeature(f)

# -----------------------------------
# 3. 面積按分による人口計算
# -----------------------------------

results = []

for minutes, polygons in polygon_layers.items():

    print(f"\n=== 徒歩{minutes}分以内 ===")

    for hospital in polygons.getFeatures():

        hospital_id = int(hospital["fid"])

        if hospital_id not in hospital_ids:
            continue

        name = str(hospital["P04_002"])
        area = hospital.geometry()

        total_population = 0.0
        matched_meshes = 0
        null_meshes = 0

        # ポリゴン周辺のメッシュのみ探索
        candidate_ids = index.intersects(
            area.boundingBox()
        )

        for mesh_id in candidate_ids:

            cell = mesh_features[mesh_id]
            cell_geom = cell.geometry()

            if not area.intersects(cell_geom):
                continue

            intersection = area.intersection(cell_geom)

            if intersection.isEmpty():
                continue

            overlap_area = intersection.area()
            original_area = cell_geom.area()

            if overlap_area <= 0 or original_area <= 0:
                continue

            population = cell["population"]

            if population is None or not isinstance(population, Number):
                null_meshes += 1
                continue

            # 面積按分
            ratio = min(1.0, overlap_area / original_area)
            total_population += float(population) * ratio
            matched_meshes += 1

        results.append({
            "hospital_id": hospital_id,
            "hospital_name": name,
            "minutes": minutes,
            "population_est": round(total_population, 2),
            "mesh_count": matched_meshes,
            "null_mesh_count": null_meshes
        })

        print(
            f"{name}: {total_population:.1f}人 "
            f"(人口あり:{matched_meshes}, NULL:{null_meshes})"
        )

# -----------------------------------
# 4. CSVで保存
# -----------------------------------

output_dir = os.path.join(
    project.homePath(), "access_results"
)
os.makedirs(output_dir, exist_ok=True)

output_csv = os.path.join(
    output_dir,
    "moriyama_analysis_A_population.csv"
)

results.sort(key=lambda r: (
    r["hospital_id"], r["minutes"]
))

with open(output_csv, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "hospital_id",
            "hospital_name",
            "minutes",
            "population_est",
            "mesh_count",
            "null_mesh_count"
        ]
    )
    writer.writeheader()
    writer.writerows(results)

# -----------------------------------
# 5. 結果の整合性をチェック
# -----------------------------------

print("\n=== 結果チェック ===")
print("集計件数:", len(results))
print("期待件数:", len(hospital_ids) * 3)

if len(results) != len(hospital_ids) * 3:
    print("警告：病院または時間圏が不足しています")

for hid in sorted(hospital_ids):
    values = {
        r["minutes"]: r["population_est"]
        for r in results
        if r["hospital_id"] == hid
    }

    if len(values) == 3:
        if not (values[10] <= values[20] <= values[30]):
            print("警告：累積人口が単調増加していません", hid, values)

print("保存先:", output_csv)
print("処理終了")
