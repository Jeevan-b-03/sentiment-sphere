import sqlite3
import os

# Check common locations
possible_dbs = [
    'comments.db',
    'instance/comments.db',
    os.path.join(os.getcwd(), 'comments.db'),
    os.path.join(os.getcwd(), 'instance', 'comments.db'),
    # Add instance path if it exists
    os.path.join('instance', 'comments.db')
]

# Unique paths
unique_dbs = set(os.path.abspath(p) for p in possible_dbs)

for db_path in unique_dbs:
    if not os.path.exists(db_path):
        continue
        
    print(f"Processing {db_path}...")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check table columns
        cursor.execute("PRAGMA table_info(comment)")
        cols = [r[1] for r in cursor.fetchall()]
        
        if 'replied' not in cols:
            print(f"Adding 'replied' column to {db_path}...")
            cursor.execute("ALTER TABLE comment ADD COLUMN replied BOOLEAN DEFAULT 0")
            conn.commit()
            print("Done.")
        else:
            print(f"Column already exists in {db_path}.")
        conn.close()
    except Exception as e:
        print(f"Error on {db_path}: {e}")
