#!/usr/bin/env python3
"""Launch a cross-harness worker CLI with a scrubbed, confined environment.

This is the public Prompt it package's *own* self-contained launch surface
for the "Standalone direct-launch contract" in ``SKILL.md``: a coordinator
that wants to name a direct ``claude``/``codex``/``devin``/``gemini`` CLI
invocation as a ready cross-harness candidate must route the actual exec
through this helper, not a bare shell/subprocess call. A bare invocation
inherits every provider API key, backend-routing override, and startup
code-injection variable the coordinator's own shell happens to hold, and
runs wherever the coordinator's cwd happens to be — silently able to switch
a worker off its own already-authenticated session onto a billable key
route, redirect it to an unintended backend endpoint, run planted code
before the worker's own logic executes, or operate outside any isolated
worktree. None of that is "direct CLI invocation is safe" — it is exactly
the gap this helper closes.

This package is published standalone (no dependency on any private
Side Lane package, runner, or selector), so it does not reuse the private
local-side-lane repo's own launcher or its ``scripts/local_claude_settings.py``
module -- it reimplements the same class of guarantee, scoped to what a
standalone coordinator actually needs. It is deliberately narrower in one
respect: it never forwards a Claude OAuth token or any other coordinator
credential to the child at all (the private package's file-descriptor
forwarding machinery), so the child always relies on its own
already-authenticated CLI session. It is *not* narrower on settings
inspection, though: even with no credential forwarded, a saved
``ANTHROPIC_BASE_URL``, auth token/API key, custom header, or
``CLAUDE_CODE_USE_*`` backend selector in a claude child's effective
settings (managed, user, or project/local -- see "Claude saved-settings
inspection" below) would still redirect the child's *own* session to an
unintended endpoint, so every effective settings source is inspected and
an auth/routing override or an uninspectable source fails the launch
closed before the child ever runs.

What this helper guarantees before it execs the child:

- **Environment allowlist** -- the child's environment is built from
  scratch out of ``ALLOWED_ENV_EXACT``/``ALLOWED_ENV_LC_NAMES`` (home,
  locale/terminal presentation, each CLI's own config-directory pointer),
  not the inherited environment minus a denylist. Every provider API key
  and backend-routing override (``ANTHROPIC_*``, ``OPENAI_*``,
  ``AZURE_OPENAI_*``, ``GOOGLE_API_KEY``, ``GEMINI_*``, ``DEVIN_API_KEY``,
  and siblings), every unrelated coordinator credential a prefix denylist
  would otherwise miss by name (``GITHUB_TOKEN``, ``AWS_ACCESS_KEY_ID``,
  ``AZURE_CLIENT_SECRET``, ``SSH_AUTH_SOCK``, ...), a coordinator's own
  ``SIDE_LANE_CREDENTIAL_*``/``SIDE_LANE_CREDENTIALS_DIR``, and
  ``GOOGLE_APPLICATION_CREDENTIALS`` are all absent by construction, for
  every child. A Claude child also never sees ``CLAUDE_CODE_OAUTH_TOKEN``
  or the ``CLAUDE_CODE_USE_*`` backend selectors -- this helper never
  forwards them, so the child always runs on its own existing CLI session.
- **Startup-injection scrub** -- ``DYLD_*``/``LD_*`` dynamic-loader
  injection variables, Node's ``NODE_OPTIONS``/``NODE_PATH``, Python's
  ``PYTHONPATH``/``PYTHONHOME``, and the POSIX shell startup hooks
  ``BASH_ENV``/``ENV`` are all absent from the allowlisted child
  environment (none of them is an allowlisted name), so a planted loader,
  module, or shell-startup script cannot run inside the child.
- **Sanitized PATH and interpreter identity** -- the child's ``PATH`` is
  never forwarded verbatim; ``sanitize_path_env`` keeps only directories
  that pass the same ownership/write-bit trust walk as the resolved
  executable itself, so an attacker-writable directory prepended to the
  inherited ``PATH`` cannot substitute a planted binary for a bare CLI
  name. The same sanitized ``PATH`` is used to validate a script child's
  own shebang interpreter chain (``resolve_interpreter_chain``): a CLI
  whose entrypoint is, say, ``#!/usr/bin/env node`` is not safely launched
  merely because that script file is trusted -- the ``node`` (or ``bash``,
  ``python3``, ...) it names must itself resolve to a trusted executable,
  or the launch fails closed.
- **Trusted executable** -- the resolved child binary (and every canonical
  ancestor directory) must be owned by the current user or root with no
  group/world write bit, or the launch fails closed.
- **Resolved-executable provenance** -- ``argv[0]``'s basename (``claude``,
  ``codex``, ``devin``, ``gemini``) is caller-controlled and never by
  itself authorizes that CLI's policy. A trusted directory can still
  contain a symlink literally named e.g. ``claude`` pointing at an
  unrelated trusted binary -- ``/bin/sh`` passes ``is_trusted_executable``
  outright (a real, locked-down system file) and has no shebang to further
  validate, so without this check the caller's own argv (``-c <shell
  command>``) would run as a full shell under the guise of a ``claude``
  launch. ``verify_cli_provenance`` requires the resolved executable's own
  canonical path to match a known, hand-verified install layout for that
  CLI name (e.g. ``~/.local/share/claude/versions/<version>``, the macOS
  ``ChatGPT.app`` bundle's ``codex``, a ``gemini-cli`` npm install's
  ``node_modules/@google/gemini-cli/bundle/gemini.js``, or ``~/.local/
  share/devin/cli/_versions/<version>/bin/devin``) before any per-CLI
  policy applies; a resolved path this module does not recognize fails the
  launch closed rather than being trusted on name alone. A matching path
  *suffix* alone is not enough, though: a checkout-controlled file tree --
  something laid out inside the validated ``--worktree`` itself, or the
  shared main checkout -- can reproduce those same trailing path segments
  without being a genuine install at all, and ownership/write-bit checks
  do not catch this, since the same user legitimately owns their own
  worktree contents too. So the resolved path is first refused outright
  when it sits inside the validated worktree or the main checkout, and the
  match is then bound to an actual install *root* or package identity, not
  merely the suffix shape: ``claude``/``devin`` must resolve directly
  under the real OS user database's own home directory (``_real_home_dir``
  -- deliberately not the inherited, caller-controlled ``HOME``
  environment variable a coordinator's own shell could set to redirect
  this check), ``codex`` must resolve directly under the fixed system
  ``/Applications`` directory (``_codex_app_root``), and ``gemini`` --
  which has no single fixed install root across an nvm version dir,
  Homebrew, or a global npm prefix -- must instead carry a ``package.json``
  sibling of its own bundle directory that declares the genuine npm
  package identity ``@google/gemini-cli`` (``_gemini_package_identity_ok``).
- **Linked Git worktree confinement** -- ``--worktree`` must resolve to the
  root of a *linked* ``git worktree add`` lane, never the shared main
  checkout, a subdirectory, or an unrelated path; the check is bound to an
  allowlisted system ``git`` (PATH is never consulted) with repository-
  redirecting ``GIT_*`` variables scrubbed from the probe.
- **Root-expansion rejection** -- a ``codex`` child may not carry
  ``-C``/``--cd``/``--worktree`` (would move its working root outside the
  validated worktree), ``--add-dir`` (would grant an extra writable
  directory), ``-o``/``--output-last-message`` (writes the agent's final
  message to a caller-chosen path outside the worktree), or ``-c``/
  ``--config`` (an arbitrary config override that can grant the same thing
  under a different key, such as ``sandbox_workspace_write.writable_roots``
  or ``sandbox_mode="danger-full-access"``); a ``claude`` child may not
  carry ``--add-dir``, ``--settings`` (a caller-supplied settings source
  above the ones a direct CLI normally reads), or ``--mcp-config``/
  ``--plugin-dir``/``--plugin-url`` (each loads an additive MCP server
  registration or plugin -- including a local process command or a
  fetched remote plugin -- before the worker begins, bypassing the saved-
  settings and worktree checks this helper already ran, in both the
  space-separated and ``=``-joined forms verified against ``claude
  --help``); a ``gemini`` child may not carry its own ``-w``/``--worktree``
  (a different, gemini-managed worktree) or ``--include-directories``; a
  ``devin`` child may not carry ``--config`` (an arbitrary config file
  that can grant its own write permissions). This is a closed list of
  specific flags verified against each CLI's own ``--help`` output, not a
  proof that every other flag is safe -- it narrows the launch surface,
  it does not sandbox the child process itself, so a child's own
  shell/tool calls are still whatever that CLI's own execution mode
  allows outside this helper. ``claude``'s own ``--client-data-url`` was
  inspected too (per ``claude --help``, "URL for a signed configuration
  document") and deliberately left unrejected: it is Anthropic-signed and
  gates model availability rather than granting a working-root override,
  an unsandboxed startup code path, or a permission bypass, so it is not
  in the same class as the flags above.
- **Permission-bypass rejection** -- a ``claude`` child may not carry
  ``--dangerously-skip-permissions`` or ``--allow-dangerously-skip-
  permissions`` (both documented by ``claude --help`` as bypassing all
  permission checks, the latter only deferring that bypass to an
  in-session choice rather than removing the risk), rejected the same
  unconditional way as codex's own
  ``--dangerously-bypass-approvals-and-sandbox``/``--dangerously-bypass-
  hook-trust``.
- **Sandbox/permission-value rejection** -- a ``codex`` child's own
  ``-s``/``--sandbox`` flag selects its shell-command sandbox policy per
  ``codex exec --help`` (``read-only``, ``workspace-write``, or
  ``danger-full-access``); unlike the flags above, the flag itself is
  legitimate and not rejected outright, only the ``danger-full-access``
  value is, in every argv-parseable form (``-s danger-full-access``,
  ``-sdanger-full-access``, ``-s=danger-full-access``, ``--sandbox
  danger-full-access``, ``--sandbox=danger-full-access``) -- each verified
  to actually reach codex's own argument parser, not merely guessed at.
  ``read-only`` and ``workspace-write`` remain usable. The same by-value
  treatment applies to a ``claude`` child's ``--permission-mode``: every
  value is legitimate (``acceptEdits``, ``auto``, ``manual``, ``dontAsk``,
  ``plan``) except ``bypassPermissions``, which disables permission
  checks exactly like the flags above and is rejected in both the
  space-separated and ``=``-joined forms.
- **Closed CLI allowlist** -- only ``codex``, ``claude``, ``devin``, and
  ``gemini`` may be launched through this helper at all.
- **Host-support helper exposure** -- a ``codex`` child that spawns
  ``codex-code-mode-host`` as a sibling of its own real executable can miss
  it when ``codex`` was reached through a symlink elsewhere; the resolved
  executable's real parent directory is prepended to the child's ``PATH``
  once it is confirmed to hold that helper and the helper itself passes
  the same trust walk (see ``support_dir_for``). A distribution layout that
  genuinely has no such helper is untouched; a present-but-untrusted one
  fails the launch closed.
- **Claude saved-settings inspection** -- for a ``claude`` child, every
  effective settings source (managed, user, project/local -- including a
  linked worktree's main-checkout ``settings.local.json``) is read for an
  auth/routing ``env`` override, a startup-injection ``env`` override
  (``BASH_ENV``, ``ENV``, ``NODE_OPTIONS``, ``NODE_PATH``, ``PYTHONPATH``,
  ``PYTHONHOME``, ``LD_PRELOAD``, and the wider ``LD_*``/``DYLD_*``
  dynamic-loader families -- the same variables ``build_child_env`` already
  keeps out of the environment this helper forwards, checked here too since
  a settings ``env`` block applies inside the child's own session
  regardless of what was forwarded on the way in), or ``apiKeyHelper``; any
  override, or a declared ``CLAUDE_CONFIG_DIR`` location that cannot be
  inspected, fails the launch closed. Only file paths and key names are
  ever reported -- never values.
- **Claude startup-hook/MCP structural confinement** -- a ``claude`` child's
  argv always carries ``--safe-mode`` and ``--strict-mcp-config``,
  unconditionally appended after ``validate_child_argv`` has already run on
  the caller's own argv (see the "Claude startup-hook/MCP structural
  confinement" section above): together they confine every ``SessionStart``
  (and other) hook and every MCP server registration this helper cannot
  argv-police -- a settings file's own ``hooks`` block, ``~/.claude.json``'s
  global and per-project ``mcpServers``, and a worktree's own checked-in
  ``.mcp.json`` -- without failing closed on their mere presence, which
  would refuse every launch for an account (like a real developer's) that
  has ever saved an ordinary hook or MCP server. Neither flag has a
  negating counterpart on the installed ``claude --help``, so no argv a
  caller supplies can reintroduce one.
- **Codex effective-config preflight** -- for a ``codex`` child,
  ``$CODEX_HOME/config.toml`` (default ``~/.codex/config.toml``) and the
  *project-scoped* ``<worktree>/.codex/config.toml`` are never read or
  parsed at all; instead the launch refuses closed whenever either path
  could be loaded, based on existence alone. A hand-written partial TOML
  scanner previously read these files looking for specific dangerous keys
  (``sandbox_mode``, ``model_provider``, ``[mcp_servers.*]``, ...); an
  exact-head review found valid TOML encodings that slipped past its
  tracked-key checks, and that it never accounted for ``notify`` (an
  executable callback setting) at all -- any future Codex config key this
  module has not enumerated would create the same class of gap. This
  preflight closes that structurally rather than by enumerating more
  keys: it refuses on the mere presence of a config source, never on
  what that source contains. ``$CODEX_HOME/config.toml`` is skipped only
  when argv carries ``--ignore-user-config``, which codex itself also
  skips it for; the project-scoped file has no such exemption --
  ``--ignore-user-config`` is documented only as skipping the user file,
  never the project one. A ``-p``/``--profile`` flag on argv is refused
  outright: the profile it names selects a third file
  (``$CODEX_HOME/<name>.config.toml``) this preflight does not compute a
  path for or inspect either. Project config is, in this module's actual
  usage, always exactly the single file at the validated worktree's own
  root -- this helper's ``codex`` child never receives
  ``-C``/``--cd``/``--worktree``, so its cwd is always that worktree,
  itself already required to be its own Git toplevel by
  ``validate_linked_worktree``. A symlinked config file, or a symlinked
  ``.codex``/``$CODEX_HOME`` directory, an unreadable stat, or anything
  else that is not "confirmed absent all the way up its own parent
  directory" is treated exactly like a present regular file and refuses
  the launch, rather than being silently followed or skipped. Only file
  paths are ever reported in a refusal message -- the file is never
  opened, so there is nothing from its contents to leak. Codex CLI also
  exposes ``--dangerously-bypass-approvals-and-sandbox`` and
  ``--dangerously-bypass-hook-trust`` directly on argv; both are rejected
  the same way ``-c``/``--config`` already is. A top-level ``profile =
  "name"`` selector in ``config.toml`` is moot here since the file is
  never read at all -- and separately, Codex CLI (0.134.0+, verified
  against the installed 0.155.0-alpha.16.4) no longer honors that key
  regardless. This is a deliberately reduced-capability route: a real
  ``config.toml`` commonly carries a developer's own local MCP servers,
  model overrides, or other settings a normal interactive codex session
  would use, and none of that reaches a child launched through this
  helper -- a coordinator staffing a cross-harness codex candidate this
  way should mark those capabilities absent for that route and prefer a
  native same-harness path, or an installed Side Lane package's own
  launcher, when the task actually needs them.

This is an environment-and-confinement gate, not a route selector or
approval gate: it pins no model, reads no credential store, and makes no
model call itself. It changes no argv for ``codex``, ``devin``, or
``gemini``; a ``claude`` child is the sole, deliberate exception (see
"Claude startup-hook/MCP structural confinement" above) -- every other
caller-supplied token still reaches the child exactly as given. Served-model
verification, the completion receipt, and independent acceptance review
remain the coordinator's own responsibility under the "Standalone
direct-launch contract" in ``SKILL.md``. Standard library only.

Usage::

    python3 standalone_cli_launch.py --worktree <dir> -- <cli argv...>
"""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import shutil
import subprocess
import sys
from pathlib import Path


# The only worker CLIs this helper exists to launch. A closed allowlist
# means there is no arbitrary-CLI bypass around the trust/confinement
# checks below -- every child is a named worker whose resolved executable
# must still pass ``is_trusted_executable``.
WORKER_CLI_NAMES = frozenset({"codex", "claude", "devin", "gemini"})

# Non-secret runtime/session variables preserved for the child's own
# already-authenticated CLI session: locale/terminal presentation and each
# CLI's own config-directory pointer. This is an *allowlist*, not a
# denylist: an environment variable this list does not name is dropped by
# default rather than forwarded. A prefix denylist (the previous design)
# has to name every provider-key/credential family it knows about, and
# silently forwards anything it does not -- ``GITHUB_TOKEN``,
# ``AWS_ACCESS_KEY_ID``/``AWS_SECRET_ACCESS_KEY``, ``AZURE_CLIENT_SECRET``,
# ``SSH_AUTH_SOCK``, and any other coordinator credential an unlisted name
# happens to carry. An allowlist has the opposite failure mode -- a
# legitimate variable a CLI genuinely needs but this list has not yet
# learned about is dropped too -- which is the safe direction to fail in
# for a helper whose whole purpose is confinement.
#
# Matching is case-insensitive: Windows environment variable names are
# case-insensitive (``Path`` and ``PATH`` name the same variable), and
# folding case here costs nothing on a case-sensitive POSIX shell, where a
# name either matches one of these exact spellings or it does not.
# ``PATH`` itself is deliberately not in this set -- see ``build_child_env``
# and ``sanitize_path_env``: it is never forwarded verbatim, only as a
# sanitized value with untrusted directories removed.
ALLOWED_ENV_EXACT = frozenset(
    name.upper()
    for name in (
        # Home/identity: every CLI's own config discovery starts here.
        "HOME", "USERPROFILE", "USER", "LOGNAME", "USERNAME",
        # Terminal presentation only. SHELL is excluded: workers can use it
        # as the executable for shell tools, bypassing the PATH trust gate.
        "TERM", "COLORTERM", "TERM_PROGRAM", "TERM_PROGRAM_VERSION",
        "COLUMNS", "LINES",
        # Locale/timezone -- affects only formatting/messages.
        "LANG", "LANGUAGE", "TZ",
        # Temp-directory location, not a secret value.
        "TMPDIR", "TEMP", "TMP",
        # Each worker CLI's own config-directory pointer.
        "CODEX_HOME",
        "CLAUDE_CONFIG_DIR",
        # A non-secret project id a gemini/devin child's own SDK may read.
        "GOOGLE_CLOUD_PROJECT",
        # Windows system-DLL resolution a CLI's own runtime may need.
        "SYSTEMROOT", "WINDIR",
    )
)
# The standard POSIX ``LC_*`` locale category names. This is an *exact*
# set, not a prefix: a prefix match on ``LC_`` would also allow through
# any coordinator-chosen name that merely happens to start with it --
# ``LC_SECRET_TOKEN``, ``LC_API_KEY``, and the like -- which is exactly
# the kind of unbounded allowance the allowlist design (see
# ``ALLOWED_ENV_EXACT`` above) exists to avoid. Every genuine locale
# category is fixed and known in advance, so there is no reason to accept
# an unbounded ``LC_`` namespace here.
ALLOWED_ENV_LC_NAMES = frozenset(
    name.upper()
    for name in (
        "LC_ALL", "LC_COLLATE", "LC_CTYPE", "LC_MESSAGES", "LC_MONETARY",
        "LC_NUMERIC", "LC_TIME", "LC_PAPER", "LC_NAME", "LC_ADDRESS",
        "LC_TELEPHONE", "LC_MEASUREMENT", "LC_IDENTIFICATION",
    )
)

# Repository-redirecting Git variables removed from both the worktree
# validation probe and the child environment: an inherited ``GIT_DIR``
# would otherwise override ``-C`` and let an arbitrary directory pass as a
# linked worktree, and the same variables would redirect the child's own
# Git operations.
GIT_REDIRECT_EXACT = frozenset(
    {
        "GIT_DIR",
        "GIT_WORK_TREE",
        "GIT_COMMON_DIR",
        "GIT_INDEX_FILE",
        "GIT_OBJECT_DIRECTORY",
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
        "GIT_CEILING_DIRECTORIES",
        "GIT_DISCOVERY_ACROSS_FILESYSTEM",
        "GIT_NAMESPACE",
        "GIT_PREFIX",
        "GIT_EXEC_PATH",
        "GIT_SHALLOW_FILE",
        "GIT_QUARANTINE_PATH",
    }
)
GIT_REDIRECT_PREFIXES = ("GIT_CONFIG",)

# The exact OS/system Git locations the worktree-validation probe may bind.
# This is provenance, not preference: a user-owned ``~/bin/git`` passes
# ownership/mode checks too, so PATH order is never consulted -- only these
# fixed, package-manager/OS-owned locations are eligible.
SYSTEM_GIT_CANDIDATES = ("/usr/bin/git", "/bin/git")

# On macOS the allowlisted /usr/bin/git is an Xcode CLT shim. These
# inherited selectors can redirect that trusted shim to a caller-chosen
# toolchain's git while it proves a worktree, so they are removed only for
# the validation probe -- a child worker may still need them for its own
# builds. Mirrors ``local_git_probe.XCRUN_SELECT_EXACT``/``_PREFIXES``.
XCRUN_SELECT_EXACT = frozenset({"DEVELOPER_DIR", "TOOLCHAINS", "SDKROOT"})
XCRUN_SELECT_PREFIXES = ("XCRUN_",)


class LaunchError(RuntimeError):
    """A launch precondition failed; message is safe to print."""


def _owned_by_user_or_root(st):
    getuid = getattr(os, "getuid", None)
    return getuid is None or st.st_uid in (getuid(), 0)


def _is_macos_admin_dir(st):
    """``True`` for the standard macOS root:admin system layout.

    ``/Applications`` and similar system directories are root-owned,
    group ``admin``, and group-writable by design -- any member of the
    admin group can already administer the machine, so this is not an
    added trust exception in practice.
    """
    if sys.platform != "darwin":
        return False
    try:
        import grp
        return grp.getgrgid(st.st_gid).gr_name == "admin"
    except (ImportError, KeyError, OSError):
        return False


def _directory_is_locked_down(st):
    if not stat.S_ISDIR(st.st_mode):
        return False
    if st.st_mode & stat.S_IWOTH:
        return False
    if st.st_mode & stat.S_IWGRP and not _is_macos_admin_dir(st):
        return False
    return _owned_by_user_or_root(st)


def _directory_and_ancestors_locked_down(resolved):
    """``True`` if ``resolved`` and every canonical ancestor directory up
    to the filesystem root are locked down.

    Checking only ``resolved`` itself is not enough: an attacker who can
    write to an *ancestor* directory (but not ``resolved`` itself) can
    still rename/replace that ancestor -- or replant a symlink somewhere
    along the chain -- to swap out the directory a caller believes it
    validated. Mirrors the ancestor walk ``is_trusted_executable`` already
    does for a resolved executable file.
    """
    try:
        st = resolved.stat()
    except OSError:
        return False
    if not _directory_is_locked_down(st):
        return False
    for ancestor in resolved.parents:
        try:
            ast = ancestor.stat()
        except OSError:
            return False
        if not _directory_is_locked_down(ast):
            return False
    return True


def is_trusted_executable(resolved):
    """The file is a regular, executable, user/root-owned file with no
    group/world write bit, and every canonical ancestor directory is
    owned by the current user or root with no world write and no group
    write outside the macOS root:admin system layout."""
    resolved = Path(resolved)
    try:
        st = resolved.stat()
    except OSError:
        return False
    if not stat.S_ISREG(st.st_mode):
        return False
    if not os.access(resolved, os.X_OK):
        return False
    if st.st_mode & (stat.S_IWGRP | stat.S_IWOTH):
        return False
    if not _owned_by_user_or_root(st):
        return False
    for ancestor in resolved.parents:
        try:
            ast = ancestor.stat()
        except OSError:
            return False
        if not _directory_is_locked_down(ast):
            return False
    return True


# Helper binaries a host CLI spawns from its own real directory. codex-cli
# launches ``codex-code-mode-host`` as a sibling of the real ``codex``
# binary; when the CLI is reached through a symlink elsewhere (e.g.
# ``~/.local/bin/codex -> /Applications/ChatGPT.app/.../codex``) the
# sibling lookup fails, so the canonical parent is prepended to the child's
# ``PATH`` once. Mirrors ``scripts/local_native_launch.py``'s
# ``support_dir_for``/``with_support_dir``; nothing else is substituted.
HOST_SUPPORT_BINARIES = {"codex": ("codex-code-mode-host",)}


def support_dir_for(cli_name, executable):
    """Return ``executable``'s canonical parent when it holds trusted helpers.

    ``executable`` is already the resolved real path, so its parent is the
    real directory a symlinked invocation would otherwise hide from the
    child's own sibling lookup. Returns ``None`` when ``cli_name`` names no
    known helper, or the resolved executable's directory has none of them
    at all -- a distribution layout genuinely lacking that helper is not an
    error. A helper that *is* present but fails the same ownership/write-bit
    trust walk ``is_trusted_executable`` runs for the worker binary itself
    raises :class:`LaunchError`: a replaceable sibling (a group/world-
    writable ``codex-code-mode-host``, a dangling symlink, or a non-regular
    file) must never be silently skipped and left for the child to
    discover on its own, or exposed on the child's ``PATH``.
    """
    helpers = HOST_SUPPORT_BINARIES.get(cli_name, ())
    if executable is None or not helpers:
        return None
    real_dir = Path(executable).resolve().parent
    for name in helpers:
        helper = real_dir / name
        try:
            helper.lstat()
        except OSError:
            return None
        try:
            resolved_helper = helper.resolve()
        except OSError as exc:
            raise LaunchError(
                "{} host-support helper {} could not be resolved: {}".format(
                    cli_name, helper, exc
                )
            ) from exc
        if (
            not resolved_helper.is_file()
            or not os.access(resolved_helper, os.X_OK)
            or not is_trusted_executable(resolved_helper)
        ):
            raise LaunchError(
                "{} host-support helper {} exists but is not a trusted "
                "executable (owned by this user or root, no group/world "
                "write on the file or any ancestor directory outside the "
                "macOS root:admin system layout); refusing to launch".format(
                    cli_name, helper
                )
            )
    return str(real_dir)


def with_support_dir(env, support_dir):
    """Prepend ``support_dir`` to ``env["PATH"]`` exactly once; never reorder
    otherwise."""
    if not support_dir:
        return env
    entries = [entry for entry in env.get("PATH", "").split(os.pathsep) if entry]
    if entries[:1] != [support_dir]:
        env["PATH"] = os.pathsep.join(
            [support_dir] + [entry for entry in entries if entry != support_dir]
        )
    return env


_VERSION_LIKE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def _is_version_like(segment):
    return bool(_VERSION_LIKE.match(segment))


# Known, hand-verified install layouts, keyed by worker CLI name: the exact
# trailing path components a genuine install's resolved (symlink-followed)
# executable has, verified by hand against a real installed copy of each
# CLI (see ``verify_cli_provenance``). A callable entry matches any single
# path segment that looks like a version string; every other entry must
# match the literal segment exactly. This is a closed list of recognized
# distributions, not a claim that every legitimate install matches one --
# an install this module does not recognize fails closed rather than being
# trusted on argv0's name alone.
#
# Matching this suffix shape is necessary but not sufficient:
# ``verify_cli_provenance`` also binds the match to an actual install root
# or package identity (a checkout-controlled file tree can reproduce these
# same trailing segments without being a real install at all -- see the
# module docstring's "Resolved-executable provenance" section).
CLI_PROVENANCE_SUFFIXES = {
    # ``~/.local/share/claude/versions/<version>`` -- the version-named
    # binary itself; ``~/.local/bin/claude`` is a separate symlink to it.
    "claude": (
        (".local", "share", "claude", "versions", _is_version_like),
    ),
    # The macOS ChatGPT.app bundle's own codex binary.
    "codex": (
        ("ChatGPT.app", "Contents", "Resources", "codex"),
    ),
    # A gemini-cli npm install's bundled entrypoint script, wherever the
    # enclosing Node install root (an nvm version, Homebrew, a global npm
    # prefix, ...) happens to live.
    "gemini": (
        ("node_modules", "@google", "gemini-cli", "bundle", "gemini.js"),
    ),
    # ``~/.local/share/devin/cli/_versions/<version>/bin/devin``.
    "devin": (
        (
            ".local", "share", "devin", "cli", "_versions", _is_version_like,
            "bin", "devin",
        ),
    ),
}


def _path_tail_matches(parts, expected):
    """``True`` if the final ``len(expected)`` entries of ``parts`` match.

    Each entry in ``expected`` is either an exact path-segment string or a
    predicate for a variable segment (e.g. a version directory/file name).
    """
    if len(parts) < len(expected):
        return False
    tail = parts[-len(expected):]
    for actual, want in zip(tail, expected):
        if callable(want):
            if not want(actual):
                return False
        elif actual != want:
            return False
    return True


def _real_home_dir():
    """The OS user database's own home directory for the current user,
    independent of any caller-controlled ``HOME`` environment variable.

    ``verify_cli_provenance`` anchors ``claude``/``devin`` recognition to
    this directory. Deriving that anchor from an inherited ``HOME`` value
    instead would let a coordinator that controls its own environment (the
    same environment this helper's own inherited ``os.environ`` comes
    from, before ``build_child_env`` ever runs) redirect the anchor to an
    attacker-chosen directory tree that merely happens to end in the right
    path segments -- exactly the checkout-controlled bypass this binding
    exists to close. POSIX systems record the real home directory in the
    user database (``pwd``) independent of any environment variable; this
    reads it from there. Windows has no equivalent session-independent
    database reachable from the standard library, so on Windows this falls
    back to ``Path.home()`` -- this module (and this helper's ``codex``
    provenance root below) already documents itself as macOS-first. Test
    callers substitute a fixture directory by monkeypatching this function
    directly on the loaded module, never through an environment variable.
    """
    try:
        import pwd
        return Path(pwd.getpwuid(os.getuid()).pw_dir).resolve()
    except (ImportError, AttributeError, KeyError, OSError):
        return Path.home()


def _codex_app_root():
    """The fixed system directory a genuine macOS ``ChatGPT.app`` bundle
    installs under.

    Hardcoded to the one real, OS-owned location rather than derived from
    any caller-controlled environment variable or ``PATH`` lookup, so a
    checkout-controlled directory tree cannot redirect this anchor the way
    it could redirect an environment-derived one. Test callers substitute a
    fixture directory by monkeypatching this function directly on the
    loaded module.
    """
    return Path("/Applications")


def _gemini_package_identity_ok(parts):
    """``True`` if the resolved gemini path's own ``package.json`` (two
    directories up from the matched ``bundle/gemini.js`` suffix) declares
    the genuine npm package identity ``@google/gemini-cli``.

    ``gemini-cli`` has no single fixed install root -- an nvm version
    directory, a Homebrew prefix, and a global npm prefix are all
    legitimate -- unlike ``claude``/``devin`` (anchored to the real home
    directory) or ``codex`` (anchored to ``/Applications``), so path shape
    alone cannot be strengthened with a root anchor the same way for
    gemini. Reading the package's own declared name binds the match to
    package identity instead: a directory tree that merely mimics the
    ``node_modules/@google/gemini-cli/bundle/gemini.js`` shape without
    genuinely being that npm package's own install directory would also
    have to carry a ``package.json`` claiming that exact name.
    """
    if len(parts) < 2:
        return False
    package_json = Path(*parts[:-2]) / "package.json"
    try:
        if not package_json.is_file():
            return False
        data = json.loads(package_json.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeDecodeError):
        return False
    return isinstance(data, dict) and data.get("name") == "@google/gemini-cli"


def verify_cli_provenance(cli_name, resolved, *, worktree=None, main_checkout=None):
    """``True`` if ``resolved``'s own canonical path matches a known,
    hand-verified install layout for ``cli_name`` (see
    ``CLI_PROVENANCE_SUFFIXES``) *and* that layout is anchored to a real
    install root or package identity, not merely the path-suffix shape.

    ``cli_name`` is argv0's basename -- caller-controlled -- and must never
    by itself authorize a CLI's policy (allowlist membership, the flag
    policy in ``validate_child_argv``, the claude settings inspection): a
    trusted directory can still contain a symlink literally named e.g.
    ``claude`` pointing at an unrelated trusted binary such as ``/bin/sh``,
    which passes ``is_trusted_executable`` outright (a real, locked-down
    system file) and has no shebang of its own to further validate --
    without this check the caller's own argv (``-c <shell command>``)
    would run as a full shell under the guise of a ``claude`` launch. This
    binds the policy to the resolved executable's actual on-disk identity
    instead of the name it was invoked under.

    A matching path suffix is necessary but not sufficient: a checkout-
    controlled file tree (something an attacker can lay out inside the
    validated ``--worktree`` -- or, if named, the shared main checkout --
    itself, since a normal worktree checkout is user-owned and locked down
    exactly like a real install) can reproduce the same trailing path
    segments without being a genuine install at all, and the ownership/
    write-bit trust walk ``is_trusted_executable`` already ran does not
    catch this, since the same user legitimately owns their own worktree
    contents too. So ``resolved`` is refused outright when it sits inside
    ``worktree`` or ``main_checkout`` (either may be ``None`` -- a direct
    unit-test caller that has no worktree context to pass simply skips that
    exclusion), and the suffix match is then bound to an actual install
    root (``_real_home_dir`` for ``claude``/``devin``, ``_codex_app_root``
    for ``codex``) or package identity (``_gemini_package_identity_ok`` for
    ``gemini``, which has no single fixed root).
    """
    suffixes = CLI_PROVENANCE_SUFFIXES.get(cli_name)
    if not suffixes:
        return False
    resolved_path = Path(resolved).resolve()
    for boundary in (worktree, main_checkout):
        if boundary is None:
            continue
        try:
            boundary_path = Path(boundary).resolve()
        except OSError:
            continue
        if resolved_path == boundary_path or resolved_path.is_relative_to(boundary_path):
            return False
    parts = resolved_path.parts
    matched = next(
        (expected for expected in suffixes if _path_tail_matches(parts, expected)),
        None,
    )
    if matched is None:
        return False
    if cli_name == "gemini":
        return _gemini_package_identity_ok(parts)
    anchor_parts = parts[: -len(matched)]
    if not anchor_parts:
        return False
    if cli_name in ("claude", "devin"):
        return Path(*anchor_parts) == _real_home_dir()
    if cli_name == "codex":
        return Path(*anchor_parts) == _codex_app_root().resolve()
    return False


def scrub_repo_env(environ):
    """``environ`` minus every repository-redirecting Git variable."""
    return {
        name: value
        for name, value in environ.items()
        if name not in GIT_REDIRECT_EXACT
        and not name.startswith(GIT_REDIRECT_PREFIXES)
    }


def _scrub_probe_env(environ):
    scrubbed = {
        name: value
        for name, value in scrub_repo_env(environ).items()
        if name not in XCRUN_SELECT_EXACT
        and not name.startswith(XCRUN_SELECT_PREFIXES)
        and not name.startswith(("DYLD_", "LD_"))
    }
    scrubbed["GIT_CONFIG_GLOBAL"] = os.devnull
    scrubbed["GIT_CONFIG_SYSTEM"] = os.devnull
    scrubbed["GIT_CONFIG_NOSYSTEM"] = "1"
    return scrubbed


def trusted_git_executable(candidates=None):
    """The first allowlisted system Git that passes the trust walk, or
    ``None`` (fail closed) when none exists or passes."""
    for candidate in SYSTEM_GIT_CANDIDATES if candidates is None else candidates:
        try:
            resolved = Path(candidate).resolve()
        except OSError:
            continue
        if resolved.is_file() and os.access(resolved, os.X_OK) and is_trusted_executable(resolved):
            return resolved
    return None


def _run_git_probe(argv, environ, runner=subprocess.run):
    git_path = trusted_git_executable()
    if git_path is None:
        raise LaunchError(
            "no trusted git executable in the system allowlist ({}); "
            "refusing to validate the worktree".format(
                ", ".join(SYSTEM_GIT_CANDIDATES)
            )
        )
    return runner(
        ["git"] + list(argv),
        executable=str(git_path),
        env=_scrub_probe_env(environ),
        capture_output=True,
        text=True,
        check=False,
    )


def validate_linked_worktree(path, runner=subprocess.run, environ=None):
    """Require ``path`` to be the root of a *registered, linked* Git worktree.

    Returns ``(resolved, main_checkout)``: the resolved, canonical path, and
    the repository's main checkout root (``None`` when the main worktree is
    bare). Raises :class:`LaunchError` for anything else: a non-directory, a
    path outside any Git repository, the shared main checkout (which reports
    the same value for its Git directory and its common directory; a linked
    worktree's differs), or a directory that merely *looks* like a linked
    worktree -- e.g. a copied/cloned ``.git`` gitfile pointing at a real
    ``worktrees/<name>`` entry -- but is not itself registered in the
    repository's own ``git worktree list``. That registration check
    (``main_checkout_root``) runs for every launch, not only a ``claude``
    child, since an unregistered directory is not a genuine isolated lane
    for any worker.
    """
    resolved = Path(path).resolve()
    if not resolved.is_dir():
        raise LaunchError("worktree {} is not a directory".format(path))
    if environ is None:
        environ = os.environ
    try:
        completed = _run_git_probe(
            [
                "-C", str(resolved), "rev-parse", "--path-format=absolute",
                "--show-toplevel", "--absolute-git-dir", "--git-common-dir",
            ],
            environ,
            runner=runner,
        )
    except OSError as exc:
        raise LaunchError(
            "could not run git for worktree {}: {}".format(resolved, exc)
        ) from exc
    if completed.returncode != 0:
        raise LaunchError(
            "worktree {} is not inside a Git repository".format(resolved)
        )
    lines = completed.stdout.splitlines()
    if len(lines) < 3:
        raise LaunchError(
            "unexpected git rev-parse output for worktree {}".format(resolved)
        )
    toplevel, git_dir, common_dir = (Path(p.strip()).resolve() for p in lines[:3])
    if toplevel != resolved:
        raise LaunchError(
            "worktree {} is not the root of its Git worktree "
            "(toplevel is {})".format(resolved, toplevel)
        )
    if git_dir == common_dir:
        raise LaunchError(
            "worktree {} is a main checkout, not a linked Git worktree "
            "(git worktree add)".format(resolved)
        )
    # ``rev-parse`` alone proves ``resolved`` sits inside *some* Git
    # worktree with a distinct git-dir/common-dir -- not that this exact
    # directory is a real, registered entry rather than a copied/cloned
    # gitfile pointing at another worktree's metadata. ``main_checkout_root``
    # cross-checks the repository's own ``git worktree list`` and fails
    # closed when ``resolved`` is not registered there.
    main_checkout = main_checkout_root(resolved, runner=runner, environ=environ)
    return resolved, main_checkout


def _get_path_value(environ):
    """The inherited ``PATH`` value, matched case-insensitively.

    POSIX only ever sets ``PATH``; Windows environment names are
    case-insensitive, so a caller-provided mapping could carry ``Path``
    instead. Returns ``""`` when unset.
    """
    for name, value in environ.items():
        if name.upper() == "PATH":
            return value or ""
    return ""


def sanitize_path_env(raw_path):
    """A ``PATH`` value containing only directories that pass the same
    ownership/write-bit trust walk as a launched executable's ancestors.

    An inherited ``PATH`` may list a directory an attacker can write to
    ahead of a legitimate one -- e.g. a world-writable directory prepended
    by a compromised shell profile. Resolving a bare CLI name, or a bare
    interpreter name a script's shebang names (``env``, ``node``,
    ``python3``, ``bash``, ...), through such a ``PATH`` could silently
    substitute a planted binary even though the resolved script file
    itself is trusted. Each candidate directory is resolved and must
    itself -- and every canonical ancestor directory up to the filesystem
    root -- be owned by the current user or root with no group/world
    write bit (mirrors ``is_trusted_executable``'s ancestor walk); an
    untrusted ancestor is exactly as disqualifying as an untrusted leaf
    directory, since an attacker who can write to the ancestor can still
    replace or relink the directory itself. A nonexistent, non-directory,
    or untrusted entry is dropped rather than failing the whole ``PATH``,
    so unrelated cruft does not block a legitimate launch. Order is
    preserved (first match still wins) and duplicates are removed.
    """
    if not raw_path:
        return ""
    seen = set()
    kept = []
    for entry in raw_path.split(os.pathsep):
        if not entry:
            continue
        try:
            resolved = Path(entry).resolve()
        except OSError:
            continue
        if str(resolved) in seen:
            continue
        if not _directory_and_ancestors_locked_down(resolved):
            continue
        seen.add(str(resolved))
        kept.append(str(resolved))
    return os.pathsep.join(kept)


def build_child_env(inherited, *, cli_name=None):
    """Return a fresh child environment built from an explicit allowlist.

    Every inherited variable is dropped unless its name (folded to upper
    case) is in ``ALLOWED_ENV_EXACT`` or ``ALLOWED_ENV_LC_NAMES`` -- so a
    coordinator credential under a name this helper has never heard of
    (``GITHUB_TOKEN``, ``AWS_ACCESS_KEY_ID``, ``AZURE_CLIENT_SECRET``,
    ``SSH_AUTH_SOCK``, a provider key this list predates, ``LC_SECRET``-
    shaped name, ...) is scrubbed by default rather than needing its own
    denylist entry. ``PATH`` is never taken from this allowlist path: it
    is always replaced with ``sanitize_path_env``'s output, so a launch
    never forwards an inherited directory this helper has not itself
    judged trustworthy. ``cli_name`` is accepted for forward compatibility
    (a future CLI-specific safe variable) but every child currently gets
    the same allowlist.
    """
    kept = {
        name: value
        for name, value in inherited.items()
        if name.upper() in ALLOWED_ENV_EXACT
        or name.upper() in ALLOWED_ENV_LC_NAMES
    }
    kept["PATH"] = sanitize_path_env(_get_path_value(inherited))
    return scrub_repo_env(kept)


def resolve_executable(argv0, path_env, base=None):
    """Resolve the child program to a canonical filesystem path.

    A bare name is looked up on the *child's* ``PATH`` (already sanitized
    by ``sanitize_path_env`` for every caller in this module); an argv0
    containing a separator is resolved against ``base`` -- the validated
    worktree that becomes the child's cwd -- never the coordinator's own
    cwd. Returns ``None`` when nothing resolves.
    """
    if os.sep in argv0 or (os.altsep and os.altsep in argv0):
        candidate = Path(argv0)
        if not candidate.is_absolute():
            candidate = (Path(base) if base is not None else Path.cwd()) / candidate
        candidate = candidate.resolve()
        return candidate if candidate.is_file() else None
    found = shutil.which(argv0, path=path_env)
    return Path(found).resolve() if found else None


def _read_shebang_line(path):
    """The interpreter line of a ``#!``-script, or ``None`` for anything else.

    Reads only the first 512 bytes -- more than any real shebang line needs
    -- so this never has to load a large binary to conclude it is not a
    script.

    Raises :class:`LaunchError` when the header cannot be read at all
    (permission denied on an execute-only file, a race where the file
    vanished, an I/O error, ...): an unreadable header must never be
    treated the same as "no shebang line" -- that would silently skip
    ``resolve_interpreter_chain``'s own interpreter-chain validation for a
    file this process could not actually inspect, the same fail-open gap
    ``is_trusted_executable`` and the rest of this module exist to close.
    Returns ``None`` only when the header was read successfully and
    genuinely does not start with ``#!`` (a native binary, or anything else
    that is not a script).
    """
    try:
        with open(path, "rb") as handle:
            head = handle.read(512)
    except OSError as exc:
        raise LaunchError(
            "{} header could not be read: {}; refusing to launch".format(
                path, exc
            )
        ) from exc
    if not head.startswith(b"#!"):
        return None
    line = head.split(b"\n", 1)[0][2:]
    try:
        return line.decode("utf-8").strip()
    except UnicodeDecodeError:
        return None


_MAX_SHEBANG_CHAIN_DEPTH = 5


def resolve_interpreter_chain(executable, path_env, base=None, _depth=0):
    """Validate every interpreter a chain of ``#!`` shebangs would invoke.

    A trusted, executable *file* (``is_trusted_executable``) is not the
    whole story when it is a script: the kernel resolves the interpreter
    the shebang names -- directly, or indirectly through
    ``#!/usr/bin/env <name>`` -- and that resolution follows ``PATH``. A
    coordinator-controlled ``PATH`` could otherwise substitute a planted
    ``node``/``python3``/``bash`` ahead of the real one even though the
    script itself passed every ownership/write-bit check. Every interpreter
    in the chain (a shebang script can itself point at another script) must
    resolve, via ``path_env``, to a trusted executable, or the launch fails
    closed; a chain longer than ``_MAX_SHEBANG_CHAIN_DEPTH`` also fails
    closed rather than looping. Returns ``None`` for a non-script
    executable (nothing further to validate).
    """
    if _depth >= _MAX_SHEBANG_CHAIN_DEPTH:
        raise LaunchError(
            "{} has more than {} chained shebang interpreters; refusing "
            "to launch".format(executable, _MAX_SHEBANG_CHAIN_DEPTH)
        )
    shebang = _read_shebang_line(executable)
    if shebang is None:
        return None
    tokens = shebang.split()
    if not tokens:
        raise LaunchError(
            "{} has an empty shebang line; refusing to launch".format(executable)
        )
    first = tokens[0]
    if Path(first).name == "env":
        # ``first`` names the ``env`` program itself -- ``#!/usr/bin/env
        # node`` or an attacker-controlled ``#!/tmp/env node`` alike -- and
        # it is the kernel's actual entry point for this shebang: it runs
        # (and could act on the script) *before* ever looking up the
        # ``node``/``python3``/... name in its own argv. Validating only
        # that downstream name and skipping ``env`` itself would let a
        # planted ``/tmp/env`` (or a PATH-resolved impostor ``env``) run
        # unchecked, so it must resolve to a trusted executable exactly
        # like any other interpreter in the chain, before the interpreter
        # it names is even considered.
        env_program = resolve_executable(first, path_env, base=base)
        if env_program is None or not is_trusted_executable(env_program):
            raise LaunchError(
                "{} shebang env executable {!r} does not resolve to a "
                "trusted executable; refusing to launch".format(executable, first)
            )
        # ``env``'s own flags (``-i``, ``-S``, ``NAME=value``, ...) are not
        # the interpreter name; the first plain token after them is.
        rest = [tok for tok in tokens[1:] if "=" not in tok and not tok.startswith("-")]
        if not rest:
            raise LaunchError(
                "{} shebang '#!/usr/bin/env' names no interpreter; "
                "refusing to launch".format(executable)
            )
        interpreter_name = rest[0]
    else:
        interpreter_name = first
    interpreter = resolve_executable(interpreter_name, path_env, base=base)
    if interpreter is None or not is_trusted_executable(interpreter):
        raise LaunchError(
            "{} shebang interpreter {!r} does not resolve to a trusted "
            "executable; refusing to launch".format(executable, interpreter_name)
        )
    resolve_interpreter_chain(interpreter, path_env, base=base, _depth=_depth + 1)
    return interpreter


def _argv_has_flag(tokens, *, long_names=(), short_names=()):
    """``True`` if any of ``tokens`` invokes one of the named flags.

    Covers every shape a caller could use to smuggle the flag past a naive
    ``token in (...)`` check: the bare long form (``--add-dir``), the
    joined ``=`` form (``--add-dir=/tmp``), the bare short form (``-C``),
    and the joined short form clap also accepts with no separator
    (``-C/tmp``). A long flag never has a joined non-``=`` form (clap
    requires ``=`` there), so only short flags get the length-prefix check.
    """
    long_eq = tuple(name + "=" for name in long_names)
    for token in tokens:
        if token in long_names or token in short_names:
            return True
        if token.startswith(long_eq):
            return True
        if any(token.startswith(name) and len(token) > len(name) for name in short_names):
            return True
    return False


# Flags that would expand or relocate a child's writable/working root, or
# override its config with an arbitrary value that could do the same,
# keyed by the resolved CLI name. Verified against each CLI's own
# ``--help`` output; a flag only appears here once its exact spelling
# (including joined/``=``/short forms) has been confirmed against that
# output, not guessed. This is a closed list, not a general permission
# gate -- it exists solely to keep the validated ``--worktree`` the
# child's only writable/working root.
_ROOT_EXPANSION_FLAGS = {
    "codex": {
        # Root/working-directory overrides: would move the child's cwd or
        # session root away from the validated worktree.
        "long_names": ("--cd", "--worktree"),
        "short_names": ("-C",),
        # Directly grants an extra writable directory outside the
        # worktree, or (``-c``/``--config``) sets an arbitrary
        # ``key=value`` override -- including
        # ``sandbox_workspace_write.writable_roots`` or
        # ``sandbox_mode="danger-full-access"`` -- that grants the same
        # thing by another name. ``-o``/``--output-last-message`` writes
        # the agent's final message to a caller-chosen path with no
        # requirement that it sit inside the validated worktree.
        "extra_long_names": ("--add-dir", "--config", "--output-last-message"),
        "extra_short_names": ("-c", "-o"),
    },
    "claude": {
        # Grants tool access to directories outside the worktree.
        "extra_long_names": ("--add-dir",),
        # Adds a caller-supplied settings source above the ones a direct
        # CLI invocation normally reads.
        "extra_long_names_settings": ("--settings",),
        # Each loads an additive MCP server registration or plugin --
        # including a local process command (``--mcp-config``/
        # ``--plugin-dir``) or a fetched remote plugin (``--plugin-url``)
        # -- before the worker begins, running caller-controlled startup
        # code that the saved-settings and worktree checks above never
        # see. Verified against ``claude --help``: ``--mcp-config
        # <configs...>`` ("Load MCP servers from JSON files or strings"),
        # ``--plugin-dir <path>`` ("Load a plugin from a directory or .zip
        # for this session only"), ``--plugin-url <url>`` ("Fetch a plugin
        # .zip from a URL for this session only").
        "extra_long_names_startup": (
            "--mcp-config", "--plugin-dir", "--plugin-url",
        ),
    },
    "gemini": {
        # ``-w``/``--worktree`` runs the session in a *different*,
        # gemini-managed worktree, bypassing the validated one entirely;
        # ``--include-directories`` grants extra workspace directories
        # outside it.
        "long_names": ("--worktree", "--include-directories"),
        "short_names": ("-w",),
    },
    "devin": {
        # An arbitrary config file can grant its own ``Write(...)``/
        # permission rules outside the worktree.
        "extra_long_names": ("--config",),
    },
}

# Flags that disable a child's own permission/sandbox/approval confinement
# outright, independent of any working-root override -- neither category is
# a working-root override (the category ``_ROOT_EXPANSION_FLAGS`` covers),
# so each is checked separately: even a child confined to the validated
# ``--worktree`` with a scrubbed environment executes model-generated
# shell commands, or its own tool calls, completely unconfined if any of
# these reach argv.
#
# ``codex``'s pair is verified against ``codex exec --help`` (Codex CLI
# 0.155), which labels them "EXTREMELY DANGEROUS" and "DANGEROUS"
# respectively.
#
# ``claude``'s pair is verified against the installed ``claude --help``
# (2.1.283): ``--dangerously-skip-permissions`` ("Bypass all permission
# checks. Recommended only for sandboxes with no internet access.") and
# ``--allow-dangerously-skip-permissions`` ("Enable bypassing all
# permission checks as an option, without it being enabled by default.
# Recommended only for sandboxes with no internet access.") -- the latter
# does not itself skip a permission check the instant it is parsed, but it
# grants the child the ability to enable that same total bypass at its own
# discretion during the session, which is exactly the capability this
# helper exists to keep out of a launch it already validated, so it is
# rejected the same unconditional way as the flag it enables.
_SANDBOX_BYPASS_FLAGS = {
    "codex": (
        "--dangerously-bypass-approvals-and-sandbox",
        "--dangerously-bypass-hook-trust",
    ),
    "claude": (
        "--dangerously-skip-permissions",
        "--allow-dangerously-skip-permissions",
    ),
}

# ``-s``/``--sandbox <SANDBOX_MODE>`` per ``codex exec --help`` (Codex CLI
# 0.155): "Select the sandbox policy to use when executing model-generated
# shell commands" -- possible values ``read-only``, ``workspace-write``,
# ``danger-full-access``. Unlike ``_ROOT_EXPANSION_FLAGS`` and
# ``_SANDBOX_BYPASS_FLAGS``, the flag itself is not rejected outright: a
# caller legitimately needs to select ``read-only``/``workspace-write``, so
# only the ``danger-full-access`` value is dangerous -- it disables the
# sandbox for every model-generated shell command exactly like
# ``--dangerously-bypass-approvals-and-sandbox`` does -- and is checked by
# value, not by flag presence, across every argv-parseable form verified
# against the installed ``codex`` binary: the separate-token form
# (``-s danger-full-access`` / ``--sandbox danger-full-access``), the
# joined ``=`` form (``-s=danger-full-access`` /
# ``--sandbox=danger-full-access``), and the joined short form with no
# separator (``-sdanger-full-access``).
# ``claude``'s own ``--permission-mode <mode>`` per ``claude --help``
# (2.1.283): "Permission mode to use for the session" -- possible values
# ``acceptEdits``, ``auto``, ``bypassPermissions``, ``manual``,
# ``dontAsk``, ``plan``. Same by-value treatment as codex's ``--sandbox``:
# every value but ``bypassPermissions`` is legitimate, and only that value
# disables permission checks for the session exactly like
# ``--dangerously-skip-permissions`` does, so only it is rejected, in
# both the separate-token (``--permission-mode bypassPermissions``) and
# ``=``-joined (``--permission-mode=bypassPermissions``) forms; claude has
# no short form for this flag.
_SANDBOX_VALUE_FLAGS = {
    "codex": {
        "long_name": "--sandbox",
        "short_name": "-s",
        "dangerous_values": frozenset({"danger-full-access"}),
    },
    "claude": {
        "long_name": "--permission-mode",
        "short_name": None,
        "dangerous_values": frozenset({"bypassPermissions"}),
    },
}


def _flag_values(tokens, *, long_name=None, short_name=None):
    """Every value passed to a ``long_name``/``short_name`` option in
    ``tokens``, across the same argv-parseable forms ``_argv_has_flag``
    recognizes for a boolean flag: separate-token (``--flag value`` /
    ``-f value``), ``=``-joined (``--flag=value`` / ``-f=value``), and the
    short-joined form with no separator (``-fvalue``). Unlike
    ``_argv_has_flag`` this reports the value that follows the option, not
    merely whether the option occurred, since a value-taking flag can be
    safe for some values and dangerous for others (see
    ``_SANDBOX_VALUE_FLAGS``). A trailing occurrence with no following
    token contributes no value rather than raising.
    """
    values = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if long_name is not None:
            if token == long_name:
                if index + 1 < len(tokens):
                    values.append(tokens[index + 1])
                index += 2
                continue
            prefix = long_name + "="
            if token.startswith(prefix):
                values.append(token[len(prefix):])
                index += 1
                continue
        if short_name is not None:
            if token == short_name:
                if index + 1 < len(tokens):
                    values.append(tokens[index + 1])
                index += 2
                continue
            if token.startswith(short_name) and len(token) > len(short_name):
                rest = token[len(short_name):]
                if rest.startswith("="):
                    rest = rest[1:]
                values.append(rest)
                index += 1
                continue
        index += 1
    return values


def validate_child_argv(child_argv):
    """Reject child argv that would bypass the validated launch.

    Every rejected flag is one that could relocate a child's working root
    or grant it a writable/readable directory outside the validated
    ``--worktree`` -- directly (``-C``/``--cd``/``--worktree`` for
    ``codex``, its own ``--worktree``/``--include-directories`` for
    ``gemini``, ``--add-dir`` for ``codex``/``claude``) or indirectly, via
    an arbitrary config override that can set the same thing by another
    name (``-c``/``--config`` for ``codex``, ``--config`` for ``devin``).
    ``--settings`` is rejected for ``claude`` for the same reason: it adds
    a caller-supplied settings source above the ones a direct CLI
    invocation normally reads. ``-o``/``--output-last-message`` is rejected
    for ``codex`` for the same reason: it writes the agent's own final
    message to a caller-chosen path outside the validated worktree.
    ``_ROOT_EXPANSION_FLAGS`` is a closed list of specific, verified-
    dangerous flags per CLI, not an exhaustive proof that every other flag
    is safe -- an unlisted flag simply is not checked here, on the same
    "verify, do not guess" basis: only a flag whose exact spelling has been
    confirmed against that CLI's own ``--help`` output is listed at all.
    ``_SANDBOX_VALUE_FLAGS`` checks ``codex``'s own ``-s``/``--sandbox``
    and ``claude``'s own ``--permission-mode`` by *value* rather than
    presence: each flag is legitimate for its other values, but a
    ``danger-full-access``/``bypassPermissions`` value is rejected in
    every argv-parseable form, the same way
    ``--dangerously-bypass-approvals-and-sandbox``/
    ``--dangerously-skip-permissions`` already are. ``extra_long_names_
    startup`` rejects ``claude``'s own ``--mcp-config``/``--plugin-dir``/
    ``--plugin-url``: each loads an additive MCP server or plugin --
    including a local process command or a fetched remote plugin -- as
    caller-controlled startup code the saved-settings inspection below
    never sees.

    Both the ``--`` end-of-options scan restriction and the value-form
    coverage (separate-token, ``=``-joined, and -- where the CLI supports
    it -- the joined-short form) are verified against the installed
    child's own ``--help``/parsing behavior for both ``codex`` and
    ``claude``, not merely guessed at: ``codex exec -- --ignore-user-
    config`` and ``claude -p -- --dangerously-skip-permissions`` both hand
    the flag spelling to the child as plain prompt text, never as the
    actual option, so scanning tokens after a literal ``--`` for either
    CLI would misclassify a legitimate prompt as an attempted bypass.
    """
    cli_name = Path(child_argv[0]).name
    spec = _ROOT_EXPANSION_FLAGS.get(cli_name)
    if spec is None:
        return
    tokens = child_argv[1:]
    if cli_name in ("codex", "claude"):
        # Both treat every token after a literal ``--`` as positional
        # prompt text, never as a flag (verified above). Apply all argv
        # guards to the same option slice as codex_config_findings.
        tokens = _tokens_before_end_of_options(tokens)
    long_names = spec.get("long_names", ()) + spec.get("extra_long_names", ())
    short_names = spec.get("short_names", ()) + spec.get("extra_short_names", ())
    if _argv_has_flag(tokens, long_names=long_names, short_names=short_names):
        raise LaunchError(
            "{} argv may not set a working-root override or grant an "
            "extra writable/readable directory (including via a config "
            "override); the validated --worktree is already the child's "
            "only root".format(cli_name)
        )
    settings_names = spec.get("extra_long_names_settings", ())
    if settings_names and _argv_has_flag(tokens, long_names=settings_names):
        raise LaunchError(
            "claude argv may not supply --settings; caller settings "
            "could override the launch this helper validated"
        )
    startup_names = spec.get("extra_long_names_startup", ())
    if startup_names and _argv_has_flag(tokens, long_names=startup_names):
        raise LaunchError(
            "{} argv may not supply {}; each loads an additive MCP server "
            "or plugin registration -- including a local process command "
            "or a fetched remote plugin -- before the worker begins, "
            "bypassing the saved-settings and worktree checks this "
            "helper already ran".format(cli_name, "/".join(startup_names))
        )
    bypass_names = _SANDBOX_BYPASS_FLAGS.get(cli_name, ())
    if bypass_names and _argv_has_flag(tokens, long_names=bypass_names):
        raise LaunchError(
            "{} argv may not disable its own permission/sandbox/approval "
            "confinement ({})".format(cli_name, "/".join(bypass_names))
        )
    sandbox_spec = _SANDBOX_VALUE_FLAGS.get(cli_name)
    if sandbox_spec is not None:
        values = _flag_values(
            tokens,
            long_name=sandbox_spec["long_name"],
            short_name=sandbox_spec["short_name"],
        )
        if any(value in sandbox_spec["dangerous_values"] for value in values):
            flag_desc = sandbox_spec["long_name"]
            if sandbox_spec["short_name"]:
                flag_desc = "{}/{}".format(sandbox_spec["short_name"], flag_desc)
            raise LaunchError(
                "{} argv may not set {} to {}".format(
                    cli_name,
                    flag_desc,
                    "/".join(sorted(sandbox_spec["dangerous_values"])),
                )
            )


# ---------------------------------------------------------------------------
# Claude startup-hook/MCP structural confinement.
#
# The saved-settings inspection below (``claude_settings_findings``) fails a
# launch closed on an *auth/routing* override (``env``, ``apiKeyHelper``) --
# but it deliberately never scanned for a ``hooks`` key or an MCP server
# registration at all: those are not auth/routing overrides, they are
# arbitrary startup *commands* -- a ``SessionStart`` hook, or an MCP server
# entry naming a local process to spawn -- that Claude Code runs before this
# helper's caller ever sees a prompt, from sources this helper's argv
# validation never reaches: every effective settings file's own ``hooks``
# block, ``~/.claude.json``'s top-level ``mcpServers`` and its per-project
# ``projects.<path>.mcpServers``/``enabledMcpjsonServers``, and a linked
# worktree's own checked-in ``.mcp.json`` -- any of which a checkout-
# controlled branch (or a real developer's ordinary, legitimately-configured
# account) can carry.
#
# Failing closed on the mere *presence* of a ``hooks`` key or an MCP
# registration -- the same "refuse on existence" structure used for codex's
# ``config.toml`` above -- was tried and rejected: unlike a developer's
# ``~/.codex/config.toml`` (commonly absent), a real, ordinary account's own
# ``~/.claude/settings.json`` commonly carries its own legitimate ``hooks``
# block, and ``~/.claude.json`` commonly carries its own legitimate
# ``mcpServers`` registrations (verified against this module's own
# maintainer account) -- a blanket existence check would refuse every
# standalone Claude launch for such an account outright, which is not a
# "reduced capability" trade like the codex one, it is "this route never
# works" for any account that has ever run an interactive Claude Code
# session and saved a hook or an MCP server.
#
# Instead this confines the *child itself*, structurally, the same way the
# module already lets a codex child's own ``-s``/``--sandbox`` value or a
# claude child's own ``--permission-mode`` value pass through mostly intact
# and only refuses the one dangerous value: two of claude's own documented
# flags, verified against the installed ``claude --help`` (2.1.283), are
# unconditionally appended to a claude child's argv after
# ``validate_child_argv`` has already run on the caller's own argv --
#
# - ``--safe-mode`` -- "Start with all customizations (CLAUDE.md, skills,
#   installed plugins, hooks, MCP servers, custom commands and agents,
#   output styles, workflows, custom themes, keybindings, and more)
#   disabled ... Auth, model selection, built-in tools and plugins, and
#   permissions work normally." This is the "verified strict/isolated"
#   option this module prefers over a blanket refusal: hooks (from every
#   settings source) and MCP servers (from every registration source) are
#   both named explicitly as disabled, while the child's own existing
#   OAuth session, model access, and permission prompting are unaffected --
#   unlike ``--bare`` (also considered and rejected here), which forces
#   ``ANTHROPIC_API_KEY``/``apiKeyHelper``-only auth and would break this
#   route for any account (like this module's own maintainer's) that relies
#   on an existing OAuth login rather than an API key.
# - ``--strict-mcp-config`` -- "Only use MCP servers from --mcp-config,
#   ignoring all other MCP configurations" -- appended as a second,
#   independent guarantee against MCP registrations specifically. Its own
#   documented behavior carries no carve-out for managed/policy settings the
#   way ``--safe-mode``'s parenthetical ("Admin-managed (policy) settings
#   still apply") might be read to leave one for hooks; since this helper
#   never appends its own ``--mcp-config`` and ``validate_child_argv``
#   already rejects a caller-supplied one outright (see
#   ``extra_long_names_startup`` above), the effective MCP server set is
#   unconditionally empty regardless of source.
#
# Neither flag has a negating counterpart on the installed ``claude --help``
# (no ``--no-safe-mode``/``--unsafe``/equivalent for either), and both are
# appended after ``validate_child_argv`` -- which already rejects a caller
# ``--mcp-config``/``--plugin-dir``/``--plugin-url``/``--settings`` outright
# -- so no argv a caller supplies can reintroduce an MCP server or cancel
# either flag. Both are inserted immediately after ``child_argv[0]``, before
# any caller-supplied ``--`` end-of-options marker, so they are always
# parsed as the intended options rather than swallowed as positional prompt
# text (see ``validate_child_argv``'s own docstring on why a literal ``--``
# matters for claude argv parsing).
#
# This is a deliberate, narrow exception to this module's general
# "changes no argv" posture (see the module docstring): every other launch
# path still hands the caller's argv through unmodified. The trade is the
# same shape as the codex config preflight's: a claude child launched this
# way runs with its own skills, custom commands/agents, output styles,
# themes, and saved hooks/MCP servers all absent for the session -- a
# coordinator staffing a cross-harness claude candidate through this route
# should mark those capabilities absent for it and prefer a native
# same-harness path, or an installed Side Lane package's own launcher, when
# the task actually needs them.

CLAUDE_CONFINEMENT_FLAGS = ("--safe-mode", "--strict-mcp-config")


def ensure_claude_confinement_flags(child_argv):
    """Return ``child_argv`` with ``CLAUDE_CONFINEMENT_FLAGS`` inserted.

    Inserted immediately after ``child_argv[0]`` -- always before any
    caller-supplied ``--`` end-of-options marker, whatever the rest of the
    argv looks like -- so both flags are always parsed as options, never as
    positional prompt text.

    "Already present" is deliberately narrower than ``_argv_has_flag``'s
    general-purpose value-flag coverage: only an *exact* bare token
    (``--safe-mode``, ``--strict-mcp-config``), and only among the tokens
    before a literal ``--``, counts. Two reasons, both verified against the
    installed claude's own parsing rather than assumed:

    - A literal ``--`` ends option parsing for claude (see
      ``validate_child_argv``'s own docstring); every token after it is
      positional prompt text, never a flag. Scanning the full argv would
      let a prompt that happens to spell ``--safe-mode`` verbatim as its
      own positional text be misread as the caller already having supplied
      the flag, suppressing the real insertion and leaving the launch
      unconfined. ``_tokens_before_end_of_options`` -- the same helper
      ``validate_child_argv`` uses -- excludes that trailing slice here.
    - Neither flag takes a value on the installed claude: ``claude
      --safe-mode=false`` is rejected outright as ``error: unknown option
      '--safe-mode=false'`` (verified; claude refuses to start at all
      rather than starting unconfined), so an ``=``-joined token is not an
      alternate spelling of the real flag -- it is a different, invalid
      token that must not suppress inserting the genuine bare flag. Using
      a plain exact-token check instead of ``_argv_has_flag`` (which would
      treat the ``=``-joined form as a match via its general value-flag
      prefix check) keeps that token from being credited as "already
      confined". A caller cannot use this or any other argv shape to
      negate confinement: the two flags have no negating counterpart on
      claude's own ``--help``, and a bogus ``=value`` token alongside the
      real inserted flag still fails the child closed rather than running
      unconfined (verified above).

    A flag already present as an exact bare token is not duplicated;
    duplicate boolean flags are almost certainly harmless to claude's own
    parser, but an exact, minimal argv is easier to reason about and to
    test.
    """
    tokens = child_argv[1:]
    option_tokens = _tokens_before_end_of_options(tokens)
    to_insert = [
        flag for flag in CLAUDE_CONFINEMENT_FLAGS if flag not in option_tokens
    ]
    return [child_argv[0]] + to_insert + tokens


# ---------------------------------------------------------------------------
# Claude saved-settings inspection.
#
# ``apiKeyHelper`` and a settings ``env`` block apply above the inherited
# process environment for every Claude Code session, including one relying
# entirely on its own existing login -- this helper forwards no credential
# to any child, but a saved ``ANTHROPIC_BASE_URL``, auth token/API key,
# custom header, or ``CLAUDE_CODE_USE_*`` backend selector would still
# silently redirect the *child's own* already-authenticated session to an
# unintended endpoint. This package is published standalone (see module
# docstring), so it reimplements this inspection rather than importing the
# private local-side-lane repo's ``scripts/local_claude_settings.py`` --
# same threat model (documented precedence: managed settings, then a
# ``--settings`` payload -- rejected outright above --, then project/local,
# then user settings; ``CLAUDE_CONFIG_DIR`` relocates the user tier and is
# itself chased one settings-env hop; a linked worktree's project-local
# file is read at the main checkout's root), narrowed to what a
# standalone, self-contained coordinator needs. Only key names are ever
# returned -- never values -- so a stored credential or helper command
# cannot leak through a launch-refusal message.

MANAGED_SETTINGS_PATHS = (
    Path("/Library/Application Support/ClaudeCode/managed-settings.json"),
    Path("/etc/claude-code/managed-settings.json"),
)
USER_SETTINGS_FILENAMES = ("settings.json", "settings.local.json")

# Settings ``env`` keys that would redirect a claude child's own
# credential/backend -- mirrors ``CLAUDE_BLOCK_ENV_NAMES`` in the private
# local-side-lane launcher.
CLAUDE_BLOCK_ENV_NAMES = frozenset(
    {
        "ANTHROPIC_BASE_URL",
        "ANTHROPIC_AUTH_TOKEN",
        "ANTHROPIC_API_KEY",
        "ANTHROPIC_CUSTOM_HEADERS",
        "ANTHROPIC_VERTEX_PROJECT",
        "CLAUDE_CODE_OAUTH_TOKEN",
        "CLAUDE_CODE_OAUTH_REFRESH_TOKEN",
        "CLAUDE_CODE_OAUTH_SCOPES",
        "CLAUDE_CODE_OAUTH_TOKEN_FILE_DESCRIPTOR",
        "CLAUDE_CODE_API_KEY_FILE_DESCRIPTOR",
        "CLAUDE_CODE_GATEWAY_TOKEN_FILE_DESCRIPTOR",
        "CLAUDE_CODE_WEBSOCKET_AUTH_FILE_DESCRIPTOR",
        "CLAUDE_CODE_REMOTE",
        "CLAUDE_BG_AUTH_SNAPSHOT_PATH",
        "CLAUDE_CODE_SESSION_ACCESS_TOKEN",
        "CLAUDE_CODE_USE_BEDROCK",
        "CLAUDE_CODE_USE_VERTEX",
        "CLAUDE_CODE_USE_FOUNDRY",
        "CLAUDE_CODE_SUBAGENT_MODEL",
    }
)

# ``build_child_env``'s allowlist keeps these startup-injection variables out
# of the child's own process environment, but a saved settings ``env`` block
# applies *inside* Claude Code's own session (and reaches any subprocess
# Claude or its tools spawn) regardless of what this helper forwarded on the
# way in -- the same class of gap ``CLAUDE_BLOCK_ENV_NAMES`` already closes
# for auth/routing overrides. ``BASH_ENV``/``ENV`` run arbitrary shell
# startup code the moment any POSIX shell tool call starts; ``NODE_OPTIONS``/
# ``NODE_PATH`` and ``PYTHONPATH``/``PYTHONHOME`` can load an attacker
# module into any Node/Python child process; ``LD_PRELOAD`` and the wider
# ``LD_*``/``DYLD_*`` dynamic-loader families can inject a shared object into
# any dynamically linked executable the session or its tools launch. Checked
# at every effective settings tier (managed, user, project/local) exactly
# like ``CLAUDE_BLOCK_ENV_NAMES`` -- see ``claude_settings_findings``.
CLAUDE_BLOCK_STARTUP_ENV_NAMES = frozenset(
    {
        "BASH_ENV",
        "ENV",
        "NODE_OPTIONS",
        "NODE_PATH",
        "PYTHONPATH",
        "PYTHONHOME",
        "LD_PRELOAD",
    }
)
CLAUDE_BLOCK_STARTUP_ENV_PREFIXES = ("LD_", "DYLD_")
CLAUDE_BLOCK_TOP_LEVEL_KEYS = ("apiKeyHelper",)

# Checked only against ``MANAGED_SETTINGS_PATHS``, never against a project or
# user settings file -- see ``claude_settings_findings``. The installed
# ``claude --help`` documents ``--safe-mode`` as disabling "hooks" among
# other customizations, then immediately qualifies that with "Admin-managed
# (policy) settings still apply" (verified, ``claude --help``, 2.1.283): a
# ``hooks`` block saved in a project/user settings file is exactly the kind
# of customization ``--safe-mode`` does disable, so checking for it there
# too would refuse this route for any ordinary account that has one -- the
# same "refuse on mere presence" trade already rejected for those tiers in
# the "Claude startup-hook/MCP structural confinement" section above. A
# managed settings file's own ``hooks`` block is different: it is exactly
# the one hook source ``--safe-mode`` itself says still applies, so
# ``ensure_claude_confinement_flags``'s structural confinement does not
# reach it at all -- an executable startup command from that one surface
# would run regardless. This module cannot disable that hook (there is no
# claude flag for it), so it fails the launch closed instead.
CLAUDE_MANAGED_ONLY_BLOCK_TOP_LEVEL_KEYS = ("hooks",)


def _settings_env_value(path, name):
    """A settings file's ``env.<name>`` string value, or ``None``.

    Internal path-discovery aid only -- the value locates a further
    settings source and is never surfaced in a finding or error message.
    ``.strip()`` only decides blankness, matching
    ``scripts/local_claude_settings.py``'s ``_settings_env_value``: a
    nonblank value is returned exactly as declared, leading/trailing
    whitespace included, since that is the literal directory Claude Code
    itself resolves it against.
    """
    try:
        source = Path(path)
        if not stat.S_ISREG(source.stat().st_mode):
            return None
        data = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    env = data.get("env")
    if not isinstance(env, dict):
        return None
    value = env.get(name)
    if isinstance(value, str) and value.strip():
        return value
    return None


def _resolve_settings_config_dir(raw, base=None):
    """Resolve a declared ``CLAUDE_CONFIG_DIR`` value as the child sees it.

    ``~`` expands against the user's home; a relative value resolves from
    ``base`` -- the validated worktree that becomes the child's cwd, the
    directory Claude Code itself resolves it against.
    """
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = (Path(base) if base is not None else Path.cwd()) / path
    return path


def _resolve_home_dir(environ, home=None, base=None):
    """The child's own effective home directory.

    ``home`` is an explicit override, used verbatim, for callers (and
    tests) that already resolve their own home path. Otherwise this
    derives ``HOME`` from the *child's own* environment (``environ``) --
    the same environment view the caller is inspecting settings for --
    rather than this coordinator process's ``Path.home()``: the child does
    not necessarily share this process's home directory. A relative
    ``HOME`` value resolves against ``base`` -- the validated worktree that
    becomes the child's actual cwd, mirroring
    ``_resolve_settings_config_dir`` -- since that is the directory the
    child process itself would resolve a relative ``HOME`` from, not
    wherever this coordinator process happens to be running. Falls back to
    ``Path.home()`` only when ``environ`` carries no usable ``HOME`` at
    all.
    """
    if home is not None:
        return Path(home)
    raw = (environ or {}).get("HOME")
    if isinstance(raw, str) and raw != "":
        path = Path(raw)
        if not path.is_absolute():
            path = (Path(base) if base is not None else Path.cwd()) / path
        return path
    return Path.home()


def _inspectable_config_dir(path):
    """``True`` when ``path`` cannot hide settings: absent or a readable dir.

    A declared config directory that exists but is not a directory, or
    cannot be read, is uninspectable -- absence of an override cannot be
    proven, so the caller must fail closed.
    """
    try:
        st = path.stat()
    except FileNotFoundError:
        return True
    except (OSError, ValueError):
        return False
    if not stat.S_ISDIR(st.st_mode):
        return False
    return os.access(path, os.R_OK | os.X_OK)


def user_config_dirs(environ=None, home=None, base=None):
    """``(dirs, problems)`` -- effective Claude user config directories.

    ``CLAUDE_CONFIG_DIR`` relocates the entire ``~/.claude`` directory; the
    variable is also honored from a managed or user settings ``env`` block
    (one relocation hop), so a directory a settings file itself declares is
    scanned too. ``environ`` is the child's environment view -- also the
    source ``home`` is derived from (via ``_resolve_home_dir``) when
    ``home`` is not given explicitly, with a relative ``HOME`` anchored to
    ``base`` (the validated worktree that becomes the child's actual cwd)
    rather than this coordinator process's own cwd or real home directory.
    ``problems`` are ``(path, key)`` findings for a declared directory that
    cannot be inspected.
    """
    home_dir = _resolve_home_dir(environ, home=home, base=base)
    default_dir = home_dir / ".claude"
    env_raw = (environ or {}).get("CLAUDE_CONFIG_DIR")
    if isinstance(env_raw, str) and env_raw.strip():
        declared = [env_raw]
        dirs = []
    else:
        declared = []
        dirs = [default_dir]
        for path in (default_dir / name for name in USER_SETTINGS_FILENAMES):
            value = _settings_env_value(path, "CLAUDE_CONFIG_DIR")
            if value:
                declared.append(value)
    for path in MANAGED_SETTINGS_PATHS:
        value = _settings_env_value(path, "CLAUDE_CONFIG_DIR")
        if value:
            declared.append(value)
    problems = []
    unresolvable = False
    for raw in declared:
        try:
            directory = _resolve_settings_config_dir(raw, base=base)
        except (OSError, ValueError, RuntimeError, TypeError):
            unresolvable = True
            continue
        if directory not in dirs:
            dirs.append(directory)
    if unresolvable:
        problems.append(("CLAUDE_CONFIG_DIR", "<unresolvable config directory>"))
    for directory in dirs:
        if not _inspectable_config_dir(directory):
            problems.append((str(directory), "<uninspectable config directory>"))
    return dirs, problems


def project_settings_paths(worktree, main_checkout=None):
    """Project settings files for the directory the child runs in.

    ``main_checkout`` is the main checkout root when ``worktree`` is a
    linked worktree: Claude Code reads the project-local file
    (``.claude/settings.local.json``, gitignored) at the main checkout's
    root there rather than the fresh worktree's own ``.claude``.
    """
    root = Path(worktree)
    paths = [root / ".claude" / "settings.json", root / ".claude" / "settings.local.json"]
    if main_checkout is not None:
        local = Path(main_checkout) / ".claude" / "settings.local.json"
        if local not in paths:
            paths.append(local)
    return paths


def main_checkout_root(worktree, runner=subprocess.run, environ=None):
    """Main checkout root for a linked worktree, or ``None`` if bare.

    Raises :class:`LaunchError` when it cannot be determined -- a caller
    that is about to inspect settings for a claude launch must fail closed
    rather than skip the main checkout's project-local source. Identified
    through the trusted system git's own ``git worktree list --porcelain
    -z`` (see ``_run_git_probe``): NUL-terminated fields, so no quoting or
    whitespace ambiguity survives, and the requested worktree must itself
    appear as a registered non-bare entry.
    """
    try:
        resolved = Path(worktree).resolve()
    except OSError as exc:
        raise LaunchError("cannot resolve worktree {}: {}".format(worktree, exc)) from exc
    try:
        completed = _run_git_probe(
            ["-C", str(resolved), "worktree", "list", "--porcelain", "-z"],
            os.environ if environ is None else environ,
            runner=runner,
        )
    except OSError as exc:
        raise LaunchError(
            "could not list git worktrees for {}: {}".format(resolved, exc)
        ) from exc
    if completed.returncode != 0:
        raise LaunchError(
            "git worktree list failed for {}".format(resolved)
        )
    blocks = []
    block = None
    for field in completed.stdout.split("\0"):
        if not field:
            block = None
            continue
        if block is None:
            if not field.startswith("worktree ") or field == "worktree ":
                raise LaunchError(
                    "unexpected git worktree list output for {}".format(resolved)
                )
            block = []
            blocks.append(block)
        elif field.startswith("worktree "):
            raise LaunchError(
                "malformed git worktree list output for {}".format(resolved)
            )
        block.append(field)
    if not blocks:
        raise LaunchError("git worktree list named no worktree for {}".format(resolved))
    seen = set()
    registered = False
    main_root = None
    for index, listed in enumerate(blocks):
        try:
            resolved_listed = str(Path(listed[0][len("worktree "):]).resolve())
        except OSError as exc:
            raise LaunchError("cannot resolve listed worktree: {}".format(exc)) from exc
        if index == 0:
            main_root = Path(resolved_listed)
            if not main_root.exists():
                raise LaunchError("main worktree in git's listing is inaccessible")
        if resolved_listed in seen:
            raise LaunchError(
                "git worktree list reported {} more than once for {}".format(
                    listed[0][len("worktree "):], resolved
                )
            )
        seen.add(resolved_listed)
        if resolved_listed == str(resolved) and "bare" not in listed:
            registered = True
    if not registered:
        raise LaunchError(
            "worktree {} is not a registered non-bare git worktree".format(resolved)
        )
    main = blocks[0]
    if "bare" in main:
        return None
    return main_root


def find_settings_overrides(paths, *, env_names=(), env_prefixes=(), top_level_keys=()):
    """``(path, key)`` findings for saved overrides -- never values.

    A settings file that exists but cannot be read or parsed as an object
    is reported as ``<unreadable settings file>`` so the caller fails
    closed rather than assumes it is safe. The same applies to a settings
    path that exists (following any symlink) as anything *other than* a
    regular file -- a FIFO or device node could otherwise be loaded by
    Claude Code itself while this preflight silently ``continue``s past it
    and reports no finding at all. That check uses ``stat()`` (which
    reports the *target*'s type for a symlink) but never opens or reads a
    non-regular node -- reading a FIFO can block indefinitely, so this
    reports it as unreadable purely from its file type instead.
    """
    findings = []
    for path in paths:
        path = Path(path)
        try:
            if "\x00" in str(path):
                raise ValueError("NUL in settings path")
            st = path.stat()
        except (FileNotFoundError, NotADirectoryError):
            continue
        except (OSError, ValueError):
            findings.append((str(path), "<unreadable settings file>"))
            continue
        if not stat.S_ISREG(st.st_mode):
            findings.append((str(path), "<unreadable settings file>"))
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, UnicodeDecodeError):
            data = None
        if not isinstance(data, dict):
            findings.append((str(path), "<unreadable settings file>"))
            continue
        for key in top_level_keys:
            if key in data:
                findings.append((str(path), key))
        env = data.get("env")
        if isinstance(env, dict):
            for name in sorted(env):
                if name in env_names or any(
                    name.startswith(prefix) for prefix in env_prefixes
                ):
                    findings.append((str(path), "env." + name))
        elif "env" in data:
            findings.append((str(path), "<malformed env>"))
    return findings


def claude_settings_findings(worktree, environ=None, main_checkout=None):
    """``(findings, problems)`` for a claude child's saved settings.

    ``findings`` are ``(path, key)`` overrides that refuse the launch;
    ``problems`` are ``(path, key)`` entries for a declared
    ``CLAUDE_CONFIG_DIR`` location that cannot be inspected -- an
    unexamined config directory could hide one, so it fails closed too.

    Managed settings paths are checked against a wider key set than every
    other tier -- see ``CLAUDE_MANAGED_ONLY_BLOCK_TOP_LEVEL_KEYS`` -- since
    ``--safe-mode`` does not reach that one source. Every path, managed or
    not, still fails closed on being unreadable/non-regular/malformed JSON
    regardless of which keys are checked for (see
    ``find_settings_overrides``), so an uninspectable managed file is
    already refused independent of this split.
    """
    dirs, problems = user_config_dirs(environ=environ, base=worktree)
    other_paths = []
    for directory in dirs:
        other_paths += [directory / name for name in USER_SETTINGS_FILENAMES]
    other_paths += project_settings_paths(worktree, main_checkout=main_checkout)
    blocked_env_names = CLAUDE_BLOCK_ENV_NAMES | CLAUDE_BLOCK_STARTUP_ENV_NAMES
    findings = find_settings_overrides(
        list(MANAGED_SETTINGS_PATHS),
        env_names=blocked_env_names,
        env_prefixes=CLAUDE_BLOCK_STARTUP_ENV_PREFIXES,
        top_level_keys=CLAUDE_BLOCK_TOP_LEVEL_KEYS + CLAUDE_MANAGED_ONLY_BLOCK_TOP_LEVEL_KEYS,
    )
    findings += find_settings_overrides(
        other_paths,
        env_names=blocked_env_names,
        env_prefixes=CLAUDE_BLOCK_STARTUP_ENV_PREFIXES,
        top_level_keys=CLAUDE_BLOCK_TOP_LEVEL_KEYS,
    )
    return findings, problems


# ---------------------------------------------------------------------------
# Codex effective-config preflight.
#
# ``CODEX_HOME`` is forwarded to a codex child by name (see
# ``ALLOWED_ENV_EXACT``) because the CLI's own config/auth discovery starts
# there, but the module's earlier claim that argv restriction plus the
# environment allowlist fully confines a codex launch was wrong: a caller
# that controls ``CODEX_HOME`` (or the default ``~/.codex`` this helper never
# inspected) controls ``$CODEX_HOME/config.toml``, and codex reads
# ``sandbox_mode``, ``model_provider``, ``[mcp_servers.*]``, and other
# security-relevant settings from that file with no equivalent of
# ``-c``/``--config`` on argv to police -- rejecting ``-c``/``--config``
# (see ``_ROOT_EXPANSION_FLAGS``) narrows the argv surface but does nothing
# about a file argv never names.
#
# An earlier version of this preflight read and parsed ``config.toml`` with
# a narrow, hand-written scanner (no Python 3.9 stdlib TOML parser exists,
# and this package is standard-library-only) looking only for a fixed set
# of dangerous keys. An exact-head review found valid TOML encodings that
# reached those keys without the scanner recognizing the shape (defeating
# the tracked-key checks outright), and separately found the scanner never
# accounted for ``notify`` -- a top-level key that names an *executable*
# codex runs as a callback, exactly the class of saved, argv-invisible
# startup command this helper exists to keep out, and one this scanner's
# author had not enumerated. Any config key a future Codex release adds
# would create the same gap again: a denylist of known-dangerous keys is
# only ever as complete as its last review.
#
# This preflight replaces that approach structurally instead of adding more
# tracked keys: it never reads or parses ``config.toml`` content at all.
# A config source refuses the launch closed on its mere *existence* --
# see ``_codex_config_source_present`` -- regardless of what it contains.
# This is unconditionally more conservative than the old scanner (every
# input the old scanner would have refused is still refused; many it would
# have passed -- a config with only a harmless ``model = "..."`` line, or a
# remote MCP server -- are now refused too), and it is the deliberate
# trade: a real developer's ``~/.codex/config.toml`` commonly carries their
# own local MCP servers, model overrides, or other settings a normal
# interactive session would use, and none of that reaches a child launched
# through this helper. A coordinator staffing a cross-harness codex
# candidate through this route should mark those capabilities absent for
# it and prefer a native same-harness path, or an installed Side Lane
# package's own launcher, when the task actually needs them.
#
# Verified against ``codex exec --help`` (Codex CLI 0.155):
#
# - ``--ignore-user-config`` "does not load ``$CODEX_HOME/config.toml``" --
#   codex itself never reads it, so this preflight does not either.
#   Nothing in that documentation states it also skips the *project-scoped*
#   ``<worktree>/.codex/config.toml`` (verified against the OpenAI Codex
#   docs' config reference/advanced pages,
#   https://developers.openai.com/codex/config-advanced and
#   .../config-reference, current as of this module's writing), so the
#   project file is refused on existence unconditionally -- with or
#   without ``--ignore-user-config`` on argv.
# - ``-p``/``--profile <NAME>`` "layers ``$CODEX_HOME/<name>.config.toml``
#   on top of the base user config" -- a third config source. Computing
#   whether that specific file happens to exist would only reintroduce a
#   narrower version of the same class of gap (a path-construction detail
#   this module could get wrong for a future codex release), so the flag
#   itself is refused outright instead: naming a profile at all is refused,
#   independent of whether the file exists.
#
# Project config is, in this module's actual usage, always exactly the
# single file at the validated worktree's own root: this helper's ``codex``
# child never receives ``-C``/``--cd``/``--worktree``
# (``_ROOT_EXPANSION_FLAGS`` rejects all three), so its cwd is always the
# validated ``--worktree`` -- and ``validate_linked_worktree`` already
# requires that worktree to be its own Git toplevel. Codex's own project
# config walk (every ``.codex/config.toml`` from a project's Git toplevel
# down to its cwd) therefore collapses to exactly this one file, with no
# ancestor directory to visit.
#
# The top-level ``profile = "name"`` config-file selector (a separate,
# older mechanism from ``--profile`` on argv) is moot here since the file
# it would appear in is never read at all -- and separately, verified
# against the installed Codex CLI (0.155.0-alpha.16.4) and the same config
# docs, that selector "is no longer supported" as of Codex 0.134.0.


def _codex_home_dir(environ, base=None):
    """The effective ``$CODEX_HOME`` a codex child resolves config from.

    A relative ``CODEX_HOME`` resolves against ``base`` -- the validated
    worktree that becomes the child's cwd. Codex treats ``~`` literally in
    this environment value, so this deliberately does not call the Claude
    settings resolver, which expands it. Falls back
    to ``~/.codex`` under the child's own ``HOME`` (or this process's, if
    unset) when ``CODEX_HOME`` is not set, matching codex's own default.

    Codex's own resolution (``os.environ.get("CODEX_HOME") or default``)
    treats only the empty string as unset -- a whitespace-only value is
    truthy and used verbatim, unlike Claude Code's ``CLAUDE_CONFIG_DIR``
    (see ``mode.py``'s ``_prompt_it_mode_path``). So this checks non-empty,
    not ``.strip()``-truthy, or a whitespace-only override would be silently
    dropped in favor of scanning ``~/.codex``, missing a config source
    codex itself would load from the literal whitespace path.

    The ``~/.codex`` fallback itself is derived from the child's own
    ``HOME`` (via ``_resolve_home_dir``), with a relative ``HOME`` anchored
    to ``base`` -- the validated worktree that becomes the child's actual
    cwd -- rather than this coordinator process's own cwd or real home
    directory.
    """
    raw = (environ or {}).get("CODEX_HOME")
    if isinstance(raw, str) and raw != "":
        path = Path(raw)
        if not path.is_absolute():
            path = (Path(base) if base is not None else Path.cwd()) / path
        return path
    return _resolve_home_dir(environ, base=base) / ".codex"


def project_codex_config_path(worktree):
    """The single project-scoped ``.codex/config.toml`` this launch can load.

    Codex discovers project config by walking every ``.codex/config.toml``
    from a project's own Git toplevel down to its cwd (see the "Codex
    effective-config preflight" section above). This helper's ``codex``
    child never receives ``-C``/``--cd``/``--worktree``, so its cwd is
    always the validated ``worktree`` -- itself already required by
    ``validate_linked_worktree`` to be its own Git toplevel -- collapsing
    that walk to exactly this one file; there is deliberately no ancestor
    directory walk here.
    """
    return Path(worktree) / ".codex" / "config.toml"


def _codex_config_source_present(path):
    """``True`` unless ``path`` is confirmed absent, without ever opening it.

    "Confirmed absent" requires both ``path`` itself and its parent
    directory to plainly not exist (or, for the parent, to exist as an
    ordinary, non-symlink directory with ``path`` itself absent under it).
    Anything else -- a regular file, a symlinked config file, a symlinked
    ``.codex``/``$CODEX_HOME`` directory, or a path this process cannot
    stat at all -- is treated exactly like a present regular file: this
    preflight refuses to read through a symlink to decide whether the
    *target* is dangerous, so it fails closed on the mere possibility
    instead. ``lstat`` (never ``stat``) is used throughout so a symlink is
    identified as itself present rather than silently followed.
    """
    parent = path.parent
    try:
        parent_st = parent.lstat()
    except FileNotFoundError:
        return False
    except OSError:
        return True
    if stat.S_ISLNK(parent_st.st_mode):
        return True
    if not stat.S_ISDIR(parent_st.st_mode):
        return False
    try:
        path.lstat()
    except FileNotFoundError:
        return False
    except OSError:
        return True
    return True


def _tokens_before_end_of_options(tokens):
    """``tokens`` truncated at the first literal ``--`` marker, if any.

    Codex's own argument parser (like every clap-based CLI) treats a bare
    ``--`` as ending option parsing: every token after it is positional --
    prompt text for ``codex exec``, not a flag -- even when it happens to
    spell one out verbatim, e.g. ``codex exec -- --ignore-user-config``.
    Scanning every token unconditionally would let prompt text disable this
    preflight's own user-config check, or wrongly trigger the ``--profile``
    refusal, for something codex itself will never treat as that flag.
    """
    if "--" in tokens:
        return tokens[: tokens.index("--")]
    return tokens


def codex_config_findings(worktree, child_argv, environ=None):
    """``(path, reason)`` refusals for a codex child's config sources.

    Never reads or parses any config file's content -- see the module-level
    "Codex effective-config preflight" note above for why. Checks, in
    order:

    - ``$CODEX_HOME/config.toml`` -- refused when present, unless child
      argv carries ``--ignore-user-config`` (the one flag codex itself
      documents as skipping that file).
    - ``<worktree>/.codex/config.toml`` (see ``project_codex_config_path``)
      -- refused when present, regardless of ``--ignore-user-config``.
    - ``-p``/``--profile`` on argv, in every form ``_argv_has_flag``
      recognizes -- refused outright, independent of whether the file it
      would select exists.

    Both flag scans are restricted to the tokens before the first literal
    ``--`` end-of-options marker (see ``_tokens_before_end_of_options``):
    anything after it is positional prompt text to the child CLI, not a
    flag, even if it spells one out verbatim.

    An empty return means every checked source is confirmed absent and no
    profile was requested; the caller should treat that as safe to launch.
    """
    findings = []
    codex_home = _codex_home_dir(environ, base=worktree)
    option_tokens = _tokens_before_end_of_options(child_argv[1:])
    ignore_user_config = _argv_has_flag(
        option_tokens, long_names=("--ignore-user-config",)
    )
    if not ignore_user_config:
        user_config = codex_home / "config.toml"
        if _codex_config_source_present(user_config):
            findings.append((str(user_config), "user config present"))
    project_config = project_codex_config_path(worktree)
    if _codex_config_source_present(project_config):
        findings.append((str(project_config), "project config present"))
    if _argv_has_flag(
        option_tokens, long_names=("--profile",), short_names=("-p",)
    ):
        findings.append(
            ("argv", "-p/--profile selects a separate, uninspected config source")
        )
    return findings


def main(argv=None, runner=subprocess.run):
    parser = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--worktree",
        required=True,
        help="linked Git worktree the worker runs in (becomes the child's cwd)",
    )
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="worker CLI argv, verbatim; prefix with -- to separate",
    )
    args = parser.parse_args(argv)

    child_argv = list(args.command)
    if child_argv[:1] == ["--"]:
        child_argv = child_argv[1:]

    try:
        inherited = dict(os.environ)
        worktree, main_checkout = validate_linked_worktree(
            args.worktree, runner=runner, environ=inherited
        )
        if not child_argv:
            raise LaunchError("no worker CLI argv given after --")
        validate_child_argv(child_argv)
        cli_name = Path(child_argv[0]).name
        if cli_name not in WORKER_CLI_NAMES:
            raise LaunchError(
                "only the known worker CLIs may launch through this "
                "helper ({}); got {!r}".format(
                    ", ".join(sorted(WORKER_CLI_NAMES)), child_argv[0]
                )
            )
        env = build_child_env(inherited, cli_name=cli_name)
        executable = resolve_executable(
            child_argv[0], env.get("PATH", ""), base=worktree
        )
        if executable is None or not is_trusted_executable(executable):
            raise LaunchError(
                "{} does not resolve to a trusted executable (owned by "
                "this user or root, no group/world write on the file or "
                "any ancestor directory outside the macOS root:admin "
                "system layout); refusing to launch".format(child_argv[0])
            )
        if not verify_cli_provenance(
            cli_name, executable, worktree=worktree, main_checkout=main_checkout
        ):
            raise LaunchError(
                "{} resolves to {}, which does not match a recognized {} "
                "install layout; refusing to launch (a PATH entry or "
                "symlink may be substituting an unrelated trusted "
                "executable)".format(child_argv[0], executable, cli_name)
            )
        # codex-cli spawns ``codex-code-mode-host`` as a sibling of its own
        # real executable; when ``codex`` is reached through a symlink
        # elsewhere, that sibling lookup fails unless the canonical real
        # directory is exposed on the child's ``PATH`` -- see
        # ``support_dir_for``. A present-but-untrusted helper fails the
        # launch closed rather than being silently skipped.
        support_dir = support_dir_for(cli_name, executable)
        env = with_support_dir(env, support_dir)
        # A trusted *file* is not the whole story when it is a script: the
        # shebang interpreter it names (directly, or via
        # ``#!/usr/bin/env <name>``) is resolved through the same sanitized
        # ``PATH`` and must itself be trusted, or the launch fails closed --
        # see ``resolve_interpreter_chain``.
        resolve_interpreter_chain(executable, env.get("PATH", ""), base=worktree)
        if cli_name == "claude":
            # Saved settings apply above the inherited (already scrubbed)
            # environment for every Claude session, forwarded credential or
            # not, so this fails closed on an auth/routing override or an
            # uninspectable source before the child ever runs -- see the
            # "Claude saved-settings inspection" section above. The main
            # checkout was already identified by ``validate_linked_worktree``
            # (its registration check runs for every CLI); reused here
            # rather than probed a second time.
            findings, settings_problems = claude_settings_findings(
                worktree, environ=env, main_checkout=main_checkout
            )
            if findings or settings_problems:
                raise LaunchError(
                    "saved Claude settings carry an auth/routing override "
                    "or an uninspectable source; resolve these before "
                    "launch (values not shown): " + "; ".join(
                        "{}: {}".format(path, key)
                        for path, key in (findings + settings_problems)
                    )
                )
            # Neither the settings scan above nor ``validate_child_argv``
            # covers a ``hooks`` block or an MCP server registration --
            # see the "Claude startup-hook/MCP structural confinement"
            # section above for why those are refused structurally, via
            # claude's own ``--safe-mode``/``--strict-mcp-config``, rather
            # than by failing closed on their mere presence.
            child_argv = ensure_claude_confinement_flags(child_argv)
        elif cli_name == "codex":
            # $CODEX_HOME/config.toml, a project-scoped
            # <worktree>/.codex/config.toml, and a ``-p``/``--profile``-
            # selected layered file are all real config sources this helper
            # never argv-polices, so this refuses closed whenever any of
            # them could be loaded at all, before the child ever runs --
            # see the "Codex effective-config preflight" section above.
            # This is existence-only: the config file itself is never
            # opened, so there is no content to leak.
            findings = codex_config_findings(worktree, child_argv, environ=env)
            if findings:
                raise LaunchError(
                    "a Codex config source could be loaded by this launch "
                    "(user config, project config, or a --profile "
                    "selection); this preflight refuses on existence alone "
                    "rather than reading file contents: " + "; ".join(
                        "{}: {}".format(path, reason)
                        for path, reason in findings
                    )
                )
    except LaunchError as exc:
        print("standalone_cli_launch: error: {}".format(exc), file=sys.stderr)
        return 2

    try:
        completed = runner(
            child_argv,
            cwd=str(worktree),
            env=env,
            executable=str(executable),
        )
    except OSError as exc:
        print(
            "standalone_cli_launch: error: could not start {}: {}".format(
                child_argv[0], exc
            ),
            file=sys.stderr,
        )
        return 2
    return int(completed.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
