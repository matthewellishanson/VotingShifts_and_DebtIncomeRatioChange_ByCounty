"""Run from any working directory; no installation or third-party packages required."""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from voting_debt.pipeline import import_sources, prepare

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("command", choices=["import", "prepare", "all"])
args = parser.parse_args()
try:
    if args.command in {"import", "all"}:
        import_sources(ROOT)
    if args.command in {"prepare", "all"}:
        prepare(ROOT)
except (ValueError, OSError, KeyError) as exc:
    parser.exit(1, f"ERROR: {exc}\n")
