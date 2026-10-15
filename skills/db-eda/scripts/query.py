#!/usr/bin/env python3
"""Bounded read queries against trusted local SQLite or DuckDB files."""
import argparse
import json
from pathlib import Path
import sqlite3
import sys
import threading
import time


def open_database(path, engine, timeout):
    path = Path(path).resolve(strict=True)
    if not path.is_file():
        raise ValueError("Database must be a regular file")
    if engine == "sqlite":
        conn = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=timeout)
        conn.execute("PRAGMA query_only=ON")
        deadline = time.monotonic() + timeout
        conn.set_progress_handler(lambda: int(time.monotonic() > deadline), 1000)
        allowed = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ,
                   sqlite3.SQLITE_FUNCTION, sqlite3.SQLITE_RECURSIVE}

        def authorize(action, arg1, arg2, db, trigger):
            if action == sqlite3.SQLITE_FUNCTION and str(arg2).lower() in {
                    "load_extension", "readfile", "writefile"}:
                return sqlite3.SQLITE_DENY
            return sqlite3.SQLITE_OK if action in allowed else sqlite3.SQLITE_DENY

        conn.set_authorizer(authorize)
        return conn
    import duckdb
    conn = duckdb.connect(str(path), read_only=True, config={
        "enable_external_access": "false",
        "autoinstall_known_extensions": "false",
        "autoload_known_extensions": "false",
        "allow_community_extensions": "false",
        "memory_limit": "512MB", "threads": "2",
    })
    try:
        conn.execute("SET lock_configuration = true")
    except Exception:
        conn.close()
        raise
    return conn


def query(conn, sql, engine, rows):
    if not 1 <= rows <= 10000:
        raise ValueError("rows must be between 1 and 10000")
    sql = sql.strip()
    if sql.endswith(";"):
        sql = sql[:-1].rstrip()
    if not sql:
        raise ValueError("Empty SQL")
    if engine == "duckdb":
        statements = conn.extract_statements(sql)
        if len(statements) != 1 or statements[0].type.name != "SELECT":
            raise ValueError("Exactly one SELECT statement is required")
    # SQLite execute rejects multiple statements; the authorizer rejects writes.
    # Newlines prevent a trailing line comment from consuming the wrapper.
    cursor = conn.execute("SELECT * FROM (\n" + sql + "\n) AS result LIMIT "
                          + str(rows + 1))
    values = cursor.fetchmany(rows + 1)
    return {"columns": [item[0] for item in cursor.description],
            "rows": values[:rows], "truncated": len(values) > rows}


def schema(conn, engine):
    if engine == "sqlite":
        cursor = conn.execute("SELECT name, sql FROM sqlite_master "
                              "WHERE type IN ('table','view') AND sql IS NOT NULL "
                              "ORDER BY name LIMIT 101")
    else:
        cursor = conn.execute("SELECT table_schema, table_name, column_name, data_type "
                              "FROM information_schema.columns "
                              "WHERE (table_schema, table_name) IN "
                              "(SELECT table_schema, table_name FROM information_schema.tables "
                              "ORDER BY table_schema, table_name LIMIT 100) "
                              "ORDER BY table_schema, table_name, ordinal_position LIMIT 1001")
    values = cursor.fetchmany(101 if engine == "sqlite" else 1001)
    limit = 100 if engine == "sqlite" else 1000
    return {"columns": [item[0] for item in cursor.description],
            "rows": values[:limit], "truncated": len(values) > limit,
            "scope": "at most 100 tables/views; DuckDB at most 1000 columns",
            "table_coverage": "bounded; additional tables may exist"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("database", type=Path)
    parser.add_argument("--engine", choices=["sqlite", "duckdb"])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--schema", action="store_true")
    mode.add_argument("--sql-file", type=Path)
    parser.add_argument("--rows", type=int, default=100)
    parser.add_argument("--timeout", type=float, default=10)
    args = parser.parse_args()
    if not 1 <= args.rows <= 10000 or not 0 < args.timeout <= 120:
        parser.error("rows: 1..10000; timeout: >0 and <=120 seconds")
    engine = args.engine or ("duckdb" if args.database.suffix.lower() == ".duckdb" else "sqlite")
    conn = None
    timer = None
    try:
        sql = args.sql_file.read_text(encoding="utf-8") if args.sql_file else None
        conn = open_database(args.database, engine, args.timeout)
        if engine == "duckdb":
            timer = threading.Timer(args.timeout, conn.interrupt)
            timer.daemon = True
            timer.start()
        result = schema(conn, engine) if args.schema else query(conn, sql, engine, args.rows)
        print(json.dumps(result, ensure_ascii=False, default=str))
    except Exception as exc:
        print("Query failed: " + str(exc), file=sys.stderr)
        return 1
    finally:
        if timer:
            timer.cancel()
            timer.join()
        if conn:
            conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
