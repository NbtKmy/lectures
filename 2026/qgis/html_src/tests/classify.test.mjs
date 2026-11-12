import test from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";

const { classify, classIndex } = createRequire(import.meta.url)("../classify.js");

const nonDecreasing = (a) => a.every((v, i) => i === 0 || v >= a[i - 1]);

test("equal interval splits the range evenly", () => {
  assert.deepEqual(classify([0, 10], "equal", 2), [0, 5, 10]);
});

test("quantile puts the median at the middle break", () => {
  const b = classify([1, 2, 3, 4], "quantile", 2);
  assert.equal(b.length, 3);
  assert.equal(b[0], 1);
  assert.equal(b[1], 2.5);
  assert.equal(b[2], 4);
});

test("jenks separates two obvious clusters", () => {
  const b = classify([1, 2, 3, 10, 11, 12], "jenks", 2);
  assert.equal(b.length, 3);
  assert.equal(b[0], 1);
  assert.equal(b[2], 12);
  assert.ok(b[1] >= 3 && b[1] < 10, `middle break ${b[1]}`);
});

test("null and NaN are ignored", () => {
  assert.deepEqual(classify([0, null, NaN, 10, undefined], "equal", 2), [0, 5, 10]);
});

test("classIndex maps min to 0 and max to k-1", () => {
  const b = classify([0, 10], "equal", 2);
  assert.equal(classIndex(0, b), 0);
  assert.equal(classIndex(4.9, b), 0);
  assert.equal(classIndex(5, b), 0);
  assert.equal(classIndex(5.1, b), 1);
  assert.equal(classIndex(10, b), 1);
});

test("classIndex clamps out-of-range values", () => {
  const b = [0, 5, 10];
  assert.equal(classIndex(-3, b), 0);
  assert.equal(classIndex(99, b), 1);
});

for (const mode of ["equal", "quantile", "jenks"]) {
  test(`${mode}: all-identical values stay well-formed`, () => {
    const b = classify([5, 5, 5, 5], mode, 3);
    assert.equal(b.length, 4);
    assert.ok(nonDecreasing(b), JSON.stringify(b));
    assert.doesNotThrow(() => classIndex(5, b));
    const i = classIndex(5, b);
    assert.ok(i >= 0 && i <= 2);
  });

  test(`${mode}: fewer distinct values than classes stay well-formed`, () => {
    const b = classify([1, 2], mode, 5);
    assert.equal(b.length, 6);
    assert.ok(nonDecreasing(b), JSON.stringify(b));
    assert.equal(b[0], 1);
    assert.equal(b[5], 2);
    for (const v of [1, 2]) {
      const i = classIndex(v, b);
      assert.ok(i >= 0 && i <= 4);
    }
  });

  test(`${mode}: empty input does not throw`, () => {
    const b = classify([null, NaN], mode, 3);
    assert.equal(b.length, 4);
    assert.doesNotThrow(() => classIndex(1, b));
  });
}
