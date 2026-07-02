import numpy as np
import pandas as pd
import streamlit as st

from utils.auth import require_auth
from utils.app_state import render_page_setup
from utils.alerts import build_alerts
from utils.calculations import fmt_money, fmt_num
from utils.charts import geographic_figure
from utils.data_loader import load_data
from utils.geocoding import prepare_property_coordinates
from utils.theme import apply_theme, compact_table, kpi_card, page_header, panel_start, panel_end

st.set_page_config(page_title="Geographic View", page_icon="🗺️", layout="wide")
require_auth()
apply_theme()

try:
    df = load_data()
except Exception as e:
    st.error(f"Could not load data: {e}")
    st.stop()

page_header("Geographic View", "State counts and property-level map dots for the selected completed reporting month.")
filters = render_page_setup(df)
fdf = filters["filtered"]
current_month = filters["current_month"]
previous_month = filters["previous_month"]

cur = fdf[fdf["billing_month"] == current_month].copy()
alerts = build_alerts(fdf, current_month, previous_month)

# State summary uses all filtered properties for property count and current month for metrics.
property_counts = fdf.groupby("state")["property"].nunique().reset_index(name="Properties")
if not cur.empty:
    state_amount_usage = cur.groupby("state", as_index=False).agg(amount=("amount", "sum"), usage=("usage", "sum"))
    state_treatments = (
        cur.groupby(["state", "property"], as_index=False)["treatments"].max()
        .groupby("state", as_index=False)["treatments"].sum()
    )
    state_metrics = state_amount_usage.merge(state_treatments, on="state", how="left")
else:
    state_metrics = pd.DataFrame(columns=["state", "amount", "usage", "treatments"])
alert_state = alerts.groupby("State").size().reset_index(name="Alerts").rename(columns={"State": "state"}) if not alerts.empty else pd.DataFrame(columns=["state", "Alerts"])
state_df = property_counts.merge(state_metrics, on="state", how="left").merge(alert_state, on="state", how="left").fillna({"amount":0, "usage":0, "treatments":0, "Alerts":0})
state_df["Cost/Treatment"] = np.where(state_df["treatments"] > 0, state_df["amount"] / state_df["treatments"], np.nan)
state_df = state_df.rename(columns={"state": "State", "amount": "Total Cost", "usage": "Usage", "treatments": "Treatments"})
state_df["Alerts"] = state_df["Alerts"].astype(int)
state_df["Properties"] = state_df["Properties"].astype(int)

# Property dot summary.
prop_base = fdf.sort_values("billing_month").groupby("property", as_index=False).agg(
    State=("state", "first"), City=("city", "first"), Street=("street", "first"), Zip=("zip", "first"),
    Address=("address", "first"), latitude=("latitude", "first"), longitude=("longitude", "first"),
)
cur_prop = cur.groupby("property", as_index=False).agg(amount=("amount", "sum"), usage=("usage", "sum"), treatments=("treatments", "max")) if not cur.empty else pd.DataFrame(columns=["property", "amount", "usage", "treatments"])
cur_prop["Cost/Treatment"] = np.where(cur_prop["treatments"] > 0, cur_prop["amount"] / cur_prop["treatments"], np.nan) if not cur_prop.empty else np.nan
prop_status = pd.DataFrame(columns=["property", "Status"])
if not alerts.empty:
    priority = {"Critical": 3, "Review": 2, "Info": 1}
    a = alerts.copy()
    a["Priority"] = a["Severity"].map(priority).fillna(0)
    prop_status = a.sort_values("Priority", ascending=False).groupby("Property", as_index=False).first()[["Property", "Severity"]].rename(columns={"Property": "property", "Severity": "Status"})
prop_df = prop_base.merge(cur_prop, on="property", how="left").merge(prop_status, on="property", how="left")
prop_df["Status"] = prop_df["Status"].fillna("Normal")
prop_df["Total Cost"] = prop_df["amount"].fillna(0)
prop_df["Property"] = prop_df["property"]
prop_df = prepare_property_coordinates(prop_df)
mapped_df = prop_df.dropna(subset=["lat", "lon"]).copy() if not prop_df.empty else prop_df.copy()
unmapped_df = prop_df[prop_df[["lat", "lon"]].isna().any(axis=1)].copy() if not prop_df.empty else prop_df.copy()

cols = st.columns(5)
with cols[0]:
    kpi_card("States Visible", str(state_df["State"].nunique() if not state_df.empty else 0), "Filtered view", None)
with cols[1]:
    kpi_card("Properties", str(prop_base["property"].nunique() if not prop_base.empty else 0), f"{len(mapped_df):,} mapped", None)
with cols[2]:
    kpi_card("State Cost", fmt_money(state_df["Total Cost"].sum() if not state_df.empty else 0), "Current month", None)
with cols[3]:
    kpi_card("Active Alerts", str(int(state_df["Alerts"].sum()) if not state_df.empty else 0), "Across states", None)
with cols[4]:
    highest = state_df.sort_values("Cost/Treatment", ascending=False).iloc[0]["State"] if not state_df.empty and state_df["Cost/Treatment"].notna().any() else "—"
    kpi_card("Highest CPT State", highest, f"{len(unmapped_df):,} unmapped", None)

left, right = st.columns([1.55, 1])
with left:
    panel_start("US Portfolio Map", "State shading shows property counts; dots show individual property locations and alert status.")
    if not state_df.empty:
        fig = geographic_figure(state_df, mapped_df)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Dots are shown only when the app has exact Latitude/Longitude or a successful full-address geocode from Street + City + State + Zip Code. The app does not use random/state-center fallback dots.")
    else:
        st.info("No geographic data available for the selected filters.")
    panel_end()

with right:
    panel_start("Property Count by State", "Includes property count, active alerts, and current-month cost/treatment.")
    if not state_df.empty:
        display = state_df.sort_values(["Properties", "Alerts"], ascending=[False, False]).copy()
        display["Total Cost"] = display["Total Cost"].apply(lambda x: fmt_money(x))
        display["Cost/Treatment"] = display["Cost/Treatment"].apply(lambda x: fmt_money(x, 2))
        display["Usage"] = display["Usage"].apply(lambda x: fmt_num(x))
        display["Treatments"] = display["Treatments"].apply(lambda x: fmt_num(x))
        compact_table(display, ["State", "Properties", "Alerts", "Total Cost", "Cost/Treatment"], max_rows=25)
    else:
        st.info("No state summary available.")
    panel_end()

if not unmapped_df.empty:
    panel_start("Unmapped Properties", "These properties were not placed on the map because exact coordinates were not available. Address fields are not displayed in the client view.")
    unmapped = unmapped_df.copy()
    compact_table(unmapped, ["Property", "City", "State", "Geocode Status"], max_rows=12)
    panel_end()

panel_start("Highest Cost Properties by Utility", "Current-month property comparisons are separated by utility so totals are more actionable and not blended across unrelated utilities.")
if not cur.empty:
    high = cur.groupby(["property", "city", "state", "utility"], as_index=False).agg(
        amount=("amount", "sum"),
        treatments=("treatments", "max"),
        usage=("usage", "sum"),
    )
    high["Cost/Treatment"] = np.where(high["treatments"] > 0, high["amount"] / high["treatments"], np.nan)
    if not alerts.empty:
        status_lookup = alerts.sort_values("Severity").groupby(["Property", "Utility"], as_index=False).first()[["Property", "Utility", "Severity"]]
        high = high.merge(status_lookup, left_on=["property", "utility"], right_on=["Property", "Utility"], how="left")
    else:
        high["Severity"] = "Normal"
    high["Status"] = high["Severity"].fillna("Normal")
    high = high.sort_values(["utility", "amount"], ascending=[True, False]).head(15)
    high = high.rename(columns={"property": "Property", "city": "City", "state": "State", "utility": "Utility", "amount": "Total Cost"})
    high["Total Cost"] = high["Total Cost"].apply(lambda x: fmt_money(x))
    high["Cost/Treatment"] = high["Cost/Treatment"].apply(lambda x: fmt_money(x, 2))
    compact_table(high, ["Status", "Utility", "Property", "City", "State", "Total Cost", "Cost/Treatment"], max_rows=15)
else:
    st.info("No current-month property summary available for the selected filters.")
panel_end()
