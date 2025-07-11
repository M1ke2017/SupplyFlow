def login_user(username, password, conn):
    cur = conn.cursor()
    cur.execute(
        "SELECT role FROM users WHERE username = %s AND password = %s",
        (username, password)
    )
    result = cur.fetchone()
    return result[0] if result else None
