# 如何貢獻新 Skill

## 步驟

1. **Fork** 本 repo
2. 建立新分支：`git checkout -b skill/my-new-skill`
3. 在 `skills/` 下建立目錄：`mkdir skills/my-new-skill`
4. 複製 [SKILL_TEMPLATE.md](SKILL_TEMPLATE.md) 為 `skills/my-new-skill/SKILL.md`
5. 填寫 frontmatter 和內容
6. 更新 `README.md` 的 Skills 清單
7. 提交 PR

## Checklist（PR 前自查）

- [ ] `SKILL.md` frontmatter 包含所有必填欄位（name, description, allowed-tools, author, version, tags, required_env）
- [ ] `name` 和目錄名稱一致
- [ ] 沒有 hardcode 任何 credential（API key, token, password）
- [ ] 第一步是前置條件檢查（環境變數 / 工具是否存在）
- [ ] 有錯誤處理和使用者友善的錯誤訊息
- [ ] `README.md` 的 Skills 清單已更新
- [ ] 如果有 scripts/，都放在 skill 自己的目錄下

## 目錄結構

```
skills/my-new-skill/
├── SKILL.md            # 必要：skill 定義
├── scripts/            # 可選：複雜腳本
│   └── main.py
├── templates/          # 可選：範本檔案
└── references/         # 可選：參考資料
```

## 命名慣例

- 目錄名：`kebab-case`（例：`generate-image`、`sql-review`）
- 動詞開頭（例：`generate-image` 而非 `image-generator`）
- 簡短明確（2-3 個單字）

## 安全規則

1. **禁止 hardcode credential** — 用環境變數 + `required_env` 宣告
2. **危險操作要確認** — `rm`、`DROP`、`DELETE` 等操作前詢問用戶
3. **不要存取敏感路徑** — `~/.ssh`、`~/.gnupg`、`.env` 等
4. **外部 API 呼叫用 timeout** — 避免 hang 住
