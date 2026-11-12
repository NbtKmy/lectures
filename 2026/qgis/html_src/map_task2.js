/* Task 2 map: Kawashima Hospital, 10-minute walking reach and the population inside it. */
(function () {
  "use strict";

  var RAMP = ["#184f95", "#256abf", "#3987e5", "#6da7ec", "#b7d3f6"]; // low -> high, dark surface
  var fmt = function (n) { return Math.round(n).toLocaleString("en-US"); };

  window.MapInit = window.MapInit || {};
  window.MapInit.task2 = function (container, data) {
    var root = container.closest(".mapbox");
    var map = window.makeBaseMap(container, { zoomSnap: 0.25 });

    // Panes keep the stacking order stable however the boxes are ticked on and off.
    var order = ["boundary", "reach", "mesh", "roads", "hospital"];
    order.forEach(function (name, i) {
      map.createPane("pane-" + name).style.zIndex = 410 + i * 10;
    });

    var values = data.mesh.features.map(function (f) { return f.properties.pop_est; });
    var breaks = Classify.classify(values, "equal", RAMP.length);
    var meshColor = function (v) { return RAMP[Classify.classIndex(v, breaks)]; };

    var layers = {
      boundary: L.geoJSON(data.boundary, {
        pane: "pane-boundary", interactive: false,
        style: { color: "#9aa6c4", weight: 1.2, dashArray: "6 4", fill: false },
      }),
      reach: L.geoJSON(data.reach, {
        pane: "pane-reach", interactive: false,
        style: { color: "#9ec5f4", weight: 1.5, fillColor: "#3987e5", fillOpacity: 0.12 },
      }),
      mesh: L.geoJSON(data.mesh, {
        pane: "pane-mesh",
        style: function (f) {
          return { color: "#0e1320", weight: 0.8, fillColor: meshColor(f.properties.pop_est), fillOpacity: 0.7 };
        },
        onEachFeature: function (f, lyr) {
          lyr.bindTooltip("≈" + fmt(f.properties.pop_est) + " residents (estimated)", { sticky: true });
        },
      }),
      roads: L.geoJSON(data.service_area, {
        pane: "pane-roads", interactive: false,
        style: { color: "#f2b84b", weight: 2.5, opacity: 0.95, lineCap: "round" },
      }),
      hospital: L.circleMarker(
        [data.hospital.geometry.coordinates[1], data.hospital.geometry.coordinates[0]],
        { pane: "pane-hospital", radius: 8, color: "#f2b84b", weight: 3, fillColor: "#ffffff", fillOpacity: 1 }
      ).bindTooltip(data.hospital.properties.name, { permanent: true, direction: "top", offset: [0, -8] }),
    };

    order.forEach(function (name) { layers[name].addTo(map); });
    map.fitBounds(layers.reach.getBounds().pad(0.15));
    map.layers = layers; // handy for checks in the browser console

    root.querySelectorAll("input[data-layer]").forEach(function (box) {
      box.addEventListener("change", function () {
        var layer = layers[box.getAttribute("data-layer")];
        if (box.checked) layer.addTo(map);
        else map.removeLayer(layer);
      });
    });

    var legend = root.querySelector("[data-legend]");
    RAMP.forEach(function (c, i) {
      var li = document.createElement("li");
      var sw = document.createElement("span");
      sw.className = "swatch";
      sw.style.background = c;
      li.appendChild(sw);
      li.appendChild(document.createTextNode(fmt(breaks[i]) + " – " + fmt(breaks[i + 1]) + " people per cell"));
      legend.appendChild(li);
    });

    var s = data.summary;
    root.querySelector("[data-total]").textContent = "≈" + fmt(s.total_pop_est);
    root.querySelector("[data-summary]").textContent =
      "Estimated residents within the 10-minute reach: ≈" + fmt(s.total_pop_est) +
      " (" + s.mesh_count + " mesh cells around " + s.hospital_name + ").";
    return map;
  };
})();
