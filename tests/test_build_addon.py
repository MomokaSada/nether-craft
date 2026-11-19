import base64
import io
import json
from pathlib import Path
import subprocess
import shutil
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
                    expected = {"manifest.json", "loot_tables/entities/piglin_barter.json"}
                    if (ROOT / "pack_icon.png").is_file():
                        expected.add("pack_icon.png")
                    self.assertEqual(set(pack.namelist()), expected)
                    for name in pack.namelist():
                        self.assertEqual(pack.read(name), (ROOT / name).read_bytes())

    def test_icon_is_optional_and_included_at_pack_root(self):
        icon = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aT1sAAAAASUVORK5CYII="
        )
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in ["manifest.json", "scripts/build_addon.py", "loot_tables/entities/piglin_barter.json"]:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, target)
            for with_icon in [False, True]:
                with self.subTest(with_icon=with_icon):
                    if with_icon:
                        (root / "pack_icon.png").write_bytes(icon)
                    subprocess.run([sys.executable, str(root / "scripts/build_addon.py")], check=True, capture_output=True)
                    addon = next((root / "dist").glob("*.mcaddon"))
                    with zipfile.ZipFile(addon) as outer:
                        with zipfile.ZipFile(io.BytesIO(outer.read("nether-craft-bp.mcpack"))) as pack:
                            self.assertEqual("pack_icon.png" in pack.namelist(), with_icon)
                            if with_icon:
                                self.assertEqual(pack.read("pack_icon.png"), icon)

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
