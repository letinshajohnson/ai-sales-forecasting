import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from src.config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, REPORT_TO


def send_report_email(
    report_path: str,
    summary: dict,
    recipients: list = None
):
    """
    Send the weekly PDF report by email with an HTML summary.
    summary: dict with keys total_revenue, avg_daily, anomaly_count, at_risk_count
    """
    if not SMTP_USER or not SMTP_PASSWORD:
        print("⚠️  SMTP credentials not configured. Skipping email.")
        return

    recipients = recipients or REPORT_TO
    if not recipients or recipients == [""]:
        print("⚠️  No email recipients configured.")
        return

    msg = MIMEMultipart("alternative")
    msg["From"]    = SMTP_USER
    msg["To"]      = ", ".join(recipients)
    msg["Subject"] = f"📊 Weekly Sales Report — {datetime.now().strftime('%B %d, %Y')}"

    # HTML body
    html = f"""
    <html><body style="font-family: Arial, sans-serif; color: #1E2A3A; max-width: 600px; margin: auto;">
      <div style="background: #1A56DB; padding: 24px; border-radius: 12px; margin-bottom: 24px;">
        <h1 style="color: white; margin: 0; font-size: 22px;">📊 Weekly Sales Report</h1>
        <p style="color: #93C5FD; margin: 4px 0 0;">{datetime.now().strftime('%B %d, %Y')}</p>
      </div>

      <h2 style="font-size: 16px; color: #1E2A3A;">Key Metrics This Week</h2>
      <table style="width: 100%; border-collapse: collapse; margin-bottom: 24px;">
        <tr>
          <td style="padding: 12px; background: #EBF2FF; border-radius: 8px; margin: 4px; text-align: center;">
            <div style="font-size: 22px; font-weight: bold; color: #1A56DB;">₹{summary.get('total_revenue', 0):,.0f}</div>
            <div style="font-size: 12px; color: #64748B;">Total Revenue</div>
          </td>
          <td style="width: 8px;"></td>
          <td style="padding: 12px; background: #DCFCE7; border-radius: 8px; text-align: center;">
            <div style="font-size: 22px; font-weight: bold; color: #16A34A;">₹{summary.get('avg_daily', 0):,.0f}</div>
            <div style="font-size: 12px; color: #64748B;">Avg Daily Revenue</div>
          </td>
          <td style="width: 8px;"></td>
          <td style="padding: 12px; background: #FEF3C7; border-radius: 8px; text-align: center;">
            <div style="font-size: 22px; font-weight: bold; color: #D97706;">{summary.get('anomaly_count', 0)}</div>
            <div style="font-size: 12px; color: #64748B;">Anomalies Detected</div>
          </td>
          <td style="width: 8px;"></td>
          <td style="padding: 12px; background: #FEE2E2; border-radius: 8px; text-align: center;">
            <div style="font-size: 22px; font-weight: bold; color: #DC2626;">{summary.get('at_risk_count', 0)}</div>
            <div style="font-size: 12px; color: #64748B;">Products at Risk</div>
          </td>
        </tr>
      </table>

      <p style="color: #64748B; font-size: 14px;">
        The full detailed report with charts, forecasts, and restock recommendations
        is attached as a PDF.
      </p>

      <hr style="border: none; border-top: 1px solid #E2E8F0; margin: 24px 0;">
      <p style="color: #94A3B8; font-size: 12px;">
        Generated automatically by AI Sales Forecasting Tool
      </p>
    </body></html>
    """

    msg.attach(MIMEText(html, "html"))

    # Attach PDF
    if os.path.exists(report_path):
        with open(report_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={os.path.basename(report_path)}"
            )
            msg.attach(part)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, recipients, msg.as_string())
        print(f"✅ Report emailed to: {', '.join(recipients)}")
    except Exception as e:
        print(f"❌ Email failed: {e}")
