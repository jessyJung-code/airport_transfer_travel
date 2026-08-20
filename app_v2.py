"""
app.py — Free Korea Transit Tour · Survey Dashboard  v2
-------------------------------------------------------
변경사항:
  1. 헤더 제목 글씨 색상 → 흰색(다크) / 진한 남색(라이트) 명확 처리
  2. 라이트 / 다크 모드 토글 (사이드바 스위치)
  3. 필터 → 클릭 토글 버튼 방식 (st.pills / 버튼 매트릭스)
실행: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re
from collections import Counter

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG  (반드시 첫 번째 st 호출)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Transit Tour Dashboard",
    page_icon="✈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE 초기화
# ─────────────────────────────────────────────────────────────────────────────
if "dark_mode"   not in st.session_state: st.session_state.dark_mode   = True
if "sel_gender"  not in st.session_state: st.session_state.sel_gender  = ["Female", "Male", "Prefer not to say"]
if "sel_age"     not in st.session_state: st.session_state.sel_age     = ["Under 20","20s","30s","40s","50s","60+"]
if "sel_visit"   not in st.session_state: st.session_state.sel_visit   = ["First time","2–3 times","4+ times"]

# ─────────────────────────────────────────────────────────────────────────────
# THEME  변수
# ─────────────────────────────────────────────────────────────────────────────
DK = st.session_state.dark_mode

if DK:
    BG0, BG1, BG2    = "#0d1b2a", "#0f2035", "#162840"
    T1,  T2,  T3     = "#f0f4f8", "#a8bcd0", "#6a8caa"
    BORDER           = "#1e3a52"
    GRID_C           = "#1e3a52"
    TICK_C           = "#6a8caa"
    LEGEND_C         = "#a8bcd0"
    TITLE_CSS_CLR    = "#ffffff"          # ← 헤더 글씨 흰색
    PLOT_PAPER       = "rgba(0,0,0,0)"
    PLOT_BG          = "rgba(0,0,0,0)"
    ST_THEME         = "dark"
else:
    BG0, BG1, BG2    = "#f1f5f9", "#ffffff", "#e8eef4"
    T1,  T2,  T3     = "#0f172a", "#475569", "#94a3b8"
    BORDER           = "#cbd5e1"
    GRID_C           = "#e2e8f0"
    TICK_C           = "#94a3b8"
    LEGEND_C         = "#475569"
    TITLE_CSS_CLR    = "#0f172a"          # ← 라이트 모드 진한 남색
    PLOT_PAPER       = "rgba(0,0,0,0)"
    PLOT_BG          = "rgba(0,0,0,0)"
    ST_THEME         = "light"

ACCENT    = "#3b82f6"
PALETTE   = ["#3b82f6","#10b981","#f97316","#f59e0b","#8b5cf6","#ef4444","#06b6d4","#ec4899"]

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html,body,[class*="css"]{{font-family:'Inter',sans-serif;}}

/* ── 앱 배경 ── */
.stApp{{background:{BG0};}}
section[data-testid="stSidebar"]{{background:{BG1} !important;border-right:1px solid {BORDER};}}
.block-container{{padding:1.4rem 2rem 2rem;max-width:1600px;}}
#MainMenu,footer,header{{visibility:hidden;}}

/* ── 헤더 제목 글씨 색상 ── */
.dash-title{{font-size:1.1rem;font-weight:500;color:{TITLE_CSS_CLR};letter-spacing:-.01em;margin:0;line-height:1.2;}}
.dash-sub{{font-size:.82rem;color:{T3};margin-top:.2rem;}}

/* ── KPI 카드 ── */
.kpi-card{{
    background:{BG1};border:.5px solid {BORDER};border-radius:12px;
    padding:.85rem .75rem;text-align:center;border-top:2.5px solid transparent;
}}
.kpi-card.blue  {{border-top-color:#3b82f6;}}
.kpi-card.teal  {{border-top-color:#10b981;}}
.kpi-card.purple{{border-top-color:#8b5cf6;}}
.kpi-card.coral {{border-top-color:#f97316;}}
.kpi-card.amber {{border-top-color:#f59e0b;}}
.kpi-card.green {{border-top-color:#10b981;}}
.kpi-card::before{{display:none;}}
.kpi-card.blue::before  {{background:#3b82f6;}}
.kpi-card.teal::before  {{background:#10b981;}}
.kpi-card.purple::before{{background:#8b5cf6;}}
.kpi-card.coral::before {{background:#f97316;}}
.kpi-card.amber::before {{background:#f59e0b;}}
.kpi-card.green::before {{background:#10b981;}}
.kpi-label{{font-size:.68rem;font-weight:500;color:{T3};text-transform:uppercase;letter-spacing:.06em;margin-bottom:.3rem;}}
.kpi-value{{font-size:1.5rem;font-weight:500;line-height:1;margin-bottom:.2rem;}}
.kpi-unit {{font-size:.72rem;color:{T3};}}
.kpi-card.blue   .kpi-value{{color:#60a5fa;}}
.kpi-card.teal   .kpi-value{{color:#34d399;}}
.kpi-card.purple .kpi-value{{color:#a78bfa;}}
.kpi-card.coral  .kpi-value{{color:#fb923c;}}
.kpi-card.amber  .kpi-value{{color:#fbbf24;}}
.kpi-card.green  .kpi-value{{color:#34d399;}}

/* ── 섹션 헤더 ── */
.sec-hdr{{
    font-size:.75rem;font-weight:500;color:{ACCENT};
    text-transform:uppercase;letter-spacing:.09em;
    border-bottom:.5px solid {BORDER};padding-bottom:5px;margin:1.4rem 0 .85rem;
}}

/* ── 필터 토글 버튼 ── */
.filter-section{{
    background:{BG1};border:1px solid {BORDER};border-radius:12px;
    padding:.85rem 1.1rem;margin-bottom:1rem;
}}
.filter-hdr{{font-size:.68rem;font-weight:700;color:{T3};
    text-transform:uppercase;letter-spacing:.08em;margin-bottom:.5rem;}}

/* ── IPA 사분면 배지 ── */
.ipa-keep{{background:#d4f4ec;color:#085041;border-radius:4px;padding:2px 7px;font-size:10px;font-weight:600;}}
.ipa-conc{{background:#fdeaea;color:#791f1f;border-radius:4px;padding:2px 7px;font-size:10px;font-weight:600;}}
.ipa-over{{background:#fef3dc;color:#633806;border-radius:4px;padding:2px 7px;font-size:10px;font-weight:600;}}
.ipa-low {{background:{BG2};color:{T3};border-radius:4px;padding:2px 7px;font-size:10px;font-weight:600;}}

/* ── 인용 카드 ── */
.quote-card{{
    background:{BG1};border-left:3px solid {ACCENT};border-radius:0 8px 8px 0;
    padding:.65rem .9rem;margin-bottom:.5rem;font-size:.83rem;color:{T2};
    font-style:italic;
}}

/* ── Streamlit 위젯 다크 보정 ── */
.stMultiSelect [data-baseweb="tag"]{{background:{BG2} !important;}}
div[data-testid="stMetricValue"]{{color:{T1};}}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_raw():
    df = pd.read_excel("raw_data.xlsx", sheet_name="Form Responses 1")

    def likert5(col):
        m = {"5 (Very high)": 5, "4": 4, "3": 3, "2": 2, "1 (Very low)": 1}
        return col.map(lambda x: m.get(str(x).strip(), np.nan)).astype(float)

    q27_map = {"Very satisfied": 5, "Satisfied": 4, "Neutral": 3,
               "Dissatisfied": 2, "Very dissatisfied": 1}
    q28_map = q27_map.copy()

    IMP = [c for c in df.columns if "-1)" in c and "Importance" in c]
    SAT = [c for c in df.columns if "-2)" in c and "Satisfaction" in c]
    for c in IMP + SAT:
        df[c] = likert5(df[c])

    for c in [c for c in df.columns if "Q27." in c]:
        df[c] = df[c].map(q27_map)
    for c in [c for c in df.columns if "Q28." in c]:
        df[c] = df[c].map(q28_map)

    df["Q34_num"] = pd.to_numeric(
        df["Q34.  Overall, how satisfied are you with this transit tour?"], errors="coerce")

    spend_map = {"$10 or less": 5, "$11 – $50": 30,
                 "$51 – $100": 75, "$101 – $200": 150, "More than $200": 250}
    future_map = {"$500 or less": 250, "$501 – $1,000": 750,
                  "$1,001 – $2,000": 1500, "$2,001 – $3,000": 2500, "More than $3,000": 3500}
    df["spend_mid"]       = df["Q19-2.  Approximate total spending (USD)?"].map(spend_map)
    df["future_spend_mid"]= df["Q20.  If you visit Korea as a tourist in the future, how much do you expect to spend in total?"].map(future_map)
    return df, IMP, SAT

df_all, IMP_COLS, SAT_COLS = load_raw()

# ─────────────────────────────────────────────────────────────────────────────
# FILTER HELPERS
# ─────────────────────────────────────────────────────────────────────────────
ITEM_META = [
    ("Program Composition",        "Variety of programs"),
    ("Program Composition",        "Attractiveness of destinations"),
    ("Program Composition",        "Appropriateness of schedule"),
    ("Operation & Service",        "Tour guide expertise"),
    ("Operation & Service",        "Guide friendliness"),
    ("Operation & Service",        "Smooth operation"),
    ("Transportation Convenience", "Comfort of tour bus"),
    ("Transportation Convenience", "Appropriateness of travel time"),
    ("Transportation Convenience", "Reliability of return time"),
    ("Information Provision",      "Sufficiency of information"),
    ("Information Provision",      "Convenience of booking"),
    ("Information Provision",      "Clarity of airport signage"),
    ("Tourism Experience",         "Korean culture experience"),
    ("Tourism Experience",         "Free time at destinations"),
    ("Tourism Experience",         "Food and shopping"),
]
CAT_COLORS = {
    "Program Composition":        "#3b82f6",
    "Operation & Service":        "#10b981",
    "Transportation Convenience": "#f97316",
    "Information Provision":      "#f59e0b",
    "Tourism Experience":         "#8b5cf6",
}
GRAND_IMP, GRAND_SAT = 4.742, 4.718

def apply_filters():
    mask = (
        df_all["Gender"].isin(st.session_state.sel_gender) &
        df_all["Age Group:"].isin(st.session_state.sel_age) &
        df_all["Previous visits to Korea"].isin(st.session_state.sel_visit)
    )
    return df_all[mask].copy()

def pct(series, val):
    return series.eq(val).sum() / len(series) * 100

# ─────────────────────────────────────────────────────────────────────────────
# PLOTLY DEFAULTS
# ─────────────────────────────────────────────────────────────────────────────
def base_layout(**kw):
    layout = dict(
        paper_bgcolor=PLOT_PAPER, plot_bgcolor=PLOT_BG,
        font=dict(family="Inter", color=T2, size=12),
        margin=dict(l=40, r=20, t=36, b=40),
    )
    if "legend" not in kw:
        layout["legend"] = dict(bgcolor="rgba(0,0,0,0)", font=dict(color=LEGEND_C, size=11))
    layout.update(kw)
    return layout

def axis(title="", fmt=None, **kw):
    a = dict(gridcolor=GRID_C, zerolinecolor=GRID_C,
             tickcolor=TICK_C, tickfont=dict(color=TICK_C, size=11),
             title=dict(text=title, font=dict(color=T3, size=11)), **kw)
    if fmt:
        a["tickformat"] = fmt
    return a

# ─────────────────────────────────────────────────────────────────────────────
# REUSABLE CHART BUILDERS
# ─────────────────────────────────────────────────────────────────────────────
def bar_h(labels, values, colors, title="", h=None):
    if h is None:
        h = max(200, len(labels) * 34 + 60)
    fig = go.Figure(go.Bar(
        x=values, y=labels, orientation="h",
        marker_color=colors if isinstance(colors, list) else [colors]*len(labels),
        marker_cornerradius=3,
        text=[str(v) for v in values], textposition="outside",
        textfont=dict(color=T2, size=11),
    ))
    fig.update_layout(**base_layout(title=title, height=h),
                      xaxis=axis(), yaxis=axis(showgrid=False))
    return fig

def bar_v(labels, values, colors, title="", h=300):
    fig = go.Figure(go.Bar(
        x=labels, y=values,
        marker_color=colors if isinstance(colors, list) else [colors]*len(labels),
        marker_cornerradius=3,
        text=[str(v) for v in values], textposition="outside",
        textfont=dict(color=T2, size=11),
    ))
    fig.update_layout(**base_layout(title=title, height=h),
                      xaxis=axis(showgrid=False), yaxis=axis())
    return fig

def donut(labels, values, colors, title="", h=280):
    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        marker=dict(colors=colors, line=dict(color=BG1, width=2)),
        hole=0.52, textfont=dict(size=12),
        hovertemplate="%{label}: %{value} (%{percent})<extra></extra>",
    ))
    layout = base_layout(title=title, height=h)
    # base_layout 안의 legend를 덮어쓰지 않도록 직접 merge
    layout["legend"] = dict(
        bgcolor="rgba(0,0,0,0)",
        font=dict(color=LEGEND_C, size=11),
        orientation="v", x=1.0, y=0.5,
    )
    fig.update_layout(**layout)
    return fig

# ─────────────────────────────────────────────────────────────────────────────
# IPA HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def get_quadrant(imp, sat):
    hi   = imp >= GRAND_IMP
    good = sat >= GRAND_SAT
    if hi and good:     return "★ Keep Up"
    if hi and not good: return "▲ Concentrate Here"
    if not hi and good: return "◆ Possible Overkill"
    return "○ Low Priority"

def get_quad_color(q):
    return {"★ Keep Up": "#10b981", "▲ Concentrate Here": "#ef4444",
            "◆ Possible Overkill": "#f59e0b", "○ Low Priority": "#6b7280"}[q]

def get_quad_badge(q):
    cls = {"★ Keep Up":"ipa-keep","▲ Concentrate Here":"ipa-conc",
           "◆ Possible Overkill":"ipa-over","○ Low Priority":"ipa-low"}[q]
    return f'<span class="{cls}">{q}</span>'

def build_ipa_df(dff):
    rows = []
    for (cat, item), ic, sc in zip(ITEM_META, IMP_COLS, SAT_COLS):
        imp = dff[ic].mean()
        sat = dff[sc].mean()
        quad = get_quadrant(imp, sat)
        rows.append({"Category": cat, "Item": item,
                     "Importance": imp, "Satisfaction": sat,
                     "Gap": sat - imp, "Quadrant": quad})
    return pd.DataFrame(rows)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION HEADER
# ─────────────────────────────────────────────────────────────────────────────
def sec(icon, text, size=".75rem"):
    st.markdown(
        f'<div class="sec-hdr" style="font-size:{size};">{icon}&nbsp; {text}</div>',
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# KPI CARD
# ─────────────────────────────────────────────────────────────────────────────
def kpi_card(label, value, unit, cls):
    return f"""
    <div class="kpi-card {cls}">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
      <div class="kpi-unit">{unit}</div>
    </div>"""

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    # ── 로고 + 제목
    st.markdown(f"""
    <div style='text-align:center;padding:1.1rem .75rem .7rem;border-bottom:.5px solid {BORDER};'>
      <div style='font-size:1.6rem;margin-bottom:4px;'>✈</div>
      <div style='font-size:.88rem;font-weight:500;color:{T1};'>Transit Tour</div>
      <div style='font-size:.72rem;color:{T3};'>Survey Dashboard</div>
    </div>
    """, unsafe_allow_html=True)

    # ── 페이지 네비게이션
    st.markdown("<div style='height:.3rem;'></div>", unsafe_allow_html=True)
    page = st.radio(
        "Navigation",
        ["📊 KPI Overview",
         "👥 Demographics",
         "🎯 IPA Analysis",
         "✈ Airport Competitiveness",
         "💡 Business Insights",
         "💬 Open-Ended Feedback"],
        label_visibility="collapsed",
    )
    st.markdown("<div style='height:.3rem;'></div>", unsafe_allow_html=True)

    st.markdown("<hr style='border-color:" + BORDER + ";margin:.8rem 0;'>",
                unsafe_allow_html=True)

    # ── 적용된 응답자 수
    ALL_GENDER = ["Female", "Male", "Prefer not to say"]
    ALL_AGE    = ["Under 20", "20s", "30s", "40s", "50s", "60+"]
    ALL_VISIT  = ["First time", "2–3 times", "4+ times"]

    dff_temp = apply_filters()
    Nf_side  = len(dff_temp)
    st.markdown(f"""
    <div style='text-align:center;padding:.5rem .75rem .4rem;'>
      <div style='font-size:.68rem;color:{T3};text-transform:uppercase;letter-spacing:.06em;margin-bottom:3px;'>적용된 응답자</div>
      <div style='font-size:1.5rem;font-weight:500;color:{T1};line-height:1.2;'>{Nf_side}</div>
      <div style='font-size:.72rem;color:{T3};'>/ 434명</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:" + BORDER + ";margin:.8rem 0;'>",
                unsafe_allow_html=True)

    # ── 필터: 성별
    st.markdown(f"<div style='font-size:.68rem;font-weight:500;color:{T3};text-transform:uppercase;letter-spacing:.07em;margin-bottom:5px;'>성별 (Gender)</div>",
                unsafe_allow_html=True)
    g_cols = st.columns(len(ALL_GENDER))
    for i, g in enumerate(ALL_GENDER):
        label_map = {"Female": "여성", "Male": "남성", "Prefer not to say": "기타"}
        selected  = g in st.session_state.sel_gender
        btn_type  = "primary" if selected else "secondary"
        if g_cols[i].button(label_map[g], key=f"g_{g}", use_container_width=True, type=btn_type):
            if selected and len(st.session_state.sel_gender) > 1:
                st.session_state.sel_gender = [x for x in st.session_state.sel_gender if x != g]
            elif not selected:
                st.session_state.sel_gender = st.session_state.sel_gender + [g]
            st.rerun()

    st.markdown("<div style='height:.5rem;'></div>", unsafe_allow_html=True)

    # ── 필터: 연령대
    st.markdown(f"<div style='font-size:.68rem;font-weight:500;color:{T3};text-transform:uppercase;letter-spacing:.07em;margin-bottom:5px;'>연령대 (Age)</div>",
                unsafe_allow_html=True)
    age_row1 = st.columns(3)
    age_row2 = st.columns(3)
    for i, a in enumerate(ALL_AGE):
        col      = age_row1[i] if i < 3 else age_row2[i - 3]
        selected = a in st.session_state.sel_age
        btn_type = "primary" if selected else "secondary"
        if col.button(a, key=f"a_{a}", use_container_width=True, type=btn_type):
            if selected and len(st.session_state.sel_age) > 1:
                st.session_state.sel_age = [x for x in st.session_state.sel_age if x != a]
            elif not selected:
                st.session_state.sel_age = st.session_state.sel_age + [a]
            st.rerun()

    st.markdown("<div style='height:.5rem;'></div>", unsafe_allow_html=True)

    # ── 필터: 방문 경험
    st.markdown(f"<div style='font-size:.68rem;font-weight:500;color:{T3};text-transform:uppercase;letter-spacing:.07em;margin-bottom:5px;'>방문 경험</div>",
                unsafe_allow_html=True)
    v_label  = {"First time": "첫 방문", "2–3 times": "2–3회", "4+ times": "4회+"}
    v_cols   = st.columns(3)
    for i, v in enumerate(ALL_VISIT):
        selected = v in st.session_state.sel_visit
        btn_type = "primary" if selected else "secondary"
        if v_cols[i].button(v_label[v], key=f"v_{v}", use_container_width=True, type=btn_type):
            if selected and len(st.session_state.sel_visit) > 1:
                st.session_state.sel_visit = [x for x in st.session_state.sel_visit if x != v]
            elif not selected:
                st.session_state.sel_visit = st.session_state.sel_visit + [v]
            st.rerun()

    st.markdown("<div style='height:.5rem;'></div>", unsafe_allow_html=True)

    # ── 전체 선택 / 초기화
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        if st.button("전체 선택", use_container_width=True):
            st.session_state.sel_gender = list(ALL_GENDER)
            st.session_state.sel_age    = list(ALL_AGE)
            st.session_state.sel_visit  = list(ALL_VISIT)
            st.rerun()
    with col_r2:
        if st.button("초기화", use_container_width=True):
            st.session_state.sel_gender = list(ALL_GENDER)
            st.session_state.sel_age    = list(ALL_AGE)
            st.session_state.sel_visit  = list(ALL_VISIT)
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# 필터 적용
# ─────────────────────────────────────────────────────────────────────────────
dff = apply_filters()
Nf  = len(dff)

# ─────────────────────────────────────────────────────────────────────────────
# 헤더
# ─────────────────────────────────────────────────────────────────────────────
# 헤더 — 타이틀 + 오른쪽 상단 테마 버튼
_hcol1, _hcol2 = st.columns([6, 1])
with _hcol1:
    st.markdown(f"""
    <div style='margin-bottom:1.2rem;'>
      <div class='dash-title'>Free Korea Transit Tour — Survey Dashboard</div>
      <div class='dash-sub'>
        Incheon International Airport&nbsp;·&nbsp;
        n = <b style='color:{T1};'>{Nf}</b> / 434&nbsp;·&nbsp;
        필터: 성별 {len(st.session_state.sel_gender)}개 · 연령 {len(st.session_state.sel_age)}개 · 방문경험 {len(st.session_state.sel_visit)}개
      </div>
    </div>
    """, unsafe_allow_html=True)
with _hcol2:
    st.markdown("<div style='padding-top:.35rem;'></div>", unsafe_allow_html=True)
    _mode_label = '☀ 라이트' if DK else '🌙 다크'
    if st.button(_mode_label, use_container_width=True, key='theme_btn'):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()



# ═════════════════════════════════════════════════════════════════════════════
# PAGE 1 · KPI OVERVIEW
# ═════════════════════════════════════════════════════════════════════════════
if page == "📊 KPI Overview":

    sec("⚡", "KEY PERFORMANCE INDICATORS", size="1rem")
    c1,c2,c3,c4,c5,c6 = st.columns(6)

    overall_sat  = dff["Q34_num"].mean()
    rec_pct      = dff["Q15.  Would you recommend this transit tour to others?"].isin(["Definitely yes","Probably yes"]).sum() / Nf * 100
    revisit_pct  = dff["Q3.  How likely are you to visit Korea as a tourist in the future after this transit tour?"].eq("Very likely").sum() / Nf * 100
    increased    = dff["Q22.  Which statement best describes how this transit tour affected your intention to revisit Korea?"].eq("The tour increased my intention to revisit Korea").sum() / Nf * 100
    purchase_pct = dff["Q19.  Did you make any additional purchases (food, souvenirs, etc.) during the transit tour?"].eq("Yes").sum() / Nf * 100
    avg_spend    = dff["spend_mid"].mean()

    with c1: st.markdown(kpi_card("종합 만족도 (Q34)", f"{overall_sat:.2f}", "/ 10점", "blue"), unsafe_allow_html=True)
    with c2: st.markdown(kpi_card("추천 의향 (Q15)", f"{rec_pct:.1f}%", "Def. + Prob. Yes", "teal"), unsafe_allow_html=True)
    with c3: st.markdown(kpi_card("재방문 가능성 (Q3)", f"{revisit_pct:.1f}%", "Very Likely", "teal"), unsafe_allow_html=True)
    with c4: st.markdown(kpi_card("투어→재방문 의향", f"{increased:.1f}%", "의향 증가 (Q22)", "purple"), unsafe_allow_html=True)
    with c5: st.markdown(kpi_card("현장 구매율 (Q19)", f"{purchase_pct:.1f}%", "추가 구매 비율", "coral"), unsafe_allow_html=True)
    with c6: st.markdown(kpi_card("평균 현장 지출", f"${avg_spend:.0f}", "USD per buyer", "amber"), unsafe_allow_html=True)

    st.markdown("<div style='height:.9rem;'></div>", unsafe_allow_html=True)

    # Q34 분포 + Q15 추천
    sec("📈", "SATISFACTION & RECOMMENDATION")
    col_l, col_r = st.columns([1.4, 1])

    with col_l:
        sat_dist = dff["Q34_num"].value_counts().sort_index()
        colors_s = ["#ef4444" if v<=4 else "#f59e0b" if v<=6 else "#3b82f6" if v<=8 else "#10b981" for v in sat_dist.index]
        fig_s = go.Figure(go.Bar(x=sat_dist.index.astype(str), y=sat_dist.values,
                                  marker_color=colors_s, marker_cornerradius=3,
                                  text=sat_dist.values, textposition="outside",
                                  textfont=dict(color=T2, size=11)))
        fig_s.update_layout(**base_layout(title="Q34 종합 만족도 분포 (0–10)", height=300),
                             xaxis=axis(title="점수"), yaxis=axis(title="응답 수"))
        st.plotly_chart(fig_s, use_container_width=True)

    with col_r:
        rec = dff["Q15.  Would you recommend this transit tour to others?"].value_counts()
        fig_r = donut(rec.index.tolist(), rec.values.tolist(),
                      ["#10b981","#3b82f6","#94a3b8"], "Q15 추천 의향")
        st.plotly_chart(fig_r, use_container_width=True)

    # Q27 투어 요소 만족도
    sec("⭐", "TOUR ELEMENT SATISFACTION (Q27)")
    Q27C = [c for c in df_all.columns if "Q27." in c]
    q27l = [c.split("[")[1].rstrip("]") for c in Q27C]
    q27m = [dff[c].mean() for c in Q27C]
    s_idx = sorted(range(len(q27m)), key=lambda i: q27m[i], reverse=True)
    fig_q27 = go.Figure(go.Bar(
        x=[q27m[i] for i in s_idx], y=[q27l[i] for i in s_idx],
        orientation="h", marker_cornerradius=3,
        marker=dict(color=[q27m[i] for i in s_idx],
                    colorscale=[[0,"#3b82f6"],[0.5,"#10b981"],[1,"#34d399"]], cmin=4.0, cmax=5.0),
        text=[f"{q27m[i]:.3f}" for i in s_idx], textposition="outside",
        textfont=dict(color=T2, size=11),
    ))
    fig_q27.update_layout(**base_layout(title="평균 점수 (1=매우 불만족 → 5=매우 만족)", height=300),
                           xaxis=axis(title="평균 점수", range=[4.0, 5.2]), yaxis=axis())
    st.plotly_chart(fig_q27, use_container_width=True)

    # Q22 + Q3
    sec("🔄", "REVISIT INTENT & LIKELIHOOD")
    col_a, col_b = st.columns(2)
    with col_a:
        q22 = dff["Q22.  Which statement best describes how this transit tour affected your intention to revisit Korea?"].value_counts()
        short22 = {"The tour increased my intention to revisit Korea": "투어로 의향 증가",
                   "I had already planned to revisit before the tour": "이미 계획 있었음",
                   "The tour did not greatly affect my intention, but I may revisit Korea": "미영향·방문 가능",
                   "The tour decreased my intention to revisit Korea": "의향 감소"}
        q22.index = [short22.get(i, i) for i in q22.index]
        fig22 = bar_h(q22.index.tolist(), q22.values.tolist(),
                      ["#10b981","#3b82f6","#f59e0b","#ef4444"], "Q22 투어의 재방문 의향 영향", h=260)
        st.plotly_chart(fig22, use_container_width=True)
    with col_b:
        q3 = dff["Q3.  How likely are you to visit Korea as a tourist in the future after this transit tour?"].value_counts()
        fig3 = bar_v(q3.index.tolist(), q3.values.tolist(),
                     ["#10b981","#3b82f6","#94a3b8","#f97316","#ef4444"], "Q3 한국 재방문 가능성", h=260)
        st.plotly_chart(fig3, use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 2 · DEMOGRAPHICS
# ═════════════════════════════════════════════════════════════════════════════
elif page == "👥 Demographics":

    sec("👤", "PROFILE BREAKDOWN")
    c1,c2,c3,c4 = st.columns(4)

    with c1:
        g = dff["Gender"].value_counts()
        st.plotly_chart(donut(g.index.tolist(), g.values.tolist(),
                               ["#f97316","#3b82f6","#94a3b8"], "성별"), use_container_width=True)
    with c2:
        age_order = ["Under 20","20s","30s","40s","50s","60+"]
        age = dff["Age Group:"].value_counts().reindex(age_order).dropna()
        fig_age = bar_v(age.index.tolist(), age.values.tolist(), "#3b82f6", "연령대", h=260)
        st.plotly_chart(fig_age, use_container_width=True)
    with c3:
        pu = dff["Purpose"].value_counts()
        st.plotly_chart(donut(pu.index.tolist(), pu.values.tolist(),
                               ["#10b981","#3b82f6","#f59e0b","#f97316"], "방문 목적"), use_container_width=True)
    with c4:
        pv = dff["Previous visits to Korea"].value_counts()
        st.plotly_chart(donut(pv.index.tolist(), pv.values.tolist(),
                               ["#3b82f6","#10b981","#f59e0b"], "이전 방문 경험"), use_container_width=True)

    sec("🌍", "TOP NATIONALITIES")
    nat = dff["1.1. Nationality:"].value_counts().head(12)
    fig_n = bar_h(nat.index.tolist(), nat.values.tolist(),
                   [PALETTE[i % len(PALETTE)] for i in range(len(nat))],
                   "국적별 응답자 수 (Top 12)", h=max(260, len(nat)*34+60))
    st.plotly_chart(fig_n, use_container_width=True)

    sec("🗺", "TOURS JOINED")
    tours = dff["Which tour did you join?"].value_counts()
    short_t = [t.split("(")[0].strip()[:55] for t in tours.index]
    fig_t = bar_h(short_t, tours.values.tolist(), "#8b5cf6",
                   "투어 프로그램별 참여 인원", h=max(220, len(tours)*34+60))
    st.plotly_chart(fig_t, use_container_width=True)

    sec("⏱", "REVISIT LIKELIHOOD & LAYOVER")
    col_a, col_b = st.columns(2)
    with col_a:
        q3 = dff["Q3.  How likely are you to visit Korea as a tourist in the future after this transit tour?"].value_counts()
        fig_q3 = bar_v(q3.index.tolist(), q3.values.tolist(),
                        ["#10b981","#3b82f6","#94a3b8","#ef4444","#7f1d1d"], "Q3 한국 재방문 가능성", h=280)
        st.plotly_chart(fig_q3, use_container_width=True)
    with col_b:
        q7 = dff["Q7.  What is the total duration of your layover at Incheon Airport?"].value_counts()
        st.plotly_chart(donut(q7.index.tolist(), q7.values.tolist(),
                               PALETTE[:len(q7)], "Q7 환승 체류 시간", h=280), use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 3 · IPA ANALYSIS
# ═════════════════════════════════════════════════════════════════════════════
elif page == "🎯 IPA Analysis":

    st.markdown(f"<p style='color:{T3};font-size:.82rem;margin-bottom:1rem;'>15개 항목 · 5개 카테고리 · 1–5점 척도 · Gap = 만족도 − 중요도</p>",
                unsafe_allow_html=True)

    ipa = build_ipa_df(dff)
    gi  = ipa["Importance"].mean()
    gs  = ipa["Satisfaction"].mean()

    # ── IPA 산점도
    sec("📍", "IPA QUADRANT — 15 ITEMS")
    fig_ipa = go.Figure()

    xm = ipa["Importance"].min() - .05
    xM = ipa["Importance"].max() + .05
    ym = ipa["Satisfaction"].min() - .05
    yM = ipa["Satisfaction"].max() + .05

    # 사분면 배경
    a = .07 if DK else .04
    for x0,x1,y0,y1,clr in [
        (gi,xM,gs,yM, f"rgba(16,185,129,{a})"),
        (xm,gi,gs,yM, f"rgba(245,158,11,{a})"),
        (gi,xM,ym,gs, f"rgba(239,68,68,{a})"),
        (xm,gi,ym,gs, f"rgba(107,114,128,{a})"),
    ]:
        fig_ipa.add_shape(type="rect", x0=x0,x1=x1,y0=y0,y1=y1, fillcolor=clr, line_width=0, layer="below")

    # 평균선
    for line in [
        dict(type="line",x0=gi,x1=gi,y0=ym,y1=yM),
        dict(type="line",x0=xm,x1=xM,y0=gs,y1=gs),
    ]:
        fig_ipa.add_shape(**line, line=dict(color=GRID_C, width=1.5, dash="dash"))

    # 사분면 라벨
    for txt,x,y,anchor in [
        ("★ Keep Up", gi+.003, yM-.003, "left top"),
        ("◆ Overkill", xm+.003, yM-.003, "left top"),
        ("▲ Concentrate Here", gi+.003, ym+.003, "left bottom"),
        ("○ Low Priority", xm+.003, ym+.003, "left bottom"),
    ]:
        xanchor, yanchor = anchor.split()
        fig_ipa.add_annotation(x=x, y=y, text=txt, showarrow=False,
                                font=dict(color=T3, size=10, family="Inter"),
                                xanchor=xanchor, yanchor=yanchor)

    # 항목 점
    for cat in ipa["Category"].unique():
        sub = ipa[ipa["Category"] == cat]
        fig_ipa.add_trace(go.Scatter(
            x=sub["Importance"], y=sub["Satisfaction"],
            mode="markers+text", name=cat,
            text=sub["Item"].str[:24],
            textposition="top center", textfont=dict(size=9, color=T2),
            marker=dict(size=14, color=CAT_COLORS[cat],
                        line=dict(width=2, color=BG1), symbol="circle"),
            customdata=sub[["Gap","Quadrant"]].values,
            hovertemplate="<b>%{text}</b><br>Imp: %{x:.3f}  Sat: %{y:.3f}<br>Gap: %{customdata[0]:+.3f}<br>%{customdata[1]}<extra></extra>",
        ))

    _ipa_layout = base_layout(
        title=f"IPA Scatter — 전체 평균 Importance={gi:.3f} / Satisfaction={gs:.3f}",
        height=540, showlegend=True,
    )
    _ipa_layout["legend"] = dict(
        bgcolor="rgba(0,0,0,0)", font=dict(color=LEGEND_C, size=10),
        orientation="h", x=0, y=-0.12,
    )
    fig_ipa.update_layout(
        **_ipa_layout,
        xaxis=axis(title="Importance (avg 1–5)", range=[xm,xM]),
        yaxis=axis(title="Satisfaction (avg 1–5)", range=[ym,yM]))
    st.plotly_chart(fig_ipa, use_container_width=True)

    # ── 카테고리 IPA
    sec("📊", "CATEGORY-LEVEL IPA")
    cat_ipa = ipa.groupby("Category").agg({"Importance":"mean","Satisfaction":"mean","Gap":"mean"}).reset_index()
    ci_avg  = cat_ipa["Importance"].mean()
    cs_avg  = cat_ipa["Satisfaction"].mean()
    cat_ipa["Quadrant"] = cat_ipa.apply(lambda r: get_quadrant(r["Importance"], r["Satisfaction"]), axis=1)

    col_l, col_r = st.columns([1.2, 1])
    with col_l:
        fig_cat = go.Figure()
        xm2 = cat_ipa["Importance"].min()-.03
        xM2 = cat_ipa["Importance"].max()+.03
        ym2 = cat_ipa["Satisfaction"].min()-.03
        yM2 = cat_ipa["Satisfaction"].max()+.03
        for x0,x1,y0,y1,clr in [(ci_avg,xM2,cs_avg,yM2,f"rgba(16,185,129,{a})"),(xm2,ci_avg,cs_avg,yM2,f"rgba(245,158,11,{a})"),(ci_avg,xM2,ym2,cs_avg,f"rgba(239,68,68,{a})"),(xm2,ci_avg,ym2,cs_avg,f"rgba(107,114,128,{a})")]:
            fig_cat.add_shape(type="rect",x0=x0,x1=x1,y0=y0,y1=y1,fillcolor=clr,line_width=0,layer="below")
        fig_cat.add_shape(type="line",x0=ci_avg,x1=ci_avg,y0=ym2,y1=yM2,line=dict(color=GRID_C,width=1.5,dash="dash"))
        fig_cat.add_shape(type="line",x0=xm2,x1=xM2,y0=cs_avg,y1=cs_avg,line=dict(color=GRID_C,width=1.5,dash="dash"))
        for _, row in cat_ipa.iterrows():
            fig_cat.add_trace(go.Scatter(
                x=[row["Importance"]], y=[row["Satisfaction"]],
                mode="markers+text", name=row["Category"],
                text=[row["Category"].split()[0]],
                textposition="top center", textfont=dict(size=10, color=CAT_COLORS[row["Category"]]),
                marker=dict(size=20, color=CAT_COLORS[row["Category"]], line=dict(width=2, color=BG1)),
                showlegend=False,
                hovertemplate=f"<b>{row['Category']}</b><br>Imp: {row['Importance']:.3f}  Sat: {row['Satisfaction']:.3f}<br>Gap: {row['Gap']:+.3f}<extra></extra>",
            ))
        fig_cat.update_layout(**base_layout(title="Category IPA", height=360, showlegend=False),
                               xaxis=axis(title="Importance", range=[xm2,xM2]),
                               yaxis=axis(title="Satisfaction", range=[ym2,yM2]))
        st.plotly_chart(fig_cat, use_container_width=True)

    with col_r:
        st.markdown(f"<div style='height:.3rem;'></div>", unsafe_allow_html=True)
        quad_sym = {"★ Keep Up":"★","▲ Concentrate Here":"▲","◆ Possible Overkill":"◆","○ Low Priority":"○"}
        for _, row in cat_ipa.sort_values("Importance", ascending=False).iterrows():
            badge = get_quad_badge(row["Quadrant"])
            gap_c = "#10b981" if row["Gap"] >= 0 else "#ef4444"
            st.markdown(f"""
            <div style='background:{BG1};border:1px solid {BORDER};border-radius:10px;padding:.75rem 1rem;margin-bottom:.55rem;'>
              <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:.4rem;'>
                <span style='color:{T1};font-weight:600;font-size:.88rem;'>{row["Category"]}</span>
                {badge}
              </div>
              <div style='display:flex;gap:1.2rem;'>
                <span style='font-size:.78rem;color:{T3};'>Imp: <b style='color:#3b82f6;'>{row["Importance"]:.3f}</b></span>
                <span style='font-size:.78rem;color:{T3};'>Sat: <b style='color:#10b981;'>{row["Satisfaction"]:.3f}</b></span>
                <span style='font-size:.78rem;color:{T3};'>Gap: <b style='color:{gap_c};'>{row["Gap"]:+.3f}</b></span>
              </div>
            </div>""", unsafe_allow_html=True)

    # ── 15-item table
    sec("📋", "15-ITEM DETAIL TABLE")
    st.dataframe(
        ipa[["Category","Item","Importance","Satisfaction","Gap","Quadrant"]].round(3),
        use_container_width=True,
        column_config={
            "Importance":   st.column_config.ProgressColumn("Importance", min_value=4.0, max_value=5.0, format="%.3f"),
            "Satisfaction": st.column_config.ProgressColumn("Satisfaction", min_value=4.0, max_value=5.0, format="%.3f"),
            "Gap":          st.column_config.NumberColumn("Gap (Sat−Imp)", format="%+.3f"),
        },
        height=540,
    )

    # ── Gap bar
    sec("📉", "GAP ANALYSIS (Satisfaction − Importance)")
    ipa_s = ipa.sort_values("Gap")
    gap_c = ["#ef4444" if g < 0 else "#10b981" for g in ipa_s["Gap"]]
    fig_g = go.Figure(go.Bar(
        x=ipa_s["Gap"], y=ipa_s["Item"], orientation="h",
        marker_color=gap_c, marker_cornerradius=3,
        text=[f"{g:+.3f}" for g in ipa_s["Gap"]], textposition="outside",
        textfont=dict(color=T2, size=11),
    ))
    fig_g.add_vline(x=0, line_color=GRID_C, line_width=1.5)
    fig_g.update_layout(**base_layout(title="Gap = Satisfaction − Importance (양수 = 기대 초과)", height=460),
                         xaxis=axis(title="Gap"), yaxis=axis())
    st.plotly_chart(fig_g, use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 4 · AIRPORT COMPETITIVENESS
# ═════════════════════════════════════════════════════════════════════════════
elif page == "✈ Airport Competitiveness":

    sec("⚡", "KEY METRICS")
    c1,c2,c3,c4 = st.columns(4)
    influenced = dff["Q9.  Did the transit tour program influence your decision to transit through Incheon Airport?"].isin(["A lot","Somewhat"]).sum()/Nf*100
    future_lk  = dff["Q10.  When booking future flights, would the availability of a transit tour program make you more likely to choose Incheon Airport as a transit hub?"].isin(["Much more likely","Somewhat more likely"]).sum()/Nf*100
    knew_inf   = dff["Q12.  Did you know about the transit tour BEFORE choosing Incheon Airport?"].eq("Knew about it and it influenced my choice").sum()/Nf*100
    tour_prim  = dff["Q14.  What was the PRIMARY reason you chose Incheon Airport as your transit hub?"].eq("Availability of the transit tour program").sum()/Nf*100

    with c1: st.markdown(kpi_card("투어 ICN 선택 영향", f"{influenced:.1f}%", "A lot + Somewhat", "blue"), unsafe_allow_html=True)
    with c2: st.markdown(kpi_card("미래 ICN 선택↑", f"{future_lk:.1f}%", "Much/Somewhat more", "teal"), unsafe_allow_html=True)
    with c3: st.markdown(kpi_card("사전 인지 + 영향", f"{knew_inf:.1f}%", "Q12 응답", "purple"), unsafe_allow_html=True)
    with c4: st.markdown(kpi_card("1순위 이유: 투어", f"{tour_prim:.1f}%", "Q14 응답", "coral"), unsafe_allow_html=True)

    st.markdown("<div style='height:.7rem;'></div>", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)
    with col_l:
        sec("📌", "Q9 — 투어가 ICN 선택에 미친 영향")
        q9 = dff["Q9.  Did the transit tour program influence your decision to transit through Incheon Airport?"].value_counts()
        order9 = ["A lot","Somewhat","Neutral","Very little","Not at all"]
        q9 = q9.reindex([o for o in order9 if o in q9.index])
        fig9 = bar_v(q9.index.tolist(), q9.values.tolist(),
                      ["#10b981","#3b82f6","#94a3b8","#f59e0b","#ef4444"], h=280)
        st.plotly_chart(fig9, use_container_width=True)

        sec("💡", "Q12 — ICN 선택 전 투어 인지 여부")
        q12 = dff["Q12.  Did you know about the transit tour BEFORE choosing Incheon Airport?"].value_counts()
        short12 = {"Knew about it and it influenced my choice":"Knew & Influenced",
                   "Found out after choosing Incheon":"Found Out After",
                   "Did not know about it":"Did Not Know",
                   "Knew about it but it did not affect my choice":"Knew, No Effect"}
        q12.index = [short12.get(i,i) for i in q12.index]
        st.plotly_chart(donut(q12.index.tolist(), q12.values.tolist(),
                               ["#10b981","#f59e0b","#ef4444","#3b82f6"], "Q12 ICN 선택 전 인지", h=280),
                         use_container_width=True)

    with col_r:
        sec("🔮", "Q10 — 향후 ICN 환승 선택 가능성")
        q10 = dff["Q10.  When booking future flights, would the availability of a transit tour program make you more likely to choose Incheon Airport as a transit hub?"].value_counts()
        order10 = ["Much more likely","Somewhat more likely","No change","Somewhat less likely","Much less likely"]
        q10 = q10.reindex([o for o in order10 if o in q10.index])
        fig10 = bar_v(q10.index.tolist(), q10.values.tolist(),
                       ["#10b981","#3b82f6","#94a3b8","#ef4444","#7f1d1d"], h=280)
        st.plotly_chart(fig10, use_container_width=True)

        sec("🎯", "Q14 — ICN 선택 주요 이유")
        q14 = dff["Q14.  What was the PRIMARY reason you chose Incheon Airport as your transit hub?"].value_counts().head(6)
        short14 = {"Availability of the transit tour program":"Transit Tour Program",
                   "Lower airfare price":"Lower Airfare","Suitable flight schedule":"Flight Schedule",
                   "Previous positive experience":"Past Experience","Superior airport facilities":"Airport Facilities"}
        q14.index = [short14.get(i, i[:32]) for i in q14.index]
        fig14 = bar_h(q14.index.tolist(), q14.values.tolist(),
                       [PALETTE[i%len(PALETTE)] for i in range(len(q14))], h=280)
        st.plotly_chart(fig14, use_container_width=True)

    sec("💰", "Q21 — 유료 전환 시 지불 의향 (WTP)")
    wtp_raw   = dff["Q21.  If this tour were offered as a paid program, what would you be willing to pay?"]
    wtp_valid = wtp_raw.map(lambda x: x if x in ["It should remain free","$10 or less","$11 – $20","$21 – $30","$31 – $50"] else np.nan).dropna()
    wtp = wtp_valid.value_counts().reindex(["It should remain free","$10 or less","$11 – $20","$21 – $30","$31 – $50"]).dropna()
    fig_wtp = bar_v(wtp.index.tolist(), wtp.values.tolist(),
                     ["#ef4444","#f59e0b","#3b82f6","#10b981","#8b5cf6"], h=280)
    st.plotly_chart(fig_wtp, use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 5 · BUSINESS INSIGHTS
# ═════════════════════════════════════════════════════════════════════════════
elif page == "💡 Business Insights":

    sec("💴", "SPENDING SIGNALS")
    c1,c2,c3 = st.columns(3)
    pur_pct    = dff["Q19.  Did you make any additional purchases (food, souvenirs, etc.) during the transit tour?"].eq("Yes").sum()/Nf*100
    avg_spend  = dff["spend_mid"].mean()
    avg_future = dff["future_spend_mid"].mean()
    with c1: st.markdown(kpi_card("현장 구매율 (Q19)", f"{pur_pct:.1f}%", "추가 구매 비율", "teal"), unsafe_allow_html=True)
    with c2: st.markdown(kpi_card("평균 현장 지출", f"${avg_spend:.0f}", "USD (buyers only)", "blue"), unsafe_allow_html=True)
    with c3: st.markdown(kpi_card("향후 여행 예산", f"${avg_future:,.0f}", "USD 예상", "amber"), unsafe_allow_html=True)

    st.markdown("<div style='height:.7rem;'></div>", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)
    with col_l:
        sec("🛍", "Q19-2 — 현장 지출 분포")
        spend = dff["Q19-2.  Approximate total spending (USD)?"].value_counts()
        order_s = ["$10 or less","$11 – $50","$51 – $100","$101 – $200","More than $200"]
        spend = spend.reindex([o for o in order_s if o in spend.index])
        st.plotly_chart(bar_v(spend.index.tolist(), spend.values.tolist(), "#3b82f6", h=280),
                         use_container_width=True)
    with col_r:
        sec("🏦", "Q20 — 향후 한국 여행 예상 지출")
        q20 = dff["Q20.  If you visit Korea as a tourist in the future, how much do you expect to spend in total?"].value_counts()
        order20 = ["$500 or less","$501 – $1,000","$1,001 – $2,000","$2,001 – $3,000","More than $3,000"]
        q20 = q20.reindex([o for o in order20 if o in q20.index])
        st.plotly_chart(bar_v(q20.index.tolist(), q20.values.tolist(), "#10b981", h=280),
                         use_container_width=True)

    # Priority vs Satisfaction (Q26 vs Q31)
    sec("⚖", "PRIORITY vs. SATISFACTION GAP  (Q26 vs Q31)")
    cats_pvs = ["Program Composition","Operation & Service","Transportation Convenience","Information Provision","Tourism Experience"]
    q26_m = {"Program composition":"Program Composition","Operation & service":"Operation & Service",
              "Transportation convenience":"Transportation Convenience","Information provision":"Information Provision","Tourism experience":"Tourism Experience"}
    q31_m = q26_m.copy()
    q26r = {q26_m.get(k,k): v for k,v in dff["Q26.  Which category do you consider most IMPORTANT in a transit tour?"].value_counts(normalize=True).items()}
    q31r = {q31_m.get(k,k): v for k,v in dff["Q31.  Which category of this transit tour were you most satisfied with?"].value_counts(normalize=True).items()}
    pvs_imp = [q26r.get(c,0) for c in cats_pvs]
    pvs_sat = [q31r.get(c,0) for c in cats_pvs]
    pvs_gap = [s-i for i,s in zip(pvs_imp,pvs_sat)]
    short_cats = ["Program","Operation","Transport","Information","Tourism"]

    fig_pvs = make_subplots(rows=1, cols=2,
                             subplot_titles=["Q26 중요 vs Q31 만족 (%)","Gap (만족−중요)"])
    fig_pvs.add_trace(go.Bar(name="Most Important (Q26)", x=short_cats, y=pvs_imp,
                               marker_color="#3b82f6", marker_cornerradius=3,
                               text=[f"{v:.1%}" for v in pvs_imp], textposition="outside",
                               textfont=dict(color=T2, size=10)), row=1, col=1)
    fig_pvs.add_trace(go.Bar(name="Most Satisfied (Q31)", x=short_cats, y=pvs_sat,
                               marker_color="#10b981", marker_cornerradius=3,
                               text=[f"{v:.1%}" for v in pvs_sat], textposition="outside",
                               textfont=dict(color=T2, size=10)), row=1, col=1)
    fig_pvs.add_trace(go.Bar(name="Gap", x=short_cats, y=pvs_gap,
                               marker_color=["#10b981" if g>=0 else "#ef4444" for g in pvs_gap],
                               marker_cornerradius=3,
                               text=[f"{g:+.1%}" for g in pvs_gap], textposition="outside",
                               textfont=dict(color=T2, size=10), showlegend=False), row=1, col=2)
    fig_pvs.add_hline(y=0, line_color=GRID_C, line_width=1, row=1, col=2)
    fig_pvs.update_layout(**base_layout(height=360, barmode="group"),
                           xaxis=dict(gridcolor=GRID_C, tickfont=dict(color=TICK_C, size=10)),
                           xaxis2=dict(gridcolor=GRID_C, tickfont=dict(color=TICK_C, size=10)),
                           yaxis=dict(gridcolor=GRID_C, tickfont=dict(color=TICK_C, size=10), tickformat=".0%"),
                           yaxis2=dict(gridcolor=GRID_C, tickfont=dict(color=TICK_C, size=10), tickformat=".0%"))
    st.plotly_chart(fig_pvs, use_container_width=True)

    # Q24 Barriers + Q23 Region
    col_a, col_b = st.columns(2)
    with col_a:
        sec("🚧", "Q24 — 재방문 장벽 (multi-select)")
        bc = Counter()
        for row in dff["Q24.  What are the main barriers to revisiting Korea as a tourist?"].dropna():
            for b in str(row).split(","):
                b = b.strip()
                if b: bc[b] += 1
        barriers = pd.Series(dict(bc)).sort_values(ascending=True).tail(8)
        fig_b = bar_h(barriers.index.tolist(), barriers.values.tolist(),
                       ["#ef4444"]*len(barriers), h=max(200, len(barriers)*34+60))
        st.plotly_chart(fig_b, use_container_width=True)

    with col_b:
        sec("🗺", "Q23 — 다음 한국 여행 희망 지역")
        q23 = dff["Q23.  Which region would you most like to visit on your next trip to Korea?"]
        q23_clean = q23.map(lambda x: x if x in ["Seoul","Busan","Jeju","Airport vicinity"] else "Other").value_counts()
        st.plotly_chart(donut(q23_clean.index.tolist(), q23_clean.values.tolist(),
                               ["#3b82f6","#10b981","#f97316","#f59e0b","#94a3b8"], "Q23 희망 방문 지역", h=280),
                         use_container_width=True)

    # Q25 share
    sec("📣", "Q25 — SNS 공유 의향")
    q25 = dff["Q25.  Do you intend to share your tour experience on social media, a blog, or a review platform?"].value_counts()
    st.plotly_chart(donut(q25.index.tolist(), q25.values.tolist(),
                           ["#10b981","#ef4444","#3b82f6"], "Q25 소셜 공유 의향", h=260),
                     use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 6 · OPEN-ENDED FEEDBACK
# ═════════════════════════════════════════════════════════════════════════════
elif page == "💬 Open-Ended Feedback":

    STOP = {"the","a","an","is","it","i","my","to","of","and","in","was","for",
            "on","at","with","this","that","but","had","not","very","so","we",
            "be","by","as","or","from","what","they","our","are","have","has",
            "would","could","should","you","your","me","its","if","do","did",
            "just","all","up","been","were","also","how","when","than","any",
            "some","into","about","more","can","most","their","will","out","one"}

    def top_words(series, n=20):
        words = []
        for row in series.dropna():
            for w in re.findall(r"[a-z']+", str(row).lower()):
                if w not in STOP and len(w) > 2:
                    words.append(w)
        return Counter(words).most_common(n)

    col_l, col_r = st.columns(2)

    with col_l:
        sec("❤", "Q16 — 가장 좋았던 점 (Top Keywords)")
        liked = top_words(dff["Q16.  What did you like most about this tour?"])
        if liked:
            wl, cl = zip(*liked)
            fig_l = bar_h(list(wl), list(cl),
                           [PALETTE[i%len(PALETTE)] for i in range(len(wl))],
                           "Q16 키워드 Top 20", h=520)
            st.plotly_chart(fig_l, use_container_width=True)

        sec("💬", "실제 응답 샘플 (Q16)")
        samples_l = dff["Q16.  What did you like most about this tour?"].dropna().sample(min(5,Nf), random_state=42)
        for txt in samples_l:
            st.markdown(f'<div class="quote-card">"{str(txt)[:220]}"</div>', unsafe_allow_html=True)

    with col_r:
        sec("🔧", "Q17 — 개선이 필요한 점 (Top Keywords)")
        improve = top_words(dff["Q17.  What could be improved?"])
        if improve:
            wi, ci = zip(*improve)
            fig_i = bar_h(list(wi), list(ci),
                           ["#f59e0b"]*len(wi),
                           "Q17 키워드 Top 20", h=520)
            st.plotly_chart(fig_i, use_container_width=True)

        sec("💬", "실제 응답 샘플 (Q17)")
        samples_i = dff["Q17.  What could be improved?"].dropna().sample(min(5,Nf), random_state=7)
        for txt in samples_i:
            st.markdown(f'<div class="quote-card" style="border-left-color:#f59e0b;">"{str(txt)[:220]}"</div>',
                         unsafe_allow_html=True)

    sec("🌟", "Q28 — 경험적 가치 만족도 (avg 1–5)")
    Q28C = [c for c in df_all.columns if "Q28." in c]
    q28l = [c.split("[")[1].rstrip("]") for c in Q28C]
    q28m = [dff[c].mean() for c in Q28C]
    fig28 = go.Figure(go.Bar(
        x=q28m, y=q28l, orientation="h",
        marker=dict(color=q28m, colorscale=[[0,"#3b82f6"],[1,"#10b981"]], cmin=3.5, cmax=5.0, showscale=False),
        marker_cornerradius=3,
        text=[f"{v:.3f}" for v in q28m], textposition="outside",
        textfont=dict(color=T2, size=11),
    ))
    fig28.update_layout(**base_layout(title="Q28 경험 가치 평균", height=260),
                         xaxis=axis(title="평균 점수", range=[4.0, 5.2]), yaxis=axis())
    st.plotly_chart(fig28, use_container_width=True)
