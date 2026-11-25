import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
db_path = PROJECT_ROOT / "data" / "hate_speech_detector.db"

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()
tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
print("Tables in SQLite database:")
for (t,) in tables:
    count = cursor.execute(f"SELECT count(*) FROM [{t}]").fetchone()[0]
    print(f"  {t}: {count} rows")

print("\n--- DATASETS OVERVIEW ---")
datasets = cursor.execute("SELECT id, name, total_samples, is_benchmark FROM datasets").fetchall()
for d in datasets:
    print(f"Dataset: id={d[0]}, name={d[1]}, total={d[2]}, is_benchmark={d[3]}")

print("\n--- SPLITS IN DATASET_RECORDS ---")
splits = cursor.execute("SELECT dataset_id, split, count(*) FROM dataset_records GROUP BY dataset_id, split").fetchall()
for s in splits:
    print(f"  dataset={s[0]}, split={s[1]}: {s[2]} records")

print("\n--- DUPLICATES CHECK ---")
dups = cursor.execute("""
    SELECT text, count(*) as c 
    FROM dataset_records 
    GROUP BY text 
    HAVING c > 1
""").fetchall()
print(f"Duplicate texts across all records: {len(dups)}")
for text, c in dups[:10]:
    splits_where = cursor.execute("SELECT dataset_id, split FROM dataset_records WHERE text = ?", (text,)).fetchall()
    print(f"  count={c} across {splits_where}: {text[:60]}...")

print("\n--- MODEL REGISTRY ---")
models = cursor.execute("SELECT id, name, version, architecture, is_active FROM model_registry").fetchall()
for m in models:
    print(f"  model: {m}")
conn.close()
