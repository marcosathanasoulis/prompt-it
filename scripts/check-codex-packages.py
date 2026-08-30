#!/usr/bin/env python3

"""Validate the public Codex plugin packages with the Python standard library."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
PACKAGES = (
    REPO_ROOT / "codex-plugin",
    REPO_ROOT / "codex-plugins" / "side-lane",
    REPO_ROOT / "codex-plugins" / "bring-me-back",
)
REQUIRED_INTERFACE_FIELDS = (
    "displayName",
    "shortDescription",
    "longDescription",
    "developerName",
    "category",
    "capabilities",
    "defaultPrompt",
)
FRONTMATTER_FIELD = re.compile(r"^(name|description):\s*(.+)$", re.MULTILINE)
MARKDOWN_LINK = re.compile(r"\[[^]]+\]\(([^)]+\.md)(?:#[^)]+)?\)")
PERSONAL_HOME_PATH = re.compile(r"(?:/Users/[^/\s]+/|/home/[^/\s]+/|[A-Za-z]:\\Users\\[^\\\s]+\\)")


def load_json(path: Path, errors: list[str]) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{path.relative_to(REPO_ROOT)}: invalid JSON: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{path.relative_to(REPO_ROOT)}: expected a JSON object")
        return {}
    return value


def require_text(payload: dict, field: str, path: Path, errors: list[str]) -> None:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path.relative_to(REPO_ROOT)}: missing non-empty {field}")


def validate_markdown(path: Path, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    if "[TODO:" in text:
        errors.append(f"{path.relative_to(REPO_ROOT)}: unfinished TODO placeholder")
    if PERSONAL_HOME_PATH.search(text):
        errors.append(f"{path.relative_to(REPO_ROOT)}: contains an absolute user-home path")
    for target in MARKDOWN_LINK.findall(text):
        if "://" in target or target.startswith("/"):
            continue
        resolved = (path.parent / target).resolve()
        if not resolved.is_file():
            errors.append(
                f"{path.relative_to(REPO_ROOT)}: missing Markdown reference {target}"
            )


def validate_package(package: Path, errors: list[str]) -> None:
    manifest_path = package / ".codex-plugin" / "plugin.json"
    source_path = package / ".source.json"
    manifest = load_json(manifest_path, errors)
    source = load_json(source_path, errors)

    for field in ("name", "version", "description", "skills"):
        require_text(manifest, field, manifest_path, errors)

    interface = manifest.get("interface")
    if not isinstance(interface, dict):
        errors.append(f"{manifest_path.relative_to(REPO_ROOT)}: missing interface object")
    else:
        for field in REQUIRED_INTERFACE_FIELDS:
            value = interface.get(field)
            if value is None or value == "" or value == []:
                errors.append(
                    f"{manifest_path.relative_to(REPO_ROOT)}: missing interface.{field}"
                )

    expected_package_path = package.relative_to(REPO_ROOT).as_posix()
    if source.get("package_path") != expected_package_path:
        errors.append(
            f"{source_path.relative_to(REPO_ROOT)}: package_path must be "
            f"{expected_package_path!r}"
        )
    if source.get("version") != manifest.get("version"):
        errors.append(
            f"{source_path.relative_to(REPO_ROOT)}: version differs from plugin.json"
        )

    skills_root = package / "skills"
    if not skills_root.is_dir():
        errors.append(f"{skills_root.relative_to(REPO_ROOT)}: missing skills directory")
        return
    skill_dirs = sorted(path for path in skills_root.iterdir() if path.is_dir())
    if not skill_dirs:
        errors.append(f"{skills_root.relative_to(REPO_ROOT)}: no skill directories")
        return

    for skill_dir in skill_dirs:
        skill_path = skill_dir / "SKILL.md"
        if not skill_path.is_file():
            errors.append(f"{skill_path.relative_to(REPO_ROOT)}: missing")
            continue
        text = skill_path.read_text(encoding="utf-8")
        if not text.startswith("---\n") or "\n---\n" not in text[4:]:
            errors.append(f"{skill_path.relative_to(REPO_ROOT)}: invalid frontmatter")
            continue
        frontmatter = text.split("\n---\n", 1)[0][4:]
        fields = dict(FRONTMATTER_FIELD.findall(frontmatter))
        if fields.get("name") != skill_dir.name:
            errors.append(
                f"{skill_path.relative_to(REPO_ROOT)}: name must match directory"
            )
        if not fields.get("description", "").strip():
            errors.append(f"{skill_path.relative_to(REPO_ROOT)}: missing description")

    for markdown_path in package.rglob("*.md"):
        validate_markdown(markdown_path, errors)


def main() -> int:
    errors: list[str] = []
    for package in PACKAGES:
        validate_package(package, errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Validated {len(PACKAGES)} public Codex plugin packages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
