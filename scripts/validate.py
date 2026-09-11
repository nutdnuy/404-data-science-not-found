#!/usr/bin/env python3
"""Validate the portable skill package and its local documentation references."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml


ROOT = Path(__file__).resolve().parents[1]
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
LINK = re.compile(r"(?<!!)\[[^\]\n]+\]\(([^\s)]+)(?:\s+\"[^\"]*\")?\)")
ALLOWED = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
IGNORED = {".git", ".venv", "node_modules", "outputs", "__pycache__"}


def contained(path: Path, root: Path) -> bool:
    return path.resolve().is_relative_to(root.resolve())


def check_skill(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    pieces = re.split(r"^---\s*$", text, maxsplit=2, flags=re.MULTILINE)
    if len(pieces) != 3 or pieces[0].strip():
        return [f"{path}: missing YAML frontmatter"]
    try:
        metadata = yaml.safe_load(pieces[1])
    except yaml.YAMLError as exc:
        return [f"{path}: invalid YAML: {exc}"]
    if not isinstance(metadata, dict):
        return [f"{path}: frontmatter must be a mapping"]
    name = metadata.get("name")
    if not isinstance(name, str) or len(name) > 64 or not NAME.fullmatch(name):
        errors.append(f"{path}: invalid skill name")
    if name != path.parent.name:
        errors.append(f"{path}: name must match folder")
    description = metadata.get("description")
    if not isinstance(description, str) or not 1 <= len(description.strip()) <= 1024:
        errors.append(f"{path}: description must contain 1–1024 characters")
    if set(metadata) - ALLOWED:
        errors.append(f"{path}: non-portable metadata keys: {set(metadata) - ALLOWED}")
    if not pieces[2].strip():
        errors.append(f"{path}: empty instructions")
    if len(text.splitlines()) > 500:
        errors.append(f"{path}: move conditional detail into references (over 500 lines)")
    for target in LINK.findall(pieces[2]):
        parsed = urlsplit(target.strip("<>"))
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        resolved = path.parent / unquote(parsed.path)
        if not contained(resolved, path.parent):
            errors.append(f"{path}: dependency escapes individually installed skill: {target}")
        elif not resolved.exists():
            errors.append(f"{path}: missing skill resource: {target}")
    return errors


def validate(root: Path = ROOT) -> tuple[list[str], int]:
    errors: list[str] = []
    manifest = json.loads((root / "skills.json").read_text())
    expected = manifest["skills"]
    names = [entry["name"] for entry in expected]
    if len(names) != len(set(names)):
        errors.append("skills.json: duplicate skill names")
    skills = sorted((root / "skills").glob("*/SKILL.md"))
    actual = {path.parent.name for path in skills}
    if actual != set(names):
        errors.append(f"Manifest/package mismatch: missing={set(names) - actual}, extra={actual - set(names)}")
    for path in skills:
        errors.extend(check_skill(path))
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if any(part in IGNORED for part in relative.parts):
            continue
        if path.is_symlink():
            errors.append(f"{relative}: distribution must contain real files, not local symlinks")
        if not path.is_file() or path.suffix != ".md":
            continue
        body = path.read_text(encoding="utf-8")
        if "/Users/" in body or "/private/tmp/" in body:
            errors.append(f"{relative}: contains a machine-specific local path")
        if "OWNER/" in body or "github.com/OWNER" in body:
            errors.append(f"{relative}: unresolved repository owner")
        # Code fences contain illustrative paths rather than documentation links.
        prose = re.sub(r"```.*?```", "", body, flags=re.DOTALL)
        for target in LINK.findall(prose):
            parsed = urlsplit(target.strip("<>"))
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            resolved = path.parent / unquote(parsed.path)
            if not contained(resolved, root) or not resolved.exists():
                errors.append(f"{relative}: broken local link: {target}")
    return errors, len(skills)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    errors, count = validate(args.root.resolve())
    if errors:
        print("\n".join(errors))
        print(f"FAILED: {len(errors)} package errors")
        return 1
    print(f"PASS: {count} portable skills, matching catalog, and valid local documentation links")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
