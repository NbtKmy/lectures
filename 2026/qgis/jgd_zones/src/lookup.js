/* Zone lookup helpers shared by the browser (window.Lookup) and Node tests.
 *
 * zoneAt(lat, lon, zonesGeo) -> zone number 1..19, or null outside every zone.
 * parseLatLon(text) -> [lat, lon] inside Japan's extent, or null.
 * search(places, query, limit) -> [{name, lat, lon}] from rows [name, key, lat, lon].
 * toPlane(lat, lon, zone) -> {x: northing, y: easting} in metres (needs the global proj4).
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.Lookup = factory();
})(this, function () {
  "use strict";

  function inRing(x, y, ring) {
    let inside = false;
    for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
      const xi = ring[i][0], yi = ring[i][1], xj = ring[j][0], yj = ring[j][1];
      if ((yi > y) !== (yj > y) && x < xi + ((y - yi) * (xj - xi)) / (yj - yi)) inside = !inside;
    }
    return inside;
  }

  function inPolygon(x, y, rings) {
    if (!inRing(x, y, rings[0])) return false;
    for (let h = 1; h < rings.length; h++) if (inRing(x, y, rings[h])) return false;
    return true;
  }

  function bbox(geometry) {
    if (geometry._bbox) return geometry._bbox;
    const b = [Infinity, Infinity, -Infinity, -Infinity];
    const polys = geometry.type === "MultiPolygon" ? geometry.coordinates : [geometry.coordinates];
    for (const p of polys) for (const [x, y] of p[0]) {
      if (x < b[0]) b[0] = x;
      if (y < b[1]) b[1] = y;
      if (x > b[2]) b[2] = x;
      if (y > b[3]) b[3] = y;
    }
    Object.defineProperty(geometry, "_bbox", { value: b });
    return b;
  }

  function zoneAt(lat, lon, zonesGeo) {
    for (const f of zonesGeo.features) {
      const g = f.geometry, b = bbox(g);
      if (lon < b[0] || lon > b[2] || lat < b[1] || lat > b[3]) continue;
      const polys = g.type === "MultiPolygon" ? g.coordinates : [g.coordinates];
      for (const p of polys) if (inPolygon(lon, lat, p)) return f.properties.zone;
    }
    return null;
  }

  const LAT = [20, 46], LON = [122, 154];
  const ok = (lat, lon) => lat >= LAT[0] && lat <= LAT[1] && lon >= LON[0] && lon <= LON[1];

  function parseLatLon(text) {
    const nums = String(text).match(/-?\d+(?:\.\d+)?/g);
    if (!nums || nums.length !== 2) return null;
    const a = parseFloat(nums[0]), b = parseFloat(nums[1]);
    if (ok(a, b)) return [a, b];
    if (ok(b, a)) return [b, a];
    return null;
  }

  // Same rules as prep.fold: lower case, macrons dropped, municipal suffix and separators removed.
  function fold(name) {
    let s = String(name).trim().toLowerCase().normalize("NFKD").replace(/[̀-ͯ]/g, "");
    s = s.replace(/[-\s](shi|ku|machi|cho|mura|son|gun)$/, "");
    return s.replace(/[-\s']/g, "");
  }

  function search(places, query, limit) {
    const q = fold(query);
    if (!q) return [];
    const n = limit || 8;
    const prefix = [], inner = [];
    for (const row of places) {
      const i = row[1].indexOf(q);
      if (i === 0) prefix.push(row);
      else if (i > 0) inner.push(row);
    }
    const byLength = (a, b) => a[0].length - b[0].length;
    return prefix.sort(byLength).concat(inner.sort(byLength)).slice(0, n)
      .map((r) => ({ name: r[0], lat: r[2], lon: r[3] }));
  }

  function toPlane(lat, lon, zone) {
    const def = "+proj=tmerc +lat_0=" + zone.origin_lat + " +lon_0=" + zone.origin_lon +
      " +k=0.9999 +x_0=0 +y_0=0 +ellps=GRS80 +units=m +no_defs";
    const p = getProj4()(def, [lon, lat]);
    return { x: p[1], y: p[0] };
  }

  function getProj4() {
    if (typeof proj4 === "function") return proj4;
    throw new Error("proj4 is not loaded");
  }

  return { zoneAt, parseLatLon, search, toPlane, fold };
});
