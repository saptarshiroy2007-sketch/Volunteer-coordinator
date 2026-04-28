import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from utils.engine import (
    load_data, rank_needs, match_volunteers_to_need,
    add_need, add_volunteer, assign_volunteer, get_stats,
    SKILL_MAP, compute_urgency_score
)

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VolunteerIQ — Smart Resource Allocation",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
}

/* Dark bg */
.stApp {
    background: #0a0e1a;
    color: #e2e8f0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0f1524;
    border-right: 1px solid #1e2a40;
}

/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, #111827 0%, #1a2235 100%);
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    margin-bottom: 10px;
}
.metric-value {
    font-size: 2.5rem;
    font-weight: 700;
    color: #38bdf8;
    font-family: 'JetBrains Mono', monospace;
}
.metric-label {
    font-size: 0.8rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-top: 4px;
}

/* Need cards */
.need-card {
    background: #111827;
    border-left: 4px solid #ef4444;
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 12px;
}
.need-card.high { border-left-color: #f97316; }
.need-card.medium { border-left-color: #eab308; }
.need-card.low { border-left-color: #22c55e; }

.need-title { font-size: 1rem; font-weight: 600; color: #f1f5f9; }
.need-meta { font-size: 0.78rem; color: #64748b; margin-top: 4px; }
.score-badge {
    display: inline-block;
    background: #1e293b;
    border-radius: 20px;
    padding: 2px 12px;
    font-size: 0.8rem;
    font-family: 'JetBrains Mono', monospace;
    color: #38bdf8;
    float: right;
}

/* Vol cards */
.vol-card {
    background: #111827;
    border: 1px solid #1e2a40;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 8px;
}
.vol-name { font-weight: 600; color: #f1f5f9; }
.vol-meta { font-size: 0.78rem; color: #64748b; }
.skill-tag {
    display: inline-block;
    background: #0c1a2e;
    border: 1px solid #1e3a5f;
    border-radius: 4px;
    padding: 1px 8px;
    font-size: 0.7rem;
    color: #38bdf8;
    margin: 2px;
}

/* Section headers */
.section-header {
    font-size: 1.4rem;
    font-weight: 700;
    color: #f1f5f9;
    border-bottom: 2px solid #1e3a5f;
    padding-bottom: 8px;
    margin-bottom: 20px;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #0ea5e9, #6366f1);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    font-family: 'Space Grotesk', sans-serif;
}

/* Inputs */
.stSelectbox, .stTextInput, .stNumberInput, .stSlider {
    color: #e2e8f0;
}

/* Tab styling */
.stTabs [data-baseweb="tab"] {
    color: #64748b;
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    color: #38bdf8 !important;
    border-bottom-color: #38bdf8 !important;
}

/* Status pills */
.status-open { color: #ef4444; font-weight: 600; }
.status-inprogress { color: #f97316; font-weight: 600; }
.status-resolved { color: #22c55e; font-weight: 600; }
.status-available { color: #22c55e; font-weight: 600; }
.status-busy { color: #f97316; font-weight: 600; }
</style>
""", unsafe_allow_html=True)


# ─── Sidebar ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎯 VolunteerIQ")
    st.markdown("<p style='color:#64748b;font-size:0.8rem'>Smart Resource Allocation for Social Impact</p>", unsafe_allow_html=True)
    st.divider()
    
    page = st.radio(
        "Navigate",
        ["📊 Dashboard", "🔴 Needs Map", "🤝 Volunteer Match", "➕ Add Data", "👥 Volunteers"],
        label_visibility="collapsed"
    )
    
    st.divider()
    st.markdown("<p style='color:#64748b;font-size:0.75rem'>Data last synced from field reports, surveys & NGO partners</p>", unsafe_allow_html=True)


needs, volunteers = load_data()
stats = get_stats(needs, volunteers)
ranked_needs = rank_needs(needs)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
if page == "📊 Dashboard":
    st.markdown("<h1 style='color:#f1f5f9;margin-bottom:4px'>Community Needs Intelligence</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b'>Real-time urgency scoring across all active field reports</p>", unsafe_allow_html=True)
    st.divider()

    # KPI Row
    col1, col2, col3, col4, col5 = st.columns(5)
    kpis = [
        (stats["active_needs"], "Active Needs"),
        (stats["total_volunteers"], "Total Volunteers"),
        (stats["available_volunteers"], "Available Now"),
        (stats["resolved_needs"], "Resolved"),
        (len([n for n in ranked_needs if n.get("urgency_score", 0) >= 75]), "Critical Alerts"),
    ]
    for col, (val, label) in zip([col1, col2, col3, col4, col5], kpis):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{val}</div>
                <div class="metric-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        st.markdown("<div class='section-header'>📈 Category Breakdown</div>", unsafe_allow_html=True)
        cat_df = pd.DataFrame(
            list(stats["category_breakdown"].items()),
            columns=["Category", "Count"]
        ).sort_values("Count", ascending=True)

        fig = px.bar(
            cat_df, x="Count", y="Category", orientation="h",
            color="Count", color_continuous_scale=["#1e3a5f", "#0ea5e9", "#6366f1"],
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#94a3b8",
            coloraxis_showscale=False,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis=dict(gridcolor="#1e2a40"),
            yaxis=dict(gridcolor="rgba(0,0,0,0)"),
        )
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown("<div class='section-header'>🌍 Area Urgency Scores</div>", unsafe_allow_html=True)
        area_df = pd.DataFrame(
            list(stats["area_urgency"].items()),
            columns=["Area", "Urgency"]
        ).sort_values("Urgency", ascending=False)

        fig2 = px.bar(
            area_df, x="Area", y="Urgency",
            color="Urgency", color_continuous_scale=["#22c55e", "#eab308", "#ef4444"],
        )
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#94a3b8",
            coloraxis_showscale=False,
            margin=dict(l=0, r=0, t=20, b=0),
            xaxis=dict(gridcolor="rgba(0,0,0,0)", tickangle=-30),
            yaxis=dict(gridcolor="#1e2a40"),
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Top 5 Critical Needs
    st.markdown("<div class='section-header'>🔴 Top Critical Needs</div>", unsafe_allow_html=True)
    for need in ranked_needs[:5]:
        score = need.get("urgency_score", 0)
        card_class = "need-card" if score >= 75 else ("need-card high" if score >= 50 else "need-card medium")
        st.markdown(f"""
        <div class="{card_class}">
            <span class="score-badge">{score} / 100</span>
            <div class="need-title">{need['description']}</div>
            <div class="need-meta">
                📍 {need['area']} &nbsp;|&nbsp; 🏷️ {need['category']} &nbsp;|&nbsp; 
                👥 {need['volunteers_needed'] - need['volunteers_assigned']} volunteers needed &nbsp;|&nbsp; 
                {need.get('urgency_label', '')}
            </div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: NEEDS MAP
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🔴 Needs Map":
    st.markdown("<h1 style='color:#f1f5f9'>Active Community Needs</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b'>All open needs ranked by urgency score</p>", unsafe_allow_html=True)
    st.divider()

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        filter_cat = st.selectbox("Filter by Category", ["All"] + list(SKILL_MAP.keys()))
    with col_f2:
        filter_area = st.selectbox("Filter by Area", ["All"] + list(set(n["area"] for n in needs)))
    with col_f3:
        filter_status = st.selectbox("Filter by Status", ["All", "Open", "In Progress"])

    filtered = ranked_needs
    if filter_cat != "All":
        filtered = [n for n in filtered if n["category"] == filter_cat]
    if filter_area != "All":
        filtered = [n for n in filtered if n["area"] == filter_area]
    if filter_status != "All":
        filtered = [n for n in filtered if n["status"] == filter_status]

    st.markdown(f"<p style='color:#64748b'>{len(filtered)} needs found</p>", unsafe_allow_html=True)

    for need in filtered:
        score = need.get("urgency_score", 0)
        with st.expander(f"{need.get('urgency_label','🟢')} [{need['id']}] {need['description']} — {need['area']}"):
            c1, c2, c3 = st.columns(3)
            c1.metric("Urgency Score", f"{score}/100")
            c2.metric("Severity", f"{need['severity']}/10")
            c3.metric("Mentions", need["mentions"])
            c1.metric("Volunteers Needed", need["volunteers_needed"])
            c2.metric("Assigned", need["volunteers_assigned"])
            c3.metric("Source", need["source"])
            st.markdown(f"**Status:** {need['status']} | **Reported:** {need['date_reported']}")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: VOLUNTEER MATCH
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🤝 Volunteer Match":
    st.markdown("<h1 style='color:#f1f5f9'>Smart Volunteer Matching</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b'>AI-powered matching based on skills, location & availability</p>", unsafe_allow_html=True)
    st.divider()

    need_options = {f"[{n['id']}] {n['description']} ({n['area']})": n for n in ranked_needs if n["status"] != "Resolved"}
    selected_label = st.selectbox("Select a Need to Match", list(need_options.keys()))
    selected_need = need_options[selected_label]

    st.markdown(f"""
    <div class="need-card">
        <div class="need-title">{selected_need['description']}</div>
        <div class="need-meta">
            📍 {selected_need['area']} &nbsp;|&nbsp; 🏷️ {selected_need['category']} &nbsp;|&nbsp;
            Urgency: {selected_need.get('urgency_score', 0)}/100 &nbsp;|&nbsp;
            Needs {selected_need['volunteers_needed'] - selected_need['volunteers_assigned']} more volunteer(s)
        </div>
    </div>
    """, unsafe_allow_html=True)

    matched = match_volunteers_to_need(selected_need, volunteers)

    if not matched:
        st.warning("No available volunteers right now. Check back soon!")
    else:
        st.markdown(f"<div class='section-header'>Top {len(matched)} Matches</div>", unsafe_allow_html=True)
        for vol, match_score in matched:
            skills_html = " ".join([f"<span class='skill-tag'>{s}</span>" for s in vol["skills"]])
            area_match = "✅ Same area" if vol["area"] == selected_need["area"] else f"📍 {vol['area']}"
            st.markdown(f"""
            <div class="vol-card">
                <div class="vol-name">{vol['name']} &nbsp; <span style='font-size:0.75rem;color:#64748b;font-family:JetBrains Mono'>Match: {match_score:.0f}pts</span></div>
                <div class="vol-meta">{area_match} &nbsp;|&nbsp; ⭐ {vol['rating']} &nbsp;|&nbsp; {vol['experience_years']}y exp &nbsp;|&nbsp; ✅ {vol['tasks_completed']} tasks</div>
                <div style='margin-top:6px'>{skills_html}</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"Assign {vol['name']} → {selected_need['id']}", key=f"assign_{vol['id']}_{selected_need['id']}"):
                success, msg = assign_volunteer(selected_need["id"], vol["id"])
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: ADD DATA
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "➕ Add Data":
    st.markdown("<h1 style='color:#f1f5f9'>Add New Data</h1>", unsafe_allow_html=True)
    st.divider()

    tab1, tab2 = st.tabs(["📋 Report a Community Need", "🙋 Register a Volunteer"])

    with tab1:
        st.markdown("#### Report a Community Need")
        col1, col2 = st.columns(2)
        with col1:
            desc = st.text_input("Description of Need")
            category = st.selectbox("Category", list(SKILL_MAP.keys()))
            area = st.selectbox("Area", ["Salt Lake", "Park Street", "Jadavpur", "Howrah", "Barasat", "Dum Dum", "Behala", "Tollygunge"])
        with col2:
            severity = st.slider("Severity (1–10)", 1, 10, 5)
            mentions = st.number_input("No. of times reported / mentions", 1, 100, 1)
            vols_needed = st.number_input("Volunteers Needed", 1, 50, 5)
            source = st.selectbox("Data Source", ["Paper Survey", "Field Report", "WhatsApp Group", "Direct Call", "NGO Partner", "Manual Entry"])

        if st.button("Submit Need", use_container_width=True):
            if desc:
                new_need = add_need(desc, category, area, severity, int(mentions), int(vols_needed), source)
                st.success(f"✅ Need {new_need['id']} added successfully!")
            else:
                st.error("Description can't be empty bro")

    with tab2:
        st.markdown("#### Register a Volunteer")
        col1, col2 = st.columns(2)
        SKILLS_LIST = ["Medical", "Teaching", "Logistics", "Counseling", "IT", "Cooking", "Construction", "Legal", "Photography", "Driving"]
        with col1:
            name = st.text_input("Full Name")
            skills = st.multiselect("Skills", SKILLS_LIST)
            area = st.selectbox("Area", ["Salt Lake", "Park Street", "Jadavpur", "Howrah", "Barasat", "Dum Dum", "Behala", "Tollygunge"], key="vol_area")
        with col2:
            availability = st.selectbox("Availability", ["Weekdays", "Weekends", "Both", "Flexible"])
            experience = st.slider("Years of Experience", 0, 20, 0)
            contact = st.text_input("Contact Number")

        if st.button("Register Volunteer", use_container_width=True):
            if name and skills and contact:
                new_vol = add_volunteer(name, skills, area, availability, experience, contact)
                st.success(f"✅ {new_vol['name']} registered as {new_vol['id']}!")
            else:
                st.error("Fill in all fields!")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: VOLUNTEERS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "👥 Volunteers":
    st.markdown("<h1 style='color:#f1f5f9'>Volunteer Directory</h1>", unsafe_allow_html=True)
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        filter_skill = st.selectbox("Filter by Skill", ["All"] + ["Medical", "Teaching", "Logistics", "Counseling", "IT", "Cooking", "Construction", "Legal", "Photography", "Driving"])
    with col2:
        filter_vstatus = st.selectbox("Filter by Status", ["All", "Available", "Busy", "On Leave"])

    filtered_vols = volunteers
    if filter_skill != "All":
        filtered_vols = [v for v in filtered_vols if filter_skill in v["skills"]]
    if filter_vstatus != "All":
        filtered_vols = [v for v in filtered_vols if v["status"] == filter_vstatus]

    filtered_vols = sorted(filtered_vols, key=lambda v: v["rating"], reverse=True)
    st.markdown(f"<p style='color:#64748b'>{len(filtered_vols)} volunteers found</p>", unsafe_allow_html=True)

    for vol in filtered_vols:
        skills_html = " ".join([f"<span class='skill-tag'>{s}</span>" for s in vol["skills"]])
        status_color = "#22c55e" if vol["status"] == "Available" else ("#f97316" if vol["status"] == "Busy" else "#64748b")
        st.markdown(f"""
        <div class="vol-card">
            <div class="vol-name">
                {vol['name']} 
                <span style='font-size:0.75rem;color:{status_color};margin-left:8px'>● {vol['status']}</span>
                <span style='float:right;font-size:0.75rem;color:#64748b;font-family:JetBrains Mono'>{vol['id']}</span>
            </div>
            <div class="vol-meta">📍 {vol['area']} &nbsp;|&nbsp; ⭐ {vol['rating']} &nbsp;|&nbsp; {vol['experience_years']}y exp &nbsp;|&nbsp; ✅ {vol['tasks_completed']} tasks &nbsp;|&nbsp; 🕐 {vol['availability']}</div>
            <div style='margin-top:6px'>{skills_html}</div>
        </div>
        """, unsafe_allow_html=True)
