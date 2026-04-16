# Claude Skills

> Power-ups for Claude Code.

![Validate Skills](https://github.com/MakiDevelop/claude-skills/actions/workflows/validate.yml/badge.svg)
![Skills: 16](https://img.shields.io/badge/skills-16-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

Reusable skill packs for **[Claude Code](https://claude.ai/claude-code)** CLI. Install once, use everywhere — from data analysis to image generation to career tools.

## Quickstart

### Install all skills

```bash
git clone https://github.com/MakiDevelop/claude-skills.git ~/.claude/repos/claude-skills
~/.claude/repos/claude-skills/tools/install.sh install --all
```

### Install a single skill

```bash
# Clone first (if not already)
git clone https://github.com/MakiDevelop/claude-skills.git ~/.claude/repos/claude-skills

# Install a specific skill
~/.claude/repos/claude-skills/tools/install.sh install generate-image
```

### Update

```bash
~/.claude/repos/claude-skills/tools/install.sh update
```

## Available Skills (16)

### AI / Image Generation

| Skill | Description | Env Vars |
|-------|-------------|----------|
| [generate-image](skills/generate-image/) | Generate images with Gemini Nano Banana 2 | `GEMINI_API_KEY` |

### Data Analysis

| Skill | Description | Env Vars |
|-------|-------------|----------|
| [csv-to-chart](skills/csv-to-chart/) | CSV/TSV → auto chart (line/bar/pie/scatter) | — |
| [db-eda](skills/db-eda/) | Natural language queries for SQLite / DuckDB (read-only) | — |
| [pdf-to-summary](skills/pdf-to-summary/) | PDF → structured summary with page references | — |

### Developer Tools

| Skill | Description | Env Vars |
|-------|-------------|----------|
| [gh-issue-to-spec](skills/gh-issue-to-spec/) | GitHub Issue → technical spec document | — |
| [postmortem](skills/postmortem/) | Incident report + root cause analysis + prevention | — |

### Diagrams / Documentation

| Skill | Description | Env Vars |
|-------|-------------|----------|
| [drawio](skills/drawio/) | Generate .drawio files (editable) with optional PNG/SVG/PDF export | — |
| [architecture-diagram](skills/architecture-diagram/) | Self-contained HTML architecture diagrams (inline SVG, dark theme) for blogs/READMEs | — |

### Strategy & Communication

| Skill | Description | Env Vars |
|-------|-------------|----------|
| [case-study](skills/case-study/) | Package projects into case studies (interview/LinkedIn/portfolio) | — |
| [cv-optimize](skills/cv-optimize/) | Resume optimization with targeted positioning | — |
| [demo-storytelling](skills/demo-storytelling/) | Turn PoC into a compelling demo story | — |
| [product-positioning](skills/product-positioning/) | Product market positioning + pitch strategy | — |
| [proposal-review](skills/proposal-review/) | Presentation structure review (slides/titles/content balance) | — |
| [roundtable](skills/roundtable/) | Virtual expert roundtable — multiple thinkers analyze your document | — |
| [vendor-eval](skills/vendor-eval/) | Vendor proposal evaluation (tech/cost/market/background) | — |

### System Maintenance

| Skill | Description | Env Vars |
|-------|-------------|----------|
| [disk-cleanup](skills/disk-cleanup/) | macOS disk cleanup (Docker/Xcode/venv/cache) | — |

## How it works

Each skill is a single `SKILL.md` file with YAML frontmatter defining metadata, required tools, and the skill logic itself. The installer creates symlinks in your `~/.claude/commands/` directory.

```
skills/
└── generate-image/
    └── SKILL.md          # Frontmatter + skill logic

tools/
├── install.sh            # Install / update / remove
├── validate.py           # CI validation
├── build_registry.py     # Auto-generate registry.json
└── build_site.py         # Auto-generate catalog site
```

CI automatically validates all skills on push and rebuilds the registry.

## Contributing

1. Fork this repo
2. Create a new directory under `skills/` with a `SKILL.md`
3. Follow the [Skill Template](docs/SKILL_TEMPLATE.md) format
4. Submit a PR

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for details.

## Skill Frontmatter Spec

```yaml
---
name: skill-name              # Unique ID (same as directory name)
description: One-line desc    # Purpose + trigger keywords
argument-hint: "[args]"       # Optional argument hint
allowed-tools: Bash(...), Read # Required tool permissions
author: your-name
version: "1.0.0"
tags: [image, gemini]
required_env:
  - GEMINI_API_KEY
---
```

## License

MIT
