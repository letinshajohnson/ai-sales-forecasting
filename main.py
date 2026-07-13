"""
AI Sales Forecasting Tool — Main Pipeline
Run: python main.py [--demo] [--email] [--days 30]
"""
import argparse
import pandas as pd
from src.data_loader import load_sales_data, load_inventory_data, generate_sample_data
from src.eda import (clean_data, add_time_features, daily_totals,
                     category_summary, top_products, moving_averages)
from src.forecasting import (forecast_revenue, forecast_by_product,
                              demand_forecast_for_restock)
from src.anomaly_detection import (detect_revenue_anomalies,
                                   detect_product_anomalies, stockout_risk)
from src.report_generator import generate_pdf_report
from src.email_sender import send_report_email
from src.config import FORECAST_DAYS


def run_pipeline(use_demo: bool = False, send_email: bool = False, days: int = 365):
    print("\n🚀 AI Sales Forecasting Pipeline Starting...")
    print("=" * 55)

    # ── 1. Load Data ─────────────────────────────────────────
    print("\n📥 Step 1: Loading data...")
    if use_demo:
        print("   Using demo data (no DB connection needed)")
        raw_df       = generate_sample_data(days=days)
        inventory_df = pd.DataFrame({
            "product_id":   [f"P{str(i).zfill(3)}" for i in range(1, 11)],
            "product_name": ["Rice 5kg","Cooking Oil 1L","Sugar 1kg","Wheat Flour 1kg",
                             "Milk 500ml","Butter 100g","Eggs (12)","Detergent 1kg",
                             "Shampoo 200ml","Toothpaste"],
            "stock": [5, 50, 12, 3, 80, 25, 8, 60, 15, 40]
        })
    else:
        raw_df       = load_sales_data(days=days)
        inventory_df = load_inventory_data()
    print(f"   ✅ Loaded {len(raw_df):,} records across {raw_df['product_id'].nunique()} products")

    # ── 2. Clean & Engineer Features ─────────────────────────
    print("\n🧹 Step 2: Cleaning data & engineering features...")
    df       = clean_data(raw_df)
    df       = add_time_features(df)
    daily_df = moving_averages(df)
    print(f"   ✅ Date range: {df['date'].min().date()} → {df['date'].max().date()}")

    # ── 3. EDA Summary ───────────────────────────────────────
    print("\n📊 Step 3: Running exploratory analysis...")
    cat_df  = category_summary(df)
    top_df  = top_products(df, n=10)
    print(f"   ✅ {len(cat_df)} categories | Top product: {top_df.iloc[0]['product_name']}")
    print(f"   ✅ Total revenue: ₹{df['revenue'].sum():,.0f}")
    print(f"   ✅ Avg daily revenue: ₹{daily_df['total_revenue'].mean():,.0f}")

    # ── 4. Forecasting ───────────────────────────────────────
    print(f"\n🔮 Step 4: Forecasting next {FORECAST_DAYS} days...")
    forecast_df = forecast_revenue(df, days=FORECAST_DAYS)
    restock_df  = demand_forecast_for_restock(df, inventory_df, days=14)
    print(f"   ✅ Forecast range: {forecast_df['date'].min().date()} → {forecast_df['date'].max().date()}")
    print(f"   ✅ Expected revenue: ₹{forecast_df['forecast'].sum():,.0f}")
    at_risk = restock_df[restock_df.get('at_risk', pd.Series(False))] if 'at_risk' in restock_df.columns else pd.DataFrame()
    print(f"   ✅ Products at stockout risk: {len(at_risk)}")

    # ── 5. Anomaly Detection ─────────────────────────────────
    print("\n🔍 Step 5: Detecting anomalies...")
    anomalies_df         = detect_revenue_anomalies(df)
    product_anomalies_df = detect_product_anomalies(df)
    stockout_df          = stockout_risk(df, inventory_df)
    print(f"   ✅ Revenue anomalies: {len(anomalies_df)}")
    print(f"   ✅ Product anomalies: {len(product_anomalies_df)}")
    print(f"   ✅ Stockout risks: {len(stockout_df)}")

    if len(anomalies_df) > 0:
        print("\n   📌 Top anomalies:")
        for _, row in anomalies_df.head(3).iterrows():
            print(f"      {row['date'].strftime('%b %d')} — {row['direction'].upper()} "
                  f"(₹{row['total_revenue']:,.0f}, z={row['z_score']:.1f})")

    # ── 6. Generate PDF Report ───────────────────────────────
    print("\n📄 Step 6: Generating PDF report...")
    report_path = generate_pdf_report(
        daily_df       = daily_df,
        forecast_df    = forecast_df,
        top_products_df = top_df,
        category_df    = cat_df,
        anomalies_df   = anomalies_df,
        restock_df     = restock_df,
        raw_df         = df
    )

    # ── 7. Email Report ──────────────────────────────────────
    if send_email:
        print("\n📧 Step 7: Sending email report...")
        summary = {
            "total_revenue":  df["revenue"].sum(),
            "avg_daily":      daily_df["total_revenue"].mean(),
            "anomaly_count":  len(anomalies_df),
            "at_risk_count":  len(at_risk)
        }
        send_report_email(report_path, summary)

    print("\n" + "=" * 55)
    print("✅ Pipeline complete!")
    print(f"📁 Report: {report_path}")
    return report_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Sales Forecasting Tool")
    parser.add_argument("--demo",  action="store_true", help="Use demo data instead of DB")
    parser.add_argument("--email", action="store_true", help="Send report by email")
    parser.add_argument("--days",  type=int, default=365, help="Days of history to analyze")
    args = parser.parse_args()

    run_pipeline(use_demo=args.demo, send_email=args.email, days=args.days)
