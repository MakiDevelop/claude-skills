---
name: disk-cleanup
description: macOS 磁碟清理。掃描大目錄、分類可刪/可搬/需確認、Docker/Xcode 清理。當用戶說「清磁碟」「磁碟空間不夠」「disk cleanup」時使用。
allowed-tools: Read, Bash(du *), Bash(df *), Bash(ls *), Bash(docker system df*), Bash(xcrun simctl runtime list*), Bash(diskutil apfs list*), Bash(tmutil listlocalsnapshots*), Bash(find *)
author: Maki
version: "1.1.0"
tags: [macos, devtools, cleanup, disk]
required_env: []
required_bins: []
platforms: [macos]
safety_level: cautious
disable-model-invocation: true
---

# macOS 磁碟清理

一鍵掃描磁碟用量，分類建議，協助清理空間。

## 流程

### Step 1：總覽

同時執行：

```bash
df -h /
diskutil apfs list | grep -E "Capacity In Use|Capacity Not Allocated" | head -2
```

分別報告 df 與 APFS 容量及觀測時間；Finder 可能含可清除空間，不將不同定義混成同一個數字。

### Step 2：掃描大目錄

```bash
du -sh ~/Documents ~/Downloads ~/Movies ~/GitHub ~/GitLab ~/Projects ~/.cache ~/Library/Caches ~/Library/Developer ~/Library/Containers 2>/dev/null | sort -rh
```

對 > 5GB 的目錄進一步展開子目錄。

### Step 3：分類

將找到的項目分成三類，用表格呈現：

| 類別 | 說明 | 需確認 |
|------|------|--------|
| **可評估重建** | cache、.venv、node_modules、DerivedData、__pycache__、.ruff_cache | 確認用途與重建成本；只提供清單 |
| **可搬到外接** | 大型模型、VM、DMG、影片、舊專案 | 列出後問用戶 |
| **需確認** | 不確定用途的大目錄 | 問用戶 |

### Step 4：Docker 清理

```bash
docker system df
```

若有可回收空間，建議 `docker system prune`（需用戶確認）。

### Step 5：Xcode 清理

檢查：
```bash
xcrun simctl runtime list                    # Simulator runtimes
ls ~/Library/Developer/Xcode/iOS\ DeviceSupport/   # DeviceSupport
du -sh ~/Library/Developer/Xcode/DerivedData        # DerivedData
du -sh /Library/Developer/CoreSimulator             # CoreSimulator 總量
```

列出候選舊版本與相依專案；不得假設最新兩版足夠。只提供操作草案，由用戶自行清理。

### Step 6：Python venvs

掃描所有 .venv 和 virtualenvs：
```bash
find "$HOME" -maxdepth 4 -type d \( -name ".venv" -o -name "venv" \) -prune 2>/dev/null
```

### Step 7：Time Machine 本機快照

```bash
tmutil listlocalsnapshots /
```

列出快照日期與用量資訊；數量本身不是刪除理由，不自動清除備份。

### Step 8：結果報告

```
## 磁碟清理報告

**清理前**: APFS free {X}GB
**可回收空間**:
- 候選重建項目（未刪除）: {X}GB
- 可搬到外接: {X}GB
- Docker: {X}GB
- Xcode: {X}GB

### 建議操作（需你確認）:
1. ...
2. ...
```

## 注意

- 本 skill 僅掃描與提出建議，不執行刪除、prune、跨磁碟搬移或快照清理。危險命令只提供草案，由用戶自行執行。
- 不要刪 .env、credentials、SSH key 等敏感檔案
- 掃描不應超過 60 秒
- 此 skill 僅適用 macOS

## Quality Gates

- [ ] 掃描限於用戶指定位置；避免跨磁碟與全家目錄無界掃描。
- [ ] 權限錯誤、未掃描範圍與逾時明確標記。
- [ ] 可回收為估計值；沒有執行操作就不宣稱已釋放空間。
- [ ] 不執行任何刪除命令，也不因 allowed-tools pattern 而推定已獲破壞性操作授權。
