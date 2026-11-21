#!/usr/bin/env python3
"""Prepare validated static data for the Kansas research frontend.

The normal command copies rebuildable pipeline output and the reviewed Census
geometry subset into ``frontend/public/data``. Geometry import is an explicit,
separate operation because it changes a versioned input snapshot.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DATA = ROOT / "data" / "processed" / "county_demo.json"
GEOMETRY_ARCHIVE = ROOT / "data" / "archives" / "cb_2024_us_county_500k.zip"
GEOMETRY_SUBSET = ROOT / "data" / "raw" / "census" / "ks_counties_2024_500k.geojson"
GEOMETRY_MANIFEST = ROOT / "data" / "raw" / "census" / "geometry_manifest.json"
PUBLIC_DATA = ROOT / "frontend" / "public" / "data"

SOURCE_URL = "https://www2.census.gov/geo/tiger/GENZ2024/kml/cb_2024_us_county_500k.zip"
SOURCE_PAGE = "https://www.census.gov/geographies/mapping-files/2024/geo/carto-boundary-file.html"
ARCHIVE_SHA256 = "6b8cb48faba362e629fa179c77a01e3df4472d25730c7275a1cced3f940e6a69"
KML_NS = "http://www.opengis.net/kml/2.2"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _coordinates(text: str | None) -> list[list[float]]:
    if not text:
        raise ValueError("Census KML ring has no coordinates")
    points: list[list[float]] = []
    for coordinate in text.split():
        longitude, latitude, *_ = coordinate.split(",")
        points.append([float(longitude), float(latitude)])
    if len(points) < 4 or points[0] != points[-1]:
        raise ValueError("Census KML ring is not a closed polygon")
    return points


def import_geometry() -> None:
    if not GEOMETRY_ARCHIVE.exists():
        raise FileNotFoundError(
            f"Missing {GEOMETRY_ARCHIVE.relative_to(ROOT)}. Download the pinned archive from {SOURCE_URL}."
        )
    archive_hash = sha256(GEOMETRY_ARCHIVE)
    if archive_hash != ARCHIVE_SHA256:
        raise ValueError(
            f"Unexpected Census archive SHA-256: {archive_hash}; expected {ARCHIVE_SHA256}"
        )

    with ZipFile(GEOMETRY_ARCHIVE) as archive:
        member = "cb_2024_us_county_500k.kml"
        with archive.open(member) as source:
            root = ET.parse(source).getroot()

    namespace = {"k": KML_NS}
    features: list[dict[str, object]] = []
    for placemark in root.findall(".//k:Placemark", namespace):
        properties = {
            item.attrib["name"]: (item.text or "").strip()
            for item in placemark.findall(".//k:SimpleData", namespace)
        }
        if properties.get("STATEFP") != "20":
            continue

        polygons: list[list[list[list[float]]]] = []
        for polygon in placemark.findall(".//k:Polygon", namespace):
            outer = polygon.find(
                "./k:outerBoundaryIs/k:LinearRing/k:coordinates", namespace
            )
            if outer is None:
                raise ValueError(f"County {properties.get('GEOID')} has no outer boundary")
            rings = [_coordinates(outer.text)]
            rings.extend(
                _coordinates(inner.text)
                for inner in polygon.findall(
                    "./k:innerBoundaryIs/k:LinearRing/k:coordinates", namespace
                )
            )
            polygons.append(rings)

        if not polygons:
            raise ValueError(f"County {properties.get('GEOID')} has no polygon geometry")
        geometry: dict[str, object]
        if len(polygons) == 1:
            geometry = {"type": "Polygon", "coordinates": polygons[0]}
        else:
            geometry = {"type": "MultiPolygon", "coordinates": polygons}

        features.append(
            {
                "type": "Feature",
                "properties": {
                    "county_fips": properties["GEOID"],
                    "county_name": properties["NAME"],
                    "county_label": properties["NAMELSAD"],
                    "state": properties["STUSPS"],
                },
                "geometry": geometry,
            }
        )

    features.sort(key=lambda feature: str(feature["properties"]["county_fips"]))
    if len(features) != 105:
        raise ValueError(f"Expected 105 Kansas county geometries; found {len(features)}")

    collection = {
        "type": "FeatureCollection",
        "metadata": {
            "source": "U.S. Census Bureau 2024 Cartographic Boundary Files",
            "source_url": SOURCE_URL,
            "source_page": SOURCE_PAGE,
            "vintage": 2024,
            "scale": "1:500,000",
            "retrieved": "2026-11-18",
            "archive_sha256": archive_hash,
            "scope": "Kansas counties (STATEFP 20)",
        },
        "features": features,
    }
    GEOMETRY_SUBSET.parent.mkdir(parents=True, exist_ok=True)
    GEOMETRY_SUBSET.write_text(
        json.dumps(collection, separators=(",", ":"), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    manifest = {
        "source_url": SOURCE_URL,
        "source_page": SOURCE_PAGE,
        "retrieved": "2026-11-18",
        "vintage": 2024,
        "scale": "1:500,000",
        "archive_path": str(GEOMETRY_ARCHIVE.relative_to(ROOT)).replace("/", "\\"),
        "archive_sha256": archive_hash,
        "subset_path": str(GEOMETRY_SUBSET.relative_to(ROOT)).replace("/", "\\"),
        "subset_sha256": sha256(GEOMETRY_SUBSET),
        "features": len(features),
        "filter": "STATEFP == '20'",
    }
    GEOMETRY_MANIFEST.write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(
        "Imported 105 Kansas county boundaries from the pinned 2024 Census archive; "
        "recorded archive and subset hashes."
    )


def _load_json(path: Path) -> dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(f"Missing {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def prepare() -> None:
    demo = _load_json(PROCESSED_DATA)
    geometry = _load_json(GEOMETRY_SUBSET)
    geometry_manifest = _load_json(GEOMETRY_MANIFEST)

    recorded_subset_hash = geometry_manifest.get("subset_sha256")
    actual_subset_hash = sha256(GEOMETRY_SUBSET)
    if recorded_subset_hash != actual_subset_hash:
        raise ValueError(
            "Kansas geometry subset does not match data/raw/census/geometry_manifest.json; "
            "review the snapshot and rebuild it explicitly if the change is deliberate"
        )

    counties = demo.get("counties")
    if not isinstance(counties, list):
        raise ValueError("county_demo.json has no counties array")
    kansas = [county for county in counties if county.get("state") == "KS"]
    if len(kansas) != 105:
        raise ValueError(f"Expected 105 Kansas data rows; found {len(kansas)}")

    features = geometry.get("features")
    if not isinstance(features, list) or len(features) != 105:
        raise ValueError("Expected 105 Kansas geometry features")

    data_ids = {str(county["county_fips"]) for county in kansas}
    geometry_ids = {
        str(feature["properties"]["county_fips"]) for feature in features
    }
    if data_ids != geometry_ids:
        missing_geometry = sorted(data_ids - geometry_ids)
        missing_data = sorted(geometry_ids - data_ids)
        raise ValueError(
            f"Kansas FIPS mismatch; missing geometry={missing_geometry}, missing data={missing_data}"
        )
    if any(len(fips) != 5 or not fips.startswith("20") for fips in data_ids):
        raise ValueError("Kansas county FIPS must be five-character strings beginning with 20")

    PUBLIC_DATA.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(PROCESSED_DATA, PUBLIC_DATA / "county_demo.json")
    shutil.copyfile(GEOMETRY_SUBSET, PUBLIC_DATA / "ks_counties.json")
    print(
        "Prepared county_demo.json and 105 matched Kansas boundaries in frontend/public/data."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--import-geometry",
        action="store_true",
        help="Deliberately rebuild the versioned Kansas geometry subset from the pinned local Census ZIP.",
    )
    args = parser.parse_args()
    if args.import_geometry:
        import_geometry()
    prepare()


if __name__ == "__main__":
    main()
