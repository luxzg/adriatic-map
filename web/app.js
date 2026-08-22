(() => {
  "use strict";

  const ADRIATIC_BOUNDS = L.latLngBounds([39.1, 11.4], [46.0, 20.7]);
  const DALMATIA_BOUNDS = L.latLngBounds([42.2, 14.0], [44.8, 18.9]);
  const DEFAULT_OPACITY = 0.45;
  const overlayStatus = document.querySelector("#overlay-status");
  const overlayToggle = document.querySelector("#overlay-toggle");
  const opacitySlider = document.querySelector("#opacity-slider");
  const opacityValue = document.querySelector("#opacity-value");
  const dataSummary = document.querySelector("#data-summary");

  const map = L.map("map", {
    preferCanvas: true,
    zoomControl: true,
    minZoom: 5,
    maxBounds: L.latLngBounds([37, 8], [48, 23]).pad(0.2),
  });

  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>',
  }).addTo(map);

  L.control.scale({ imperial: false, position: "bottomright" }).addTo(map);
  map.fitBounds(DALMATIA_BOUNDS, { padding: [18, 18] });
  map.createPane("coastalZone");
  map.getPane("coastalZone").style.zIndex = 450;
  map.getPane("coastalZone").style.pointerEvents = "none";

  let overlayLayer = null;

  function overlayStyle() {
    return {
      pane: "coastalZone",
      color: "#c76808",
      weight: 1.25,
      opacity: Math.min(1, Number(opacitySlider.value) / 100 + 0.2),
      fillColor: "#f59e0b",
      fillOpacity: Number(opacitySlider.value) / 100,
      interactive: false,
    };
  }

  function applyOverlayVisibility() {
    if (!overlayLayer) {
      return;
    }
    if (overlayToggle.checked) {
      if (!map.hasLayer(overlayLayer)) {
        overlayLayer.addTo(map);
      }
    } else if (map.hasLayer(overlayLayer)) {
      map.removeLayer(overlayLayer);
    }
  }

  async function loadOverlay() {
    try {
      const response = await fetch("/data/adriatic_6nm.geojson");
      if (!response.ok) {
        throw new Error("HTTP " + response.status);
      }
      const data = await response.json();
      if (data.type !== "FeatureCollection" || !Array.isArray(data.features)) {
        throw new Error("unexpected GeoJSON structure");
      }
      overlayLayer = L.geoJSON(data, { style: overlayStyle });
      applyOverlayVisibility();
      if (data.features.length === 0) {
        overlayStatus.textContent = "Coastal zone data has not been generated yet.";
        overlayStatus.classList.add("warning");
      } else {
        overlayStatus.textContent = "6 NM coastal zone loaded.";
        overlayStatus.classList.add("ready");
      }
    } catch (error) {
      overlayStatus.textContent = "Could not load the coastal zone: " + error.message;
      overlayStatus.classList.add("error");
      overlayToggle.disabled = true;
    }
  }

  async function loadMetadata() {
    try {
      const response = await fetch("/data/metadata.json");
      if (!response.ok) {
        throw new Error("HTTP " + response.status);
      }
      const metadata = await response.json();
      if (metadata.generated) {
        dataSummary.textContent = "Generated from " + metadata.source_name + " (" + metadata.source_date + ") using a " + metadata.buffer_metres.toLocaleString("en") + " m metric buffer. See docs/DATA.md for the complete method and limitations.";
      } else {
        dataSummary.textContent = "The real GIS-derived overlay is pending generation.";
      }
    } catch (error) {
      dataSummary.textContent = "Generation metadata is unavailable: " + error.message;
    }
  }

  overlayToggle.addEventListener("change", applyOverlayVisibility);
  opacitySlider.addEventListener("input", () => {
    const percent = Number(opacitySlider.value);
    opacityValue.value = percent + "%";
    if (overlayLayer) {
      overlayLayer.setStyle(overlayStyle());
    }
  });
  document.querySelector("#view-adriatic").addEventListener("click", () => {
    map.fitBounds(ADRIATIC_BOUNDS, { padding: [18, 18] });
  });
  document.querySelector("#view-dalmatia").addEventListener("click", () => {
    map.fitBounds(DALMATIA_BOUNDS, { padding: [18, 18] });
  });

  opacitySlider.value = String(DEFAULT_OPACITY * 100);
  opacityValue.value = Math.round(DEFAULT_OPACITY * 100) + "%";
  void Promise.all([loadOverlay(), loadMetadata()]);
})();
