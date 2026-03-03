"""
Abrigo Fraud Intelligence Middleware Dashboard
Production-ready Streamlit dashboard with mock data, pipeline visualization,
transaction table, charts, and live scan capability.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random
import time
import json

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Abrigo Fraud Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# GLOBAL STYLE INJECTION
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── Base ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', system-ui, sans-serif;
}

/* ── Hide default Streamlit chrome ── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ── Main background ── */
.stApp { background-color: #0f172a; }
.block-container { padding: 1rem 2rem 2rem 2rem !important; max-width: 100% !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0c1628 0%, #1a2744 100%);
    border-right: 1px solid #1e3a5f;
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.2rem !important;
    width: 100% !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.01em;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: linear-gradient(135deg, #16a34a 0%, #15803d 100%) !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(34,197,94,0.35) !important;
}

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 0.75rem 1rem !important;
}
[data-testid="stMetricLabel"] { color: #94a3b8 !important; font-size: 0.75rem !important; font-weight: 500; text-transform: uppercase; letter-spacing: 0.06em; }
[data-testid="stMetricValue"] { color: #f1f5f9 !important; font-size: 1.6rem !important; font-weight: 700 !important; }
[data-testid="stMetricDelta"] { font-size: 0.78rem !important; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] { border: 1px solid #334155 !important; border-radius: 10px !important; overflow: hidden; }

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #1e293b;
    border: 1px solid #334155 !important;
    border-radius: 10px !important;
}
[data-testid="stExpander"] summary { color: #94a3b8 !important; font-weight: 600 !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { background: #1e293b; border-radius: 8px; gap: 4px; }
.stTabs [data-baseweb="tab"] { color: #94a3b8; border-radius: 6px; }
.stTabs [data-baseweb="tab"][aria-selected="true"] { background: #0f172a; color: #22c55e; }

/* ── Inputs ── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] select,
[data-baseweb="select"] { 
    background-color: #0f172a !important; 
    color: #f1f5f9 !important;
    border-color: #334155 !important;
}

/* ── Badge styles ── */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.badge-go { background: rgba(34,197,94,0.15); color: #4ade80; border: 1px solid rgba(34,197,94,0.3); }
.badge-hold { background: rgba(234,179,8,0.15); color: #fde047; border: 1px solid rgba(234,179,8,0.3); }
.badge-block { background: rgba(239,68,68,0.15); color: #f87171; border: 1px solid rgba(239,68,68,0.3); }
.badge-low { background: rgba(34,197,94,0.12); color: #4ade80; border: 1px solid rgba(34,197,94,0.25); }
.badge-medium { background: rgba(234,179,8,0.12); color: #fde047; border: 1px solid rgba(234,179,8,0.25); }
.badge-high { background: rgba(249,115,22,0.12); color: #fb923c; border: 1px solid rgba(249,115,22,0.25); }
.badge-critical { background: rgba(239,68,68,0.12); color: #f87171; border: 1px solid rgba(239,68,68,0.25); }

/* ── Pipeline card ── */
.pipeline-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 0.85rem 1rem;
    position: relative;
    transition: all 0.2s ease;
}
.pipeline-card:hover { border-color: #22c55e; box-shadow: 0 0 0 1px rgba(34,197,94,0.2); }
.pipeline-stage { font-size: 0.68rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: #64748b; margin-bottom: 2px; }
.pipeline-label { font-size: 0.85rem; font-weight: 700; color: #e2e8f0; margin-bottom: 0.5rem; line-height: 1.2; }
.pipeline-metric { font-size: 1.1rem; font-weight: 700; color: #f1f5f9; }
.pipeline-sub { font-size: 0.72rem; color: #94a3b8; margin-top: 1px; }
.pipeline-bar-bg { background: #0f172a; border-radius: 4px; height: 5px; margin-top: 0.6rem; overflow: hidden; }
.pipeline-bar-fill { height: 100%; border-radius: 4px; transition: width 1s ease; }

/* ── KPI row ── */
.kpi-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 0.85rem 1rem;
    text-align: center;
    transition: border-color 0.2s;
}
.kpi-card:hover { border-color: #475569; }
.kpi-label { font-size: 0.68rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 4px; }
.kpi-value { font-size: 1.6rem; font-weight: 800; color: #f1f5f9; line-height: 1; margin-bottom: 4px; }
.kpi-delta-pos { font-size: 0.72rem; color: #4ade80; font-weight: 600; }
.kpi-delta-neg { font-size: 0.72rem; color: #f87171; font-weight: 600; }

/* ── Section headers ── */
.section-header {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #475569;
    margin-bottom: 0.5rem;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid #1e293b;
}

/* ── Detail panel ── */
.detail-panel {
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 0.85rem;
}
.detail-panel h4 {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #64748b;
    margin: 0 0 0.5rem 0;
}
.detail-row {
    display: flex;
    justify-content: space-between;
    padding: 3px 0;
    font-size: 0.8rem;
    border-bottom: 1px solid #1e293b;
}
.detail-row:last-child { border-bottom: none; }
.detail-key { color: #94a3b8; }
.detail-val { color: #e2e8f0; font-weight: 500; text-align: right; }

/* ── Scan result card ── */
.scan-score-card {
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    margin-bottom: 1rem;
}
.scan-score-label { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; opacity: 0.7; margin-bottom: 8px; }
.scan-score-value { font-size: 3rem; font-weight: 900; line-height: 1; }
.scan-score-decision { font-size: 1rem; font-weight: 700; margin-top: 6px; }

/* ── Progress stage ── */
.stage-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 6px 0;
    font-size: 0.82rem;
}
.stage-dot {
    width: 10px; height: 10px;
    border-radius: 50%;
    flex-shrink: 0;
}
.stage-dot-pending { background: #334155; }
.stage-dot-running { background: #eab308; animation: pulse 1s infinite; }
.stage-dot-done { background: #22c55e; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }

/* ── Add to dashboard button ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%) !important;
    border: none !important;
    color: #fff !important;
    font-weight: 700 !important;
}

/* ── Select row hint ── */
.select-hint {
    font-size: 0.75rem;
    color: #475569;
    font-style: italic;
    margin-top: 4px;
}

/* ── Logo area ── */
.sidebar-logo {
    padding: 1rem 0 0.5rem 0;
    border-bottom: 1px solid #1e3a5f;
    margin-bottom: 1rem;
}
.sidebar-logo-title {
    font-size: 1.1rem;
    font-weight: 800;
    color: #f1f5f9 !important;
    letter-spacing: -0.01em;
}
.sidebar-logo-sub {
    font-size: 0.7rem;
    color: #64748b !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 2px;
}

/* ── Divider ── */
.custom-divider { border: none; border-top: 1px solid #1e293b; margin: 1rem 0; }

/* ── Page title ── */
.page-title {
    font-size: 1.4rem;
    font-weight: 800;
    color: #f1f5f9;
    letter-spacing: -0.02em;
}
.page-subtitle {
    font-size: 0.78rem;
    color: #64748b;
    margin-top: 2px;
}
.live-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(34,197,94,0.1);
    border: 1px solid rgba(34,197,94,0.25);
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.7rem;
    font-weight: 700;
    color: #4ade80;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    vertical-align: middle;
    margin-left: 10px;
}
.live-dot {
    width: 6px; height: 6px;
    background: #22c55e;
    border-radius: 50%;
    animation: pulse 2s infinite;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# CONSTANTS & HELPERS
# ─────────────────────────────────────────────
FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Barbara", "David", "Elizabeth", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Lisa", "Daniel", "Nancy",
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
    "Steven", "Dorothy", "Paul", "Kimberly", "Andrew", "Emily", "Kenneth", "Donna",
    "Wei", "Priya", "Omar", "Sofia", "Aiden", "Fatima", "Hiroshi", "Amara",
]
LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen",
    "Hill", "Flores", "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera",
    "Campbell", "Mitchell", "Carter", "Roberts", "Patel", "Kim", "Chen", "Zhang",
]
IP_COUNTRIES = [
    ("US", "New York"), ("US", "Los Angeles"), ("US", "Chicago"), ("US", "Houston"),
    ("US", "Miami"), ("GB", "London"), ("DE", "Berlin"), ("FR", "Paris"),
    ("CA", "Toronto"), ("AU", "Sydney"), ("RU", "Moscow"), ("CN", "Shanghai"),
    ("BR", "São Paulo"), ("IN", "Mumbai"), ("NG", "Lagos"), ("UA", "Kyiv"),
    ("VN", "Hanoi"), ("MX", "Mexico City"), ("JP", "Tokyo"), ("KR", "Seoul"),
]
IP_TYPES = ["Residential", "Corporate", "VPN", "Proxy", "Tor", "Datacenter", "Mobile"]
IP_TYPE_WEIGHTS = [0.45, 0.25, 0.12, 0.08, 0.04, 0.04, 0.02]
BREACH_SOURCES = [
    "LinkedIn 2021", "Equifax 2017", "Yahoo 2016", "Adobe 2013",
    "Marriott 2018", "Capital One 2019", "Experian 2015", "T-Mobile 2021",
    "Facebook 2021", "Twitter 2022", "LastPass 2022", "Uber 2022",
]
OFAC_NAMES = [
    "Gazprombank OJSC", "Rosneft Oil Company", "Islamic Revolutionary Guard",
    "Al-Nusra Front", "Hezbollah", "Cali Cartel", "Sinaloa Federation",
]
TRANSACTION_TYPES = ["ACH", "Wire", "Check"]
DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "icloud.com", "hotmail.com", "protonmail.com"]


def random_account():
    prefix = random.randint(1000, 9999)
    suffix = random.randint(100000, 999999)
    return f"{prefix}-{suffix}"


def random_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def random_email(name):
    parts = name.lower().split()
    patterns = [
        f"{parts[0]}.{parts[1]}",
        f"{parts[0]}{parts[1]}",
        f"{parts[0][0]}{parts[1]}",
        f"{parts[0]}{random.randint(10,99)}",
    ]
    return f"{random.choice(patterns)}@{random.choice(DOMAINS)}"


def random_ip():
    return f"{random.randint(1,254)}.{random.randint(0,254)}.{random.randint(0,254)}.{random.randint(1,254)}"


def risk_tier(score):
    if score < 30:
        return "Low"
    elif score < 55:
        return "Medium"
    elif score < 75:
        return "High"
    else:
        return "Critical"


def decision_for_score(score):
    if score >= 80:
        return "BLOCK"
    elif score >= 50:
        return "HOLD" if random.random() < 0.60 else "GO"
    else:
        return "GO"


def random_amount(tx_type):
    if tx_type == "Wire":
        return round(random.uniform(5000, 250000), 2)
    elif tx_type == "ACH":
        return round(random.uniform(100, 50000), 2)
    else:  # Check
        return round(random.uniform(50, 25000), 2)


def random_risk_score():
    """Weighted risk score distribution per spec."""
    r = random.random()
    if r < 0.45:
        return random.randint(5, 29)
    elif r < 0.72:
        return random.randint(30, 54)
    elif r < 0.88:
        return random.randint(55, 74)
    else:
        return random.randint(75, 95)


def generate_ip_detail():
    country, city = random.choice(IP_COUNTRIES)
    ip_type = random.choices(IP_TYPES, weights=IP_TYPE_WEIGHTS)[0]
    is_vpn_or_worse = ip_type in ("VPN", "Proxy", "Tor")
    abuse = random.randint(70, 99) if is_vpn_or_worse else random.randint(0, 30)
    return {
        "ip": random_ip(),
        "country": country,
        "city": city,
        "type": ip_type,
        "abuse_score": abuse,
        "vpn": ip_type in ("VPN", "Proxy", "Tor"),
        "isp": random.choice(["Comcast", "AT&T", "Verizon", "Deutsche Telekom", "BT Group",
                               "Cloudflare", "Digital Ocean", "AWS", "Azure", "SoftLayer"]),
    }


def generate_ofac_detail(account_holder):
    hit = random.random() < 0.12
    if hit:
        matched_name = random.choice(OFAC_NAMES)
        confidence = round(random.uniform(0.65, 0.97), 2)
        return {"hit": True, "matched_name": matched_name, "confidence": confidence, "list": "SDN", "date_added": "2023-01-15"}
    return {"hit": False, "matched_name": None, "confidence": 0, "list": None, "date_added": None}


def generate_breach_detail(email):
    hit = random.random() < 0.18
    if hit:
        count = random.randint(1, 3)
        sources = random.sample(BREACH_SOURCES, min(count, len(BREACH_SOURCES)))
        return {"hit": True, "sources": sources, "exposed_fields": random.sample(["email", "password", "phone", "SSN", "address", "DOB"], random.randint(2, 4))}
    return {"hit": False, "sources": [], "exposed_fields": []}


def generate_account_risk(score):
    return {
        "velocity_24h": random.randint(1, 12),
        "velocity_7d": random.randint(1, 45),
        "account_age_days": random.randint(30, 3650),
        "prior_flags": random.randint(0, 5),
        "pattern_score": score + random.randint(-10, 10),
        "behavior_anomaly": score > 60,
    }


def make_transaction(i, seed=None):
    if seed is not None:
        random.seed(seed + i)
    tx_type = random.choice(TRANSACTION_TYPES)
    direction = random.choice(["Credit", "Debit"])
    name = random_name()
    score = random_risk_score()
    decision = decision_for_score(score)
    now = datetime.now()
    tx_time = now - timedelta(minutes=random.randint(1, 1440))
    return {
        "time": tx_time.strftime("%H:%M:%S"),
        "timestamp": tx_time,
        "account": random_account(),
        "holder": name,
        "email": random_email(name),
        "amount": random_amount(tx_type),
        "type": tx_type,
        "direction": direction,
        "risk_score": score,
        "tier": risk_tier(score),
        "decision": decision,
        "status": "Processed" if decision == "GO" else ("Flagged" if decision == "HOLD" else "Blocked"),
        "ip_detail": generate_ip_detail(),
        "ofac": generate_ofac_detail(name),
        "breach": generate_breach_detail(random_email(name)),
        "account_risk": generate_account_risk(score),
        "counterparty": random_name(),
    }


@st.cache_data
def generate_initial_transactions():
    """Generate 15 initial mock transactions. Cached for performance."""
    return [make_transaction(i, seed=42) for i in range(15)]


@st.cache_data
def generate_trend_data():
    """Generate 24h risk score trend data."""
    now = datetime.now()
    hours = [now - timedelta(hours=23 - i) for i in range(24)]
    scores = []
    base = 35
    for h in hours:
        base += random.gauss(0, 5)
        base = max(10, min(85, base))
        scores.append(round(base, 1))
    return hours, scores


@st.cache_data
def generate_pipeline_metrics():
    """Generate pipeline stage metrics."""
    total = 2847
    stages = [
        ("01", "Transaction Ingestion", total, 0, "#22c55e"),
        ("02", "Account Risk", total, 312, "#eab308"),
        ("03", "IP Intelligence", total - 10, 189, "#f97316"),
        ("04", "OFAC Screen", total - 12, 23, "#ef4444"),
        ("05", "Breach Check", total - 15, 47, "#8b5cf6"),
        ("06", "Abrigo Decision", total - 15, 88, "#22c55e"),
    ]
    return stages


# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────
if "transactions" not in st.session_state:
    st.session_state.transactions = generate_initial_transactions()
if "scan_result" not in st.session_state:
    st.session_state.scan_result = None
if "scan_running" not in st.session_state:
    st.session_state.scan_running = False
if "selected_row" not in st.session_state:
    st.session_state.selected_row = None
if "show_scan_result" not in st.session_state:
    st.session_state.show_scan_result = False


# ─────────────────────────────────────────────
# HELPER: COLOR BY TIER/DECISION
# ─────────────────────────────────────────────
TIER_COLORS = {
    "Low": "#22c55e",
    "Medium": "#eab308",
    "High": "#f97316",
    "Critical": "#ef4444",
}
DECISION_COLORS = {
    "GO": "#22c55e",
    "HOLD": "#eab308",
    "BLOCK": "#ef4444",
}


def score_color(score):
    tier = risk_tier(score)
    return TIER_COLORS[tier]


def decision_badge(decision):
    cls = f"badge badge-{decision.lower()}"
    return f'<span class="{cls}">{decision}</span>'


def tier_badge(tier):
    cls = f"badge badge-{tier.lower()}"
    return f'<span class="{cls}">{tier}</span>'


# ─────────────────────────────────────────────
# SIDEBAR: LOGO + NEW SCAN FORM
# ─────────────────────────────────────────────
with st.sidebar:
    # Logo
    st.markdown("""
    <div class="sidebar-logo">
        <div style="display:flex;align-items:center;gap:10px;">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect width="32" height="32" rx="8" fill="#22c55e" fill-opacity="0.15"/>
                <path d="M16 4L6 9V16C6 21.5 10.5 26.6 16 28C21.5 26.6 26 21.5 26 16V9L16 4Z" 
                      stroke="#22c55e" stroke-width="1.5" stroke-linejoin="round"/>
                <path d="M11 16L14.5 19.5L21 13" stroke="#22c55e" stroke-width="1.8" 
                      stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <div>
                <div class="sidebar-logo-title">Abrigo</div>
                <div class="sidebar-logo-sub">Fraud Intelligence</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── NEW SCAN FORM ──
    st.markdown('<div class="section-header" style="margin-top:0.5rem;">🔍 New Fraud Scan</div>', unsafe_allow_html=True)

    with st.form("scan_form", clear_on_submit=False):
        acct_num = st.text_input("Account Number *", placeholder="e.g. 4821-384729")
        acct_holder = st.text_input("Account Holder Name *", placeholder="e.g. John Smith")
        acct_email = st.text_input("Holder Email", placeholder="john@example.com")
        tx_amount = st.number_input("Transaction Amount ($) *", min_value=0.01, value=1000.00, step=100.0, format="%.2f")
        tx_type = st.selectbox("Transaction Type", ["ACH", "Wire", "Check"])
        tx_dir = st.selectbox("Direction", ["Credit", "Debit"])
        counterparty = st.text_input("Counterparty Name", placeholder="e.g. Acme Corp")
        source_ip = st.text_input("Source IP Address", placeholder="e.g. 192.168.1.100")

        st.markdown("<div style='margin-top:4px;'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("🛡️ Run Fraud Intelligence Scan", use_container_width=True)

    # ── SCAN ANIMATION & RESULTS ──
    if submitted:
        if not acct_num.strip() or not acct_holder.strip() or tx_amount <= 0:
            st.error("Please fill in all required fields.")
        else:
            st.session_state.show_scan_result = False
            st.session_state.scan_result = None

            st.markdown('<div class="section-header" style="margin-top:1rem;">⚡ Scan Progress</div>', unsafe_allow_html=True)

            stages_info = [
                ("Account Risk Assessment", "Analyzing velocity, history & patterns"),
                ("IP Intelligence", "Geolocating & scoring source address"),
                ("IP Intelligence", "Checking proxy, VPN & Tor networks"),
                ("OFAC / Sanctions Screen", "Checking SDN & sanctions lists"),
                ("Dark Web Breach Check", "Scanning known breach databases"),
                ("Composite Scoring", "Generating final risk assessment"),
            ]

            stage_containers = []
            for label, sub in stages_info:
                c = st.empty()
                stage_containers.append(c)
                c.markdown(
                    f'<div class="stage-item">'
                    f'<div class="stage-dot stage-dot-pending"></div>'
                    f'<div>'
                    f'<div style="color:#475569;font-size:0.78rem;font-weight:600;">{label}</div>'
                    f'<div style="color:#334155;font-size:0.68rem;">{sub}</div>'
                    f'</div>'
                    f'<div style="margin-left:auto;font-size:0.68rem;color:#334155;">Queued</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            # Animate each stage
            for idx, (label, sub) in enumerate(stages_info):
                # Show running
                stage_containers[idx].markdown(
                    f'<div class="stage-item">'
                    f'<div class="stage-dot stage-dot-running"></div>'
                    f'<div>'
                    f'<div style="color:#fde047;font-size:0.78rem;font-weight:600;">{label}</div>'
                    f'<div style="color:#64748b;font-size:0.68rem;">{sub}</div>'
                    f'</div>'
                    f'<div style="margin-left:auto;font-size:0.68rem;color:#eab308;font-weight:600;">Running...</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                time.sleep(0.65)
                # Show done
                stage_containers[idx].markdown(
                    f'<div class="stage-item">'
                    f'<div class="stage-dot stage-dot-done"></div>'
                    f'<div>'
                    f'<div style="color:#4ade80;font-size:0.78rem;font-weight:600;">{label}</div>'
                    f'<div style="color:#64748b;font-size:0.68rem;">{sub}</div>'
                    f'</div>'
                    f'<div style="margin-left:auto;font-size:0.68rem;color:#22c55e;font-weight:600;">✓ Done</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            # Generate scan result
            score = random_risk_score()
            decision = decision_for_score(score)
            ip_used = source_ip.strip() if source_ip.strip() else random_ip()
            ip_det = generate_ip_detail()
            ip_det["ip"] = ip_used
            name_for_ofac = acct_holder.strip()
            email_for_breach = acct_email.strip() if acct_email.strip() else random_email(name_for_ofac)
            ofac_det = generate_ofac_detail(name_for_ofac)
            breach_det = generate_breach_detail(email_for_breach)
            acct_risk = generate_account_risk(score)

            result = {
                "account": acct_num.strip(),
                "holder": name_for_ofac,
                "email": email_for_breach,
                "amount": tx_amount,
                "type": tx_type,
                "direction": tx_dir,
                "counterparty": counterparty.strip() or random_name(),
                "risk_score": score,
                "tier": risk_tier(score),
                "decision": decision,
                "status": "Processed" if decision == "GO" else ("Flagged" if decision == "HOLD" else "Blocked"),
                "time": datetime.now().strftime("%H:%M:%S"),
                "timestamp": datetime.now(),
                "ip_detail": ip_det,
                "ofac": ofac_det,
                "breach": breach_det,
                "account_risk": acct_risk,
            }
            st.session_state.scan_result = result
            st.session_state.show_scan_result = True
            st.rerun()

    # Show scan results in sidebar
    if st.session_state.show_scan_result and st.session_state.scan_result:
        r = st.session_state.scan_result
        score = r["risk_score"]
        decision = r["decision"]
        tier = r["tier"]
        col = TIER_COLORS.get(tier, "#22c55e")
        dec_col = DECISION_COLORS.get(decision, "#22c55e")

        st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">📊 Scan Results</div>', unsafe_allow_html=True)

        # Score card
        st.markdown(f"""
        <div class="scan-score-card" style="background:linear-gradient(135deg,{col}18,{col}08);border:1px solid {col}44;">
            <div class="scan-score-label">Composite Risk Score</div>
            <div class="scan-score-value" style="color:{col};">{score}</div>
            <div class="scan-score-decision" style="color:{dec_col};">
                {'🛑' if decision=='BLOCK' else '⚠️' if decision=='HOLD' else '✅'} {decision} — {tier} Risk
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Detail panels
        ip = r["ip_detail"]
        ofac = r["ofac"]
        breach = r["breach"]
        acct = r["account_risk"]

        with st.expander("Account Risk", expanded=False):
            st.markdown(f"""
            <div>
            <div class="detail-row"><span class="detail-key">24h Velocity</span><span class="detail-val">{acct['velocity_24h']} txns</span></div>
            <div class="detail-row"><span class="detail-key">7d Velocity</span><span class="detail-val">{acct['velocity_7d']} txns</span></div>
            <div class="detail-row"><span class="detail-key">Account Age</span><span class="detail-val">{acct['account_age_days']}d</span></div>
            <div class="detail-row"><span class="detail-key">Prior Flags</span><span class="detail-val">{acct['prior_flags']}</span></div>
            <div class="detail-row"><span class="detail-key">Behavior Anomaly</span><span class="detail-val" style="color:{'#f87171' if acct['behavior_anomaly'] else '#4ade80'}">{'YES ⚠' if acct['behavior_anomaly'] else 'No'}</span></div>
            </div>
            """, unsafe_allow_html=True)

        with st.expander("IP Intelligence", expanded=False):
            ip_col = "#f87171" if ip["vpn"] else "#4ade80"
            st.markdown(f"""
            <div>
            <div class="detail-row"><span class="detail-key">Address</span><span class="detail-val">{ip['ip']}</span></div>
            <div class="detail-row"><span class="detail-key">Location</span><span class="detail-val">{ip['city']}, {ip['country']}</span></div>
            <div class="detail-row"><span class="detail-key">Type</span><span class="detail-val" style="color:{ip_col};">{ip['type']}</span></div>
            <div class="detail-row"><span class="detail-key">ISP</span><span class="detail-val">{ip['isp']}</span></div>
            <div class="detail-row"><span class="detail-key">Abuse Score</span><span class="detail-val" style="color:{'#f87171' if ip['abuse_score']>50 else '#4ade80'};">{ip['abuse_score']}/100</span></div>
            </div>
            """, unsafe_allow_html=True)

        with st.expander("OFAC / Sanctions", expanded=False):
            if ofac["hit"]:
                st.markdown(f"""
                <div>
                <div class="detail-row"><span class="detail-key">Status</span><span class="detail-val" style="color:#f87171;">🚨 HIT</span></div>
                <div class="detail-row"><span class="detail-key">Matched Name</span><span class="detail-val">{ofac['matched_name']}</span></div>
                <div class="detail-row"><span class="detail-key">List</span><span class="detail-val">{ofac['list']}</span></div>
                <div class="detail-row"><span class="detail-key">Confidence</span><span class="detail-val">{int(ofac['confidence']*100)}%</span></div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown('<div style="color:#4ade80;font-size:0.82rem;padding:4px 0;">✅ No sanctions matches found</div>', unsafe_allow_html=True)

        with st.expander("Dark Web Breach", expanded=False):
            if breach["hit"]:
                sources_html = "".join(f'<div class="detail-row"><span class="detail-key">Source</span><span class="detail-val">{s}</span></div>' for s in breach["sources"])
                fields_html = ", ".join(breach["exposed_fields"])
                st.markdown(f"""
                <div>
                <div class="detail-row"><span class="detail-key">Status</span><span class="detail-val" style="color:#f97316;">⚠️ BREACHED</span></div>
                {sources_html}
                <div class="detail-row"><span class="detail-key">Exposed Fields</span><span class="detail-val">{fields_html}</span></div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown('<div style="color:#4ade80;font-size:0.82rem;padding:4px 0;">✅ No breach records found</div>', unsafe_allow_html=True)

        # Add to dashboard button
        if st.button("➕ Add to Dashboard", use_container_width=True, key="add_to_dash"):
            r_copy = dict(r)
            st.session_state.transactions.insert(0, r_copy)
            st.session_state.show_scan_result = False
            st.session_state.scan_result = None
            st.success("Transaction added to dashboard!")
            st.rerun()

    # ── Sidebar footer stats ──
    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">System Status</div>', unsafe_allow_html=True)
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown('<div style="font-size:0.7rem;color:#64748b;">API Latency</div><div style="font-size:0.9rem;color:#4ade80;font-weight:700;">142ms</div>', unsafe_allow_html=True)
    with col_s2:
        st.markdown('<div style="font-size:0.7rem;color:#64748b;">Uptime</div><div style="font-size:0.9rem;color:#4ade80;font-weight:700;">99.97%</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.68rem;color:#334155;margin-top:8px;">Last sync: just now · All systems operational</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MAIN CONTENT
# ─────────────────────────────────────────────

# ── Page Header ──
header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    now_str = datetime.now().strftime("%A, %B %d, %Y · %I:%M %p")
    st.markdown(f"""
    <div>
        <div class="page-title">
            Fraud Intelligence Dashboard
            <span class="live-badge"><span class="live-dot"></span>Live</span>
        </div>
        <div class="page-subtitle">{now_str} · Real-time transaction monitoring & risk assessment</div>
    </div>
    """, unsafe_allow_html=True)
with header_col2:
    if st.button("🔄 Refresh Data", key="refresh_main"):
        st.cache_data.clear()
        st.session_state.transactions = generate_initial_transactions()
        st.rerun()

st.markdown("<div style='margin-top:1.2rem;'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SECTION 1: PIPELINE FLOW
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">Pipeline Flow</div>', unsafe_allow_html=True)

pipeline_stages = generate_pipeline_metrics()
pipe_cols = st.columns(6, gap="small")

for i, (num, label, processed, flagged, color) in enumerate(pipeline_stages):
    pct = (flagged / processed * 100) if processed > 0 else 0
    flag_pct_bar = min(100, pct * 2)  # visual exaggeration for bar
    with pipe_cols[i]:
        st.markdown(f"""
        <div class="pipeline-card">
            <div class="pipeline-stage">Stage {num}</div>
            <div class="pipeline-label">{label}</div>
            <div style="display:flex;justify-content:space-between;align-items:baseline;margin-top:2px;">
                <div>
                    <div class="pipeline-metric">{processed:,}</div>
                    <div class="pipeline-sub">processed</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:1rem;font-weight:700;color:{color};">{flagged:,}</div>
                    <div class="pipeline-sub">flagged</div>
                </div>
            </div>
            <div class="pipeline-bar-bg">
                <div class="pipeline-bar-fill" style="width:{flag_pct_bar:.1f}%;background:{color};"></div>
            </div>
            <div style="font-size:0.66rem;color:#475569;margin-top:4px;">{pct:.1f}% flag rate</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='margin-top:1.2rem;'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SECTION 2: KPI CARDS
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">Key Performance Indicators</div>', unsafe_allow_html=True)

kpis = [
    ("Transactions Today", "2,847", "+12.4%", True),
    ("Items Flagged", "436", "+8.2%", False),
    ("OFAC Hits", "23", "+4.5%", False),
    ("High Risk IPs", "89", "+15.3%", False),
    ("Breach Alerts", "47", "+6.8%", False),
    ("Auto-Blocked", "88", "-3.2%", True),
    ("Avg Processing", "142ms", "-8.1%", True),
]

kpi_cols = st.columns(7, gap="small")
for i, (label, value, delta, is_positive) in enumerate(kpis):
    delta_class = "kpi-delta-pos" if is_positive else "kpi-delta-neg"
    with kpi_cols[i]:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="{delta_class}">{delta} vs yday</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='margin-top:1.4rem;'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SECTION 3: TRANSACTION TABLE + CHARTS
# ─────────────────────────────────────────────
table_col, chart_col = st.columns([3, 1], gap="medium")

with table_col:
    st.markdown('<div class="section-header">Recent Transactions</div>', unsafe_allow_html=True)

    txns = st.session_state.transactions

    # Build display dataframe
    display_rows = []
    for t in txns:
        tier = t.get("tier", risk_tier(t["risk_score"]))
        display_rows.append({
            "Time": t["time"],
            "Account": t["account"],
            "Holder": t["holder"],
            "Amount": f"${t['amount']:,.2f}",
            "Type": f"{t['type']} {t['direction']}",
            "Risk Score": t["risk_score"],
            "Tier": tier,
            "Decision": t["decision"],
            "Status": t["status"],
        })

    df_display = pd.DataFrame(display_rows)

    # Color mapping for display
    def highlight_decision(val):
        color_map = {"GO": "#22c55e", "HOLD": "#eab308", "BLOCK": "#ef4444"}
        return f"color: {color_map.get(val, '#f1f5f9')}"

    def highlight_tier(val):
        color_map = {"Low": "#22c55e", "Medium": "#eab308", "High": "#f97316", "Critical": "#ef4444"}
        return f"color: {color_map.get(val, '#f1f5f9')}"

    def highlight_score(val):
        if isinstance(val, (int, float)):
            if val < 30:
                return "color: #22c55e"
            elif val < 55:
                return "color: #eab308"
            elif val < 75:
                return "color: #f97316"
            else:
                return "color: #ef4444"
        return ""

    styled_df = df_display.style.applymap(
        highlight_decision, subset=["Decision"]
    ).applymap(
        highlight_tier, subset=["Tier"]
    ).applymap(
        highlight_score, subset=["Risk Score"]
    ).set_properties(**{
        "background-color": "#1e293b",
        "color": "#e2e8f0",
        "border-color": "#334155",
    })

    # Row selection via selectbox
    row_labels = [f"Row {i+1} — {txns[i]['account']} · ${txns[i]['amount']:,.2f} · {txns[i]['decision']}" for i in range(len(txns))]
    selected_label = st.selectbox(
        "Select a transaction to inspect:",
        ["— None —"] + row_labels,
        key="row_selector",
        label_visibility="collapsed",
    )
    st.markdown('<div class="select-hint">Select a transaction above to view enrichment details</div>', unsafe_allow_html=True)

    # Determine selection
    selected_idx = None
    if selected_label != "— None —":
        try:
            selected_idx = row_labels.index(selected_label)
        except ValueError:
            selected_idx = None

    # Dataframe
    st.dataframe(
        styled_df,
        use_container_width=True,
        height=420,
        hide_index=True,
    )

    # ── Detail Expander ──
    if selected_idx is not None and selected_idx < len(txns):
        t = txns[selected_idx]
        ip = t["ip_detail"]
        ofac = t["ofac"]
        breach = t["breach"]
        acct = t["account_risk"]
        tier = t.get("tier", risk_tier(t["risk_score"]))
        col_val = TIER_COLORS.get(tier, "#94a3b8")
        dec_col = DECISION_COLORS.get(t["decision"], "#94a3b8")

        with st.expander(
            f"🔎 Transaction Detail — {t['account']} · {t['holder']} · ${t['amount']:,.2f} · {t['decision']}",
            expanded=True
        ):
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:1rem;padding-bottom:0.75rem;border-bottom:1px solid #334155;">
                <div style="background:{col_val}18;border:1px solid {col_val}44;border-radius:50%;width:44px;height:44px;display:flex;align-items:center;justify-content:center;font-size:1.3rem;font-weight:900;color:{col_val};">{t['risk_score']}</div>
                <div>
                    <div style="font-size:1rem;font-weight:700;color:#f1f5f9;">{t['holder']}</div>
                    <div style="font-size:0.78rem;color:#64748b;">{t['email']} · {t['account']}</div>
                </div>
                <div style="margin-left:auto;text-align:right;">
                    <div style="font-size:1.1rem;font-weight:800;color:{dec_col};">{t['decision']}</div>
                    <div style="font-size:0.72rem;color:#64748b;">{tier} Risk</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            d1, d2, d3, d4 = st.columns(4, gap="small")

            with d1:
                st.markdown(f"""
                <div class="detail-panel">
                    <h4>Account Risk</h4>
                    <div class="detail-row"><span class="detail-key">24h Velocity</span><span class="detail-val">{acct['velocity_24h']} txns</span></div>
                    <div class="detail-row"><span class="detail-key">7d Velocity</span><span class="detail-val">{acct['velocity_7d']} txns</span></div>
                    <div class="detail-row"><span class="detail-key">Account Age</span><span class="detail-val">{acct['account_age_days']}d</span></div>
                    <div class="detail-row"><span class="detail-key">Prior Flags</span><span class="detail-val">{acct['prior_flags']}</span></div>
                    <div class="detail-row"><span class="detail-key">Pattern Score</span><span class="detail-val">{max(0,min(100,acct['pattern_score']))}</span></div>
                    <div class="detail-row"><span class="detail-key">Behavior Anomaly</span><span class="detail-val" style="color:{'#f87171' if acct['behavior_anomaly'] else '#4ade80'}">{'YES ⚠' if acct['behavior_anomaly'] else 'Normal'}</span></div>
                </div>
                """, unsafe_allow_html=True)

            with d2:
                ip_col = "#f87171" if ip["vpn"] else "#4ade80"
                abuse_col = "#f87171" if ip["abuse_score"] > 50 else "#eab308" if ip["abuse_score"] > 20 else "#4ade80"
                st.markdown(f"""
                <div class="detail-panel">
                    <h4>IP Intelligence</h4>
                    <div class="detail-row"><span class="detail-key">Address</span><span class="detail-val">{ip['ip']}</span></div>
                    <div class="detail-row"><span class="detail-key">Location</span><span class="detail-val">{ip['city']}, {ip['country']}</span></div>
                    <div class="detail-row"><span class="detail-key">Type</span><span class="detail-val" style="color:{ip_col};">{ip['type']}</span></div>
                    <div class="detail-row"><span class="detail-key">ISP</span><span class="detail-val">{ip['isp']}</span></div>
                    <div class="detail-row"><span class="detail-key">Abuse Score</span><span class="detail-val" style="color:{abuse_col};">{ip['abuse_score']}/100</span></div>
                    <div class="detail-row"><span class="detail-key">VPN/Proxy</span><span class="detail-val" style="color:{ip_col};">{'YES ⚠' if ip['vpn'] else 'No'}</span></div>
                </div>
                """, unsafe_allow_html=True)

            with d3:
                if ofac["hit"]:
                    ofac_html = f"""
                    <div class="detail-row"><span class="detail-key">Status</span><span class="detail-val" style="color:#f87171;">🚨 HIT</span></div>
                    <div class="detail-row"><span class="detail-key">Matched</span><span class="detail-val" style="font-size:0.7rem;">{ofac['matched_name']}</span></div>
                    <div class="detail-row"><span class="detail-key">List</span><span class="detail-val">{ofac['list']}</span></div>
                    <div class="detail-row"><span class="detail-key">Confidence</span><span class="detail-val">{int(ofac['confidence']*100)}%</span></div>
                    <div class="detail-row"><span class="detail-key">Date Added</span><span class="detail-val">{ofac['date_added']}</span></div>
                    """
                else:
                    ofac_html = '<div style="color:#4ade80;font-size:0.8rem;padding:8px 0;">✅ No sanctions matches</div>'
                st.markdown(f"""
                <div class="detail-panel">
                    <h4>OFAC / Sanctions</h4>
                    {ofac_html}
                </div>
                """, unsafe_allow_html=True)

            with d4:
                if breach["hit"]:
                    src_rows = "".join(f'<div class="detail-row"><span class="detail-key">Source</span><span class="detail-val">{s}</span></div>' for s in breach["sources"])
                    fields = ", ".join(breach["exposed_fields"])
                    breach_html = f"""
                    <div class="detail-row"><span class="detail-key">Status</span><span class="detail-val" style="color:#f97316;">⚠️ BREACHED</span></div>
                    {src_rows}
                    <div class="detail-row"><span class="detail-key">Exposed</span><span class="detail-val" style="font-size:0.7rem;">{fields}</span></div>
                    """
                else:
                    breach_html = '<div style="color:#4ade80;font-size:0.8rem;padding:8px 0;">✅ No breach records</div>'
                st.markdown(f"""
                <div class="detail-panel">
                    <h4>Dark Web / Breach</h4>
                    {breach_html}
                </div>
                """, unsafe_allow_html=True)

with chart_col:
    st.markdown('<div class="section-header">Risk Analytics</div>', unsafe_allow_html=True)

    # ── Risk Distribution Donut ──
    txns = st.session_state.transactions
    tier_counts = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
    for t in txns:
        tier = t.get("tier", risk_tier(t["risk_score"]))
        tier_counts[tier] = tier_counts.get(tier, 0) + 1

    labels = list(tier_counts.keys())
    values = list(tier_counts.values())
    colors = [TIER_COLORS[l] for l in labels]

    donut_fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.65,
        marker=dict(colors=colors, line=dict(color="#0f172a", width=2)),
        textinfo="none",
        hovertemplate="%{label}: %{value} (%{percent})<extra></extra>",
    )])
    donut_fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="v",
            x=1, y=0.5,
            font=dict(color="#94a3b8", size=11),
            bgcolor="rgba(0,0,0,0)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=20, b=10, l=0, r=80),
        height=200,
        annotations=[dict(
            text=f"<b>{sum(values)}</b><br><span style='font-size:10px'>txns</span>",
            x=0.38, y=0.5,
            font=dict(size=16, color="#f1f5f9"),
            showarrow=False,
        )],
    )

    st.markdown('<div style="font-size:0.78rem;font-weight:600;color:#94a3b8;margin-bottom:4px;">Risk Distribution</div>', unsafe_allow_html=True)
    st.plotly_chart(donut_fig, use_container_width=True, config={"displayModeBar": False})

    # ── Risk Score Trend ──
    hours, scores = generate_trend_data()
    hour_labels = [h.strftime("%H:%M") for h in hours]

    # Color gradient: segment by risk level
    trend_fig = go.Figure()

    # Background shading zones
    trend_fig.add_hrect(y0=0, y1=30, fillcolor="rgba(34,197,94,0.04)", line_width=0)
    trend_fig.add_hrect(y0=30, y1=55, fillcolor="rgba(234,179,8,0.04)", line_width=0)
    trend_fig.add_hrect(y0=55, y1=75, fillcolor="rgba(249,115,22,0.04)", line_width=0)
    trend_fig.add_hrect(y0=75, y1=100, fillcolor="rgba(239,68,68,0.06)", line_width=0)

    trend_fig.add_trace(go.Scatter(
        x=hour_labels,
        y=scores,
        mode="lines",
        line=dict(color="#22c55e", width=2, shape="spline"),
        fill="tozeroy",
        fillcolor="rgba(34,197,94,0.08)",
        hovertemplate="%{x}: Score %{y}<extra></extra>",
    ))

    trend_fig.update_layout(
        xaxis=dict(
            tickfont=dict(color="#475569", size=9),
            gridcolor="#1e293b",
            tickangle=-45,
            nticks=8,
            showline=False,
            zeroline=False,
        ),
        yaxis=dict(
            tickfont=dict(color="#475569", size=9),
            gridcolor="#1e293b",
            range=[0, 100],
            showline=False,
            zeroline=False,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=10, b=10, l=30, r=10),
        height=180,
        showlegend=False,
    )

    st.markdown('<div style="font-size:0.78rem;font-weight:600;color:#94a3b8;margin-bottom:4px;">24h Risk Score Trend</div>', unsafe_allow_html=True)
    st.plotly_chart(trend_fig, use_container_width=True, config={"displayModeBar": False})

    # ── Decision breakdown mini bar ──
    st.markdown('<div style="font-size:0.78rem;font-weight:600;color:#94a3b8;margin-bottom:6px;">Decision Breakdown</div>', unsafe_allow_html=True)

    dec_counts = {"GO": 0, "HOLD": 0, "BLOCK": 0}
    for t in txns:
        dec_counts[t["decision"]] = dec_counts.get(t["decision"], 0) + 1

    total_txns = max(1, sum(dec_counts.values()))
    for dec, cnt in dec_counts.items():
        pct = cnt / total_txns * 100
        color = DECISION_COLORS[dec]
        st.markdown(f"""
        <div style="margin-bottom:6px;">
            <div style="display:flex;justify-content:space-between;font-size:0.72rem;margin-bottom:3px;">
                <span style="color:{color};font-weight:600;">{dec}</span>
                <span style="color:#64748b;">{cnt} ({pct:.0f}%)</span>
            </div>
            <div style="background:#0f172a;border-radius:4px;height:6px;overflow:hidden;">
                <div style="width:{pct:.1f}%;height:100%;background:{color};border-radius:4px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── IP Type breakdown ──
    st.markdown('<div style="font-size:0.78rem;font-weight:600;color:#94a3b8;margin-top:12px;margin-bottom:6px;">IP Type Breakdown</div>', unsafe_allow_html=True)

    ip_type_counts = {}
    for t in txns:
        itype = t["ip_detail"]["type"]
        ip_type_counts[itype] = ip_type_counts.get(itype, 0) + 1

    ip_sorted = sorted(ip_type_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    ip_total = max(1, sum(v for _, v in ip_sorted))

    ip_colors_map = {
        "Residential": "#22c55e",
        "Corporate": "#3b82f6",
        "VPN": "#eab308",
        "Proxy": "#f97316",
        "Tor": "#ef4444",
        "Datacenter": "#8b5cf6",
        "Mobile": "#06b6d4",
    }
    for itype, cnt in ip_sorted:
        pct = cnt / ip_total * 100
        color = ip_colors_map.get(itype, "#64748b")
        st.markdown(f"""
        <div style="margin-bottom:5px;">
            <div style="display:flex;justify-content:space-between;font-size:0.7rem;margin-bottom:2px;">
                <span style="color:{color};font-weight:600;">{itype}</span>
                <span style="color:#64748b;">{cnt}</span>
            </div>
            <div style="background:#0f172a;border-radius:3px;height:4px;overflow:hidden;">
                <div style="width:{pct:.1f}%;height:100%;background:{color};border-radius:3px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("<div style='margin-top:2rem;'></div>", unsafe_allow_html=True)
st.markdown("""
<div style="border-top:1px solid #1e293b;padding-top:0.75rem;display:flex;justify-content:space-between;align-items:center;">
    <div style="font-size:0.7rem;color:#334155;">
        Abrigo Fraud Intelligence Middleware · v2.4.1 · © 2026 Abrigo
    </div>
    <div style="font-size:0.7rem;color:#334155;">
        All data shown is simulated for demonstration purposes
    </div>
    <div style="display:flex;gap:12px;">
        <span style="font-size:0.7rem;color:#22c55e;">● API Online</span>
        <span style="font-size:0.7rem;color:#22c55e;">● DB Online</span>
        <span style="font-size:0.7rem;color:#22c55e;">● Scan Engine Ready</span>
    </div>
</div>
""", unsafe_allow_html=True)
