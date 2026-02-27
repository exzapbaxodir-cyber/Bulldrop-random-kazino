from database import cursor, conn, add_free

def create_promo(code, amount):
    cursor.execute("INSERT OR REPLACE INTO promos VALUES (?, ?)", (code, amount))
    conn.commit()

def use_promo(user_id, code):
    cursor.execute("SELECT amount FROM promos WHERE code=?", (code,))
    row = cursor.fetchone()
    if not row:
        return False

    add_free(user_id, row[0])
    return row[0]
