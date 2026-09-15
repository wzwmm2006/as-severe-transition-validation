import argparse, json, sys
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "src"))


def arguments(description):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--config", required=True, help="YAML configuration outside the public repository")
    return parser.parse_args()


def emit(result):
    print(json.dumps(result, indent=2))

