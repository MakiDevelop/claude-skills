---
name: db-eda
description: 用自然語言查詢 SQLite 或 DuckDB 資料庫。當用戶說「查資料庫」「SQL 查詢」「db eda」「自然語言查 DB」時使用。
argument-hint: "[db 檔案路徑 + 問題，如 'data.db 最近一週的銷售額']"
allowed-tools: Bash(python3*), Bash(pip3*), Read, Write
author: Maki
version: "1.0.0"
tags: [database, sqlite, duckdb, eda, data]
required_env: []
---

# 自然語言查詢 SQLite / DuckDB

## 目標

讓用戶用自然語言對 SQLite 或 DuckDB 資料庫提問，自動轉成 SQL 執行並格式化輸出。全程 read-only，安全第一。

## 前置條件

### 檢查資料庫引擎

```bash
python3 -c "
import sqlite3; print('sqlite3: OK')
try:
    import duckdb; print(f'duckdb: {duckdb.__version__}')
except ImportError:
    print('duckdb: NOT_FOUND (only needed for .duckdb files)')
"
```

- SQLite：Python 內建，不需額外安裝
- DuckDB：只在開啟 `.duckdb` 檔案時需要（`pip3 install duckdb`）

## 流程

### Step 1: 確認輸入

根據 `$ARGUMENTS` 判斷：

- 解析出 DB 檔案路徑和自然語言問題
- 如果缺少 → 詢問用戶
- 根據副檔名判斷類型：`.db` / `.sqlite` → SQLite，`.duckdb` → DuckDB

### Step 2: 讀取 Schema

```bash
python3 << 'PYEOF'
import sqlite3, json, sys

DB_PATH = "USER_DB_PATH"

# 強制 read-only 連線
conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)

# 取得所有 table 的 DDL
cursor = conn.execute("""
    SELECT name, sql FROM sqlite_master
    WHERE type='table' AND sql IS NOT NULL
    ORDER BY name
""")
tables = cursor.fetchall()

for name, ddl in tables:
    print(f"\n-- Table: {name}")
    print(ddl)
    # Sample data (前 3 行)
    sample = conn.execute(f"SELECT * FROM [{name}] LIMIT 3").fetchall()
    cols = [d[0] for d in conn.execute(f"SELECT * FROM [{name}] LIMIT 0").description]
    print(f"-- Columns: {cols}")
    print(f"-- Sample ({len(sample)} rows): {sample[:2]}")
    # Row count
    count = conn.execute(f"SELECT COUNT(*) FROM [{name}]").fetchone()[0]
    print(f"-- Total rows: {count}")

conn.close()
PYEOF
```

將 schema + sample data 展示給用戶確認目標 table。

### Step 3: 自然語言 → SQL

基於 schema context，Claude 將用戶的自然語言問題轉為 SQL。

**轉換規則：**
- 使用與 DB 類型對應的 SQL 方言（SQLite vs DuckDB）
- 只產生 SELECT 語句
- 自動加上 `LIMIT 100`（除非用戶明確要全部）
- 欄位名用 `[bracket]` 包裹避免保留字衝突

**展示 SQL 給用戶確認後才執行。**

### Step 4: 安全執行 SQL

```bash
python3 << 'PYEOF'
import sqlite3, sys, re, signal

DB_PATH = "USER_DB_PATH"
SQL = """USER_SQL_HERE"""

# === 安全檢查 ===

# 1. 阻擋危險語句
dangerous = re.compile(r'(?i)\b(DROP|DELETE|UPDATE|INSERT|ALTER|ATTACH|DETACH|PRAGMA\s+(?!table_info|database_list))\b')
if dangerous.search(SQL):
    print("BLOCKED: Only SELECT queries are allowed.", file=sys.stderr)
    sys.exit(1)

# 2. 強制 LIMIT
if not re.search(r'(?i)\bLIMIT\b', SQL):
    SQL = f"{SQL.rstrip(';')} LIMIT 100;"

# 3. Timeout (30 秒)
def timeout_handler(signum, frame):
    raise TimeoutError("Query exceeded 30 second timeout")

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(30)

# === 執行 ===
try:
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    cursor = conn.execute(SQL)
    columns = [d[0] for d in cursor.description]
    rows = cursor.fetchall()

    # Markdown table 輸出
    print(f"| {' | '.join(columns)} |")
    print(f"| {' | '.join(['---'] * len(columns))} |")
    for row in rows:
        print(f"| {' | '.join(str(v) if v is not None else '' for v in row)} |")

    print(f"\n({len(rows)} rows returned)")

except TimeoutError:
    print("ERROR: Query timeout (>30s). Try a more specific query.", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
finally:
    signal.alarm(0)
    conn.close()
PYEOF
```

### Step 5: 格式化輸出

1. 結果以 Markdown table 呈現
2. 如果結果太多欄位 → 自動截斷並提示
3. 詢問用戶是否要：
   - 追問更多問題
   - 匯出為 CSV
   - 用 `csv-to-chart` 畫圖表

## 安全機制

| 防線 | 說明 |
|------|------|
| **Read-only 連線** | SQLite `?mode=ro`、DuckDB `read_only=True` |
| **語句過濾** | Regex 阻擋 DROP/DELETE/UPDATE/INSERT/ALTER/ATTACH |
| **強制 LIMIT** | 沒有 LIMIT 的查詢自動加 `LIMIT 100` |
| **Timeout** | 30 秒超時自動中斷 |
| **用戶確認** | SQL 執行前展示給用戶確認 |

## DuckDB 支援

如果檔案是 `.duckdb`：

```python
import duckdb
conn = duckdb.connect("USER_DB_PATH", read_only=True)
# Schema: SHOW TABLES; DESCRIBE table_name;
# 其餘流程相同
```

需要 `pip3 install duckdb`。

## 注意事項

- 資料庫始終以 read-only 模式開啟，不會修改任何資料
- 執行前必須讓用戶確認 SQL
- 不支援需要密碼的遠端資料庫（僅本地檔案）
- 大型資料庫（>1GB）的 schema 讀取可能較慢
