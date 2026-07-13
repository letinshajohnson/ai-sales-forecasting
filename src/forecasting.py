import pandas as pd
import numpy as np
from datetime import timedelta
from src.eda import daily_totals


def _exponential_smoothing(series: pd.Series, alpha: float = 0.3) -> np.ndarray:
    """Simple exponential smoothing."""
    result = [series.iloc[0]]
    for val in series.iloc[1:]:
        result.append(alpha * val + (1 - alpha) * result[-1])
    return np.array(result)


def forecast_revenue(df: pd.DataFrame, days: int = 30) -> pd.DataFrame:
    """
    Forecast daily revenue for the next N days using:
    1. Exponential smoothing for trend
    2. Day-of-week seasonality adjustment
    3. Monthly seasonal factor
    Returns DataFrame with date, forecast, lower_bound, upper_bound.
    """
    daily = daily_totals(df).set_index("date").sort_index()
    series = daily["total_revenue"]

    # Smooth the series
    smoothed  = _exponential_smoothing(series, alpha=0.3)
    last_value = smoothed[-1]

    # Compute day-of-week multipliers from historical data
    daily["dow"] = pd.to_datetime(daily.index).dayofweek
    dow_avg = daily.groupby("dow")["total_revenue"].mean()
    overall_avg = daily["total_revenue"].mean()
    dow_factors = (dow_avg / overall_avg).to_dict()

    # Compute trend slope (linear regression over last 30 days)
    recent = series.tail(30).values
    x = np.arange(len(recent))
    slope = np.polyfit(x, recent, 1)[0]

    # Compute residual std for confidence intervals
    residuals = series.values - smoothed
    std = residuals.std()

    # Generate forecast
    last_date  = daily.index[-1]
    forecasts  = []

    for i in range(1, days + 1):
        future_date  = last_date + timedelta(days=i)
        dow          = future_date.dayofweek
        dow_factor   = dow_factors.get(dow, 1.0)
        trend_adj    = last_value + slope * i
        forecast_val = max(0, trend_adj * dow_factor)

        forecasts.append({
            "date":        future_date,
            "forecast":    round(forecast_val, 2),
            "lower_bound": round(max(0, forecast_val - 1.96 * std), 2),
            "upper_bound": round(forecast_val + 1.96 * std, 2),
            "day_name":    future_date.strftime("%A")
        })

    return pd.DataFrame(forecasts)


def forecast_by_product(df: pd.DataFrame, days: int = 30) -> pd.DataFrame:
    """Forecast revenue per product for the next N days."""
    results = []
    last_date = df["date"].max()

    for product_id, group in df.groupby("product_id"):
        product_name = group["product_name"].iloc[0]
        daily = group.groupby("date")["revenue"].sum().sort_index()

        if len(daily) < 7:
            continue

        smoothed   = _exponential_smoothing(daily, alpha=0.3)
        last_val   = smoothed[-1]
        recent     = daily.tail(14).values
        x          = np.arange(len(recent))
        slope      = np.polyfit(x, recent, 1)[0] if len(recent) > 1 else 0
        forecast   = max(0, last_val + slope * days)

        results.append({
            "product_id":      product_id,
            "product_name":    product_name,
            "current_avg_daily": round(daily.tail(7).mean(), 2),
            "forecast_total":  round(forecast * days, 2),
            "trend":           "↑ Growing" if slope > 0 else "↓ Declining"
        })

    return pd.DataFrame(results).sort_values("forecast_total", ascending=False)


def demand_forecast_for_restock(
    df: pd.DataFrame,
    inventory_df: pd.DataFrame,
    days: int = 14
) -> pd.DataFrame:
    """
    Combine sales forecast with current inventory to suggest restock quantities.
    Returns products at risk of stockout within the forecast period.
    """
    product_forecasts = forecast_by_product(df, days=days)

    # Daily forecast per product
    merged = product_forecasts.merge(
        inventory_df[["product_id", "product_name", "stock"]],
        on="product_id", how="left", suffixes=("_fc", "_inv")
    )
    merged["stock"] = merged["stock"].fillna(0)
    merged["estimated_demand"] = (merged["current_avg_daily"] * days).round()
    merged["days_until_stockout"] = (
        merged["stock"] / merged["current_avg_daily"].replace(0, np.nan)
    ).round(1)
    merged["restock_needed"] = merged["estimated_demand"] - merged["stock"]
    merged["restock_needed"] = merged["restock_needed"].clip(lower=0).round()
    merged["at_risk"] = merged["days_until_stockout"] <= days

    return merged[[
        "product_id", "product_name", "stock",
        "estimated_demand", "days_until_stockout",
        "restock_needed", "at_risk", "trend"
    ]].sort_values("days_until_stockout")
