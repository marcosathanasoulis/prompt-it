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
        SKILL.parent / "references" / "research-teams.md",
        SKILL.parent / "references" / "task-graphs.md",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        fail(f"missing required files: {', '.join(missing)}")

    claude = load_json(CLAUDE_MANIFEST)
    codex = load_json(CODEX_MANIFEST)
    if claude.get("name") != "prompt-it" or codex.get("name") != "prompt-it":
        fail("plugin names must be prompt-it")
    if claude.get("version") != "1.3.0" or codex.get("version") != "1.3.0":
        fail("Claude and Codex plugin versions must both be 1.3.0")
    if claude.get("license") != "MIT" or codex.get("license") != "MIT":
        fail("Claude and Codex manifests must declare MIT")

    # Codex declares the skills directory; Claude uses the standard plugin-root
    # skills directory when no additional skills path is configured.
    codex_skills = codex.get("skills")
    claude_skills = claude.get("skills", "./skills/")
    if not isinstance(codex_skills, str) or not isinstance(claude_skills, str):
        fail("canonical package must expose one skills directory per host")
    canonical_skills = (PLUGIN / "skills").resolve()
    if any((PLUGIN / value).resolve() != canonical_skills
           for value in (codex_skills, claude_skills)):
        fail("Claude and Codex must resolve the same canonical skills directory")

    # Both loaders should offer identical gate/authorization semantics.
    gate_blocks = []
    for filename in ("agents-md-gate.md", "claude-md-gate.md"):
        loader = (ROOT / "snippets" / filename).read_text(encoding="utf-8")
        try:
            gate_blocks.append(loader.split("```markdown\n", 1)[1].split("```", 1)[0])
        except IndexError:
            fail(f"missing loader block: {filename}")
    if gate_blocks[0] != gate_blocks[1]:
        fail("Claude and Codex loader gate semantics must remain aligned")

    codex_market = load_json(ROOT / ".agents" / "plugins" / "marketplace.json")
    claude_market = load_json(ROOT / ".claude-plugin" / "marketplace.json")
    for label, market in (("Codex", codex_market), ("Claude", claude_market)):
        plugins = market.get("plugins")
        entries = [item for item in plugins if isinstance(item, dict)
                   and item.get("name") == "prompt-it"] if isinstance(plugins, list) else []
        if len(entries) != 1:
            fail(f"{label} marketplace must list prompt-it exactly once")
        source = entries[0].get("source")
        if isinstance(source, dict) and source.get("source") == "local":
            source = source.get("path")
        if not isinstance(source, str) or (ROOT / source).resolve() != PLUGIN.resolve():
            fail(f"{label} marketplace must resolve the canonical prompt-it package")

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
