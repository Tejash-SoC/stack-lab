"""
Loads the CSVs into a SQLite database and runs every query in sql/queries.sql.

Run:  python run_sql.py
Output is printed and saved to outputs/sql_results.txt
(open retail.db in DB Browser for SQLite to explore it yourself).
"""
import re
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
DB = ROOT / "retail.db"
DB.unlink(missing_ok=True)

con = sqlite3.connect(DB)
for name in ["customers", "products", "orders", "order_items"]:
    pd.read_csv(ROOT / "data" / f"{name}.csv").to_sql(name, con, index=False)
con.executescript((ROOT / "sql/00_views.sql").read_text())

text = (ROOT / "sql/queries.sql").read_text()
blocks = re.split(r"^-- name: ", text, flags=re.M)[1:]

report = []
for block in blocks:
    title, _, query = block.partition("\n")
    df = pd.read_sql_query(query, con)
    report.append(f"### {title}\n{df.to_string(index=False)}\n")

out = "\n".join(report)
(ROOT / "outputs").mkdir(exist_ok=True)
(ROOT / "outputs/sql_results.txt").write_text(out)
print(out)
con.close()
