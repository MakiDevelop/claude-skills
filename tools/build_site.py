#!/usr/bin/env python3
"""從 registry.json 生成靜態 catalog site（docs/index.html）。"""

import json
from html import escape
from pathlib import Path
from datetime import datetime

REPO_URL = "https://github.com/MakiDevelop/claude-skills"


def build_site():
    repo_root = Path(__file__).parent.parent
    registry = json.loads((repo_root / "registry.json").read_text())
    skills = registry["skills"]

    # 按 tag 分組
    categories = {}
    tag_to_category = {
        "image": "AI / 圖像生成",
        "gemini": "AI / 圖像生成",
        "ai": "AI / 圖像生成",
        "diagram": "視覺化 / 文件",
        "drawio": "視覺化 / 文件",
        "architecture": "視覺化 / 文件",
        "svg": "視覺化 / 文件",
        "html": "視覺化 / 文件",
        "blog": "視覺化 / 文件",
        "documentation": "視覺化 / 文件",
        "data": "資料分析",
        "visualization": "資料分析",
        "database": "資料分析",
        "csv": "資料分析",
        "sqlite": "資料分析",
        "duckdb": "資料分析",
        "eda": "資料分析",
        "pdf": "資料分析",
        "github": "開發工具",
        "spec": "開發工具",
        "devops": "開發工具",
        "incident": "開發工具",
        "debugging": "開發工具",
        "career": "職涯 / 溝通",
        "interview": "職涯 / 溝通",
        "linkedin": "職涯 / 溝通",
        "presentation": "職涯 / 溝通",
        "demo": "職涯 / 溝通",
        "storytelling": "職涯 / 溝通",
        "product": "職涯 / 溝通",
        "marketing": "職涯 / 溝通",
        "positioning": "職涯 / 溝通",
        "pitch": "職涯 / 溝通",
        "proposal": "職涯 / 溝通",
        "review": "職涯 / 溝通",
        "macos": "系統維護",
        "cleanup": "系統維護",
        "disk": "系統維護",
    }

    for skill in skills:
        cat = "其他"
        for tag in skill["tags"]:
            if tag in tag_to_category:
                cat = tag_to_category[tag]
                break
        categories.setdefault(cat, []).append(skill)

    # 生成 HTML
    cards_html = ""
    for cat_name in ["AI / 圖像生成", "視覺化 / 文件", "資料分析", "開發工具", "職涯 / 溝通", "系統維護", "其他"]:
        cat_skills = categories.get(cat_name, [])
        if not cat_skills:
            continue
        cards_html += f'<h2 class="cat">{escape(cat_name)}</h2>\n<div class="grid">\n'
        for s in cat_skills:
            tags_html = " ".join(f'<span class="tag">{escape(t)}</span>' for t in s["tags"])
            env_html = ""
            if s["required_env"]:
                env_html = f'<div class="env">需要: {escape(", ".join(s["required_env"]))}</div>'
            raw_desc = s["description"]
            desc = escape(raw_desc.split("。")[0] + "。" if "。" in raw_desc else raw_desc)
            name_esc = escape(s["name"])
            ver_esc = escape(s["version"])
            path_esc = escape(s["path"])
            cards_html += f"""<div class="card">
  <h3><a href="{REPO_URL}/blob/main/{path_esc}">{name_esc}</a> <span class="ver">v{ver_esc}</span></h3>
  <p>{desc}</p>
  <div class="meta">{tags_html}</div>
  {env_html}
  <code>install.sh install {name_esc}</code>
</div>
"""
        cards_html += "</div>\n"

    html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Claude Skills Catalog</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
       background: #0a0a0a; color: #e0e0e0; padding: 2rem; max-width: 1200px; margin: 0 auto; }}
h1 {{ font-size: 2rem; margin-bottom: 0.5rem; color: #fff; }}
.subtitle {{ color: #888; margin-bottom: 2rem; }}
.stats {{ color: #666; font-size: 0.85rem; margin-bottom: 2rem; }}
h2.cat {{ font-size: 1.2rem; color: #aaa; margin: 2rem 0 1rem; border-bottom: 1px solid #222; padding-bottom: 0.5rem; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1rem; }}
.card {{ background: #151515; border: 1px solid #252525; border-radius: 8px; padding: 1.2rem;
         transition: border-color 0.2s; }}
.card:hover {{ border-color: #444; }}
.card h3 {{ font-size: 1rem; margin-bottom: 0.5rem; }}
.card h3 a {{ color: #58a6ff; text-decoration: none; }}
.card h3 a:hover {{ text-decoration: underline; }}
.ver {{ font-size: 0.75rem; color: #555; font-weight: normal; }}
.card p {{ font-size: 0.9rem; color: #aaa; margin-bottom: 0.8rem; line-height: 1.4; }}
.meta {{ margin-bottom: 0.5rem; }}
.tag {{ display: inline-block; font-size: 0.7rem; background: #1a2332; color: #58a6ff;
        padding: 2px 8px; border-radius: 12px; margin: 2px 2px; }}
.env {{ font-size: 0.8rem; color: #d29922; margin-bottom: 0.5rem; }}
code {{ display: block; font-size: 0.8rem; background: #1a1a1a; color: #7ee787; padding: 6px 10px;
        border-radius: 4px; font-family: 'SF Mono', Consolas, monospace; }}
.install {{ background: #151515; border: 1px solid #252525; border-radius: 8px; padding: 1.5rem;
            margin-bottom: 2rem; }}
.install h2 {{ font-size: 1rem; margin-bottom: 0.8rem; color: #fff; }}
.install code {{ margin-bottom: 0.5rem; }}
footer {{ margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #222; color: #555; font-size: 0.8rem; }}
</style>
</head>
<body>
<h1>Claude Skills</h1>
<p class="subtitle">可重用的 Claude CLI 技能包分享平台</p>
<p class="stats">{len(skills)} skills | Generated {datetime.now().strftime('%Y-%m-%d')}</p>

<div class="install">
<h2>Quick Install</h2>
<code>git clone {REPO_URL}.git ~/.claude/repos/claude-skills</code>
<code>~/.claude/repos/claude-skills/tools/install.sh install --all</code>
</div>

{cards_html}

<footer>
<a href="{REPO_URL}" style="color:#58a6ff">GitHub</a> ·
<a href="{REPO_URL}/blob/main/docs/CONTRIBUTING.md" style="color:#58a6ff">Contribute</a> ·
MIT License
</footer>
</body>
</html>"""

    docs_dir = repo_root / "docs"
    docs_dir.mkdir(exist_ok=True)
    (docs_dir / "index.html").write_text(html, encoding="utf-8")
    print(f"Generated docs/index.html ({len(skills)} skills)")


if __name__ == "__main__":
    build_site()
