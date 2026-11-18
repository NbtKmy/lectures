import test from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { readFileSync } from "node:fs";

const require = createRequire(import.meta.url);
globalThis.proj4 = require("../vendor/proj4/proj4.js");
const { zoneAt, parseLatLon, search, toPlane } = require("../lookup.js");

const read = (rel) => JSON.parse(readFileSync(new URL(rel, import.meta.url), "utf-8"));
const ZONES = read("../data/zones.geojson");
const PLACES = read("../data/places.json");

// [label, lat, lon, zone] — checked against https://www.gsi.go.jp/LAW/heimencho.html
const SAMPLES = [
  ["Moriyama, Nagoya", 35.203, 136.977, 7], ["Sapporo", 43.062, 141.354, 12],
  ["Hakodate", 41.769, 140.729, 11], ["Kushiro", 42.985, 144.381, 13],
  ["Shinjuku", 35.69, 139.7, 9], ["Hachijojima", 33.11, 139.79, 9],
  ["Chichijima", 27.094, 142.191, 14], ["Okinotorishima", 20.423, 136.0739, 18],
  ["Minamitorishima", 24.287, 153.981, 19], ["Naha", 26.212, 127.681, 15],
  ["Ishigaki", 24.34, 124.156, 16], ["Minamidaito", 25.846, 131.247, 17],
  ["Nagasaki", 32.75, 129.878, 1], ["Kagoshima city", 31.596, 130.557, 2],
  ["Amami (Naze)", 28.377, 129.494, 1], ["Niigata", 37.916, 139.036, 8],
  // ~2 km either side of the Gifu (VII) / Nagano (VIII) border near Magome
  ["Nakatsugawa side", 35.52, 137.55, 7], ["Nagiso side", 35.58, 137.62, 8],
];

test("sample points land in the expected zone", () => {
  for (const [label, lat, lon, zone] of SAMPLES) {
    assert.equal(zoneAt(lat, lon, ZONES), zone, label);
  }
});

test("open sea is no zone", () => {
  assert.equal(zoneAt(35.0, 150.0, ZONES), null);
  assert.equal(zoneAt(34.0, 138.5, ZONES), null); // Suruga Bay mouth
});

test("parseLatLon handles order and symbols", () => {
  assert.deepEqual(parseLatLon("35.19, 136.97"), [35.19, 136.97]);
  assert.deepEqual(parseLatLon("136.97, 35.19"), [35.19, 136.97]);
  assert.deepEqual(parseLatLon("35.19 136.97"), [35.19, 136.97]);
  assert.deepEqual(parseLatLon(" 35.19°N, 136.97°E "), [35.19, 136.97]);
  assert.equal(parseLatLon("abc"), null);
  assert.equal(parseLatLon("0, 0"), null);
  assert.equal(parseLatLon("Osaka"), null);
});

test("search finds Osaka in four spellings", () => {
  for (const q of ["Ōsaka", "osaka", "Osaka-shi", "大阪"]) {
    const hits = search(PLACES, q);
    assert.ok(hits.length > 0, q);
    assert.ok(/osaka|大阪/i.test(hits[0].name.normalize("NFKD").replace(/[\u0300-\u036f]/g, "")), `${q} -> ${hits[0].name}`);
  }
});

test("search hits carry the stored zone", () => {
  const rows = [["Urakawa", "urakawa", 42.1556, 142.7836, 12]];
  assert.deepEqual(search(rows, "urakawa"), [{ name: "Urakawa", lat: 42.1556, lon: 142.7836, zone: 12 }]);
});

test("search returns at most the limit and nothing for blanks", () => {
  assert.ok(search(PLACES, "a", 5).length <= 5);
  assert.deepEqual(search(PLACES, "  "), []);
});

test("toPlane at the origin is 0,0", () => {
  const p = toPlane(36, 137 + 10 / 60, { zone: 7, origin_lat: 36, origin_lon: 137 + 10 / 60 });
  assert.ok(Math.abs(p.x) < 0.001 && Math.abs(p.y) < 0.001, JSON.stringify(p));
});

test("toPlane matches PROJ for Nagoya Station", () => {
  // gdaltransform -s_srs EPSG:6668 -t_srs EPSG:6675: easting -25972.1653, northing -91941.6689
  const p = toPlane(35.170915, 136.881537, { zone: 7, origin_lat: 36, origin_lon: 137 + 10 / 60 });
  assert.ok(Math.abs(p.x - -91941.6689) < 0.01, `x ${p.x}`);
  assert.ok(Math.abs(p.y - -25972.1653) < 0.01, `y ${p.y}`);
});
