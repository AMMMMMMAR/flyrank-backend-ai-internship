import sqlite3

def init_db():
    # 1. Connect to the database (creates 'tasks.db' if it doesn't exist)
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()

    # 2. Create the tasks table if it doesn't already exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0
        )
    """)

    # 3. Check if the table is empty
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]

    # 4. Insert 3 default tasks only if the table is empty
    if count == 0:
        example_tasks = [
            ("This is task 1", 0),
            ("This is task 2", 1),
            ("This is task 3", 0)
        ]
        # executemany binds each tuple in the list to the placeholders (?, ?)
        cursor.executemany("INSERT INTO tasks (title, done) VALUES (?, ?)", example_tasks)
        
    # Commit the transaction to save changes to disk
    conn.commit()

    # 5. Clean up by closing the connection
    conn.close()


init_db()