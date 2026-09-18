import sqlite3

connection = sqlite3.connect("revision.db")
cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        hash TEXT NOT NULL
    )
""")

connection.commit()
connection.close()

def apology():
    print("Sorry, this is a test program. No real functionality is implemented.")
    