import pandas as pd
import pymysql
from src.config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD


def get_connection():
    return pymysql.connect(
        host=DB_HOST, port=DB_PORT,
        db=DB_NAME, user=DB_USER,
        password=DB_PASSWORD,
        cursorclass=pymysql.cursors.DictCursor
    )


def load_sales_data(days: int = 365) -> pd.DataFrame:
    """
    Load raw sales transactions from the POS database.
    Returns a DataFrame with columns:
      date, product_id, product_name, category, quantity, revenue
    """
    query = f"""
        SELECT
            DATE(o.created_at)          AS date,
            p.id                        AS product_id,
            p.name                      AS product_name,
            p.category                  AS category,
            SUM(oi.quantity)            AS quantity,
            SUM(oi.subtotal)            AS revenue
        FROM orders o
        JOIN order_items oi ON oi.order_id = o.id
        JOIN products p     ON p.id = oi.product_id
        WHERE o.status = 'paid'
          AND o.created_at >= DATE_SUB(NOW(), INTERVAL {days} DAY)
        GROUP BY DATE(o.created_at), p.id
        ORDER BY date ASC
    """
    conn = get_connection()
    try:
        df = pd.read_sql(query, conn)
        df["date"] = pd.to_datetime(df["date"])
        return df
    finally:
        conn.close()


def load_inventory_data() -> pd.DataFrame:
    """Load current inventory levels."""
    query = """
        SELECT
            p.id        AS product_id,
            p.name      AS product_name,
            p.category  AS category,
            i.quantity  AS stock
        FROM inventory i
        JOIN products p ON p.id = i.product_id
        WHERE p.is_active = 1
    """
    conn = get_connection()
    try:
        return pd.read_sql(query, conn)
    finally:
        conn.close()


def generate_sample_data(days: int = 365) -> pd.DataFrame:
    """
    Generate realistic sample sales data for demo/testing.
    Includes trends, seasonality, and random noise.
    """
    import numpy as np
    from datetime import date, timedelta

    np.random.seed(42)

    products = [
        ("P001", "Rice 5kg",       "Grains"),
        ("P002", "Cooking Oil 1L", "Oils"),
        ("P003", "Sugar 1kg",      "Essentials"),
        ("P004", "Wheat Flour 1kg","Grains"),
        ("P005", "Milk 500ml",     "Dairy"),
        ("P006", "Butter 100g",    "Dairy"),
        ("P007", "Eggs (12)",      "Dairy"),
        ("P008", "Detergent 1kg",  "Household"),
        ("P009", "Shampoo 200ml",  "Personal Care"),
        ("P010", "Toothpaste",     "Personal Care"),
    ]

    records = []
    start   = date.today() - timedelta(days=days)

    for pid, pname, cat in products:
        base_qty = np.random.randint(20, 80)
        base_price = round(np.random.uniform(30, 200), 2)

        for d in range(days):
            current_date = start + timedelta(days=d)
            # Weekend boost
            weekend_factor = 1.4 if current_date.weekday() >= 5 else 1.0
            # Monthly trend (slow growth)
            trend_factor = 1 + (d / days) * 0.2
            # Seasonal variation (sin wave)
            seasonal = 1 + 0.15 * np.sin(2 * np.pi * d / 30)
            # Random noise
            noise = np.random.normal(1, 0.15)

            qty = max(0, int(base_qty * weekend_factor * trend_factor * seasonal * noise))
            if qty > 0:
                records.append({
                    "date":         pd.Timestamp(current_date),
                    "product_id":   pid,
                    "product_name": pname,
                    "category":     cat,
                    "quantity":     qty,
                    "revenue":      round(qty * base_price, 2)
                })

    return pd.DataFrame(records)
