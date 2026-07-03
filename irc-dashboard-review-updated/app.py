import pandas as pd
import streamlit as st

from utils.auth import require_auth
from utils.app_state import render_page_setup
from utils.alerts import alert_counts, build_alerts
from utils.calculations import (
    fmt_money,
    fmt_num,
    selected_month_summary,
    utility_cost_per_usage_breakdown,
    year_over_year_cost_trend,
)
from utils.charts import bar_chart, line_chart
from utils.data_loader import load_data
from utils.theme import apply_theme, alert_cards, compact_table, kpi_card, page_header, panel_start, panel_end, delta_html

st.set_page_config(page_title="Operations Command Center", page_icon="⚡", layout="wide")
require_auth()
apply_theme()

try:
    df = load_data()
except Exception as e:
    st.error(f"Could not load data: {e}")
    st.stop()

page_header(
    "Utility Operations Command Center",
    "Default view opens to the most recently completed month to avoid incomplete current-month billing.",
)
filters = render_page_setup(df)
fdf = filters["filtered"]
current_month = filters["current_month"]
previous_month = filters["previous_month"]
selected_utilities = filters["selected_utility_values"]

summary = selected_month_summary(fdf, current_month, previous_month)
alerts = build_alerts(fdf, current_month, previous_month)
counts = alert_counts(alerts)

cols = st.columns(6)
with cols[0]:
    kpi_card("Total Cost", fmt_money(summary["current"]["amount"]), fmt_money(summary["previous"]["amount"]), summary["delta_amount"], delta_direction="treatment_adjusted", reference_delta=summary["delta_treatments"])
with cols[1]:
    kpi_card("Cost / Treatment", fmt_money(summary["current"]["cost_per_treatment"], 2), fmt_money(summary["previous"]["cost_per_treatment"], 2), summary["delta_cpt"], delta_direction="lower_is_better")
with cols[2]:
    if len(selected_utilities) == 1:
        kpi_card("Cost / Usage", fmt_money(summary["current"]["cost_per_usage"], 4), fmt_money(summary["previous"]["cost_per_usage"], 4), summary["delta_cpu"], selected_utilities[0], delta_direction="lower_is_better")
    else:
        kpi_card("Cost / Usage", "Select Utility Filter", "", None, "Choose one utility to view cost per usage.")
with cols[3]:
    kpi_card("Total Usage", fmt_num(summary["current"]["usage"]), fmt_num(summary["previous"]["usage"]), summary["delta_usage"], delta_direction="treatment_adjusted", reference_delta=summary["delta_treatments"])
with cols[4]:
    kpi_card("Treatments", fmt_num(summary["current"]["treatments"]), fmt_num(summary["previous"]["treatments"]), summary["delta_treatments"], delta_direction="higher_is_better")
with cols[5]:
    kpi_card("Active Alerts", str(counts["Total"]), f"{counts['Critical']} Critical", None, f"{counts['Review']} Review")

st.markdown("<br>", unsafe_allow_html=True)
left, right = st.columns([1.45, 1])

with left:
    panel_start("Year-over-Year Cost Trend", "Compares the selected reporting year to the prior year through the selected completed month.")
    trend = year_over_year_cost_trend(fdf, current_month)
    if not trend.empty:
        year_cols = [c for c in trend.columns if c != "Month"]
        fig = line_chart(trend, "Month", year_cols, "Current Year vs Prior Year Cost", 380)
        fig.update_yaxes(title="Total Cost")
        fig.update_xaxes(title="Month")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No year-over-year trend data available for the selected filters.")
    panel_end()

with right:
    panel_start("Cost per Usage by Utility", "Indicator only: billing totals may include blended charges, fees, and adjustments. Units are kept separate and should not be read as exact utility rates.")
    breakdown = utility_cost_per_usage_breakdown(fdf, current_month, previous_month)
    if not breakdown.empty:
        view = breakdown.copy()
        view["This Month"] = view["This Month"].apply(lambda x: fmt_money(x, 4))
        view["Previous Month"] = view["Previous Month"].apply(lambda x: fmt_money(x, 4))
        view["% Change"] = view["% Change"].apply(lambda x: delta_html(x, direction="lower_is_better"))
        compact_table(view, ["Utility", "This Month", "Previous Month", "% Change", "Unit"], max_rows=8)
    else:
        st.info("No utility breakdown available.")
    panel_end()

bottom_left, bottom_right = st.columns([1.2, 1])
with bottom_left:
    panel_start("Current Month Cost Drivers", "Utility spend for the selected month and filters.")
    cur = fdf[fdf["billing_month"] == current_month]
    by_util = cur.groupby("utility", as_index=False)["amount"].sum().sort_values("amount", ascending=False)
    if not by_util.empty:
        fig = bar_chart(by_util, "utility", "amount", title="Cost by Utility", height=330)
        fig.update_yaxes(title="Cost")
        fig.update_xaxes(title="Utility")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No current month utility data.")
    panel_end()

with bottom_right:
    panel_start("Priority Alerts", "Highest-impact items requiring analyst review.")
    alert_cards(alerts, max_cards=5)
    panel_end()
