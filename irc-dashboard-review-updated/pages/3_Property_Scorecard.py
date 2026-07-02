import pandas as pd
import streamlit as st

from utils.auth import require_auth
from utils.app_state import render_page_setup
from utils.alerts import build_alerts
from utils.calculations import fmt_money, fmt_num, selected_month_summary, utility_aggregate
from utils.charts import line_chart, bar_chart
from utils.data_loader import load_data
from utils.theme import apply_theme, alert_cards, compact_table, kpi_card, page_header, panel_start, panel_end, delta_html

st.set_page_config(page_title="Property Scorecard", page_icon="🏥", layout="wide")
require_auth()
apply_theme()

try:
    df = load_data()
except Exception as e:
    st.error(f"Could not load data: {e}")
    st.stop()

page_header("Property Scorecard", "Property-level investigation with one focused property, utility mix, and condensed billing history.")
filters = render_page_setup(df)
fdf = filters["filtered"]
current_month = filters["current_month"]
previous_month = filters["previous_month"]

properties = sorted(fdf["property"].dropna().unique().tolist())
if not properties:
    st.info("No properties match the selected filters.")
    st.stop()

selected_filter_properties = filters.get("selected_property_values", [])
if len(selected_filter_properties) == 1 and selected_filter_properties[0] in properties:
    selected_property = selected_filter_properties[0]
    st.caption("Focused property comes from the Property filter above.")
else:
    selected_property = st.selectbox(
        "Choose property to review",
        properties,
        index=0,
        help="Use this only when the top Property filter is set to All or multiple properties.",
    )

prop_df = fdf[fdf["property"] == selected_property].copy()
page_header(selected_property, f"Focused scorecard for {current_month.strftime('%B %Y')}")
summary = selected_month_summary(prop_df, current_month, previous_month)
alerts = build_alerts(prop_df, current_month, previous_month)

cols = st.columns(5)
with cols[0]:
    kpi_card("Current Cost", fmt_money(summary["current"]["amount"]), fmt_money(summary["previous"]["amount"]), summary["delta_amount"], delta_direction="treatment_adjusted", reference_delta=summary["delta_treatments"])
with cols[1]:
    kpi_card("Cost / Treatment", fmt_money(summary["current"]["cost_per_treatment"], 2), fmt_money(summary["previous"]["cost_per_treatment"], 2), summary["delta_cpt"], delta_direction="lower_is_better")
with cols[2]:
    kpi_card("Cost / Usage", fmt_money(summary["current"]["cost_per_usage"], 4), fmt_money(summary["previous"]["cost_per_usage"], 4), summary["delta_cpu"], delta_direction="lower_is_better")
with cols[3]:
    kpi_card("Usage", fmt_num(summary["current"]["usage"]), fmt_num(summary["previous"]["usage"]), summary["delta_usage"], delta_direction="treatment_adjusted", reference_delta=summary["delta_treatments"])
with cols[4]:
    kpi_card("Treatments", fmt_num(summary["current"]["treatments"]), fmt_num(summary["previous"]["treatments"]), summary["delta_treatments"], delta_direction="higher_is_better")

left, right = st.columns([1.45, 1])
with left:
    panel_start("Monthly Cost Trend", "Total utility cost by reporting month. Cost per treatment is shown separately so the chart scale stays readable.")
    hist = utility_aggregate(prop_df).sort_values("billing_month")
    if not hist.empty:
        cost_trend = hist.groupby("billing_month", as_index=False)["amount"].sum()
        cost_trend["month_label"] = cost_trend["billing_month"].dt.strftime("%b %Y")
        fig = line_chart(cost_trend, "month_label", "amount", "Property Cost Trend", height=370)
        fig.update_yaxes(title="Total Cost")
        fig.update_xaxes(title="Reporting Month")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No property trend data available.")
    panel_end()

with right:
    panel_start("Treatment-Normalized Metrics", "Month-over-month values separated from the cost chart for easier interpretation.")
    metric_rows = pd.DataFrame([
        {"Metric": "Cost/Treatment", "This Month": fmt_money(summary["current"]["cost_per_treatment"], 2), "Previous": fmt_money(summary["previous"]["cost_per_treatment"], 2), "Change": delta_html(summary["delta_cpt"], direction="lower_is_better")},
        {"Metric": "Cost/Usage", "This Month": fmt_money(summary["current"]["cost_per_usage"], 4), "Previous": fmt_money(summary["previous"]["cost_per_usage"], 4), "Change": delta_html(summary["delta_cpu"], direction="lower_is_better")},
        {"Metric": "Usage/Treatment", "This Month": fmt_num(summary["current"]["usage"] / summary["current"]["treatments"] if summary["current"].get("treatments") else None, 2), "Previous": fmt_num(summary["previous"]["usage"] / summary["previous"]["treatments"] if summary["previous"].get("treatments") else None, 2), "Change": ""},
    ])
    compact_table(metric_rows, ["Metric", "This Month", "Previous", "Change"], max_rows=3)
    panel_end()

left2, right2 = st.columns([1.2, 1])
with left2:
    panel_start("Utility Cost Mix", "Current month spend split by utility.")
    cur = prop_df[prop_df["billing_month"] == current_month]
    mix = cur.groupby("utility", as_index=False)["amount"].sum().sort_values("amount", ascending=False)
    if not mix.empty:
        fig = bar_chart(mix, "utility", "amount", title="Current Month Cost", height=320)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No current month utility mix available.")
    panel_end()

with right2:
    panel_start("Automatic Explanation", "Treatment-adjusted alerts for this focused property.")
    alert_cards(alerts, max_cards=4)
    panel_end()

panel_start("Condensed Billing History", "Decision-making summary only; account numbers, meter numbers, and raw reads are not displayed.")
hist = utility_aggregate(prop_df).sort_values("billing_month", ascending=False)
if not hist.empty:
    table = hist[["billing_month", "utility", "amount", "usage", "treatments", "cost_per_treatment", "cost_per_usage", "days_billed"]].copy()
    table["Month"] = table["billing_month"].dt.strftime("%b %Y")
    table["Utility"] = table["utility"]
    table["Cost"] = table["amount"].apply(lambda x: fmt_money(x))
    table["Usage"] = table["usage"].apply(lambda x: fmt_num(x))
    table["Treatments"] = table["treatments"].apply(lambda x: fmt_num(x))
    table["Cost/Treatment"] = table["cost_per_treatment"].apply(lambda x: fmt_money(x, 2))
    table["Cost/Usage"] = table["cost_per_usage"].apply(lambda x: fmt_money(x, 4))
    table["Days Billed"] = table["days_billed"].apply(lambda x: fmt_num(x))
    compact_table(table, ["Month", "Utility", "Cost", "Usage", "Treatments", "Cost/Treatment", "Cost/Usage", "Days Billed"], max_rows=10)
else:
    st.info("No billing history available.")
panel_end()
