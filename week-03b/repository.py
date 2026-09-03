from database import get_connection


def get_all_tasks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "title": r[1], "done": r[2]} for r in rows]


def get_task_by_id(task_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = %s", (task_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "title": row[1], "done": row[2]}
    return None


def create_task(title: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id",
        (title, False)
    )
    new_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return {"id": new_id, "title": title, "done": False}


def update_task(task_id: int, title: str = None, done: bool = None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, done FROM tasks WHERE id = %s", (task_id,))
    existing = cursor.fetchone()
    if not existing:
        conn.close()
        return None

    new_title = title if title is not None else existing[1]
    new_done = done if done is not None else existing[2]

    cursor.execute(
        "UPDATE tasks SET title = %s, done = %s WHERE id = %s",
        (new_title, new_done, task_id)
    )
    conn.commit()
    conn.close()
    return {"id": task_id, "title": new_title, "done": new_done}


def delete_task(task_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted > 0