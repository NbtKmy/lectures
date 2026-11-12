
from qgis.core import QgsProject

# 病院レイヤの取得
layers = QgsProject.instance().mapLayersByName(
    "moriyama_buffer_hospitals"
)

if not layers:
    print("病院レイヤが見つかりません")
else:
    hospitals = layers[0]

    print("レイヤ名:", hospitals.name())
    print("病院数:", hospitals.featureCount())
    print("CRS:", hospitals.crs().authid())
    print("ジオメトリ:", hospitals.geometryType())

    print("\n属性フィールド:")
    for field in hospitals.fields():
        print(" -", field.name(), ":", field.typeName())

    print("\n最初の3施設:")
    for feature in list(hospitals.getFeatures())[:3]:
        print(feature.attributes())
