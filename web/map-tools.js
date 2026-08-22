(function (root, factory) {
  "use strict";

  const tools = factory();
  if (typeof module === "object" && module.exports) {
    module.exports = tools;
  }
  if (root) {
    root.AdriaticMapTools = tools;
  }
})(typeof globalThis === "object" ? globalThis : this, () => {
  "use strict";

  const SEGMENT_EPSILON = 1e-10;

  function pointOnSegment(point, start, end) {
    const [x, y] = point;
    const [startX, startY] = start;
    const [endX, endY] = end;
    const squaredLength = (endX - startX) ** 2 + (endY - startY) ** 2;
    if (squaredLength <= SEGMENT_EPSILON) {
      return (x - startX) ** 2 + (y - startY) ** 2 <= SEGMENT_EPSILON;
    }
    const cross = (x - startX) * (endY - startY) - (y - startY) * (endX - startX);
    if (Math.abs(cross) > SEGMENT_EPSILON) {
      return false;
    }
    const dot = (x - startX) * (endX - startX) + (y - startY) * (endY - startY);
    if (dot < -SEGMENT_EPSILON) {
      return false;
    }
    return dot <= squaredLength + SEGMENT_EPSILON;
  }

  function pointInRing(point, ring) {
    let inside = false;
    for (let index = 0, previous = ring.length - 1; index < ring.length; previous = index++) {
      const currentPoint = ring[index];
      const previousPoint = ring[previous];
      if (pointOnSegment(point, previousPoint, currentPoint)) {
        return true;
      }
      const crossesLatitude = (currentPoint[1] > point[1]) !== (previousPoint[1] > point[1]);
      if (!crossesLatitude) {
        continue;
      }
      const intersectionLongitude =
        ((previousPoint[0] - currentPoint[0]) * (point[1] - currentPoint[1])) /
          (previousPoint[1] - currentPoint[1]) +
        currentPoint[0];
      if (point[0] < intersectionLongitude) {
        inside = !inside;
      }
    }
    return inside;
  }

  function pointInPolygon(point, rings) {
    if (rings.length === 0 || !pointInRing(point, rings[0])) {
      return false;
    }
    return !rings.slice(1).some((ring) => pointInRing(point, ring));
  }

  function pointInGeometry(point, geometry) {
    if (!geometry) {
      return false;
    }
    if (geometry.type === "Polygon") {
      return pointInPolygon(point, geometry.coordinates);
    }
    if (geometry.type === "MultiPolygon") {
      return geometry.coordinates.some((polygon) => pointInPolygon(point, polygon));
    }
    return false;
  }

  function pointInDocument(point, document) {
    if (!document) {
      return false;
    }
    if (document.type === "FeatureCollection") {
      return document.features.some((feature) => pointInGeometry(point, feature.geometry));
    }
    if (document.type === "Feature") {
      return pointInGeometry(point, document.geometry);
    }
    return pointInGeometry(point, document);
  }

  function classifyDistanceBand(point, overlays) {
    const ordered = [...overlays].sort((left, right) => left.nauticalMiles - right.nauticalMiles);
    let previousDistance = 0;
    for (const overlay of ordered) {
      if (pointInDocument(point, overlay.data)) {
        return {
          kind: "band",
          lowerNauticalMiles: previousDistance,
          upperNauticalMiles: overlay.nauticalMiles,
        };
      }
      previousDistance = overlay.nauticalMiles;
    }
    return {
      kind: "unclassified",
      beyondNauticalMiles: previousDistance,
    };
  }

  function normalizeHexColor(value) {
    const match = /^#?([0-9a-f]{6})$/i.exec(value.trim());
    return match ? `#${match[1].toLowerCase()}` : null;
  }

  function contrastTextColor(value) {
    const normalized = normalizeHexColor(value);
    if (!normalized) {
      return "#ffffff";
    }
    const red = Number.parseInt(normalized.slice(1, 3), 16);
    const green = Number.parseInt(normalized.slice(3, 5), 16);
    const blue = Number.parseInt(normalized.slice(5, 7), 16);
    const brightness = (red * 299 + green * 587 + blue * 114) / 1000;
    return brightness >= 150 ? "#172033" : "#ffffff";
  }

  return {
    classifyDistanceBand,
    contrastTextColor,
    normalizeHexColor,
    pointInDocument,
  };
});
