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

#### SQLite

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
    sample = conn.execute(f'SELECT * FROM "{name}" LIMIT 3').fetchall()
    cols = [d[0] for d in conn.execute(f'SELECT * FROM "{name}" LIMIT 0').description]
    print(f"-- Columns: {cols}")
    print(f"-- Sample ({len(sample)} rows): {sample[:2]}")

conn.close()
PYEOF
```

#### DuckDB

```bash
python3 << 'PYEOF'
import sys
try:
    import duckdb
except ImportError:
    print("ERROR: pip3 install duckdb")
    sys.exit(1)

DB_PATH = "USER_DB_PATH"
conn = duckdb.connect(DB_PATH, read_only=True)

tables = conn.execute("SHOW TABLES").fetchall()
for (name,) in tables:
    print(f"\n-- Table: {name}")
    ddl = conn.execute(f'DESCRIBE "{name}"').fetchall()
    for col_name, col_type, *_ in ddl:
        print(f"--   {col_name}: {col_type}")
    sample = conn.execute(f'SELECT * FROM "{name}" LIMIT 3').fetchall()
    print(f"-- Sample: {sample[:2]}")

conn.close()
PYEOF
```

將 schema + sample data 展示給用戶確認目標 table。

### Step 3: 自然語言 → SQL

基於 schema context，Claude 將用戶的自然語言問題轉為 SQL。

**轉換規則：**
- 使用與 DB 類型對應的 SQL 方言（SQLite vs DuckDB）
- **只產生單一 SELECT 或 WITH...SELECT 語句**（禁止多 statement）
- 自動加上 `LIMIT 100`（除非用戶明確要全部）
- 欄位名用雙引號 `"column"` 包裹避免保留字衝突（SQLite 和 DuckDB 通用）

**展示 SQL 給用戶確認後才執行。**

### Step 4: 安全執行 SQL

```bash
python3 << 'PYEOF'
import sqlite3, sys, re

DB_PATH = "USER_DB_PATH"
DB_TYPE = "sqlite"  # or "duckdb"
SQL = """USER_SQL_HERE"""

# === 安全檢查 ===

# 1. 禁止多 statement（分號只能出現在結尾）
sql_stripped = SQL.strip().rstrip(';')
if ';' in sql_stripped:
    print("BLOCKED: Multiple statements not allowed.", file=sys.stderr)
    sys.exit(1)

# 2. 首 token 必須是 SELECT 或 WITH
first_token = sql_stripped.split()[0].upper() if sql_stripped.split() else ""
if first_token not in ("SELECT", "WITH"):
    print(f"BLOCKED: Only SELECT/WITH queries allowed (got: {first_token}).", file=sys.stderr)
    sys.exit(1)

# 3. 阻擋危險關鍵字（即使在子查詢中）
dangerous = re.compile(
    r'(?i)\b(DROP|DELETE|UPDATE|INSERT|ALTER|ATTACH|DETACH|CREATE|VACUUM|ANALYZE|REINDEX|PRAGMA)\b'
)
if dangerous.search(SQL):
    print("BLOCKED: Dangerous keyword detected.", file=sys.stderr)
    sys.exit(1)

# 4. 強制 LIMIT
if not re.search(r'(?i)\bLIMIT\b', SQL):
    SQL = f"{sql_stripped} LIMIT 100;"

# === 執行 ===
conn = None
try:
    if DB_TYPE == "sqlite":
        conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        # 額外防護：用 authorizer 阻擋非 SELECT 操作
        def authorizer(action, arg1, arg2, db_name, trigger):
            ALLOWED = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ,
                       sqlite3.SQLITE_FUNCTION, sqlite3.SQLITE_RECURSIVE}
            return sqlite3.SQLITE_OK if action in ALLOWED else sqlite3.SQLITE_DENY
        conn.set_authorizer(authorizer)
    else:
        import duckdb
        conn = duckdb.connect(DB_PATH, read_only=True)

    cursor = conn.execute(SQL)
    columns = [d[0] for d in cursor.description]
    rows = cursor.fetchall()

    # Markdown table 輸出
    print(f"| {' | '.join(columns)} |")
    print(f"| {' | '.join(['---'] * len(columns))} |")
    for row in rows:
        print(f"| {' | '.join(str(v) if v is not None else '' for v in row)} |")

    print(f"\n({len(rows)} rows returned)")

except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
finally:
    if conn is not None:
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
| **首 token 檢查** | 只允許 SELECT / WITH 開頭 |
| **多 statement 阻擋** | 禁止分號分隔的多語句 |
| **危險關鍵字過濾** | DROP/DELETE/UPDATE/INSERT/ALTER/CREATE/ATTACH/PRAGMA 等 |
| **SQLite authorizer** | `set_authorizer()` 在 opcode 層阻擋非 SELECT 操作 |
| **強制 LIMIT** | 沒有 LIMIT 的查詢自動加 `LIMIT 100` |
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
