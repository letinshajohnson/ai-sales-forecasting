import os
from dotenv import load_dotenv

load_dotenv()

# Database
DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = int(os.getenv("DB_PORT", 3306))
DB_NAME     = os.getenv("DB_NAME", "pos_db")
DB_USER     = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

# Email (for automated reports)
SMTP_HOST     = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT     = int(os.getenv("SMTP_PORT", 587))
SMTP_USER     = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
REPORT_TO     = os.getenv("REPORT_TO", "").split(",")  # comma-separated emails

# Report output directory
REPORTS_DIR = os.getenv("REPORTS_DIR", "reports")

# Forecasting settings
FORECAST_DAYS      = int(os.getenv("FORECAST_DAYS", 30))
LOW_STOCK_THRESHOLD = int(os.getenv("LOW_STOCK_THRESHOLD", 10))
ANOMALY_THRESHOLD   = float(os.getenv("ANOMALY_THRESHOLD", 2.5))  # std deviations
