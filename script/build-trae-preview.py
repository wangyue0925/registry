#!/usr/bin/env python3
"""Build the TRAE-only index used by this fork's preview releases."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil


def build_registry(metadata, manifest, release_base):
    version = manifest["distribution_version"]
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+-preview\.[1-9][0-9]*", version):
        raise ValueError("Expected an X.Y.Z-preview.N distribution version")
    if manifest["product"] != "traecli" or metadata["id"] != "traecli":
        raise ValueError("Expected TRAE CLI metadata")
    if manifest["binary_version"] != manifest["version"]:
        raise ValueError("The manifest's binary versions disagree")

    expected = {
        "darwin-aarch64", "darwin-x86_64", "linux-aarch64",
        "linux-x86_64", "windows-aarch64", "windows-x86_64",
    }
    binary = {}
    archive_base = (
        "https://lf-cdn.trae.com.cn/obj/trae-com-cn/trae-cli/v2/acp/releases/"
        + version + "/"
    )
    for artifact in manifest["artifacts"]:
        platform = artifact["platform"]
        if platform not in expected or platform in binary:
            raise ValueError("Unexpected or repeated platform: " + platform)
        extension = ".zip" if platform.startswith("windows-") else ".tar.gz"
        filename = "traecli-acp-" + platform + extension
        if artifact["url"] != archive_base + filename:
            raise ValueError("Unexpected archive URL for " + platform)
        if not re.fullmatch(r"[a-f0-9]{64}", artifact["sha256"]):
            raise ValueError("Invalid SHA-256 for " + platform)
        command = "./bin/traex.exe" if platform.startswith("windows-") else "./bin/traex"
        if artifact["cmd"] != command or artifact["args"] != ["acp", "serve"]:
            raise ValueError("Unexpected ACP command for " + platform)
        binary[platform] = {
            "archive": artifact["url"],
            "sha256": artifact["sha256"],
            "cmd": artifact["cmd"],
            "args": artifact["args"],
        }
        if artifact.get("env"):
            binary[platform]["env"] = artifact["env"]
    if set(binary) != expected:
        raise ValueError("The preview manifest must cover all six platforms")

    agent = {key: value for key, value in metadata.items() if key != "preview"}
    agent.update(
        version=version,
        icon=release_base.rstrip("/") + "/traecli.svg",
        distribution={"binary": binary},
    )
    return {"version": "1.0.0", "agents": [agent]}


def main():
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=root / "traecli/preview-manifest.json")
    parser.add_argument("--output-dir", type=Path, default=root / "dist/trae-preview")
    parser.add_argument("--repository", default="wangyue0925/registry")
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    metadata = json.loads((root / "traecli/agent.json").read_text(encoding="utf-8"))
    tag = "traecli-" + manifest["distribution_version"]
    release_base = "https://github.com/" + args.repository + "/releases/download/" + tag
    registry = build_registry(metadata, manifest, release_base)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "registry.json").write_text(
        json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    shutil.copyfile(root / "traecli/icon.svg", args.output_dir / "traecli.svg")
    shutil.copyfile(args.manifest, args.output_dir / "manifest.json")
    names = ["registry.json", "traecli.svg", "manifest.json"]
    checksums = [
        hashlib.sha256((args.output_dir / name).read_bytes()).hexdigest() + "  " + name
        for name in names
    ]
    (args.output_dir / "SHA256SUMS").write_text("\n".join(checksums) + "\n", encoding="utf-8")
    print("Release tag:", tag)
    print("Registry URL:", release_base + "/registry.json")
    print("Artifacts:", args.output_dir)


if __name__ == "__main__":
    main()
