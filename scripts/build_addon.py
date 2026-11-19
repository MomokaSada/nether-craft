"""Build the behavior pack as an mcpack inside an mcaddon, using only the standard library."""

import argparse
import io
import json
from pathlib import Path
import uuid
import zipfile


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=root / "dist")
    parser.add_argument("--tag", help="Release tag, which must match the manifest version")
    args = parser.parse_args()

    files = [root / "manifest.json", *sorted((root / "loot_tables").rglob("*.json"))]
    documents = {p.relative_to(root).as_posix(): p.read_bytes() for p in files}
    parsed = {name: json.loads(data) for name, data in documents.items()}
    manifest = parsed["manifest.json"]
    version = manifest["header"]["version"]
    if len(version) != 3 or any(type(n) is not int or n < 0 for n in version):
        parser.error("manifest version must contain three non-negative integers")
    for module in manifest["modules"]:
        uuid.UUID(module["uuid"])
        if module["version"] != version:
            parser.error("module version must match header version")
    uuid.UUID(manifest["header"]["uuid"])
    if "loot_tables/entities/piglin_barter.json" not in documents:
        parser.error("piglin barter loot table is missing")
    version_text = ".".join(map(str, version))
    if args.tag is not None and args.tag != f"v{version_text}":
        parser.error(f"tag must match manifest version: v{version_text}")

    pack = io.BytesIO()
    with zipfile.ZipFile(pack, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in documents.items():
            archive.writestr(name, data)
    addon = io.BytesIO()
    with zipfile.ZipFile(addon, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("nether-craft-bp.mcpack", pack.getvalue())
    args.output.mkdir(parents=True, exist_ok=True)
    destination = args.output / f"nether-craft-{version_text}.mcaddon"
    destination.write_bytes(addon.getvalue())
    print(destination)


if __name__ == "__main__":
    main()
