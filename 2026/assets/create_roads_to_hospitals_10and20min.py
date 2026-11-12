
import os
import processing
from qgis.core import QgsProject, QgsProcessingFeedback

project = QgsProject.instance()

# 入力レイヤ
hospitals = project.mapLayersByName(
    "moriyama_buffer_hospitals"
)[0]

roads = project.mapLayersByName(
    "moriyama_osm_walkable_preliminary"
)[0]

# QGISプロジェクトのフォルダ内に出力先を作る
output_dir = os.path.join(project.homePath(), "access_results")
os.makedirs(output_dir, exist_ok=True)

# 徒歩4km/hでの距離閾値（メートル）
thresholds = {
    10: 4000 * 10 / 60,
    20: 4000 * 20 / 60
}

for minutes, distance in thresholds.items():

    print(f"\n=== 徒歩{minutes}分圏の計算開始 ===")

    output_path = os.path.join(
        output_dir,
        f"moriyama_hospitals_{minutes}min_lines.gpkg"
    )

    # 古い出力があれば上書きを避けて停止
    if os.path.exists(output_path):
        print("既にファイルがあります:", output_path)
        continue

    result = processing.run(
        "native:serviceareafromlayer",
        {
            "INPUT": roads,
            "START_POINTS": hospitals,
            "STRATEGY": 0,
            "TRAVEL_COST": distance,
            "DIRECTION_FIELD": None,
            "VALUE_FORWARD": "",
            "VALUE_BACKWARD": "",
            "VALUE_BOTH": "",
            "DEFAULT_DIRECTION": 2,
            "SPEED_FIELD": None,
            "DEFAULT_SPEED": 4,
            "TOLERANCE": 0,
            "POINT_TOLERANCE": 100,
            "INCLUDE_BOUNDS": False,
            "OUTPUT_LINES": output_path,
            "OUTPUT": "TEMPORARY_OUTPUT",
            "OUTPUT_NON_ROUTABLE": "TEMPORARY_OUTPUT"
        },
        feedback=QgsProcessingFeedback()
    )

    project.addMapLayer(
        QgsVectorLayer(
            result["OUTPUT_LINES"],
            f"moriyama_hospitals_{minutes}min_lines",
            "ogr"
        )
    )

    print("保存先:", output_path)

    from qgis.core import QgsVectorLayer

    check = QgsVectorLayer(output_path, "check", "ogr")
    print("出力地物数:", check.featureCount())

    print(f"徒歩{minutes}分圏の処理完了")

print("\nすべての処理が終了しました")
