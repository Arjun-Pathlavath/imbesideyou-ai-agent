
from pathlib import Path
import re
from datetime import date
def is_valid_iso_date(value: str) -> bool:
    """Return True only for real dates formatted as YYYY-MM-DD."""
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return False

    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False
ASSIGNMENT_ROOT = Path(
    r"C:\Users\pathl\Desktop\imbesideyou-assignment"
).resolve()

EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
}

ALLOWED_EXTENSIONS = {
    ".md",
    ".py",
    ".json",
    ".jsonl",
    ".csv",
    ".txt",
    ".yml",
    ".yaml",
}


def list_assignment_files():
    """List inspectable files without modifying the assignment."""
    if not ASSIGNMENT_ROOT.is_dir():
        raise FileNotFoundError(
            f"Assignment folder not found: {ASSIGNMENT_ROOT}"
        )

    results = []

    for path in ASSIGNMENT_ROOT.rglob("*"):
        relative = path.relative_to(ASSIGNMENT_ROOT)

        if any(part in EXCLUDED_DIRS for part in relative.parts):
            continue

        if path.is_file() and path.suffix.lower() in ALLOWED_EXTENSIONS:
            results.append(str(relative))

    return sorted(results)


def read_assignment_file(relative_path: str) -> str:
    """Read an allowlisted text file confined to the assignment folder."""
    root = ASSIGNMENT_ROOT.resolve()
    target = (root / relative_path).resolve()

    if target != root and root not in target.parents:
        raise ValueError("Access outside the assignment folder is forbidden.")

    if not target.is_file():
        raise FileNotFoundError(f"File not found: {relative_path}")

    if target.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError("This file type is not allowed for inspection.")

    if target.stat().st_size > 1_000_000:
        raise ValueError("Files larger than 1 MB cannot be read.")

    return target.read_text(encoding="utf-8")


if __name__ == "__main__":
    files = list_assignment_files()

    print(f"Assignment files available for inspection: {len(files)}")
    for filename in files:
        print(f" - {filename}")

    print("\nRead-only listing complete. No assignment files were modified.")
