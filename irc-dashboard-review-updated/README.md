# IRC Utility Operations Dashboard

Client-safe Streamlit dashboard for reviewing dialysis center utility cost, usage, treatments, anomalies, property scorecards, geographic location views, and a one-page monthly summary report.

## Data source

This repo is preconfigured to read the shared Google Sheet:

```python
GOOGLE_SHEET_ID = "1_4coHOmEkzY9cLYRtqmnUJ51LuqeY6yz"
GOOGLE_SHEET_GID = "910919948"
```

The dashboard uses **Month + Year** as the reporting period. It does **not** use Billing Date for month selection, trend logic, anomalies, or missing bill logic.

## Review-driven updates included

- Defaults to the **most recently completed month** instead of the current calendar month.
- Redesigns the portfolio trend section as a **year-over-year cost comparison**.
- Clarifies that **cost per usage is an indicator**, not an exact utility rate.
- Simplifies the Property Scorecard property selection when a single property is already selected in the top filter.
- Removes cost per treatment from the same property trend chart scale and shows it separately.
- Keeps utility cost mix and condensed billing history.
- Refines Geographic View highest-cost property reporting by utility type instead of blended all-utility totals.
- Keeps the dashboard client-safe with no raw data explorer, no raw CSV/Excel export, and no account/meter/raw-read fields displayed.

## Pages

- Operations Command Center
- Exception Center
- Property Scorecard
- Geographic View
- Monthly Summary Report

## Deploying to Streamlit Cloud

Main file path:

```text
app.py
```

Set the password in Streamlit Secrets if you do not want to use the placeholder in `config.py`:

```toml
APP_PASSWORD = "your-password-here"
```

## Monthly report email automation

The repo includes a script/workflow structure for monthly PDF email automation. Keep the workflow disabled until the report output is approved.
