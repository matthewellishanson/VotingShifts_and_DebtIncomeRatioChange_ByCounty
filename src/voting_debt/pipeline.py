"""Deterministic offline pipeline. Source files are never edited in place."""
import csv
import hashlib
import io
import json
import zipfile
from collections import defaultdict
from pathlib import Path

ARCHIVES = {
    "fed": "household-debt.zip",
    "medsl": "dataverse_files.zip",
    "ctm": "callthemap-results-2026-all.zip",
}


def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows):
    if not rows:
        raise ValueError(f"No rows to write: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fips(value):
    value = value.strip()
    if not value.isdigit() or len(value) > 5:
        raise ValueError(f"Invalid FIPS: {value!r}")
    return value.zfill(5)


def margin(dem, rep, total):
    if total <= 0:
        return None
    if min(dem, rep) < 0 or dem + rep > total:
        raise ValueError("Invalid candidate totals")
    return 100 * (dem - rep) / total


def transition(start, end):
    a, b = float(start["low"]), float(end["low"])
    return "higher_category" if b > a else "lower_category" if b < a else "same_category"


def archive_rows(z, name):
    with z.open(name) as raw:
        return list(csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8-sig")))


def load_config(root):
    cfg = json.loads((root / "config/demo.json").read_text())
    if cfg["presidential_year"] != 2024 or cfg["comparison_year"] != 2026:
        raise ValueError("This adapter supports 2024 president and 2026 comparisons only; extend code before changing years.")
    if cfg["states"] != {"KS": "20", "MO": "29"}:
        raise ValueError("This adapter is scoped to KS/MO; review reporting geography before expanding states.")
    for field in ("debt_start", "debt_end"):
        y, q = cfg[field]
        if not (1999 <= y <= 2025 and q in (1, 2, 3, 4)):
            raise ValueError(f"Unsupported {field}: {cfg[field]}")
    if tuple(cfg["debt_start"]) >= tuple(cfg["debt_end"]):
        raise ValueError("Debt start must precede end")
    return cfg


def import_sources(root):
    cfg = load_config(root)
    states = cfg["states"]
    raw = root / "data/raw"
    manifest = {"scope": cfg, "archives": [], "subsets": []}
    for source, name in ARCHIVES.items():
        path = root / "data/archives" / name
        if not path.exists():
            raise ValueError(f"Missing {path}. See README: original archive placement.")
        manifest["archives"].append({"source": source, "path": str(path.relative_to(root)), "sha256": digest(path)})
        with zipfile.ZipFile(path) as z:
            if source == "fed":
                rows = [r for r in archive_rows(z, "household-debt-by-county.csv")
                        if r["area_fips"][:2] in states.values()
                        and int(r["year"]) in range(cfg["debt_start"][0], cfg["debt_end"][0] + 1)]
                target = raw / "fed/county_debt_ks_mo.csv"
                docs = [("household-debt-by-county.txt", "dictionary.txt")]
            elif source == "medsl":
                rows = [r for r in archive_rows(z, "countypres_2000-2024.csv")
                        if r["state_po"] in states and int(r["year"]) == cfg["presidential_year"]]
                target = raw / "medsl/president_2024_ks_mo.csv"
                docs = [("County Presidential Returns 2000-2024.md", "codebook.md"), ("sources-president.csv", "sources-president.csv")]
            else:
                rows = [r for r in archive_rows(z, "counties.csv")
                        if r["state"] in states and r["office"] in {"House", "Governor", "Senate"}]
                target = raw / "callthemap/counties_2026_ks_mo.csv"
                races = [r for r in archive_rows(z, "races.csv") if r["race_id"] in {x["race_id"] for x in rows}]
                write_csv(raw / "callthemap/races_2026_ks_mo.csv", races)
                docs = [("README.txt", "README_source.txt")]
            write_csv(target, rows)
            for member, filename in docs:
                (target.parent / filename).write_bytes(z.read(member))
            manifest["subsets"].append({"path": str(target.relative_to(root)), "rows": len(rows), "sha256": digest(target)})
    # Include metadata/codebooks too: every file in raw has a recorded digest.
    manifest["raw_files"] = [{"path": p.relative_to(root).as_posix(), "sha256": digest(p)}
                             for p in sorted(raw.rglob("*")) if p.is_file()]
    write_json(root / "data/source_manifest.json", manifest)
    print("Imported source subsets; preserved original archive hashes.")


def president_totals(rows):
    groups = defaultdict(list)
    for r in rows:
        groups[fips(r["county_fips"])].append(r)
    out = {}
    for key, group in groups.items():
        # This scoped adapter intentionally refuses other mode conventions.
        if {r["mode"] for r in group} != {"TOTAL"}:
            raise ValueError(f"{key}: unsupported/mixed presidential modes; review source before expanding.")
        identities = [(r["candidate"], r["party"]) for r in group]
        if len(set(identities)) != len(identities):
            raise ValueError(f"{key}: duplicate presidential candidate rows")
        totals = {int(r["totalvotes"]) for r in group}
        if len(totals) != 1:
            raise ValueError(f"{key}: inconsistent presidential denominators")
        total = totals.pop()
        votes = [int(r["candidatevotes"]) for r in group]
        if min(votes) < 0 or sum(votes) != total:
            raise ValueError(f"{key}: presidential votes do not reconcile")
        dem = sum(int(r["candidatevotes"]) for r in group if r["party"] == "DEMOCRAT")
        rep = sum(int(r["candidatevotes"]) for r in group if r["party"] == "REPUBLICAN")
        out[key] = {"county_name": group[0]["county_name"], "dem": dem, "rep": rep, "total": total,
                    "margin": margin(dem, rep, total), "source_version": group[0]["version"]}
    return out


def comparison_totals(rows):
    groups = defaultdict(list)
    seen = set()
    for r in rows:
        key = (r["state"], r["office"], fips(r["fips"]))
        identity = (r["race_id"], key[2])
        if identity in seen:
            raise ValueError(f"Duplicate county/race: {identity}")
        seen.add(identity)
        if r["place_kind"] not in {"county", "county part"}:
            raise ValueError(f"Unsupported reporting geography: {r['place_kind']}")
        groups[key].append(r)
    out = {}
    for key, group in groups.items():
        dem = rep = total = 0
        comparable = True
        for r in group:
            a, b, other, t = [int(r[k]) for k in ("votes_a", "votes_b", "votes_other", "total_votes")]
            if min(a, b, other, t) < 0 or a + b + other != t:
                raise ValueError(f"{r['race_id']}/{r['fips']}: vote arithmetic mismatch")
            parties = {r["party_a"], r["party_b"]}
            comparable &= parties == {"D", "R"} and a > 0 and b > 0
            dem += (a if r["party_a"] == "D" else 0) + (b if r["party_b"] == "D" else 0)
            rep += (a if r["party_a"] == "R" else 0) + (b if r["party_b"] == "R" else 0)
            total += t
        out[key] = {"dem": dem, "rep": rep, "total": total,
                    "margin": margin(dem, rep, total) if comparable else None,
                    "race_ids": sorted(r["race_id"] for r in group),
                    "finished": all(r["finished"] == "yes" for r in group),
                    "comparable": comparable}
    return out


def prepare(root):
    cfg = load_config(root)
    raw = root / "data/raw"
    manifest = json.loads((root / "data/source_manifest.json").read_text())
    if manifest["scope"] != cfg:
        raise ValueError("Configuration changed: run 'all' again to reimport matching subsets.")
    for subset in manifest["raw_files"]:
        if digest(root / subset["path"]) != subset["sha256"]:
            raise ValueError(f"Source subset changed: {subset['path']}. Reimport or document a new snapshot.")
    debt = read_csv(raw / "fed/county_debt_ks_mo.csv")
    pres = president_totals(read_csv(raw / "medsl/president_2024_ks_mo.csv"))
    comparison_rows = read_csv(raw / "callthemap/counties_2026_ks_mo.csv")
    comp = comparison_totals(comparison_rows)
    race_rows = read_csv(raw / "callthemap/races_2026_ks_mo.csv")
    race_ids = sorted({r["race_id"] for r in comparison_rows})
    reconciliation = []
    for rid in race_ids:
        counties = [r for r in comparison_rows if r["race_id"] == rid]
        races = [r for r in race_rows if r["race_id"] == rid]
        totals = {int(r["total_votes"]) for r in races}
        if len(totals) != 1 or sum(int(r["votes"]) for r in races) != next(iter(totals)):
            raise ValueError(f"{rid}: invalid race-level metadata")
        expected = totals.pop()
        observed = sum(int(r["total_votes"]) for r in counties)
        if observed != expected:
            raise ValueError(f"{rid}: county total {observed} != race total {expected}")
        reconciliation.append({"race_id": rid, "county_total": observed, "race_total": expected, "match": True})
    def period_index(period):
        selected = [r for r in debt if [int(r["year"]), int(r["qtr"])] == period]
        out = {fips(r["area_fips"]): r for r in selected}
        if len(out) != len(selected):
            raise ValueError("Duplicate county/quarter debt observations")
        return out
    start, end = period_index(cfg["debt_start"]), period_index(cfg["debt_end"])
    if start.keys() != end.keys():
        raise ValueError("Debt periods have different geographic coverage")
    output, issues = [], []
    for key, p in pres.items():
        if key not in start:
            issues.append({"source_fips": key, "county_name": p["county_name"], "reason": "Unmatched reporting unit; do not allocate its votes using population weights."})
    for st, prefix in cfg["states"].items():
        keys = sorted(k for k in start if k.startswith(prefix))
        if len(keys) != cfg["expected_counties"][st]:
            raise ValueError(f"{st}: unexpected county count {len(keys)}")
        for key in keys:
            p = pres.get(key)
            blocked = key in cfg["missouri_unresolved_counties"] or p is None
            row = {"state": st, "county_fips": key, "county_name": p["county_name"] if p else key,
                   "debt_start_period": f"{cfg['debt_start'][0]}Q{cfg['debt_start'][1]}",
                   "debt_end_period": f"{cfg['debt_end'][0]}Q{cfg['debt_end'][1]}",
                   "debt_start_low": float(start[key]["low"]),
                   "debt_start_high": float(start[key]["high"]) if start[key]["high"] else None,
                   "debt_end_low": float(end[key]["low"]),
                   "debt_end_high": float(end[key]["high"]) if end[key]["high"] else None,
                   "debt_transition": transition(start[key], end[key]),
                   "president_2024_dem_votes": p["dem"] if p else None,
                   "president_2024_rep_votes": p["rep"] if p else None,
                   "president_2024_total_votes": p["total"] if p else None,
                   "president_2024_margin_pp": p["margin"] if p and not blocked else None,
                   "president_source_version": p["source_version"] if p else None,
                   "president_geography_status": "needs_reconciliation" if blocked else "matched",
                   "comparison_year": cfg["comparison_year"],
                   "results_status": "provisional_unverified"}
            if blocked:
                issues.append({"source_fips": key, "county_name": row["county_name"], "reason": "Presidential geographic baseline withheld pending official reconciliation."})
            for office in ("House", "Governor", "Senate"):
                c = comp.get((st, office, key))
                tag = office.lower() + "_2026"
                row[tag + "_dem_votes"] = c["dem"] if c else None
                row[tag + "_rep_votes"] = c["rep"] if c else None
                row[tag + "_total_votes"] = c["total"] if c else None
                row[tag + "_margin_pp"] = c["margin"] if c else None
                row[tag + "_minus_president_2024_pp"] = (c["margin"] - p["margin"]
                    if c and c["margin"] is not None and p and not blocked else None)
                row[tag + "_race_ids"] = ";".join(c["race_ids"]) if c else ""
                row[tag + "_source_finished"] = c["finished"] if c else None
            output.append(row)
    counts = {st: {label: sum(r["state"] == st and r["debt_transition"] == label for r in output)
                   for label in ("higher_category", "same_category", "lower_category")} for st in cfg["states"]}
    unfinished = sum(r["finished"] != "yes" for r in comparison_rows)
    report = {"pipeline_status": "passed_with_documented_limitations", "county_rows": len(output),
              "source_manifest_sha256": digest(root / "data/source_manifest.json"),
              "comparison_county_part_rows": len(comparison_rows),
              "source_not_marked_finished_rows": unfinished,
              "debt_periods": [cfg["debt_start"], cfg["debt_end"]], "debt_category_counts": counts,
              "race_reconciliation": reconciliation, "geographic_issues": issues,
              "limitations": ["2026 counts are provisional and have not been independently verified against certified returns.",
                  f"{unfinished} of {len(comparison_rows)} source county/part rows are not marked finished=yes; a called race is not certification.",
                  "No exact debt change or debt/electoral-change ratio is calculated.",
                  "2024 House data were not supplied; same-office House shift is not available.",
                  "Missouri has no Governor or Senate comparison in this supplied snapshot."]}
    processed = root / "data/processed"
    write_csv(processed / "county_demo.csv", output)
    write_json(processed / "county_demo.json", {"metadata": report, "counties": output})
    write_json(root / "reports/quality_report.json", report)
    text = ["# Data quality report", "", f"Prepared {len(output)} county rows. These are research outputs, not publication-ready verified results.", "",
            "## Limitations", "", *["- " + x for x in report["limitations"]], "", "## Geographic holds", ""]
    text.extend(f"- {x['source_fips']} / {x['county_name']}: {x['reason']}" for x in issues)
    text += ["", f"All {len(reconciliation)} selected race totals reconcile within the supplied archive. This checks internal consistency, not independent accuracy.", ""]
    (root / "reports/quality_report.md").write_text("\n".join(text), encoding="utf-8")
    print(f"Prepared {len(output)} county rows; {len(reconciliation)} race totals reconcile.")
    print("Read reports/quality_report.md before analysis. MO geographic holds and provisional 2026 status remain.")
