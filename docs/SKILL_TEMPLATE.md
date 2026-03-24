# Skill 範本

建立新 skill 時，複製此範本到 `skills/<skill-name>/SKILL.md`，填入內容。

```markdown
---
name: my-skill
description: 簡短描述這個 skill 做什麼。當用戶說「關鍵字A」「關鍵字B」時使用。
argument-hint: "[參數說明，或留空]"
allowed-tools: Bash(python3*), Read, Write
author: your-name
version: "1.0.0"
tags: [category1, category2]
required_env:
  - ENV_VAR_NAME
---

# Skill 名稱

## 目標

一句話說明這個 skill 要達成什麼。

## 前置條件檢查

在做任何事之前，檢查必要條件（API key、CLI 工具等）。
如果缺少，引導用戶取得。

## 流程

### Step 1: 確認輸入

根據 `$ARGUMENTS` 判斷用戶意圖。

### Step 2: 執行核心邏輯

（你的主要邏輯）

### Step 3: 展示結果

輸出結果給用戶確認。

## 常見問題

列出常見錯誤與解法。

## 注意事項

任何使用限制或安全提醒。
```

## 撰寫原則

1. **自給自足**：skill 不應依賴特定 MCP server 或本地工具，盡量用 Python stdlib 或 curl
2. **前置檢查**：第一步永遠是檢查環境變數 / 必要工具是否存在
3. **不含 credential**：禁止 hardcode API key，一律用環境變數
4. **英文 prompt**：如果涉及 AI 模型，prompt 用英文效果最好
5. **錯誤處理**：每個外部呼叫都要有錯誤提示和建議修復方式
