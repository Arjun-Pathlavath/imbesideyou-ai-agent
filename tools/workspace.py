from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent


def list_workspace_files():
    """List project files without exposing virtual-environment or Git internals."""
    excluded = {".git", ".venv", "__pycache__", ".pytest_cache"}

    files = []

    for path in WORKSPACE_ROOT.rglob("*"):
        if not path.is_file():
            continue

        relative = path.relative_to(WORKSPACE_ROOT)

        if any(part in excluded for part in relative.parts):
            continue

        files.append(str(relative))

    return sorted(files)


def read_workspace_file(relative_path: str) -> str:
    """Read a text file only if it is inside the agent workspace."""
    root = WORKSPACE_ROOT.resolve()
    target = (root / relative_path).resolve()

    if target != root and root not in target.parents:
        raise ValueError("Access outside the agent workspace is not allowed.")

    if not target.is_file():
        raise FileNotFoundError(f"File not found: {relative_path}")

    if target.stat().st_size > 1_000_000:
        raise ValueError("Files larger than 1 MB cannot be read.")

    return target.read_text(encoding="utf-8")


if __name__ == "__main__":
    for filename in list_workspace_files():
        print(filename)