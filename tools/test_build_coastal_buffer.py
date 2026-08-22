from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import unittest

from osgeo import gdal, ogr

from tools import build_coastal_buffer as coastal
from tools import validate_generated_overlay as overlay_validation


def polygon_with_hole() -> ogr.Geometry:
    geometry = ogr.CreateGeometryFromWkt(
        "POLYGON (("
        "15 43, 16 43, 16 44, 15 44, 15 43"
        "),("
        "15.4 43.4, 15.4 43.6, 15.6 43.6, 15.6 43.4, 15.4 43.4"
        "))"
    )
    geometry.AssignSpatialReference(coastal.spatial_reference_epsg(4326))
    return geometry


class CoastalBufferTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        gdal.UseExceptions()

    def test_supported_nautical_miles_convert_to_exact_metres(self) -> None:
        expected = {1: 1852, 3: 5556, 6: 11112, 12: 22224, 20: 37040}
        for nautical_miles, metres in expected.items():
            with self.subTest(nautical_miles=nautical_miles):
                self.assertEqual(
                    nautical_miles * coastal.NAUTICAL_MILE_METRES,
                    metres,
                )
        self.assertEqual(coastal.DEFAULT_BUFFER_METRES, expected[6])

    def test_inner_rings_are_filled_before_buffering(self) -> None:
        filled = coastal.without_inner_rings(polygon_with_hole())
        former_hole = ogr.CreateGeometryFromWkt("POINT (15.5 43.5)")
        self.assertTrue(filled.Contains(former_hole))

    def test_metric_buffer_is_marine_only_and_clipped(self) -> None:
        land = ogr.CreateGeometryFromWkt(
            "POLYGON ((15 43, 15.1 43, 15.1 43.1, 15 43.1, 15 43))"
        )
        land.AssignSpatialReference(coastal.spatial_reference_epsg(4326))
        zone, area = coastal.build_coastal_zone(
            land,
            buffer_metres=11112.0,
            simplify_metres=0,
            output_bounds=(14.5, 42.5, 15.5, 43.5),
        )
        self.assertGreater(area, 100)
        self.assertFalse(zone.Contains(ogr.CreateGeometryFromWkt("POINT (15.05 43.05)")))
        self.assertTrue(zone.Contains(ogr.CreateGeometryFromWkt("POINT (14.98 43.05)")))
        self.assertFalse(zone.Contains(ogr.CreateGeometryFromWkt("POINT (14.7 43.05)")))
        west, south, east, north = coastal.geometry_bounds(zone)
        self.assertGreaterEqual(west, 14.5)
        self.assertGreaterEqual(south, 42.5)
        self.assertLessEqual(east, 15.5)
        self.assertLessEqual(north, 43.5)

    def test_projection_distortion_is_below_half_percent(self) -> None:
        self.assertLess(coastal.relative_projection_error_percent(), 0.5)

    def test_expected_marine_coverage_respects_buffer_and_tolerance(self) -> None:
        self.assertTrue(
            overlay_validation.expected_marine_coverage(1000, 1852, 100)
        )
        self.assertFalse(
            overlay_validation.expected_marine_coverage(3000, 1852, 100)
        )
        self.assertIsNone(
            overlay_validation.expected_marine_coverage(1900, 1852, 100)
        )

    def test_geojson_writer_emits_licensed_feature_collection(self) -> None:
        geometry = ogr.CreateGeometryFromWkt(
            "POLYGON ((15 43, 15.1 43, 15.1 43.1, 15 43.1, 15 43))"
        )
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "overlay.geojson"
            coastal.write_geojson(output, geometry, 6, 11112)
            document = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(document["type"], "FeatureCollection")
        self.assertEqual(len(document["features"]), 1)
        properties = document["features"][0]["properties"]
        self.assertEqual(document["name"], "adriatic_6nm")
        self.assertEqual(properties["distance_m"], 11112)
        self.assertEqual(properties["license"], "ODbL-1.0")

    def test_geojson_name_follows_the_buffer_distance(self) -> None:
        geometry = ogr.CreateGeometryFromWkt(
            "POLYGON ((15 43, 15.1 43, 15.1 43.1, 15 43.1, 15 43))"
        )
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "overlay.geojson"
            coastal.write_geojson(output, geometry, 12, 22224)
            document = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(document["name"], "adriatic_12nm")
        self.assertEqual(document["features"][0]["properties"]["distance_nm"], 12)

    def test_metadata_records_source_provenance_and_tool_versions(self) -> None:
        statistics = coastal.BuildStatistics(
            source_features=2,
            source_polygons=3,
            output_area_square_kilometres=4.5,
            output_bounds=(11.4, 39.0, 20.7, 46.1),
            projection_max_relative_error_percent=0.1,
        )
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.zip"
            metadata_path = Path(directory) / "metadata.json"
            source.write_bytes(b"source data")
            retrieved_timestamp = 1_700_000_000
            os.utime(source, (retrieved_timestamp, retrieved_timestamp))
            coastal.write_metadata(
                metadata_path,
                source,
                "https://example.invalid/source.zip",
                "2026-08-22T03:36:41Z",
                6,
                11112,
                50,
                statistics,
            )
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            expected_sha256 = coastal.sha256_file(source)

        self.assertEqual(metadata["source_archive_bytes"], 11)
        self.assertEqual(metadata["source_retrieved_at"], "2023-11-14T22:13:20+00:00")
        self.assertEqual(metadata["source_date"], "2026-08-22T03:36:41Z")
        self.assertEqual(metadata["source_sha256"], expected_sha256)
        self.assertRegex(metadata["tool_versions"]["python"], r"^\d+\.\d+\.\d+")
        self.assertIn("GDAL", metadata["tool_versions"]["gdal"])
        self.assertRegex(metadata["tool_versions"]["proj"], r"^\d+\.\d+\.\d+$")


if __name__ == "__main__":
    unittest.main()
