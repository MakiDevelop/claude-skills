#!/usr/bin/env python3
"""從 skills/*/SKILL.md frontmatter 自動生成 registry.json。"""

import json
import re
import yaml
from datetime import datetime, timezone
from pathlib import Path


def parse_frontmatter(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return None
    try:
        return yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None


def build_registry():
    repo_root = Path(__file__).parent.parent
    skills_dir = repo_root / "skills"
    skills = []

    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue

        fm = parse_frontmatter(skill_md)
        if fm is None:
            continue

        skills.append({
            "name": fm.get("name", skill_dir.name),
            "description": fm.get("description", ""),
            "version": str(fm.get("version", "0.0.0")),
            "author": fm.get("author", "unknown"),
            "tags": fm.get("tags", []),
            "required_env": fm.get("required_env", []),
            "required_bins": fm.get("required_bins", []),
            "platforms": fm.get("platforms", ["macos", "linux", "windows"]),
            "safety_level": fm.get("safety_level", "safe"),
            "path": f"skills/{skill_dir.name}/SKILL.md",
        })

    registry = {
        "version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "skill_count": len(skills),
        "skills": skills,
    }

    out_path = repo_root / "registry.json"
    out_path.write_text(
        json.dumps(registry, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Generated registry.json with {len(skills)} skills")


if __name__ == "__main__":
    build_registry()
