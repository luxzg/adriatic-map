package generateddata

import "embed"

// Assets contains the reviewed runtime overlay and its generation metadata.
//
//go:embed adriatic_6nm.geojson metadata.json NOTICE.md
var Assets embed.FS
