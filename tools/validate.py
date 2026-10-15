#!/usr/bin/env python3
"""Claude Skills validator — 檢查 SKILL.md frontmatter 和結構完整性。"""

import sys
import ast
import re
import yaml
from pathlib import Path

REQUIRED_FIELDS = ["name", "description", "allowed-tools", "author", "version", "tags", "required_env"]
OPTIONAL_FIELDS = ["argument-hint", "required_bins", "platforms", "safety_level"]
VALID_SAFETY_LEVELS = ["safe", "cautious", "dangerous"]
VALID_PLATFORMS = ["macos", "linux", "windows"]

class ValidationError:
    def __init__(self, skill: str, level: str, msg: str):
        self.skill = skill
        self.level = level  # ERROR / WARN
        self.msg = msg

    def __str__(self):
        icon = "❌" if self.level == "ERROR" else "⚠️"
        return f"  {icon} [{self.level}] {self.msg}"


def parse_frontmatter(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return None
    try:
        parsed = yaml.safe_load(match.group(1))
        return parsed if isinstance(parsed, dict) else None
    except yaml.YAMLError:
        return None


def validate_skill(skill_dir: Path) -> list[ValidationError]:
    errors = []
    name = skill_dir.name
    skill_md = skill_dir / "SKILL.md"

    # 1. SKILL.md 存在
    if not skill_md.exists():
        errors.append(ValidationError(name, "ERROR", "SKILL.md not found"))
        return errors

    # 2. Frontmatter 可解析
    fm = parse_frontmatter(skill_md)
    if fm is None:
        errors.append(ValidationError(name, "ERROR", "Cannot parse YAML frontmatter"))
        return errors

    # 3. 必填欄位
    for field in REQUIRED_FIELDS:
        if field not in fm:
            errors.append(ValidationError(name, "ERROR", f"Missing required field: {field}"))

    # Validate types before len(), .get() consumers and registry generation.
    for field in ("name", "description", "author", "version"):
        if field in fm and (not isinstance(fm[field], str) or not fm[field].strip()):
            errors.append(ValidationError(name, "ERROR", f"{field} must be a non-empty string"))
    for field in ("tags", "required_env", "required_bins", "platforms"):
        if field in fm and (not isinstance(fm[field], list)
                            or any(not isinstance(item, str) or not item.strip()
                                   for item in fm[field])):
            errors.append(ValidationError(name, "ERROR", f"{field} must be a list of non-empty strings"))
    tools = fm.get("allowed-tools")
    if "allowed-tools" in fm and not (
        (isinstance(tools, str) and tools.strip())
        or (isinstance(tools, list) and tools
            and all(isinstance(item, str) and item.strip() for item in tools))
    ):
        errors.append(ValidationError(name, "ERROR", "allowed-tools must be a non-empty string or list"))
    if "disable-model-invocation" in fm and not isinstance(fm["disable-model-invocation"], bool):
        errors.append(ValidationError(name, "ERROR", "disable-model-invocation must be boolean"))
    if errors:
        return errors

    # 4. name 與目錄名一致
    if fm.get("name") and fm["name"] != name:
        errors.append(ValidationError(name, "ERROR",
            f"name '{fm['name']}' does not match directory '{name}'"))

    # 5. version 格式
    version = fm.get("version", "")
    if version and not re.match(r"^\d+\.\d+\.\d+$", str(version)):
        errors.append(ValidationError(name, "WARN",
            f"version '{version}' is not semver (expected X.Y.Z)"))

    # 6. tags 是 list
    tags = fm.get("tags")
    if tags is not None and not isinstance(tags, list):
        errors.append(ValidationError(name, "ERROR", "tags must be a list"))

    # 7. required_env 是 list
    req_env = fm.get("required_env")
    if req_env is not None and not isinstance(req_env, list):
        errors.append(ValidationError(name, "ERROR", "required_env must be a list"))

    # 8. safety_level 值檢查
    safety = fm.get("safety_level")
    if safety and safety not in VALID_SAFETY_LEVELS:
        errors.append(ValidationError(name, "WARN",
            f"safety_level '{safety}' not in {VALID_SAFETY_LEVELS}"))

    # 9. platforms 值檢查
    platforms = fm.get("platforms")
    if platforms:
        if not isinstance(platforms, list):
            errors.append(ValidationError(name, "ERROR", "platforms must be a list"))
        else:
            for p in platforms:
                if p not in VALID_PLATFORMS:
                    errors.append(ValidationError(name, "WARN",
                        f"platform '{p}' not in {VALID_PLATFORMS}"))

    # 10. description 長度
    desc = fm.get("description", "")
    if len(desc) > 200:
        errors.append(ValidationError(name, "WARN",
            f"description is {len(desc)} chars (recommend < 200)"))

    # 11. 內容檢查：有沒有 hardcode credential
    content = skill_md.read_text(encoding="utf-8")
    cred_patterns = [
        r'(?:sk-|ghp_|gho_|AIza)[A-Za-z0-9_-]{20,}',
        r'AKIA[0-9A-Z]{16}',
        r'xox[bpras]-[0-9A-Za-z-]{10,}',
        r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY',
        r'(?:password|secret|token|api_key|access_key|private_key|credential)\s*=\s*["\'](?!your|example|change|insert|replace)[^"\']{10,}["\']',
        r'(?:postgresql|mysql|mongodb(?:\+srv)?|redis)://[^@\s]{3,}@',
    ]
    for pattern in cred_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            errors.append(ValidationError(name, "ERROR",
                "Possible hardcoded credential detected"))

    # Parse bundled Python without executing it or creating bytecode files.
    for script in sorted(skill_dir.rglob("*.py")):
        try:
            ast.parse(script.read_text(encoding="utf-8"), filename=str(script))
        except (SyntaxError, UnicodeError) as exc:
            errors.append(ValidationError(name, "ERROR",
                f"Invalid Python script {script.relative_to(skill_dir)}: {type(exc).__name__}"))

    # 12. 有 Quality Gates 段落
    if "## Quality Gates" not in content and "## Quality" not in content:
        errors.append(ValidationError(name, "WARN", "No Quality Gates section"))

    return errors


def main():
    skills_dir = Path(__file__).parent.parent / "skills"
    if not skills_dir.exists():
        print("ERROR: skills/ directory not found")
        sys.exit(1)

    skill_dirs = sorted([d for d in skills_dir.iterdir() if d.is_dir()])
    if not skill_dirs:
        print("ERROR: No skills found in skills/")
        sys.exit(1)

    total_errors = 0
    total_warns = 0

    for skill_dir in skill_dirs:
        errors = validate_skill(skill_dir)
        errs = [e for e in errors if e.level == "ERROR"]
        warns = [e for e in errors if e.level == "WARN"]

        if errors:
            status = "FAIL" if errs else "WARN"
            print(f"\n{'❌' if errs else '⚠️'} {skill_dir.name} — {status}")
            for e in errors:
                print(e)
        else:
            print(f"✅ {skill_dir.name} — PASS")

        total_errors += len(errs)
        total_warns += len(warns)

    # Summary
    print(f"\n{'='*40}")
    print(f"Skills: {len(skill_dirs)} | Errors: {total_errors} | Warnings: {total_warns}")

    if total_errors > 0:
        print("VALIDATION FAILED")
        sys.exit(1)
    else:
        print("VALIDATION PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
