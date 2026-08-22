(() => {
  "use strict";

  const ADRIATIC_BOUNDS = L.latLngBounds([39.1, 11.4], [46.0, 20.7]);
  const DALMATIA_BOUNDS = L.latLngBounds([42.2, 14.0], [44.8, 18.9]);
  const DEFAULT_OPACITY = 0.45;
  const DEFAULT_COLOR = "#0e0af5";

  const distanceBadge = document.querySelector(".distance-badge");
  const distanceDetail = document.querySelector(".distance-detail");
  const distanceSelect = document.querySelector("#distance-select");
  const overlayColorPicker = document.querySelector("#overlay-color");
  const overlayColorHex = document.querySelector("#overlay-color-hex");
  const colorError = document.querySelector("#color-error");
  const overlayStatus = document.querySelector("#overlay-status");
  const overlayToggle = document.querySelector("#overlay-toggle");
  const opacitySlider = document.querySelector("#opacity-slider");
  const opacityValue = document.querySelector("#opacity-value");
  const inspectToggle = document.querySelector("#inspect-toggle");
  const inspectResult = document.querySelector("#inspect-result");
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

  let overlayCatalog = null;
  let selectedConfiguration = null;
  let activeOverlayLayer = null;
  let overlayColor = DEFAULT_COLOR;
  let overlayLoadSequence = 0;
  let inspectionEnabled = false;
  let inspectionSequence = 0;
  let inspectionMarker = null;
  const overlayPromises = new Map();

  function overlayStyle() {
    return {
      pane: "coastalZone",
      color: overlayColor,
      weight: 1.25,
      opacity: Math.min(1, Number(opacitySlider.value) / 100 + 0.2),
      fillColor: overlayColor,
      fillOpacity: Number(opacitySlider.value) / 100,
      interactive: false,
    };
  }

  function applyOverlayVisibility() {
    if (!activeOverlayLayer) {
      return;
    }
    if (overlayToggle.checked) {
      if (!map.hasLayer(activeOverlayLayer)) {
        activeOverlayLayer.addTo(map);
      }
    } else if (map.hasLayer(activeOverlayLayer)) {
      map.removeLayer(activeOverlayLayer);
    }
  }

  async function fetchJson(url) {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status} for ${url}`);
    }
    return response.json();
  }

  function loadOverlayBundle(configuration) {
    const key = configuration.nautical_miles;
    if (!overlayPromises.has(key)) {
      const promise = Promise.all([
        fetchJson(configuration.geojson),
        fetchJson(configuration.metadata),
      ]).then(([data, metadata]) => {
        if (data.type !== "FeatureCollection" || !Array.isArray(data.features)) {
          throw new Error("unexpected GeoJSON structure");
        }
        if (Number(metadata.buffer_nautical_miles) !== Number(key)) {
          throw new Error("overlay metadata distance does not match the catalog");
        }
        return { configuration, data, metadata };
      }).catch((error) => {
        overlayPromises.delete(key);
        throw error;
      });
      overlayPromises.set(key, promise);
    }
    return overlayPromises.get(key);
  }

  function updateDistanceDisplay(configuration) {
    distanceBadge.textContent = `${configuration.nautical_miles} NM`;
    distanceDetail.textContent = `${configuration.metres.toLocaleString("en")} m`;
  }

  function updateMetadataSummary(metadata) {
    dataSummary.textContent =
      `Generated from ${metadata.source_name} (${metadata.source_date}) using a ` +
      `${metadata.buffer_metres.toLocaleString("en")} m metric buffer. ` +
      "See the method and data notice links below.";
  }

  async function selectDistance(nauticalMiles) {
    if (!overlayCatalog) {
      return;
    }
    const configuration = overlayCatalog.overlays.find(
      (entry) => Number(entry.nautical_miles) === Number(nauticalMiles),
    );
    if (!configuration) {
      overlayStatus.textContent = "The selected distance is not available.";
      overlayStatus.className = "status-message error";
      return;
    }

    selectedConfiguration = configuration;
    updateDistanceDisplay(configuration);
    overlayStatus.textContent = `Loading ${configuration.nautical_miles} NM coastal zone…`;
    overlayStatus.className = "status-message";
    overlayToggle.disabled = true;
    const loadSequence = ++overlayLoadSequence;

    try {
      const bundle = await loadOverlayBundle(configuration);
      if (loadSequence !== overlayLoadSequence) {
        return;
      }
      if (activeOverlayLayer && map.hasLayer(activeOverlayLayer)) {
        map.removeLayer(activeOverlayLayer);
      }
      activeOverlayLayer = L.geoJSON(bundle.data, { style: overlayStyle });
      applyOverlayVisibility();
      updateMetadataSummary(bundle.metadata);
      overlayStatus.textContent = `${configuration.nautical_miles} NM coastal zone loaded.`;
      overlayStatus.className = "status-message ready";
    } catch (error) {
      if (loadSequence !== overlayLoadSequence) {
        return;
      }
      overlayStatus.textContent = `Could not load the coastal zone: ${error.message}`;
      overlayStatus.className = "status-message error";
    } finally {
      if (loadSequence === overlayLoadSequence) {
        overlayToggle.disabled = false;
      }
    }
  }

  function applyOverlayColor(value) {
    overlayColor = value;
    document.documentElement.style.setProperty("--overlay-color", value);
    document.documentElement.style.setProperty(
      "--overlay-contrast",
      AdriaticMapTools.contrastTextColor(value),
    );
    overlayColorPicker.value = value;
    overlayColorHex.value = value;
    overlayColorHex.setAttribute("aria-invalid", "false");
    colorError.hidden = true;
    if (activeOverlayLayer) {
      activeOverlayLayer.setStyle(overlayStyle());
    }
  }

  function setInspectionEnabled(enabled) {
    inspectionEnabled = enabled;
    inspectionSequence += 1;
    inspectToggle.setAttribute("aria-pressed", String(enabled));
    inspectToggle.textContent = enabled ? "Inspect point: on" : "Inspect point: off";
    map.getContainer().classList.toggle("inspect-active", enabled);
    if (inspectionMarker) {
      map.removeLayer(inspectionMarker);
      inspectionMarker = null;
    }
    inspectResult.textContent = enabled
      ? "Inspection enabled. Select a map point to classify its precomputed distance band."
      : "Inspection is off.";
  }

  function formatDistanceBand(classification) {
    if (classification.kind !== "band") {
      return `More than ${classification.beyondNauticalMiles} NM from mapped land, on land, or outside the covered region.`;
    }
    if (classification.lowerNauticalMiles === 0) {
      return `Within ${classification.upperNauticalMiles} NM of mapped land.`;
    }
    return `More than ${classification.lowerNauticalMiles} NM and within ${classification.upperNauticalMiles} NM of mapped land.`;
  }

  async function inspectPoint(event) {
    if (!inspectionEnabled || !overlayCatalog || !selectedConfiguration) {
      return;
    }
    const requestSequence = ++inspectionSequence;
    inspectResult.textContent = "Loading distance bands…";

    try {
      const bundles = await Promise.all(overlayCatalog.overlays.map(loadOverlayBundle));
      if (!inspectionEnabled || requestSequence !== inspectionSequence) {
        return;
      }
      const point = [event.latlng.lng, event.latlng.lat];
      const classification = AdriaticMapTools.classifyDistanceBand(
        point,
        bundles.map((bundle) => ({
          nauticalMiles: bundle.configuration.nautical_miles,
          data: bundle.data,
        })),
      );
      const selectedBundle = bundles.find(
        (bundle) => bundle.configuration.nautical_miles === selectedConfiguration.nautical_miles,
      );
      const insideSelected = AdriaticMapTools.pointInDocument(point, selectedBundle.data);

      if (inspectionMarker) {
        map.removeLayer(inspectionMarker);
      }
      inspectionMarker = L.circleMarker(event.latlng, {
        radius: 5,
        color: "#075985",
        weight: 2,
        fillColor: "#ffffff",
        fillOpacity: 1,
        interactive: false,
      }).addTo(map);
      inspectResult.textContent =
        `${event.latlng.lat.toFixed(5)}, ${event.latlng.lng.toFixed(5)} — ` +
        `${formatDistanceBand(classification)} ` +
        `${insideSelected ? "Inside" : "Outside"} the selected ${selectedConfiguration.nautical_miles} NM zone.`;
    } catch (error) {
      if (inspectionEnabled && requestSequence === inspectionSequence) {
        inspectResult.textContent = `Inspection failed: ${error.message}`;
      }
    }
  }

  async function initialize() {
    try {
      overlayCatalog = await fetchJson("/data/overlays.json");
      if (!Array.isArray(overlayCatalog.overlays) || overlayCatalog.overlays.length === 0) {
        throw new Error("overlay catalog is empty");
      }
      distanceSelect.replaceChildren();
      for (const configuration of overlayCatalog.overlays) {
        const option = document.createElement("option");
        option.value = String(configuration.nautical_miles);
        option.textContent = `${configuration.nautical_miles} NM`;
        distanceSelect.append(option);
      }
      distanceSelect.value = String(overlayCatalog.default_nautical_miles);
      await selectDistance(overlayCatalog.default_nautical_miles);
    } catch (error) {
      overlayStatus.textContent = `Could not load overlay catalog: ${error.message}`;
      overlayStatus.className = "status-message error";
      overlayToggle.disabled = true;
      distanceSelect.disabled = true;
      dataSummary.textContent = "Generation metadata is unavailable.";
    }
  }

  distanceSelect.addEventListener("change", () => {
    void selectDistance(Number(distanceSelect.value));
  });
  overlayToggle.addEventListener("change", applyOverlayVisibility);
  opacitySlider.addEventListener("input", () => {
    const percent = Number(opacitySlider.value);
    opacityValue.value = `${percent}%`;
    if (activeOverlayLayer) {
      activeOverlayLayer.setStyle(overlayStyle());
    }
  });
  overlayColorPicker.addEventListener("input", () => {
    applyOverlayColor(overlayColorPicker.value.toLowerCase());
  });
  overlayColorHex.addEventListener("input", () => {
    const normalized = AdriaticMapTools.normalizeHexColor(overlayColorHex.value);
    overlayColorHex.setAttribute("aria-invalid", String(!normalized));
    colorError.hidden = Boolean(normalized);
    if (normalized) {
      applyOverlayColor(normalized);
    }
  });
  inspectToggle.addEventListener("click", () => {
    setInspectionEnabled(!inspectionEnabled);
  });
  map.on("click", (event) => {
    void inspectPoint(event);
  });
  document.querySelector("#view-adriatic").addEventListener("click", () => {
    map.fitBounds(ADRIATIC_BOUNDS, { padding: [18, 18] });
  });
  document.querySelector("#view-dalmatia").addEventListener("click", () => {
    map.fitBounds(DALMATIA_BOUNDS, { padding: [18, 18] });
  });

  opacitySlider.value = String(DEFAULT_OPACITY * 100);
  opacityValue.value = `${Math.round(DEFAULT_OPACITY * 100)}%`;
  applyOverlayColor(DEFAULT_COLOR);
  setInspectionEnabled(false);
  void initialize();
})();
