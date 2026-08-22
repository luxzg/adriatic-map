// Adriatic Map is licensed under GPL-3.0-or-later. See LICENSE.
package server

import (
	"encoding/json"
	"io/fs"
	"net/http"
	"strings"

	generateddata "github.com/luxzg/adriatic-map/data/generated"
	webassets "github.com/luxzg/adriatic-map/web"
)

type Config struct {
	Version string
}

type healthResponse struct {
	Name    string `json:"name"`
	Status  string `json:"status"`
	Version string `json:"version"`
}

func New(config Config) http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("GET /healthz", func(writer http.ResponseWriter, _ *http.Request) {
		writer.Header().Set("Content-Type", "application/json; charset=utf-8")
		_ = json.NewEncoder(writer).Encode(healthResponse{
			Name:    "adriatic-map",
			Status:  "ok",
			Version: config.Version,
		})
	})

	dataFiles, err := fs.Sub(generateddata.Assets, ".")
	if err != nil {
		panic(err)
	}
	mux.Handle("GET /data/", http.StripPrefix("/data/", http.FileServer(http.FS(dataFiles))))

	webFiles, err := fs.Sub(webassets.Assets, ".")
	if err != nil {
		panic(err)
	}
	mux.Handle("GET /", http.FileServer(http.FS(webFiles)))

	return securityHeaders(cacheHeaders(mux))
}

func cacheHeaders(next http.Handler) http.Handler {
	return http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		switch {
		case strings.HasPrefix(request.URL.Path, "/vendor/"):
			writer.Header().Set("Cache-Control", "public, max-age=31536000, immutable")
		case strings.HasPrefix(request.URL.Path, "/data/"):
			writer.Header().Set("Cache-Control", "public, max-age=3600")
		default:
			writer.Header().Set("Cache-Control", "no-cache")
		}
		next.ServeHTTP(writer, request)
	})
}

func securityHeaders(next http.Handler) http.Handler {
	return http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		writer.Header().Set("Content-Security-Policy", "default-src 'self'; img-src 'self' data: https://tile.openstreetmap.org; style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
		writer.Header().Set("Referrer-Policy", "strict-origin-when-cross-origin")
		writer.Header().Set("X-Content-Type-Options", "nosniff")
		writer.Header().Set("X-Frame-Options", "DENY")
		writer.Header().Set("Permissions-Policy", "geolocation=(), camera=(), microphone=()")
		next.ServeHTTP(writer, request)
	})
}
