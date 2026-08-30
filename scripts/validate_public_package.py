#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "prompt-it"
SKILL = PLUGIN / "skills" / "prompt-it" / "SKILL.md"
CLAUDE_MANIFEST = PLUGIN / ".claude-plugin" / "plugin.json"
CODEX_MANIFEST = PLUGIN / ".codex-plugin" / "plugin.json"


def fail(message: str) -> None:
    raise ValueError(message)


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot load {path.relative_to(ROOT)}: {exc}")
    if not isinstance(value, dict):
        fail(f"{path.relative_to(ROOT)} must contain an object")
    return value


def validate() -> None:
    required = [
        ROOT / "LICENSE",
        ROOT / ".claude-plugin" / "marketplace.json",
        ROOT / ".agents" / "plugins" / "marketplace.json",
        CLAUDE_MANIFEST,
        CODEX_MANIFEST,
        SKILL,
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        fail(f"missing required files: {', '.join(missing)}")

    claude = load_json(CLAUDE_MANIFEST)
    codex = load_json(CODEX_MANIFEST)
    if claude.get("name") != "prompt-it" or codex.get("name") != "prompt-it":
        fail("plugin names must be prompt-it")
    if claude.get("version") != "1.2.0" or codex.get("version") != "1.2.0":
        fail("Claude and Codex plugin versions must both be 1.2.0")
    if claude.get("license") != "MIT" or codex.get("license") != "MIT":
        fail("Claude and Codex manifests must declare MIT")

    codex_market = load_json(ROOT / ".agents" / "plugins" / "marketplace.json")
    claude_market = load_json(ROOT / ".claude-plugin" / "marketplace.json")
    for label, market in (("Codex", codex_market), ("Claude", claude_market)):
        plugins = market.get("plugins")
        if not isinstance(plugins, list) or not any(
            isinstance(item, dict) and item.get("name") == "prompt-it"
            for item in plugins
        ):
            fail(f"{label} marketplace must list prompt-it")

    text = SKILL.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    required_phrases = (
        "Before a substantial new task",
        "Research before drafting",
        "dedicated worktree",
        "never trigger automatic quota detection",
    )
    for phrase in required_phrases:
        if phrase not in normalized:
            fail(f"canonical skill is missing required contract: {phrase}")

    banned = ("credible" + "mind", "project-" + "lifeview", "/users/" + "marcos")
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        try:
            value = path.read_text(encoding="utf-8").lower()
        except UnicodeDecodeError:
            continue
        for marker in banned:
            if marker in value:
                fail(f"private marker {marker!r} found in {path.relative_to(ROOT)}")

    digest = hashlib.sha256(SKILL.read_bytes()).hexdigest()
    print(f"prompt-it public package validation passed ({digest[:12]})")


if __name__ == "__main__":
    try:
        validate()
    except ValueError as exc:
        print(f"validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
