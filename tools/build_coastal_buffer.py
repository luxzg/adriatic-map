#!/usr/bin/env python3
"""Generate a marine coastal-distance overlay from OSM-derived land polygons."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import sys
import zipfile

from osgeo import gdal, ogr, osr

gdal.UseExceptions()
ogr.UseExceptions()
osr.UseExceptions()

NAUTICAL_MILE_METRES = 1852.0
DEFAULT_BUFFER_NM = 6.0
DEFAULT_BUFFER_METRES = DEFAULT_BUFFER_NM * NAUTICAL_MILE_METRES
DEFAULT_SIMPLIFY_METRES = 50.0
BUFFER_QUADRANT_SEGMENTS = 24
OUTPUT_BOUNDS = (11.4, 39.0, 20.7, 46.1)
SOURCE_MARGIN_DEGREES = 1.0
SOURCE_URL = (
    "https://osmdata.openstreetmap.de/download/"
    "land-polygons-split-4326.zip"
)
SOURCE_NAME = "OpenStreetMap coastline land polygons"
METRIC_CRS_PROJ4 = (
    "+proj=aeqd +lat_0=43 +lon_0=16 +datum=WGS84 "
    "+units=m +no_defs +type=crs"
)


@dataclass(frozen=True)
class BuildStatistics:
    source_features: int
    source_polygons: int
    output_area_square_kilometres: float
    output_bounds: tuple[float, float, float, float]
    projection_max_relative_error_percent: float


def spatial_reference_epsg(code: int) -> osr.SpatialReference:
    reference = osr.SpatialReference()
    reference.ImportFromEPSG(code)
    reference.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    return reference


def metric_spatial_reference() -> osr.SpatialReference:
    reference = osr.SpatialReference()
    reference.ImportFromProj4(METRIC_CRS_PROJ4)
    reference.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    return reference


def rectangle_geometry(
    bounds: tuple[float, float, float, float],
    reference: osr.SpatialReference,
) -> ogr.Geometry:
    west, south, east, north = bounds
    ring = ogr.Geometry(ogr.wkbLinearRing)
    for longitude, latitude in (
        (west, south),
        (east, south),
        (east, north),
        (west, north),
        (west, south),
    ):
        ring.AddPoint_2D(longitude, latitude)
    polygon = ogr.Geometry(ogr.wkbPolygon)
    polygon.AddGeometry(ring)
    polygon.AssignSpatialReference(reference)
    return polygon


def transformed(
    geometry: ogr.Geometry,
    source: osr.SpatialReference,
    target: osr.SpatialReference,
) -> ogr.Geometry:
    result = geometry.Clone()
    result.AssignSpatialReference(source)
    transformation = osr.CoordinateTransformation(source, target)
    result.Transform(transformation)
    result.AssignSpatialReference(target)
    return result


def polygon_parts(geometry: ogr.Geometry):
    geometry_type = ogr.GT_Flatten(geometry.GetGeometryType())
    if geometry_type == ogr.wkbPolygon:
        yield geometry
        return
    if geometry_type in (ogr.wkbMultiPolygon, ogr.wkbGeometryCollection):
        for index in range(geometry.GetGeometryCount()):
            yield from polygon_parts(geometry.GetGeometryRef(index))


def without_inner_rings(geometry: ogr.Geometry) -> ogr.Geometry:
    """Return polygonal geometry with every interior ring filled."""
    polygons = ogr.Geometry(ogr.wkbMultiPolygon)
    for polygon in polygon_parts(geometry):
        if polygon.GetGeometryCount() == 0:
            continue
        exterior_only = ogr.Geometry(ogr.wkbPolygon)
        exterior_only.AddGeometry(polygon.GetGeometryRef(0).Clone())
        polygons.AddGeometry(exterior_only)
    if polygons.GetGeometryCount() == 0:
        raise ValueError("geometry contains no polygons")
    result = polygons.UnionCascaded()
    if result is None or result.IsEmpty():
        raise ValueError("could not dissolve exterior polygons")
    return valid_geometry(result)


def valid_geometry(geometry: ogr.Geometry) -> ogr.Geometry:
    if geometry is None or geometry.IsEmpty():
        raise ValueError("geometry is empty")
    if geometry.IsValid():
        return geometry
    repaired = geometry.MakeValid()
    if repaired is None or repaired.IsEmpty() or not repaired.IsValid():
        raise ValueError("geometry could not be repaired")
    return repaired


def resolve_vector_source(source_path: Path) -> str:
    absolute = source_path.resolve()
    if absolute.suffix.lower() != ".zip":
        return str(absolute)
    with zipfile.ZipFile(absolute) as archive:
        candidates = [
            name
            for name in archive.namelist()
            if name.lower().endswith(".shp")
            and "land_polygon" in name.lower()
        ]
    if len(candidates) != 1:
        raise ValueError(
            "expected exactly one land-polygon shapefile in archive; "
            f"found {len(candidates)}"
        )
    return f"/vsizip/{absolute}/{candidates[0]}"


def load_land_geometry(
    source_path: Path,
    output_bounds: tuple[float, float, float, float] = OUTPUT_BOUNDS,
    source_margin_degrees: float = SOURCE_MARGIN_DEGREES,
) -> tuple[ogr.Geometry, int, int]:
    source_reference = spatial_reference_epsg(4326)
    source_bounds = (
        output_bounds[0] - source_margin_degrees,
        output_bounds[1] - source_margin_degrees,
        output_bounds[2] + source_margin_degrees,
        output_bounds[3] + source_margin_degrees,
    )
    source_clip = rectangle_geometry(source_bounds, source_reference)
    dataset = gdal.OpenEx(resolve_vector_source(source_path), gdal.OF_VECTOR)
    if dataset is None:
        raise ValueError(f"cannot open vector source: {source_path}")
    layer = dataset.GetLayer(0)
    if layer is None:
        raise ValueError("vector source has no layers")
    layer_reference = layer.GetSpatialRef()
    if layer_reference is None:
        raise ValueError("source layer has no spatial reference")
    layer_reference.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    if not layer_reference.IsSame(source_reference):
        raise ValueError("source layer must use WGS84 / EPSG:4326")

    layer.SetSpatialFilterRect(*source_bounds)
    collected = ogr.Geometry(ogr.wkbMultiPolygon)
    feature_count = 0
    polygon_count = 0
    for feature in layer:
        source_geometry = feature.GetGeometryRef()
        if source_geometry is None or source_geometry.IsEmpty():
            continue
        clipped = source_geometry.Intersection(source_clip)
        if clipped is None or clipped.IsEmpty():
            continue
        for polygon in polygon_parts(clipped):
            collected.AddGeometry(polygon)
            polygon_count += 1
        feature_count += 1

    if polygon_count == 0:
        raise ValueError("no land polygons intersect the configured source extent")
    land = without_inner_rings(collected)
    land.AssignSpatialReference(source_reference)
    return land, feature_count, polygon_count


def build_coastal_zone(
    land_wgs84: ogr.Geometry,
    buffer_metres: float = DEFAULT_BUFFER_METRES,
    simplify_metres: float = DEFAULT_SIMPLIFY_METRES,
    output_bounds: tuple[float, float, float, float] = OUTPUT_BOUNDS,
) -> tuple[ogr.Geometry, float]:
    if buffer_metres <= 0:
        raise ValueError("buffer distance must be positive")
    if simplify_metres < 0:
        raise ValueError("simplification tolerance cannot be negative")

    wgs84 = spatial_reference_epsg(4326)
    metric = metric_spatial_reference()
    land_filled = without_inner_rings(land_wgs84)
    land_metric = valid_geometry(transformed(land_filled, wgs84, metric))
    buffered = valid_geometry(
        land_metric.Buffer(buffer_metres, BUFFER_QUADRANT_SEGMENTS)
    )
    marine_zone = valid_geometry(buffered.Difference(land_metric))
    output_clip = transformed(
        rectangle_geometry(output_bounds, wgs84),
        wgs84,
        metric,
    )
    marine_zone = valid_geometry(marine_zone.Intersection(output_clip))
    if simplify_metres > 0:
        marine_zone = valid_geometry(
            marine_zone.SimplifyPreserveTopology(simplify_metres)
        )
    area_square_kilometres = marine_zone.Area() / 1_000_000.0
    result = valid_geometry(transformed(marine_zone, metric, wgs84))
    return result, area_square_kilometres


def relative_projection_error_percent() -> float:
    wgs84 = spatial_reference_epsg(4326)
    metric = metric_spatial_reference()
    segments = []
    for longitude, latitude in (
        (11.6, 39.2),
        (20.4, 39.2),
        (11.6, 45.8),
        (20.4, 45.8),
        (16.0, 43.0),
    ):
        segments.append(((longitude, latitude), (longitude + 0.1, latitude)))
        segments.append(((longitude, latitude), (longitude, latitude + 0.1)))

    maximum = 0.0
    for start, end in segments:
        line = ogr.Geometry(ogr.wkbLineString)
        line.AddPoint_2D(*start)
        line.AddPoint_2D(*end)
        line.AssignSpatialReference(wgs84)
        geodesic = line.GeodesicLength()
        projected = transformed(line, wgs84, metric).Length()
        if not math.isfinite(geodesic) or geodesic <= 0:
            raise ValueError("could not calculate geodesic reference length")
        maximum = max(maximum, abs(projected - geodesic) / geodesic * 100.0)
    return maximum


def geometry_bounds(
    geometry: ogr.Geometry,
) -> tuple[float, float, float, float]:
    minimum_x, maximum_x, minimum_y, maximum_y = geometry.GetEnvelope()
    return minimum_x, minimum_y, maximum_x, maximum_y


def validate_output(
    geometry: ogr.Geometry,
    output_bounds: tuple[float, float, float, float] = OUTPUT_BOUNDS,
) -> None:
    if geometry is None or geometry.IsEmpty():
        raise ValueError("output geometry is empty")
    if not geometry.IsValid():
        raise ValueError("output geometry is invalid")
    west, south, east, north = geometry_bounds(geometry)
    tolerance = 0.0001
    expected_west, expected_south, expected_east, expected_north = output_bounds
    if (
        west < expected_west - tolerance
        or south < expected_south - tolerance
        or east > expected_east + tolerance
        or north > expected_north + tolerance
    ):
        raise ValueError("output geometry exceeds the configured Adriatic bounds")
    projection_error = relative_projection_error_percent()
    if projection_error > 0.5:
        raise ValueError(
            "metric projection distortion exceeds 0.5%: "
            f"{projection_error:.4f}%"
        )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_geojson(
    path: Path,
    geometry: ogr.Geometry,
    buffer_nautical_miles: float,
    buffer_metres: float,
) -> None:
    geometry_json = json.loads(
        geometry.ExportToJson(["COORDINATE_PRECISION=6"])
    )
    document = {
        "type": "FeatureCollection",
        "name": "adriatic_6nm",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "distance_nm": buffer_nautical_miles,
                    "distance_m": buffer_metres,
                    "source": SOURCE_NAME,
                    "attribution": "© OpenStreetMap contributors",
                    "license": "ODbL-1.0",
                },
                "geometry": geometry_json,
            }
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as destination:
        json.dump(document, destination, separators=(",", ":"), ensure_ascii=False)
        destination.write("\n")


def write_metadata(
    path: Path,
    source_path: Path,
    source_url: str,
    source_date: str,
    buffer_nautical_miles: float,
    buffer_metres: float,
    simplify_metres: float,
    statistics: BuildStatistics,
) -> None:
    source_retrieved_at = datetime.fromtimestamp(
        source_path.stat().st_mtime,
        timezone.utc,
    ).isoformat(timespec="seconds")
    metadata = {
        "generated": True,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_name": SOURCE_NAME,
        "source_url": source_url,
        "source_date": source_date,
        "source_retrieved_at": source_retrieved_at,
        "source_archive_bytes": source_path.stat().st_size,
        "source_sha256": sha256_file(source_path),
        "source_license": "ODbL-1.0",
        "attribution": "© OpenStreetMap contributors",
        "buffer_nautical_miles": buffer_nautical_miles,
        "buffer_metres": buffer_metres,
        "metric_crs_proj4": METRIC_CRS_PROJ4,
        "buffer_quadrant_segments": BUFFER_QUADRANT_SEGMENTS,
        "simplify_metres": simplify_metres,
        "coordinate_precision_degrees": 0.000001,
        "source_margin_degrees": SOURCE_MARGIN_DEGREES,
        "source_features": statistics.source_features,
        "source_polygons": statistics.source_polygons,
        "output_area_square_kilometres": round(
            statistics.output_area_square_kilometres, 3
        ),
        "output_bounds": [round(value, 6) for value in statistics.output_bounds],
        "projection_max_relative_error_percent": round(
            statistics.projection_max_relative_error_percent, 6
        ),
        "tool_versions": {
            "python": sys.version.split()[0],
            "gdal": gdal.VersionInfo("--version"),
            "proj": (
                f"{osr.GetPROJVersionMajor()}."
                f"{osr.GetPROJVersionMinor()}."
                f"{osr.GetPROJVersionMicro()}"
            ),
        },
        "navigation_use": False,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as destination:
        json.dump(metadata, destination, indent=2, sort_keys=True, ensure_ascii=False)
        destination.write("\n")


def parse_arguments(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--source-url", default=SOURCE_URL)
    parser.add_argument(
        "--source-date",
        required=True,
        help="source snapshot date or Last-Modified timestamp",
    )
    parser.add_argument("--buffer-nm", type=float, default=DEFAULT_BUFFER_NM)
    parser.add_argument(
        "--simplify-metres",
        type=float,
        default=DEFAULT_SIMPLIFY_METRES,
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    arguments = parse_arguments(argv or sys.argv[1:])
    if not arguments.source.is_file():
        raise ValueError(f"source file does not exist: {arguments.source}")
    buffer_metres = arguments.buffer_nm * NAUTICAL_MILE_METRES
    land, feature_count, polygon_count = load_land_geometry(arguments.source)
    zone, area_square_kilometres = build_coastal_zone(
        land,
        buffer_metres=buffer_metres,
        simplify_metres=arguments.simplify_metres,
    )
    validate_output(zone)
    statistics = BuildStatistics(
        source_features=feature_count,
        source_polygons=polygon_count,
        output_area_square_kilometres=area_square_kilometres,
        output_bounds=geometry_bounds(zone),
        projection_max_relative_error_percent=relative_projection_error_percent(),
    )
    write_geojson(
        arguments.output,
        zone,
        buffer_nautical_miles=arguments.buffer_nm,
        buffer_metres=buffer_metres,
    )
    write_metadata(
        arguments.metadata,
        arguments.source,
        arguments.source_url,
        arguments.source_date,
        arguments.buffer_nm,
        buffer_metres,
        arguments.simplify_metres,
        statistics,
    )
    print(
        f"wrote {arguments.output} "
        f"({area_square_kilometres:,.1f} km², "
        f"{feature_count} source features)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
