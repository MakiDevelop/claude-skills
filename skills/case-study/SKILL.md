---
name: case-study
description: 專案案例包裝。把真實專案包裝成面試/LinkedIn 用的結構化案例（問題→方案→架構→Tech Stack→成果→展示重點）。當用戶說「包裝案例」「寫 case study」「面試用的案例」時使用。
argument-hint: "[專案名稱或 repo 路徑]"
allowed-tools: Read, Grep, Glob, Bash(git*), Bash(cloc*), Bash(find*), Bash(wc*)
author: Maki
version: "1.0.0"
tags: [career, interview, linkedin, writing]
required_env: []
---

# 專案案例包裝

## 目標

把一個真實專案包裝成結構化的案例包，可直接用於面試、LinkedIn、或作品集。

## 與其他 Skill 的差異

- `demo-storytelling`：PoC → 演示腳本（給觀眾看的故事）
- `case-study`：完整專案 → 結構化案例（給面試官/讀者的事實）
- `product-positioning`：產品 → 市場定位（給客戶的訊息）

## 輸入

從 `$ARGUMENTS` 或對話中取得：

| 欄位 | 必填 | 說明 |
|------|------|------|
| 專案名稱 | 是 | 名稱或 repo 路徑 |
| 目標用途 | 否 | 預設：面試 + LinkedIn 雙用 |
| 受眾 | 否 | 預設：技術主管 / HR / 資深工程師 |

若缺專案名稱，問用戶。

## 資訊收集流程

### Step 1: 自動偵測專案資訊

若提供 repo 路徑：
1. 讀 README.md / CLAUDE.md
2. `git log --oneline -20` 看開發歷史
3. `git log --oneline --since="6 months ago" | wc -l` 算活躍度
4. Glob 看主要檔案結構

若只提供名稱：
1. 問用戶補充背景資訊

### Step 2: 量化指標挖掘

主動嘗試取得以下數字（能自動抓就抓，不能就標 `_（待填）_`）：

- 程式碼統計：`cloc` 或 `find . -name "*.py" | wc -l`
- 測試數：`grep -r "def test_" | wc -l`
- 部署環境數
- 服務使用者數（問用戶）
- 效能改善數字（問用戶）
- 節省時間/成本（問用戶）

### Step 3: 問用戶補充

自動收集完後，列出缺少的關鍵數字，一次問完：

```
以下數字我無法自動取得，請補充（沒有的寫「無」）：
1. 服務使用者數：
2. 每日/月處理量：
3. 節省的時間或成本：
4. 其他你想強調的成果：
```

## 輸出格式

```markdown
# 案例：{專案名} — {一句話定位}

> 面試 / LinkedIn 用案例包

## 問題

{2-3 個 bullet，描述要解決什麼問題}

## 解決方案

{方案概述 + 3-4 個關鍵設計決策}

## 技術架構

{ASCII 或文字描述的架構圖}

## Technology Stack

| 層級 | 技術 |
|------|------|
| ... | ... |

## 成果

{帶數字的成果列表}

## 展示重點（面試時強調）

1. **{能力標籤}**：{一句話說明}
2. ...
3. ...
4. ...
```

## Quality Gates

- [ ] 問題描述是業務痛點，不是技術描述
- [ ] 架構圖清晰可懂（非工程師也能看懂大致結構）
- [ ] Tech Stack 表完整（每一層都有）
- [ ] 成果有至少 2 個數字（沒有 = 不及格）
- [ ] 展示重點對應市場需求（Product 思維 / Engineering / AI 實戰）
- [ ] 沒有公司機密或敏感資訊

## Heuristics

- 問題描述用「用戶/團隊遇到什麼困難」，不用「我想做一個...」
- 成果數字優先用相對值（「降低 97%」比「從 90s 到 3s」更直覺）
- 展示重點最多 4 個，太多 = 沒重點
- 如果專案太小不值得包裝 → 告訴用戶，建議合併到其他案例
