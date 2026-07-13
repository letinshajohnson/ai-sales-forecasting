# 📈 AI Sales Forecasting & Analytics Tool

![Status](https://img.shields.io/badge/Status-Production%20Ready-green?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)
![Pandas](https://img.shields.io/badge/Pandas-2.2-150458?style=flat-square&logo=pandas)
![Matplotlib](https://img.shields.io/badge/Matplotlib-3.8-11557C?style=flat-square)
![scikit--learn](https://img.shields.io/badge/scikit--learn-1.4-F7931E?style=flat-square&logo=scikit-learn)
![License](https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square)

An end-to-end Python data pipeline that ingests POS/sales transaction data, performs exploratory analysis, generates **30-day revenue forecasts**, detects **anomalies**, produces **automated PDF reports**, and emails them to stakeholders every Monday — with zero manual effort.

---

## ✨ Features

- 📥 **Data Pipeline** — Connects to MySQL POS database or runs with built-in demo data
- 🧹 **Data Cleaning** — Handles missing values, duplicates, and outliers automatically
- 📊 **EDA** — Revenue trends, top products, category breakdown, day-of-week patterns
- 🔮 **30-Day Forecast** — Exponential smoothing + trend + seasonality with confidence bands
- 🛒 **Restock Recommendations** — Flags products at stockout risk within 14 days
- 🔍 **Anomaly Detection** — Z-score method detects revenue spikes and drops automatically
- 📄 **PDF Report** — Professional multi-page report with charts, KPI summary, and restock table
- 📧 **Automated Email** — Sends HTML email + PDF attachment every Monday at 08:00
- ⏰ **Scheduler** — Built-in weekly scheduler, no cron setup needed

---

## 🏗️ Pipeline Architecture

```
MySQL DB / Demo Data
        ↓
   data_loader.py     ← Load raw transactions
        ↓
      eda.py          ← Clean, feature engineer, aggregate
        ↓
   forecasting.py     ← 30-day revenue + product forecasts
        ↓
anomaly_detection.py  ← Z-score anomaly + stockout risk
        ↓
report_generator.py   ← matplotlib charts → PDF
        ↓
  email_sender.py     ← HTML email + PDF attachment
        ↓
    scheduler.py      ← Run every Monday 08:00
```

---

## 📊 Report Contents

Each generated PDF includes:

| Page | Content |
|---|---|
| **Cover** | KPI summary: total revenue, avg daily, forecast, anomaly count |
| **Page 2** | Revenue trend line + 30-day forecast with confidence band |
| **Page 3** | Top 10 products by revenue (horizontal bar chart) |
| **Page 4** | Category revenue breakdown (pie + bar chart) |
| **Page 5** | Anomaly detection chart (spikes and drops highlighted) |
| **Page 6** | Revenue heatmap — day of week × month |
| **Page 7** | Restock recommendations table |

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| **Data Processing** | Python, Pandas, NumPy |
| **Forecasting** | Exponential Smoothing, Linear Trend, Seasonality |
| **Anomaly Detection** | Z-score (rolling window) |
| **Visualization** | Matplotlib |
| **PDF Generation** | Matplotlib PdfPages |
| **Email** | Python smtplib + MIME |
| **Scheduler** | schedule library |
| **Database** | MySQL via pymysql |

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/letinshajohnson/ai-sales-forecasting.git
cd ai-sales-forecasting
```

### 2. Install dependencies
```bash
python -m venv venv
source venv/bin/activate     # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment
```bash
cp .env.example .env
# Edit .env with your DB credentials and email settings
```

### 4. Run with demo data (no DB needed)
```bash
python main.py --demo
```

### 5. Run with your database
```bash
python main.py
```

### 6. Run and send email report
```bash
python main.py --demo --email
```

### 7. Start the weekly scheduler
```bash
python scheduler.py
```

---

## 📁 Project Structure

```
ai-sales-forecasting/
│
├── main.py                    # Pipeline entry point + CLI
├── scheduler.py               # Weekly automated scheduler
├── requirements.txt
├── .env.example
│
├── src/
│   ├── __init__.py
│   ├── config.py              # All settings from .env
│   ├── data_loader.py         # MySQL loader + demo data generator
│   ├── eda.py                 # Cleaning, feature engineering, aggregations
│   ├── forecasting.py         # Revenue forecast + product forecast + restock
│   ├── anomaly_detection.py   # Z-score anomaly + stockout risk detection
│   ├── report_generator.py    # All charts + PDF generation
│   └── email_sender.py        # HTML email + PDF attachment sender
│
├── reports/                   # Generated PDF reports (gitignored)
└── data/                      # Optional CSV data files
```

---

## 🔮 How Forecasting Works

```
Historical daily revenue
        ↓
Exponential Smoothing (α=0.3)
→ Reduces noise, captures recent trend
        ↓
Linear Trend Extraction
→ Slope from last 30 days of data
        ↓
Day-of-Week Seasonality
→ Each day gets a multiplier (e.g. Sunday = 1.4x)
        ↓
Combined Forecast
= (smoothed_base + trend × day) × day_of_week_factor
        ↓
Confidence Bands
→ ±1.96 × residual std (95% interval)
```

---

## 🔍 How Anomaly Detection Works

```
Daily revenue series
        ↓
Rolling 14-day mean and std dev calculated
        ↓
Z-score = (actual - rolling_mean) / rolling_std
        ↓
|z| > 2.5  →  flagged as anomaly
        ↓
z > 0  →  Revenue Spike  ↑
z < 0  →  Revenue Drop   ↓
        ↓
Severity: moderate (2.5-3.0) | high (3.0-inf) | extreme
```

---

## ⏰ Automation Schedule

```
Monday 08:00 AM
      ↓
Pipeline runs automatically:
  1. Load last 365 days from DB
  2. Generate all analysis + charts
  3. Create PDF report
  4. Send HTML email + PDF to all recipients

No manual intervention needed — set once, runs forever.
```

---

## 🗺️ Roadmap

- [x] MySQL data ingestion pipeline
- [x] EDA and feature engineering
- [x] 30-day revenue forecasting
- [x] Per-product forecasting
- [x] Stockout risk analysis
- [x] Z-score anomaly detection
- [x] Multi-page PDF report generation
- [x] HTML email with PDF attachment
- [x] Weekly automated scheduler
- [x] Built-in demo data generator
- [ ] FastAPI dashboard (REST endpoints)
- [ ] React frontend for interactive charts
- [ ] Prophet model integration for better seasonality
- [ ] Slack/WhatsApp alert integration
- [ ] Docker deployment

---

## 👩‍💻 Author

**Letinsha Johnson**
Senior Software Engineer · AI Specialist
📧 letinshajohnson@gmail.com
🔗 [linkedin.com/in/letinsha-johnson-3b21a5256](https://linkedin.com/in/letinsha-johnson-3b21a5256)
🐙 [github.com/letinshajohnson](https://github.com/letinshajohnson)

---
