/* Classification helpers shared by the browser (window.Classify) and Node tests.
 *
 * classify(values, mode, k) -> k+1 ascending breaks [min, ..., max].
 * Class i holds the values in (breaks[i], breaks[i+1]]; the first class also holds the minimum.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.Classify = factory();
})(typeof self !== "undefined" ? self : this, function () {
  function clean(values) {
    return values
      .filter((v) => typeof v === "number" && Number.isFinite(v))
      .sort((a, b) => a - b);
  }

  function equal(sorted, k) {
    const min = sorted[0];
    const max = sorted[sorted.length - 1];
    const step = (max - min) / k;
    const breaks = [];
    for (let i = 0; i < k; i++) breaks.push(min + i * step);
    breaks.push(max);
    return breaks;
  }

  function quantile(sorted, k) {
    const n = sorted.length;
    const breaks = [];
    for (let i = 0; i <= k; i++) {
      const pos = ((n - 1) * i) / k;
      const lo = Math.floor(pos);
      const hi = Math.min(lo + 1, n - 1);
      breaks.push(sorted[lo] + (sorted[hi] - sorted[lo]) * (pos - lo));
    }
    breaks[k] = sorted[n - 1];
    return breaks;
  }

  // Fisher-Jenks: split the sorted values into k runs minimising within-run variance.
  function jenks(sorted, k) {
    const n = sorted.length;
    if (new Set(sorted).size <= k) return equal(sorted, k);

    const s1 = [0];
    const s2 = [0];
    for (let i = 0; i < n; i++) {
      s1.push(s1[i] + sorted[i]);
      s2.push(s2[i] + sorted[i] * sorted[i]);
    }
    // Sum of squared deviations of sorted[i..j) (half-open, 0-based).
    const ssd = (i, j) => {
      const m = j - i;
      const sum = s1[j] - s1[i];
      return s2[j] - s2[i] - (sum * sum) / m;
    };

    // cost[c][j]: best total SSD of the first j values split into c runs.
    const cost = [new Array(n + 1).fill(Infinity)];
    cost[0][0] = 0;
    const cut = [[]];
    for (let c = 1; c <= k; c++) {
      cost.push(new Array(n + 1).fill(Infinity));
      cut.push(new Array(n + 1).fill(0));
      for (let j = c; j <= n; j++) {
        for (let m = c - 1; m < j; m++) {
          const v = cost[c - 1][m] + ssd(m, j);
          if (v < cost[c][j]) {
            cost[c][j] = v;
            cut[c][j] = m;
          }
        }
      }
    }

    const breaks = new Array(k + 1);
    breaks[0] = sorted[0];
    breaks[k] = sorted[n - 1];
    let j = n;
    for (let c = k; c > 1; c--) {
      j = cut[c][j];
      breaks[c - 1] = sorted[j - 1]; // upper bound of the lower run
    }
    return breaks;
  }

  function classify(values, mode, k) {
    const sorted = clean(values);
    if (sorted.length === 0) return new Array(k + 1).fill(0);
    if (mode === "quantile") return quantile(sorted, k);
    if (mode === "jenks") return jenks(sorted, k);
    return equal(sorted, k);
  }

  function classIndex(value, breaks) {
    const k = breaks.length - 1;
    for (let i = 0; i < k; i++) if (value <= breaks[i + 1]) return i;
    return k - 1;
  }

  return { classify, classIndex };
});
