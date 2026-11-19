import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/build_addon.py"


class BuildAddonTest(unittest.TestCase):
    def test_package_contains_only_pack_files_matching_source(self):
        version = ".".join(map(str, json.loads((ROOT / "manifest.json").read_text())["header"]["version"]))
        with tempfile.TemporaryDirectory() as output:
            subprocess.run([sys.executable, str(SCRIPT), "--output", output, "--tag", f"v{version}"], check=True)
            with zipfile.ZipFile(Path(output) / f"nether-craft-{version}.mcaddon") as outer:
                self.assertIsNone(outer.testzip())
                self.assertEqual(outer.namelist(), ["nether-craft-bp.mcpack"])
                with zipfile.ZipFile(io.BytesIO(outer.read("nether-craft-bp.mcpack"))) as pack:
                    self.assertIsNone(pack.testzip())
                    self.assertEqual(set(pack.namelist()), {"manifest.json", "loot_tables/entities/piglin_barter.json"})
                    for name in pack.namelist():
                        self.assertEqual(pack.read(name), (ROOT / name).read_bytes())

    def test_mismatched_tag_produces_no_release_file(self):
        with tempfile.TemporaryDirectory() as output:
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--output", output, "--tag", "v999.999.999"],
                capture_output=True, text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("tag must match", result.stderr)
            self.assertEqual(list(Path(output).iterdir()), [])


if __name__ == "__main__":
    unittest.main()
