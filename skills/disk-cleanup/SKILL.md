---
name: disk-cleanup
description: macOS 磁碟清理。掃描大目錄、分類可刪/可搬/需確認、Docker/Xcode 清理。當用戶說「清磁碟」「磁碟空間不夠」「disk cleanup」時使用。
allowed-tools: Bash(du*), Bash(df*), Bash(ls*), Bash(docker*), Bash(xcrun*), Bash(diskutil*), Bash(tmutil*), Bash(find*), Read
author: Maki
version: "1.0.0"
tags: [macos, devtools, cleanup, disk]
required_env: []
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

報告：APFS 實際可用空間（注意 Finder 數字含 purgeable，不準確）。

### Step 2：掃描大目錄

```bash
du -sh ~/Documents ~/Downloads ~/Movies ~/GitHub ~/GitLab ~/Projects ~/.cache ~/Library/Caches ~/Library/Developer ~/Library/Containers 2>/dev/null | sort -rh
```

對 > 5GB 的目錄進一步展開子目錄。

### Step 3：分類

將找到的項目分成三類，用表格呈現：

| 類別 | 說明 | 需確認 |
|------|------|--------|
| **可安全刪除** | cache、.venv、node_modules、DerivedData、__pycache__、.ruff_cache | 自動列出，確認後刪 |
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

列出可刪的舊版本（保留最新兩個），用戶確認後執行。

### Step 6：Python venvs

掃描所有 .venv 和 virtualenvs：
```bash
find ~ -maxdepth 4 -type d -name ".venv" -o -name "venv" 2>/dev/null
```

### Step 7：Time Machine 本機快照

```bash
tmutil listlocalsnapshots /
```

若快照過多（> 10 個），建議清理。

### Step 8：結果報告

```
## 磁碟清理報告

**清理前**: APFS free {X}GB
**可回收空間**:
- 可安全刪除: {X}GB
- 可搬到外接: {X}GB
- Docker: {X}GB
- Xcode: {X}GB

### 建議操作（需你確認）:
1. ...
2. ...
```

## 注意

- 所有刪除操作前必須讓用戶確認
- 不要刪 .env、credentials、SSH key 等敏感檔案
- 掃描不應超過 60 秒
- 此 skill 僅適用 macOS
