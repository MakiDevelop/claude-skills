---
name: postmortem
description: 事故記錄。收集資訊、分析 root cause、記錄修復步驟、防止再發。當服務出事故後使用。
argument-hint: "[事故簡述，如 '網站掛了兩小時' / 'deploy 後 API 500']"
allowed-tools: Bash(git*), Read, Write, Grep, Glob
author: Maki
version: "1.0.0"
tags: [devops, incident, debugging, documentation]
required_env: []
---

# 事故記錄（Postmortem）

## 目標

快速記錄事故，結構化分析 root cause，防止重複犯錯。

## 流程

### Step 1: 收集資訊

詢問用戶（或從上下文取得）：
- 什麼壞了？
- 什麼時候發現的？
- 影響範圍？（用戶數、持續時間、資料損失？）

### Step 2: 分析 root cause

- 觸發的命令或操作
- 錯誤訊息
- 為什麼會走到這一步（5 Whys）

若有 repo，自動檢查：
- `git log --oneline -10` 看最近改動
- 搜尋相關錯誤訊息

### Step 3: 記錄修復步驟

- 怎麼修好的
- 花了多久
- 是否有 workaround 還是根本修復

### Step 4: 寫入檔案

追加到當前專案的 `logs/errors.md`（沒有就建立），格式：

```markdown
## YYYY-MM-DD: [簡述問題]

**影響**：[影響範圍和持續時間]
**觸發**：[什麼操作觸發的]
**錯誤**：[錯誤訊息]
**Root Cause**：[根本原因]
**修復**：[修復步驟]
**防止再發**：[應該怎麼避免]
**Timeline**：
- HH:MM 發現問題
- HH:MM 開始修復
- HH:MM 恢復正常
```

### Step 5: 提出預防建議

- 如果這類問題之前發生過，指出來
- 建議加入自動化防護（CI check、monitoring、alert）
- 建議更新文件（CLAUDE.md、README、runbook）

## Quality Gates

- [ ] Root cause 不是「設定錯誤」這種表面原因，要挖到為什麼會設定錯誤
- [ ] 修復步驟可重現（別人照做也能修）
- [ ] 防止再發有具體動作（不是「以後注意」）
- [ ] Timeline 完整（從發現到恢復）

## Heuristics

- 事故後 24 小時內記錄，記憶最清楚
- Root cause 用 5 Whys：問五次「為什麼」才算到底
- 防止再發優先考慮自動化（人的注意力不可靠）
- Blameless：記錄事實和流程，不指責個人
