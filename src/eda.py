import pandas as pd
import numpy as np


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and validate raw sales data."""
    df = df.copy()
    df["date"]     = pd.to_datetime(df["date"])
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0).astype(int)
    df["revenue"]  = pd.to_numeric(df["revenue"],  errors="coerce").fillna(0.0)
    df = df[df["quantity"] >= 0]
    df = df[df["revenue"]  >= 0]
    df = df.drop_duplicates()
    return df.sort_values("date").reset_index(drop=True)


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add calendar-based features for analysis and modelling."""
    df = df.copy()
    df["day_of_week"] = df["date"].dt.dayofweek        # 0=Mon, 6=Sun
    df["day_name"]    = df["date"].dt.day_name()
    df["week"]        = df["date"].dt.isocalendar().week.astype(int)
    df["month"]       = df["date"].dt.month
    df["month_name"]  = df["date"].dt.month_name()
    df["quarter"]     = df["date"].dt.quarter
    df["year"]        = df["date"].dt.year
    df["is_weekend"]  = df["day_of_week"].isin([5, 6]).astype(int)
    return df


def daily_totals(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate to daily totals across all products."""
    return (
        df.groupby("date")
          .agg(total_quantity=("quantity", "sum"),
               total_revenue=("revenue",  "sum"),
               num_products=("product_id", "nunique"))
          .reset_index()
    )


def category_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Revenue and quantity breakdown by product category."""
    return (
        df.groupby("category")
          .agg(total_quantity=("quantity", "sum"),
               total_revenue=("revenue",  "sum"),
               avg_daily_revenue=("revenue", "mean"))
          .sort_values("total_revenue", ascending=False)
          .reset_index()
    )


def top_products(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Top N products by total revenue."""
    return (
        df.groupby(["product_id", "product_name", "category"])
          .agg(total_quantity=("quantity", "sum"),
               total_revenue=("revenue",  "sum"))
          .sort_values("total_revenue", ascending=False)
          .head(n)
          .reset_index()
    )


def weekly_trends(df: pd.DataFrame) -> pd.DataFrame:
    """Weekly revenue aggregation for trend visualization."""
    df = df.copy()
    df["week_start"] = df["date"] - pd.to_timedelta(df["date"].dt.dayofweek, unit="D")
    return (
        df.groupby("week_start")
          .agg(total_revenue=("revenue", "sum"),
               total_quantity=("quantity", "sum"))
          .reset_index()
    )


def moving_averages(df: pd.DataFrame, windows: list = [7, 14, 30]) -> pd.DataFrame:
    """Add rolling averages to daily totals."""
    daily = daily_totals(df).set_index("date")
    for w in windows:
        daily[f"revenue_ma{w}"] = daily["total_revenue"].rolling(w, min_periods=1).mean()
    return daily.reset_index()
