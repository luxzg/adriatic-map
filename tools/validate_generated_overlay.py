#!/usr/bin/env python3
"""Validate generated overlay classifications against the complete source land."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

from osgeo import gdal, ogr

from tools import build_coastal_buffer as coastal

CORRIDOR_SAMPLE = (16.27, 43.12)
MARINE_SAMPLES = (
    (15.0, 42.5),
    (13.5, 44.0),
    (18.5, 41.0),
)
LAND_SAMPLE = (16.44, 43.51)
SMALL_ISLET_LAND_SAMPLE = (15.299471111962, 43.795332114611)
SMALL_ISLET_WATER_SAMPLE = (15.31, 43.79533)
GRID_LONGITUDES = tuple(11.8 + index * 0.5 for index in range(18))
GRID_LATITUDES = tuple(39.3 + index * 0.5 for index in range(14))


def load_overlay(path: Path) -> ogr.Geometry:
    dataset = gdal.OpenEx(str(path), gdal.OF_VECTOR)
    if dataset is None:
        raise ValueError(f"cannot open overlay: {path}")
    layer = dataset.GetLayer(0)
    if layer is None or layer.GetFeatureCount() != 1:
        raise ValueError("overlay must contain exactly one feature")
    feature = layer.GetNextFeature()
    geometry = feature.GetGeometryRef()
    if geometry is None:
        raise ValueError("overlay feature has no geometry")
    result = geometry.Clone()
    result.AssignSpatialReference(coastal.spatial_reference_epsg(4326))
    coastal.validate_output(result)
    return result


def point(longitude: float, latitude: float) -> ogr.Geometry:
    geometry = ogr.Geometry(ogr.wkbPoint)
    geometry.AddPoint_2D(longitude, latitude)
    geometry.AssignSpatialReference(coastal.spatial_reference_epsg(4326))
    return geometry


def covered(geometry: ogr.Geometry, sample: ogr.Geometry) -> bool:
    return bool(geometry.Contains(sample) or geometry.Intersects(sample))


def expected_marine_coverage(
    distance_metres: float,
    buffer_metres: float,
    tolerance_metres: float,
) -> bool | None:
    if abs(distance_metres - buffer_metres) <= tolerance_metres:
        return None
    return distance_metres < buffer_metres


def validate_classifications(
    land_wgs84: ogr.Geometry,
    overlay_wgs84: ogr.Geometry,
    buffer_metres: float,
    simplify_metres: float,
) -> dict[str, object]:
    wgs84 = coastal.spatial_reference_epsg(4326)
    metric = coastal.metric_spatial_reference()
    land_metric = coastal.transformed(land_wgs84, wgs84, metric)
    tolerance_metres = (
        simplify_metres * 2
        + buffer_metres * coastal.relative_projection_error_percent() / 100
        + 25
    )

    corridor = point(*CORRIDOR_SAMPLE)
    corridor_metric = coastal.transformed(corridor, wgs84, metric)
    corridor_distance = land_metric.Distance(corridor_metric)
    corridor_covered = covered(overlay_wgs84, corridor)
    corridor_expected = expected_marine_coverage(
        corridor_distance,
        buffer_metres,
        tolerance_metres,
    )
    if corridor_expected is not None and corridor_covered != corridor_expected:
        raise ValueError("the Dalmatian corridor classification is incorrect")

    marine_samples = []
    for longitude, latitude in MARINE_SAMPLES:
        sample = point(longitude, latitude)
        sample_metric = coastal.transformed(sample, wgs84, metric)
        distance = land_metric.Distance(sample_metric)
        actual = covered(overlay_wgs84, sample)
        expected = expected_marine_coverage(
            distance,
            buffer_metres,
            tolerance_metres,
        )
        if expected is not None and actual != expected:
            raise ValueError(
                f"marine sample ({longitude}, {latitude}) classification is incorrect"
            )
        marine_samples.append(
            {
                "longitude": longitude,
                "latitude": latitude,
                "nearest_land_metres_projected": round(distance, 3),
                "covered": actual,
            }
        )

    land_sample = point(*LAND_SAMPLE)
    land_sample_metric = coastal.transformed(land_sample, wgs84, metric)
    if not covered(land_metric, land_sample_metric):
        raise ValueError("configured land sample is not on source land")
    if covered(overlay_wgs84, land_sample):
        raise ValueError("marine overlay covers the configured land sample")

    small_islet_land = point(*SMALL_ISLET_LAND_SAMPLE)
    small_islet_land_metric = coastal.transformed(small_islet_land, wgs84, metric)
    if not covered(land_metric, small_islet_land_metric):
        raise ValueError("configured small-islet sample is not on source land")
    if covered(overlay_wgs84, small_islet_land):
        raise ValueError("marine overlay covers the small-islet land sample")
    small_islet_water = point(*SMALL_ISLET_WATER_SAMPLE)
    small_islet_water_metric = coastal.transformed(small_islet_water, wgs84, metric)
    small_islet_distance = land_metric.Distance(small_islet_water_metric)
    if covered(land_metric, small_islet_water_metric):
        raise ValueError("configured small-islet water sample is on source land")
    if not covered(overlay_wgs84, small_islet_water):
        raise ValueError("small-islet coastal zone was not retained in the overlay")
    if small_islet_distance > buffer_metres + tolerance_metres:
        raise ValueError("small-islet water sample is farther than the buffer")

    checked = 0
    skipped_near_boundary = 0
    land_points = 0
    mismatches: list[dict[str, float | bool]] = []
    for longitude in GRID_LONGITUDES:
        for latitude in GRID_LATITUDES:
            sample = point(longitude, latitude)
            sample_metric = coastal.transformed(sample, wgs84, metric)
            actual = covered(overlay_wgs84, sample)
            if covered(land_metric, sample_metric):
                land_points += 1
                expected = False
                distance = 0.0
            else:
                distance = land_metric.Distance(sample_metric)
                if abs(distance - buffer_metres) <= tolerance_metres:
                    skipped_near_boundary += 1
                    continue
                expected = distance < buffer_metres
            checked += 1
            if actual != expected:
                mismatches.append(
                    {
                        "longitude": longitude,
                        "latitude": latitude,
                        "distance_metres": round(distance, 3),
                        "expected": expected,
                        "actual": actual,
                    }
                )

    if mismatches:
        raise ValueError(
            f"{len(mismatches)} source-vs-output grid classifications differ: "
            f"{mismatches[:5]}"
        )
    return {
        "corridor_sample": {
            "longitude": CORRIDOR_SAMPLE[0],
            "latitude": CORRIDOR_SAMPLE[1],
            "nearest_land_metres_projected": round(corridor_distance, 3),
            "covered": corridor_covered,
        },
        "marine_samples": marine_samples,
        "land_samples": 2,
        "small_islet_sample": {
            "land": {
                "longitude": SMALL_ISLET_LAND_SAMPLE[0],
                "latitude": SMALL_ISLET_LAND_SAMPLE[1],
                "covered_by_overlay": False,
            },
            "water": {
                "longitude": SMALL_ISLET_WATER_SAMPLE[0],
                "latitude": SMALL_ISLET_WATER_SAMPLE[1],
                "nearest_land_metres_projected": round(small_islet_distance, 3),
                "covered_by_overlay": True,
            },
        },
        "grid_points_checked": checked,
        "grid_land_points": land_points,
        "grid_points_skipped_near_boundary": skipped_near_boundary,
        "grid_mismatches": 0,
        "classification_tolerance_metres": round(tolerance_metres, 3),
    }


def parse_arguments(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--overlay", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument(
        "--update-metadata",
        action="store_true",
        help="write validation results and timestamp into metadata",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    arguments = parse_arguments(argv or sys.argv[1:])
    metadata = json.loads(arguments.metadata.read_text(encoding="utf-8"))
    if coastal.sha256_file(arguments.source) != metadata["source_sha256"]:
        raise ValueError("source checksum does not match generation metadata")
    buffer_nautical_miles = float(metadata["buffer_nautical_miles"])
    expected_buffer_metres = buffer_nautical_miles * coastal.NAUTICAL_MILE_METRES
    if float(metadata["buffer_metres"]) != expected_buffer_metres:
        raise ValueError("metadata nautical-mile and metre distances disagree")

    land, feature_count, polygon_count = coastal.load_land_geometry(arguments.source)
    if feature_count != metadata["source_features"]:
        raise ValueError("source feature count differs from generation metadata")
    if polygon_count != metadata["source_polygons"]:
        raise ValueError("source polygon count differs from generation metadata")
    overlay = load_overlay(arguments.overlay)
    validation = validate_classifications(
        land,
        overlay,
        buffer_metres=float(metadata["buffer_metres"]),
        simplify_metres=float(metadata["simplify_metres"]),
    )
    recorded_validation = metadata.get("validation")
    if (
        recorded_validation is not None
        and recorded_validation != validation
        and not arguments.update_metadata
    ):
        raise ValueError("recorded validation results differ from current results")
    if arguments.update_metadata:
        metadata["validation"] = validation
        metadata["validated_at"] = datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        )
        with arguments.metadata.open(
            "w", encoding="utf-8", newline="\n"
        ) as destination:
            json.dump(
                metadata,
                destination,
                indent=2,
                sort_keys=True,
                ensure_ascii=False,
            )
            destination.write("\n")
    print(
        f"validated {buffer_nautical_miles:g} NM across "
        f"{validation['grid_points_checked']} grid points with "
        f"{validation['grid_mismatches']} mismatches"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
