import pandas as pd
import numpy as np
from src.eda import daily_totals
from src.config import ANOMALY_THRESHOLD


def detect_revenue_anomalies(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    """
    Detect days with unusually high or low revenue using Z-score method.
    Returns DataFrame of anomalous days with severity and direction.
    """
    daily = daily_totals(df).set_index("date").sort_index()
    series = daily["total_revenue"]

    rolling_mean = series.rolling(window, min_periods=3).mean()
    rolling_std  = series.rolling(window, min_periods=3).std()

    z_scores = (series - rolling_mean) / rolling_std.replace(0, np.nan)

    anomalies = daily.copy()
    anomalies["z_score"]      = z_scores
    anomalies["rolling_mean"] = rolling_mean
    anomalies["is_anomaly"]   = z_scores.abs() > ANOMALY_THRESHOLD
    anomalies["direction"]    = np.where(z_scores > 0, "spike", "drop")
    anomalies["severity"]     = pd.cut(
        z_scores.abs(),
        bins=[0, 2, 3, np.inf],
        labels=["moderate", "high", "extreme"]
    )

    return anomalies[anomalies["is_anomaly"]].reset_index()


def detect_product_anomalies(df: pd.DataFrame, window: int = 7) -> pd.DataFrame:
    """Detect anomalies per product — sudden sales spikes or drops."""
    results = []

    for product_id, group in df.groupby("product_id"):
        product_name = group["product_name"].iloc[0]
        daily = group.groupby("date")["quantity"].sum().sort_index()

        if len(daily) < window + 2:
            continue

        rolling_mean = daily.rolling(window, min_periods=2).mean()
        rolling_std  = daily.rolling(window, min_periods=2).std()
        z_scores     = (daily - rolling_mean) / rolling_std.replace(0, np.nan)

        for date, z in z_scores.items():
            if abs(z) > ANOMALY_THRESHOLD:
                results.append({
                    "date":         date,
                    "product_id":   product_id,
                    "product_name": product_name,
                    "actual_qty":   int(daily[date]),
                    "expected_qty": round(rolling_mean[date], 1),
                    "z_score":      round(z, 2),
                    "direction":    "spike" if z > 0 else "drop"
                })

    return pd.DataFrame(results).sort_values("date", ascending=False) if results else pd.DataFrame()


def stockout_risk(df: pd.DataFrame, inventory_df: pd.DataFrame) -> pd.DataFrame:
    """Flag products at risk of stocking out based on recent sales velocity."""
    from src.config import LOW_STOCK_THRESHOLD

    # Average daily sales per product over last 14 days
    recent = df[df["date"] >= df["date"].max() - pd.Timedelta(days=14)]
    avg_daily = recent.groupby("product_id")["quantity"].mean().reset_index()
    avg_daily.columns = ["product_id", "avg_daily_sales"]

    merged = inventory_df.merge(avg_daily, on="product_id", how="left")
    merged["avg_daily_sales"] = merged["avg_daily_sales"].fillna(0)
    merged["days_of_stock"]   = (
        merged["stock"] / merged["avg_daily_sales"].replace(0, np.nan)
    ).round(1)
    merged["risk_level"] = pd.cut(
        merged["days_of_stock"],
        bins=[-np.inf, 3, 7, 14, np.inf],
        labels=["critical", "high", "medium", "ok"]
    )

    return merged[merged["risk_level"].isin(["critical", "high", "medium"])]\
        .sort_values("days_of_stock")\
        [["product_id", "product_name", "stock", "avg_daily_sales", "days_of_stock", "risk_level"]]
