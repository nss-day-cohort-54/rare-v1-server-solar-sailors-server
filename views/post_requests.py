import sqlite3
import json
from models import Post, Category, Tag, Reaction

def get_all_posts():
    # Open a connection to the database
    with sqlite3.connect("./db.sqlite3") as conn:

        # Just use these. It's a Black Box.
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        # Write the SQL query to get the information you want
        db_cursor.execute("""
        SELECT
            p.id,
            p.user_id,
            p.category_id,
            p.title,
            p.publication_date,
            p.image_url,
            p.content,
            p.approved,
            c.id cat_id,
            c.label
        FROM Posts p
        JOIN Categories c
        ON c.id = p.category_id
        """)

        # Initialize an empty list to hold all post representations
        posts = []

        # Convert rows of data into a Python list
        dataset = db_cursor.fetchall()

        # Iterate list of data returned from database
        for row in dataset:

            
            post = Post(row['id'], row['user_id'], row['category_id'], row['title'] , row['publication_date'], row['image_url'], row['content'] )
            
            category = Category(row['cat_id'], row['label'])
            
            tags =[]
            
            db_cursor.execute(""" 
                            SELECT
                                t.id,
                                t.label tag_label
                            FROM Posts p
                            JOIN PostTags pt
                            ON pt.post_id = p.id
                            LEFT JOIN Tags t
                            ON pt.tag_id = t.id
                            WHERE pt.post_id = ?
                            """, ( post.id, ))
            
            post_tags = db_cursor.fetchall()
            
            for pt in post_tags:
                tag = Tag(pt['id'], pt['tag_label'])
                tag = tag.__dict__
                tags.append(tag)
            
            post.tags = tags
            
            post.category = category.__dict__
            
            posts.append(post.__dict__)

    # Use `json` package to properly serialize list as JSON
    return json.dumps(posts)

def get_single_post(id):
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        # Use a ? parameter to inject a variable's value
        # into the SQL statement.
        db_cursor.execute("""
        SELECT
            p.id,
            p.user_id,
            p.category_id,
            p.title,
            p.publication_date,
            p.image_url,
            p.content,
            p.approved,
            c.id cat_id,
            c.label
        FROM Posts p
        JOIN Categories c
        ON c.id = p.category_id
        JOIN PostReactions pr
        ON pr.post_id = p.id
        LEFT JOIN Reactions r
        ON pr.reaction_id = r.id
        WHERE pr.post_id = ?
        """, (id, ))

        # Load the single result into memory
        data = db_cursor.fetchone()
        
        # Create an post instance from the current row
        post = Post(data['id'], data['user_id'], data['category_id'], data['title'] , data['publication_date'], data['image_url'], data['content'])
            
        category = Category(data['id'], data['label'])
        
        post.category = category.__dict__
        
        return json.dumps(post.__dict__)

def get_post_by_search(string_variable):

    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        # Write the SQL query to get the information you want
        db_cursor.execute("""
        SELECT
            p.id,
            p.user_id,
            p.category_id,
            p.title,
            p.publication_date,
            p.image_url,
            p.content,
            p.approved
        FROM Posts p
        WHERE p.post LIKE ?
        """, ( '%'+ string_variable +'%', ))

        posts = []
        
        dataset = db_cursor.fetchall()

        for data in dataset:
            post = Post(data['id'], data['user_id'], data['category_id'], data['title'] , data['publication_date'], data['image_url'], data['content'], data['approved'] )
            
            posts.append(post.__dict__)

    return json.dumps(posts)

def create_post(new_post):
    with sqlite3.connect("./db.sqlite3") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute("""
        INSERT INTO Post
            ( category_id, title, image_url, content, approved, )
        VALUES
            ( ?, ?, ?, ? );
        """, (new_post['category_id'], new_post['title'], new_post['image_url'] , new_post['content'], ))

        # The `lastrowid` property on the cursor will return
        # the primary key of the last thing that got added to
        # the database.
        id = db_cursor.lastrowid

        # Add the `id` property to the post dictionary that
        # was sent by the client so that the client sees the
        # primary key in the response.
        new_post['id'] = id
        
        for tag in new_post['tags']:
            db_cursor.execute("""
                INSERT INTO PostTags
                ( post_id, tag_id)
                VALUES
                ( ?, ? )
            """, ( id, tag,))

    return json.dumps(new_post)

def update_post(id, new_post):
    with sqlite3.connect("./db.sqlite3") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute("""
        UPDATE Posts
            SET
                category_id = ?,
                title = ?,
                image_url = ?,
                content = ?
        WHERE id = ?
        """, (new_post['category_id'], new_post['title'], new_post['image_url'] , new_post['content'], id, ))

        # Were any rows affected?
        # Did the client send an `id` that exists?
        rows_affected = db_cursor.rowcount

    if rows_affected == 0:
        # Forces 404 response by main module
        return False
    else:
        # Forces 204 response by main module
        return True    
        
def delete_post(id):
    with sqlite3.connect("./db.sqlite3") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute("""
        DELETE FROM Posts
        WHERE id = ?
        """, (id, ))