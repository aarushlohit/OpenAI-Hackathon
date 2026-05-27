import json
import unittest
from pathlib import Path


class ExtensionManifestTests(unittest.TestCase):
    def test_manifest_v3_contract(self) -> None:
        manifest = json.loads(Path("frontend/browser_extension/manifest.json").read_text())

        self.assertEqual(manifest["manifest_version"], 3)
        self.assertIn("src/background.js", manifest["background"]["service_worker"])

