# QGISセッション用HTML資料 実装計画

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 設計書どおり、4タブ(Task 1/2/3/Limits)と3つの埋め込み地図を持つ、英語・ダークモードの**単体HTMLファイル** `2026/qgis/qgis_session.html` を生成するビルド一式を作る。

**Architecture:** `2026/qgis/html_src/` にソース(Python製ビルドスクリプト、HTMLテンプレート、CSS、JS、タブ本文の断片)を置く。`build.py` が `2026/assets/` のGIS資産をQGIS同梱の `ogr2ogr` でWGS84・簡略化GeoJSONに変換し、JSON・CSS・JS(Leaflet含む)・本文をテンプレートへ全部インライン化して1ファイルにする。地図はLeaflet、分類(Equal Interval / Quantile / Natural Breaks)はテスト可能な自前のJS(`classify.js`)、サムネイルはビルド時にPythonでSVG生成する。

**Tech Stack:** Python 3.11(標準ライブラリ+`unittest`のみ)、Node 24(`node:test`)、GDAL 3.13の `ogr2ogr`、Leaflet 1.9.4(`html_src/vendor/` に同梱)、素のHTML/CSS/JS。

**Spec:** `2026/qgis/html_session_design.md`(§2 構成、§3 HTML仕様、§4 データ、§9 追記の判断)。実行者は必ず両方を読むこと。

## Global Constraints

- 出力は**1つのHTMLファイル**、`2026/qgis/qgis_session.html`。外部へ読みに行くのは**背景タイルのみ**。JS・CSS・データはすべてインライン(設計書§3)。
- 言語は**英語**。ただし市区町村名・病院名は**日本語(漢字)のまま**表示する(設計書§9-6)。
- **ダークモード基調**、ファンシー、スマートフォン幅でも読める(設計書§3)。色・地図の見せ方は着手前に `dataviz` スキル、画面設計は `frontend-design` スキルを読むこと。
- タブは**4つ**: Task 1 / Task 2 / Task 3 / Limits。選んだタブの内容が縦スクロール1ページで見える。`#task1` `#task2` `#task3` `#limits` のハッシュで直接開ける。最初の画面(landing)に3つのサムネイル。「Start here」はタブの手前に常時表示。
- 各Taskの地図は**ちょうど1つ**。Task 1 = 件数↔率トグル+分類Mode切替(凡例連動)。Task 2 = 川島病院の徒歩10分の道路ライン+10分圏+圏内メッシュ人口。Task 3 = 10/20/30分スライダー(圏域とアクセス率が連動)。
- フッターに出典・帰属を常時表示: OpenStreetMap contributors(ODbL)/ 国土数値情報(MLIT)N03・P04 / e-Stat 国勢調査(令和2年)/ 在留外国人統計(e-Stat)。
- 数値は設計書どおり: Task 3 = 17.90% / 46.61% / 62.60%(分母174,833.87人、30分圏内109,452.93人)。Task 2 = 圏内20メッシュ、`pop_est` 合計 **5,420.9人**。Task 2とTask 3は**方式が異なる**ため、両ページに断り書きを入れ、数字を並べて比較しない。
- Task 3の数字は**近似・潜在的アクセス**と明記する。62.6%を検証済みの事実のように書かない。
- 目標サイズ: 完成HTMLは**6MB以下**(上限16MB)。
- スクリーンショットは**この版では使わない**(設計書§3「後日撮影」)。
- ユーザーが明示的に頼むまで**コミット・プッシュをしない**。各Taskの最後は「`git status` で意図した変更だけであることを確認」で終える。
- `2026/assets/` の元ファイルは**読み取り専用**。変更しない。
- テスト実行: Python = `python3 -I -m unittest discover -s 2026/qgis/html_src/tests -v`、JS = `node --test 2026/qgis/html_src/tests/`。`ogr2ogr` は `/Applications/QGIS.app/Contents/MacOS/ogr2ogr`(環境変数 `OGR2OGR` で上書き可)。

## Review Focus

仕様が暗黙に求めるが、どのTaskのテストにも自然には現れにくい、ユーザーが踏みやすい失敗(可能性の高い順)。各行のテストは担当Taskにある。

1. **所属未定地(`23000`、CSVに行なし)**: 率が `null`。灰色で描き、ツールチップは "no data"。**0%として分類・描画しない**。分類の対象外。(Task 2 / Task 8)
2. **分母が極小の自治体**(設楽町 `pr_all=7`、ブラジル3人 → 42.86%): 率の地図で目立つ。ツールチップに**件数(分子・分母)も併記**し、小さい数の問題が見えるようにする。(Task 8)
3. **背景タイルに接続できない**(オフライン): ポリゴンは暗色背景に描画され、未処理例外が出ない。(Task 8, 15)
4. **スマートフォン幅(375px)**: タブが折り返し/横スクロールし、ページ自体は横スクロールしない。地図に十分な高さがある。(Task 7, 15)
5. **隠れたタブ内の地図**: 直接 `#task3` で開いてもLeafletのサイズが正しい。未知のハッシュはTask 1の既定へ。ブラウザの戻るで前のタブに戻れる。(Task 7, 15)

(別途、`classify.js` は値の重複・距離の異なる値がk未満の場合でも壊れない。Task 5。)

---

## ファイル構成

```
2026/qgis/
  qgis_session.html            # 生成物(追跡する)
  html_src/
    build.py                   # 組立(エントリポイント): python3 2026/qgis/html_src/build.py
    data_prep.py               # GISデータ → Web用GeoJSON・統計(辞書)
    thumbnails.py              # GeoJSON → SVGサムネイル文字列
    template.html              # {{name}} 置換方式のページ骨格
    style.css
    app.js                     # タブ・ハッシュ・遅延初期化
    classify.js                # 分類(ブラウザ/Node両用)
    map_task1.js map_task2.js map_task3.js
    content/                   # タブ本文の断片(英語HTML)
      start.html task1.html task2.html task3.html limits.html
    vendor/leaflet/            # leaflet.js leaflet.css (1.9.4)
    .cache/                    # 変換途中のGeoJSON(gitignore)
    tests/
      test_data_prep.py test_thumbnails.py test_build.py classify.test.mjs
2026/assets/README.md          # 出典と「参加者が使うのはここだけ」
```

**データ契約**(JSの `window.DATA` と `data_prep` の戻り値は同一):

- `task1`: GeoJSON FeatureCollection(70地物、市区町村コードごとに1 MultiPolygon)。`properties` = `{code:str, name:str, pr_all:int|null, pr_brazil:int|null, rate_brazil:float|null}`。`rate_brazil = round(pr_brazil / pr_all * 100, 2)`。
- `task2`: `{hospital: Feature(Point){name}, boundary: FC, service_area: FC(Line), reach: FC(Polygon), mesh: FC(Polygon){pop_est:float}, summary: {hospital_name:"川島病院", total_pop_est:float, mesh_count:int}}`。
- `task3`: `{boundary: FC, hospitals: FC(Point, 41地物){name}, coverage: {"10":FC,"20":FC,"30":FC}, stats: {"10":{total,accessible,outside,percent}, "20":…, "30":…}}`(数値はCSV由来のfloat)。

---

### Task 1: 足場とGeoJSON変換器

**Files:**
- Create: `2026/qgis/html_src/data_prep.py`(変換器のみ)、`2026/qgis/html_src/tests/test_data_prep.py`、`2026/qgis/html_src/vendor/leaflet/leaflet.js`、`.../leaflet.css`
- Modify: `/Users/nobu/lectures/.gitignore`

**Interfaces:**
- Produces: `data_prep.ogr_to_geojson(src: Path, dest: Path, *, layer: str | None = None, simplify_deg: float = 0.0, precision: int = 5) -> dict` — `src` を EPSG:4326へ変換・簡略化して `dest` に書き、読み込んだGeoJSON(dict)を返す。`data_prep.ASSETS: Path`(= `2026/assets`)、`data_prep.CACHE: Path`(= `html_src/.cache`)。

- [ ] **Step 1: 失敗するテストを書く** — `test_data_prep.py::TestConverter`: `test_reprojects_to_wgs84`(`moriyama_admin_field.gpkg` を変換 → 全座標が経度136–138・緯度34–36に入る)、`test_simplify_reduces_size`(`simplify_deg=0.001` の出力バイト数が `0.0` より小さい)、`test_missing_source_raises`(`FileNotFoundError`)。
- [ ] **Step 2: 実行して失敗を確認** — `python3 -I -m unittest discover -s 2026/qgis/html_src/tests -v` → `ModuleNotFoundError` か `ImportError`。
- [ ] **Step 3: `ogr_to_geojson` を実装** — `subprocess.run` で `ogr2ogr -f GeoJSON -t_srs EPSG:4326 -lco COORDINATE_PRECISION=<precision> [-simplify <deg>] dest src [layer]`。`OGR2OGR` 環境変数があればそれを使う。`dest` の親フォルダを作る。
- [ ] **Step 4: Leaflet 1.9.4 を同梱** — `curl -fsSL https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js` と `.../leaflet.css` を `vendor/leaflet/` へ保存。
- [ ] **Step 5: `.gitignore` を更新** — `2026/qgis/html_src/.cache/` を無視に追加。`!2026/assets/moriyama_buffer_hospitals.gpkg`(41病院、Task 3のビルド入力)を許可リストに追加。
- [ ] **Step 6: テストを実行して通過を確認** — 同コマンド → 3件PASS。`git status` で意図した変更だけであることを確認。

---

### Task 2: Task 1用データ(愛知県の永住外国人)

**Files:** Modify: `data_prep.py`, `tests/test_data_prep.py`

**Interfaces:**
- Consumes: `ogr_to_geojson`、`ASSETS`。
- Produces: `data_prep.build_task1() -> dict`(データ契約の `task1`)。入力 `aichi_admin_fields2025.geojson`(GeoJSON、1033地物)と `aichi_permanent_residents_202512.csv`(UTF-8、69行)。同じ `N03_007` の地物を1つの MultiPolygon にまとめる(union不要、ポリゴンを集めるだけ)。`name` はCSVの `municipality`。CSVに無い `23000` は `name="所属未定地"` ・数値は `null`。

- [ ] **Step 1: 失敗するテストを書く** — `TestTask1`: `test_feature_count_is_70`、`test_unassigned_area_has_null_rate`(`code=="23000"` で `rate_brazil is None` かつ `pr_all is None`)、`test_totals_match_csv`(`pr_all` の合計 = 106839、`pr_brazil` の合計 = 34357)、`test_rate_is_rounded_percentage`(設楽町 `23561`: `pr_all=7`, `pr_brazil=3`, `rate_brazil==42.86`)、`test_geometry_is_multipolygon_for_all`、`test_payload_size_under_1_5mb`(`len(json.dumps(...))`)。
- [ ] **Step 2: 失敗を確認** — `AttributeError: build_task1`。
- [ ] **Step 3: `build_task1` を実装** — 簡略化の許容値(`simplify_deg`)は、サイズ上限を満たす範囲で最大の細かさを選ぶ(目安 0.0005)。
- [ ] **Step 4: 通過を確認** — `TestTask1` の6件 PASS。`git status` を確認。

---

### Task 3: Task 2用データ(川島病院の徒歩10分圏)

**Files:** Modify: `data_prep.py`, `tests/test_data_prep.py`

**Interfaces:**
- Consumes: `ogr_to_geojson`。
- Produces: `data_prep.build_task2() -> dict`(データ契約の `task2`)。入力(すべて `ASSETS` 配下):`moriyama_admin_field.gpkg`(境界)、`moriyama_hospital_test.gpkg`(病院点。名前は `P04_002`)、`moriyama_service_area_lines.gpkg`(道路ライン)、`moriyama_test_10min_polygon_clean.gpkg`(10分圏)、`moriyama_test_10min_intersection_with_population_clean.gpkg`(圏内メッシュ、`pop_est`)。`summary.hospital_name` は `"川島病院"` 固定、`total_pop_est` は `pop_est` の合計(小数1桁)。

- [ ] **Step 1: 失敗するテストを書く** — `TestTask2`: `test_mesh_has_20_cells`、`test_total_pop_est`(`summary.total_pop_est == 5420.9`)、`test_service_area_is_line_geometry`、`test_reach_inside_boundary_bbox`(10分圏のbboxが境界のbboxを大きくはみ出さない。許容 0.01度)、`test_payload_size_under_600kb`。
- [ ] **Step 2: 失敗を確認** — `AttributeError: build_task2`。
- [ ] **Step 3: `build_task2` を実装** — メッシュと10分圏は `precision=5`、`simplify_deg=0`(小さいので簡略化しない)。道路ラインはそのまま。
- [ ] **Step 4: 通過を確認** — 5件 PASS。`git status` を確認。

---

### Task 4: Task 3用データ(アクセス率)

**Files:** Modify: `data_prep.py`, `tests/test_data_prep.py`

**Interfaces:**
- Produces: `data_prep.build_task3() -> dict`(データ契約の `task3`)。入力:`moriyama_admin_field.gpkg`、`moriyama_buffer_hospitals.gpkg`(41点、名前は `P04_002`)、`moriyama_analysis_B_{10,20,30}min_coverage.gpkg`、`moriyama_analysis_B_accessibility.csv`(**UTF-8 BOM付き**: `encoding="utf-8-sig"`)。

- [ ] **Step 1: 失敗するテストを書く** — `TestTask3`: `test_hospital_count_is_41`、`test_stats_match_csv`(`stats["30"] == {"total":174833.87,"accessible":109452.93,"outside":65380.94,"percent":62.6}`、`stats["10"]["percent"]==17.9`、`stats["20"]["percent"]==46.61`)、`test_coverage_has_one_feature_per_minute`、`test_percent_is_monotonic`(10 ≤ 20 ≤ 30)、`test_payload_size_under_1mb`。
- [ ] **Step 2: 失敗を確認** — `AttributeError: build_task3`。
- [ ] **Step 3: `build_task3` を実装** — 到達圏ポリゴンは細かい穴が多いので `simplify_deg` を調整してサイズ上限(1MB)を満たす。穴(内側リング)は残す。
- [ ] **Step 4: 通過を確認** — 5件 PASS。`git status` を確認。

---

### Task 5: 分類モジュール `classify.js`

**Files:** Create: `html_src/classify.js`, `html_src/tests/classify.test.mjs`

**Interfaces:**
- Produces(ブラウザでは `window.Classify`、Nodeでは `module.exports`):
  - `classify(values: number[], mode: "equal" | "quantile" | "jenks", k: number) -> number[]` — `null`/`NaN` を除いた値から、**昇順の境界 `k+1` 個**(先頭=最小、末尾=最大)を返す。
  - `classIndex(value: number, breaks: number[]) -> number` — `0..k-1`。`value` が最大値のとき `k-1`。範囲外はクランプ。

- [ ] **Step 1: 失敗するテストを書く** — `classify.test.mjs`(`node:test`):`equal` は `[0,10]`, k=2 → `[0,5,10]`;`quantile` は `[1,2,3,4]`, k=2 → 先頭 1、中央 2.5、末尾 4;`jenks` は `[1,2,3,10,11,12]`, k=2 → 中央境界が 3 と 10 の間(3 以上 10 未満);`null`/`NaN` は無視される;`classIndex` が最小=0・最大=k-1;**重複値**(`[5,5,5,5]`, k=3)でも境界が昇順(非減少)で長さ k+1、`classIndex` が例外を出さない;異なる値が k 未満(`[1,2]`, k=5)でも同様。
- [ ] **Step 2: 失敗を確認** — `node --test 2026/qgis/html_src/tests/` → モジュールなしで FAIL。
- [ ] **Step 3: 実装** — `jenks` は Fisher-Jenks の動的計画法(値をソートして分散最小化)。値の数が k 以下なら退化した境界を返す。
- [ ] **Step 4: 通過を確認** — 全テスト PASS。`git status` を確認。

---

### Task 6: SVGサムネイル生成

**Files:** Create: `html_src/thumbnails.py`, `html_src/tests/test_thumbnails.py`

**Interfaces:**
- Produces: `thumbnails.svg_thumbnail(layers: list[tuple[dict, dict]], width: int = 480, height: int = 300) -> str` — `layers` は `(FeatureCollection, style)` の並び。`style` = `{"fill": str | Callable[[dict], str] | None, "stroke": str | None, "stroke_width": float, "opacity": float}`。全レイヤの外接bboxをビューに収め、緯度経度は等距円筒(経度に `cos(緯度)` を掛ける)で投影。Polygon / MultiPolygon / LineString / MultiLineString / Point を描く。返り値は `<svg ...>…</svg>` 文字列(`role="img"` と `aria-label` なし → 呼び出し側で付ける)。

- [ ] **Step 1: 失敗するテストを書く** — `test_polygon_becomes_path`(`<path` を含み、`fill` 色が反映)、`test_fill_callable_per_feature`(地物ごとに異なる色)、`test_point_becomes_circle`、`test_empty_layers_returns_valid_svg`(`<svg` で始まり `</svg>` で終わる)、`test_coordinates_stay_inside_viewbox`(`path` の数値が 0..width/height 内)、`test_hole_uses_evenodd`(穴付きポリゴンで `fill-rule="evenodd"`)。
- [ ] **Step 2: 失敗を確認** — `ModuleNotFoundError: thumbnails`。
- [ ] **Step 3: 実装** — 標準ライブラリのみ。座標は小数1桁に丸めてサイズを抑える。
- [ ] **Step 4: 通過を確認** — 6件 PASS。`git status` を確認。

---

### Task 7: ページの骨格(テンプレート、CSS、タブ、ビルド)

**Files:** Create: `html_src/build.py`, `template.html`, `style.css`, `app.js`, `content/{start,task1,task2,task3,limits}.html`(各ファイルは見出しだけの仮本文)、`tests/test_build.py`。Output: `2026/qgis/qgis_session.html`

**Interfaces:**
- Consumes: `data_prep.build_task1/2/3`、`thumbnails.svg_thumbnail`、Task 5の `classify.js`、同梱Leaflet。
- Produces:
  - `build.assemble(data: dict, thumbs: dict[str, str], src_dir: Path) -> str` — テンプレートの `{{style}}` `{{leaflet_css}}` `{{leaflet_js}}` `{{data_json}}`(`</` を `<\/` にエスケープ)`{{classify_js}}` `{{app_js}}` `{{map_task1_js}}` `{{map_task2_js}}` `{{map_task3_js}}` `{{thumb_task1}}` … `{{content_start}}` `{{content_task1}}` … を置換した完全なHTML文字列を返す。未置換の `{{…}}` が残れば `ValueError`。
  - `build.main() -> Path` — データを作り、サムネイルを作り(Task 1 = 率で色分け、Task 2 = 道路ライン+10分圏、Task 3 = 30分圏+境界)、HTMLを `2026/qgis/qgis_session.html` に書く。
  - `app.js`: `window.showTab(id: "task1"|"task2"|"task3"|"limits") -> void`。タブのDOM = `button[data-tab]`、パネル = `section[data-panel]`。初回表示時に `window.MapInit[id]?.(...)` を呼び、2回目以降は `map.invalidateSize()`。`hashchange`/`popstate` に追従し、**未知のハッシュは `task1`**。landingのサムネイルカードは `a[href="#taskN"]`。

- [ ] **Step 1: 失敗するテストを書く** — `test_build.py`: `test_assemble_has_four_tabs`(`data-tab="task1"` など4つ)、`test_no_unreplaced_placeholders`、`test_no_external_resources_except_tiles`(`<script src=`、`<link ... href=`(stylesheet)、`<img src="http`、`@import`、`<iframe` が無い。本文中の `<a href="https://…">` は許可。実行時に取得する外部URLはタイルURLだけ)、`test_footer_attribution`(OpenStreetMap / MLIT / e-Stat を含む)、`test_json_embedding_escapes_script_end`(`</script>` を含むデータが埋め込まれてもページが壊れない)、`test_html_lang_is_en`。
- [ ] **Step 2: 失敗を確認** — `ModuleNotFoundError: build`。
- [ ] **Step 3: `template.html`・`style.css`・`app.js` を実装** — ダークテーマ(CSS変数)、上部の粘着タブ、landing(3カード+タイトル+1行のゴール説明)、Start hereの枠、フッター。375px幅で崩れないこと(タブは折り返しまたは横スクロール、ページ全体は横スクロールしない)。`prefers-reduced-motion` を尊重。
- [ ] **Step 4: `build.py` を実装** — `python3 2026/qgis/html_src/build.py` で出力。
- [ ] **Step 5: ユニットテスト通過を確認** — 6件 PASS。
- [ ] **Step 6: ビルド実行とブラウザ確認** — `python3 2026/qgis/html_src/build.py`。`python3 -m http.server 8765 --directory 2026/qgis` をバックグラウンドで起動し、Playwright(`browser_navigate http://localhost:8765/qgis_session.html#task3`)で:パネル `task3` が表示、タブ `task3` が `aria-selected="true"`、タブをクリックすると URL のハッシュが変わり、ブラウザの戻る(`browser_navigate_back`)で前のタブに戻る、`#nonsense` で `task1`、`browser_console_messages` にエラーなし。
- [ ] **Step 7: `git status` を確認。**

---

### Task 8: Task 1の地図(件数↔率、分類Mode)

**Files:** Create: `html_src/map_task1.js`; Modify: `template.html`(地図コンテナ)、`style.css`、`tests/test_build.py`

**Interfaces:**
- Consumes: `window.DATA.task1`、`window.Classify`、Leaflet `L`。
- Produces: `window.MapInit.task1(container: HTMLElement, data: object) -> L.Map`。UI = 指標トグル(Count `pr_brazil` / Rate `rate_brazil`)、Mode選択(Equal interval / Quantile / Natural breaks)、クラス数(3–7、既定5)、凡例(境界値を表示し、切替で再計算)。シーケンシャル単色系の配色(`dataviz` スキルに従う)。`null` の地物は**灰色のハッチ風または明確に区別できる灰色**で、分類から除外。ツールチップ = 名称(漢字)+ 現在の指標値+ **`n = pr_brazil / pr_all`**(Review Focus 2)。背景タイルは `tileerror` を握りつぶし、暗色の単色背景にフォールバック(Review Focus 3)。

- [ ] **Step 1: 失敗するテストを書く** — `test_build.py::test_task1_map_markup`:出力HTMLに `id="map-task1"`、Mode選択の3つの値(`equal` `quantile` `jenks`)、指標トグル(`count` `rate`)が含まれる。
- [ ] **Step 2: 失敗を確認** — テスト FAIL。
- [ ] **Step 3: 実装。**
- [ ] **Step 4: ブラウザで確認**(Task 7 Step 6と同じサーバ)— `#task1` を開き、`browser_evaluate` で: ① 70地物が描画されている(Leaflet のレイヤ数)、② `23000` の塗りが他と異なる灰色、③ Modeを `jenks` に変えると凡例の境界値が変わる、④ 率に切り替えると、設楽町(`23561`)の率ツールチップに `3 / 7` が含まれる、⑤ `browser_network_requests` を失敗(オフライン相当)にしてもコンソールに未処理例外がない(タイルのドメインを `browser_run_code_unsafe` でブロックして確認)。
- [ ] **Step 5: `git status` を確認。**

---

### Task 9: Task 2の地図(川島病院の徒歩10分)

**Files:** Create: `html_src/map_task2.js`; Modify: `template.html`, `style.css`, `tests/test_build.py`

**Interfaces:**
- Consumes: `window.DATA.task2`。
- Produces: `window.MapInit.task2(container, data) -> L.Map`。レイヤのチェックボックス = Ward boundary / 10-min reach / Population mesh / Walkable roads / Hospital。メッシュは `pop_est` で色分け(ツールチップに推計人口)。道路ラインは明るい色の線。病院は円マーカー(ラベル「川島病院」)。パネルに `Estimated residents within the 10-minute reach: ≈5,421` と、**Task 3とは方式が異なる**旨の1行。地図の初期範囲は10分圏に合わせる。

- [ ] **Step 1: 失敗するテストを書く** — `test_task2_map_markup`:`id="map-task2"`、5つのレイヤ切替、方式が異なる旨の文言(`different method`)。
- [ ] **Step 2: 失敗を確認。**
- [ ] **Step 3: 実装。**
- [ ] **Step 4: ブラウザで確認** — `#task2` で、チェックを外すとそのレイヤが消える/付けると戻る(`browser_click` → `browser_evaluate` で `map.hasLayer`)、合計表示が `5,421`(5420.9の丸め)、コンソールエラーなし。
- [ ] **Step 5: `git status` を確認。**

---

### Task 10: Task 3の地図(10/20/30分スライダー)

**Files:** Create: `html_src/map_task3.js`; Modify: `template.html`, `style.css`, `tests/test_build.py`

**Interfaces:**
- Consumes: `window.DATA.task3`。
- Produces: `window.MapInit.task3(container, data) -> L.Map`。スライダー `input[type=range]` は3段階(10/20/30)、キーボード操作可。選択中の圏域だけを表示(病院41点と境界は常時)。読み出し = `minutes`、`percent`(小数2桁、例 `62.60%`)、`accessible / total`(例 `109,453 of 174,834 residents`)、`outside`。常時表示の注意書き = `Approximate, potential access — not actual use of care` と方式の説明1行(Task 2の方式とは異なる)。

- [ ] **Step 1: 失敗するテストを書く** — `test_task3_map_markup`:`id="map-task3"`、`type="range"` が `min="10" max="30" step="10"`、`Approximate` の文言。
- [ ] **Step 2: 失敗を確認。**
- [ ] **Step 3: 実装。**
- [ ] **Step 4: ブラウザで確認** — `#task3` でスライダーを10/20/30に動かし(`browser_evaluate` で `input` イベント)、読み出しが `17.90%` / `46.61%` / `62.60%` と `109,453 of 174,834` になる。
- [ ] **Step 5: `git status` を確認。**

---

### Task 11: Task 1タブ本文(クリック単位の手順)

**Files:** Modify: `html_src/content/task1.html`, `tests/test_build.py`

**内容(英語、初心者向け、QGIS 3.44のメニュー名)。** 元資料は `qgis_for_socialsciences_en.md` と `qgis_for_socialsciences_en_slides.md`(Hands-on 1–5 と Pitfalls)。

- 冒頭に目標1行と所要約25分。事前配布データ2点へのリンク(`https://github.com/NbtKmy/lectures/blob/main/2026/assets/aichi_admin_fields2025.geojson`、`.../aichi_permanent_residents_202512.csv`)。
- 番号付き手順(ダイアログの入力値まで): ① 背景タイル(Layer > Add Layer > Add XYZ Layer、GSI標準タイルURL)、② GeoJSONをドラッグ&ドロップ、属性テーブルで `N03_007` を確認、③ CSVを追加し、Properties > Joins で `city_code` ↔ `N03_007`、④ Symbology > Graduated、Value = `pr_brazil`、カラーランプ、Classify、⑤ Modeを切り替えて比較(**驚き1**)、⑥ 率 `pr_brazil / pr_all × 100` のフィールド計算(Field calculator)で件数と率を比較(**驚き2**)、⑦ 任意: Print Layoutで画像出力。
- 「Watch out」(2〜3点): 小さい数の率、欠損≠0(`23000`)、定義の違い。各1〜2行で Limits タブへ誘導(`<a href="#limits">`)。
- 地図(Task 8)へのリンクは本文内に1行(「same maps, in your browser」)。
- 注記「Menu names follow QGIS 3.44; other versions differ slightly.」

- [ ] **Step 1: 失敗するテストを書く** — `test_task1_content`:出力HTMLの `task1` パネルに、上記2つのGitHubリンク、`Add XYZ Layer`、`Joins`、`Graduated`、`N03_007`、`city_code`、`pr_brazil`、`3.44`、`href="#limits"` が含まれ、`<ol` が1つ以上ある。
- [ ] **Step 2: 失敗を確認。**
- [ ] **Step 3: 本文を書く。** 1手順1アクションに分け、日本語UIの訳語は併記しない(英語UIで説明する)。
- [ ] **Step 4: 通過とブラウザ確認** — `#task1` を開いて、手順と地図が同じページで読めること、375px幅で崩れないこと。
- [ ] **Step 5: `git status` を確認。**

---

### Task 12: Task 2・Task 3タブ本文

**Files:** Modify: `html_src/content/task2.html`, `content/task3.html`, `tests/test_build.py`

**内容(英語)。** 元資料は `demo1_qgis_guidance.md` 第8–9章(Task 2)、第12–14・16章(Task 3)。

- **Task 2**(約15分、完成品ツアー): 目標 = 「1つの病院から徒歩10分で行ける範囲に、何人住んでいるか」。ツアーの順(開くプロジェクト、レイヤのON/OFF、道路ライン、10分圏、メッシュをクリックして属性、合計5,421人)。使うレイヤのファイル名一覧(`moriyama_admin_field.gpkg` ほか6つ)と、リポジトリへのリンク。**圏の作り方はQNEAT3等の名前を出さず**「a smoothed surface of walking time over the road network, cut at 10 minutes」と平易に説明。**方式が異なる**断り書き(Task 3とは別の方法で、数字は比較しない)。Watch outを2点(面積按分=メッシュ内一様の仮定、徒歩速度4km/h)→ Limits へ。
- **Task 3**(スライドのみ、約7分): 問い = 「守山区民のうち、徒歩圏内に病院がある人は何%か」。4工程(41病院の到達圏 → 時間別にDissolve → 守山区でClip → メッシュとの面積按分で人口集計)。結果の表(10/20/30分: 17.90% / 46.61% / 62.60%、分母 174,833.87、圏内 31,287.80 / 81,492.41 / 109,452.93)。重複排除の重要性(病院別の人数を足してはいけない)。方式の断り書き。**「近似・潜在的アクセス」**を明記。

- [ ] **Step 1: 失敗するテストを書く** — `test_task2_task3_content`:`task2` パネルに `川島病院`、`different method`、`5,421`、`moriyama_admin_field.gpkg`、`href="#limits"` が、`task3` パネルに `17.90%`、`46.61%`、`62.60%`、`174,833.87`、`Dissolve`、`Clip`、`potential` が含まれ、**`QNEAT3` が含まれない**。
- [ ] **Step 2: 失敗を確認。**
- [ ] **Step 3: 本文を書く。**
- [ ] **Step 4: 通過とブラウザ確認** — 両タブの本文と地図が同じページで読める。
- [ ] **Step 5: `git status` を確認。**

---

### Task 13: Limitsと Start here

**Files:** Modify: `html_src/content/limits.html`, `content/start.html`, `tests/test_build.py`

**内容(英語)。** 設計書§2の Limits 3点を、初心者向けに各3〜5文で。

- Limits: ① 30mバッファは近似(幅を変えると人口が変わる。道路網はOSMの暫定ルールで接続性は未検証)、② 人口は面積按分(メッシュ内一様の仮定、人口NULLメッシュ96件はNULLの理由が未検証で0としていない)、③ 潜在的な地理アクセスであり、実際の受診行動・診療の可用性ではない。「So what for your own research」を最後に1段落(自分のデータで問うべき3つ: 分母は何か、単位は何か、欠損は何か)。
- Start here: セッションの流れと所要時間(導入5 / Task 1 25 / Task 2 15 / Task 3 7 / Limits 6 / 締め2)、必要なもの(QGIS 3.44推奨、データ2点)、出典の一覧(GSI、MLIT N03/P04、e-Stat 国勢調査メッシュ、在留外国人統計、OSM、総務省コード)へのリンク。

- [ ] **Step 1: 失敗するテストを書く** — `test_limits_and_start_content`:`limits` に `approximation`、`96`、`potential` が、`start` に `3.44`、`MLIT`、`e-Stat`、`OpenStreetMap` が含まれる。
- [ ] **Step 2: 失敗を確認。**
- [ ] **Step 3: 本文を書く。**
- [ ] **Step 4: 通過を確認。**
- [ ] **Step 5: `git status` を確認。**

---

### Task 14: `2026/assets/README.md`(出典と「参加者が使うのはここだけ」)

**Files:** Create: `2026/assets/README.md`

- [ ] **Step 1: README を書く** — (英語)冒頭に「Participants only need: `aichi_admin_fields2025.geojson` and `aichi_permanent_residents_202512.csv`」。Task 2用ファイル一覧(Task 12と同じ6つ+`moriyama_hospitals.gpkg`)、Task 3用ファイル、各ファイルの出典・ライセンス・基準日(MLIT N03-2025 CC BY 4.0、MLIT P04、e-Stat 令和2年国勢調査メッシュ、OSM ODbL、在留外国人統計 2025年12月、総務省コード)。その他の `assets/` のファイルは作業用で、`.gitignore` で除外されていると一言。
- [ ] **Step 2: 内容を確認** — `grep -c "N03" 2026/assets/README.md` 等で出典が揃っているか。`grep -rn "aichi_admin_fields.gpkg" 2026 --include='*.md'` が空であることを確認(古い名前の参照が残っていないこと)。
- [ ] **Step 3: `git status` を確認。**

---

### Task 15: 最終確認(ブラウザ・サイズ・数値・保険)

**Files:** なし(確認のみ。不具合は該当Taskの修正として直す)。

- [ ] **Step 1: 全テスト** — Python と Node の全テスト PASS。
- [ ] **Step 2: ビルドとサイズ** — `python3 2026/qgis/html_src/build.py`。`ls -lh 2026/qgis/qgis_session.html` が **6MB以下**。
- [ ] **Step 3: 数値の突き合わせ** — ページ内の数字(17.90 / 46.61 / 62.60、174,833.87、109,452.93、5,421、70地物、41病院)が `moriyama_analysis_B_accessibility.csv` と `data_prep` のテストの期待値と一致。
- [ ] **Step 4: ブラウザ確認(デスクトップ)** — 4タブすべてを `browser_navigate` で直接開き、`browser_take_screenshot` を確認。コンソールエラーなし。landingの3サムネイルから各タブへ移動できる。
- [ ] **Step 5: ブラウザ確認(スマートフォン幅)** — `browser_resize` で 375×800:ページの横スクロールなし(`document.documentElement.scrollWidth <= innerWidth`)、地図の高さ ≥ 280px。
- [ ] **Step 6: オフライン確認** — タイルのドメインをブロックして再読み込み:ポリゴンが暗色背景に描画され、コンソールに未処理例外なし(Review Focus 3)。
- [ ] **Step 7: `file://` で開く** — 生成HTMLを `file://` で開いて(`browser_navigate file:///Users/nobu/lectures/2026/qgis/qgis_session.html#task3`)、データ・地図が動く(設計書「ダブルクリックで開ける」)。
- [ ] **Step 8: 結果を報告** — 追跡対象に入る新規ファイルの一覧と、`git status` を提示。コミットはユーザーの指示を待つ。
