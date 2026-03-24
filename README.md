# Claude Skills

可重用的 Claude CLI 技能包（Skills）分享平台。

## 快速開始

### 安裝全部 Skills

```bash
git clone https://github.com/MakiDevelop/claude-skills.git ~/.claude/repos/claude-skills
~/.claude/repos/claude-skills/tools/install.sh install --all
```

### 安裝單一 Skill

```bash
# 如果還沒 clone
git clone https://github.com/MakiDevelop/claude-skills.git ~/.claude/repos/claude-skills

# 安裝指定 skill
~/.claude/repos/claude-skills/tools/install.sh install generate-image
```

### 更新 Skills

```bash
~/.claude/repos/claude-skills/tools/install.sh update
```

## Skills 清單

### AI / 圖像生成

| Skill | 說明 | 需要的環境變數 |
|-------|------|---------------|
| [generate-image](skills/generate-image/) | 使用 Gemini Nano Banana 2 產生圖片 | `GEMINI_API_KEY` |

### 職涯 / 溝通

| Skill | 說明 | 需要的環境變數 |
|-------|------|---------------|
| [case-study](skills/case-study/) | 專案案例包裝（面試 / LinkedIn / 作品集） | — |
| [demo-storytelling](skills/demo-storytelling/) | PoC 包裝成有說服力的 demo 故事 | — |
| [product-positioning](skills/product-positioning/) | 產品市場定位 + pitch 策略 | — |

### DevOps / 工具

| Skill | 說明 | 需要的環境變數 |
|-------|------|---------------|
| [postmortem](skills/postmortem/) | 事故記錄 + root cause 分析 + 防止再發 | — |
| [proposal-review](skills/proposal-review/) | 提案簡報結構審查（分頁/標題/內容分配） | — |
| [disk-cleanup](skills/disk-cleanup/) | macOS 磁碟清理（Docker/Xcode/venv/cache） | — |

## 目錄結構

```
claude-skills/
├── skills/                 # 所有 skills（一個目錄一個 skill）
│   └── generate-image/
│       └── SKILL.md
├── tools/
│   └── install.sh          # 安裝/更新/移除腳本
├── docs/
│   ├── CONTRIBUTING.md     # 如何貢獻新 skill
│   └── SKILL_TEMPLATE.md   # Skill 範本
└── README.md
```

## 貢獻新 Skill

1. Fork 本 repo
2. 在 `skills/` 下建立新目錄，包含 `SKILL.md`
3. 遵循 [Skill 範本](docs/SKILL_TEMPLATE.md) 的 frontmatter 格式
4. 提交 PR，至少一人 review

詳見 [CONTRIBUTING.md](docs/CONTRIBUTING.md)。

## Skill Frontmatter 規範

每個 `SKILL.md` 的 YAML frontmatter 必須包含：

```yaml
---
name: skill-name              # 唯一識別碼（同目錄名）
description: 一行描述          # 用途說明 + 觸發關鍵字
argument-hint: "[參數說明]"    # 可選參數提示
allowed-tools: Bash(...), Read # 需要的工具權限
author: your-name              # 作者
version: "1.0.0"               # 語意化版本
tags: [image, gemini]          # 分類標籤
required_env:                  # 需要的環境變數（空陣列表示無）
  - GEMINI_API_KEY
---
```

## License

MIT
