import sqlite3
from datetime import datetime

conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    free_coin INTEGER DEFAULT 0,
    paid_coin INTEGER DEFAULT 0,
    last_bonus TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS promos (
    code TEXT PRIMARY KEY,
    amount INTEGER
)
""")

conn.commit()

def add_user(user_id):
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

def get_user(user_id):
    cursor.execute("SELECT free_coin, paid_coin, last_bonus FROM users WHERE user_id=?", (user_id,))
    return cursor.fetchone()

def add_free(user_id, amount):
    cursor.execute("UPDATE users SET free_coin = free_coin + ? WHERE user_id=?", (amount, user_id))
    conn.commit()

def add_paid(user_id, amount):
    cursor.execute("UPDATE users SET paid_coin = paid_coin + ? WHERE user_id=?", (amount, user_id))
    conn.commit()

def take_coin(user_id, coin_type, amount):
    if coin_type == "free":
        cursor.execute("UPDATE users SET free_coin = free_coin - ? WHERE user_id=?", (amount, user_id))
    else:
        cursor.execute("UPDATE users SET paid_coin = paid_coin - ? WHERE user_id=?", (amount, user_id))
    conn.commit()
