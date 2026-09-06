"""Exercise canonical-package parity and reject host-specific drift offline."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PackageParityTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='prompt-it-package-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / 'package'
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(
            '.git', '__pycache__', '*.pyc', '.scratch'))

    def validate(self):
        return subprocess.run(
            [sys.executable, 'scripts/validate_public_package.py'],
            cwd=self.root, capture_output=True, text=True, check=False,
        )

    def manifest(self, host, skills):
        path = self.root / 'plugins/prompt-it' / host / 'plugin.json'
        value = json.loads(path.read_text())
        value['skills'] = skills
        path.write_text(json.dumps(value))

    def test_both_packaged_hosts_validate(self):
        result = self.validate()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_explicit_claude_path_can_use_the_same_canonical_directory(self):
        self.manifest('.claude-plugin', './skills/')
        result = self.validate()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_either_host_pointing_at_another_skill_copy_is_rejected(self):
        for host in ('.codex-plugin', '.claude-plugin'):
            with self.subTest(host=host):
                path = self.root / 'plugins/prompt-it' / host / 'plugin.json'
                original = path.read_text()
                self.manifest(host, './other-skills/')
                self.assertNotEqual(self.validate().returncode, 0)
                path.write_text(original)

    def test_different_loader_authority_is_rejected(self):
        path = self.root / 'snippets/claude-md-gate.md'
        text = path.read_text().replace(
            'then stop for execution approval.', 'then begin implementation immediately.')
        self.assertNotEqual(text, path.read_text())
        path.write_text(text)
        self.assertNotEqual(self.validate().returncode, 0)

    def test_either_marketplace_pointing_at_another_package_is_rejected(self):
        for relative in ('.agents/plugins/marketplace.json', '.claude-plugin/marketplace.json'):
            with self.subTest(marketplace=relative):
                path = self.root / relative
                original = path.read_text()
                payload = json.loads(original)
                entry = next(item for item in payload['plugins'] if item['name'] == 'prompt-it')
                source = entry['source']
                if isinstance(source, dict):
                    source['path'] = './plugins/other'
                else:
                    entry['source'] = './plugins/other'
                path.write_text(json.dumps(payload))
                self.assertNotEqual(self.validate().returncode, 0)
                path.write_text(original)

    def test_missing_shared_reference_is_rejected(self):
        path = self.root / 'plugins/prompt-it/skills/prompt-it/references/task-graphs.md'
        path.unlink()
        self.assertNotEqual(self.validate().returncode, 0)


if __name__ == '__main__':
    unittest.main()
