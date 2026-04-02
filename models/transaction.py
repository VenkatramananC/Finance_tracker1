from database import get_connection


VALID_TYPES = ('income', 'expense')


def validate_transaction(amount, type_, category, date):
    errors = []
    if amount is None:
        errors.append("Amount is required.")
    else:
        try:
            amount = float(amount)
            if amount <= 0:
                errors.append("Amount must be positive.")
        except (ValueError, TypeError):
            errors.append("Amount must be a number.")

    if type_ not in VALID_TYPES:
        errors.append(f"Type must be one of: {VALID_TYPES}")

    if not category or not category.strip():
        errors.append("Category is required.")

    if not date or not date.strip():
        errors.append("Date is required.")

    return errors


def create_transaction(user_id, amount, type_, category, date, notes=""):
    errors = validate_transaction(amount, type_, category, date)
    if errors:
        return None, errors

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO transactions (user_id, amount, type, category, date, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, float(amount), type_, category.strip(), date.strip(), notes))
        conn.commit()
        return cursor.lastrowid, None
    except Exception as e:
        return None, [str(e)]
    finally:
        conn.close()


def get_all_transactions(user_id=None, type_=None, category=None, date_from=None, date_to=None):
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM transactions WHERE 1=1"
    params = []

    if user_id:
        query += " AND user_id = ?"
        params.append(user_id)
    if type_:
        query += " AND type = ?"
        params.append(type_)
    if category:
        query += " AND category = ?"
        params.append(category)
    if date_from:
        query += " AND date >= ?"
        params.append(date_from)
    if date_to:
        query += " AND date <= ?"
        params.append(date_to)

    query += " ORDER BY date DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_transaction_by_id(transaction_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_transaction(transaction_id, amount=None, type_=None, category=None, date=None, notes=None):
    existing = get_transaction_by_id(transaction_id)
    if not existing:
        return False, ["Transaction not found."]

    new_amount   = amount   if amount   is not None else existing['amount']
    new_type     = type_    if type_    is not None else existing['type']
    new_category = category if category is not None else existing['category']
    new_date     = date     if date     is not None else existing['date']
    new_notes    = notes    if notes    is not None else existing['notes']

    errors = validate_transaction(new_amount, new_type, new_category, new_date)
    if errors:
        return False, errors

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE transactions
            SET amount=?, type=?, category=?, date=?, notes=?
            WHERE id=?
        """, (float(new_amount), new_type, new_category, new_date, new_notes, transaction_id))
        conn.commit()
        return True, None
    except Exception as e:
        return False, [str(e)]
    finally:
        conn.close()


def delete_transaction(transaction_id):
    existing = get_transaction_by_id(transaction_id)
    if not existing:
        return False, "Transaction not found."

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
        conn.commit()
        return True, None
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()