from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from pathlib import Path

import pandas as pd

from utils.alerts import build_alerts, alert_counts
from utils.calculations import selected_previous_month
from utils.data_loader import load_data
from utils.reporting import generate_monthly_pdf, monthly_takeaways


def _latest_month(df: pd.DataFrame):
    months = sorted(pd.to_datetime(df["billing_month"].dropna().unique()))
    return months[-1] if months else None


def _send_email(subject: str, body: str, pdf_bytes: bytes, filename: str):
    to = os.getenv("REPORT_EMAIL_TO", "").strip()
    sender = os.getenv("REPORT_EMAIL_FROM", os.getenv("SMTP_USERNAME", "")).strip()
    username = os.getenv("SMTP_USERNAME", "").strip()
    password = os.getenv("SMTP_PASSWORD", "").strip()
    host = os.getenv("SMTP_HOST", "smtp.gmail.com").strip()
    port = int(os.getenv("SMTP_PORT", "587"))

    if not (to and sender and username and password):
        print("Email secrets are not fully configured. PDF was generated but email was skipped.")
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to
    msg.set_content(body)
    msg.add_attachment(pdf_bytes, maintype="application", subtype="pdf", filename=filename)

    with smtplib.SMTP(host, port) as smtp:
        smtp.starttls()
        smtp.login(username, password)
        smtp.send_message(msg)
    print(f"Sent monthly report to {to}")


def main():
    df = load_data()
    current_month = _latest_month(df)
    if current_month is None:
        raise RuntimeError("No reporting month found in sheet.")
    previous_month = selected_previous_month(df, current_month)
    pdf_bytes = generate_monthly_pdf(df, current_month, previous_month)
    month_label = pd.to_datetime(current_month).strftime("%B %Y")
    filename = f"utility-summary-{pd.to_datetime(current_month).strftime('%Y-%m')}.pdf"
    out_path = Path(filename)
    out_path.write_bytes(pdf_bytes)

    alerts = build_alerts(df, current_month, previous_month)
    counts = alert_counts(alerts)
    takeaways = monthly_takeaways(df, current_month, previous_month, alerts)[:4]
    body = f"Attached is the {month_label} Utility Summary Report.\n\n"
    body += f"Alerts: {counts['Critical']} critical / {counts['Review']} review.\n\n"
    body += "Highlights:\n" + "\n".join(f"- {x}" for x in takeaways)
    _send_email(f"Monthly Utility Summary Report - {month_label}", body, pdf_bytes, filename)


if __name__ == "__main__":
    main()
