# Claude Skills Roadmap

## Vision

成為 Claude CLI 生態中最值得收藏的 skill 集合，最終演化為跨 agent 的 skill 標準與 package manager。

## Phase 1: 旗艦 Skill（v0.2）

做 4 個殺手級「接線型」skill，每個解決一個 Claude CLI 呼叫外部工具的痛點。

| Skill | 說明 | 狀態 |
|-------|------|------|
| gh-issue-to-spec | GitHub Issue → 技術規格文件 | 🚧 |
| csv-to-chart | CSV/TSV → matplotlib 圖表 | 🚧 |
| db-eda | 自然語言查 SQLite/DuckDB | 🚧 |
| pdf-to-summary | PDF → 結構化摘要 | 🚧 |

## Phase 2: Skill Spec + Registry（v0.3）

- frontmatter 升級為正式規格（加 `required_bins`、`platforms`、`safety_level`）
- `tools/validate.py` — skill linter / validator
- `registry.json` — CI 自動從 frontmatter 生成
- 靜態 catalog site（GitHub Pages）
- 每個 skill 附 `examples/` 目錄

## Phase 3: CLI Package Manager（v0.4）

- `install.sh` 支援 `github:user/repo@ref/skill-name`
- 升級為 Node/TS CLI（`npx claude-skills install ...`）
- 搜尋、版本管理、trust model
- 支援多 agent surface（Claude CLI、Codex CLI、Gemini CLI）

## 策略依據

- **Codex（Engineer）**：先做內容再做 infra。bash 做不了真正的 PM，要做就升 Node/TS。第三條路（Skill Spec + Curated Registry）最有價值。
- **Gemini（Analyst）**：路線 B 有 Anthropic Sherlocking 風險。路線 A 是長尾 API 串接，官方不會做。擁抱 MCP 標準做避險。
- **共識**：先把 repo 做成值得收藏，再做成值得依賴。
