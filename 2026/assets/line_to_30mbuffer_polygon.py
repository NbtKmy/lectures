
import os
import processing
from qgis.core import QgsProject, QgsVectorLayer, QgsWkbTypes

project = QgsProject.instance()

output_dir = os.path.join(
    project.homePath(), "access_results"
)

# 既存の到達道路レイヤ名
layer_names = {
    10: "moriyama_hospitals_10min_lines",
    20: "moriyama_hospitals_20min_lines",
    30: "moriyama_all_hospitals_30min_lines"
}

for minutes, layer_name in layer_names.items():

    print(f"\n=== {minutes}分圏のポリゴン化 ===")

    layers = project.mapLayersByName(layer_name)

    if not layers:
        print("レイヤが見つかりません:", layer_name)
        continue

    lines = layers[0]

    if lines.featureCount() != 41:
        print("警告：想定した41施設と件数が異なります")

    if lines.crs().authid() != "EPSG:6675":
        print("CRSが異なります。処理を中止します")
        continue

    output_path = os.path.join(
        output_dir,
        f"moriyama_hospitals_{minutes}min_buffer30m.gpkg"
    )

    if os.path.exists(output_path):
        print("すでに存在します:", output_path)
        continue

    result = processing.run(
        "native:buffer",
        {
            "INPUT": lines,
            "DISTANCE": 30,
            "SEGMENTS": 8,
            "END_CAP_STYLE": 0,
            "JOIN_STYLE": 0,
            "MITER_LIMIT": 2,
            "DISSOLVE": False,
            "OUTPUT": output_path
        }
    )

    polygon = QgsVectorLayer(
        result["OUTPUT"],
        f"moriyama_hospitals_{minutes}min_buffer30m",
        "ogr"
    )

    if not polygon.isValid():
        print("出力の読み込みに失敗")
        continue

    project.addMapLayer(polygon)

    print("ポリゴン数:", polygon.featureCount())
    print("ジオメトリ:", QgsWkbTypes.displayString(
        polygon.wkbType()
    ))
    print("フィールド:", polygon.fields().names())
    print("保存先:", output_path)

print("\nすべての処理が終了しました")
