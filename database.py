import sqlite3
import os

DB_STRING = "cromos.db"

db_directory = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(db_directory, DB_STRING)

def setup_database():
    image_table = """ CREATE TABLE IF NOT EXISTS images (
        image_id INTEGER PRIMARY KEY AUTOINCREMENT,
        img_name TEXT NOT NULL,
        collection_id INTEGER NOT NULL,
        creation_date TEXT NOT NULL, 
        uploaded_by INTEGER NOT NULL,
        owner_id INTEGER,
        FOREIGN KEY (collection_id) REFERENCES collection_table (id_collection),
        FOREIGN KEY (uploaded_by) REFERENCES users (id),
        FOREIGN KEY (owner_id) REFERENCES users (id)
    );"""

    user_table = """ CREATE TABLE IF NOT EXISTS users ( 
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        token TEXT
    );"""

    transaction_table = """ CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        current_owner_id INTEGER NOT NULL,
        previous_owner_id INTEGER,
        ts TEXT NOT NULL,
        image_id INTEGER NOT NULL,
        FOREIGN KEY (current_owner_id) REFERENCES users (id),
        FOREIGN KEY (previous_owner_id) REFERENCES users (id),
        FOREIGN KEY (image_id) REFERENCES images (image_id)
    );
    """

    collection_table = """ CREATE TABLE IF NOT EXISTS collections (
        id_collection INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    );"""

    with sqlite3.connect(db_path) as con:
        con.execute(image_table)
        con.execute(user_table)
        con.execute(collection_table)
        con.execute(transaction_table)

def cleanup_database():
    image_table = "DROP TABLE IF EXISTS images;"
    users_table = "DROP TABLE IF EXISTS users;"
    collection_table = "DROP TABLE IF EXISTS collections;"
    transaction_table = "DROP TABLE IF EXISTS transactions;"
    with sqlite3.connect(db_path) as con:
        con.execute(image_table)
        con.execute(users_table)
        con.execute(collection_table)
        con.execute(transaction_table)

def main():
    setup_database()

    # cleanup_database()

if __name__ == '__main__':
    main()
