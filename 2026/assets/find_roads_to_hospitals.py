
import processing
from qgis.core import QgsProject, QgsProcessingFeedback

project = QgsProject.instance()

# すでに確認できた病院レイヤ
hospitals = project.mapLayersByName(
    "moriyama_buffer_hospitals"
)[0]

# 徒歩道路ネットワーク
roads = project.mapLayersByName(
    "moriyama_osm_walkable_preliminary"
)[0]

# 事前確認
assert hospitals.crs().authid() == "EPSG:6675"
assert roads.crs().authid() == "EPSG:6675"

print("病院数:", hospitals.featureCount())
print("道路数:", roads.featureCount())

# 徒歩4km/h × 30分 = 2000m
result = processing.run(
    "native:serviceareafromlayer",
    {
        "INPUT": roads,
        "START_POINTS": hospitals,
        "STRATEGY": 0,
        "TRAVEL_COST": 2000,
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
        "OUTPUT_LINES": "memory:",
        "OUTPUT": "memory:",
        "OUTPUT_NON_ROUTABLE": "memory:"
    },
    feedback=QgsProcessingFeedback()
)

# 結果をQGISに追加
lines = result["OUTPUT_LINES"]
lines.setName("moriyama_all_hospitals_30min_lines")
project.addMapLayer(lines)

print("到達道路の地物数:", lines.featureCount())
print("出力フィールド:", lines.fields().names())

non_routable = result["OUTPUT_NON_ROUTABLE"]
print("道路へ接続できなかった病院:", non_routable.featureCount())

print("処理完了")
