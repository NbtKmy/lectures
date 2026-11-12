/* Task 1 map: permanent residents (Brazil) by municipality in Aichi. */
(function () {
  "use strict";

  // Sequential blue for the dark surface: near-zero recedes into the background, large values glow.
  // Steps 600 -> 150 of the shared blue ramp.
  var RAMP = ["#184f95", "#1c5cab", "#256abf", "#2a78d6", "#3987e5", "#5598e7", "#6da7ec", "#86b6ef", "#9ec5f4", "#b7d3f6"];
  var NO_DATA = "#4a4d55";
  var SMALL_BASE = 100; // total permanent residents below this: read the rate with care

  var fmt = function (n) { return Number(n).toLocaleString("en-US"); };

  function pickColors(k) {
    var out = [];
    for (var i = 0; i < k; i++) out.push(RAMP[Math.round((i * (RAMP.length - 1)) / Math.max(k - 1, 1))]);
    return out;
  }

  window.MapInit = window.MapInit || {};
  window.MapInit.task1 = function (container, data) {
    var root = container.closest(".mapbox");
    var legendEl = root.querySelector("[data-legend]");
    var noteEl = root.querySelector("[data-note]");
    var measureBtns = Array.prototype.slice.call(root.querySelectorAll("[data-measure]"));
    var modeSel = root.querySelector("[data-mode]");
    var classSel = root.querySelector("[data-classes]");

    var state = { measure: "count", mode: "equal", k: 5, breaks: [], colors: [] };
    var map = window.makeBaseMap(container, { zoomSnap: 0.25 });

    function valueOf(props) {
      return state.measure === "rate" ? props.rate_brazil : props.pr_brazil;
    }

    function colorFor(props) {
      var v = valueOf(props);
      if (v === null || v === undefined) return NO_DATA;
      return state.colors[Classify.classIndex(v, state.breaks)];
    }

    function styleFor(feature) {
      var p = feature.properties;
      var nodata = valueOf(p) === null || valueOf(p) === undefined;
      var small = state.measure === "rate" && p.pr_all !== null && p.pr_all < SMALL_BASE;
      return {
        fillColor: colorFor(p),
        fillOpacity: nodata ? 0.7 : 0.88,
        color: small ? "#f2b84b" : "#9aa6c4",
        weight: small ? 1.8 : 0.5,
        dashArray: small ? "4 3" : nodata ? "3 3" : null,
        opacity: small ? 1 : 0.55,
      };
    }

    function tooltipFor(p) {
      var lines = [];
      if (p.pr_all === null) {
        lines.push("no data");
      } else {
        lines.push(
          state.measure === "rate"
            ? "Brazil share: " + p.rate_brazil.toFixed(2) + "%"
            : "Brazil: " + fmt(p.pr_brazil) + " residents"
        );
        lines.push("n = " + fmt(p.pr_brazil) + " / " + fmt(p.pr_all)); // keep the small-numbers problem visible
      }
      var box = document.createElement("div");
      var title = document.createElement("strong");
      title.textContent = p.name;
      box.appendChild(title);
      lines.forEach(function (text) {
        var div = document.createElement("div");
        div.textContent = text;
        box.appendChild(div);
      });
      return box;
    }

    var layer = L.geoJSON(data, {
      style: styleFor,
      onEachFeature: function (feature, lyr) {
        lyr.bindTooltip(function () { return tooltipFor(feature.properties); }, { sticky: true });
        lyr.on("mouseover", function () { lyr.setStyle({ weight: 2, opacity: 1, color: "#ffffff" }); lyr.bringToFront(); });
        lyr.on("mouseout", function () { layer.resetStyle(lyr); });
      },
    }).addTo(map);
    map.fitBounds(layer.getBounds());
    map.dataLayer = layer; // handy for checks in the browser console

    function rangeLabel(lo, hi) {
      if (state.measure === "rate") return lo.toFixed(1) + " – " + hi.toFixed(1) + "%";
      return fmt(Math.round(lo)) + " – " + fmt(Math.round(hi));
    }

    function drawLegend() {
      legendEl.innerHTML = "";
      state.colors.forEach(function (c, i) {
        var li = document.createElement("li");
        var sw = document.createElement("span");
        sw.className = "swatch";
        sw.style.background = c;
        li.appendChild(sw);
        li.appendChild(document.createTextNode(rangeLabel(state.breaks[i], state.breaks[i + 1])));
        legendEl.appendChild(li);
      });
      var nd = document.createElement("li");
      nd.innerHTML = '<span class="swatch nodata"></span>';
      nd.appendChild(document.createTextNode("No data (unassigned area)"));
      legendEl.appendChild(nd);
      if (state.measure === "rate") {
        var sm = document.createElement("li");
        sm.innerHTML = '<span class="swatch" style="border:2px dashed #f2b84b;background:transparent"></span>';
        sm.appendChild(document.createTextNode("Fewer than " + SMALL_BASE + " residents in total: read with care"));
        legendEl.appendChild(sm);
      }
    }

    function refresh() {
      var values = data.features.map(function (f) { return valueOf(f.properties); });
      state.breaks = Classify.classify(values, state.mode, state.k);
      state.colors = pickColors(state.k);
      layer.setStyle(styleFor);
      drawLegend();
      noteEl.textContent =
        state.measure === "rate"
          ? "Rate = Brazilian permanent residents as a share of all permanent residents. It jumps around where the total is tiny: Shitara (設楽町) has 7 permanent residents in all, so 3 Brazilians already read as 42.86%."
          : "Colours show permanent residents with Brazilian nationality. Counts mostly follow where many people live; switch to Rate and see which places move.";
      measureBtns.forEach(function (b) {
        b.setAttribute("aria-pressed", b.getAttribute("data-measure") === state.measure ? "true" : "false");
      });
    }

    measureBtns.forEach(function (b) {
      b.addEventListener("click", function () { state.measure = b.getAttribute("data-measure"); refresh(); });
    });
    modeSel.addEventListener("change", function () { state.mode = modeSel.value; refresh(); });
    classSel.addEventListener("change", function () { state.k = parseInt(classSel.value, 10); refresh(); });

    refresh();
    return map;
  };
})();
