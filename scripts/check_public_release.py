"""Fail closed on public-release data, path, or credential hazards."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", ".pytest_cache", "__pycache__"}
FORBIDDEN_SUFFIXES = {".csv", ".tsv", ".parquet", ".feather", ".pkl", ".pickle", ".sqlite", ".sqlite3", ".db", ".duckdb", ".log"}
TEXT_SUFFIXES = {".py", ".md", ".yaml", ".yml", ".json", ".cff", ".txt", ""}
SECRET_PATTERNS = [re.compile(x, re.I) for x in (r"-----BEGIN .*PRIVATE KEY-----", r"api[_-]?key\s*[:=]\s*['\"]?[^ <{]", r"password\s*[:=]\s*['\"]?[^ <{]", r"token\s*[:=]\s*['\"]?[^ <{]")]
ABSOLUTE_PATTERNS = [re.compile(r"(?<![A-Za-z])[A-Za-z]:[\\/](?!path[\\/])"), re.compile(r"/(?:home|Users)/[^\s\"']+")]

errors = []
for path in ROOT.rglob("*"):
    if not path.is_file() or any(part in SKIP_DIRS for part in path.parts):
        continue
    relative = path.relative_to(ROOT).as_posix()
    if path.suffix.lower() in FORBIDDEN_SUFFIXES:
        errors.append(f"forbidden file type: {relative}")
    if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {"LICENSE", ".gitignore", "SHA256SUMS"}:
        errors.append(f"unreviewed binary/unknown file: {relative}")
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        errors.append(f"non-UTF8 file: {relative}")
        continue
    if relative != "scripts/check_public_release.py" and any(pattern.search(text) for pattern in SECRET_PATTERNS):
        errors.append(f"credential-like pattern: {relative}")
    if relative != "PUBLIC_RELEASE_SANITIZATION_REPORT.md" and any(pattern.search(text) for pattern in ABSOLUTE_PATTERNS):
        errors.append(f"unsafe absolute path: {relative}")
    if re.search(r"\b1\d{7}\b", text) and relative.endswith((".json", ".md", ".yaml", ".yml", ".cff")):
        errors.append(f"possible patient identifier in public content: {relative}")

if errors:
    raise SystemExit("PUBLIC_RELEASE_SANITIZATION_FAIL\n" + "\n".join(errors))
print("PUBLIC_RELEASE_SANITIZATION_PASS")
