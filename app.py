"""
app.py — Free Korea Transit Tour · Survey Dashboard
실행: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Transit Tour Dashboard",
    page_icon="✈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Dark background */
.stApp { background: #0d1b2a; }
section[data-testid="stSidebar"] { background: #0f1f30 !important; border-right: 1px solid #1e3a52; }

/* Hide streamlit branding */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 2rem; max-width: 1600px; }

/* KPI cards */
.kpi-card {
    background: linear-gradient(135deg, #0f2035 0%, #1a3a55 100%);
    border: 1px solid #1e4060;
    border-radius: 16px;
    padding: 1.2rem 1.4rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: transform .2s, box-shadow .2s;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 16px 16px 0 0;
}
.kpi-card:hover { transform: translateY(-3px); box-shadow: 0 12px 32px rgba(0,0,0,.4); }
.kpi-card.blue::before  { background: linear-gradient(90deg,#185FA5,#378ADD); }
.kpi-card.teal::before  { background: linear-gradient(90deg,#1D9E75,#2DD4A0); }
.kpi-card.purple::before{ background: linear-gradient(90deg,#534AB7,#8b82e8); }
.kpi-card.coral::before { background: linear-gradient(90deg,#D85A30,#f08060); }
.kpi-card.amber::before { background: linear-gradient(90deg,#EF9F27,#f7c86a); }
.kpi-card.green::before { background: linear-gradient(90deg,#217346,#4CAF50); }
.kpi-label  { font-size: .72rem; color: #7aa0c0; font-weight: 500; letter-spacing: .06em; text-transform: uppercase; margin-bottom: .4rem; }
.kpi-value  { font-size: 2.1rem; font-weight: 800; line-height: 1; margin-bottom: .25rem; }
.kpi-unit   { font-size: .75rem; color: #5a8aaa; }
.kpi-card.blue   .kpi-value { color: #5ab0ff; }
.kpi-card.teal   .kpi-value { color: #2dd4a0; }
.kpi-card.purple .kpi-value { color: #a89df0; }
.kpi-card.coral  .kpi-value { color: #f08060; }
.kpi-card.amber  .kpi-value { color: #f7c86a; }
.kpi-card.green  .kpi-value { color: #6dce8a; }

/* Section headers */
.section-hdr {
    display: flex; align-items: center; gap: .7rem;
    font-size: .85rem; font-weight: 700; color: #5ab0ff;
    text-transform: uppercase; letter-spacing: .1em;
    border-bottom: 2px solid #1e3a52;
    padding-bottom: .5rem; margin: 2rem 0 1rem;
}

/* IPA quadrant labels */
.quad-badge {
    display: inline-flex; align-items: center; gap: .3rem;
    border-radius: 6px; padding: .2rem .7rem;
    font-size: .72rem; font-weight: 700;
}
.quad-keep   { background: #0d3325; color: #2dd4a0; }
.quad-conc   { background: #3d1515; color: #ff8080; }
.quad-over   { background: #3d2e00; color: #f7c86a; }
.quad-low    { background: #1a1a1a; color: #8a8a8a; }

/* Sidebar nav */
.sidebar-nav-item {
    padding: .6rem 1rem; border-radius: 10px; cursor: pointer;
    font-size: .88rem; color: #7aa0c0; margin-bottom: .3rem;
    transition: background .2s, color .2s;
}
.sidebar-nav-item:hover, .sidebar-nav-item.active {
    background: #1e3a52; color: #ffffff;
}

/* Plotly chart dark override */
.js-plotly-plot .plotly .bg { fill: transparent !important; }

/* Divider */
.divider { border: none; border-top: 1px solid #1e3a52; margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADING & PROCESSING
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_excel("raw_data.xlsx", sheet_name="Form Responses 1")

    # ── Likert numeric converter (IPA cols use "5 (Very high)" etc.)
    def likert5(col):
        mapping = {"5 (Very high)": 5, "4": 4, "3": 3, "2": 2, "1 (Very low)": 1}
        return col.map(lambda x: mapping.get(str(x).strip(), np.nan)).astype(float)

    # ── Q27 satisfaction (text → numeric)
    q27_map = {"Very satisfied": 5, "Satisfied": 4, "Neutral": 3,
                "Dissatisfied": 2, "Very dissatisfied": 1}

    # ── IPA columns
    IMP_COLS = [c for c in df.columns if "-1)" in c and "Importance" in c]
    SAT_COLS = [c for c in df.columns if "-2)" in c and "Satisfaction" in c]

    for c in IMP_COLS + SAT_COLS:
        df[c] = likert5(df[c])

    # ── Q27 tour element satisfaction
    Q27_COLS = [c for c in df.columns if "Q27." in c]
    for c in Q27_COLS:
        df[c] = df[c].map(q27_map)

    # ── Q34 overall satisfaction (already numeric)
    df["Q34_num"] = pd.to_numeric(df["Q34.  Overall, how satisfied are you with this transit tour?"], errors="coerce")

    # ── Q19-2 spending (buckets → midpoint)
    spend_map = {
        "$10 or less": 5, "$11 – $50": 30,
        "$51 – $100": 75, "$101 – $200": 150,
        "More than $200": 250,
    }
    df["spend_mid"] = df["Q19-2.  Approximate total spending (USD)?"].map(spend_map)

    # ── Q20 future spend
    future_map = {
        "$500 or less": 250, "$501 – $1,000": 750,
        "$1,001 – $2,000": 1500, "$2,001 – $3,000": 2500,
        "More than $3,000": 3500,
    }
    df["future_spend_mid"] = df["Q20.  If you visit Korea as a tourist in the future, how much do you expect to spend in total?"].map(future_map)

    return df, IMP_COLS, SAT_COLS

df, IMP_COLS, SAT_COLS = load_data()
N = len(df)

# ─────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
DARK_BG  = "#0d1b2a"
CARD_BG  = "#0f2035"
GRID_CLR = "#1e3a52"
TEXT_CLR = "#cce0f5"
ACCENT   = "#5ab0ff"

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color=TEXT_CLR, size=12),
    margin=dict(l=40, r=20, t=40, b=40),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=GRID_CLR, borderwidth=1),
)

CATEGORY_COLORS = {
    "Program Composition":    "#534AB7",
    "Operation & Service":    "#1D9E75",
    "Transportation Convenience": "#185FA5",
    "Information Provision":  "#EF9F27",
    "Tourism Experience":     "#D85A30",
}

QUAD_COLORS = {
    "Keep Up the Good Work": "#1D9E75",
    "Concentrate Here":      "#E24B4A",
    "Possible Overkill":     "#EF9F27",
    "Low Priority":          "#6B6B6B",
}

def kpi(label, value, unit, cls):
    return f"""
    <div class="kpi-card {cls}">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
      <div class="kpi-unit">{unit}</div>
    </div>"""

def section(icon, title):
    st.markdown(f'<div class="section-hdr"><span>{icon}</span><span>{title}</span></div>', unsafe_allow_html=True)

def get_ipa_df():
    ITEMS = [
        ("Program Composition",      "Variety of tour programs"),
        ("Program Composition",      "Attractiveness of destinations"),
        ("Program Composition",      "Appropriateness of tour schedule"),
        ("Operation & Service",      "Tour guide expertise"),
        ("Operation & Service",      "Guide friendliness"),
        ("Operation & Service",      "Smooth operation of the tour"),
        ("Transportation Convenience","Comfort of the tour bus"),
        ("Transportation Convenience","Appropriateness of travel time"),
        ("Transportation Convenience","Reliability of return time to airport"),
        ("Information Provision",    "Sufficiency of tour information"),
        ("Information Provision",    "Convenience of booking process"),
        ("Information Provision",    "Clarity of airport signage"),
        ("Tourism Experience",       "Korean culture experience"),
        ("Tourism Experience",       "Free time at destinations"),
        ("Tourism Experience",       "Food and shopping experience"),
    ]
    rows = []
    for (cat, item), ic, sc in zip(ITEMS, IMP_COLS, SAT_COLS):
        imp = df[ic].mean()
        sat = df[sc].mean()
        rows.append({"Category": cat, "Item": item, "Importance": imp, "Satisfaction": sat, "Gap": sat - imp})

    ipa = pd.DataFrame(rows)
    grand_imp = ipa["Importance"].mean()
    grand_sat = ipa["Satisfaction"].mean()

    def quadrant(row):
        hi = row["Importance"] >= grand_imp
        good = row["Satisfaction"] >= grand_sat
        if hi and good:   return "Keep Up the Good Work"
        if hi and not good: return "Concentrate Here"
        if not hi and good: return "Possible Overkill"
        return "Low Priority"

    ipa["Quadrant"] = ipa.apply(quadrant, axis=1)
    ipa["grand_imp"] = grand_imp
    ipa["grand_sat"] = grand_sat
    return ipa

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:1rem 0 1.5rem;'>
      <div style='font-size:2rem;'>✈</div>
      <div style='font-size:1rem;font-weight:700;color:#cce0f5;'>Transit Tour</div>
      <div style='font-size:.75rem;color:#5a8aaa;'>Survey Dashboard</div>
    </div>
    """, unsafe_allow_html=True)

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

    st.markdown("<hr style='border-color:#1e3a52;margin:1rem 0;'>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='font-size:.78rem;color:#5a8aaa;text-align:center;'>
      n = <b style='color:#cce0f5;'>{N}</b> respondents<br>
      Incheon International Airport
    </div>
    """, unsafe_allow_html=True)

    # Filters (sidebar)
    st.markdown("<div style='margin-top:1.5rem;font-size:.8rem;color:#5a8aaa;font-weight:600;'>FILTERS</div>", unsafe_allow_html=True)
    gender_filter = st.multiselect("Gender", options=df["Gender"].dropna().unique().tolist(),
                                   default=df["Gender"].dropna().unique().tolist(), label_visibility="collapsed")
    st.caption("Gender")
    age_filter = st.multiselect("Age", options=["Under 20","20s","30s","40s","50s","60+"],
                                default=["Under 20","20s","30s","40s","50s","60+"], label_visibility="collapsed")
    st.caption("Age Group")

# Apply filters
dff = df[df["Gender"].isin(gender_filter) & df["Age Group:"].isin(age_filter)]
if len(dff) == 0:
    dff = df.copy()
Nf = len(dff)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 1 · KPI OVERVIEW
# ═════════════════════════════════════════════════════════════════════════════
if page == "📊 KPI Overview":
    st.markdown("""
    <div style='margin-bottom:1.5rem;'>
      <h1 style='color:#cce0f5;font-size:1.8rem;font-weight:800;margin:0;'>
        Free Korea Transit Tour
      </h1>
      <p style='color:#5a8aaa;margin:.2rem 0 0;font-size:.9rem;'>
        Satisfaction Survey Dashboard · Incheon International Airport
      </p>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI Row 1
    section("⚡", "KEY PERFORMANCE INDICATORS")
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    overall_sat = dff["Q34_num"].mean()
    recommend_pct = (dff["Q15.  Would you recommend this transit tour to others?"]
                     .isin(["Definitely yes","Probably yes"]).sum() / Nf * 100)
    revisit_pct = (dff["Q3.  How likely are you to visit Korea as a tourist in the future after this transit tour?"]
                   .eq("Very likely").sum() / Nf * 100)
    tour_increased = (dff["Q22.  Which statement best describes how this transit tour affected your intention to revisit Korea?"]
                      .eq("The tour increased my intention to revisit Korea").sum() / Nf * 100)
    purchase_pct = dff["Q19.  Did you make any additional purchases (food, souvenirs, etc.) during the transit tour?"].eq("Yes").sum() / Nf * 100
    avg_spend = dff["spend_mid"].mean()

    with c1: st.markdown(kpi("Overall Satisfaction", f"{overall_sat:.2f}", "out of 10", "blue"), unsafe_allow_html=True)
    with c2: st.markdown(kpi("Would Recommend", f"{recommend_pct:.1f}%", "Def. + Prob. Yes", "teal"), unsafe_allow_html=True)
    with c3: st.markdown(kpi("Very Likely to Revisit", f"{revisit_pct:.1f}%", "Korea (Q3)", "teal"), unsafe_allow_html=True)
    with c4: st.markdown(kpi("Tour Increased Intent", f"{tour_increased:.1f}%", "to revisit Korea", "purple"), unsafe_allow_html=True)
    with c5: st.markdown(kpi("Made a Purchase", f"{purchase_pct:.1f}%", "during tour", "coral"), unsafe_allow_html=True)
    with c6: st.markdown(kpi("Avg Onsite Spend", f"${avg_spend:.0f}", "USD per buyer", "amber"), unsafe_allow_html=True)

    st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)

    # ── Q34 Distribution + Q15 Recommend side by side
    section("📈", "SATISFACTION & RECOMMENDATION")
    col_left, col_right = st.columns([1.4, 1])

    with col_left:
        sat_dist = dff["Q34_num"].value_counts().sort_index()
        fig_sat = go.Figure()
        colors = ["#E24B4A" if v<=4 else "#EF9F27" if v<=6 else "#185FA5" if v<=8 else "#1D9E75"
                  for v in sat_dist.index]
        fig_sat.add_trace(go.Bar(
            x=sat_dist.index.astype(str), y=sat_dist.values,
            marker_color=colors, text=sat_dist.values, textposition="outside",
            textfont=dict(color=TEXT_CLR, size=11),
        ))
        fig_sat.update_layout(**PLOTLY_LAYOUT, title="Q34 Overall Satisfaction Distribution (0–10)",
                               xaxis=dict(gridcolor=GRID_CLR, title="Score"),
                               yaxis=dict(gridcolor=GRID_CLR, title="Respondents"), height=320)
        st.plotly_chart(fig_sat, use_container_width=True)

    with col_right:
        rec = dff["Q15.  Would you recommend this transit tour to others?"].value_counts()
        colors_rec = {"Definitely yes": "#1D9E75", "Probably yes": "#185FA5", "Not sure": "#EF9F27"}
        fig_rec = go.Figure(go.Pie(
            labels=rec.index, values=rec.values,
            marker_colors=[colors_rec.get(l, "#888") for l in rec.index],
            hole=.55, textfont=dict(size=12),
            hovertemplate="%{label}: %{value} (%{percent})<extra></extra>",
        ))
        fig_rec.update_layout(**PLOTLY_LAYOUT, title="Q15 Would You Recommend?", height=320,
                               legend=dict(orientation="v", x=1.05, y=.5))
        st.plotly_chart(fig_rec, use_container_width=True)

    # ── Tour Element Satisfaction (Q27)
    section("⭐", "TOUR ELEMENT SATISFACTION (Q27)")
    Q27_COLS = [c for c in df.columns if "Q27." in c]
    q27_labels = [c.split("[")[1].rstrip("]") for c in Q27_COLS]
    q27_means  = [dff[c].mean() for c in Q27_COLS]
    q27_sorted = sorted(zip(q27_means, q27_labels), reverse=True)
    means_s, labels_s = zip(*q27_sorted)

    fig_q27 = go.Figure(go.Bar(
        x=list(means_s), y=list(labels_s), orientation="h",
        marker=dict(
            color=list(means_s),
            colorscale=[[0,"#185FA5"],[0.5,"#1D9E75"],[1,"#2DD4A0"]],
            cmin=4.0, cmax=5.0,
        ),
        text=[f"{v:.3f}" for v in means_s], textposition="outside",
        textfont=dict(color=TEXT_CLR, size=12),
    ))
    fig_q27.update_layout(**PLOTLY_LAYOUT, title="Average Score (1=Very dissatisfied → 5=Very satisfied)",
                           xaxis=dict(range=[4.0, 5.2], gridcolor=GRID_CLR, title="Average Score"),
                           yaxis=dict(gridcolor=GRID_CLR), height=320)
    st.plotly_chart(fig_q27, use_container_width=True)

    # ── Q22 revisit intent + Q25 share intent
    section("🔄", "REVISIT INTENT & SHARING")
    c1, c2 = st.columns(2)
    with c1:
        q22 = dff["Q22.  Which statement best describes how this transit tour affected your intention to revisit Korea?"].value_counts()
        short = {
            "The tour increased my intention to revisit Korea": "Tour increased intent",
            "I had already planned to revisit before the tour": "Already planned",
            "The tour did not greatly affect my intention, but I may revisit Korea": "Unaffected but may revisit",
            "The tour decreased my intention to revisit Korea": "Decreased intent",
        }
        q22.index = [short.get(i, i) for i in q22.index]
        cols_q22 = ["#1D9E75","#185FA5","#EF9F27","#E24B4A"]
        fig22 = go.Figure(go.Bar(
            x=q22.values, y=q22.index, orientation="h",
            marker_color=cols_q22[:len(q22)],
            text=[f"{v}  ({v/Nf*100:.1f}%)" for v in q22.values], textposition="outside",
            textfont=dict(color=TEXT_CLR, size=11),
        ))
        fig22.update_layout(**PLOTLY_LAYOUT, title="Q22 How Tour Affected Revisit Intention",
                             xaxis=dict(gridcolor=GRID_CLR), yaxis=dict(gridcolor=GRID_CLR), height=280)
        st.plotly_chart(fig22, use_container_width=True)

    with c2:
        q25 = dff["Q25.  Do you intend to share your tour experience on social media, a blog, or a review platform?"].value_counts()
        fig25 = go.Figure(go.Pie(
            labels=q25.index, values=q25.values,
            marker_colors=["#1D9E75","#E24B4A","#185FA5"],
            hole=.5, textfont=dict(size=12),
        ))
        fig25.update_layout(**PLOTLY_LAYOUT, title="Q25 Social Media Sharing Intent", height=280)
        st.plotly_chart(fig25, use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 2 · DEMOGRAPHICS
# ═════════════════════════════════════════════════════════════════════════════
elif page == "👥 Demographics":
    st.markdown("<h1 style='color:#cce0f5;font-size:1.8rem;font-weight:800;margin:0 0 1.5rem;'>Respondent Demographics</h1>", unsafe_allow_html=True)

    # Gender / Age / Purpose / Visits
    section("👤", "PROFILE BREAKDOWN")
    c1,c2,c3,c4 = st.columns(4)

    with c1:
        gender = dff["Gender"].value_counts()
        fig = go.Figure(go.Pie(labels=gender.index, values=gender.values,
                               marker_colors=["#1D9E75","#185FA5","#6B6B6B"],
                               hole=.5, textfont=dict(size=12)))
        fig.update_layout(**PLOTLY_LAYOUT, title="Gender", height=280)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        age_order = ["Under 20","20s","30s","40s","50s","60+"]
        age = dff["Age Group:"].value_counts().reindex(age_order).dropna()
        fig = go.Figure(go.Bar(
            x=age.index, y=age.values, marker_color="#185FA5",
            text=age.values, textposition="outside", textfont=dict(color=TEXT_CLR)))
        fig.update_layout(**PLOTLY_LAYOUT, title="Age Group", height=280,
                           xaxis=dict(gridcolor=GRID_CLR), yaxis=dict(gridcolor=GRID_CLR))
        st.plotly_chart(fig, use_container_width=True)

    with c3:
        purp = dff["Purpose"].value_counts()
        fig = go.Figure(go.Pie(labels=purp.index, values=purp.values,
                               marker_colors=["#1D9E75","#185FA5","#EF9F27","#534AB7"],
                               hole=.5, textfont=dict(size=11)))
        fig.update_layout(**PLOTLY_LAYOUT, title="Travel Purpose", height=280)
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        prev = dff["Previous visits to Korea"].value_counts()
        fig = go.Figure(go.Pie(labels=prev.index, values=prev.values,
                               marker_colors=["#534AB7","#1D9E75","#EF9F27"],
                               hole=.5, textfont=dict(size=12)))
        fig.update_layout(**PLOTLY_LAYOUT, title="Previous Visits to Korea", height=280)
        st.plotly_chart(fig, use_container_width=True)

    # Nationality
    section("🌍", "TOP NATIONALITIES")
    nat = dff["1.1. Nationality:"].value_counts().head(12)
    fig_nat = go.Figure(go.Bar(
        x=nat.values, y=nat.index, orientation="h",
        marker=dict(color=nat.values, colorscale=[[0,"#185FA5"],[1,"#1D9E75"]], showscale=False),
        text=[f"{v}  ({v/Nf*100:.1f}%)" for v in nat.values], textposition="outside",
        textfont=dict(color=TEXT_CLR, size=11),
    ))
    fig_nat.update_layout(**PLOTLY_LAYOUT, title="Number of Respondents per Nationality (Top 12)",
                           xaxis=dict(gridcolor=GRID_CLR), yaxis=dict(gridcolor=GRID_CLR), height=380)
    st.plotly_chart(fig_nat, use_container_width=True)

    # Tours joined
    section("🗺", "TOURS JOINED")
    tours = dff["Which tour did you join?"].value_counts()
    short_tours = [t.split("(")[0].strip()[:52] for t in tours.index]
    fig_tours = go.Figure(go.Bar(
        x=tours.values, y=short_tours, orientation="h",
        marker_color="#534AB7",
        text=[f"{v}  ({v/Nf*100:.1f}%)" for v in tours.values], textposition="outside",
        textfont=dict(color=TEXT_CLR, size=11),
    ))
    fig_tours.update_layout(**PLOTLY_LAYOUT, title="Tour Participation by Program",
                             xaxis=dict(gridcolor=GRID_CLR), yaxis=dict(gridcolor=GRID_CLR), height=360)
    st.plotly_chart(fig_tours, use_container_width=True)

    # Q3 revisit + layover duration
    section("⏱", "REVISIT INTENTION & LAYOVER")
    c1, c2 = st.columns(2)
    with c1:
        q3 = dff["Q3.  How likely are you to visit Korea as a tourist in the future after this transit tour?"].value_counts()
        order3 = ["Very likely","Option 2","Neutral","Unlikely","Very unlikely"]
        q3 = q3.reindex([o for o in order3 if o in q3.index])
        cols3 = ["#1D9E75","#185FA5","#EF9F27","#E24B4A","#8B0000"]
        fig3 = go.Figure(go.Bar(
            x=q3.index, y=q3.values, marker_color=cols3[:len(q3)],
            text=[f"{v}\n({v/Nf*100:.1f}%)" for v in q3.values], textposition="outside",
            textfont=dict(color=TEXT_CLR, size=11),
        ))
        fig3.update_layout(**PLOTLY_LAYOUT, title="Q3 Likelihood to Visit Korea",
                           xaxis=dict(gridcolor=GRID_CLR), yaxis=dict(gridcolor=GRID_CLR), height=300)
        st.plotly_chart(fig3, use_container_width=True)

    with c2:
        q7 = dff["Q7.  What is the total duration of your layover at Incheon Airport?"].value_counts()
        fig7 = go.Figure(go.Pie(labels=q7.index, values=q7.values,
                                marker_colors=px.colors.sequential.Blues_r[:len(q7)],
                                hole=.5, textfont=dict(size=11)))
        fig7.update_layout(**PLOTLY_LAYOUT, title="Q7 Layover Duration", height=300)
        st.plotly_chart(fig7, use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 3 · IPA ANALYSIS
# ═════════════════════════════════════════════════════════════════════════════
elif page == "🎯 IPA Analysis":
    st.markdown("<h1 style='color:#cce0f5;font-size:1.8rem;font-weight:800;margin:0 0 .3rem;'>Importance–Performance Analysis (IPA)</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#5a8aaa;margin-bottom:1.5rem;'>15 items · 5 categories · Scale 1–5 · Gap = Satisfaction − Importance</p>", unsafe_allow_html=True)

    # Recompute on filtered data
    IMP_COLS_F = [c for c in dff.columns if "-1)" in c and "Importance" in c]
    SAT_COLS_F = [c for c in dff.columns if "-2)" in c and "Satisfaction" in c]

    ITEM_META = [
        ("Program Composition",       "Variety of tour programs"),
        ("Program Composition",       "Attractiveness of destinations"),
        ("Program Composition",       "Appropriateness of tour schedule"),
        ("Operation & Service",       "Tour guide expertise"),
        ("Operation & Service",       "Guide friendliness"),
        ("Operation & Service",       "Smooth operation of the tour"),
        ("Transportation Convenience","Comfort of the tour bus"),
        ("Transportation Convenience","Appropriateness of travel time"),
        ("Transportation Convenience","Reliability of return time to airport"),
        ("Information Provision",     "Sufficiency of tour information"),
        ("Information Provision",     "Convenience of booking process"),
        ("Information Provision",     "Clarity of airport signage"),
        ("Tourism Experience",        "Korean culture experience"),
        ("Tourism Experience",        "Free time at destinations"),
        ("Tourism Experience",        "Food and shopping experience"),
    ]

    ipa_rows = []
    for (cat, item), ic, sc in zip(ITEM_META, IMP_COLS_F, SAT_COLS_F):
        imp_vals = pd.to_numeric(dff[ic].map({"5 (Very high)":5,"4":4,"3":3,"2":2,"1 (Very low)":1}).fillna(dff[ic]), errors="coerce")
        sat_vals = pd.to_numeric(dff[sc].map({"5 (Very high)":5,"4":4,"3":3,"2":2,"1 (Very low)":1}).fillna(dff[sc]), errors="coerce")
        ipa_rows.append({
            "Category": cat, "Item": item,
            "Importance": imp_vals.mean(), "Satisfaction": sat_vals.mean(),
            "Gap": sat_vals.mean() - imp_vals.mean(),
        })
    ipa = pd.DataFrame(ipa_rows)
    grand_imp = ipa["Importance"].mean()
    grand_sat = ipa["Satisfaction"].mean()

    def quad(row):
        hi = row["Importance"] >= grand_imp
        good = row["Satisfaction"] >= grand_sat
        if hi and good:     return "Keep Up the Good Work"
        if hi and not good: return "Concentrate Here"
        if not hi and good: return "Possible Overkill"
        return "Low Priority"

    ipa["Quadrant"] = ipa.apply(quad, axis=1)

    # ── Scatter IPA chart
    section("📍", "IPA QUADRANT — 15 ITEMS")
    fig_ipa = go.Figure()

    # Quadrant background rectangles
    x_min, x_max = ipa["Importance"].min()-.04, ipa["Importance"].max()+.04
    y_min, y_max = ipa["Satisfaction"].min()-.04, ipa["Satisfaction"].max()+.04

    quad_fills = [
        (grand_imp, x_max, grand_sat, y_max, "rgba(29,158,117,.06)", "Keep Up"),
        (x_min, grand_imp, grand_sat, y_max, "rgba(239,159,39,.06)", "Possible Overkill"),
        (grand_imp, x_max, y_min, grand_sat, "rgba(226,75,74,.06)", "Concentrate Here"),
        (x_min, grand_imp, y_min, grand_sat, "rgba(107,107,107,.06)", "Low Priority"),
    ]
    for x0, x1, y0, y1, clr, _ in quad_fills:
        fig_ipa.add_shape(type="rect", x0=x0, x1=x1, y0=y0, y1=y1,
                          fillcolor=clr, line_width=0, layer="below")

    # Average lines
    fig_ipa.add_shape(type="line", x0=grand_imp, x1=grand_imp, y0=y_min, y1=y_max,
                      line=dict(color="#5a8aaa", width=1.5, dash="dash"))
    fig_ipa.add_shape(type="line", x0=x_min, x1=x_max, y0=grand_sat, y1=grand_sat,
                      line=dict(color="#5a8aaa", width=1.5, dash="dash"))

    # Quadrant labels
    fig_ipa.add_annotation(x=grand_imp+.005, y=y_max-.005, text="★ Keep Up", showarrow=False,
                            font=dict(color="#1D9E75", size=11, family="Inter"), xanchor="left", yanchor="top")
    fig_ipa.add_annotation(x=x_min+.003, y=y_max-.005, text="◆ Possible Overkill", showarrow=False,
                            font=dict(color="#EF9F27", size=11, family="Inter"), xanchor="left", yanchor="top")
    fig_ipa.add_annotation(x=grand_imp+.005, y=y_min+.003, text="▲ Concentrate Here", showarrow=False,
                            font=dict(color="#E24B4A", size=11, family="Inter"), xanchor="left", yanchor="bottom")
    fig_ipa.add_annotation(x=x_min+.003, y=y_min+.003, text="○ Low Priority", showarrow=False,
                            font=dict(color="#6B6B6B", size=11, family="Inter"), xanchor="left", yanchor="bottom")

    # Plot each category as separate trace for legend
    for cat in ipa["Category"].unique():
        sub = ipa[ipa["Category"] == cat]
        fig_ipa.add_trace(go.Scatter(
            x=sub["Importance"], y=sub["Satisfaction"],
            mode="markers+text",
            name=cat,
            text=sub["Item"].str[:28],
            textposition="top center",
            textfont=dict(size=9, color=TEXT_CLR),
            marker=dict(size=14, color=CATEGORY_COLORS[cat],
                        line=dict(width=2, color="white"), symbol="circle"),
            customdata=sub[["Gap","Quadrant"]],
            hovertemplate="<b>%{text}</b><br>Importance: %{x:.3f}<br>Satisfaction: %{y:.3f}<br>Gap: %{customdata[0]:+.3f}<br>Quadrant: %{customdata[1]}<extra></extra>",
        ))

    fig_ipa.update_layout(
        **PLOTLY_LAYOUT,
        title=f"IPA Scatter (grand mean Importance={grand_imp:.3f}, Satisfaction={grand_sat:.3f})",
        xaxis=dict(title="Importance (avg 1–5)", gridcolor=GRID_CLR, range=[x_min, x_max]),
        yaxis=dict(title="Satisfaction (avg 1–5)", gridcolor=GRID_CLR, range=[y_min, y_max]),
        height=560, showlegend=True,
    )
    st.plotly_chart(fig_ipa, use_container_width=True)

    # ── Category-level IPA
    section("📊", "CATEGORY-LEVEL IPA SUMMARY")
    cat_ipa = ipa.groupby("Category").agg({"Importance":"mean","Satisfaction":"mean","Gap":"mean"}).reset_index()
    grand_cat_imp = cat_ipa["Importance"].mean()
    grand_cat_sat = cat_ipa["Satisfaction"].mean()

    def cat_quad(row):
        hi = row["Importance"] >= grand_cat_imp
        good = row["Satisfaction"] >= grand_cat_sat
        if hi and good:     return "Keep Up the Good Work"
        if hi and not good: return "Concentrate Here"
        if not hi and good: return "Possible Overkill"
        return "Low Priority"
    cat_ipa["Quadrant"] = cat_ipa.apply(cat_quad, axis=1)

    c_left, c_right = st.columns([1.3, 1])
    with c_left:
        fig_cat = go.Figure()
        xm, xM = cat_ipa["Importance"].min()-.02, cat_ipa["Importance"].max()+.02
        ym, yM = cat_ipa["Satisfaction"].min()-.02, cat_ipa["Satisfaction"].max()+.02
        for x0, x1, y0, y1, clr in [
            (grand_cat_imp,xM,grand_cat_sat,yM,"rgba(29,158,117,.08)"),
            (xm,grand_cat_imp,grand_cat_sat,yM,"rgba(239,159,39,.08)"),
            (grand_cat_imp,xM,ym,grand_cat_sat,"rgba(226,75,74,.08)"),
            (xm,grand_cat_imp,ym,grand_cat_sat,"rgba(107,107,107,.08)"),
        ]:
            fig_cat.add_shape(type="rect", x0=x0,x1=x1,y0=y0,y1=y1,fillcolor=clr,line_width=0,layer="below")
        fig_cat.add_shape(type="line",x0=grand_cat_imp,x1=grand_cat_imp,y0=ym,y1=yM,line=dict(color="#5a8aaa",width=1.5,dash="dash"))
        fig_cat.add_shape(type="line",x0=xm,x1=xM,y0=grand_cat_sat,y1=grand_cat_sat,line=dict(color="#5a8aaa",width=1.5,dash="dash"))

        for _, row in cat_ipa.iterrows():
            col = CATEGORY_COLORS[row["Category"]]
            qcol = QUAD_COLORS[row["Quadrant"]]
            fig_cat.add_trace(go.Scatter(
                x=[row["Importance"]], y=[row["Satisfaction"]],
                mode="markers+text", name=row["Category"],
                text=[row["Category"].split()[0]],
                textposition="top center", textfont=dict(size=10,color=col),
                marker=dict(size=20, color=col, line=dict(width=2,color="white")),
                hovertemplate=f"<b>{row['Category']}</b><br>Importance: {row['Importance']:.3f}<br>Satisfaction: {row['Satisfaction']:.3f}<br>Gap: {row['Gap']:+.3f}<br>Quadrant: {row['Quadrant']}<extra></extra>",
            ))
        fig_cat.update_layout(**PLOTLY_LAYOUT, title="Category IPA",
                               xaxis=dict(title="Importance",gridcolor=GRID_CLR,range=[xm,xM]),
                               yaxis=dict(title="Satisfaction",gridcolor=GRID_CLR,range=[ym,yM]),
                               height=380, showlegend=False)
        st.plotly_chart(fig_cat, use_container_width=True)

    with c_right:
        # Table
        st.markdown("<div style='height:.5rem;'></div>", unsafe_allow_html=True)
        quad_emoji = {"Keep Up the Good Work":"★","Concentrate Here":"▲","Possible Overkill":"◆","Low Priority":"○"}
        for _, row in cat_ipa.sort_values("Importance", ascending=False).iterrows():
            qe = quad_emoji[row["Quadrant"]]
            qcls = {"Keep Up the Good Work":"quad-keep","Concentrate Here":"quad-conc","Possible Overkill":"quad-over","Low Priority":"quad-low"}[row["Quadrant"]]
            gap_clr = "#1D9E75" if row["Gap"] >= 0 else "#E24B4A"
            st.markdown(f"""
            <div style='background:#0f2035;border:1px solid #1e3a52;border-radius:10px;padding:.8rem 1rem;margin-bottom:.6rem;'>
              <div style='display:flex;justify-content:space-between;align-items:center;'>
                <span style='color:#cce0f5;font-weight:600;font-size:.88rem;'>{row["Category"]}</span>
                <span class='quad-badge {qcls}'>{qe} {row["Quadrant"]}</span>
              </div>
              <div style='display:flex;gap:1.5rem;margin-top:.5rem;'>
                <span style='font-size:.8rem;color:#5a8aaa;'>Imp: <b style='color:#5ab0ff;'>{row["Importance"]:.3f}</b></span>
                <span style='font-size:.8rem;color:#5a8aaa;'>Sat: <b style='color:#2dd4a0;'>{row["Satisfaction"]:.3f}</b></span>
                <span style='font-size:.8rem;color:#5a8aaa;'>Gap: <b style='color:{gap_clr};'>{row["Gap"]:+.3f}</b></span>
              </div>
            </div>
            """, unsafe_allow_html=True)

    # ── 15-item detail table
    section("📋", "15-ITEM DETAIL TABLE")
    display_ipa = ipa[["Category","Item","Importance","Satisfaction","Gap","Quadrant"]].copy()
    display_ipa["Importance"] = display_ipa["Importance"].round(3)
    display_ipa["Satisfaction"] = display_ipa["Satisfaction"].round(3)
    display_ipa["Gap"] = display_ipa["Gap"].round(3)
    st.dataframe(
        display_ipa,
        use_container_width=True,
        column_config={
            "Importance":   st.column_config.ProgressColumn("Importance", min_value=4.0, max_value=5.0, format="%.3f"),
            "Satisfaction": st.column_config.ProgressColumn("Satisfaction", min_value=4.0, max_value=5.0, format="%.3f"),
            "Gap":          st.column_config.NumberColumn("Gap (Sat−Imp)", format="%+.3f"),
            "Quadrant":     st.column_config.TextColumn("Quadrant"),
        },
        height=560,
    )

    # ── Gap bar chart
    section("📉", "GAP ANALYSIS (Satisfaction − Importance)")
    ipa_sorted = ipa.sort_values("Gap")
    gap_colors = ["#E24B4A" if g < 0 else "#1D9E75" for g in ipa_sorted["Gap"]]
    fig_gap = go.Figure(go.Bar(
        x=ipa_sorted["Gap"], y=ipa_sorted["Item"], orientation="h",
        marker_color=gap_colors,
        text=[f"{g:+.3f}" for g in ipa_sorted["Gap"]], textposition="outside",
        textfont=dict(color=TEXT_CLR, size=11),
    ))
    fig_gap.add_vline(x=0, line_color="#5a8aaa", line_width=1.5)
    fig_gap.update_layout(**PLOTLY_LAYOUT, title="Gap = Satisfaction − Importance  (Positive = Over-delivery)",
                           xaxis=dict(title="Gap", gridcolor=GRID_CLR, zeroline=True, zerolinecolor=GRID_CLR),
                           yaxis=dict(gridcolor=GRID_CLR), height=460)
    st.plotly_chart(fig_gap, use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 4 · AIRPORT COMPETITIVENESS
# ═════════════════════════════════════════════════════════════════════════════
elif page == "✈ Airport Competitiveness":
    st.markdown("<h1 style='color:#cce0f5;font-size:1.8rem;font-weight:800;margin:0 0 1.5rem;'>Airport Competitiveness</h1>", unsafe_allow_html=True)

    # KPI row
    section("⚡", "KEY METRICS")
    c1,c2,c3,c4 = st.columns(4)
    tour_influenced = dff["Q9.  Did the transit tour program influence your decision to transit through Incheon Airport?"].isin(["A lot","Somewhat"]).sum()/Nf*100
    future_likely   = dff["Q10.  When booking future flights, would the availability of a transit tour program make you more likely to choose Incheon Airport as a transit hub?"].isin(["Much more likely","Somewhat more likely"]).sum()/Nf*100
    knew_influenced = dff["Q12.  Did you know about the transit tour BEFORE choosing Incheon Airport?"].eq("Knew about it and it influenced my choice").sum()/Nf*100
    chose_tour      = dff["Q14.  What was the PRIMARY reason you chose Incheon Airport as your transit hub?"].eq("Availability of the transit tour program").sum()/Nf*100

    with c1: st.markdown(kpi("Tour Influenced ICN Choice","A lot/Somewhat",f"{tour_influenced:.1f}%","blue"), unsafe_allow_html=True)
    with c2: st.markdown(kpi("Future ICN More Likely",f"{future_likely:.1f}%","Much/Somewhat","teal"), unsafe_allow_html=True)
    with c3: st.markdown(kpi("Knew & It Influenced",f"{knew_influenced:.1f}%","pre-selection","purple"), unsafe_allow_html=True)
    with c4: st.markdown(kpi("Primary Reason: Tour",f"{chose_tour:.1f}%","of respondents","coral"), unsafe_allow_html=True)

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

    c_left, c_right = st.columns(2)

    with c_left:
        # Q9
        section("📌", "Q9 — TOUR INFLUENCE ON ICN DECISION")
        q9 = dff["Q9.  Did the transit tour program influence your decision to transit through Incheon Airport?"].value_counts()
        order9 = ["A lot","Somewhat","Neutral","Very little","Not at all"]
        q9 = q9.reindex([o for o in order9 if o in q9.index])
        colors9 = ["#1D9E75","#185FA5","#EF9F27","#E24B4A","#8B0000"]
        fig9 = go.Figure(go.Bar(
            x=q9.index, y=q9.values, marker_color=colors9[:len(q9)],
            text=[f"{v}<br>({v/Nf*100:.1f}%)" for v in q9.values], textposition="outside",
            textfont=dict(color=TEXT_CLR, size=11),
        ))
        fig9.update_layout(**PLOTLY_LAYOUT, xaxis=dict(gridcolor=GRID_CLR), yaxis=dict(gridcolor=GRID_CLR), height=320)
        st.plotly_chart(fig9, use_container_width=True)

        # Q12
        section("💡", "Q12 — AWARENESS BEFORE CHOOSING ICN")
        q12 = dff["Q12.  Did you know about the transit tour BEFORE choosing Incheon Airport?"].value_counts()
        short12 = {"Knew about it and it influenced my choice":"Knew & Influenced",
                   "Found out after choosing Incheon":"Found Out After",
                   "Did not know about it":"Did Not Know",
                   "Knew about it but it did not affect my choice":"Knew, No Effect"}
        q12.index = [short12.get(i, i) for i in q12.index]
        fig12 = go.Figure(go.Pie(labels=q12.index, values=q12.values,
                                  marker_colors=["#1D9E75","#EF9F27","#E24B4A","#185FA5"],
                                  hole=.5, textfont=dict(size=12)))
        fig12.update_layout(**PLOTLY_LAYOUT, height=320)
        st.plotly_chart(fig12, use_container_width=True)

    with c_right:
        # Q10
        section("🔮", "Q10 — FUTURE ICN TRANSIT CHOICE")
        q10 = dff["Q10.  When booking future flights, would the availability of a transit tour program make you more likely to choose Incheon Airport as a transit hub?"].value_counts()
        order10 = ["Much more likely","Somewhat more likely","No change","Somewhat less likely","Much less likely"]
        q10 = q10.reindex([o for o in order10 if o in q10.index])
        cols10 = ["#1D9E75","#185FA5","#EF9F27","#E24B4A","#8B0000"]
        fig10 = go.Figure(go.Bar(
            x=q10.index, y=q10.values, marker_color=cols10[:len(q10)],
            text=[f"{v}<br>({v/Nf*100:.1f}%)" for v in q10.values], textposition="outside",
            textfont=dict(color=TEXT_CLR, size=11),
        ))
        fig10.update_layout(**PLOTLY_LAYOUT, xaxis=dict(gridcolor=GRID_CLR,tickangle=-20), yaxis=dict(gridcolor=GRID_CLR), height=320)
        st.plotly_chart(fig10, use_container_width=True)

        # Q14
        section("🎯", "Q14 — PRIMARY REASON FOR CHOOSING ICN")
        q14 = dff["Q14.  What was the PRIMARY reason you chose Incheon Airport as your transit hub?"].value_counts().head(6)
        short14 = {
            "Availability of the transit tour program":"Transit Tour Program",
            "Lower airfare price":"Lower Airfare",
            "Suitable flight schedule":"Flight Schedule",
            "Previous positive experience":"Past Experience",
            "Superior airport facilities":"Airport Facilities",
        }
        q14.index = [short14.get(i, i[:30]) for i in q14.index]
        fig14 = go.Figure(go.Bar(
            x=q14.values, y=q14.index, orientation="h",
            marker=dict(color=q14.values, colorscale=[[0,"#185FA5"],[1,"#1D9E75"]], showscale=False),
            text=[f"{v}  ({v/Nf*100:.1f}%)" for v in q14.values], textposition="outside",
            textfont=dict(color=TEXT_CLR, size=11),
        ))
        fig14.update_layout(**PLOTLY_LAYOUT, xaxis=dict(gridcolor=GRID_CLR), yaxis=dict(gridcolor=GRID_CLR), height=320)
        st.plotly_chart(fig14, use_container_width=True)

    # Q21 WTP
    section("💰", "Q21 — WILLINGNESS TO PAY")
    wtp_raw = dff["Q21.  If this tour were offered as a paid program, what would you be willing to pay?"]
    wtp_clean = wtp_raw.map(lambda x: x if x in ["It should remain free","$10 or less","$11 – $20","$21 – $30","$31 – $50"] else np.nan).dropna()
    wtp = wtp_clean.value_counts().reindex(["It should remain free","$10 or less","$11 – $20","$21 – $30","$31 – $50"]).dropna()
    cols_wtp = ["#E24B4A","#EF9F27","#185FA5","#1D9E75","#534AB7"]
    fig_wtp = go.Figure(go.Bar(
        x=wtp.index, y=wtp.values, marker_color=cols_wtp,
        text=[f"{v}\n({v/len(wtp_clean)*100:.1f}%)" for v in wtp.values], textposition="outside",
        textfont=dict(color=TEXT_CLR, size=12),
    ))
    fig_wtp.update_layout(**PLOTLY_LAYOUT, xaxis=dict(gridcolor=GRID_CLR), yaxis=dict(gridcolor=GRID_CLR), height=300)
    st.plotly_chart(fig_wtp, use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 5 · BUSINESS INSIGHTS
# ═════════════════════════════════════════════════════════════════════════════
elif page == "💡 Business Insights":
    st.markdown("<h1 style='color:#cce0f5;font-size:1.8rem;font-weight:800;margin:0 0 1.5rem;'>Business Insights</h1>", unsafe_allow_html=True)

    section("💴", "SPENDING SIGNALS")
    c1,c2,c3 = st.columns(3)
    avg_spend = dff["spend_mid"].mean()
    avg_future = dff["future_spend_mid"].mean()
    purchase_pct = dff["Q19.  Did you make any additional purchases (food, souvenirs, etc.) during the transit tour?"].eq("Yes").sum()/Nf*100
    with c1: st.markdown(kpi("Purchase Rate (Q19)",f"{purchase_pct:.1f}%","made a purchase","teal"), unsafe_allow_html=True)
    with c2: st.markdown(kpi("Avg Onsite Spend",f"${avg_spend:.0f}","USD (buyers only)","blue"), unsafe_allow_html=True)
    with c3: st.markdown(kpi("Avg Future Trip Budget",f"${avg_future:,.0f}","USD expected","amber"), unsafe_allow_html=True)

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        # Q19-2 spending distribution
        section("🛍", "Q19-2 — ONSITE SPENDING DISTRIBUTION")
        spend_vals = dff["Q19-2.  Approximate total spending (USD)?"].value_counts()
        order_s = ["$10 or less","$11 – $50","$51 – $100","$101 – $200","More than $200"]
        spend_vals = spend_vals.reindex([o for o in order_s if o in spend_vals.index])
        fig_sp = go.Figure(go.Bar(
            x=spend_vals.index, y=spend_vals.values, marker_color="#185FA5",
            text=[f"{v}\n({v/Nf*100:.1f}%)" for v in spend_vals.values], textposition="outside",
            textfont=dict(color=TEXT_CLR,size=11),
        ))
        fig_sp.update_layout(**PLOTLY_LAYOUT, xaxis=dict(gridcolor=GRID_CLR), yaxis=dict(gridcolor=GRID_CLR), height=300)
        st.plotly_chart(fig_sp, use_container_width=True)

    with c2:
        # Q20 future spend
        section("🏦", "Q20 — EXPECTED FUTURE TRIP SPEND")
        q20 = dff["Q20.  If you visit Korea as a tourist in the future, how much do you expect to spend in total?"].value_counts()
        order20 = ["$500 or less","$501 – $1,000","$1,001 – $2,000","$2,001 – $3,000","More than $3,000"]
        q20 = q20.reindex([o for o in order20 if o in q20.index])
        fig20 = go.Figure(go.Bar(
            x=q20.index, y=q20.values, marker_color="#1D9E75",
            text=[f"{v}\n({v/Nf*100:.1f}%)" for v in q20.values], textposition="outside",
            textfont=dict(color=TEXT_CLR,size=11),
        ))
        fig20.update_layout(**PLOTLY_LAYOUT, xaxis=dict(gridcolor=GRID_CLR,tickangle=-20), yaxis=dict(gridcolor=GRID_CLR), height=300)
        st.plotly_chart(fig20, use_container_width=True)

    # Priority vs Satisfaction
    section("⚖", "PRIORITY vs. SATISFACTION GAP  (Q26 vs Q31)")
    q26 = dff["Q26.  Which category do you consider most IMPORTANT in a transit tour?"].value_counts(normalize=True)
    q31 = dff["Q31.  Which category of this transit tour were you most satisfied with?"].value_counts(normalize=True)
    cats_pvs = ["Program Composition","Operation & Service","Transportation Convenience","Information Provision","Tourism Experience"]
    q26_alias = {"Program composition":"Program Composition","Operation & service":"Operation & Service",
                 "Transportation convenience":"Transportation Convenience","Information provision":"Information Provision","Tourism experience":"Tourism Experience"}
    q31_alias = {"Program composition":"Program Composition","Operation & service":"Operation & Service",
                 "Transportation convenience":"Transportation Convenience","Information provision":"Information Provision","Tourism experience":"Tourism Experience"}
    q26r = {q26_alias.get(k,k): v for k,v in q26.items()}
    q31r = {q31_alias.get(k,k): v for k,v in q31.items()}
    pvs_imp = [q26r.get(c,0) for c in cats_pvs]
    pvs_sat = [q31r.get(c,0) for c in cats_pvs]
    pvs_gap = [s-i for i,s in zip(pvs_imp,pvs_sat)]

    fig_pvs = make_subplots(rows=1, cols=2, subplot_titles=["% Rated Most Important (Q26) vs Most Satisfying (Q31)","Gap (Satisfaction − Importance)"])
    fig_pvs.add_trace(go.Bar(name="Most Important (Q26)", x=cats_pvs, y=pvs_imp,
                              marker_color="#185FA5", text=[f"{v:.1%}" for v in pvs_imp], textposition="outside",
                              textfont=dict(color=TEXT_CLR,size=10)), row=1, col=1)
    fig_pvs.add_trace(go.Bar(name="Most Satisfying (Q31)", x=cats_pvs, y=pvs_sat,
                              marker_color="#1D9E75", text=[f"{v:.1%}" for v in pvs_sat], textposition="outside",
                              textfont=dict(color=TEXT_CLR,size=10)), row=1, col=1)
    gap_cols = ["#1D9E75" if g>=0 else "#E24B4A" for g in pvs_gap]
    fig_pvs.add_trace(go.Bar(name="Gap", x=cats_pvs, y=pvs_gap,
                              marker_color=gap_cols, text=[f"{g:+.1%}" for g in pvs_gap], textposition="outside",
                              textfont=dict(color=TEXT_CLR,size=10), showlegend=False), row=1, col=2)
    fig_pvs.add_hline(y=0, line_color="#5a8aaa", line_width=1, row=1, col=2)
    fig_pvs.update_layout(**PLOTLY_LAYOUT, height=380, barmode="group",
                           xaxis=dict(gridcolor=GRID_CLR,tickangle=-15),
                           xaxis2=dict(gridcolor=GRID_CLR,tickangle=-15),
                           yaxis=dict(gridcolor=GRID_CLR,tickformat=".0%"),
                           yaxis2=dict(gridcolor=GRID_CLR,tickformat=".0%"))
    st.plotly_chart(fig_pvs, use_container_width=True)

    # Q24 barriers
    section("🚧", "Q24 — BARRIERS TO REVISITING KOREA")
    q24_raw = dff["Q24.  What are the main barriers to revisiting Korea as a tourist?"].dropna()
    barrier_counts = {}
    for row in q24_raw:
        for b in str(row).split(","):
            b = b.strip()
            if b: barrier_counts[b] = barrier_counts.get(b, 0) + 1
    barriers = pd.Series(barrier_counts).sort_values(ascending=True).tail(8)
    fig_b = go.Figure(go.Bar(
        x=barriers.values, y=barriers.index, orientation="h",
        marker=dict(color=barriers.values, colorscale=[[0,"#185FA5"],[1,"#E24B4A"]], showscale=False),
        text=[f"{v}" for v in barriers.values], textposition="outside",
        textfont=dict(color=TEXT_CLR,size=11),
    ))
    fig_b.update_layout(**PLOTLY_LAYOUT, xaxis=dict(gridcolor=GRID_CLR), yaxis=dict(gridcolor=GRID_CLR), height=320)
    st.plotly_chart(fig_b, use_container_width=True)

    # Q23 desired region
    section("🗺", "Q23 — DESIRED REGION FOR NEXT KOREA TRIP")
    q23 = dff["Q23.  Which region would you most like to visit on your next trip to Korea?"].value_counts()
    fig23 = go.Figure(go.Pie(labels=q23.index, values=q23.values,
                              marker_colors=["#185FA5","#1D9E75","#EF9F27","#534AB7","#D85A30"],
                              hole=.45, textfont=dict(size=12)))
    fig23.update_layout(**PLOTLY_LAYOUT, height=300)
    st.plotly_chart(fig23, use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 6 · OPEN-ENDED FEEDBACK
# ═════════════════════════════════════════════════════════════════════════════
elif page == "💬 Open-Ended Feedback":
    st.markdown("<h1 style='color:#cce0f5;font-size:1.8rem;font-weight:800;margin:0 0 1.5rem;'>Open-Ended Feedback</h1>", unsafe_allow_html=True)

    import re
    from collections import Counter

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

    c1, c2 = st.columns(2)
    with c1:
        section("❤", "Q16 — WHAT DID YOU LIKE MOST?")
        liked = top_words(dff["Q16.  What did you like most about this tour?"])
        if liked:
            words_l, counts_l = zip(*liked)
            fig_l = go.Figure(go.Bar(
                x=list(counts_l), y=list(words_l), orientation="h",
                marker=dict(color=list(counts_l), colorscale=[[0,"#185FA5"],[1,"#1D9E75"]], showscale=False),
                text=[str(c) for c in counts_l], textposition="outside",
                textfont=dict(color=TEXT_CLR,size=11),
            ))
            fig_l.update_layout(**PLOTLY_LAYOUT, title="Top Keywords",
                                xaxis=dict(gridcolor=GRID_CLR), yaxis=dict(gridcolor=GRID_CLR), height=460)
            st.plotly_chart(fig_l, use_container_width=True)

        section("💬", "SAMPLE RESPONSES")
        liked_samples = dff["Q16.  What did you like most about this tour?"].dropna().sample(min(5,Nf), random_state=42)
        for txt in liked_samples:
            excerpt = str(txt)[:200]
            st.markdown(f"<div style='background:#0f2035;border-left:3px solid #1D9E75;border-radius:6px;padding:.7rem 1rem;margin-bottom:.5rem;font-size:.88rem;color:#cce0f5;'>\"{excerpt}\"</div>", unsafe_allow_html=True)

    with c2:
        section("🔧", "Q17 — WHAT COULD BE IMPROVED?")
        improve = top_words(dff["Q17.  What could be improved?"])
        if improve:
            words_i, counts_i = zip(*improve)
            fig_i = go.Figure(go.Bar(
                x=list(counts_i), y=list(words_i), orientation="h",
                marker=dict(color=list(counts_i), colorscale=[[0,"#EF9F27"],[1,"#E24B4A"]], showscale=False),
                text=[str(c) for c in counts_i], textposition="outside",
                textfont=dict(color=TEXT_CLR,size=11),
            ))
            fig_i.update_layout(**PLOTLY_LAYOUT, title="Top Keywords",
                                xaxis=dict(gridcolor=GRID_CLR), yaxis=dict(gridcolor=GRID_CLR), height=460)
            st.plotly_chart(fig_i, use_container_width=True)

        section("💬", "SAMPLE RESPONSES")
        improve_samples = dff["Q17.  What could be improved?"].dropna().sample(min(5,Nf), random_state=7)
        for txt in improve_samples:
            excerpt = str(txt)[:200]
            st.markdown(f"<div style='background:#0f2035;border-left:3px solid #EF9F27;border-radius:6px;padding:.7rem 1rem;margin-bottom:.5rem;font-size:.88rem;color:#cce0f5;'>\"{excerpt}\"</div>", unsafe_allow_html=True)

    # Q28 Experiential satisfaction
    section("🌟", "Q28 — EXPERIENTIAL VALUE RATINGS (avg 1–5)")
    q28_cols = [c for c in dff.columns if "Q28." in c]
    q28_map = {"Very satisfied":5,"Satisfied":4,"Neutral":3,"Dissatisfied":2,"Very dissatisfied":1}
    q28_labels = [c.split("[")[1].rstrip("]") for c in q28_cols]
    q28_means  = [dff[c].map(q28_map).mean() for c in q28_cols]
    fig28 = go.Figure(go.Bar(
        x=q28_means, y=q28_labels, orientation="h",
        marker=dict(color=q28_means, colorscale=[[0,"#185FA5"],[1,"#1D9E75"]], cmin=3.5, cmax=5.0, showscale=False),
        text=[f"{v:.3f}" for v in q28_means], textposition="outside",
        textfont=dict(color=TEXT_CLR,size=12),
    ))
    fig28.update_layout(**PLOTLY_LAYOUT, xaxis=dict(range=[4.0,5.2],gridcolor=GRID_CLR),
                         yaxis=dict(gridcolor=GRID_CLR), height=280)
    st.plotly_chart(fig28, use_container_width=True)
