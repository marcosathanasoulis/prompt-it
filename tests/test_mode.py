"""Offline checks for the local, per-harness Prompt it mode choice."""

import importlib.util
import json
import os
import shutil
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "plugins/prompt-it/skills/prompt-it/scripts/mode.py"


def _isolated_bootstrap(script_path, managed_settings_paths=()):
    """Source for a ``python -c`` bootstrap that loads mode.py and replaces
    ``claude_config_root``'s ``managed_paths`` default before dispatching
    to ``main()``, instead of running the script directly.

    Every test in this file spawns mode.py as a real subprocess. Run
    directly, ``config_path()`` calls ``claude_config_root(os.environ,
    Path.home(), Path.cwd())`` with no ``managed_paths`` argument, so it
    resolves through that parameter's *default* value -- the real, fixed
    ``/Library/Application Support/ClaudeCode/managed-settings.json`` and
    ``/etc/claude-code/managed-settings.json`` -- which no test env
    override (HOME, CLAUDE_CONFIG_DIR, etc.) touches. On a managed
    workstation where either file declares a ``CLAUDE_CONFIG_DIR``, that
    real file would outrank every env override these tests set up,
    silently redirecting `setup`/`show`/`set` to the developer's actual
    managed-declared config directory instead of the intended isolated
    temp directory.

    Reassigning the module-level ``MANAGED_SETTINGS_PATHS`` name after
    import does *not* work: a parameter default (``managed_paths=
    MANAGED_SETTINGS_PATHS`` in mode.py's function signature) is bound
    once, at function-definition time, into the function object's
    ``__defaults__`` -- it does not re-read the module global on each
    call. So this bootstrap patches ``claude_config_root.__defaults__``
    directly instead. That keeps production precedence and argv parsing
    completely unchanged; only this test harness's subprocess launch path
    is different, and no user-facing CLI override is added.
    """
    literal_paths = ", ".join(repr(str(path)) for path in managed_settings_paths)
    if literal_paths:
        literal_paths += ","
    return (
        "import importlib.util\n"
        f"spec = importlib.util.spec_from_file_location('prompt_it_mode', {str(script_path)!r})\n"
        "module = importlib.util.module_from_spec(spec)\n"
        "spec.loader.exec_module(module)\n"
        f"module.claude_config_root.__defaults__ = (({literal_paths}),)\n"
        "module.main()\n"
    )


def _isolated_bootstrap_stubbing_tty_eof(script_path, managed_settings_paths=()):
    """Like ``_isolated_bootstrap``, but also replaces ``sys.stdin`` with a
    stub whose ``isatty()`` returns ``True`` and monkeypatches the builtin
    ``input`` to raise ``EOFError``, then dispatches to ``main()``.

    This exercises mode.py's "tty present, but input hit EOF before a
    choice was typed" branch deterministically, without depending on a
    real pty's platform-specific ``isatty()`` behavior after its master
    side is closed (that behavior is not portable: it differs between
    macOS and Linux, and the ``pty`` module does not exist on Windows at
    all). The subprocess's real stdin is irrelevant here since both the
    tty check and the read are stubbed before ``main()`` runs.
    """
    literal_paths = ", ".join(repr(str(path)) for path in managed_settings_paths)
    if literal_paths:
        literal_paths += ","
    return (
        "import builtins, io\n"
        "import importlib.util\n"
        f"spec = importlib.util.spec_from_file_location('prompt_it_mode', {str(script_path)!r})\n"
        "module = importlib.util.module_from_spec(spec)\n"
        "spec.loader.exec_module(module)\n"
        f"module.claude_config_root.__defaults__ = (({literal_paths}),)\n"
        "class _TTYStdin(io.StringIO):\n"
        "    def isatty(self):\n"
        "        return True\n"
        "module.sys.stdin = _TTYStdin()\n"
        "def _raise_eof(*args, **kwargs):\n"
        "    raise EOFError()\n"
        "builtins.input = _raise_eof\n"
        "module.main()\n"
    )


def _run_mode(args, env, *, cwd=None, stdin=None, timeout=10, managed_settings_paths=(), bootstrap_factory=_isolated_bootstrap):
    """Run mode.py's CLI isolated from any real managed-settings file.

    Defaults to ``managed_settings_paths=()`` -- no managed tier is ever
    consulted -- since these tests exercise the env/user-settings tiers,
    not the managed tier (see test_managed_settings_declaration_outranks_*
    below for managed-tier coverage, done in-process against
    ``claude_config_root``'s injectable parameter instead).

    A bounded default ``timeout`` (seconds) means a regression that makes
    ``read_mode`` block forever on a special file (a FIFO, or a symlink
    resolving to one) fails the test loudly and quickly instead of hanging
    the suite.
    """
    bootstrap = bootstrap_factory(SCRIPT, managed_settings_paths=managed_settings_paths)
    kwargs = {"env": env, "text": True, "capture_output": True, "timeout": timeout}
    if cwd is not None:
        kwargs["cwd"] = str(cwd)
    if stdin is not None:
        kwargs["stdin"] = stdin
    return subprocess.run([sys.executable, "-c", bootstrap, *args], **kwargs)


def _load_mode_module():
    """Load mode.py in-process (no subprocess) for direct unit calls against
    ``_settings_declared_config_dir`` itself, independent of the CLI/env
    plumbing the subprocess-based tests exercise."""
    spec = importlib.util.spec_from_file_location("prompt_it_mode_direct", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ModeTests(unittest.TestCase):
    def _call_with_timeout(self, callback, *, timeout=3):
        result = []
        errors = []

        def invoke():
            try:
                result.append(callback())
            except BaseException as exc:
                errors.append(exc)

        thread = threading.Thread(target=invoke, daemon=True)
        thread.start()
        thread.join(timeout)
        self.assertFalse(thread.is_alive(), "settings read blocked on a special file")
        if errors:
            raise errors[0]
        return result[0]

    def test_settings_declared_config_dir_rejects_fifo_without_hanging(self):
        # Companion to test_fifo_settings_sources_do_not_block_mode_commands
        # below, exercised directly against the helper: a settings file that
        # is a FIFO from the start must be classified as "declares nothing"
        # promptly, not by blocking on a read open.
        module = _load_mode_module()
        with tempfile.TemporaryDirectory() as directory:
            settings_path = Path(directory) / "settings.json"
            os.mkfifo(settings_path)
            self.assertIsNone(
                self._call_with_timeout(
                    lambda: module._settings_declared_config_dir(settings_path)
                )
            )

    def test_settings_declared_config_dir_race_to_fifo_does_not_hang(self):
        # Regression: `_settings_declared_config_dir` used to `stat()` a
        # settings path, decide it was a regular file, and only *then*
        # `read_text()` it -- a check-then-open window. A settings file
        # swapped for a FIFO inside that window made the (blocking, no
        # O_NONBLOCK) `read_text()` open wait forever for a writer, hanging
        # `setup`/`show`/`set`. The fix opens first (with O_NONBLOCK) and
        # classifies the *opened descriptor* via `os.fstat`, closing the
        # window entirely.
        #
        # This drives a real race for a bounded wall-clock duration --
        # continuously flipping the path between a regular JSON file and a
        # FIFO from a background thread -- while repeatedly calling the
        # function from the main thread through daemon threads. Each call is
        # bounded by a join timeout, so a reintroduced race fails this test
        # without keeping a non-daemon thread alive at interpreter shutdown.
        module = _load_mode_module()
        with tempfile.TemporaryDirectory() as directory:
            settings_path = Path(directory) / "settings.json"
            payload = json.dumps({"env": {"CLAUDE_CONFIG_DIR": "raced"}})
            settings_path.write_text(payload, encoding="utf-8")

            stop = threading.Event()

            def toggle():
                while not stop.is_set():
                    try:
                        settings_path.unlink()
                    except OSError:
                        pass
                    try:
                        os.mkfifo(settings_path)
                    except OSError:
                        pass
                    try:
                        settings_path.unlink()
                    except OSError:
                        pass
                    try:
                        settings_path.write_text(payload, encoding="utf-8")
                    except OSError:
                        pass

            toggler = threading.Thread(target=toggle, daemon=True)
            toggler.start()
            try:
                deadline = time.monotonic() + 2.0
                calls = 0
                while time.monotonic() < deadline:
                    result = self._call_with_timeout(
                        lambda: module._settings_declared_config_dir(settings_path),
                        timeout=2,
                    )
                    self.assertIn(result, (None, "raced"))
                    calls += 1
                self.assertGreater(calls, 0)
            finally:
                stop.set()
                toggler.join(timeout=2)

    def test_fifo_settings_sources_do_not_block_mode_commands(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            default_dir = home / ".claude"
            default_dir.mkdir()
            default_fifo = default_dir / "settings.json"
            managed_fifo = home / "managed-settings.json"
            os.mkfifo(default_fifo)
            os.mkfifo(managed_fifo)
            env = {**os.environ, "HOME": str(home), "CLAUDE_CONFIG_DIR": ""}
            bootstrap = _isolated_bootstrap(SCRIPT, (managed_fifo,))
            for command in ("show", "setup", "set"):
                args = [command, "--host", "claude"]
                if command != "show":
                    args += ["--mode", "just-go"]
                result = subprocess.run(
                    [sys.executable, "-c", bootstrap, *args],
                    cwd=home, env=env, text=True, capture_output=True,
                    timeout=3,
                )
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_mode_file_fifo_reports_invalid_and_never_hangs(self):
        # Regression: `read_mode` used `Path.exists()` + `Path.read_text()`
        # against `prompt-it-mode.json` itself (not a settings.json source,
        # which is already guarded elsewhere). Opening a FIFO for reading in
        # the default blocking mode waits forever for a writer to connect,
        # so if the mode file itself is a FIFO, `show`/`setup` would hang
        # instead of failing. `_run_mode`'s bounded timeout turns a
        # reintroduced hang into a fast, loud test failure rather than a
        # stuck suite.
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            config_dir = home / ".claude"
            config_dir.mkdir(parents=True, exist_ok=True)
            fifo = config_dir / "prompt-it-mode.json"
            os.mkfifo(fifo)
            env = {**os.environ, "HOME": str(home), "CLAUDE_CONFIG_DIR": ""}
            for command, extra in (("show", ()), ("setup", ("--mode", "just-go"))):
                with self.subTest(command=command):
                    result = _run_mode(
                        [command, "--host", "claude", *extra], env,
                        stdin=subprocess.DEVNULL,
                    )
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("could not be read", result.stderr)

    def test_mode_file_symlink_to_fifo_reports_invalid_and_never_hangs(self):
        # Companion to the direct-FIFO regression above: the mode file path
        # can also be a symlink whose target is a FIFO. `read_mode` must
        # classify the *opened descriptor* (which follows the symlink), not
        # just the path's own `lstat`, so this is caught the same way.
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            config_dir = home / ".claude"
            config_dir.mkdir(parents=True, exist_ok=True)
            real_fifo = config_dir / "real-fifo"
            os.mkfifo(real_fifo)
            mode_path = config_dir / "prompt-it-mode.json"
            mode_path.symlink_to(real_fifo)
            env = {**os.environ, "HOME": str(home), "CLAUDE_CONFIG_DIR": ""}
            for command, extra in (("show", ()), ("setup", ("--mode", "just-go"))):
                with self.subTest(command=command):
                    result = _run_mode(
                        [command, "--host", "claude", *extra], env,
                        stdin=subprocess.DEVNULL,
                    )
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("could not be read", result.stderr)

    def test_setup_switch_and_harness_isolation(self):
        with tempfile.TemporaryDirectory() as directory:
            # Explicitly override CLAUDE_CONFIG_DIR (not just CODEX_HOME) so
            # this test's later `--host claude` calls cannot inherit a
            # developer's real CLAUDE_CONFIG_DIR from **os.environ and read
            # from or create the actual Claude configuration.
            claude_home = Path(directory) / "claude"
            env = {
                **os.environ,
                "HOME": directory,
                "CODEX_HOME": str(Path(directory) / "codex"),
                "CLAUDE_CONFIG_DIR": str(claude_home),
            }

            def run(*args):
                return _run_mode(args, env)

            self.assertEqual(run("show", "--host", "codex").stdout.strip(), "unset")
            self.assertEqual(run("show", "--host", "claude").stdout.strip(), "unset")
            self.assertEqual(run("setup", "--host", "codex", "--mode", "ask-first").stdout.strip(), "ask-first")
            self.assertEqual(run("setup", "--host", "codex", "--mode", "just-go").stdout.strip(), "ask-first")
            self.assertEqual(run("set", "--host", "codex", "--mode", "just-go").stdout.strip(), "just-go")
            self.assertEqual(run("setup", "--host", "claude", "--mode", "ask-first").stdout.strip(), "ask-first")
            self.assertEqual(run("show", "--host", "codex").stdout.strip(), "just-go")
            self.assertEqual(run("show", "--host", "claude").stdout.strip(), "ask-first")
            self.assertEqual(
                json.loads((Path(directory) / "codex/prompt-it-mode.json").read_text()),
                {"version": 1, "mode": "just-go"},
            )
            # Deterministic isolation check: the claude-host mode landed
            # under the overridden CLAUDE_CONFIG_DIR, not anywhere else.
            self.assertEqual(
                json.loads((claude_home / "prompt-it-mode.json").read_text()),
                {"version": 1, "mode": "ask-first"},
            )
            self.assertNotEqual(run("set", "--host", "claude", "--mode", "invalid").returncode, 0)

    def test_noninteractive_setup_requires_choice(self):
        with tempfile.TemporaryDirectory() as directory:
            env = {**os.environ, "CODEX_HOME": directory}
            result = _run_mode(
                ["setup", "--host", "codex"], env, stdin=subprocess.DEVNULL,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((Path(directory) / "prompt-it-mode.json").exists())

    def test_setup_reports_concise_error_on_eof_instead_of_traceback(self):
        # Regression: a tty-like stdin (isatty() True) that hits end of
        # input before a choice is typed -- e.g. a detached terminal or an
        # agent host that connects a pty but never writes to it -- made
        # `input()` raise EOFError uncaught, producing a raw traceback
        # instead of the CLI's normal concise parser error.
        #
        # This is stubbed (sys.stdin.isatty() forced True, input() forced
        # to raise EOFError) rather than driven through a real pty: a
        # pty's isatty() after its master side is closed is not portable
        # -- it differs between macOS and Linux -- and the `pty` module
        # does not exist on Windows at all. The stub still exercises the
        # exact `try: input() except EOFError:` branch in mode.py that
        # prints the concise error.
        with tempfile.TemporaryDirectory() as directory:
            env = {**os.environ, "HOME": directory, "CODEX_HOME": str(Path(directory) / "codex")}
            result = _run_mode(
                ["setup", "--host", "codex"], env,
                stdin=subprocess.DEVNULL,
                bootstrap_factory=_isolated_bootstrap_stubbing_tty_eof,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn("Traceback", result.stderr)
            self.assertIn("no input", result.stderr)
            self.assertFalse((Path(directory) / "codex" / "prompt-it-mode.json").exists())

    def test_setup_rejects_dangling_symlink_instead_of_silent_success(self):
        # Regression: a dangling symlink at the mode-file path makes
        # `Path.exists()` false (so `read_mode` sees "unset") but `os.link`
        # still raises FileExistsError against the stale link name. `setup`
        # must reject this case loudly instead of printing "None" and
        # exiting 0 as if a mode had been saved.
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            config_dir = home / ".codex"
            config_dir.mkdir(parents=True, exist_ok=True)
            mode_path = config_dir / "prompt-it-mode.json"
            mode_path.symlink_to(config_dir / "does-not-exist.json")
            self.assertFalse(mode_path.exists())

            env = {**os.environ, "HOME": str(home), "CODEX_HOME": str(config_dir)}
            result = _run_mode(
                ["setup", "--host", "codex", "--mode", "just-go"], env,
                stdin=subprocess.DEVNULL,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn("None", result.stdout)
            self.assertIn("could not be read", result.stderr)

    def test_show_rejects_dangling_symlink_instead_of_reporting_unset(self):
        # Regression: `read_mode` used `Path.exists()`, which follows
        # symlinks, so a dangling `prompt-it-mode.json` symlink made `show`
        # print "unset" even though `setup` refuses to create a mode file at
        # that same path (see test_setup_rejects_dangling_symlink_...).
        # `show` must fail loudly and consistently instead of misreporting
        # an invalid path as an ordinary absent one.
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            config_dir = home / ".codex"
            config_dir.mkdir(parents=True, exist_ok=True)
            mode_path = config_dir / "prompt-it-mode.json"
            mode_path.symlink_to(config_dir / "does-not-exist.json")
            self.assertFalse(mode_path.exists())

            env = {**os.environ, "HOME": str(home), "CODEX_HOME": str(config_dir)}
            result = _run_mode(["show", "--host", "codex"], env)
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn("unset", result.stdout)
            self.assertIn("could not be read", result.stderr)

    def test_show_reports_unset_for_a_normal_absent_file(self):
        # Companion to the dangling-symlink regression above: a mode-file
        # path with no filesystem entry at all (the common case) must still
        # report "unset" rather than being caught by the new lexists check.
        with tempfile.TemporaryDirectory() as directory:
            env = {**os.environ, "HOME": directory, "CODEX_HOME": str(Path(directory) / "codex")}
            result = _run_mode(["show", "--host", "codex"], env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), "unset")

    def test_empty_overrides_fall_back_to_host_default_home(self):
        # An empty (but present) CODEX_HOME/CLAUDE_CONFIG_DIR must not resolve
        # to the process cwd; it must fall back to ~/.codex or ~/.claude.
        with tempfile.TemporaryDirectory() as directory:
            env = {
                **os.environ,
                "HOME": directory,
                "CODEX_HOME": "",
                "CLAUDE_CONFIG_DIR": "   ",
            }

            def run(*args):
                return _run_mode(args, env)

            self.assertEqual(run("setup", "--host", "codex", "--mode", "just-go").stdout.strip(), "just-go")
            self.assertEqual(run("setup", "--host", "claude", "--mode", "ask-first").stdout.strip(), "ask-first")
            self.assertTrue((Path(directory) / ".codex" / "prompt-it-mode.json").exists())
            self.assertTrue((Path(directory) / ".claude" / "prompt-it-mode.json").exists())
            self.assertFalse((Path(directory) / "prompt-it-mode.json").exists())

    def test_relative_override_resolves_against_the_callers_cwd(self):
        # A relative CODEX_HOME/CLAUDE_CONFIG_DIR override resolves against
        # the process's current directory, matching each host's own
        # resolution (Codex's installer uses Path(CODEX_HOME) directly;
        # Claude Code's CLAUDE_CONFIG_DIR resolves relative to the launch
        # directory -- see scripts/local_claude_settings.py's
        # _resolve_config_dir, and tests/test_prompt_it_mode_host_parity.py
        # for a direct comparison against both real resolvers). This script
        # must not invent its own anchor (e.g. the user's home directory):
        # doing so previously disagreed with both hosts and only happened
        # to "work" because the skill's docs told the model to `cd` into the
        # skill directory before every call. The docs (SKILL.md, README.md)
        # now invoke this script by absolute path without changing cwd, so
        # `setup`, `show`, and `set` naturally agree by running from the
        # same (unchanged) caller directory every time.
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            project_cwd = home / "project"
            project_cwd.mkdir()
            env = {
                **os.environ,
                "HOME": str(home),
                "CODEX_HOME": "relative-codex-home",
                "CLAUDE_CONFIG_DIR": "relative-claude-home",
            }

            def run(cwd, *args):
                return _run_mode(args, env, cwd=cwd)

            self.assertEqual(
                run(project_cwd, "setup", "--host", "codex", "--mode", "just-go").stdout.strip(),
                "just-go",
            )
            self.assertEqual(
                run(project_cwd, "setup", "--host", "claude", "--mode", "ask-first").stdout.strip(),
                "ask-first",
            )
            # Landed relative to the caller's cwd, not under home.
            self.assertTrue((project_cwd / "relative-codex-home" / "prompt-it-mode.json").exists())
            self.assertTrue((project_cwd / "relative-claude-home" / "prompt-it-mode.json").exists())
            self.assertFalse((home / "relative-codex-home").exists())
            self.assertFalse((home / "relative-claude-home").exists())
            # Repeated calls from that same directory keep agreeing.
            self.assertEqual(run(project_cwd, "show", "--host", "codex").stdout.strip(), "just-go")
            self.assertEqual(run(project_cwd, "show", "--host", "claude").stdout.strip(), "ask-first")
            self.assertEqual(
                run(project_cwd, "set", "--host", "codex", "--mode", "ask-first").stdout.strip(),
                "ask-first",
            )
            self.assertEqual(run(project_cwd, "show", "--host", "codex").stdout.strip(), "ask-first")

    def test_claude_config_dir_override_is_honored(self):
        with tempfile.TemporaryDirectory() as directory:
            override = Path(directory) / "custom-claude-home"
            env = {**os.environ, "HOME": directory, "CLAUDE_CONFIG_DIR": str(override)}
            result = _run_mode(["setup", "--host", "claude", "--mode", "just-go"], env)
            self.assertEqual(result.stdout.strip(), "just-go")
            self.assertTrue((override / "prompt-it-mode.json").exists())
            self.assertFalse((Path(directory) / ".claude" / "prompt-it-mode.json").exists())

    def test_concurrent_set_calls_do_not_collide_on_shared_staging_file(self):
        # Regression: concurrent setup/set attempts used one fixed
        # `<file>.tmp` staging path, so one run's write could truncate or
        # replace another run's still-in-flight temp file.
        with tempfile.TemporaryDirectory() as directory:
            env = {**os.environ, "HOME": directory, "CODEX_HOME": str(Path(directory) / "codex")}

            def run(*args):
                return _run_mode(args, env)

            run("setup", "--host", "codex", "--mode", "ask-first")

            def set_mode(mode):
                return run("set", "--host", "codex", "--mode", mode)

            with ThreadPoolExecutor(max_workers=8) as pool:
                results = list(pool.map(set_mode, ["ask-first", "just-go"] * 8))

            for result in results:
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(result.stdout.strip(), {"ask-first", "just-go"})

            config_path = Path(directory) / "codex" / "prompt-it-mode.json"
            saved = json.loads(config_path.read_text())
            self.assertEqual(saved["version"], 1)
            self.assertIn(saved["mode"], {"ask-first", "just-go"})
            leftover_temp_files = list(config_path.parent.glob("*.tmp"))
            self.assertEqual(leftover_temp_files, [])

    def test_concurrent_conflicting_first_use_setup_picks_one_winner(self):
        # Regression: two concurrent first-use `setup` calls both observed
        # "unset" and both could publish a different mode, with the later
        # write silently clobbering the earlier one. `setup` must be an
        # atomic create-if-absent: exactly one mode wins, and every caller
        # -- winner and losers alike -- reports that same saved mode.
        with tempfile.TemporaryDirectory() as directory:
            env = {**os.environ, "HOME": directory, "CODEX_HOME": str(Path(directory) / "codex")}

            def setup(mode):
                return _run_mode(["setup", "--host", "codex", "--mode", mode], env)

            with ThreadPoolExecutor(max_workers=8) as pool:
                results = list(pool.map(setup, ["ask-first", "just-go"] * 8))

            for result in results:
                self.assertEqual(result.returncode, 0, result.stderr)

            reported = {result.stdout.strip() for result in results}
            self.assertEqual(len(reported), 1, f"setup callers disagreed on the winner: {reported}")

            config_path = Path(directory) / "codex" / "prompt-it-mode.json"
            saved = json.loads(config_path.read_text())
            self.assertEqual(saved, {"version": 1, "mode": next(iter(reported))})
            leftover_temp_files = list(config_path.parent.glob("*.tmp"))
            self.assertEqual(leftover_temp_files, [])

    def test_set_reports_concise_error_on_write_failure(self):
        # Regression: `set` called the filesystem writer outside the error
        # handler `show`/`setup` use, so an expected OSError (e.g. a
        # config directory that cannot be created) produced a raw Python
        # traceback instead of the CLI's normal concise parser error.
        #
        # A chmod-0500 directory is not deterministic across privilege
        # levels (root bypasses it), so instead make the config "directory"
        # a regular file: `path.parent.mkdir(..., exist_ok=True)` then
        # raises FileExistsError for every caller regardless of privilege.
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            config_dir = home / ".codex"
            config_dir.write_text("not a directory", encoding="utf-8")
            env = {**os.environ, "HOME": str(home), "CODEX_HOME": str(config_dir)}
            result = _run_mode(["set", "--host", "codex", "--mode", "just-go"], env)
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn("Traceback", result.stderr)

    def test_non_object_mode_file_is_rejected(self):
        for payload in ("[1, 2]", "null", "42", '"just-go"'):
            with self.subTest(payload=payload):
                with tempfile.TemporaryDirectory() as directory:
                    home = Path(directory)
                    config_dir = home / ".claude"
                    config_dir.mkdir(parents=True, exist_ok=True)
                    (config_dir / "prompt-it-mode.json").write_text(payload, encoding="utf-8")
                    env = {**os.environ, "HOME": str(home), "CLAUDE_CONFIG_DIR": ""}
                    result = _run_mode(["show", "--host", "claude"], env)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("invalid Prompt it mode file", result.stderr)

    def test_invalid_utf8_mode_file_is_rejected_without_traceback(self):
        # Regression: `path.read_text(encoding="utf-8")` raises
        # UnicodeDecodeError for non-UTF-8 bytes, which was uncaught and
        # surfaced as a traceback instead of the intended concise
        # "invalid mode file" error.
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            config_dir = home / ".claude"
            config_dir.mkdir(parents=True, exist_ok=True)
            (config_dir / "prompt-it-mode.json").write_bytes(b"\xff\xfe\x00\x01")
            env = {**os.environ, "HOME": str(home), "CLAUDE_CONFIG_DIR": ""}
            result = _run_mode(["show", "--host", "claude"], env)
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn("Traceback", result.stderr)
            self.assertIn("invalid Prompt it mode file", result.stderr)

    def test_unhashable_mode_value_is_rejected(self):
        # Regression: `data.get("mode") not in MODES` calls `in` against a
        # set, which raises TypeError for an unhashable value (a list or
        # object) instead of the intended "invalid mode file" ValueError.
        for payload in ('{"version": 1, "mode": ["ask-first"]}', '{"version": 1, "mode": {}}', '{"version": 1, "mode": 5}'):
            with self.subTest(payload=payload):
                with tempfile.TemporaryDirectory() as directory:
                    home = Path(directory)
                    config_dir = home / ".claude"
                    config_dir.mkdir(parents=True, exist_ok=True)
                    (config_dir / "prompt-it-mode.json").write_text(payload, encoding="utf-8")
                    env = {**os.environ, "HOME": str(home), "CLAUDE_CONFIG_DIR": ""}
                    result = _run_mode(["show", "--host", "claude"], env)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertNotIn("Traceback", result.stderr)
                    self.assertIn("invalid Prompt it mode file", result.stderr)

    def test_non_integer_version_is_rejected(self):
        # Regression: `data.get("version") != 1` uses `!=`, so JSON `true`
        # and `1.0` compare equal to the integer 1 in Python and were
        # wrongly accepted as a valid schema version.
        for payload in ('{"version": true, "mode": "just-go"}', '{"version": 1.0, "mode": "just-go"}'):
            with self.subTest(payload=payload):
                with tempfile.TemporaryDirectory() as directory:
                    home = Path(directory)
                    config_dir = home / ".claude"
                    config_dir.mkdir(parents=True, exist_ok=True)
                    (config_dir / "prompt-it-mode.json").write_text(payload, encoding="utf-8")
                    env = {**os.environ, "HOME": str(home), "CLAUDE_CONFIG_DIR": ""}
                    result = _run_mode(["show", "--host", "claude"], env)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertNotIn("Traceback", result.stderr)
                    self.assertIn("invalid Prompt it mode file", result.stderr)

    def test_integer_version_is_still_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            config_dir = home / ".claude"
            config_dir.mkdir(parents=True, exist_ok=True)
            (config_dir / "prompt-it-mode.json").write_text(
                '{"version": 1, "mode": "just-go"}', encoding="utf-8"
            )
            env = {**os.environ, "HOME": str(home), "CLAUDE_CONFIG_DIR": ""}
            result = _run_mode(["show", "--host", "claude"], env)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout.strip(), "just-go")

    def test_unresolvable_claude_config_dir_reports_concise_error(self):
        # Regression: an unresolvable ``~user`` form makes
        # ``Path.expanduser()`` raise RuntimeError from inside
        # ``config_path``, which used to happen before any of `show`,
        # `setup`, or `set`'s own error handling -- producing a raw
        # traceback instead of the CLI's normal concise argparse error.
        for command, extra in (
            ("show", ()),
            ("setup", ("--mode", "just-go")),
            ("set", ("--mode", "just-go")),
        ):
            with self.subTest(command=command):
                with tempfile.TemporaryDirectory() as directory:
                    env = {
                        **os.environ,
                        "HOME": directory,
                        "CLAUDE_CONFIG_DIR": "~unknown-user-should-not-exist/claude",
                    }
                    result = _run_mode(
                        [command, "--host", "claude", *extra], env,
                        stdin=subprocess.DEVNULL,
                    )
                    self.assertNotEqual(result.returncode, 0)
                    self.assertNotIn("Traceback", result.stderr)

    def test_set_repairs_malformed_existing_file(self):
        # Regression: `set` is an unconditional mode switch, but it used to
        # validate the existing file before dispatch, so a truncated or
        # old-schema file left users with no way to repair the preference
        # via `set`.
        for payload in ("not json at all", "[1, 2]", '{"mode": "bogus"}', ""):
            with self.subTest(payload=payload):
                with tempfile.TemporaryDirectory() as directory:
                    home = Path(directory)
                    config_dir = home / ".claude"
                    config_dir.mkdir(parents=True, exist_ok=True)
                    config_path = config_dir / "prompt-it-mode.json"
                    config_path.write_text(payload, encoding="utf-8")
                    env = {**os.environ, "HOME": str(home), "CLAUDE_CONFIG_DIR": ""}

                    result = _run_mode(["set", "--host", "claude", "--mode", "just-go"], env)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stdout.strip(), "just-go")
                    self.assertEqual(
                        json.loads(config_path.read_text()),
                        {"version": 1, "mode": "just-go"},
                    )

    def test_default_isolated_runner_ignores_a_malicious_managed_settings_path(self):
        # Proves the isolation _run_mode gives every test above actually
        # blocks a managed-settings redirect, rather than the redirect
        # simply never being exercised. Two runs against the identical
        # malicious file: wired in as a managed path, it hijacks
        # CLAUDE_CONFIG_DIR (the attack is real); through the default
        # isolated helper (managed_settings_paths=()), the same file sits
        # untouched and mode.py falls back to the plain default directory.
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            malicious = home / "malicious-managed-settings.json"
            malicious.write_text(
                json.dumps({"env": {"CLAUDE_CONFIG_DIR": "redirected-by-malicious-managed"}})
            )
            env = {"HOME": str(home), "PATH": "/usr/bin:/bin"}

            hijacked = _run_mode(
                ["setup", "--host", "claude", "--mode", "just-go"], env, cwd=home,
                managed_settings_paths=(malicious,),
            )
            self.assertEqual(hijacked.returncode, 0, hijacked.stderr)
            self.assertTrue(
                (home / "redirected-by-malicious-managed" / "prompt-it-mode.json").exists()
            )

        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            malicious = home / "malicious-managed-settings.json"
            malicious.write_text(
                json.dumps({"env": {"CLAUDE_CONFIG_DIR": "redirected-by-malicious-managed"}})
            )
            env = {"HOME": str(home), "PATH": "/usr/bin:/bin"}

            result = _run_mode(["setup", "--host", "claude", "--mode", "just-go"], env, cwd=home)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((home / ".claude" / "prompt-it-mode.json").exists())
            self.assertFalse((home / "redirected-by-malicious-managed").exists())


class StandaloneSkillInstallResolutionTests(unittest.TestCase):
    """Regression for the documented Claude Code standalone-install
    fallback (SKILL.md/README.md "Choose an approval mode at setup"): when
    ``CLAUDE_PLUGIN_ROOT`` is unset because this skill is installed as a
    symlink under a skills directory (e.g. ``~/.claude/skills/prompt-it``)
    rather than as a marketplace/managed plugin, the documented fallback --
    locate the directory of the *currently loaded* ``SKILL.md`` (resolving
    it to its real, current target when it is a symlink) and invoke that
    directory's sibling ``scripts/mode.py`` by absolute path -- must
    actually work end-to-end, must be re-resolved (not cached) across a
    mid-session repoint of the symlink, and must not depend on the default
    ``~/.claude`` skills root at all: a relocated ``CLAUDE_CONFIG_DIR`` can
    move the skills root somewhere else entirely, so the fallback must
    still work when the well-known ``~/.claude/skills/prompt-it`` path does
    not exist. Every run below uses an isolated ``HOME``/
    ``CLAUDE_CONFIG_DIR`` and never touches this machine's real
    ``~/.claude``.
    """

    def _isolated_env(self, root):
        return {
            **os.environ,
            "HOME": str(root),
            "CLAUDE_CONFIG_DIR": str(root / "isolated-claude-home"),
        }

    def _run_via_resolved_script(self, resolved_script, args, env):
        bootstrap = _isolated_bootstrap(resolved_script, managed_settings_paths=())
        return subprocess.run(
            [sys.executable, "-c", bootstrap, *args],
            env=env, text=True, capture_output=True, timeout=5,
        )

    def test_symlinked_standalone_install_resolves_to_this_checkout(self):
        # SCRIPT is .../plugins/prompt-it/skills/prompt-it/scripts/mode.py;
        # its skill directory is two levels up.
        skill_dir = SCRIPT.parent.parent
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skills_root = root / "dot-claude-skills"
            skills_root.mkdir()
            symlink = skills_root / "prompt-it"
            symlink.symlink_to(skill_dir)

            # The documented fallback: resolve the well-known standalone
            # install path (a symlink) to its real, current target --
            # equivalent to `realpath ~/.claude/skills/prompt-it`.
            resolved = symlink.resolve()
            self.assertEqual(resolved, skill_dir.resolve())
            resolved_script = resolved / "scripts" / "mode.py"
            self.assertTrue(resolved_script.is_file())
            self.assertEqual(resolved_script.resolve(), SCRIPT.resolve())

    def test_setup_show_set_work_through_the_resolved_symlink_path(self):
        skill_dir = SCRIPT.parent.parent
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skills_root = root / "dot-claude-skills"
            skills_root.mkdir()
            symlink = skills_root / "prompt-it"
            symlink.symlink_to(skill_dir)
            resolved_script = symlink.resolve() / "scripts" / "mode.py"
            env = self._isolated_env(root)

            def run(*args):
                return self._run_via_resolved_script(resolved_script, args, env)

            self.assertEqual(run("show", "--host", "claude").stdout.strip(), "unset")
            self.assertEqual(
                run("setup", "--host", "claude", "--mode", "ask-first").stdout.strip(),
                "ask-first",
            )
            self.assertEqual(run("show", "--host", "claude").stdout.strip(), "ask-first")
            # Mid-session switch, same resolved absolute path.
            self.assertEqual(
                run("set", "--host", "claude", "--mode", "just-go").stdout.strip(),
                "just-go",
            )
            self.assertEqual(run("show", "--host", "claude").stdout.strip(), "just-go")
            self.assertTrue(
                (root / "isolated-claude-home" / "prompt-it-mode.json").exists()
            )
            self.assertFalse((root / ".claude").exists())

    def test_relocated_config_root_symlink_install_resolves_via_loaded_skill_path(self):
        # CLAUDE_CONFIG_DIR can relocate the entire skills root away from
        # ~/.claude entirely, so `~/.claude/skills/prompt-it` does not exist
        # at all in this scenario -- any fallback that guesses at that
        # well-known default path would fail to find the skill. The
        # documented fix locates the directory of the *currently loaded*
        # SKILL.md instead, independent of any default home/config path --
        # modeled here by resolving the symlink under the relocated skills
        # root directly, the way a session's own skill loader would report
        # it, never falling back to a ~/.claude guess.
        skill_dir = SCRIPT.parent.parent
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            relocated_config_dir = root / "relocated-claude-config"
            relocated_skills_root = relocated_config_dir / "skills"
            relocated_skills_root.mkdir(parents=True)
            symlink = relocated_skills_root / "prompt-it"
            symlink.symlink_to(skill_dir)

            env = {
                **os.environ,
                "HOME": str(root),
                "CLAUDE_CONFIG_DIR": str(relocated_config_dir),
            }

            # The well-known default path must not exist at all here --
            # proving any fallback that guesses at it would fail to find
            # this install.
            self.assertFalse((root / ".claude" / "skills" / "prompt-it").exists())

            # The currently-loaded skill's own directory -- what a
            # session's skill loader would report -- is the relocated
            # symlink, not the default path.
            resolved_script = symlink.resolve() / "scripts" / "mode.py"
            self.assertEqual(resolved_script.resolve(), SCRIPT.resolve())

            def run(*args):
                return self._run_via_resolved_script(resolved_script, args, env)

            self.assertEqual(run("show", "--host", "claude").stdout.strip(), "unset")
            self.assertEqual(
                run("setup", "--host", "claude", "--mode", "just-go").stdout.strip(),
                "just-go",
            )
            self.assertEqual(run("show", "--host", "claude").stdout.strip(), "just-go")
            self.assertEqual(
                run("set", "--host", "claude", "--mode", "ask-first").stdout.strip(),
                "ask-first",
            )
            self.assertEqual(run("show", "--host", "claude").stdout.strip(), "ask-first")
            self.assertTrue(
                (relocated_config_dir / "prompt-it-mode.json").exists()
            )
            self.assertFalse((root / ".claude").exists())

    def test_mid_session_symlink_repoint_is_picked_up_by_re_resolving(self):
        # A cached first-resolved path must not be reused: repointing the
        # symlink to a different (copied) skill directory mid-session and
        # re-resolving must reach the *new* target, not the old one --
        # mirroring a real branch/worktree switch under
        # ~/.claude/skills/prompt-it between two mode.py invocations.
        skill_dir = SCRIPT.parent.parent
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skills_root = root / "dot-claude-skills"
            skills_root.mkdir()
            symlink = skills_root / "prompt-it"
            symlink.symlink_to(skill_dir)
            env = self._isolated_env(root)

            first_resolved_script = symlink.resolve() / "scripts" / "mode.py"
            result = self._run_via_resolved_script(
                first_resolved_script, ["setup", "--host", "claude", "--mode", "ask-first"], env,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), "ask-first")

            # Repoint the symlink to an independent copy of the skill
            # directory -- a genuinely different absolute path -- the way a
            # branch checkout under the same install location would.
            second_copy = root / "second-checkout-skill-dir"
            shutil.copytree(skill_dir, second_copy)
            symlink.unlink()
            symlink.symlink_to(second_copy)

            second_resolved = symlink.resolve()
            self.assertEqual(second_resolved, second_copy.resolve())
            self.assertNotEqual(second_resolved, skill_dir.resolve())
            second_resolved_script = second_resolved / "scripts" / "mode.py"
            self.assertTrue(second_resolved_script.is_file())

            result = self._run_via_resolved_script(
                second_resolved_script, ["show", "--host", "claude"], env,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            # State lives in the isolated CLAUDE_CONFIG_DIR, not the skill
            # directory, so the mode saved through the first (now-replaced)
            # target is still visible through the new resolved path.
            self.assertEqual(result.stdout.strip(), "ask-first")


if __name__ == "__main__":
    unittest.main()
