#!/usr/bin/env python3
"""CSV/TSV charts with full-data aggregation and explicit diagnostics."""
import argparse
import json
import math
from pathlib import Path
import sys


def identifier(value):
    return '"' + value.replace('"', '""') + '"'


def prepare(conn, path, chart_type, x, y, delimiter=None):
    conn.execute("CREATE TEMP VIEW source AS SELECT * FROM read_csv("
                 + "'" + str(path).replace("'", "''") + "'"
                 + ", header=true, all_varchar=true"
                 + (", delim='" + delimiter.replace("'", "''") + "'" if delimiter is not None else "")
                 + ")")
    # Paths and identifiers are SQL-escaped, never interpreted as Python/shell code.
    columns = [item[0] for item in conn.execute("DESCRIBE source").fetchall()]
    if x not in columns or y not in columns:
        raise ValueError("Requested column not found")
    x_expr = identifier(x)
    if chart_type == "line":
        x_expr = "TRY_CAST(" + x_expr + " AS TIMESTAMP)"
    elif chart_type == "scatter":
        x_expr = "TRY_CAST(" + x_expr + " AS DOUBLE)"
    conn.execute("CREATE TEMP VIEW typed AS SELECT " + x_expr
                 + " AS x, TRY_CAST(" + identifier(y) + " AS DOUBLE) AS y FROM source")
    valid = "x IS NOT NULL AND y IS NOT NULL AND isfinite(y)"
    if chart_type == "scatter":
        valid += " AND isfinite(x)"
    total = conn.execute("SELECT count(*) FROM source").fetchone()[0]
    conn.execute("CREATE TEMP VIEW valid AS SELECT * FROM typed WHERE " + valid)
    used = conn.execute("SELECT count(*) FROM valid").fetchone()[0]
    if not used:
        raise ValueError("No valid rows")
    if chart_type == "pie" and conn.execute(
            "SELECT count(*) FROM valid WHERE y < 0").fetchone()[0]:
        raise ValueError("Pie input contains negative values")
    sampled = False
    if chart_type == "scatter":
        # Reservoir sample applies only to plotted points, never category totals.
        rows = conn.execute("SELECT x, y FROM valid USING SAMPLE reservoir(5000 ROWS) REPEATABLE(42)").fetchall()
        sampled = used > 5000
    else:
        query = "SELECT x, sum(y) AS y FROM valid GROUP BY x"
        count = conn.execute("SELECT count(*) FROM (" + query + ")").fetchone()[0]
        if count > 10000:
            raise ValueError("More than 10,000 groups; choose an explicit coarser grouping")
        rows = conn.execute(query + (" ORDER BY x" if chart_type == "line"
                                    else " ORDER BY y DESC, x")).fetchall()
        if any(not math.isfinite(row[1]) for row in rows):
            raise ValueError("Nonfinite aggregate; check numeric range")
        if chart_type == "pie":
            if sum(row[1] for row in rows) <= 0:
                raise ValueError("Pie total must be positive")
            if len(rows) > 10:
                rows = rows[:9] + [("Others", sum(row[1] for row in rows[9:]))]
    return rows, {"total_rows": total, "used_rows": used, "rejected_rows": total-used,
                  "sampled": sampled, "plotted_points": len(rows),
                  "aggregation": "none" if chart_type == "scatter" else "sum"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--type", choices=["line", "bar", "pie", "scatter"], required=True)
    parser.add_argument("--x", required=True)
    parser.add_argument("--y", required=True)
    parser.add_argument("--title", default="")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--delimiter")
    args = parser.parse_args()
    if args.output.suffix.lower() != ".png":
        parser.error("Output must end in .png")
    if args.output.exists():
        parser.error("Output exists; choose another path")
    try:
        import duckdb
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib import font_manager
        available = {font.name for font in font_manager.fontManager.ttflist}
        fonts = [name for name in ("PingFang TC", "Microsoft JhengHei", "Noto Sans CJK TC",
                                   "Noto Sans CJK SC", "DejaVu Sans") if name in available]
        plt.rcParams["font.sans-serif"] = fonts or ["sans-serif"]
        plt.rcParams["axes.unicode_minus"] = False
        delimiter = "\t" if args.delimiter == r"\t" else args.delimiter
        with duckdb.connect(config={"memory_limit": "512MB", "threads": "2"}) as conn:
            rows, stats = prepare(conn, args.input.resolve(strict=True), args.type,
                                  args.x, args.y, delimiter)
        x, y = zip(*rows)
        fig, ax = plt.subplots(figsize=(12, 6))
        if args.type == "line":
            ax.plot(x, y)
        elif args.type == "bar":
            ax.bar(range(len(x)), y, tick_label=x)
            ax.tick_params(axis="x", labelrotation=45)
        elif args.type == "pie":
            ax.pie(y, labels=x, autopct="%1.1f%%")
        else:
            ax.scatter(x, y, alpha=0.6)
        ax.set_title(args.title)
        if args.type != "pie":
            ax.set_xlabel(args.x)
            ax.set_ylabel(args.y)
        fig.tight_layout()
        with args.output.open("xb") as output:
            fig.savefig(output, format="png", dpi=150, bbox_inches="tight")
        plt.close(fig)
        stats["path"] = str(args.output.resolve())
        print(json.dumps(stats, ensure_ascii=False))
    except ImportError:
        print("Missing dependency: install duckdb and matplotlib in an approved environment", file=sys.stderr)
        return 1
    except Exception as exc:
        print("Chart failed: " + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
