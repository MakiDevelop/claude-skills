---
name: gh-issue-to-spec
description: 把 GitHub Issue 轉成結構化技術規格文件。當用戶說「issue 轉 spec」「寫規格」「gh issue to spec」時使用。
argument-hint: "[Issue URL 或 #number，如 'https://github.com/org/repo/issues/42' 或 '#42']"
allowed-tools: Bash(gh*), Bash(git*), Read, Write, Grep, Glob
author: Maki
version: "1.0.0"
tags: [github, spec, documentation, development]
required_env: []
---

# GitHub Issue → 技術規格文件

## 目標

讀取 GitHub Issue（含 comments、linked PRs、labels），自動產出結構化的技術規格文件，可直接用於開發。

## 前置條件

### 檢查 gh CLI

```bash
gh auth status
```

- **已登入** → 繼續
- **未登入** → 提示用戶：
```
需要安裝並登入 GitHub CLI：
1. 安裝：brew install gh
2. 登入：gh auth login
```

## 流程

### Step 1: 取得 Issue 資訊

根據 `$ARGUMENTS` 判斷：

- **完整 URL** → 直接解析 owner/repo/number
- **#number** → 從當前 repo 的 `git remote` 推斷 owner/repo
- **空** → 問用戶提供 Issue URL 或 number

```bash
# 取得 Issue 本體
gh issue view {number} --repo {owner}/{repo} --json title,body,labels,assignees,milestone,state,createdAt,comments

# 取得關聯的 PR
gh pr list --repo {owner}/{repo} --search "#{number}" --json number,title,state,url

# 取得 Issue timeline（誰做了什麼）
gh api repos/{owner}/{repo}/issues/{number}/timeline --paginate
```

### Step 2: 分析 Issue 內容

從 Issue body + comments 中提取：

| 要素 | 來源 | 備註 |
|------|------|------|
| 問題描述 | Issue body | 原始需求 |
| 接受標準 | body 中的 checklist / "Acceptance Criteria" | 常見格式 |
| 技術討論 | comments | 設計決策、替代方案 |
| 約束條件 | labels + comments | 如 `breaking-change`、`performance` |
| 關聯 PR | linked PRs | 可能已有部分實作 |

### Step 3: 自動偵測 repo context

```bash
# 讀取 README 取得專案概要
gh api repos/{owner}/{repo}/readme --jq '.content' | base64 -d | head -50

# 讀取技術棧線索
gh api repos/{owner}/{repo}/languages
```

### Step 4: 產出技術規格

```markdown
# Spec: {Issue Title}

> Source: {Issue URL}
> Author: {Issue Author} | Created: {Date} | Labels: {Labels}

## 1. 問題陳述

{從 Issue body 提煉的問題描述，2-3 句}

## 2. 目標

{要達成什麼，用可驗證的語句}

## 3. 接受標準

- [ ] {從 Issue 提取或推斷的驗收條件}
- [ ] {每條都是可測試的}

## 4. 技術方案

### 4.1 方案概述

{基於 Issue 討論的技術方案}

### 4.2 影響範圍

- 需要修改的檔案/模組
- 需要新增的檔案/模組
- 可能影響的既有功能

### 4.3 替代方案

{如果 comments 中有討論過的替代方案，列出}

## 5. 約束與風險

- {從 labels 和 comments 中提取的約束}
- {潛在風險}

## 6. 測試計畫

- [ ] {Unit test 項目}
- [ ] {Integration test 項目}
- [ ] {Edge case}

## 7. 參考

- Issue: {URL}
- Related PRs: {URLs}
- {其他 comments 中提到的參考資料}
```

### Step 5: 輸出與儲存

1. 將規格文件顯示給用戶
2. 詢問是否儲存：
   - 預設路徑：`docs/specs/issue-{number}-{slug}.md`
   - 或用戶指定路徑
3. 詢問是否要在 Issue 上留 comment 附上 spec 連結

## Quality Gates

- [ ] 問題陳述是用戶語言，不是技術語言
- [ ] 接受標準每條都可測試（不是「改善效能」而是「回應時間 < 200ms」）
- [ ] 技術方案有影響範圍分析
- [ ] 沒有遺漏 Issue comments 中的重要討論
- [ ] 測試計畫涵蓋 happy path + edge case

## Heuristics

- Issue 只有一行 → 先問用戶補充，不要硬猜
- Issue 有 20+ comments → 重點摘要討論結論，不要全部列出
- 有 linked PR 且已 merged → 標註「部分已實作」
- Label 有 `bug` → 加入 root cause 分析段落
- Label 有 `breaking-change` → 加入 migration plan 段落
