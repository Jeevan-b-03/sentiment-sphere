import sqlite3
import os

def migrate():
    db_path = os.path.join(os.getcwd(), 'instance', 'project.db')
    if not os.path.exists(db_path):
        # Check if it's named something else
        db_dir = os.path.join(os.getcwd(), 'instance')
        if os.path.exists(db_dir):
            files = os.listdir(db_dir)
            print(f"Files in instance: {files}")
            # Try to find a .db file
            db_files = [f for f in files if f.endswith('.db')]
            if db_files:
                db_path = os.path.join(db_dir, db_files[0])
            else:
                print("No database file found in instance folder.")
                return
        else:
            print("No instance folder found.")
            return

    print(f"Migrating database at: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(comment)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_salesforce_user' not in columns:
            cursor.execute("ALTER TABLE comment ADD COLUMN is_salesforce_user BOOLEAN DEFAULT 0")
            conn.commit()
            print("Successfully added column 'is_salesforce_user' to 'comment' table.")
        else:
            print("Column 'is_salesforce_user' already exists.")
            
    except Exception as e:
        print(f"Migration error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
