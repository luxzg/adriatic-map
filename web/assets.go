package web

import "embed"

// Assets contains the complete browser application and vendored Leaflet runtime.
//
//go:embed index.html app.js map-tools.js style.css vendor/leaflet/*
var Assets embed.FS
