import sqlite3
import json
from models import Tag

def get_all_tags():
    with sqlite3.connect("./db.sqlite3") as conn:

        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute("""
        SELECT
            t.id,
            t.label
        FROM tags t
        """)

        tags = []

        dataset = db_cursor.fetchall()

        for row in dataset:
            tag = Tag(row['id'], row['label'])
            tags.append(tag.__dict__)

    return json.dumps(tags)


def get_single_tag(id):
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        # Use a ? parameter to inject a variable's value
        # into the SQL statement.
        db_cursor.execute("""
        SELECT
            t.id,
            t.label
            
        FROM Tags t
        """)

        # Load the single result into memory
        data = db_cursor.fetchone()

        # Create an animal instance from the current row
        tag = Tag(data['id'], data['label'])

        return json.dumps(tag.__dict__)
    
def create_tag(new_tag):
    with sqlite3.connect("./db.sqlite3") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute("""
        INSERT INTO Tags
            ( label )
        VALUES
            ( ? );
        """, (new_tag['label'], ))

        id = db_cursor.lastrowid

        new_tag['id'] = id

    return json.dumps(new_tag)
    
def delete_tag(id):
    with sqlite3.connect("./db.sqlite3") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute("""
        DELETE FROM Tags
        WHERE id = ?
        """, (id, ))