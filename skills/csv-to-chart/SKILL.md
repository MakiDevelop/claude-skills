---
name: csv-to-chart
description: 把 CSV/TSV 資料自動生成圖表（line/bar/pie/scatter）。當用戶說「畫圖表」「csv 圖表」「chart」「visualize data」時使用。
argument-hint: "[CSV/TSV 檔案路徑]"
allowed-tools: Bash(python3*), Bash(pip3*), Read, Write
author: Maki
version: "1.0.0"
tags: [data, visualization, chart, csv]
required_env: []
---

# CSV/TSV → 圖表生成器

## 目標

讀取 CSV/TSV 檔案，自動偵測欄位類型，推薦並生成合適的圖表，存為 PNG。

## 前置條件

### 檢查 matplotlib

```bash
python3 -c "import matplotlib; print(f'matplotlib {matplotlib.__version__}')" 2>/dev/null || echo "NOT_FOUND"
```

- **找到** → 繼續
- **沒找到** → 告訴用戶：
```
需要安裝 matplotlib：
pip3 install matplotlib

或者我可以幫你安裝（需確認）。
```

## 流程

### Step 1: 讀取並分析資料

```bash
python3 << 'PYEOF'
import csv, sys, json, re
from datetime import datetime

FILE_PATH = "USER_FILE_PATH"

with open(FILE_PATH, 'r', encoding='utf-8') as f:
    dialect = csv.Sniffer().sniff(f.read(4096))
    f.seek(0)
    reader = csv.DictReader(f, dialect=dialect)
    rows = list(reader)

if not rows:
    print("ERROR: Empty file")
    sys.exit(1)

columns = list(rows[0].keys())
print(f"Rows: {len(rows)}")
print(f"Columns: {columns}")

# 欄位類型偵測
date_re = re.compile(r'^\d{4}[-/]\d{1,2}[-/]\d{1,2}')
col_types = {}
for col in columns:
    samples = [r[col] for r in rows[:10] if r[col]]
    if not samples:
        col_types[col] = "empty"
    elif all(date_re.match(s) for s in samples):
        col_types[col] = "date"
    else:
        try:
            [float(s.replace(',', '')) for s in samples]
            col_types[col] = "numeric"
        except ValueError:
            unique = len(set(r[col] for r in rows if r[col]))
            col_types[col] = "category" if unique <= 20 else "text"

print(f"Column types: {json.dumps(col_types, ensure_ascii=False)}")

# 推薦圖表
dates = [c for c, t in col_types.items() if t == "date"]
nums = [c for c, t in col_types.items() if t == "numeric"]
cats = [c for c, t in col_types.items() if t == "category"]

if dates and nums:
    print(f"RECOMMEND: line (x={dates[0]}, y={nums})")
elif cats and nums:
    if len(set(r[cats[0]] for r in rows)) <= 6:
        print(f"RECOMMEND: pie (labels={cats[0]}, values={nums[0]})")
    else:
        print(f"RECOMMEND: bar (x={cats[0]}, y={nums[0]})")
elif len(nums) >= 2:
    print(f"RECOMMEND: scatter (x={nums[0]}, y={nums[1]})")
elif nums:
    print(f"RECOMMEND: bar (x=index, y={nums[0]})")
else:
    print("RECOMMEND: table (no numeric data for charting)")
PYEOF
```

### Step 2: 確認圖表設定

向用戶展示分析結果，確認：

1. 圖表類型（可覆寫推薦）
2. X/Y 軸欄位
3. 標題
4. 輸出檔名

### Step 3: 生成圖表

```bash
python3 << 'PYEOF'
import csv, sys, re
from datetime import datetime

# 動態 import matplotlib
try:
    import matplotlib
    matplotlib.use('Agg')  # 無頭模式
    import matplotlib.pyplot as plt
except ImportError:
    print("ERROR: matplotlib not installed. Run: pip3 install matplotlib")
    sys.exit(1)

# 跨平台中文字型
plt.rcParams['font.sans-serif'] = [
    'PingFang SC',      # macOS
    'Microsoft YaHei',  # Windows
    'Noto Sans CJK SC', # Linux
    'SimHei',           # Windows fallback
    'sans-serif'
]
plt.rcParams['axes.unicode_minus'] = False

# --- 設定 ---
FILE_PATH = "USER_FILE_PATH"
CHART_TYPE = "USER_CHART_TYPE"  # line / bar / pie / scatter
X_COL = "USER_X_COL"
Y_COLS = ["USER_Y_COL"]  # 可多欄
TITLE = "USER_TITLE"
OUTPUT = "/tmp/chart.png"

# --- 讀取資料 ---
with open(FILE_PATH, 'r', encoding='utf-8') as f:
    dialect = csv.Sniffer().sniff(f.read(4096))
    f.seek(0)
    reader = csv.DictReader(f, dialect=dialect)
    rows = list(reader)

# 限制行數防止卡死
if len(rows) > 5000:
    step = len(rows) // 5000
    rows = rows[::step]
    print(f"Downsampled to {len(rows)} rows")

# --- 解析 ---
date_re = re.compile(r'^\d{4}[-/]\d{1,2}[-/]\d{1,2}')

def parse_val(v):
    if not v:
        return None
    try:
        return float(v.replace(',', ''))
    except ValueError:
        return None

def parse_date(v):
    for fmt in ('%Y-%m-%d', '%Y/%m/%d', '%Y-%m-%d %H:%M:%S'):
        try:
            return datetime.strptime(v, fmt)
        except ValueError:
            continue
    return v

x_data = [parse_date(r[X_COL]) if date_re.match(r.get(X_COL, '')) else r.get(X_COL, '') for r in rows]

fig, ax = plt.subplots(figsize=(12, 6))

if CHART_TYPE == "line":
    for y_col in Y_COLS:
        y_data = [parse_val(r[y_col]) for r in rows]
        ax.plot(x_data, y_data, marker='o', markersize=2, label=y_col)
    ax.legend()

elif CHART_TYPE == "bar":
    y_data = [parse_val(r[Y_COLS[0]]) or 0 for r in rows]
    ax.bar(range(len(x_data)), y_data, tick_label=x_data)
    plt.xticks(rotation=45, ha='right')

elif CHART_TYPE == "pie":
    y_data = [parse_val(r[Y_COLS[0]]) or 0 for r in rows]
    ax.pie(y_data, labels=x_data, autopct='%1.1f%%')

elif CHART_TYPE == "scatter":
    y_data = [parse_val(r[Y_COLS[0]]) for r in rows]
    ax.scatter(x_data, y_data, alpha=0.6)

ax.set_title(TITLE, fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(OUTPUT, dpi=150, bbox_inches='tight')
print(f"CHART_SAVED:{OUTPUT}")
plt.close()
PYEOF
```

### Step 4: 展示結果

1. 用 Read tool 讀取圖片，展示給用戶
2. 詢問是否滿意
3. 不滿意 → 調整設定重新生成

## 支援的圖表類型

| 類型 | 適用場景 | 自動推薦條件 |
|------|---------|-------------|
| line | 時間序列趨勢 | X 軸為日期 + Y 軸為數值 |
| bar | 類別比較 | X 軸為分類（>6 種）+ Y 軸為數值 |
| pie | 佔比分布 | X 軸為分類（≤6 種）+ Y 軸為數值 |
| scatter | 相關性分析 | 兩個數值欄位 |

## 注意事項

- 需要 `matplotlib`（`pip3 install matplotlib`）
- 超過 5000 行自動降採樣
- 支援中文標題和標籤（macOS / Windows / Linux）
- 輸出預設 150 DPI PNG
