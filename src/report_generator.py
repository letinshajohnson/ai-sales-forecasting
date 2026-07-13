import os
import io
from datetime import datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
import numpy as np
from src.config import REPORTS_DIR

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "figure.facecolor": "white",
    "axes.facecolor": "#f8fafc"
})

PRIMARY = "#1A56DB"
ACCENT  = "#16A34A"
DANGER  = "#DC2626"
GRAY    = "#64748B"


def _fig_to_bytes(fig) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    buf.seek(0)
    return buf.read()


def plot_revenue_trend(daily_df: pd.DataFrame, forecast_df: pd.DataFrame) -> plt.Figure:
    """Revenue history + forecast chart."""
    fig, ax = plt.subplots(figsize=(12, 5))

    # Historical
    ax.plot(daily_df["date"], daily_df["total_revenue"],
            color=PRIMARY, linewidth=1.5, label="Actual Revenue", alpha=0.8)

    # 7-day MA
    if "revenue_ma7" in daily_df.columns:
        ax.plot(daily_df["date"], daily_df["revenue_ma7"],
                color=PRIMARY, linewidth=2.5, linestyle="--", label="7-Day Moving Avg")

    # Forecast
    if not forecast_df.empty:
        ax.plot(forecast_df["date"], forecast_df["forecast"],
                color=ACCENT, linewidth=2, linestyle="--", label="Forecast")
        ax.fill_between(forecast_df["date"],
                        forecast_df["lower_bound"], forecast_df["upper_bound"],
                        color=ACCENT, alpha=0.15, label="95% Confidence Band")

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    plt.xticks(rotation=30)
    ax.set_title("Revenue Trend & 30-Day Forecast", fontsize=14, fontweight="bold", pad=15)
    ax.set_ylabel("Revenue (₹)")
    ax.legend(loc="upper left", framealpha=0.9)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
    plt.tight_layout()
    return fig


def plot_top_products(top_df: pd.DataFrame) -> plt.Figure:
    """Horizontal bar chart of top products by revenue."""
    fig, ax = plt.subplots(figsize=(10, 5))
    top_df = top_df.head(10).sort_values("total_revenue")

    colors = [PRIMARY if i >= len(top_df) - 3 else GRAY
              for i in range(len(top_df))]

    bars = ax.barh(top_df["product_name"], top_df["total_revenue"],
                   color=colors, height=0.6, edgecolor="white")

    for bar, val in zip(bars, top_df["total_revenue"]):
        ax.text(bar.get_width() + max(top_df["total_revenue"]) * 0.01,
                bar.get_y() + bar.get_height() / 2,
                f"₹{val:,.0f}", va="center", fontsize=9, color=GRAY)

    ax.set_title("Top 10 Products by Revenue", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Total Revenue (₹)")
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
    plt.tight_layout()
    return fig


def plot_category_breakdown(category_df: pd.DataFrame) -> plt.Figure:
    """Pie chart of revenue by category."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Pie chart
    colors = plt.cm.Set3(np.linspace(0, 1, len(category_df)))
    wedges, texts, autotexts = ax1.pie(
        category_df["total_revenue"],
        labels=category_df["category"],
        autopct="%1.1f%%",
        colors=colors,
        startangle=90,
        pctdistance=0.85
    )
    for t in autotexts:
        t.set_fontsize(9)
    ax1.set_title("Revenue by Category", fontsize=13, fontweight="bold")

    # Bar chart
    ax2.bar(category_df["category"], category_df["total_revenue"],
            color=colors, edgecolor="white")
    ax2.set_title("Category Revenue Comparison", fontsize=13, fontweight="bold")
    ax2.set_ylabel("Revenue (₹)")
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    return fig


def plot_anomalies(daily_df: pd.DataFrame, anomalies_df: pd.DataFrame) -> plt.Figure:
    """Revenue chart with anomaly markers."""
    fig, ax = plt.subplots(figsize=(12, 5))

    ax.plot(daily_df["date"], daily_df["total_revenue"],
            color=PRIMARY, linewidth=1.5, alpha=0.7, label="Revenue")

    if not anomalies_df.empty:
        spikes = anomalies_df[anomalies_df["direction"] == "spike"]
        drops  = anomalies_df[anomalies_df["direction"] == "drop"]

        if not spikes.empty:
            ax.scatter(spikes["date"], spikes["total_revenue"],
                       color=ACCENT, s=80, zorder=5, label="Revenue Spike", marker="^")
        if not drops.empty:
            ax.scatter(drops["date"], drops["total_revenue"],
                       color=DANGER, s=80, zorder=5, label="Revenue Drop", marker="v")

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    plt.xticks(rotation=30)
    ax.set_title("Revenue Anomaly Detection", fontsize=14, fontweight="bold", pad=15)
    ax.set_ylabel("Revenue (₹)")
    ax.legend(framealpha=0.9)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
    plt.tight_layout()
    return fig


def plot_weekly_heatmap(df: pd.DataFrame) -> plt.Figure:
    """Heatmap of avg revenue by day of week and month."""
    df = df.copy()
    df["dow"]   = df["date"].dt.day_name()
    df["month"] = df["date"].dt.month_name()

    pivot = df.pivot_table(
        values="revenue", index="dow", columns="month",
        aggfunc="mean"
    )
    dow_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    pivot = pivot.reindex([d for d in dow_order if d in pivot.index])

    fig, ax = plt.subplots(figsize=(12, 4))
    im = ax.imshow(pivot.values, cmap="Blues", aspect="auto")
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_yticks(range(len(pivot.index)))
    ax.set_xticklabels(pivot.columns, rotation=30, ha="right")
    ax.set_yticklabels(pivot.index)
    plt.colorbar(im, ax=ax, label="Avg Revenue (₹)")
    ax.set_title("Revenue Heatmap: Day of Week × Month", fontsize=13, fontweight="bold", pad=15)
    plt.tight_layout()
    return fig


def generate_pdf_report(
    daily_df,
    forecast_df,
    top_products_df,
    category_df,
    anomalies_df,
    restock_df,
    raw_df
) -> str:
    """
    Generate a full PDF report with all charts and tables.
    Saves to reports/ directory and returns the file path.
    """
    os.makedirs(REPORTS_DIR, exist_ok=True)
    timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(REPORTS_DIR, f"sales_report_{timestamp}.pdf")

    with PdfPages(report_path) as pdf:
        # ── Cover page ──────────────────────────────────────────────────
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.axis("off")
        ax.text(0.5, 0.7, "📊 Sales Analytics Report",
                ha="center", va="center", fontsize=28, fontweight="bold",
                color=PRIMARY, transform=ax.transAxes)
        ax.text(0.5, 0.55, f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}",
                ha="center", va="center", fontsize=14, color=GRAY, transform=ax.transAxes)

        # KPI summary
        total_rev  = daily_df["total_revenue"].sum()
        total_qty  = daily_df["total_quantity"].sum()
        num_days   = len(daily_df)
        avg_daily  = daily_df["total_revenue"].mean()
        fc_total   = forecast_df["forecast"].sum() if not forecast_df.empty else 0

        kpis = [
            ("Total Revenue",       f"₹{total_rev:,.0f}"),
            ("Total Orders (days)", f"{num_days:,}"),
            ("Avg Daily Revenue",   f"₹{avg_daily:,.0f}"),
            ("30-Day Forecast",     f"₹{fc_total:,.0f}"),
            ("Anomalies Detected",  str(len(anomalies_df))),
            ("Products at Risk",    str(len(restock_df[restock_df.get('at_risk', pd.Series(False))])
                                        if 'at_risk' in restock_df.columns else 0)),
        ]
        for i, (label, value) in enumerate(kpis):
            x = 0.15 + (i % 3) * 0.3
            y = 0.35 - (i // 3) * 0.12
            ax.text(x, y, value, ha="center", fontsize=18, fontweight="bold",
                    color=PRIMARY, transform=ax.transAxes)
            ax.text(x, y - 0.05, label, ha="center", fontsize=10, color=GRAY,
                    transform=ax.transAxes)
        pdf.savefig(fig, bbox_inches="tight"); plt.close()

        # ── Charts ──────────────────────────────────────────────────────
        for chart_fn, args in [
            (plot_revenue_trend,    (daily_df, forecast_df)),
            (plot_top_products,     (top_products_df,)),
            (plot_category_breakdown, (category_df,)),
            (plot_anomalies,        (daily_df, anomalies_df)),
            (plot_weekly_heatmap,   (raw_df,)),
        ]:
            fig = chart_fn(*args)
            pdf.savefig(fig, bbox_inches="tight"); plt.close()

        # ── Restock table ────────────────────────────────────────────────
        if not restock_df.empty:
            fig, ax = plt.subplots(figsize=(12, max(3, len(restock_df) * 0.4 + 1)))
            ax.axis("off")
            ax.set_title("Restock Recommendations", fontsize=14, fontweight="bold",
                         pad=15, loc="left")
            cols = ["product_name", "stock", "estimated_demand", "days_until_stockout",
                    "restock_needed", "trend"]
            cols = [c for c in cols if c in restock_df.columns]
            table = ax.table(
                cellText=restock_df[cols].round(1).values,
                colLabels=[c.replace("_", " ").title() for c in cols],
                cellLoc="center", loc="center"
            )
            table.auto_set_font_size(False)
            table.set_fontsize(9)
            table.scale(1, 1.5)
            for (r, c), cell in table.get_celld().items():
                if r == 0:
                    cell.set_facecolor(PRIMARY)
                    cell.set_text_props(color="white", fontweight="bold")
                elif r % 2 == 0:
                    cell.set_facecolor("#f0f4ff")
            pdf.savefig(fig, bbox_inches="tight"); plt.close()

        # PDF metadata
        d = pdf.infodict()
        d["Title"]   = "Sales Analytics Report"
        d["Author"]  = "AI Sales Forecasting Tool"
        d["Subject"] = "Sales Trends, Forecasts, Anomalies, Restock"

    print(f"✅ Report saved: {report_path}")
    return report_path
