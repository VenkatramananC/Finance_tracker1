from database import get_connection

def get_summary(user_id=None):
    conn = get_connection()
    cursor = conn.cursor()

    base = "FROM transactions"
    params = []
    if user_id:
        base += " WHERE user_id = ?"
        params.append(user_id)

    cursor.execute(f"SELECT COALESCE(SUM(amount), 0) {base} AND type='income'" if user_id
                   else f"SELECT COALESCE(SUM(amount), 0) {base} WHERE type='income'", params)
    total_income = cursor.fetchone()[0]

    cursor.execute(f"SELECT COALESCE(SUM(amount), 0) {base} AND type='expense'" if user_id
                   else f"SELECT COALESCE(SUM(amount), 0) {base} WHERE type='expense'", params)
    total_expense = cursor.fetchone()[0]

    conn.close()
    return {
        "total_income": round(total_income, 2),
        "total_expense": round(total_expense, 2),
        "balance": round(total_income - total_expense, 2)
    }


def get_category_breakdown(user_id=None):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT category, type, ROUND(SUM(amount), 2) as total
        FROM transactions
    """
    params = []
    if user_id:
        query += " WHERE user_id = ?"
        params.append(user_id)
    query += " GROUP BY category, type ORDER BY total DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_monthly_totals(user_id=None):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT strftime('%Y-%m', date) as month,
               type,
               ROUND(SUM(amount), 2) as total
        FROM transactions
    """
    params = []
    if user_id:
        query += " WHERE user_id = ?"
        params.append(user_id)
    query += " GROUP BY month, type ORDER BY month DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_recent_activity(user_id=None, limit=10):
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM transactions"
    params = []
    if user_id:
        query += " WHERE user_id = ?"
        params.append(user_id)
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]