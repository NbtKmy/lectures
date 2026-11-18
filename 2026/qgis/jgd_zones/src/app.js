/* Zone finder UI: map, search, coordinates, geolocation and the result card. */
(function () {
  "use strict";

  var DATA = JSON.parse(document.getElementById("zone-data").textContent);
  var INFO = {};
  DATA.info.forEach(function (z) { INFO[z.zone] = z; });

  // Six hues cycled by zone number: neighbouring zones (n, n+1) never share a colour.
  var HUES = ["#3987e5", "#f2b84b", "#4fbf8f", "#e5737a", "#a98be8", "#5cc6d6"];
  var colour = function (zone) { return HUES[(zone - 1) % HUES.length]; };

  var statusEl = document.getElementById("status");
  var card = document.getElementById("result");
  var input = document.getElementById("q");
  var hitsEl = document.getElementById("hits");

  var fmt = function (n, d) { return n.toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d }); };
  var esc = function (s) {
    return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; });
  };
  var say = function (msg) { statusEl.textContent = msg || ""; };

  /* Map: GSI pale tiles, darkened by CSS. Offline => the zones on a plain dark background. */
  var small = window.matchMedia("(max-width: 760px)").matches;
  var map = L.map("map", { zoomSnap: 0.5, worldCopyJump: false }).setView([36.5, 137.5], small ? 4 : 5);
  var tiles = L.tileLayer("https://cyberjapandata.gsi.go.jp/xyz/pale/{z}/{x}/{y}.png", {
    maxZoom: 18,
    attribution: '<a href="https://maps.gsi.go.jp/development/ichiran.html">地理院タイル</a> · N03 (MLIT) · GeoNames',
  });
  tiles.on("tileerror", function () { /* offline: keep the zones on the dark background */ });
  tiles.addTo(map);

  L.geoJSON(DATA.zones, {
    style: function (f) {
      return { color: colour(f.properties.zone), weight: 1.2, opacity: 0.9, fillColor: colour(f.properties.zone), fillOpacity: 0.28 };
    },
  }).addTo(map);
  map.on("click", function (e) { showAt(e.latlng.lat, e.latlng.lng); });

  // Roman-numeral labels; they are also the click target for zones too small to hit (XVIII, XIX).
  DATA.zones.features.forEach(function (f) {
    var p = f.properties, z = INFO[p.zone];
    L.circleMarker(p.label, { radius: 6, color: "#fff", weight: 1, fillColor: colour(p.zone), fillOpacity: 1 })
      .bindTooltip(z.roman, { permanent: true, direction: "right", className: "zone-label", offset: [6, 0] })
      .on("click", function (e) { L.DomEvent.stopPropagation(e); showAt(p.label[0], p.label[1], "Zone " + z.roman + " marker"); })
      .addTo(map);
  });

  // Label text only from zoom 5: below that the numerals of central Honshu overlap.
  var syncLabels = function () { map.getContainer().classList.toggle("labels-off", map.getZoom() < 5); };
  map.on("zoomend", syncLabels);
  syncLabels();

  var pin = null;

  function showAt(lat, lon, name, fly) {
    var zone = Lookup.zoneAt(lat, lon, DATA.zones);
    if (pin) pin.remove();
    pin = L.circleMarker([lat, lon], { radius: 8, color: "#0e1320", weight: 2, fillColor: "#fff", fillOpacity: 1, interactive: false }).addTo(map);
    if (fly) map.flyTo([lat, lon], Math.max(map.getZoom(), 8), { duration: 0.8 });
    highlightRow(zone);
    var where = name ? "<p class=\"card-place\">" + esc(name) + "</p>" : "";
    var coords = "<dt>Lat, lon</dt><dd>" + fmt(lat, 5) + ", " + fmt(lon, 5) + "</dd>";
    if (zone === null) {
      card.innerHTML = where + '<p class="card-zone">No zone</p>' +
        "<p>Not in a JGD2011 plane rectangular zone. Click on land, or zoom in for small islands.</p><dl>" + coords + "</dl>";
      say("");
      return;
    }
    var z = INFO[zone], xy = Lookup.toPlane(lat, lon, z);
    card.innerHTML = where +
      '<p class="card-zone">Zone ' + z.roman + ' <span lang="ja">(' + z.zone + "系)</span></p>" +
      '<div class="card-epsg"><code>EPSG:' + z.epsg + '</code><button type="button" class="btn btn-small" data-copy="EPSG:' + z.epsg + '">Copy</button></div>' +
      "<dl>" + coords +
      "<dt>X (north)</dt><dd>" + fmt(xy.x, 1) + " m</dd>" +
      "<dt>Y (east)</dt><dd>" + fmt(xy.y, 1) + " m</dd>" +
      "<dt>Origin</dt><dd>" + fmt(z.origin_lat, 4) + "°N, " + fmt(z.origin_lon, 4) + "°E</dd>" +
      "<dt>JGD2000</dt><dd>EPSG:" + z.epsg_jgd2000 + "</dd></dl>" +
      '<p class="card-note">Zone lines are simplified. Within a few hundred metres of a line, check the municipality in the table below.</p>';
    say("");
  }

  function highlightRow(zone) {
    Array.prototype.forEach.call(document.querySelectorAll("tr[data-zone]"), function (tr) {
      tr.classList.toggle("current", Number(tr.getAttribute("data-zone")) === zone);
    });
  }

  card.addEventListener("click", function (e) {
    var btn = e.target.closest("[data-copy]");
    if (!btn) return;
    var text = btn.getAttribute("data-copy");
    var done = function () { btn.textContent = "Copied"; setTimeout(function () { btn.textContent = "Copy"; }, 1500); };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, function () { say("Copy failed — select the code and copy it by hand."); });
    } else {
      say("Copy is not available here — select the code and copy it by hand.");
    }
  });

  /* Search: place names (offline list) or a pasted "lat, lon". */
  var hits = [], active = -1;

  function renderHits() {
    hitsEl.innerHTML = hits.map(function (h, i) {
      var zone = Lookup.zoneAt(h.lat, h.lon, DATA.zones);
      var tag = zone ? '<span class="hit-zone">' + INFO[zone].roman + "</span>" : "";
      return '<li role="option" id="hit-' + i + '" aria-selected="' + (i === active) + '" data-i="' + i + '">' + esc(h.name) + tag + "</li>";
    }).join("");
    hitsEl.hidden = hits.length === 0;
    input.setAttribute("aria-expanded", String(hits.length > 0));
    if (active >= 0) input.setAttribute("aria-activedescendant", "hit-" + active);
    else input.removeAttribute("aria-activedescendant");
  }

  function update() {
    var q = input.value;
    var ll = Lookup.parseLatLon(q);
    hits = ll ? [{ name: "Go to " + fmt(ll[0], 5) + ", " + fmt(ll[1], 5), lat: ll[0], lon: ll[1], coords: true }] : Lookup.search(DATA.places, q, 8);
    active = hits.length ? 0 : -1;
    renderHits();
    if (q.trim() && !hits.length) say("No match. Try another spelling, the Japanese name, or paste coordinates like 35.19, 136.97.");
    else say("");
  }

  function choose(i) {
    var h = hits[i];
    if (!h) return;
    hits = []; active = -1; renderHits();
    input.value = h.coords ? input.value : h.name;
    showAt(h.lat, h.lon, h.coords ? null : h.name, true);
  }

  input.addEventListener("input", update);
  input.addEventListener("keydown", function (e) {
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      if (!hits.length) return;
      e.preventDefault();
      active = (active + (e.key === "ArrowDown" ? 1 : hits.length - 1)) % hits.length;
      renderHits();
    } else if (e.key === "Escape") {
      hits = []; active = -1; renderHits();
    }
  });
  hitsEl.addEventListener("mousedown", function (e) {
    var li = e.target.closest("li[data-i]");
    if (li) { e.preventDefault(); choose(Number(li.getAttribute("data-i"))); }
  });
  input.addEventListener("blur", function () { setTimeout(function () { hits = []; active = -1; renderHits(); }, 100); });
  document.getElementById("search-form").addEventListener("submit", function (e) {
    e.preventDefault();
    if (!hits.length) update();
    choose(Math.max(active, 0));
  });

  /* My location */
  document.getElementById("locate").addEventListener("click", function () {
    var fail = function () { say("Location not available — click the map or type a place instead."); };
    if (!navigator.geolocation) return fail();
    say("Finding your location…");
    navigator.geolocation.getCurrentPosition(function (pos) {
      showAt(pos.coords.latitude, pos.coords.longitude, "Your location", true);
    }, fail, { enableHighAccuracy: false, timeout: 10000, maximumAge: 600000 });
  });
})();
