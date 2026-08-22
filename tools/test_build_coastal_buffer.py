from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from osgeo import gdal, ogr

from tools import build_coastal_buffer as coastal


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

    def test_six_nautical_miles_is_exactly_11112_metres(self) -> None:
        self.assertEqual(coastal.DEFAULT_BUFFER_METRES, 11112.0)

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
        self.assertEqual(properties["distance_m"], 11112)
        self.assertEqual(properties["license"], "ODbL-1.0")


if __name__ == "__main__":
    unittest.main()
