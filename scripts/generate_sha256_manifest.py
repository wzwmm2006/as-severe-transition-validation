"""Generate a deterministic checksum list for public repository files."""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "manifests" / "SHA256SUMS"
EXCLUDED = {".git", ".pytest_cache", "__pycache__"}

files = [p for p in ROOT.rglob("*") if p.is_file() and not any(part in EXCLUDED for part in p.parts)
         and p != OUTPUT and not p.name.endswith((".pyc", ".pyo"))]
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
lines = [f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(ROOT).as_posix()}" for path in sorted(files)]
OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

