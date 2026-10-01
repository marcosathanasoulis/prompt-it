#!/usr/bin/env python3
"""Store Prompt it approval mode for one local harness, without credentials."""

import argparse
import json
import os
import stat
import tempfile
from pathlib import Path
import sys

MODES = {"ask-first", "just-go"}

# Claude Code managed (enterprise policy) settings locations -- fixed OS
# paths, independent of any CLAUDE_CONFIG_DIR relocation. Managed settings
# outrank every other source (code.claude.com/docs/en/settings), so a
# managed-declared CLAUDE_CONFIG_DIR wins over the process environment and
# over a user settings declaration.
MANAGED_SETTINGS_PATHS = (
    Path("/Library/Application Support/ClaudeCode/managed-settings.json"),
    Path("/etc/claude-code/managed-settings.json"),
)
# Per-user settings files under the *default* ~/.claude directory -- read
# only when nothing above (managed, then the environment variable) already
# relocates the config directory, matching real Claude Code precedence.
USER_SETTINGS_FILENAMES = ("settings.json", "settings.local.json")


def _settings_declared_config_dir(path):
    """Return a settings file's ``env.CLAUDE_CONFIG_DIR`` string, or ``None``.

    A settings file that is missing, unreadable, or not valid JSON is
    treated as declaring nothing -- the caller falls through to the next
    source rather than crashing, matching
    ``scripts/local_claude_settings.py``'s ``_settings_env_value``.
    ``.strip()`` only decides blankness; a nonblank value is returned
    exactly as declared, leading/trailing whitespace included.

    Open first, then classify the *opened descriptor* (`os.fstat`, not a
    separate `stat()`/`exists()` call against the path) so a symlink or
    mount swapped in between a type check and the open cannot slip a FIFO
    or other special file past the check -- there is no check-then-open
    window, matching ``read_mode()``. `O_NONBLOCK` (POSIX-only; absent on
    Windows, where this whole class of special file does not arise the same
    way) keeps a FIFO open from blocking forever waiting for a writer.
    """
    flags = os.O_RDONLY
    if hasattr(os, "O_NONBLOCK"):
        flags |= os.O_NONBLOCK
    try:
        descriptor = os.open(path, flags)
    except OSError:
        return None
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            return None
        with os.fdopen(descriptor, "r", encoding="utf-8") as handle:
            descriptor = None  # ownership transferred; `with` closes it
            data = json.loads(handle.read())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    finally:
        if descriptor is not None:
            os.close(descriptor)
    if not isinstance(data, dict):
        return None
    env = data.get("env")
    if not isinstance(env, dict):
        return None
    value = env.get("CLAUDE_CONFIG_DIR")
    if isinstance(value, str) and value.strip():
        return value
    return None


def _resolve_claude_config_dir(raw, base):
    """Expand/anchor a declared ``CLAUDE_CONFIG_DIR`` value like Claude does.

    ``~`` expands against the user's home; a relative value resolves from
    ``base`` -- the directory the host itself was launched in.
    """
    candidate = Path(raw).expanduser()
    return candidate if candidate.is_absolute() else base / candidate


def claude_config_root(environ, home, base, managed_paths=MANAGED_SETTINGS_PATHS):
    """Effective ``~/.claude``-equivalent directory, in real precedence order.

    Highest to lowest, matching ``scripts/local_claude_settings.py``'s
    documented precedence (managed settings, then the environment variable,
    then user settings, then the default): a managed settings file's
    ``env.CLAUDE_CONFIG_DIR`` wins outright; otherwise the child's own
    ``CLAUDE_CONFIG_DIR`` environment variable relocates the directory (and,
    matching real Claude Code, the default location's own settings files are
    then not consulted at all); otherwise the default directory's
    ``settings.json``/``settings.local.json`` may themselves declare a
    relocation; otherwise the default directory itself.
    """
    default = home / ".claude"
    for managed_path in managed_paths:
        declared = _settings_declared_config_dir(managed_path)
        if declared:
            return _resolve_claude_config_dir(declared, base)
    override = environ.get("CLAUDE_CONFIG_DIR")
    if override and override.strip():
        return _resolve_claude_config_dir(override, base)
    # Both settings.json and settings.local.json are consulted, in that
    # order, but a later file's declaration wins when both declare one:
    # the host resolver appends both to its directory list in this same
    # order (scripts/local_claude_settings.py's ``user_config_dirs``) and
    # settings.local.json is the more specific, higher-precedence tier, so
    # its declaration is the effective (last-appended) one.
    found = None
    for name in USER_SETTINGS_FILENAMES:
        declared = _settings_declared_config_dir(default / name)
        if declared:
            found = declared
    if found:
        return _resolve_claude_config_dir(found, base)
    return default


def config_path(host):
    # Each host normalizes its override variable differently before
    # resolving it, so the two branches below apply each host's exact
    # normalization separately rather than sharing one code path:
    #
    # - Codex's own installer (scripts/install_local_side_lane.py's
    #   ``codex_home()``) uses ``Path(os.environ.get("CODEX_HOME") or
    #   default)`` directly: no ``str.strip()`` (an empty string is falsy
    #   and falls back to the default, but a whitespace-only string is
    #   truthy and used verbatim) and no ``~`` expansion.
    # - Claude Code's ``CLAUDE_CONFIG_DIR`` resolution
    #   (scripts/local_claude_settings.py's ``user_config_dirs`` /
    #   ``_resolve_config_dir``) checks ``.strip()`` only to decide whether
    #   the raw env value counts as present -- a nonblank value with
    #   leading/trailing whitespace is kept exactly as declared and expanded
    #   (``~``)/anchored verbatim, whitespace and all.
    #
    # Both then resolve a relative result against the directory the host
    # itself was launched in -- this script must run from that same
    # directory rather than the skill's own directory -- see SKILL.md and
    # README.md, which invoke it by absolute path without changing the
    # caller's cwd.
    #
    # For Claude, a saved settings file can also declare CLAUDE_CONFIG_DIR
    # (user or managed tier): a terminal `setup`/`show`/`set` with no
    # matching env override would otherwise write under the default
    # ~/.claude even though the real Claude session honors a relocated
    # directory declared in settings.json/settings.local.json or managed
    # policy -- claude_config_root() applies the same precedence and path
    # semantics as the private host resolver
    # (scripts/local_claude_settings.py's ``user_config_dirs``).
    if host == "codex":
        override = os.environ.get("CODEX_HOME")
        default = Path.home() / ".codex"
        if override:
            candidate = Path(override)
            root = candidate if candidate.is_absolute() else Path.cwd() / candidate
        else:
            root = default
    else:
        root = claude_config_root(os.environ, Path.home(), Path.cwd())
    return root / "prompt-it-mode.json"


def _invalid_mode_file_error(path):
    return ValueError(
        f"{path} exists but could not be read as a valid mode file "
        "(for example, a dangling symlink, a non-regular file such as a "
        "FIFO, or an unreadable file); remove or repair it, then retry "
        "setup"
    )


def read_mode(path):
    if not os.path.lexists(path):
        return None
    # Open first, then classify the *opened descriptor* (`os.fstat`, not a
    # second `stat()`/`exists()` call against the path) so a symlink or
    # mount swapped in between a type check and the open cannot slip a FIFO
    # or other special file past the check -- there is no separate
    # check-then-open window. `O_NONBLOCK` (POSIX-only; absent on Windows,
    # where this whole class of special file does not arise the same way)
    # keeps a FIFO open from blocking forever waiting for a writer, so a
    # FIFO -- direct or via a symlink -- is caught below instead of hanging
    # `show`/`setup`/`set`.
    flags = os.O_RDONLY
    if hasattr(os, "O_NONBLOCK"):
        flags |= os.O_NONBLOCK
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise _invalid_mode_file_error(path) from exc
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise _invalid_mode_file_error(path)
        with os.fdopen(descriptor, "r", encoding="utf-8") as handle:
            descriptor = None  # ownership transferred; `with` closes it
            data = json.loads(handle.read())
    except OSError as exc:
        raise _invalid_mode_file_error(path) from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid Prompt it mode file") from exc
    finally:
        if descriptor is not None:
            os.close(descriptor)
    version = data.get("version") if isinstance(data, dict) else None
    if not isinstance(data, dict) or type(version) is not int or version != 1:
        raise ValueError("invalid Prompt it mode file")
    mode = data.get("mode")
    if not isinstance(mode, str) or mode not in MODES:
        raise ValueError("invalid Prompt it mode file")
    return mode


def write_mode(path, mode):
    """Replace the saved mode unconditionally (used by `set`)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=str(path.parent)
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(json.dumps({"version": 1, "mode": mode}) + "\n")
        os.chmod(temporary, 0o600)
        temporary.replace(path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def setup_mode(path, mode):
    """Create the mode file only if absent, atomically (used by `setup`).

    Two concurrent first-use `setup` calls can both observe no saved mode
    and race to publish a different choice. Publish the candidate through a
    fully-written temp file, then link (not rename) it into place so the
    file is never visible half-written and a second, concurrent `setup`
    either wins the link race or loses it outright -- there is no window
    where it can silently overwrite the winner's choice. The loser reads
    back and returns the winner's saved mode instead.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=str(path.parent)
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(json.dumps({"version": 1, "mode": mode}) + "\n")
        os.chmod(temporary, 0o600)
        try:
            os.link(str(temporary), str(path))
        except FileExistsError:
            winner = read_mode(path)
            if winner is None:
                raise _invalid_mode_file_error(path)
            return winner
        return mode
    finally:
        temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("show", "setup", "set"))
    parser.add_argument("--host", choices=("codex", "claude"), required=True)
    parser.add_argument("--mode", choices=sorted(MODES))
    args = parser.parse_args()
    try:
        path = config_path(args.host)
    except (OSError, ValueError, RuntimeError) as error:
        # ``config_path`` can reach ``Path.expanduser()`` (via a saved
        # settings declaration or the CLAUDE_CONFIG_DIR override), which
        # raises RuntimeError for an unresolvable ``~user`` form -- surface
        # it as the CLI's normal concise error instead of a raw traceback,
        # matching how ``set``/``show``/``setup`` already handle every
        # other expected failure below.
        parser.error(str(error))
    if args.command == "set":
        if not args.mode:
            parser.error("set requires --mode")
        try:
            write_mode(path, args.mode)
        except (OSError, ValueError) as error:
            # A settings-declared ``CLAUDE_CONFIG_DIR`` (or ``CODEX_HOME``)
            # containing an embedded NUL passes ``config_path()`` unchanged
            # (``Path()`` does not validate NUL bytes), but
            # ``path.parent.mkdir()`` here reaches the underlying OS call,
            # which rejects an embedded NUL with ``ValueError`` rather than
            # ``OSError`` -- catch both so `set` reports the same concise
            # error instead of a raw traceback, while still performing its
            # unconditional repair of a malformed saved mode file.
            parser.error(str(error))
        print(args.mode)
        return
    try:
        current = read_mode(path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        parser.error(str(error))
    if args.command == "show":
        print(current or "unset")
        return
    if current:
        print(current)
        return
    if args.mode:
        candidate = args.mode
    else:
        if not sys.stdin.isatty():
            parser.error("setup needs a terminal or --mode")
        print("Choose Prompt it mode: [1] Ask first  [2] Just go")
        try:
            answer = input("Mode [1/2]: ").strip()
        except EOFError:
            parser.error(
                "setup got no input on stdin (reached end of input before a "
                "choice was entered); rerun in a terminal or pass --mode"
            )
        if answer not in ("1", "2"):
            parser.error("choose 1 or 2")
        candidate = "ask-first" if answer == "1" else "just-go"
    try:
        winner = setup_mode(path, candidate)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        parser.error(str(error))
    print(winner)


if __name__ == "__main__":
    main()
