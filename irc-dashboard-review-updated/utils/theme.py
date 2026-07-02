from __future__ import annotations

import html
from typing import Callable

import pandas as pd
import streamlit as st

DARK = {
    "name": "dark",
    "bg": "#07111F",
    "panel": "#0F1F35",
    "panel2": "#122945",
    "text": "#EAF2FF",
    "muted": "#B8C7DA",
    "border": "rgba(148, 163, 184, 0.24)",
    "accent": "#38BDF8",
    "accent2": "#22C55E",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "info": "#60A5FA",
    "card_shadow": "0 14px 36px rgba(0,0,0,0.22)",
    "plotly_template": "plotly_dark",
}

LIGHT = {
    "name": "light",
    "bg": "#F5F7FB",
    "panel": "#FFFFFF",
    "panel2": "#F8FAFC",
    "text": "#0F172A",
    "muted": "#475569",
    "border": "rgba(15, 23, 42, 0.12)",
    "accent": "#0284C7",
    "accent2": "#16A34A",
    "warning": "#D97706",
    "danger": "#DC2626",
    "info": "#2563EB",
    "card_shadow": "0 12px 30px rgba(15,23,42,0.08)",
    "plotly_template": "plotly_white",
}


def init_theme():
    if "theme_mode" not in st.session_state:
        st.session_state.theme_mode = "dark"


def current_theme():
    init_theme()
    return DARK if st.session_state.theme_mode == "dark" else LIGHT


def theme_toggle():
    init_theme()
    selected = st.sidebar.toggle(
        "Light mode",
        value=(st.session_state.theme_mode == "light"),
        help="Switch the dashboard from dark mode to light mode.",
    )
    st.session_state.theme_mode = "light" if selected else "dark"


def apply_theme():
    t = current_theme()
    st.markdown(
        f"""
        <style>
        :root {{
            --app-bg: {t['bg']};
            --panel-bg: {t['panel']};
            --panel-bg-2: {t['panel2']};
            --text-main: {t['text']};
            --text-muted: {t['muted']};
            --border: {t['border']};
            --accent: {t['accent']};
            --accent-2: {t['accent2']};
            --warning: {t['warning']};
            --danger: {t['danger']};
            --info: {t['info']};
        }}
        .stApp {{
            background: radial-gradient(circle at top left, rgba(56, 189, 248, 0.11), transparent 24rem), var(--app-bg) !important;
            color: var(--text-main) !important;
        }}
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #050B14 0%, #0A1628 55%, #07111F 100%) !important;
            border-right: 1px solid rgba(148, 163, 184, 0.18);
        }}
        [data-testid="stSidebar"], [data-testid="stSidebar"] * {{
            color: #EAF2FF !important;
            -webkit-text-fill-color: #EAF2FF !important;
        }}
        .block-container {{
            padding-top: 3.85rem !important;
            padding-bottom: 3rem;
            max-width: 1540px;
        }}
        h1, h2, h3, h4, h5, h6 {{ color: var(--text-main) !important; letter-spacing: -0.02em; }}
        p, span, label, div {{ color: inherit; }}
        .page-title {{
            font-size: clamp(1.65rem, 2vw, 2.05rem);
            font-weight: 900;
            color: var(--text-main) !important;
            margin: 0 0 0.22rem 0;
            line-height: 1.14;
        }}
        .page-subtitle {{
            color: var(--text-muted) !important;
            font-size: 0.95rem;
            margin-bottom: 1rem;
            line-height: 1.35;
        }}
        .metric-card {{
            background: linear-gradient(180deg, var(--panel-bg) 0%, var(--panel-bg-2) 100%);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 18px 18px 16px 18px;
            box-shadow: {t['card_shadow']};
            min-height: 132px;
        }}
        .metric-label {{
            color: var(--text-muted) !important;
            font-size: 0.74rem;
            text-transform: uppercase;
            letter-spacing: 0.012em;
            font-weight: 800;
            white-space: normal;
            line-height: 1.22;
            overflow-wrap: normal;
            word-break: keep-all;
        }}
        .metric-value {{
            color: var(--text-main) !important;
            font-size: 1.68rem;
            font-weight: 900;
            line-height: 1.12;
            margin-top: 0.42rem;
            overflow-wrap: anywhere;
        }}
        .metric-prev {{
            color: var(--text-muted) !important;
            font-size: 0.82rem;
            margin-top: 0.36rem;
            line-height: 1.35;
        }}
        .panel {{
            background: linear-gradient(180deg, var(--panel-bg) 0%, var(--panel-bg-2) 100%);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 18px;
            box-shadow: {t['card_shadow']};
            margin-bottom: 1rem;
        }}
        .panel-title {{
            color: var(--text-main) !important;
            font-weight: 900;
            font-size: 1.05rem;
            margin-bottom: 0.15rem;
            line-height: 1.22;
        }}
        .panel-caption {{ color: var(--text-muted) !important; font-size: 0.86rem; margin-bottom: 0.8rem; line-height:1.35; }}
        .small-muted {{ color: var(--text-muted) !important; font-size: 0.86rem; }}
        .pill {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 999px;
            padding: 0.24rem 0.7rem;
            font-size: 0.76rem;
            font-weight: 900;
            margin-right: 0.35rem;
            white-space: nowrap;
            line-height: 1.1;
        }}
        .pill-danger {{ background: rgba(239,68,68,0.17); color: #FCA5A5 !important; border: 1px solid rgba(239,68,68,0.38); }}
        .pill-warning {{ background: rgba(245,158,11,0.18); color: #FCD34D !important; border: 1px solid rgba(245,158,11,0.38); }}
        .pill-good {{ background: rgba(34,197,94,0.18); color: #86EFAC !important; border: 1px solid rgba(34,197,94,0.38); }}
        .pill-info {{ background: rgba(96,165,250,0.18); color: #BFDBFE !important; border: 1px solid rgba(96,165,250,0.38); }}
        .insight-box {{
            border-left: 4px solid var(--accent);
            background: rgba(56,189,248,0.08);
            border-radius: 12px;
            padding: 12px 14px;
            margin-bottom: 0.7rem;
            color: var(--text-main) !important;
            line-height: 1.35;
        }}
        .st-key-sticky_filters {{
            position: sticky;
            top: 3.25rem;
            z-index: 999;
            background: color-mix(in srgb, var(--app-bg) 92%, transparent);
            backdrop-filter: blur(18px);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 0.70rem 0.85rem 0.82rem;
            margin: 0.25rem 0 1.05rem 0;
            box-shadow: 0 12px 28px rgba(0,0,0,0.20);
        }}
        label, [data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] * {{
            color: var(--text-main) !important;
            -webkit-text-fill-color: var(--text-main) !important;
            font-weight: 700 !important;
        }}
        .stSelectbox label, .stMultiSelect label, .stRadio label, .stTextInput label {{
            color: var(--text-main) !important;
        }}
        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div,
        input, textarea {{
            background-color: rgba(18, 41, 69, 0.94) !important;
            border: 1px solid rgba(148, 163, 184, 0.40) !important;
            color: #EAF2FF !important;
            -webkit-text-fill-color: #EAF2FF !important;
            border-radius: 12px !important;
            min-height: 42px !important;
        }}
        div[data-baseweb="select"] span,
        div[data-baseweb="select"] svg,
        div[data-baseweb="select"] input {{
            color: #EAF2FF !important;
            fill: #EAF2FF !important;
            -webkit-text-fill-color: #EAF2FF !important;
        }}
        div[data-baseweb="select"] div {{
            border-color: transparent;
        }}
        div[data-baseweb="select"] [data-baseweb="tag"] + div,
        div[data-baseweb="select"] [data-baseweb="tag"] + span {{
            border-left: 0 !important;
            box-shadow: none !important;
        }}
        div[data-baseweb="tag"] {{
            background-color: rgba(56, 189, 248, 0.16) !important;
            border: 1px solid rgba(56, 189, 248, 0.46) !important;
            border-radius: 999px !important;
            min-width: 76px !important;
            max-width: 100% !important;
            height: 32px !important;
            padding: 0 10px 0 12px !important;
            margin: 2px 5px 2px 0 !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            box-sizing: border-box !important;
            overflow: visible !important;
            box-shadow: none !important;
        }}
        div[data-baseweb="tag"]::before, div[data-baseweb="tag"]::after {{
            display: none !important;
            content: none !important;
        }}
        div[data-baseweb="tag"], div[data-baseweb="tag"] * {{
            color: #EAF2FF !important;
            -webkit-text-fill-color: #EAF2FF !important;
            font-weight: 850 !important;
            line-height: 1.05 !important;
            text-decoration: none !important;
        }}
        div[data-baseweb="tag"] span {{
            display: inline-flex !important;
            align-items: center !important;
            overflow: visible !important;
            text-overflow: clip !important;
            white-space: nowrap !important;
            min-width: fit-content !important;
        }}
        div[data-baseweb="tag"] button,
        div[data-baseweb="tag"] [role="button"] {{
            background: transparent !important;
            border: 0 !important;
            border-left: 0 !important;
            box-shadow: none !important;
            padding: 0 0 0 6px !important;
            margin: 0 !important;
            min-width: 18px !important;
        }}
        div[data-baseweb="tag"] svg {{
            width: 14px !important;
            height: 14px !important;
            fill: #EAF2FF !important;
            color: #EAF2FF !important;
        }}
        div[data-baseweb="popover"] ul,
        div[data-baseweb="popover"] li,
        div[role="listbox"], div[data-baseweb="menu"] {{
            background-color: #0F1F35 !important;
            color: #EAF2FF !important;
        }}
        div[role="option"], div[role="option"] span,
        div[data-baseweb="menu"] li, div[data-baseweb="menu"] li span {{
            color: #EAF2FF !important;
            -webkit-text-fill-color: #EAF2FF !important;
            background-color: #0F1F35 !important;
        }}
        .stButton > button, .stDownloadButton > button {{
            border-radius: 12px;
            border: 1px solid var(--border);
            background: linear-gradient(180deg, var(--panel-bg-2), var(--panel-bg));
            color: var(--text-main) !important;
            font-weight: 850;
            min-height: 42px;
        }}
        .stButton > button:hover, .stDownloadButton > button:hover {{
            border-color: var(--accent);
            color: var(--accent) !important;
        }}
        .st-key-sticky_filters .stButton > button,
        .st-key-sticky_filters div[data-testid="stButton"] button,
        .st-key-sticky_filters button[kind="secondary"] {{
            background: rgba(18, 41, 69, 0.96) !important;
            border: 1px solid rgba(148, 163, 184, 0.46) !important;
            color: #EAF2FF !important;
            -webkit-text-fill-color: #EAF2FF !important;
            font-weight: 900 !important;
            box-shadow: none !important;
        }}
        .st-key-sticky_filters .stButton > button:hover,
        .st-key-sticky_filters div[data-testid="stButton"] button:hover,
        .st-key-sticky_filters button[kind="secondary"]:hover {{
            background: rgba(56, 189, 248, 0.14) !important;
            border-color: var(--accent) !important;
            color: #EAF2FF !important;
            -webkit-text-fill-color: #EAF2FF !important;
        }}
        .dashboard-table-wrap {{ width: 100%; overflow: visible; }}
        .dashboard-table {{ width:100%; border-collapse: separate; border-spacing:0 9px; table-layout:auto; }}
        .dashboard-table th {{
            text-align:left; color:var(--text-muted) !important; font-size:.70rem; text-transform:uppercase;
            letter-spacing:.012em; padding:0 .60rem .18rem .60rem; white-space: nowrap; line-height:1.18;
        }}
        .dashboard-table td {{
            background: rgba(15,31,53,.70); border-top:1px solid var(--border); border-bottom:1px solid var(--border);
            padding:.70rem .60rem; vertical-align:top; color:var(--text-main) !important; font-size:.86rem;
            white-space: normal; overflow-wrap:normal; word-break:normal; line-height:1.28;
        }}
        .dashboard-table td:first-child {{ border-left:1px solid var(--border); border-radius:14px 0 0 14px; }}
        .dashboard-table td:last-child {{ border-right:1px solid var(--border); border-radius:0 14px 14px 0; }}
        .alert-card {{
            background: linear-gradient(180deg, rgba(15,31,53,.96), rgba(18,41,69,.92));
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 14px 16px;
            margin-bottom: 12px;
            box-shadow: {t['card_shadow']};
        }}
        .alert-head {{ display:flex; justify-content:space-between; gap:1rem; align-items:flex-start; }}
        .alert-title {{ font-weight:900; font-size:1rem; color:var(--text-main) !important; }}
        .alert-sub {{ color:var(--text-muted) !important; font-size:.84rem; margin-top:.18rem; }}
        .alert-reason {{ margin-top:.65rem; font-size:.9rem; color:var(--text-main) !important; line-height:1.35; }}
        .mini-grid {{
            display:grid;
            grid-template-columns: repeat(auto-fit, minmax(185px, 1fr));
            gap:.65rem;
            margin-top:.75rem;
            align-items:stretch;
        }}
        .mini-stat {{
            border:1px solid var(--border);
            background:rgba(255,255,255,.035);
            border-radius:12px;
            padding:.62rem .74rem;
            min-width:0;
            min-height:72px;
            overflow:visible;
        }}
        .mini-label {{
            color:var(--text-muted) !important;
            font-size:.64rem;
            text-transform:uppercase;
            letter-spacing:.012em;
            font-weight:850;
            white-space:normal;
            overflow-wrap:normal;
            word-break:keep-all;
            line-height:1.22;
        }}
        .mini-value {{ color:var(--text-main) !important; font-size:.96rem; font-weight:900; margin-top:.26rem; line-height:1.25; }}
        .delta-good, .delta-good * {{ color: var(--accent-2) !important; -webkit-text-fill-color: var(--accent-2) !important; font-weight: 950 !important; }}
        .delta-bad, .delta-bad * {{ color: var(--danger) !important; -webkit-text-fill-color: var(--danger) !important; font-weight: 950 !important; }}
        .delta-watch, .delta-watch * {{ color: var(--warning) !important; -webkit-text-fill-color: var(--warning) !important; font-weight: 950 !important; }}
        .delta-neutral, .delta-neutral * {{ color: var(--text-main) !important; -webkit-text-fill-color: var(--text-main) !important; font-weight: 950 !important; }}
        .legend-text, .legend-text * {{ color: var(--text-main) !important; -webkit-text-fill-color: var(--text-main) !important; }}
        .filter-summary {{ color: var(--text-muted) !important; font-size: .84rem; margin-top: .35rem; line-height:1.35; }}
        .sidebar-last-updated {{
            margin-top: 2rem;
            padding-top: .9rem;
            border-top: 1px solid rgba(148,163,184,.20);
            font-size: .78rem;
            color: #B8C7DA !important;
            line-height: 1.35;
        }}
        @media (max-width: 1100px) {{
            .mini-grid {{ grid-template-columns: repeat(auto-fit, minmax(155px, 1fr)); }}
            .st-key-sticky_filters {{ top: 2.8rem; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str = ""):
    st.markdown(f'<div class="page-title">{html.escape(title)}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="page-subtitle">{html.escape(subtitle)}</div>', unsafe_allow_html=True)


def _is_missing_number(value) -> bool:
    return value is None or pd.isna(value)


def _pick_delta_style(delta: float | None, direction: str = "lower_is_better", reference_delta: float | None = None) -> tuple[str, str]:
    if _is_missing_number(delta):
        return "delta-neutral", "→"
    d = float(delta)
    if abs(d) < 0.05:
        return "delta-neutral", "→"
    arrow = "▲" if d > 0 else "▼"
    if direction == "higher_is_better":
        return ("delta-good" if d > 0 else "delta-bad"), arrow
    if direction == "neutral":
        return "delta-neutral", arrow
    if direction == "treatment_adjusted":
        if _is_missing_number(reference_delta):
            return ("delta-bad" if d > 0 else "delta-good"), arrow
        gap = d - float(reference_delta)
        if gap <= 5:
            return "delta-good", arrow
        if gap <= 10:
            return "delta-watch", arrow
        return "delta-bad", arrow
    return ("delta-bad" if d > 0 else "delta-good"), arrow


def delta_html(delta: float | None, direction: str = "lower_is_better", reference_delta: float | None = None) -> str:
    t = current_theme()
    color_map = {
        "delta-good": t["accent2"],
        "delta-bad": t["danger"],
        "delta-watch": t["warning"],
        "delta-neutral": t["text"],
    }
    if _is_missing_number(delta):
        color = color_map["delta-neutral"]
        return f'<span class="delta-neutral" style="color:{color} !important; -webkit-text-fill-color:{color} !important; font-weight:950 !important;">—</span>'
    cls, arrow = _pick_delta_style(delta, direction=direction, reference_delta=reference_delta)
    color = color_map.get(cls, t["text"])
    return f'<span class="{cls}" style="color:{color} !important; -webkit-text-fill-color:{color} !important; font-weight:950 !important;">{arrow} {abs(float(delta)):.1f}%</span>'


def kpi_card(label: str, value: str, previous: str = "", delta: float | None = None, caption: str = "", delta_direction: str = "lower_is_better", reference_delta: float | None = None):
    previous_html = f'<div class="metric-prev">Prev: {html.escape(str(previous))} &nbsp;{delta_html(delta, direction=delta_direction, reference_delta=reference_delta)}</div>' if previous else ""
    caption_html = f'<div class="small-muted">{html.escape(str(caption))}</div>' if caption else ""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{html.escape(str(label))}</div>
            <div class="metric-value">{html.escape(str(value))}</div>
            {previous_html}
            {caption_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def panel_start(title: str, caption: str = ""):
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown(f'<div class="panel-title">{html.escape(title)}</div>', unsafe_allow_html=True)
    if caption:
        st.markdown(f'<div class="panel-caption">{html.escape(caption)}</div>', unsafe_allow_html=True)


def panel_end():
    st.markdown('</div>', unsafe_allow_html=True)


def severity_pill(severity: str) -> str:
    sev = str(severity)
    cls = "pill-info"
    if sev == "Critical":
        cls = "pill-danger"
    elif sev == "Review":
        cls = "pill-warning"
    elif sev in {"Normal", "Improved"}:
        cls = "pill-good"
    return f'<span class="pill {cls}">{html.escape(sev)}</span>'


def _html_or_escape(val) -> str:
    if pd.isna(val):
        return "—"
    s = str(val)
    if s.lstrip().startswith("<span") or s.lstrip().startswith("<div"):
        return s
    return html.escape(s)


def compact_table(df: pd.DataFrame, columns: list[str], formatters: dict[str, Callable] | None = None, max_rows: int = 10, empty_message: str = "No records found."):
    if df is None or df.empty:
        st.info(empty_message)
        return
    d = df.copy().head(max_rows)
    formatters = formatters or {}
    header = "".join(f"<th>{html.escape(str(col))}</th>" for col in columns)
    rows = []
    for _, r in d.iterrows():
        cells = []
        for col in columns:
            val = r.get(col, "")
            if col in formatters:
                try:
                    val = formatters[col](val)
                except Exception:
                    val = "—"
            cells.append(f"<td>{_html_or_escape(val)}</td>")
        rows.append("<tr>" + "".join(cells) + "</tr>")
    st.markdown(f"<div class='dashboard-table-wrap'><table class='dashboard-table'><thead><tr>{header}</tr></thead><tbody>{''.join(rows)}</tbody></table></div>", unsafe_allow_html=True)
    if len(df) > max_rows:
        st.caption(f"Showing top {max_rows} of {len(df)} records. Use filters to narrow the view.")


def _fmt_money_html(v, digits=0):
    if v is None or pd.isna(v):
        return "—"
    return html.escape(f"${float(v):,.{digits}f}")


def _fmt_num_html(v, digits=0):
    if v is None or pd.isna(v):
        return "—"
    return html.escape(f"{float(v):,.{digits}f}")


def _fmt_pct_html(v, direction: str = "lower_is_better", reference_delta=None):
    if v is None or pd.isna(v):
        return delta_html(None)
    return delta_html(v, direction=direction, reference_delta=reference_delta)


def alert_cards(alerts: pd.DataFrame, max_cards: int = 12):
    if alerts is None or alerts.empty:
        st.success("No active anomalies for the selected filters.")
        return
    for _, r in alerts.head(max_cards).iterrows():
        sev = r.get("Severity", "Info")
        prop = html.escape(str(r.get("Property", "Unknown")))
        utility = html.escape(str(r.get("Utility", "Unknown")))
        reason = html.escape(str(r.get("Reason", "Review item")))
        explanation = html.escape(str(r.get("Explanation", "")))
        cpt_chg = r.get("Cost/Treatment Change %")
        upt_chg = r.get("Usage/Treatment Change %")
        treatment_chg = r.get("Treatments Change %")
        impact = r.get("Estimated Monthly Impact")
        current_cost = r.get("Current Cost")
        current_cpt = r.get("Current Cost/Treatment")
        current_upt = r.get("Current Usage/Treatment")
        current_usage = r.get("Current Usage")
        is_missing = bool(r.get("Missing Bill", False)) or (pd.isna(current_cost) and "No bill found" in str(r.get("Reason", "")))

        if is_missing:
            stats = [
                ("Latest Cost", _fmt_money_html(r.get("Previous Cost"))),
                ("Latest Usage", _fmt_num_html(r.get("Previous Usage"))),
                ("Latest Treatments", _fmt_num_html(r.get("Previous Treatments"))),
                ("Latest Cost/Treatment", _fmt_money_html(r.get("Previous Cost/Treatment"), 2)),
                ("Latest Month", html.escape(str(r.get("Latest Month On File", "—")))),
                ("Est. Impact", _fmt_money_html(impact)),
            ]
        else:
            stats = [
                ("Current Cost", _fmt_money_html(current_cost)),
                ("Treatment Δ", _fmt_pct_html(treatment_chg, direction="higher_is_better")),
                ("Cost/Treatment Δ", _fmt_pct_html(cpt_chg, direction="lower_is_better")),
                ("Usage/Treatment Δ", _fmt_pct_html(upt_chg, direction="lower_is_better")),
                ("Cost/Treatment", _fmt_money_html(current_cpt, 2)),
                ("Usage/Treatment", _fmt_num_html(current_upt, 2)),
            ]

        stat_html = "".join(
            f'<div class="mini-stat"><div class="mini-label">{html.escape(label)}</div><div class="mini-value">{value}</div></div>'
            for label, value in stats[:4]
        )
        stat_html2 = "".join(
            f'<div class="mini-stat"><div class="mini-label">{html.escape(label)}</div><div class="mini-value">{value}</div></div>'
            for label, value in stats[4:]
        )
        st.markdown(
            f"""
            <div class="alert-card">
              <div class="alert-head">
                <div>
                  <div>{severity_pill(sev)} <span class="alert-title">{prop}</span></div>
                  <div class="alert-sub">{utility}</div>
                </div>
                <div class="alert-sub">Open Property Scorecard for details</div>
              </div>
              <div class="alert-reason"><b>Reason:</b> {reason}</div>
              <div class="mini-grid">{stat_html}</div>
              <div class="mini-grid">
                {stat_html2}
                <div class="mini-stat" style="grid-column: span 2;"><div class="mini-label">Explanation</div><div class="mini-value" style="font-weight:650; line-height:1.35;">{explanation}</div></div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    if len(alerts) > max_cards:
        st.caption(f"Showing top {max_cards} of {len(alerts)} alerts. Use filters to narrow the queue.")
