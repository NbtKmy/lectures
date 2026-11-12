/* Task 3 map: walking coverage of 41 hospitals at 10 / 20 / 30 minutes. */
(function () {
  "use strict";

  var fmt = function (n) { return Math.round(n).toLocaleString("en-US"); };

  window.MapInit = window.MapInit || {};
  window.MapInit.task3 = function (container, data) {
    var root = container.closest(".mapbox");
    var slider = root.querySelector('input[type="range"]');
    var map = window.makeBaseMap(container, { zoomSnap: 0.25 });

    ["boundary", "coverage", "hospitals"].forEach(function (name, i) {
      map.createPane("pane-" + name).style.zIndex = 410 + i * 10;
    });

    var boundary = L.geoJSON(data.boundary, {
      pane: "pane-boundary", interactive: false,
      style: { color: "#9aa6c4", weight: 1.5, dashArray: "6 4", fill: false },
    }).addTo(map);

    var coverage = {};
    Object.keys(data.coverage).forEach(function (m) {
      coverage[m] = L.geoJSON(data.coverage[m], {
        pane: "pane-coverage", interactive: false,
        style: { color: "#9ec5f4", weight: 1, fillColor: "#3987e5", fillOpacity: 0.5 },
      });
    });

    L.geoJSON(data.hospitals, {
      pane: "pane-hospitals",
      pointToLayer: function (f, latlng) {
        return L.circleMarker(latlng, { pane: "pane-hospitals", radius: 4, color: "#0e1320", weight: 1, fillColor: "#f2b84b", fillOpacity: 1 });
      },
      onEachFeature: function (f, lyr) { lyr.bindTooltip(f.properties.name); },
    }).addTo(map);

    map.fitBounds(boundary.getBounds().pad(0.1));

    var current = null;
    function show(minutes) {
      var key = String(minutes);
      if (current) map.removeLayer(coverage[current]);
      coverage[key].addTo(map);
      current = key;
      var s = data.stats[key];
      root.querySelector("[data-percent]").textContent = s.percent.toFixed(2) + "%";
      root.querySelector("[data-minutes]").textContent = key;
      root.querySelector("[data-count]").textContent =
        fmt(s.accessible) + " of " + fmt(s.total) + " residents; " + fmt(s.outside) + " live outside the reach.";
    }

    slider.addEventListener("input", function () { show(slider.value); });
    show(slider.value);
    return map;
  };
})();
