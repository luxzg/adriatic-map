$ErrorActionPreference = "Stop"

if (-not $env:GOCACHE) {
    $env:GOCACHE = Join-Path (Get-Location) ".gocache"
}
if (-not $env:GOMODCACHE) {
    $env:GOMODCACHE = Join-Path (Get-Location) ".gomodcache"
}

New-Item -ItemType Directory -Force -Path "dist" | Out-Null
go build -trimpath -o "dist/adriatic-map-windows-amd64.exe" ./cmd/adriatic-map
if ($LASTEXITCODE -ne 0) {
    throw "Go build failed with exit code $LASTEXITCODE"
}
Get-FileHash -Algorithm SHA256 "dist/adriatic-map-windows-amd64.exe"
