"""Convert supplied BLS county annual XLSX files and prepare a KS/MO panel, offline."""
import argparse
import csv
import hashlib
import json
import posixpath
import re
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
HEADERS = ["LAUS Code", "State FIPS Code", "County FIPS Code", "County Name/State Abbreviation",
           "Year", "Labor Force", "Employed", "Unemployed", "Unemployment Rate (%)"]
EXPECTED = {"KS": ("20", 105), "MO": ("29", 115)}
MISSING = {"", "N.A.", "NA", "N/A", "-", "--"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path, rows, fields=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields or list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_sheet(path):
    """Read cell addresses, shared/inline text and cached values, without Excel.

    This adapter expects one nonformula sheet; it is not a general Excel converter.
    """
    with zipfile.ZipFile(path) as z:
        workbook = ET.fromstring(z.read("xl/workbook.xml"))
        sheets = workbook.findall("s:sheets/s:sheet", NS)
        if len(sheets) != 1:
            raise ValueError(f"Expected one sheet: {path.name}")
        sheet = sheets[0]
        relid = sheet.get("{" + NS["r"] + "}id")
        relationships = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        rel = next(r for r in relationships if r.get("Id") == relid)
        target = rel.get("Target")
        member = target.lstrip("/") if target.startswith("/") else posixpath.normpath("xl/" + target)
        strings = []
        if "xl/sharedStrings.xml" in z.namelist():
            strings = ["".join(t.text or "" for t in si.findall(".//s:t", NS))
                       for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("s:si", NS)]
        rows = []
        for r in ET.fromstring(z.read(member)).findall("s:sheetData/s:row", NS):
            values = {}
            for c in r.findall("s:c", NS):
                if c.find("s:f", NS) is not None:
                    raise ValueError(f"Unexpected formula in {path.name}/{c.get('r')}; review before converting")
                col = re.match(r"[A-Z]+", c.get("r", ""))
                if not col:
                    raise ValueError("Cell without a valid address")
                value = c.find("s:v", NS)
                text = value.text if value is not None else ""
                if c.get("t") == "s":
                    text = strings[int(text)]
                elif c.get("t") == "inlineStr":
                    text = "".join(t.text or "" for t in c.findall(".//s:t", NS))
                elif c.get("t") == "e":
                    raise ValueError(f"Excel error in {path.name}/{c.get('r')}: {text}")
                values[col[0]] = text or ""
            rows.append((int(r.get("r")), values))
    return sheet.get("name"), rows


def fips_component(value, width):
    if not value.isdigit() or len(value) > width:
        raise ValueError(f"Invalid {width}-digit FIPS component: {value!r}")
    return value.zfill(width)


def number(value, integer=False):
    if value.strip() in MISSING:
        return None
    try:
        d = Decimal(value.replace(",", ""))
    except InvalidOperation as exc:
        raise ValueError(f"Unknown numeric token: {value!r}") from exc
    if not d.is_finite() or d < 0:
        raise ValueError(f"Invalid nonnegative value: {value!r}")
    if integer:
        if d != d.to_integral_value():
            raise ValueError(f"Nonintegral person count: {value}")
        return int(d)
    if d > 100:
        raise ValueError(f"Rate exceeds 100: {value}")
    rounded = d.quantize(Decimal("0.1"))
    if abs(d-rounded) > Decimal("0.000000001"):
        raise ValueError(f"Unexpected rate precision: {value}")
    return rounded


def average_period(year, state_fips):
    if year == 2025 and state_fips != "72":
        return 11, "eleven_month_average_excluding_october", "2025-10"
    return 12, "annual_average", ""


def parse_workbook(path):
    match = re.fullmatch(r"laucnty(\d{2})\.xlsx", path.name)
    if not match:
        raise ValueError(f"Unsupported filename: {path.name}")
    expected_year = 2000 + int(match[1])
    sheet_name, grid = read_sheet(path)
    columns = list("ABCDEFGHI")
    header = next((i for i, (_, r) in enumerate(grid) if [r.get(c, "") for c in columns] == HEADERS), None)
    if header is None:
        raise ValueError(f"Unexpected header: {path.name}")
    title = " | ".join(r.get("A", "") for _, r in grid[:header] if r.get("A"))
    if str(expected_year) not in title:
        raise ValueError(f"Title does not match filename year: {path.name}")
    notes, records, converted, alerts = [], [], [], []
    seen = set()
    for row_number, row in grid[header+1:]:
        if not row.get("A", "").startswith("CN"):
            if any(row.values()):
                notes.append({"worksheet_row": row_number, "cells": row})
            continue
        code = row["A"]
        state_fips = fips_component(row["B"], 2)
        local_fips = fips_component(row["C"], 3)
        county_fips = state_fips + local_fips
        if not re.fullmatch(r"CN\d{13}", code) or code[2:7] != county_fips:
            raise ValueError(f"LAUS/FIPS mismatch: {path.name}:{row_number}")
        year = int(row["E"])
        if year != expected_year or county_fips in seen:
            raise ValueError(f"Wrong year or duplicate county: {path.name}:{row_number}")
        seen.add(county_fips)
        if row["D"] == "District of Columbia" and state_fips == "11":
            name, state = row["D"], "DC"
        else:
            parts = row["D"].rsplit(", ", 1)
            if len(parts) != 2:
                raise ValueError(f"Unsupported county/state label: {row['D']!r}")
            name, state = parts
        if state in EXPECTED and EXPECTED[state][0] != state_fips:
            raise ValueError(f"State/FIPS mismatch: {path.name}:{row_number}")
        lf, emp, unemployed = [number(row.get(c, ""), integer=True) for c in "FGH"]
        rate = number(row.get("I", ""))
        vals = [lf, emp, unemployed, rate]
        if any(x is None for x in vals) and not all(x is None for x in vals):
            raise ValueError(f"Partially missing labor measures: {path.name}:{row_number}")
        if lf is not None:
            if lf != emp + unemployed:
                raise ValueError(f"Employment/unemployment do not add to labor force: {county_fips}/{year}")
            if lf and abs(Decimal(unemployed)*100/Decimal(lf)-rate) > Decimal("0.10"):
                alerts.append({"county_fips": county_fips, "year": year,
                               "reason": "Published rate differs from rate reconstructed from rounded counts by >0.10 pp; retain source rate."})
        months, period, excluded = average_period(year, state_fips)
        records.append({"state": state, "state_fips": state_fips, "county_fips": county_fips, "laus_code": code,
                        "county_fips_component": local_fips, "county_name": name, "year": year,
                        "labor_force": lf, "employed": emp, "unemployed": unemployed,
                        "unemployment_rate_pct": str(rate) if rate is not None else None,
                        "averaging_months": months, "period_type": period, "excluded_month": excluded,
                        "geographic_basis": "place_of_residence", "seasonal_adjustment": "not_seasonally_adjusted",
                        "data_status": "published_estimate" if lf is not None else "source_unavailable",
                        "source_file": path.name, "source_sheet": sheet_name, "source_row": row_number})
        source_row = {h: row.get(c, "") for h, c in zip(HEADERS, columns)}
        if rate is not None:
            source_row[HEADERS[-1]] = str(rate)
        converted.append(source_row)
    if not records:
        raise ValueError(f"No data in {path.name}")
    if expected_year == 2025 and not any("exclude October" in n["cells"].get("A", "") for n in notes):
        raise ValueError("2025 averaging footnote missing or changed; review period classification")
    dates = [n["cells"].get("A", "") for n in notes if re.fullmatch(r"[A-Za-z]+ \d{1,2}, \d{4}", n["cells"].get("A", ""))]
    meta = {"file": path.name, "sha256": sha(path), "sheet": sheet_name, "year": expected_year,
            "title": title, "data_rows": len(records), "source_date_text": dates[-1] if dates else "",
            "source_notes": notes, "rate_consistency_alerts": alerts,
            "ks_rows": sum(r["state"] == "KS" for r in records),
            "mo_rows": sum(r["state"] == "MO" for r in records)}
    for r in records:
        r["source_date_text"] = meta["source_date_text"]
    return records, converted, meta


def prepare(raw_dir, csv_dir, output_dir):
    files = sorted(raw_dir.glob("laucnty*.xlsx"))
    if not files:
        raise ValueError(f"No matching workbooks: {raw_dir}")
    all_rows, inventory = [], []
    years = set()
    for path in files:
        records, converted, meta = parse_workbook(path)
        year = meta["year"]
        if year in years:
            raise ValueError(f"Duplicate source year {year}")
        years.add(year)
        csv_path = csv_dir / (path.stem + ".csv")
        write_csv(csv_path, converted, HEADERS)
        meta["converted_csv_sha256"] = sha(csv_path)
        all_rows.extend(records)
        inventory.append(meta)
    all_rows.sort(key=lambda r: (r["year"], r["county_fips"]))
    selected = [r for r in all_rows if r["state"] in EXPECTED]
    coverage, previous_sets = [], {}
    for year in sorted(years):
        for state, (prefix, expected) in EXPECTED.items():
            group = [r for r in selected if r["year"] == year and r["state"] == state]
            keys = {r["county_fips"] for r in group}
            if len(group) != expected or len(keys) != expected or any(not k.startswith(prefix) for k in keys):
                raise ValueError(f"{state}/{year}: expected {expected} unique county equivalents; got {len(group)}")
            if state in previous_sets and previous_sets[state] != keys:
                raise ValueError(f"{state}/{year}: county set changed; reconcile geography")
            previous_sets[state] = keys
            missing = sum(r["data_status"] != "published_estimate" for r in group)
            if missing:
                raise ValueError(f"{state}/{year}: {missing} counties have unavailable values")
            coverage.append({"state": state, "year": year, "county_count": len(group),
                             "expected_counties": expected, "missing_measure_rows": missing,
                             "averaging_months": group[0]["averaging_months"]})
    write_csv(output_dir / "county_annual_ks_mo.csv", selected)
    write_csv(output_dir / "county_annual_all_source_areas.csv", all_rows)
    write_csv(output_dir / "coverage_by_year.csv", coverage)
    write_csv(output_dir / "source_inventory.csv", [{k: v for k, v in m.items() if k not in {"source_notes", "rate_consistency_alerts"}} for m in inventory])
    # A clearly flagged descriptive comparison, never relabeled as matched annual change.
    comparison = []
    if {2024, 2025} <= years:
        a = {r["county_fips"]: r for r in selected if r["year"] == 2024}
        b = {r["county_fips"]: r for r in selected if r["year"] == 2025}
        for key in sorted(a.keys() & b.keys()):
            x, y = a[key], b[key]
            row = {"state": x["state"], "county_fips": key, "county_name": x["county_name"],
                   "start_year": 2024, "end_year": 2025, "start_averaging_months": 12, "end_averaging_months": 11,
                   "comparability": "not_strictly_comparable_12_vs_11_months",
                   "unemployment_rate_2024_pct": x["unemployment_rate_pct"],
                   "unemployment_rate_2025_pct": y["unemployment_rate_pct"],
                   "unemployment_rate_difference_pp": str(Decimal(y["unemployment_rate_pct"])-Decimal(x["unemployment_rate_pct"]))}
            for field in ("labor_force", "employed", "unemployed"):
                row[field + "_2024"] = x[field]
                row[field + "_2025"] = y[field]
                row[field + "_difference_persons"] = y[field]-x[field]
            comparison.append(row)
        write_csv(output_dir / "county_comparison_2024_2025_caveated.csv", comparison)
    report = {"years": sorted(years), "ks_mo_rows": len(selected), "all_source_area_rows": len(all_rows),
              "ks_mo_unique_counties": len({r["county_fips"] for r in selected}), "coverage": coverage,
              "all_source_unavailable_rows": sum(r["data_status"] == "source_unavailable" for r in all_rows),
              "rate_consistency_alerts": [a for m in inventory for a in m["rate_consistency_alerts"]],
              "source_files": inventory,
              "warnings": ["These are annual/11-month averages, not monthly observations.",
                           "No 2026 observations were supplied.",
                           "2025 KS/MO data exclude October; comparison to 2024 full-year averages is not strictly comparable.",
                           "Rates refer to residents' labor force, not workplace jobs or population employment rates.",
                           "National source geography includes Puerto Rico and changes across years; no universal fixed county universe is assumed.",
                           "Published rates are preserved at one decimal place; binary Excel storage artifacts are normalized."]}
    write_json(output_dir / "manifest.json", report)
    write_json(csv_dir / "workbook_metadata.json", {"source_url": "https://www.bls.gov/lau/tables.htm", "workbooks": inventory})
    text = ["# LAUS annual conversion report", "", f"Converted {len(files)} workbooks for {min(years)}–{max(years)}.",
            f"KS/MO: {len(selected):,} county-year rows, {report['ks_mo_unique_counties']} county equivalents; 105 KS and 115 MO in every supplied year, with no missing KS/MO measures.",
            f"All source areas: {len(all_rows):,} rows; {report['all_source_unavailable_rows']} unavailable source rows retained with blanks/status flags.",
            "", "## Important limitations", "", *["- " + s for s in report["warnings"]], "",
            "## Validation", "", "- Expected schema, title year, LAUS/FIPS consistency and unique county/year checked.",
            "- KS/MO county sets stable across supplied years; all required measures present.",
            "- Published labor force equals employed plus unemployed wherever counts are available.",
            f"- {len(report['rate_consistency_alerts'])} rate/count rounding alerts; original published rates retained. See manifest.json.",
            "- XLSX source hashes, converted CSV hashes, worksheet row references and footnotes retained.", "",
            "## Next analytical input", "", "Acquire county monthly LAUS observations through the latest pre-election 2026 month. Recompute comparisons using the same available months in both years; do not reconstruct October 2025 from these annual files.", ""]
    (output_dir / "quality_report.md").write_text("\n".join(text), encoding="utf-8")
    print(f"Converted {len(files)} XLSX files: {len(all_rows):,} total source rows; {len(selected):,} KS/MO county-year rows.")
    print("Every supplied year: KS 105 / MO 115. No missing KS/MO measures. 2025 excludes October; no 2026 input.")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=ROOT / "data/raw/bls_laus_annual/xlsx")
    parser.add_argument("--csv-dir", type=Path, default=ROOT / "data/raw/bls_laus_annual/csv")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data/processed/laus_annual")
    args = parser.parse_args()
    try:
        prepare(args.raw_dir, args.csv_dir, args.output_dir)
    except (ValueError, OSError, KeyError, zipfile.BadZipFile) as exc:
        parser.exit(1, f"ERROR: {exc}\n")


if __name__ == "__main__":
    main()
