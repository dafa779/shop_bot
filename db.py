import time
import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from contextlib import contextmanager
from config import DATABASE_URL

_pool = ThreadedConnectionPool(1, 10, dsn=DATABASE_URL)

def get_conn():
    return _pool.getconn()

def put_conn(conn):
    _pool.putconn(conn)

@contextmanager
def get_db(commit=False):
    conn = None
    cur = None
    try:
        conn = get_conn()
        conn.autocommit = not commit
        cur = conn.cursor()
        yield conn, cur
        if commit:
            conn.commit()
    except Exception:
        if conn and commit:
            conn.rollback()
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            put_conn(conn)

def init_db():
    with get_db(commit=True) as (_, cur):
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            balance DOUBLE PRECISION DEFAULT 0,
            created_at BIGINT NOT NULL
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id BIGSERIAL PRIMARY KEY,
            code TEXT UNIQUE,
            title TEXT NOT NULL
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id BIGSERIAL PRIMARY KEY,
            category_id BIGINT REFERENCES categories(id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            price DOUBLE PRECISION NOT NULL,
            stock INTEGER DEFAULT 0,
            description TEXT DEFAULT ''
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id BIGSERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            product_id BIGINT REFERENCES products(id),
            quantity INTEGER NOT NULL,
            amount DOUBLE PRECISION NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at BIGINT NOT NULL
        )
        """)

def upsert_user(user_id, username="", full_name=""):
    with get_db(commit=True) as (_, cur):
        cur.execute("""
        INSERT INTO users(user_id, username, full_name, created_at)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT(user_id) DO UPDATE SET
            username=EXCLUDED.username,
            full_name=EXCLUDED.full_name
        """, (int(user_id), username, full_name, int(time.time())))

def get_user(user_id):
    with get_db() as (_, cur):
        cur.execute("""
        SELECT user_id, username, full_name, balance, created_at
        FROM users
        WHERE user_id=%s
        """, (int(user_id),))
        return cur.fetchone()

def get_categories():
    with get_db() as (_, cur):
        cur.execute("""
        SELECT id, code, title
        FROM categories
        ORDER BY id ASC
        """)
        return cur.fetchall()

def get_products_by_category(category_id):
    with get_db() as (_, cur):
        cur.execute("""
        SELECT id, title, price, stock, description
        FROM products
        WHERE category_id=%s
        ORDER BY id ASC
        """, (int(category_id),))
        return cur.fetchall()

def get_product(product_id):
    with get_db() as (_, cur):
        cur.execute("""
        SELECT id, category_id, title, price, stock, description
        FROM products
        WHERE id=%s
        """, (int(product_id),))
        return cur.fetchone()

def create_order(user_id, product_id, quantity, amount):
    with get_db(commit=True) as (_, cur):
        cur.execute("""
        INSERT INTO orders(user_id, product_id, quantity, amount, status, created_at)
        VALUES (%s, %s, %s, %s, 'pending', %s)
        RETURNING id
        """, (int(user_id), int(product_id), int(quantity), float(amount), int(time.time())))
        return cur.fetchone()[0]

def get_user_orders(user_id):
    with get_db() as (_, cur):
        cur.execute("""
        SELECT o.id, p.title, o.quantity, o.amount, o.status, o.created_at
        FROM orders o
        LEFT JOIN products p ON p.id = o.product_id
        WHERE o.user_id=%s
        ORDER BY o.id DESC
        """, (int(user_id),))
        return cur.fetchall()

def seed_sample_data():
    with get_db(commit=True) as (_, cur):
        cur.execute("SELECT COUNT(*) FROM categories")
        if (cur.fetchone() or [0])[0] > 0:
            return

        categories = [
            ("fancy", "✨ Fancy Number"),
            ("country", "🌍 Country / Area Code"),
            ("aged", "💎 Aged Accounts"),
            ("energy", "⚡ Energy Rental"),
        ]

        cat_ids = {}
        for code, title in categories:
            cur.execute("""
            INSERT INTO categories(code, title)
            VALUES (%s, %s)
            RETURNING id
            """, (code, title))
            cat_ids[code] = cur.fetchone()[0]

        products = [
            (cat_ids["fancy"], "Random 5A Fancy Number Ending with Digit 1", 6.62, 8, "All accounts are guaranteed for first-login."),
            (cat_ids["country"], "+84 Vietnam~February-May", 0.95, 85, "Session / API Link available."),
            (cat_ids["country"], "+66 Thailand~February-May", 1.47, 1281, "Session / API Link available."),
            (cat_ids["country"], "+1 USA~February-May", 0.60, 7214, "Session / API Link available."),
            (cat_ids["aged"], "1-2 Year Old Accounts", 9.99, 120, "Suitable for long-term usage."),
            (cat_ids["aged"], "3-4 Year Old Accounts", 19.99, 65, "Higher trust age."),
            (cat_ids["energy"], "TRON Energy Flash Rental", 2.50, 999, "Fast rental for TRX network."),
        ]

        for category_id, title, price, stock, description in products:
            cur.execute("""
            INSERT INTO products(category_id, title, price, stock, description)
            VALUES (%s, %s, %s, %s, %s)
            """, (category_id, title, price, stock, description))

