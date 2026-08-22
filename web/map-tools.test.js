"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const tools = require("./map-tools.js");

const polygonWithHole = {
  type: "Polygon",
  coordinates: [
    [[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]],
    [[4, 4], [6, 4], [6, 6], [4, 6], [4, 4]],
  ],
};

assert.equal(tools.pointInDocument([2, 2], polygonWithHole), true);
assert.equal(tools.pointInDocument([5, 5], polygonWithHole), false);
assert.equal(tools.pointInDocument([12, 2], polygonWithHole), false);
assert.equal(tools.pointInDocument([0, 2], polygonWithHole), true);

const oneNm = { type: "Polygon", coordinates: [[[0, 0], [2, 0], [2, 2], [0, 2], [0, 0]]] };
const threeNm = { type: "Polygon", coordinates: [[[0, 0], [4, 0], [4, 4], [0, 4], [0, 0]]] };
const band = tools.classifyDistanceBand([3, 3], [
  { nauticalMiles: 3, data: threeNm },
  { nauticalMiles: 1, data: oneNm },
]);
assert.deepEqual(band, {
  kind: "band",
  lowerNauticalMiles: 1,
  upperNauticalMiles: 3,
});
assert.deepEqual(tools.classifyDistanceBand([8, 8], [
  { nauticalMiles: 1, data: oneNm },
  { nauticalMiles: 3, data: threeNm },
]), {
  kind: "unclassified",
  beyondNauticalMiles: 3,
});

assert.equal(tools.normalizeHexColor("#F59E0B"), "#f59e0b");
assert.equal(tools.normalizeHexColor("075985"), "#075985");
assert.equal(tools.normalizeHexColor("orange"), null);
assert.equal(tools.contrastTextColor("#0e0af5"), "#ffffff");
assert.equal(tools.contrastTextColor("#f59e0b"), "#172033");

const generatedOverlays = [1, 3, 6, 12, 20].map((nauticalMiles) => ({
  nauticalMiles,
  data: JSON.parse(fs.readFileSync(
    path.join(__dirname, "..", "data", "generated", `adriatic_${nauticalMiles}nm.geojson`),
    "utf8",
  )),
}));
assert.deepEqual(tools.classifyDistanceBand([16.27, 43.12], generatedOverlays), {
  kind: "band",
  lowerNauticalMiles: 1,
  upperNauticalMiles: 3,
});
assert.deepEqual(tools.classifyDistanceBand([15.31, 43.79533], generatedOverlays), {
  kind: "band",
  lowerNauticalMiles: 0,
  upperNauticalMiles: 1,
});
assert.equal(
  tools.classifyDistanceBand([16.44, 43.51], generatedOverlays).kind,
  "unclassified",
);

console.log("map tools tests passed");
