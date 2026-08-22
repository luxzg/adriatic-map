package server

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestHealthEndpoint(t *testing.T) {
	request := httptest.NewRequest(http.MethodGet, "/healthz", nil)
	response := httptest.NewRecorder()
	New(Config{Version: "test-version"}).ServeHTTP(response, request)

	if response.Code != http.StatusOK {
		t.Fatalf("status = %d, want %d", response.Code, http.StatusOK)
	}
	var body healthResponse
	if err := json.NewDecoder(response.Body).Decode(&body); err != nil {
		t.Fatalf("decode response: %v", err)
	}
	if body.Status != "ok" || body.Version != "test-version" {
		t.Fatalf("unexpected health response: %+v", body)
	}
}

func TestEmbeddedApplicationFiles(t *testing.T) {
	tests := []struct {
		path        string
		contentType string
		contains    string
	}{
		{path: "/", contentType: "text/html", contains: "Adriatic Map"},
		{path: "/app.js", contentType: "text/javascript", contains: "tile.openstreetmap.org"},
		{path: "/style.css", contentType: "text/css", contains: "--overlay-color"},
		{path: "/vendor/leaflet/leaflet.js", contentType: "text/javascript", contains: "Leaflet"},
		{path: "/data/adriatic_6nm.geojson", contentType: "application/geo+json", contains: "FeatureCollection"},
		{path: "/data/metadata.json", contentType: "application/json", contains: "11112"},
		{path: "/data/NOTICE.md", contentType: "text/markdown", contains: "ODbL 1.0"},
	}

	handler := New(Config{Version: "test-version"})
	for _, test := range tests {
		t.Run(test.path, func(t *testing.T) {
			request := httptest.NewRequest(http.MethodGet, test.path, nil)
			response := httptest.NewRecorder()
			handler.ServeHTTP(response, request)
			if response.Code != http.StatusOK {
				t.Fatalf("status = %d, want %d", response.Code, http.StatusOK)
			}
			if !strings.Contains(response.Header().Get("Content-Type"), test.contentType) {
				t.Fatalf("Content-Type = %q, want substring %q", response.Header().Get("Content-Type"), test.contentType)
			}
			if !strings.Contains(response.Body.String(), test.contains) {
				t.Fatalf("response does not contain %q", test.contains)
			}
		})
	}
}

func TestSecurityAndCacheHeaders(t *testing.T) {
	handler := New(Config{Version: "test-version"})
	tests := []struct {
		path         string
		cacheControl string
	}{
		{path: "/", cacheControl: "no-cache"},
		{path: "/data/metadata.json", cacheControl: "public, max-age=3600"},
		{path: "/vendor/leaflet/leaflet.js", cacheControl: "public, max-age=31536000, immutable"},
	}
	for _, test := range tests {
		request := httptest.NewRequest(http.MethodGet, test.path, nil)
		response := httptest.NewRecorder()
		handler.ServeHTTP(response, request)
		if got := response.Header().Get("Cache-Control"); got != test.cacheControl {
			t.Errorf("%s Cache-Control = %q, want %q", test.path, got, test.cacheControl)
		}
		if response.Header().Get("Content-Security-Policy") == "" {
			t.Errorf("%s is missing Content-Security-Policy", test.path)
		}
	}
}
