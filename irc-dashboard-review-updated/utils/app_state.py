from __future__ import annotations

import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

import config
from utils.auth import logout_button
from utils.calculations import filter_dimension, selected_previous_month
from utils.data_loader import available_months
from utils.theme import theme_toggle


def auto_refresh():
    seconds = int(getattr(config, "AUTO_REFRESH_SECONDS", 30))
    if seconds > 0:
        st_autorefresh(interval=seconds * 1000, key="live_sheet_refresh")


def render_sidebar_shell():
    st.sidebar.markdown("### IRC Utility Operations")
    st.sidebar.caption("Live Google Sheet dashboard")
    theme_toggle()
    st.sidebar.divider()
    st.sidebar.caption("Client-safe summary view")
    st.sidebar.caption("No raw data export")
    st.sidebar.divider()
    logout_button()

    last_updated = st.session_state.get("data_last_updated", "Not loaded yet")
    st.sidebar.markdown(
        f"""
        <div class="sidebar-last-updated">
          <strong>Last Updated</strong><br>{last_updated}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _options(series: pd.Series) -> list[str]:
    vals = sorted([
        str(v).strip()
        for v in series.dropna().unique().tolist()
        if str(v).strip() and str(v).strip().lower() not in {"unknown", "nan", "none"}
    ])
    return ["All"] + vals


def _clean_selection(selection):
    if not selection or "All" in selection:
        return []
    return [x for x in selection if x != "All"]


def _safe_default(key: str, options: list[str]) -> list[str]:
    """Return a safe default for multi-selects.

    Empty selection means All. This avoids rendering a cramped "All" chip by default
    while still keeping All as an available option in the dropdown.
    """
    existing = st.session_state.get(key, [])
    if isinstance(existing, str):
        existing = [existing]
    if not existing or "All" in existing:
        return []
    valid = [x for x in existing if x in options and x != "All"]
    return valid


def _multiselect(label: str, options: list[str], key: str, help_text: str | None = None) -> list[str]:
    return st.multiselect(
        label,
        options,
        default=_safe_default(key, options),
        key=key,
        help=help_text,
        placeholder="All",
    )


def _current_month_default_index(months_desc: list[pd.Timestamp]) -> int:
    """Default to the most recently completed reporting month.

    Billing for the current calendar month is often incomplete. If today is July,
    the dashboard should open to June when June exists. If the completed month is
    not available in the sheet, use the closest earlier available month; if all
    available months are later for some reason, fall back to the newest month.
    """
    if not months_desc:
        return 0
    completed_month = (pd.Timestamp.today().to_period("M").to_timestamp() - pd.DateOffset(months=1)).to_period("M").to_timestamp()
    normalized = [pd.to_datetime(m).to_period("M").to_timestamp() for m in months_desc]
    for idx, month in enumerate(normalized):
        if month == completed_month:
            return idx
    prior_or_equal = [(idx, m) for idx, m in enumerate(normalized) if m <= completed_month]
    if prior_or_equal:
        return prior_or_equal[0][0]
    return 0


def _describe_selection(name: str, selection: list[str], all_count: int) -> str:
    selected = _clean_selection(selection)
    if not selected:
        return f"{name}: All"
    if len(selected) <= 3:
        return f"{name}: {', '.join(selected)}"
    return f"{name}: {len(selected)} selected"


def render_top_filters(df: pd.DataFrame, include_provider: bool = False, include_alert_level: bool = False) -> dict:
    months = available_months(df)
    # Use only reporting months present in the sheet. Do not invent the current
    # calendar month, because that can create blank cards and false missing-bill
    # anomalies before current-month billing is complete.
    month_set = {pd.to_datetime(m).to_period("M").to_timestamp() for m in months}

    if not month_set:
        st.error("No reporting months were found in the data.")
        st.stop()

    months_desc = sorted(list(month_set), reverse=True)
    labels = [pd.to_datetime(m).strftime("%B %Y") for m in months_desc]
    label_to_month = dict(zip(labels, months_desc))

    with st.container(key="sticky_filters"):
        base_cols = [1.05, 1.18, 1.85, 1.35]
        if include_provider:
            base_cols.append(1.45)
        if include_alert_level:
            base_cols.append(1.20)
        base_cols.append(0.95)
        cols = st.columns(base_cols)

        with cols[0]:
            default_idx = _current_month_default_index(months_desc)
            selected_label = st.selectbox("Current month", labels, index=default_idx, key="filter_current_month_v5")
            current_month = pd.to_datetime(label_to_month[selected_label])
            previous_month = selected_previous_month(df, current_month)

        state_options = _options(df["state"])
        with cols[1]:
            state_selection = _multiselect("State", state_options, "filter_state")

        state_filtered = filter_dimension(df, states=state_selection)
        property_options = _options(state_filtered["property"])
        with cols[2]:
            property_selection = _multiselect("Property", property_options, "filter_property")

        prop_filtered = filter_dimension(state_filtered, properties=property_selection)
        utility_options = _options(prop_filtered["utility"])
        with cols[3]:
            utility_selection = _multiselect("Utility", utility_options, "filter_utility")

        col_index = 4
        provider_selection = ["All"]
        if include_provider:
            provider_filtered = filter_dimension(prop_filtered, utilities=utility_selection)
            provider_options = _options(provider_filtered["provider"])
            with cols[col_index]:
                provider_selection = _multiselect("Provider", provider_options, "filter_provider")
            col_index += 1

        alert_selection = ["All"]
        if include_alert_level:
            with cols[col_index]:
                alert_selection = _multiselect("Alert level", ["All", "Critical", "Review", "Info"], "filter_alert_level")
            col_index += 1

        with cols[col_index]:
            st.markdown("<div style='height:1.72rem'></div>", unsafe_allow_html=True)
            if st.button("Reset", use_container_width=True, help="Reset all filters to the default completed month and All selections."):
                for k in ["filter_state", "filter_property", "filter_utility", "filter_provider", "filter_alert_level"]:
                    st.session_state[k] = []
                st.rerun()

        filtered = filter_dimension(df, states=state_selection, properties=property_selection, utilities=utility_selection, providers=provider_selection)
        summary_parts = [
            f"Reporting month: {current_month.strftime('%B %Y')}",
            f"Previous: {previous_month.strftime('%B %Y') if previous_month is not None else 'None found'}",
            _describe_selection("State", state_selection, len(state_options) - 1),
            _describe_selection("Property", property_selection, len(property_options) - 1),
            _describe_selection("Utility", utility_selection, len(utility_options) - 1),
        ]
        if include_provider:
            summary_parts.append(_describe_selection("Provider", provider_selection, len(provider_options) - 1))
        if include_alert_level:
            summary_parts.append(_describe_selection("Alert", alert_selection, 3))
        summary_parts.append(f"Showing {filtered['property'].nunique():,} properties")
        st.markdown(f"<div class='filter-summary'>{' &nbsp;|&nbsp; '.join(summary_parts)}</div>", unsafe_allow_html=True)

    return {
        "current_month": current_month,
        "previous_month": previous_month,
        "states": state_selection,
        "properties": property_selection,
        "utilities": utility_selection,
        "providers": provider_selection,
        "alert_levels": alert_selection,
        "filtered": filtered,
        "selected_state_values": _clean_selection(state_selection),
        "selected_property_values": _clean_selection(property_selection),
        "selected_utility_values": _clean_selection(utility_selection),
        "selected_provider_values": _clean_selection(provider_selection),
        "selected_alert_values": _clean_selection(alert_selection),
    }


def render_page_setup(df: pd.DataFrame, include_provider: bool = False, include_alert_level: bool = False) -> dict:
    auto_refresh()
    render_sidebar_shell()
    return render_top_filters(df, include_provider=include_provider, include_alert_level=include_alert_level)
