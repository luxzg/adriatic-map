package generateddata

import "embed"

// Assets contains the reviewed runtime overlays and their generation metadata.
//
//go:embed *.geojson *.json NOTICE.md
var Assets embed.FS
