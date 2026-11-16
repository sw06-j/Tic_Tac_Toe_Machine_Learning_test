import sqlite3
import json
import sys
import os

learning_file_name = sys.argv[1] if len(sys.argv) > 1 else "learning_ai1"
if learning_file_name.endswith(".db"):
    learning_file_name = learning_file_name[:-3]

db_path = f"{learning_file_name}.db"
if not os.path.exists(db_path):
    print(f"DB 파일을 찾을 수 없습니다: {db_path}")
    sys.exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
tables = [row[0] for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]

if "json_table" in tables:
    cursor.execute("SELECT array_json FROM json_table")
    result = cursor.fetchone()
    data = json.loads(result[0]) if result else []
    for level_idx, level_nodes in enumerate(data):
        print(f"=== Level {level_idx} ({len(level_nodes)} nodes) ===")
        for node in level_nodes:
            print(node)
elif "tree" in tables:
    rows = cursor.execute("SELECT level, board, drop_row, drop_col, reward FROM tree").fetchall()
    print(f"=== tree ({len(rows)} rows) ===")
    for row in rows:
        print(row)
else:
    print(f"지원하는 테이블이 없습니다. (현재 테이블: {tables})")

conn.close()
