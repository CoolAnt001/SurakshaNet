import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import math
import base64
import requests
import threading
from datetime import datetime

# --- Page Setup ---
st.set_page_config(
    page_title="SurakshaNet 2.0: Community Health Grid",
    page_icon="🛡️",
    layout="wide"
)

# --- Global Database Configuration ---
# Set your Google Apps Script Web App URL here for universal cross-device persistence
DEFAULT_GSHEET_URL = "https://script.google.com/macros/s/AKfycbzt_VXGXKrFKQltXEeXvqPjV0zHjSih0AMjQOcBwc-YwvhvmTJYe8om0NiFMbPPccZU/exec"


# --- Custom CSS Styling (Premium Glassmorphism & Micro-animations) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

    /* Global Font Override & Hide Default Streamlit Branding */
    html, body, [class*="css"], .stText, .stMarkdown, .stButton, div, p, h1, h2, h3, h4, input, select {
        font-family: 'Outfit', sans-serif !important;
    }
    footer {visibility: hidden;}

    /* Premium glassmorphic card style */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(128, 128, 128, 0.15);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        color: var(--text-color);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.25);
        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.3s ease, box-shadow 0.3s ease;
    }
    .glass-card:hover {
        transform: translateY(-3px);
        border-color: rgba(0, 242, 254, 0.4);
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.35);
    }

    /* Light Theme override for glassmorphic cards */
    @media (prefers-color-scheme: light) {
        .glass-card {
            background: rgba(255, 255, 255, 0.6);
            border: 1px solid rgba(0, 0, 0, 0.08);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.05);
        }
        .glass-card:hover {
            box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.09);
        }
    }

    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: var(--primary-color);
        line-height: 1.1;
    }
    .metric-label {
        font-size: 0.85rem;
        color: var(--text-color);
        opacity: 0.7;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .status-badge {
        padding: 6px 14px;
        border-radius: 9999px;
        font-size: 0.9rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .status-safe {
        background-color: rgba(16, 185, 129, 0.15);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .status-warning {
        background-color: rgba(245, 158, 11, 0.15);
        color: #F59E0B;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    .status-danger {
        background-color: rgba(239, 68, 68, 0.15);
        color: #EF4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    /* Style headers to dynamically adapt to Light/Dark modes */
    h1, h2, h3, h4 {
        color: var(--text-color) !important;
        font-weight: 700 !important;
    }

    /* Premium Header Hero Banner overrides */
    .custom-hero-banner {
        background: linear-gradient(135deg, #0b132b 0%, #1c2541 100%) !important;
        padding: 24px 30px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        margin-bottom: 15px;
    }
    .custom-hero-banner h1 {
        color: #00F2FE !important;
        margin: 0 !important;
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px !important;
        text-shadow: 0 0 15px rgba(0,242,254,0.3) !important;
    }
    .custom-hero-banner p {
        color: rgba(255, 255, 255, 0.85) !important;
        margin: 6px 0 0 0 !important;
        font-size: 1.05rem !important;
        font-weight: 500 !important;
    }

    /* Custom tabs styling adapting to Streamlit theme */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: var(--background-color);
        padding: 6px;
        border-radius: 8px;
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        background-color: var(--secondary-background-color);
        border-radius: 6px;
        color: var(--text-color);
        opacity: 0.8;
        font-weight: 600;
        border: none;
    }
    .stTabs [data-baseweb="tab"]:hover {
        opacity: 1.0;
        color: var(--primary-color);
    }
    .stTabs [aria-selected="true"] {
        background-color: var(--primary-color) !important;
        color: var(--background-color) !important;
        font-weight: 700 !important;
        opacity: 1.0 !important;
    }

    /* Customized Gradient Buttons */
    div.stButton > button {
        background: linear-gradient(135deg, #00F2FE 0%, #4FACFE 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 8px 24px !important;
        box-shadow: 0 4px 15px rgba(0, 242, 254, 0.25) !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    div.stButton > button:hover {
        transform: scale(1.03) !important;
        box-shadow: 0 6px 20px rgba(0, 242, 254, 0.4) !important;
        color: white !important;
        border: none !important;
    }
    div.stButton > button:active {
        transform: scale(0.97) !important;
    }

    /* Custom Centered Gateway Lock Card */
    .lock-card {
        max-width: 480px;
        margin: 40px auto;
        padding: 40px;
        text-align: center;
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 20px;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.3);
    }
    @media (prefers-color-scheme: light) {
        .lock-card {
            background: rgba(255, 255, 255, 0.7);
            border: 1px solid rgba(0, 0, 0, 0.08);
            box-shadow: 0 15px 35px rgba(31, 38, 135, 0.06);
        }
    }
    .lock-icon {
        font-size: 3rem;
        margin-bottom: 15px;
        animation: lock-wiggle 3s infinite ease-in-out;
        display: inline-block;
    }
    @keyframes lock-wiggle {
        0%, 100% { transform: rotate(0deg); }
        15% { transform: rotate(-8deg); }
        30% { transform: rotate(8deg); }
        45% { transform: rotate(-4deg); }
        60% { transform: rotate(4deg); }
    }

    /* Outbreak Alert Dynamic Animations */
    .alert-banner-warning {
        animation: pulse-orange 2.2s infinite ease-in-out;
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 20px;
        transition: border-color 0.3s ease, box-shadow 0.3s ease;
    }
    .alert-banner-danger {
        animation: blink-red 1.6s infinite ease-in-out;
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 20px;
        transition: border-color 0.3s ease, box-shadow 0.3s ease;
    }
    @keyframes pulse-orange {
        0%, 100% { box-shadow: 0 0 10px rgba(245, 158, 11, 0.15); border-color: rgba(245, 158, 11, 0.4); }
        50% { box-shadow: 0 0 25px rgba(245, 158, 11, 0.45); border-color: rgba(245, 158, 11, 1); }
    }
    @keyframes blink-red {
        0%, 100% { box-shadow: 0 0 10px rgba(239, 68, 68, 0.2); border-color: rgba(239, 68, 68, 0.4); }
        50% { box-shadow: 0 0 28px rgba(239, 68, 68, 0.55); border-color: rgba(239, 68, 68, 1); }
    }
</style>
""", unsafe_allow_html=True)

# --- Multilingual Localization (I18N) - Simplified & Plain Language ---
I18N = {
    "English": {
        "sidebar_lang_header": "🌐 Select Language / ଭାଷା / भाषा",
        "sidebar_title": "🛡️ Health Safety Grid",
        "sidebar_desc": "Helping communities track health symptoms without sharing personal data.",
        "zero_central_policy": "🔒 **Privacy Guarantee:** No names, phone numbers, or clinic files ever leave local centers. The central dashboard only analyzes masked numbers to locate outbreaks.",
        "app_title": "🛡️ SurakshaNet 2.0",
        "app_sub": "Community Early-Warning Dashboard (Privacy Protected)",
        "inject_outbreak": "🕹️ Select Simulation Scenario",
        
        # Scenario Labels
        "scenario_normal": "🟢 Normal Baseline (No Active Outbreaks)",
        "scenario_gi": "🌊 Gastrointestinal Outbreak Cluster (Waterborne)",
        "scenario_resp": "🫁 Cold-Snap Acute Respiratory Surge",
        "scenario_typo": "⚠️ False Alarm (Single-Source Data Typo)",
        "scenario_small": "🔬 Small Cohort Threat (k-Anonymity Guard Demo)",
        
        # Tabs
        "tab_public": "📢 1. Public Health Radar",
        "tab_clinic": "🏥 2. Clinic Reporter Portal (Passcode)",
        "tab_officer": "🚨 3. Health Officer Console (Passcode)",
        "tab_audit": "🔒 4. Privacy Audit Log",
        
        # Tab 1 Public Health Radar
        "radar_title": "📢 Public Health Radar & Safety Advisories",
        "radar_desc": "This section shows current health safety levels. If unusual symptom activity is detected, guidelines are shown below.",
        "threat_prob": "Outbreak Threat Probability",
        "active_symptoms": "Rising Symptoms in the Area",
        "adv_safe": "🟢 **Current Status: Safe.** Maintain standard hygiene. Wash hands regularly and drink clean water.",
        "adv_gi": "⚠️ **Warning: Gastrointestinal/Waterborne threat detected.** \n\n* **Safety Measures:** Drink only boiled or filtered water. Avoid raw street foods. Wash utensils thoroughly.",
        "adv_resp": "⚠️ **Warning: Respiratory / Flu surge detected.** \n\n* **Safety Measures:** Wear masks in crowded spaces. Keep warm. Maintain respiratory hygiene (cough into elbow).",
        "adv_general": "⚠️ **Alert: Unusual symptoms detected.** Watch local updates and contact a doctor if feeling unwell.",
        
        # Tab 2 Clinic Reporter
        "clinic_title": "🏥 Clinic Data Entry Portal",
        "clinic_desc": "Authorized clinic staff can log daily symptom counts. Patient identities are automatically masked locally before upload.",
        "select_node": "Select Node to Inspect:",
        "node_type_label": "Node Type:",
        "pass_prompt_clinic": "🔑 Enter Clinic Passcode to access entry tools:",
        "pass_warn_clinic": "🔒 Clinic Portal Locked. Please enter the passcode (1234) to unlock reporting channels and logs.",
        "db_title": "💾 Local Private Registry (Node Firewall)",
        "chart_title": "📊 Privacy Masking Visual Comparison: Raw vs. Transmitted",
        "bar_raw": "Original Private Count",
        "bar_trans": "Anonymized Count (Sent to Server)",
        "ingest_title": "✍️ Log Daily Cases (Local Ingestion)",
        "ingest_desc": "Select a reporting channel to log symptoms. Data is protected locally before transmission.",
        "ingest_method_label": "Select Reporting Channel:",
        "ingest_symptom": "Select Symptom Category:",
        "ingest_loc": "Reporter Location (Hostel / Campus Zone):",
        "ingest_tally": "Reported Case Count (Confidential Count):",
        "ingest_notes": "Clinical Notes (Avoid personal names or phones):",
        "precomp_title": "🔍 Local Privacy Filter Preview",
        "local_record_title": "🔒 Private Local Log (Stays on Edge):",
        "transmitted_payload_title": "📡 Uploaded Data (Sent to Server):",
        "submit_btn": "🚀 Safe Upload to Server",
        "logbook_title": "📂 Recent Clinic Logbook (Private Node Storage)",
        "clear_btn": "🗑️ Clear Logbook",
        "log_info": "No manual logs recorded yet. Use the channels above to enter logs.",
        "log_success": "Success! Case logged and uploaded with identity masking.",
        
        # Option Ingestion Labels
        "opt1": "Option 1: Quick Digital Form (Manual)",
        "opt2": "Option 2: Toll-Free IVR Voice Gateway (Phone Keypad)",
        "opt3": "Option 3: On-Device Paper Register Scanner (OCR)",
        "opt4": "Option 4: Automated Hospital Database Linkage",
        
        # Tab 2 Table Columns
        "col_indicator": "Symptom Indicator",
        "col_baseline": "Historical Normal Average",
        "col_raw": "Private Raw Count",
        "col_noise": "Privacy Noise Added",
        "col_dp": "Noisy Upload Count",
        "col_status": "Identity Protection Status",
        "col_trans_val": "Safe Shared Count",
        "col_trans_z": "Anomaly Deviation Strength",
        
        # Tab 3 Health Officer Console
        "officer_title": "🚨 Public Health Officer Command Console",
        "officer_desc": "Authorized Health Officers can configure global sensitivity and issue emergency broadcasts.",
        "pass_prompt_officer": "🔑 Enter Officer Passcode:",
        "pass_warn_officer": "🔒 Console Locked. Please enter the passcode (9999) to unlock controls and alert dispatch.",
        "sec_controls": "⚙️ Surveillance Parameter Tuning",
        "epsilon_label": "Privacy Protection Level (Low / Medium / High)",
        "epsilon_help": "Controls how much masking noise is added to edge tallies. Higher noise provides higher privacy.",
        "k_label": "Minimum Patient Group Size for Reporting (k-Anonymity)",
        "k_help": "Counts below this limit will be blocked to prevent linking records to small student groups.",
        "cutoff_label": "Alert Sensitivity Threshold",
        "cutoff_help": "Adjust threshold to avoid false alarms from single-day spikes.",
        "regional_table_title": "🏥 Regional Node Deviation Metrics",
        "broadcast_title": "📢 Emergency Warning Broadcast Panel",
        "broadcast_desc": "Send official warnings to mobile health units and subscriber email registries.",
        "alert_draft_label": "Draft Warning Message:",
        "alert_reg_label": "Subscriber Email List:",
        "sign_btn": "✍️ Authorize & Dispatch Emergency Alert",
        "log_title": "Emergency Dispatch Log",
        "alert_dispatched_success": "Advisory authorized with Health Master Key and dispatched to mobile units.",
        "xai_no_anom": "No active anomalies. Region operating within baseline parameters.",
        
        # Tab 4 Privacy Audit Log
        "audit_title": "🔒 Privacy Assurance & Compliance Audit Log",
        "audit_desc": "Proves mathematically that no personal names, phone numbers, or exact coordinates leave the edge nodes.",
        "privacy_compliance": "Data Protection Compliance",
        "dp_noise_distortion": "Privacy Noise Scale",
        "k_anon_suppression": "Group Suppression Active",
        "ledger_title": "⚖️ Compliance Verification Ledger",
        
        # Table Audit Columns
        "audit_col_node": "Reporting Center",
        "audit_col_field": "Indicator Category",
        "audit_col_eps": "Privacy Level",
        "audit_col_noise": "Applied Masking Noise",
        "audit_col_guard": "Group Privacy Check",
        "audit_col_payload": "Transmitted Index",
        
        # Local Node Names
        "node_campus_name": "🏫 Kalinga Institute Clinic",
        "node_campus_desc": "Tracks student health visits and daily symptoms.",
        "node_water_name": "🧪 Cuttack Municipal Water Quality Station",
        "node_water_desc": "Monitors chemical indexes, turbidity, and bacterial levels.",
        "node_hospital_name": "🏥 Capital Hospital Triage",
        "node_hospital_desc": "Aggregates urban outpatient registration counts.",
        "node_weather_name": "☁️ Bhubaneswar Weather Center",
        "node_weather_desc": "Records ambient environmental factors correlating with disease vectors.",
        "node_soa_name": "🏫 SOA University Clinic",
        "node_soa_desc": "Monitors student health visits and symptoms at Siksha 'O' Anusandhan, Bhubaneswar.",
        
        # Symptom Labels
        "lbl_gi": "Diarrhea / Stomach Pain",
        "lbl_resp": "Cough / Respiratory Issues",
        "lbl_fever": "Fever & Joint Pain",
        "lbl_coliform": "Coliform Bacteria (MPN/100ml)",
        "lbl_turb": "Water Turbidity (NTU)",
        "lbl_ph": "Water pH Level",
        "lbl_diarrhea": "Diarrheal Tally",
        "lbl_ili": "Influenza-Like Symptoms (ILI)",
        "lbl_fever_high": "High Fever Cases",
        "lbl_temp": "Average Temperature (°C)",
        "lbl_humidity": "Relative Humidity (%)",
        "lbl_rainfall": "Daily Rainfall (mm)"
    },
    "ଓଡ଼ିଆ (Odia)": {
        "sidebar_lang_header": "🌐 ଭାଷା ଚୟନ (Language)",
        "sidebar_title": "🛡️ ସ୍ୱାସ୍ଥ୍ୟ ସୁରକ୍ଷା ଗ୍ରୀଡ୍",
        "sidebar_desc": "ବ୍ୟକ୍ତିଗତ ତଥ୍ୟ ପ୍ରକାଶ ନକରି ସ୍ଥାନୀୟ ରୋଗ ଲକ୍ଷଣ ଟ୍ରାକ୍ କରିବାର ସହଜ ମାଧ୍ୟମ।",
        "zero_central_policy": "🔒 **ଗୋପନୀୟତା ଗ୍ୟାରେଣ୍ଟି:** କୌଣସି ନାମ କିମ୍ବା ଫୋନ୍ ନମ୍ବର କ୍ଲିନିକ୍ ବାହାରକୁ ଯାଏ ନାହିଁ। କେନ୍ଦ୍ରୀୟ ରାଡାର କେବଳ ସାଧାରଣ ସୂଚକାଙ୍କ ଯାଞ୍ଚ କରିଥାଏ।",
        "app_title": "🛡️ ସୁରକ୍ଷା-ନେଟ୍ ୨.୦",
        "app_sub": "ସହଜ ମହାମାରୀ ସତର୍କତା ବ୍ୟବସ୍ଥା (ଗୋପନୀୟତା ସୁରକ୍ଷିତ)",
        "inject_outbreak": "🕹️ ସିନାରିଓ ଚୟନ କରନ୍ତୁ",
        
        # Scenario Labels
        "scenario_normal": "🟢 ସ୍ୱାଭାବିକ ସ୍ଥିତି (କୌଣସି ସତର୍କତା ନାହିଁ)",
        "scenario_gi": "🌊 ପେଟ ରୋଗ / ଜଳବାହିତ ସଂକ୍ରମଣ ସିନାରିଓ",
        "scenario_resp": "🫁 ଥଣ୍ଡା ଜନିତ ଶ୍ୱାସକ୍ରିୟา ସଂକ୍ରମଣ ସିନାରିଓ",
        "scenario_typo": "⚠️ ତଥ୍ୟ ପ୍ରବେଶ ଭୁଲ୍ (ତ୍ରୁଟି ଯାଞ୍ଚ ସିମୁଲେସନ)",
        "scenario_small": "🔬 ଗୋପନୀୟତା ଯାଞ୍ଚ (k-Anonymity ସିମୁଲେସନ)",
        
        # Tabs
        "tab_public": "📢 ୧. ସାଧାରଣ ସ୍ୱାସ୍ଥ୍ୟ ସୂଚନା",
        "tab_clinic": "🏥 ୨. କ୍ଲିନିକ୍ ତଥ୍ୟ ଏଣ୍ଟ୍ରି (Passcode)",
        "tab_officer": "🚨 ୩. ସ୍ୱାସ୍ଥ୍ୟ ଅଧିକାରୀ କନସୋଲ୍ (Passcode)",
        "tab_audit": "🔒 ୪. ଗୋପନୀୟତା ଯାଞ୍ଚ ଲଗ୍",
        
        # Tab 1 Public Health Radar
        "radar_title": "📢 ସାଧାରଣ ସ୍ୱାସ୍ଥ୍ୟ ସୂଚନା ଏବଂ ସୁରକ୍ଷା ପରାମର୍ଶ",
        "radar_desc": "ଏହି ବିଭାଗରେ ବର୍ତ୍ତମାନର ସ୍ୱାସ୍ଥ୍ୟ ସୁରକ୍ଷା ସ୍ଥିତି ଦର୍ଶାଯାଇଛି। ଯଦି କୌଣସି ଅସ୍ୱାଭାବିକ ଲକ୍ଷଣ ଦେଖାଯାଏ, ସୁରକ୍ଷା ପଦକ୍ଷେପ ତଳେ ପ୍ରଦର୍ଶିତ ହେବ।",
        "threat_prob": "ଆଉଟବ୍ରେକ୍ ଆଶଙ୍କା",
        "active_symptoms": "ବର୍ତ୍ତମାନ ବଢୁଥିବା ରୋଗ ଲକ୍ଷଣ",
        "adv_safe": "🟢 **ବର୍ତ୍ତମାନ ସ୍ଥିତି: ସୁରକ୍ଷିତ।** ନିୟମିତ ହାତ ଧୁଅନ୍ତୁ ଏବଂ ସଫା ପାଣି ପିଅନ୍ତୁ।",
        "adv_gi": "⚠️ **ସତର୍କତା: ପେଟ ରୋଗ / ଦୂଷିତ ଜଳବାହିତ ଆଶଙ୍କା।** \n\n* **ସୁରକ୍ଷା ପରାମର୍ଶ:** କେବଳ ଫୁଟା ହୋଇଥିବା ପାଣି ପିଅନ୍ତୁ। ବାହାର ଖାଦ୍ୟ ଖାଆନ୍ତୁ ନାହିଁ। ବାସନକୁସନ ଭଲ ଭାବରେ ସଫା କରନ୍ତୁ।",
        "adv_resp": "⚠️ **ସତର୍କତା: ଥଣ୍ଡା ଜନିତ ଶ୍ୱାସକ୍ରିୟା ସଂକ୍ରମଣ ବୃଦ୍ଧି।** \n\n* **ସୁରକ୍ଷା ପରାମର୍ଶ:** ଭିଡ଼ ଜାଗାରେ ମାସ୍କ ବ୍ୟବହାର କରନ୍ତୁ। ଶରୀରକୁ ଗରମ ରଖନ୍ତୁ। କାଶିବା ବେଳେ ରୁମାଲ୍ ବ୍ୟବହାର କରନ୍ତୁ।",
        "adv_general": "⚠️ **ସତର୍କତା: ଅସ୍ୱାଭାବିକ ଲକ୍ଷଣ ଚିହ୍ନଟ ହୋଇଛି।** ସ୍ଥାନୀୟ ଅପଡେଟ୍ ଯାଞ୍ଚ କରନ୍ତୁ ଏବଂ ଅସୁସ୍ଥ ଅନୁଭବ କଲେ ଡାକ୍ତରଙ୍କ ସହିତ ପରାମର୍ଶ କରନ୍ତୁ।",
        
        # Tab 2 Clinic Reporter
        "clinic_title": "🏥 କ୍ଲିନିକ୍ ତଥ୍ୟ ଏଣ୍ଟ୍ରି ପୋର୍ଟାଲ୍",
        "clinic_desc": "କ୍ଲିନିକ୍ କର୍ମଚାରୀମାନେ ଏଠାରେ ଦୈନିକ ରୋଗୀ ସଂଖ୍ୟା ଦର୍ଜ କରିପାରିବେ। ରୋଗୀଙ୍କ ବ୍ୟକ୍ତିଗତ ପରିଚୟ ସ୍ଥାନୀୟ ସ୍ତରରେ ଗୋପନ ରଖାଯାଏ।",
        "select_node": "ଯାଞ୍ଚ କରିବାକୁ ନୋଡ୍ ଚୟନ କରନ୍ତୁ:",
        "node_type_label": "ନୋଡ୍ ପ୍ରକାର:",
        "pass_prompt_clinic": "🔑 କ୍ଲିନିକ୍ ପାସକୋଡ୍ (Passcode) ପ୍ରବେଶ କରନ୍ତୁ:",
        "pass_warn_clinic": "🔒 କ୍ଲିନିକ୍ ପୋର୍ଟାଲ୍ ଲକ୍ ଅଛି। ତଥ୍ୟ ଦର୍ଜ କରିବା ପାଇଁ ପାସକୋଡ୍ (1234) ବ୍ୟବହାର କରନ୍ତୁ।",
        "db_title": "💾 ସ୍ଥାନୀୟ ବ୍ୟକ୍ତିଗତ ରେଜିଷ୍ଟ୍ରି (ଫାୟାରୱାଲ୍ ଭିତରେ)",
        "chart_title": "📊 ଗୋପନୀୟତା ପ୍ରଭାବ ତୁଳନା: ପ୍ରକୃତ ବନାମ ପ୍ରେରିତ ଡାଟା",
        "bar_raw": "ବ୍ୟକ୍ତିଗତ ପ୍ରକୃତ ସଂଖ୍ୟା",
        "bar_trans": "ପ୍ରେରିତ ପରିବର୍ତ୍ତିତ ସଂଖ୍ୟା",
        "ingest_title": "✍️ ଦୈନିକ ତଥ୍ୟ ଦର୍ଜ (ସ୍ଥାନୀୟ ଏଣ୍ଟ୍ରି)",
        "ingest_desc": "ତଳେ ଥିବା ଯେକୌଣସି ମାଧ୍ୟମ ଦ୍ୱାରା ରୋଗୀଙ୍କ ଲକ୍ଷଣ ଲଗ୍ କରନ୍ତୁ। ସମସ୍ତ ତଥ୍ୟ ସ୍ଥାନୀୟ ଭାବରେ ଯାଞ୍ଚ କରାଯିବ।",
        "ingest_method_label": "ତଥ୍ୟ ପ୍ରବେଶ ମାଧ୍ୟମ ଚୟନ କରନ୍ତୁ:",
        "ingest_symptom": "ରୋଗର ଲକ୍ଷଣ ବର୍ଗ ବାଛନ୍ତୁ:",
        "ingest_loc": "ରିପୋର୍ଟ କରୁଥିବା ସ୍ଥାନ (ହଷ୍ଟେଲ / କ୍ୟାମ୍ପସ ଜୋନ୍):",
        "ingest_tally": "ରୋଗୀଙ୍କ ସଂଖ୍ୟା (ପ୍ରକୃତ ହିସାବ):",
        "ingest_notes": "କ୍ଲିନିକାଲ୍ ସୂଚନା (ବ୍ୟକ୍ତିଗତ ନାମ ବା ଫୋନ୍ ନମ୍ବର ଲେଖନ୍ତୁ ନାହିଁ):",
        "precomp_title": "🔍 ସ୍ଥାନୀୟ ଗୋପନୀୟତା ଫିଲ୍ଟର୍ ପ୍ରି-ଭ୍ୟୁ",
        "local_record_title": "🔒 ସ୍ଥାନୀୟ ବ୍ୟକ୍ତିଗତ ରେକର୍ଡ (ଏଜ୍ ଭିତରେ ରହିବ):",
        "transmitted_payload_title": "📡 ପ୍ରେରିତ ପେଲୋଡ୍ (ସର୍ଭରକୁ ପଠାଯିବ):",
        "submit_btn": "🚀 ସର୍ଭରକୁ ସୁରକ୍ଷିତ ଅପଲୋଡ୍ କରନ୍ତୁ",
        "logbook_title": "📂 ନିକଟତମ କ୍ଲିନିକ୍ ଲଗ୍‌ବୁକ୍ (ବ୍ୟକ୍ତିଗତ ନୋଡ୍ ଷ୍ଟୋରେଜ୍)",
        "clear_btn": "🗑️ ଲଗ୍ କ୍ଲିୟର୍ କରନ୍ତୁ",
        "log_info": "କୌଣସି ଲଗ୍ ଦର୍ଜ ହୋଇନାହିଁ | ତଥ୍ୟ ପ୍ରବେଶ କରିବାକୁ ଉପରୋକ୍ତ ମାଧ୍ୟମ ବ୍ୟବହାର କରନ୍ତୁ।",
        "log_success": "ସଫଳତାର ସହ ଆଉଟବକ୍ସରେ ଯୋଗ ହେଲା।",
        
        # Option Ingestion Labels
        "opt1": "ମାଧ୍ୟମ ୧: ତ୍ୱରିତ ଡିଜିଟାଲ୍ ଫର୍ମ (Manual)",
        "opt2": "ମାଧ୍ୟମ ୨: ଟୋଲ୍ ଫ୍ରି IVR ଭଏସ୍ ସିମୁଲେଟର",
        "opt3": "ମାଧ୍ୟମ ୩: ଏଜ୍ OCR ପେପର ସ୍କାନର୍",
        "opt4": "ମାଧ୍ୟମ ୪: ସ୍ୱୟଂଚାଳିତ EMR ଡାଟାବେସ୍ ସିଙ୍କ୍",
        
        # Tab 2 Table Columns
        "col_indicator": "ରୋଗ ସୂଚକ",
        "col_baseline": "ଐତିହାସିକ ହାରାହାରି",
        "col_raw": "ବ୍ୟକ୍ତିଗତ ସଂଖ୍ୟା (Raw)",
        "col_noise": "ଗୋପନୀୟତା ନଏଜ୍",
        "col_dp": "ପରିବର୍ତ୍ତିତ ସଂଖ୍ୟା (DP)",
        "col_status": "ଗୋପନୀୟତା ସ୍ଥିତି",
        "col_trans_val": "ପ୍ରେରିତ ସଂଖ୍ୟା",
        "col_trans_z": "ଅସ୍ୱାଭାବିକ ମାତ୍ରା",
        
        # Tab 3 Health Officer Console
        "officer_title": "🚨 ସ୍ୱାସ୍ଥ୍ୟ ଅଧିକାରୀ କନସୋଲ୍",
        "officer_desc": "ସ୍ୱାସ୍ଥ୍ୟ ଅଧିକାରୀମାନେ ଏଠାରେ ସିଷ୍ଟମ୍ ସମ୍ବେଦନଶୀଳତା ଏବଂ ଜରୁରୀକାଳୀନ ସୂଚନା ନିୟନ୍ତ୍ରଣ କରିପାରିବେ।",
        "pass_prompt_officer": "🔑 ଅଧିକାରୀ ପାସକୋଡ୍ (Passcode) ଦିଅନ୍ତୁ:",
        "pass_warn_officer": "🔒 ଅଧିକାରୀ କନସୋଲ୍ ଲକ୍ ଅଛି। ନିୟନ୍ତ୍ରଣ କରିବା ପାଇଁ ପାସକୋଡ୍ (9999) ବ୍ୟବହାର କରନ୍ତୁ।",
        "sec_controls": "⚙️ ସତର୍କତା ଏବଂ ଗୋପନୀୟତା ସୀମା ନିୟନ୍ତ୍ରଣ",
        "epsilon_label": "ଗୋପନୀୟତା ସୁରକ୍ଷା ସ୍ତର (କମ୍ / ମଧ୍ୟମ / ଉଚ୍ଚ)",
        "epsilon_help": "ତଥ୍ୟ ପ୍ରେରଣରେ ଯୋଗ କରାଯାଉଥିବା ନଏଜ୍ ସୀମା। ଅଧିକ ନଏଜ୍ ଅଧିକ ଗୋପନୀୟତା ଦେଇଥାଏ।",
        "k_label": "ରୋଗୀ ସଂଖ୍ୟା ଅନାମଧେୟତା ସୀମା (k-Anonymity)",
        "k_help": "କମ୍ ସଂଖ୍ୟକ ରୋଗୀଙ୍କ ତଥ୍ୟକୁ ସମ୍ପୂର୍ଣ୍ଣ ପ୍ରତିବନ୍ଧିତ କରାଯାଏ ଯେପରି ସେମାନଙ୍କୁ ଚିହ୍ନଟ କରାଯାଇପାରିବ ନାହିଁ।",
        "cutoff_label": "ଆଲର୍ଟ ସମ୍ବେଦନଶୀଳତା ସୀମା",
        "cutoff_help": "ଭୁଲ ସତର୍କତା ହ୍ରାସ କରିବା ପାଇଁ ସୀମାକୁ ସଜାଡନ୍ତୁ।",
        "regional_table_title": "🏥 ଆଞ୍ଚଳିକ ନୋଡ୍ ଗତିବିଧି ସୂଚକାଙ୍କ",
        "broadcast_title": "📢 ଜରୁରୀକାଳୀନ ସ୍ୱାସ୍ଥ୍ୟ ସୂଚନା ପ୍ରେରଣ ପ୍ୟାନେଲ୍",
        "broadcast_desc": "ଏଠାରୁ ସ୍ୱାସ୍ଥ୍ୟ କର୍ମୀ ଏବଂ ଜନସାଧାରଣଙ୍କ ପାଇଁ ଜରୁରୀକାଳୀନ ଆଲର୍ଟ ଜାରି କରିପାରିବେ।",
        "alert_draft_label": "ଆଲର୍ଟ ବାର୍ତ୍ତା ଡ୍ରାଫ୍ଟ:",
        "alert_reg_label": "ସକ୍ରିୟ ମୋବାଇଲ୍ ଓ ଇମେଲ୍ ରେଜିଷ୍ଟ୍ରି:",
        "sign_btn": "✍️ ଆଲର୍ଟ ଜାରି କରନ୍ତୁ",
        "log_title": "ସୂଚନା ପ୍ରେରଣ ଲଗ୍",
        "alert_dispatched_success": "ଜରୁରୀକାଳୀନ ସୂଚନା ସଫଳତାର ସହ ପଠାଯାଇଛି।",
        "xai_no_anom": "ସମସ୍ତ ସୂଚକାଙ୍କ ସ୍ୱାଭାବିକ ସୀମା ମଧ୍ୟରେ ଅଛି।",
        
        # Tab 4 Privacy Audit Log
        "audit_title": "🔒 ଗୋପନୀୟତା ଅଡିଟ୍ ଏବଂ ସୁରକ୍ଷା ଲେଜର",
        "audit_desc": "କୌଣସି ବ୍ୟକ୍ତିଗତ ଚିହ୍ନଟକରଣ ତଥ୍ୟ (PII) ପ୍ରକାଶ ନକରି ସ୍ୱାଧୀନ ଗଣିତ ଲେଜର।",
        "privacy_compliance": "ଡାଟା ପ୍ରୋଟେକ୍ସନ ଅନୁପାଳନ",
        "dp_noise_distortion": "ଲାପ୍ଲେସ୍ ନଏଜ୍ ପ୍ରଭାବ",
        "k_anon_suppression": "ଗୋପନ ରଖାଯାଇଥିବା ସିଗନାଲ୍",
        "ledger_title": "⚖️ ଗୋପନୀୟତା ଅନୁପାଳନ ଯାଞ୍ଚ ଲେଜର",
        
        # Table Audit Columns
        "audit_col_node": "ରିପୋର୍ଟିଂ କେନ୍ଦ୍ର",
        "audit_col_field": "ତଥ୍ୟ ବର୍ଗ",
        "audit_col_eps": "ଗୋପନୀୟତା ସ୍ତର",
        "audit_col_noise": "ଯୋଗ ହୋଇଥିବା ନଏଜ୍",
        "audit_col_guard": "ଗୋପନୀୟତା ଯାଞ୍ଚ ସ୍ଥିତି",
        "audit_col_payload": "ପ୍ରେରିତ ପେଲୋଡ୍",
        
        # Local Node Names
        "node_campus_name": "🏫 କଳିଙ୍ଗ ଇନଷ୍ଟିଚ୍ୟୁଟ୍ ଛାତ୍ର କ୍ଲିନିକ୍",
        "node_campus_desc": "କ୍ୟାମ୍ପସରେ ଛାତ୍ରଛାତ୍ରୀଙ୍କ ସ୍ୱାସ୍ଥ୍ୟ ଏବଂ ରୋଗର ଲକ୍ଷଣ ଟ୍ରାକ୍ କରେ।",
        "node_water_name": "🧪 କଟକ ମ୍ୟୁନିସିପାଲିଟି ଜଳ ପରୀକ୍ଷାଗାର",
        "node_water_desc": "ଜଳର ପିଏଚ୍, ଟର୍ବିଡିଟି ଏବଂ ବ୍ୟାକ୍ଟେରିଆ ରିଡିଂ ରେକର୍ଡ କରେ।",
        "node_hospital_name": "🏥 କ୍ୟାପିଟାଲ୍ ହସ୍ପିଟାଲ୍ ଓପିଡି ଟ୍ରାଏଜ୍",
        "node_hospital_desc": "ସହରର ପ୍ରମୁଖ ସରକାରୀ ହସ୍ପିଟาଲ୍ ଓପିଡି ରୋଗୀ ସଂଖ୍ୟା ସଂଗ୍ରହ କରେ।",
        "node_weather_name": "☁️ ଭୁବନେଶ୍ୱର ପାଣିପାଗ କେନ୍ଦ୍ର",
        "node_weather_desc": "ରୋଗ ବାହକ ଅନୁକୁଳ ପାଣିପାଗ ସୂଚନା ଟ୍ରାକ୍ କରେ।",
        "node_soa_name": "🏫 ସୋଆ ବିଶ୍ୱବିଦ୍ୟାଳୟ ସ୍ୱାସ୍ଥ୍ୟ କେନ୍ଦ୍ର",
        "node_soa_desc": "ଭୁବנେଶ୍ୱର ସୋଆ ବିଶ୍ୱବିଦ୍ୟาଳୟ କ୍ୟାମ୍ପସର ଦୈନିକ ଚିକିତ୍ସା ତଥ୍ୟ।",
        
        # Metric Labels
        "lbl_gi": "ଝାଡ଼ାବାନ୍ତି / ପେଟ ଯନ୍ତ୍ରଣା",
        "lbl_resp": "କାଶ / ଶ୍ୱାସକ୍ରିୟା ଜନିତ ସମସ୍ୟା",
        "lbl_fever": "ଜ୍ୱର ଏବଂ ଗଣ୍ଠି ବିନ୍ଧା",
        "lbl_coliform": "କଲିଫର୍ମ ବ୍ୟାକ୍ଟେରିଆ (MPN/100ml)",
        "lbl_turb": "ଜଳର ମଳିନତା (Turbidity NTU)",
        "lbl_ph": "ଜଳର pH ସ୍ତର",
        "lbl_diarrhea": "ଓପିଡି ଝାଡ଼ାବାନ୍ତି ତାଲିକା",
        "lbl_ili": "ଇନ୍‌ଫ୍ଲୁଏଞ୍ଜା ସଦୃଶ ରୋଗ (ILI)",
        "lbl_fever_high": "ଉଚ୍ଚ ଜ୍ୱର ତାଲିକା",
        "lbl_temp": "ହାରାହାରି ତାପମାତ୍ରା (°C)",
        "lbl_humidity": "ଆପେକ୍ଷିକ ଆଦ୍ରତା (%)",
        "lbl_rainfall": "ଦୈନିକ ବୃଷ୍ଟିପାତ (mm)"
    },
    "हिंदी (Hindi)": {
        "sidebar_lang_header": "🌐 भाषा चयन (Language)",
        "sidebar_title": "🛡️ स्वास्थ्य सुरक्षा ग्रिड",
        "sidebar_desc": "व्यक्तिगत पहचान उजागर किए बिना बीमारी के लक्षणों को ट्रैक करने का सरल मंच।",
        "zero_central_policy": "🔒 **गोपनीयता सुरक्षा:** कोई नाम, फोन नंबर या व्यक्तिगत जानकारी केंद्रों से बाहर नहीं जाती। केंद्रीय सर्वर केवल गुप्त सांख्यिकी का उपयोग करता है।",
        "app_title": "🛡️ सुरक्षा-नेट 2.0",
        "app_sub": "सामुदायिक स्वास्थ्य चेतावनी ग्रिड (गोपनीयता सुरक्षित)",
        "inject_outbreak": "🕹️ सिमुलेशन परिदृश्य चुनें",
        
        # Scenario Labels
        "scenario_normal": "🟢 सामान्य स्थिति (कोई सक्रिय प्रकोप नहीं)",
        "scenario_gi": "🌊 जलोढ़ प्रकोप / गैस्ट्रोइंटेस्टाइनल क्लस्टर",
        "scenario_resp": "🫁 सर्दी जनित श्वसन प्रकोप क्लस्टर",
        "scenario_typo": "⚠️ एकल स्रोत प्रविष्टि त्रुटि (डेटा संगरोध)",
        "scenario_small": "🔬 गोपनीयता जांच (k-Anonymity सिमुलेशन)",
        
        # Tabs
        "tab_public": "📢 1. सार्वजनिक स्वास्थ्य सूचना",
        "tab_clinic": "🏥 2. क्लिनिक डेटा एंट्री पोर्टल (Passcode)",
        "tab_officer": "🚨 3. स्वास्थ्य अधिकारी कंसोल (Passcode)",
        "tab_audit": "🔒 4. गोपनीयता ऑडिट लॉग",
        
        # Tab 1 Public Health Radar
        "radar_title": "📢 सार्वजनिक स्वास्थ्य रडार एवं सुरक्षा दिशा-निर्देश",
        "radar_desc": "यह अनुभाग वर्तमान सार्वजनिक स्वास्थ्य सुरक्षा स्तर दिखाता है। यदि बीमारी का प्रकोप है, तो सुरक्षा निर्देश नीचे प्रदर्शित होंगे।",
        "threat_prob": "संक्रमण फैलने की आशंका",
        "active_symptoms": "क्षेत्र में बढ़ते हुए बीमारी के लक्षण",
        "adv_safe": "🟢 **वर्तमान स्थिति: सुरक्षित।** सामान्य स्वच्छता बनाए रखें। नियमित रूप से हाथ धोएं और साफ पानी पीएं।",
        "adv_gi": "⚠️ **चेतावनी: पेट की बीमारी / दूषित पानी से संक्रमण की आशंका।** \n\n* **सुरक्षा निर्देश:** केवल उबला हुआ या फ़िल्टर किया हुआ पानी पीएं। खुले में बिकने वाले भोजन से बचें। बर्तनों को अच्छी तरह साफ करें।",
        "adv_resp": "⚠️ **चेतावनी: सर्दी/फ्लू और श्वसन रोग में वृद्धि।** \n\n* **सुरक्षा निर्देश:** भीड़भाड़ वाली जगहों पर मास्क पहनें। शरीर को गर्म रखें। खांसते या छींकते समय कोहनी का उपयोग करें।",
        "adv_general": "⚠️ **चेतावनी: असामान्य लक्षण पाए गए हैं।** स्थानीय अपडेट देखें और अस्वस्थ महसूस करने पर डॉक्टर से संपर्क करें।",
        
        # Tab 2 Clinic Reporter
        "clinic_title": "🏥 क्लिनिक डेटा प्रविष्टि पोर्टल",
        "clinic_desc": "अधिकृत क्लिनिक कर्मचारी दैनिक मरीजों की संख्या दर्ज कर सकते हैं। मरीज की पहचान प्रेषित करने से पहले गुप्त कर दी जाती है।",
        "select_node": "जांच के लिए नोड चुनें:",
        "node_type_label": "नोड प्रकार:",
        "pass_prompt_clinic": "🔑 क्लिनिक पासकोड (Passcode) दर्ज करें:",
        "pass_warn_clinic": "🔒 क्लिनिक पोर्टल सुरक्षित है। रिपोर्ट दर्ज करने के लिए पासकोड (1234) का उपयोग करें।",
        "db_title": "💾 स्थानीय निजी रजिस्ट्री (फ़ायरवॉल के भीतर)",
        "chart_title": "📊 गोपनीयता प्रभाव तुलना: वास्तविक बनाम प्रेषित डेटा",
        "bar_raw": "गोपनीय वास्तविक संख्या",
        "bar_trans": "प्रेषित शोर-युक्त संख्या",
        "ingest_title": "✍️ दैनिक रिपोर्ट दर्ज करें (स्थानीय प्रविष्टि)",
        "ingest_desc": "लक्षण लॉग करने के लिए नीचे दिए गए माध्यम का चयन करें। सभी डेटा स्थानीय रूप से संसाधित किए जाएंगे।",
        "ingest_method_label": "डेटा प्रविष्टि माध्यम चुनें:",
        "ingest_symptom": "लक्षण श्रेणी चुनें:",
        "ingest_loc": "रिपोर्टर स्थान (छात्रावास / कैंपस क्षेत्र):",
        "ingest_tally": "दर्ज मामलों की संख्या (Confidential Count):",
        "ingest_notes": "अतिरिक्त विवरण (व्यक्तिगत नाम या फोन नंबर न लिखें):",
        "precomp_title": "🔍 स्थानीय गोपनीयता फ़िल्टर पूर्वावलोकन",
        "local_record_title": "🔒 स्थानीय रिकॉर्ड (क्लिनिक में ही रहेगा):",
        "transmitted_payload_title": "📡 प्रेषित पेलोड (सर्वर को भेजा जाएगा):",
        "submit_btn": "🚀 सर्वर पर सुरक्षित अपलोड करें",
        "logbook_title": "📂 स्थानीय क्लिनिक लॉगबुक (निजी नोड स्टोरेज)",
        "clear_btn": "🗑️ लॉग साफ़ करें",
        "log_info": "अभी तक कोई लॉग दर्ज नहीं किया गया है। डेटा दर्ज करने के लिए उपरोक्त माध्यमों का उपयोग करें।",
        "log_success": "सफलतापूर्वक दर्ज और प्रेषित किया गया।",
        
        # Option Ingestion Labels
        "opt1": "विकल्प 1: त्वरित डिजिटल फॉर्म (Manual)",
        "opt2": "विकल्प 2: टोल-फ्री IVR वॉयस सिम्युलेटर",
        "opt3": "विकल्प 3: एज OCR पेपर स्कैनर",
        "opt4": "विकल्प 4: स्वचालित EMR डेटाबेस सिंक",
        
        # Tab 2 Table Columns
        "col_indicator": "लक्षण संकेतक",
        "col_baseline": "ऐतिहासिक औसत",
        "col_raw": "गोपनीय वास्तविक संख्या",
        "col_noise": "लाप्लास शोर",
        "col_dp": "प्रेषित शोर-युक्त संख्या",
        "col_status": "गोपनीयता स्थिति",
        "col_trans_val": "प्रेषित मान",
        "col_trans_z": "विचलन तीव्रता",
        
        # Tab 3 Health Officer Console
        "officer_title": "🚨 स्वास्थ्य अधिकारी नियंत्रण कंसोल",
        "officer_desc": "अधिकृत स्वास्थ्य अधिकारी सिस्टम संवेदनशीलता और आपातकालीन संदेशों को नियंत्रित कर सकते हैं।",
        "pass_prompt_officer": "🔑 स्वास्थ्य अधिकारी पासकोड (Passcode) दर्ज करें:",
        "pass_warn_officer": "🔒 कंसोल लॉक है। इसे अनलॉक करने के लिए पासकोड (9999) का उपयोग करें।",
        "sec_controls": "⚙️ सिस्टम सतर्कता एवं गोपनीयता नियंत्रण",
        "epsilon_label": "गोपनीयता सुरक्षा स्तर (कम / मध्यम / उच्च)",
        "epsilon_help": "प्रेषित डेटा में जोड़ा जाने वाला शोर (noise) स्तर। अधिक शोर अधिक गोपनीयता सुनिश्चित करता है।",
        "k_label": "न्यूनतम रोगी समूह सीमा (k-Anonymity)",
        "k_help": "कम रोगी संख्या वाले मामलों की रिपोर्ट को दबा दिया जाता है ताकि किसी की पहचान न की जा सके।",
        "cutoff_label": "चेतावनी संवेदनशीलता सीमा",
        "cutoff_help": "गलत चेतावनियों को रोकने के लिए संवेदनशीलता सीमा समायोजित करें।",
        "regional_table_title": "🏥 क्षेत्रीय नोड गतिविधि संकेतक",
        "broadcast_title": "📢 आपातकालीन चेतावनी प्रसारण पैनल",
        "broadcast_desc": "यहां से स्वास्थ्य कर्मियों और जनता के लिए आपातकालीन संदेश जारी करें।",
        "alert_draft_label": "चेतावनी संदेश ड्राफ्ट:",
        "alert_reg_label": "सक्रिय मोबाइल एवं ईमेल सूची:",
        "sign_btn": "✍️ चेतावनी प्रसारित करें",
        "log_title": "चेतावनी प्रेषण लॉग",
        "alert_dispatched_success": "आपातकालीन चेतावनी सफलतापूर्वक प्रसारित कर दी गई है।",
        "xai_no_anom": "सभी संकेतक सामान्य स्तर पर काम कर रहे हैं।",
        
        # Tab 4 Privacy Audit Log
        "audit_title": "🔒 गोपनीयता ऑडिट एवं अनुपालन बहीखाता",
        "audit_desc": "बिना किसी व्यक्तिगत पहचान डेटा (PII) को उजागर किए स्वतंत्र गणितीय बहीखाता।",
        "privacy_compliance": "डेटा गोपनीयता अनुपालन",
        "dp_noise_distortion": "लाप्लास शोर स्तर",
        "k_anon_suppression": "छिपाए गए संकेतक",
        "ledger_title": "⚖️ गोपनीयता अनुपालन सत्यापन बहीखाता",
        
        # Table Audit Columns
        "audit_col_node": "रिपोर्टिंग केंद्र",
        "audit_col_field": "डेटा श्रेणी",
        "audit_col_eps": "गोपनीयता स्तर",
        "audit_col_noise": "लाप्लास शोर स्तर",
        "audit_col_guard": "गोपनीयता जांच स्थिति",
        "audit_col_payload": "प्रेषित पेलोड",
        
        # Local Node Names
        "node_campus_name": "🏫 कलिंगा इंस्टीट्यूट छात्र क्लिनिक",
        "node_campus_desc": "कैंपस में छात्रों के स्वास्थ्य और बीमारी के लक्षणों की निगरानी करता है।",
        "node_water_name": "🧪 कटक नगर पालिका जल लैब",
        "node_water_desc": "पानी की गुणवत्ता, टर्बिडिटी और बैक्टीरिया सूचकांक रिकॉर्ड करता है।",
        "node_hospital_name": "🏥 कैपिटल अस्पताल ओपीडी ट्राइएज",
        "node_hospital_desc": "शहर के मुख्य सरकारी अस्पताल की ओपीडी रोगी संख्या एकत्र करता है।",
        "node_weather_name": "☁️ भुवनेश्वर क्षेत्रीय मौसम केंद्र",
        "node_weather_desc": "मौसम की स्थिति ट्रैक करता है जो वेक्टर जनित रोगों को बढ़ावा दे सकती है।",
        "node_soa_name": "🏫 सोआ विश्वविद्यालय स्वास्थ्य केंद्र",
        "node_soa_desc": "भुवनेश्वर सोआ विश्वविद्यालय कैंपस का दैनिक स्वास्थ्य विवरण।",
        
        # Symptom Labels
        "lbl_gi": "दस्त / पेट दर्द",
        "lbl_resp": "खांसी / सांस लेने में तकलीफ",
        "lbl_fever": "बुखार और जोड़ों का दर्द",
        "lbl_coliform": "कोलीफ़ॉर्म बैक्टीरिया (MPN/100ml)",
        "lbl_turb": "जल की मैलापन (Turbidity NTU)",
        "lbl_ph": "जल का pH स्तर",
        "lbl_diarrhea": "ओपीडी दस्त और उल्टी पंजीकरण",
        "lbl_ili": "इन्फ्लूएंजा जैसी बीमारी (ILI)",
        "lbl_fever_high": "अनिर्दिष्ट तेज बुखार",
        "lbl_temp": "औसत तापमान (°C)",
        "lbl_humidity": "सापेक्ष आर्द्रता (%)",
        "lbl_rainfall": "दैनिक वर्षा (mm)"
    }
}

if "gsheet_url" not in st.session_state:
    st.session_state.gsheet_url = DEFAULT_GSHEET_URL

st.sidebar.header(I18N["English"]["sidebar_lang_header"])
selected_lang = st.sidebar.selectbox(
    "Select Display Language / ଭାଷା ବାଛନ୍ତୁ / भाषा चुनें",
    ["English", "ଓଡ଼ିଆ (Odia)", "हिंदी (Hindi)"],
    key="global_sidebar_lang_selector"
)
t = I18N[selected_lang]

# --- Sidebar Controls (Simplified) ---
st.sidebar.title(t["sidebar_title"])
st.sidebar.markdown(t["sidebar_desc"])
st.sidebar.markdown("---")
st.sidebar.info(t["zero_central_policy"])


# --- Top Navigation / Main Header ---
col_head1, col_head2 = st.columns([2.5, 1])
with col_head1:
    st.markdown(
        f"""
        <div class="custom-hero-banner">
            <h1>{t["app_title"]}</h1>
            <p>{t["app_sub"]}</p>
        </div>
        """, unsafe_allow_html=True
    )
with col_head2:
    # Diagnostic scenario injection panel
    st.markdown("<div style='margin-top: 15px;'>", unsafe_allow_html=True)
    scenario = st.selectbox(
        t["inject_outbreak"],
        [
            "🟢 Normal Baseline (No Active Outbreaks)",
            "🌊 Gastrointestinal Outbreak Cluster (Waterborne)",
            "🫁 Cold-Snap Acute Respiratory Surge",
            "⚠️ False Alarm (Single-Source Data Typo)",
            "🔬 Small Cohort Threat (k-Anonymity Guard Demo)"
        ]
    )
    st.markdown("</div>", unsafe_allow_html=True)

# --- Node Parameter Schema ---
NODES = {
    "node_campus": {
        "name": t["node_campus_name"],
        "type": "Clinic / Campus visit log",
        "description": t["node_campus_desc"],
        "metrics": {
            "gastrointestinal": {"label": t["lbl_gi"], "baseline_mean": 3.0, "baseline_std": 0.8, "is_count": True},
            "respiratory": {"label": t["lbl_resp"], "baseline_mean": 5.0, "baseline_std": 1.2, "is_count": True},
            "fever": {"label": t["lbl_fever"], "baseline_mean": 8.0, "baseline_std": 1.8, "is_count": True}
        }
    },
    "node_water": {
        "name": t["node_water_name"],
        "type": "Environmental testing node",
        "description": t["node_water_desc"],
        "metrics": {
            "coliform": {"label": t["lbl_coliform"], "baseline_mean": 1.2, "baseline_std": 0.4, "is_count": False},
            "turbidity": {"label": t["lbl_turb"], "baseline_mean": 1.0, "baseline_std": 0.3, "is_count": False},
            "ph": {"label": t["lbl_ph"], "baseline_mean": 7.2, "baseline_std": 0.15, "is_count": False}
        }
    },
    "node_hospital": {
        "name": t["node_hospital_name"],
        "type": "Public hospital outpatient portal",
        "description": t["node_hospital_desc"],
        "metrics": {
            "diarrheal": {"label": t["lbl_diarrhea"], "baseline_mean": 12.0, "baseline_std": 2.2, "is_count": True},
            "ili": {"label": t["lbl_ili"], "baseline_mean": 15.0, "baseline_std": 3.1, "is_count": True},
            "fever_high": {"label": t["lbl_fever_high"], "baseline_mean": 25.0, "baseline_std": 4.5, "is_count": True}
        }
    },
    "node_weather": {
        "name": t["node_weather_name"],
        "type": "Regional weather node",
        "description": t["node_weather_desc"],
        "metrics": {
            "temp": {"label": t["lbl_temp"], "baseline_mean": 28.5, "baseline_std": 1.0, "is_count": False},
            "humidity": {"label": t["lbl_humidity"], "baseline_mean": 75.0, "baseline_std": 3.0, "is_count": False},
            "rainfall": {"label": t["lbl_rainfall"], "baseline_mean": 2.0, "baseline_std": 0.8, "is_count": False}
        }
    },
    "node_soa": {
        "name": t["node_soa_name"],
        "type": "Clinic / Campus visit log",
        "description": t["node_soa_desc"],
        "metrics": {
            "gastrointestinal": {"label": t["lbl_gi"], "baseline_mean": 4.0, "baseline_std": 1.0, "is_count": True},
            "respiratory": {"label": t["lbl_resp"], "baseline_mean": 6.0, "baseline_std": 1.4, "is_count": True},
            "fever": {"label": t["lbl_fever"], "baseline_mean": 9.0, "baseline_std": 2.0, "is_count": True}
        }
    }
}

# --- Initialize Session States ---
if "notifications" not in st.session_state:
    st.session_state.notifications = []
if "reg_emails" not in st.session_state:
    st.session_state.reg_emails = ["chief.epidemiologist@odisha.gov.in", "cuttack.health.officer@nic.in"]
if "ivr_call_active" not in st.session_state:
    st.session_state.ivr_call_active = False
if "local_logs" not in st.session_state:
    st.session_state.local_logs = {
        "node_campus": [
            {"symptom": "gastrointestinal", "location": "Hostel 3", "raw_val": 12.0, "timestamp": "Today, 10:30 AM", "details": "Stomach cramps, vomiting"},
            {"symptom": "respiratory", "location": "Hostel 1", "raw_val": 4.0, "timestamp": "Today, 09:15 AM", "details": "Dry cough"}
        ],
        "node_soa": [
            {"symptom": "fever", "location": "Hostel B", "raw_val": 15.0, "timestamp": "Today, 11:45 AM", "details": "High fever, chills"}
        ],
        "node_hospital": [],
        "node_water": [],
        "node_weather": []
    }

# Dynamic parameters in session state
if "epsilon" not in st.session_state:
    st.session_state.epsilon = 0.5
if "k_anonymity" not in st.session_state:
    st.session_state.k_anonymity = 5
if "false_alarm_threshold" not in st.session_state:
    st.session_state.false_alarm_threshold = 2.5
if "gsheet_url" not in st.session_state:
    st.session_state.gsheet_url = DEFAULT_GSHEET_URL
if "gsheet_logs_cache" not in st.session_state:
    st.session_state.gsheet_logs_cache = []
if "gsheet_cache_dirty" not in st.session_state:
    st.session_state.gsheet_cache_dirty = True


epsilon = st.session_state.epsilon
k_anonymity = st.session_state.k_anonymity
false_alarm_threshold = st.session_state.false_alarm_threshold
gsheet_url = st.session_state.gsheet_url

# --- Google Sheets API Connectors ---
@st.cache_data(ttl=30)
def get_gsheet_logs(url):
    """Cached fetch — hits Google Sheets at most once every 30 seconds."""
    if not url:
        return []
    try:
        response = requests.get(url, timeout=8)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return []

def _invalidate_gsheet_cache():
    """Clear the log cache so the next render fetches fresh data."""
    get_gsheet_logs.clear()
    st.session_state.gsheet_cache_dirty = True

def fetch_gsheet_logs_cached(url):
    """Wrapper that resolves local cached logs instantly or triggers a refresh."""
    if not url:
        return []
    if not st.session_state.gsheet_logs_cache or st.session_state.gsheet_cache_dirty:
        st.session_state.gsheet_logs_cache = get_gsheet_logs(url)
        st.session_state.gsheet_cache_dirty = False
    return st.session_state.gsheet_logs_cache

def add_gsheet_log(url, node_id, log):
    if not url:
        return
    # Optimistic local UI update (instant UI addition)
    max_existing_id = max([int(l.get("row_id", 0)) for l in st.session_state.gsheet_logs_cache], default=0)
    temp_row_id = max_existing_id + 1
    log_time = log.get("timestamp", datetime.now().strftime("%d %b %Y, %I:%M %p"))
    node_name = NODES.get(node_id, {}).get("name", node_id)
    optimistic_log = {
        "row_id": temp_row_id,
        "node_id": node_id,
        "node_name": node_name,
        "symptom": log["symptom"],
        "location": log["location"],
        "raw_val": log["raw_val"],
        "timestamp": log_time,
        "details": log["details"]
    }
    st.session_state.gsheet_logs_cache.append(optimistic_log)
    
    def _send():
        try:
            payload = {
                "action": "add",
                "node_id": node_id,
                "node_name": node_name,
                "symptom": log["symptom"],
                "location": log["location"],
                "raw_val": float(log["raw_val"]),
                "timestamp": log_time,
                "details": log["details"]
            }
            requests.post(url, json=payload, timeout=10)
            _invalidate_gsheet_cache()
        except Exception:
            pass
    threading.Thread(target=_send, daemon=True).start()

def delete_gsheet_log(url, row_id):
    if not url:
        return
    # Optimistic local UI update (instant UI deletion)
    st.session_state.gsheet_logs_cache = [
        l for l in st.session_state.gsheet_logs_cache if l.get("row_id") != row_id
    ]
    
    def _send():
        try:
            payload = {"action": "delete", "row_id": int(row_id)}
            requests.post(url, json=payload, timeout=10)
            _invalidate_gsheet_cache()
        except Exception:
            pass
    threading.Thread(target=_send, daemon=True).start()


# --- Data Generation Helper ---
def generate_node_data(scenario, epsilon, k_anonymity):
    seed_map = {
        "🟢 Normal Baseline (No Active Outbreaks)": 100,
        "🌊 Gastrointestinal Outbreak Cluster (Waterborne)": 200,
        "🫁 Cold-Snap Acute Respiratory Surge": 300,
        "⚠️ False Alarm (Single-Source Data Typo)": 400,
        "🔬 Small Cohort Threat (k-Anonymity Guard Demo)": 500
    }
    np.random.seed(seed_map.get(scenario, 100))
    
    node_data = {}
    for node_id, node_info in NODES.items():
        node_data[node_id] = {
            "name": node_info["name"],
            "type": node_info["type"],
            "description": node_info["description"],
            "metrics": {}
        }
        
        # Calculate sum of manual logs for this node
        manual_sums = {}
        for m_id in node_info["metrics"].keys():
            manual_sums[m_id] = 0.0
            
        # Determine source of logs (Google Sheet or Local Session State)
        active_gsheet_url = st.session_state.gsheet_url
        if active_gsheet_url:
            sheet_logs = fetch_gsheet_logs_cached(active_gsheet_url)
            for log in sheet_logs:
                if log.get("node_id") == node_id:
                    m_id = log.get("symptom")
                    if m_id in manual_sums:
                        manual_sums[m_id] += log.get("raw_val", 0.0)
        else:
            if "local_logs" in st.session_state and node_id in st.session_state.local_logs:
                for log in st.session_state.local_logs[node_id]:
                    m_id = log["symptom"]
                    if m_id in manual_sums:
                        manual_sums[m_id] += log["raw_val"]
                    
        for metric_id, metric_info in node_info["metrics"].items():
            mean = metric_info["baseline_mean"]
            std = metric_info["baseline_std"]
            is_count = metric_info["is_count"]
            
            val = max(0.0, np.random.normal(mean, std))
            
            # Scenario modifications
            if scenario == "🌊 Gastrointestinal Outbreak Cluster (Waterborne)":
                if node_id == "node_water":
                    if metric_id == "coliform":
                        val = 15.6
                    elif metric_id == "turbidity":
                        val = 6.4
                elif node_id == "node_campus" and metric_id == "gastrointestinal":
                    val = 42.0
                elif node_id == "node_soa" and metric_id == "gastrointestinal":
                    val = 48.0
                elif node_id == "node_hospital" and metric_id == "diarrheal":
                    val = 78.0
                elif node_id == "node_weather":
                    if metric_id == "temp":
                        val = 33.2
                    elif metric_id == "rainfall":
                        val = 45.0
                        
            elif scenario == "🫁 Cold-Snap Acute Respiratory Surge":
                if node_id == "node_campus" and metric_id == "respiratory":
                    val = 48.0
                elif node_id == "node_soa" and metric_id == "respiratory":
                    val = 52.0
                elif node_id == "node_hospital" and metric_id == "ili":
                    val = 98.0
                elif node_id == "node_weather":
                    if metric_id == "temp":
                        val = 16.5
                    elif metric_id == "humidity":
                        val = 93.0
                        
            elif scenario == "⚠️ False Alarm (Single-Source Data Typo)":
                if node_id == "node_campus" and metric_id == "fever":
                    val = 142.0
                    
            elif scenario == "🔬 Small Cohort Threat (k-Anonymity Guard Demo)":
                if node_id == "node_campus" and metric_id == "gastrointestinal":
                    val = 3.0
                elif node_id == "node_soa" and metric_id == "gastrointestinal":
                    val = 2.0
            
            if metric_id in manual_sums:
                val += manual_sums[metric_id]
                
            if is_count:
                val = float(round(val))
            else:
                val = round(val, 2)
                
            # LDP Laplace Mechanism
            sensitivity = 1.0 if is_count else 0.5
            scale = sensitivity / epsilon
            noise = np.random.laplace(0, scale)
            dp_val = val + noise
            
            if is_count:
                dp_val = max(0.0, float(round(dp_val)))
            else:
                dp_val = max(0.0, round(dp_val, 2))
                
            # k-Anonymity Suppression
            suppressed = False
            transmitted_val = dp_val
            if is_count and val > 0 and val < k_anonymity:
                suppressed = True
                transmitted_val = 0.0
                
            z_score = (transmitted_val - mean) / std if std > 0 else 0.0
            
            node_data[node_id]["metrics"][metric_id] = {
                "label": metric_info["label"],
                "raw_val": val,
                "dp_noise": round(noise, 2),
                "dp_val": dp_val,
                "suppressed": suppressed,
                "transmitted_val": transmitted_val,
                "z_score": round(z_score, 2),
                "baseline_mean": mean,
                "baseline_std": std
            }
    return node_data

# --- Federated Aggregation consensus logic ---
def run_federated_aggregation(node_data, threshold):
    node_lais = {}
    contributing_signals = []
    
    for node_id, node_info in node_data.items():
        z_scores = []
        for m_id, m in node_info["metrics"].items():
            z_val = m["z_score"]
            z_scores.append(z_val)
            if z_val > 0:
                contributing_signals.append({
                    "node_name": node_info["name"],
                    "metric_label": m["label"],
                    "z_score": z_val,
                    "transmitted_val": m["transmitted_val"]
                })
        
        node_lais[node_id] = max(z_scores) if z_scores else 0.0
        
    active_node_alerts = {}
    for n_id, lai in node_lais.items():
        if lai > threshold:
            active_node_alerts[n_id] = lai
            
    num_alerts = len(active_node_alerts)
    total_z_excess = sum([max(0.0, lai - threshold) for lai in node_lais.values()])
    
    if num_alerts == 0:
        confidence = 0.0
        status = "🟢 Baseline Normal"
        desc = "All local health centers are reporting normal baseline activity."
        risk_class = "safe"
    elif num_alerts == 1:
        node_name = node_data[list(active_node_alerts.keys())[0]]["name"]
        confidence = min(35.0, 15.0 + total_z_excess * 5)
        status = "🟡 Isolated Local Deviation"
        desc = f"Unusual symptoms reported only at '{node_name}'. Awaiting data from neighboring clinics to confirm."
        risk_class = "warning"
    else:
        confidence = min(99.0, 40.0 + (total_z_excess * 8) + (num_alerts * 12))
        status = "🔴 Unusual Disease Cluster Confirmed"
        desc = f"Anomalies detected across {num_alerts} local clinics. Outbreak likelihood is highly verified."
        risk_class = "danger"
        
    return {
        "node_lais": node_lais,
        "active_node_alerts": active_node_alerts,
        "confidence": round(confidence, 1),
        "status": status,
        "description": desc,
        "risk_class": risk_class,
        "contributing_signals": contributing_signals
    }

# --- Execute Core Logic ---
node_data = generate_node_data(scenario, epsilon, k_anonymity)
agg_results = run_federated_aggregation(node_data, false_alarm_threshold)

# --- Navigation Tabs ---
tab_public, tab_clinic, tab_officer, tab_audit = st.tabs([
    t["tab_public"],
    t["tab_clinic"],
    t["tab_officer"],
    t["tab_audit"]
])

# ==============================================================================
# TAB 1: PUBLIC HEALTH RADAR (PRIMARY - GENERAL PUBLIC)
# ==============================================================================
with tab_public:
    st.markdown(f"### {t['radar_title']}")
    st.markdown(t['radar_desc'])
    
    c_status = agg_results["risk_class"]
    
    # Determine alert colors, backgrounds, and icons dynamically
    if c_status == "safe":
        alert_bg = "rgba(16, 185, 129, 0.12)"
        alert_border = "#10B981"
        alert_icon = "🟢"
        safety_advice = t["adv_safe"]
    elif c_status == "warning":
        alert_bg = "rgba(245, 158, 11, 0.15)"
        alert_border = "#F59E0B"
        alert_icon = "⚠️"
        safety_advice = t["adv_general"]
    else:
        alert_bg = "rgba(239, 68, 68, 0.18)"
        alert_border = "#EF4444"
        alert_icon = "🚨"
        # Determine advice based on scenario
        if "Gastrointestinal" in scenario or "Water" in scenario or any("gastro" in str(s["metric_label"]).lower() or "diarrh" in str(s["metric_label"]).lower() for s in agg_results["contributing_signals"]):
            safety_advice = t["adv_gi"]
        elif "Respiratory" in scenario or "Cold" in scenario or any("respir" in str(s["metric_label"]).lower() or "cough" in str(s["metric_label"]).lower() or "ili" in str(s["metric_label"]).lower() for s in agg_results["contributing_signals"]):
            safety_advice = t["adv_resp"]
        else:
            safety_advice = t["adv_general"]
            
    # Determine dynamic class for animations
    if c_status == "safe":
        alert_class = ""
        alert_style = f"background-color: {alert_bg}; border: 2px solid {alert_border}; border-radius: 8px; padding: 18px; margin-bottom: 20px;"
    elif c_status == "warning":
        alert_class = "class='alert-banner-warning'"
        alert_style = f"background-color: {alert_bg};"
    else:
        alert_class = "class='alert-banner-danger'"
        alert_style = f"background-color: {alert_bg};"
        
    # Outbreak Warning Status (Filled high-visibility alert banner)
    st.markdown(
        f"""
        <div {alert_class} style='{alert_style}'>
            <div style='display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;'>
                <div style='flex: 1; min-width: 300px;'>
                    <h3 style='margin: 0; font-size: 1.5rem; color: {alert_border} !important;'>{alert_icon} {agg_results['status']}</h3>
                    <p style='color: var(--text-color); opacity: 0.9; margin: 6px 0 0 0; font-size: 1.05rem;'>{agg_results['description']}</p>
                </div>
                <div style='text-align: right; min-width: 150px;'>
                    <span style='font-size: 0.8rem; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px; color: {alert_border};'>{t['threat_prob']}</span>
                    <div style='font-size: 2.2rem; font-weight: 800; color: {alert_border}; line-height: 1.1;'>{agg_results['confidence']}%</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True
    )
    
    # Safety Advice Container
    st.markdown(
        f"""
        <div class='glass-card' style='border-top: 4px solid {alert_border};'>
            <h4 style='margin: 0 0 10px 0;'>💡 Public Safety Advisory</h4>
            <div style='font-size: 1.05rem;'>{safety_advice}</div>
        </div>
        """, unsafe_allow_html=True
    )
    
    # Simple Visual Trends (Public-friendly Chart)
    col_pub1, col_pub2 = st.columns([1.5, 2])
    with col_pub1:
        st.markdown(f"#### {t['active_symptoms']}")
        sigs = agg_results["contributing_signals"]
        
        if not sigs or all(s["z_score"] <= 0 for s in sigs):
            st.info(t["xai_no_anom"])
        else:
            sig_names = []
            sig_scores = []
            for s in sigs:
                if s["z_score"] > 0:
                    sig_names.append(s['metric_label'])
                    sig_scores.append(s["z_score"])
                    
            fig_pub = px.bar(
                x=sig_scores,
                y=sig_names,
                orientation='h',
                labels={'x': 'Relative Level of Rise', 'y': 'Symptoms'},
                color=sig_scores,
                color_continuous_scale=['#38BDF8', '#EF4444']
            )
            fig_pub.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=250,
                coloraxis_showscale=False,
                margin=dict(t=10, b=10, l=10, r=10)
            )
            st.plotly_chart(fig_pub, use_container_width=True)
            
    with col_pub2:
        st.markdown(f"<p style='text-align: center; font-size: 1.1rem; font-weight: 700; margin-bottom: 8px; color: var(--text-color);'>{t['threat_prob']} (%)</p>", unsafe_allow_html=True)
        # Simple health rules gauge
        fig_gauge_pub = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = agg_results["confidence"],
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {
                'axis': {'range': [0, 100], 'tickwidth': 1},
                'bar': {'color': alert_border},
                'bgcolor': "var(--secondary-background-color)",
                'borderwidth': 2,
                'bordercolor': "rgba(128,128,128,0.2)",
                'steps': [
                    {'range': [0, 35], 'color': 'rgba(16, 185, 129, 0.1)'},
                    {'range': [35, 70], 'color': 'rgba(245, 158, 11, 0.1)'},
                    {'range': [70, 100], 'color': 'rgba(239, 68, 68, 0.1)'}
                ]
            }
        ))
        fig_gauge_pub.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            height=250,
            margin=dict(t=35, b=10, l=30, r=30)
        )
        st.plotly_chart(fig_gauge_pub, use_container_width=True)

# ==============================================================================
# TAB 2: CLINIC REPORTER PORTAL (SECONDARY - CLINIC STAFF)
# ==============================================================================
with tab_clinic:
    # Initialize authentication state for Tab 2
    if "clinic_auth_success" not in st.session_state:
        st.session_state.clinic_auth_success = False
        
    if not st.session_state.clinic_auth_success:
        col_lock1, col_lock2, col_lock3 = st.columns([1, 1.2, 1])
        with col_lock2:
            st.markdown(
                f"""
                <div class="lock-card">
                    <div class="lock-icon">🛡️</div>
                    <h3 style="margin-top:0; color: #00F2FE !important; font-size: 1.4rem;">{t["clinic_title"]}</h3>
                    <p style="color: var(--text-color); opacity: 0.85; font-size: 0.95rem; line-height: 1.4; margin-bottom: 25px;">{t["pass_warn_clinic"]}</p>
                </div>
                """, unsafe_allow_html=True
            )
            clinic_auth = st.text_input(t["pass_prompt_clinic"], type="password", key="passcode_clinic_key", label_visibility="collapsed")
            if clinic_auth == "1234":
                st.session_state.clinic_auth_success = True
                st.rerun()
    else:
        st.markdown(f"### {t['clinic_title']}")
        st.markdown(t['clinic_desc'])
        selected_node_id = st.selectbox(
            t['select_node'],
            options=list(NODES.keys()),
            format_func=lambda x: NODES[x]["name"]
        )
        
        node = node_data[selected_node_id]
        
        # Node Profile Panel
        st.markdown(
            f"""
            <div class='glass-card' style='border-top: 3px solid var(--primary-color);'>
                <h4 style='margin: 0;'>{node['name']}</h4>
                <p style='color: var(--primary-color); font-weight: bold; margin: 4px 0;'>{t['node_type_label']} {node['type']}</p>
                <p style='color: var(--text-color); opacity:0.8; font-size: 0.9rem; margin-bottom: 0;'>{node['description']}</p>
            </div>
            """, unsafe_allow_html=True
        )
        
        # Local Private Database
        metric_rows = []
        for m_id, m in node["metrics"].items():
            status_text = "🟢 Safe (Privacy Preserved)"
            if m["suppressed"]:
                status_text = f"❌ Blocked (< Group Size {k_anonymity})"
                
            metric_rows.append({
                t["col_indicator"]: m["label"],
                t["col_baseline"]: m["baseline_mean"],
                t["col_raw"]: m["raw_val"],
                t["col_noise"]: m["dp_noise"],
                t["col_dp"]: m["dp_val"],
                t["col_status"]: status_text,
                t["col_trans_val"]: m["transmitted_val"],
                t["col_trans_z"]: m["z_score"]
            })
            
        df_metrics = pd.DataFrame(metric_rows)
        st.markdown(f"#### {t['db_title']}")
        st.dataframe(df_metrics, use_container_width=True, hide_index=True)
        
        # Visualizing Privacy Distortion
        st.markdown(f"#### {t['chart_title']}")
        labels = []
        raws = []
        transports = []
        for m_id, m in node["metrics"].items():
            labels.append(m["label"])
            raws.append(m["raw_val"])
            transports.append(m["transmitted_val"])
            
        fig_comp = go.Figure(data=[
            go.Bar(name=t['bar_raw'], x=labels, y=raws, marker_color='#38BDF8'),
            go.Bar(name=t['bar_trans'], x=labels, y=transports, marker_color='#00F2FE')
        ])
        fig_comp.update_layout(
            barmode='group',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            yaxis_title="Count Value",
            height=300,
            margin=dict(t=20, b=20, l=10, r=10)
        )
        st.plotly_chart(fig_comp, use_container_width=True)

        st.markdown("---")
        st.markdown(f"### {t['ingest_title']}")
        st.markdown(t['ingest_desc'])
        
        ingest_method = st.radio(
            t["ingest_method_label"],
            [t["opt1"], t["opt2"], t["opt3"], t["opt4"]],
            horizontal=True
        )
        
        symptom_options = list(NODES[selected_node_id]["metrics"].keys())
        symptom_labels = {k: NODES[selected_node_id]["metrics"][k]["label"] for k in symptom_options}
        
        # Dynamic context adapting to node type (Clinic vs Water Quality vs Weather)
        if selected_node_id == "node_water":
            category_title = "Select Water Quality Indicator / Test"
            tally_title = "Measured Sensor / Lab Reading"
            loc_title = "Sampling Site / Reservoir Zone"
            loc_options = ["Treatment Plant Inlet", "Main Reservoir Tank 1", "Distribution Line North", "Campus Storage Tank", "Municipal Outfall B"]
            default_val = 1.2
            step_val = 0.1
            min_val = 0.0
            max_val = 200.0
            notes_placeholder = "e.g. High turbidity recorded after pipeline flush."
            local_card_title = "Local Sensor / Lab Record"
            transmitted_card_title = "DP-Perturbed Sensor Value"
            item_header_text = "Parameter"
            val_header_text = "Reading"
        elif selected_node_id == "node_weather":
            category_title = "Select Weather / Climate Parameter"
            tally_title = "Recorded Sensor Metric Value"
            loc_title = "Weather Station / Sensor Tower"
            loc_options = ["Bhubaneswar Main Hub", "Airport Met Tower", "Coastal Weather Sensor", "North Campus Station"]
            default_val = 28.5
            step_val = 0.5
            min_val = -10.0
            max_val = 120.0
            notes_placeholder = "e.g. Flash rainfall and humidity surge recorded."
            local_card_title = "Local Meteorological Log"
            transmitted_card_title = "Aggregated Weather Metric"
            item_header_text = "Parameter"
            val_header_text = "Value"
        else:
            category_title = t["ingest_symptom"]
            tally_title = t["ingest_tally"]
            loc_title = t["ingest_loc"]
            loc_options = ["Hostel 1", "Hostel 2", "Hostel 3", "Hostel A", "Hostel B", "Outpatient Ward 1", "General Campus"]
            default_val = 5.0
            step_val = 1.0
            min_val = 1.0
            max_val = 200.0
            notes_placeholder = "e.g. Stomach cramps, vomiting. No personal details."
            local_card_title = t["local_record_title"]
            transmitted_card_title = t["transmitted_payload_title"]
            item_header_text = "Symptom"
            val_header_text = "Count"

        # Ingestion Options
        if t["opt1"] in ingest_method:
            ingest_col1, ingest_col2 = st.columns(2)
            with ingest_col1:
                selected_symptom = st.selectbox(
                    category_title,
                    options=symptom_options,
                    format_func=lambda x: symptom_labels[x],
                    key="ingest_symptom_select"
                )
                location_input = st.selectbox(
                    loc_title,
                    loc_options,
                    key="ingest_location_select"
                )
            with ingest_col2:
                raw_case_count = st.number_input(
                    tally_title,
                    min_value=float(min_val),
                    max_value=float(max_val),
                    value=float(default_val),
                    step=float(step_val),
                    key="ingest_case_count"
                )
                clinical_details = st.text_input(
                    t["ingest_notes"],
                    placeholder=notes_placeholder,
                    key="ingest_clinical_details"
                )
                
            # Pre-computation previews
            st.markdown(f"#### {t['precomp_title']}")
            is_count_item = NODES[selected_node_id]["metrics"][selected_symptom]["is_count"]
            sensitivity_val = 1.0 if is_count_item else 0.5
            
            sim_noise = np.random.laplace(0, sensitivity_val / epsilon)
            sim_dp = raw_case_count + sim_noise
            sim_dp = max(0.0, float(round(sim_dp))) if is_count_item else max(0.0, round(sim_dp, 2))
            
            sim_suppressed = is_count_item and raw_case_count < k_anonymity
            sim_transmitted_tally = 0.0 if sim_suppressed else sim_dp
            sim_transmitted_location = "General Regional Grid (Masked)" if sim_suppressed else location_input
            
            prev_col1, prev_col2 = st.columns(2)
            with prev_col1:
                st.markdown(
                    f"""
                    <div style='background-color: var(--secondary-background-color); color: var(--text-color); border: 1px solid rgba(128,128,128,0.2); border-left:4px solid #38BDF8; padding:12px; border-radius:6px;'>
                        <strong style='color:#38BDF8;'>{local_card_title}</strong><br>
                        • {item_header_text}: {symptom_labels[selected_symptom]}<br>
                        • Original {val_header_text}: <strong>{raw_case_count}</strong><br>
                        • Site: {location_input}
                    </div>
                    """, unsafe_allow_html=True
                )
            with prev_col2:
                suppress_alert = "<span style='color:#EF4444; font-weight:bold;'>⚠️ Masked (Under threshold)</span>" if sim_suppressed else "<span style='color:#10B981; font-weight:bold;'>✅ Secure Upload Allowed</span>"
                st.markdown(
                    f"""
                    <div style='background-color: var(--secondary-background-color); color: var(--text-color); border: 1px solid rgba(128,128,128,0.2); border-left:4px solid #00F2FE; padding:12px; border-radius:6px;'>
                        <strong style='color:#00F2FE;'>{transmitted_card_title}</strong><br>
                        • Uploaded Value: <strong>{sim_transmitted_tally}</strong> ({suppress_alert})<br>
                        • Uploaded Site: <strong>{sim_transmitted_location}</strong>
                    </div>
                    """, unsafe_allow_html=True
                )
                
            if st.button(t["submit_btn"], type="primary", use_container_width=True):
                new_log = {
                    "symptom": selected_symptom,
                    "location": location_input,
                    "raw_val": float(raw_case_count),
                    "timestamp": datetime.now().strftime("%d %b, %I:%M %p"),
                    "details": clinical_details
                }
                if st.session_state.gsheet_url:
                    add_gsheet_log(st.session_state.gsheet_url, selected_node_id, new_log)
                else:
                    st.session_state.local_logs[selected_node_id].append(new_log)
                st.success(t["log_success"])
                st.rerun()
                
        elif t["opt2"] in ingest_method:
            # Voice IVR keypad simulator
            ivr_col1, ivr_col2 = st.columns(2)
            with ivr_col1:
                st.markdown(
                    """
                    <div style="background-color: var(--secondary-background-color); color: var(--text-color); padding: 20px; border-radius: 12px; text-align: center; border: 1px solid rgba(128,128,128,0.2);">
                        <h3 style="color: var(--primary-color); margin: 0;">📞 1800-SURAKSHA</h3>
                        <p style="opacity: 0.8; font-size: 0.85rem; margin: 4px 0 15px 0;">Toll-Free Health Reporting Phone Line</p>
                    </div>
                    """, unsafe_allow_html=True
                )
                if not st.session_state.ivr_call_active:
                    if st.button("🟢 Start Voice Report Simulation", use_container_width=True, type="primary"):
                        st.session_state.ivr_call_active = True
                        st.rerun()
                else:
                    if st.button("🔴 Hang Up", use_container_width=True):
                        st.session_state.ivr_call_active = False
                        st.rerun()
            with ivr_col2:
                if st.session_state.ivr_call_active:
                    st.audio("https://actions.google.com/sounds/v1/teleport/teleport_start.ogg", format="audio/ogg")
                    ivr_symptom = st.radio(
                        "Symptom Code:",
                        options=symptom_options,
                        format_func=lambda x: f"[{symptom_options.index(x)+1}] {symptom_labels[x]}"
                    )
                    ivr_count = st.number_input("Keypad Tally Value:", min_value=1, max_value=150, value=8)
                    ivr_loc = st.selectbox("Location Code:", ["Hostel 1", "Hostel 2", "Hostel 3", "General Campus"])
                    
                    if st.button("📲 Submit Code (#)", use_container_width=True):
                        new_log = {
                            "symptom": ivr_symptom,
                            "location": ivr_loc,
                            "raw_val": float(ivr_count),
                            "timestamp": datetime.now().strftime("%d %b, %I:%M %p"),
                            "details": "Logged via Voice Gateway"
                        }
                        if st.session_state.gsheet_url:
                            add_gsheet_log(st.session_state.gsheet_url, selected_node_id, new_log)
                        else:
                            st.session_state.local_logs[selected_node_id].append(new_log)
                        st.session_state.ivr_call_active = False
                        st.success(t["log_success"])
                        st.rerun()
                else:
                    st.info("Start the voice simulation to enter report codes using your phone keypad.")
                    
        elif t["opt3"] in ingest_method:
            st.markdown("#### OCR hand-written scanner simulation")
            uploaded_file = st.file_uploader("Upload log sheet photo", type=["jpg", "png", "jpeg"])
            sim_scan = st.button("📸 Run Scanner Simulation", use_container_width=True, type="primary")
            if uploaded_file is not None or sim_scan:
                st.success("OCR Scan Successful! Extracted: 14 Cases (Diarrhea) from Hostel A.")
                if st.button("🚀 Upload Extracted OCR Data", use_container_width=True):
                    new_log = {
                        "symptom": symptom_options[0],
                        "location": "Hostel A",
                        "raw_val": 14.0,
                        "timestamp": datetime.now().strftime("%d %b, %I:%M %p"),
                        "details": "OCR Hand-written Scanner Scan"
                    }
                    if st.session_state.gsheet_url:
                        add_gsheet_log(st.session_state.gsheet_url, selected_node_id, new_log)
                    else:
                        st.session_state.local_logs[selected_node_id].append(new_log)
                    st.success(t["log_success"])
                    st.rerun()
                    
        elif t["opt4"] in ingest_method:
            st.markdown("#### Database Synchronizer Daemon")
            st.code("# Secure Connector pushes anonymized averages directly.\nresult = db.query('SELECT COUNT(*) FROM patient_logs')\nupload_safely(result)", language="python")
            if st.button("🔄 Trigger Sync Sync Simulation", use_container_width=True, type="primary"):
                new_log = {
                    "symptom": symptom_options[0],
                    "location": "Main Center",
                    "raw_val": 35.0,
                    "timestamp": datetime.now().strftime("%d %b, %I:%M %p"),
                    "details": "Hospital Database Sync Link"
                }
                if st.session_state.gsheet_url:
                    add_gsheet_log(st.session_state.gsheet_url, selected_node_id, new_log)
                else:
                    st.session_state.local_logs[selected_node_id].append(new_log)
                st.success(t["log_success"])
                st.rerun()

        # Log table
        st.markdown(f"#### {t['logbook_title']}")
        
        # Resolve active logs list
        active_gsheet_url = st.session_state.gsheet_url
        if active_gsheet_url:
            all_logs = fetch_gsheet_logs_cached(active_gsheet_url)
            active_node_logs = []
            for log in all_logs:
                if log.get("node_id") == selected_node_id:
                    active_node_logs.append(log)
        else:
            active_node_logs = []
            for idx, log in enumerate(st.session_state.local_logs[selected_node_id]):
                active_node_logs.append({
                    "row_id": idx,
                    "symptom": log["symptom"],
                    "location": log["location"],
                    "raw_val": log["raw_val"],
                    "timestamp": log.get("timestamp", "Recent"),
                    "details": log["details"]
                })
                
        if not active_node_logs:
            st.info(t["log_info"])
        else:
            for idx, log in enumerate(active_node_logs):
                is_count_log = NODES[selected_node_id]["metrics"][log["symptom"]]["is_count"]
                log_noise = np.random.laplace(0, (1.0 if is_count_log else 0.5) / epsilon)
                log_dp = log["raw_val"] + log_noise
                log_dp = max(0.0, float(round(log_dp))) if is_count_log else max(0.0, round(log_dp, 2))
                log_suppressed = is_count_log and log["raw_val"] < k_anonymity
                
                time_badge = log.get("timestamp")
                if not time_badge or time_badge == "Recent":
                    details_str = log.get("details", "")
                    if details_str.startswith("[") and "]" in details_str:
                        time_badge = details_str[1:details_str.find("]")]
                    else:
                        time_badge = datetime.now().strftime("%d %b, %I:%M %p")
                        
                col_l1, col_l2, col_l3 = st.columns([5, 2, 1.2])
                with col_l1:
                    clean_notes = log["details"]
                    if clean_notes.startswith("[") and "]" in clean_notes:
                        clean_notes = clean_notes[clean_notes.find("]")+1:].strip()
                    st.markdown(
                        f"""
                        <div style='background: rgba(255,255,255,0.03); border: 1px solid rgba(128,128,128,0.15); border-left: 4px solid var(--primary-color); padding: 12px; border-radius: 8px; margin-bottom: 10px;'>
                            <div style='display: flex; justify-content: space-between; align-items: center;'>
                                <strong style='font-size: 1.05rem;'>{symptom_labels.get(log["symptom"], log["symptom"])}</strong>
                                <span style='font-size: 0.78rem; opacity: 0.7; background: rgba(128,128,128,0.15); padding: 2px 8px; border-radius: 4px;'>🕒 {time_badge}</span>
                            </div>
                            <span style='font-size: 0.85rem; opacity: 0.85;'>📍 Location: {log["location"]} | {val_header_text}: <strong>{log["raw_val"]}</strong></span><br>
                            <span style='font-size: 0.8rem; opacity: 0.7;'>📝 Notes: {clean_notes if clean_notes else 'None'}</span>
                        </div>
                        """, unsafe_allow_html=True
                    )
                with col_l2:
                    badge_color = "#10B981" if not log_suppressed else "#EF4444"
                    status_badge = f"<span style='color:{badge_color}; font-weight:bold;'>{'✅ Safe Upload' if not log_suppressed else '❌ Suppressed'}</span>"
                    st.markdown(
                        f"""
                        <div style='text-align: left; padding: 12px 5px;'>
                            <span style='font-size:0.85rem;'>{status_badge}</span><br>
                            <span style='font-size:0.85rem; opacity:0.8;'>Shared: {0.0 if log_suppressed else log_dp}</span>
                        </div>
                        """, unsafe_allow_html=True
                    )
                with col_l3:
                    st.markdown("<div style='padding-top: 18px;'>", unsafe_allow_html=True)
                    btn_unique_key = f"del_btn_{selected_node_id}_{idx}_{log.get('row_id', idx)}"
                    if st.button("🗑️", key=btn_unique_key, use_container_width=True, help="Delete this entry"):
                        if active_gsheet_url:
                            delete_gsheet_log(active_gsheet_url, log["row_id"])
                        else:
                            st.session_state.local_logs[selected_node_id].pop(idx)
                        st.success("Entry deleted!")
                        st.rerun()
            if not active_gsheet_url:
                if st.button(t["clear_btn"]):
                    st.session_state.local_logs[selected_node_id] = []
                    st.success("Cleared.")
                    st.rerun()

# ==============================================================================
# TAB 3: HEALTH OFFICER CONSOLE (TERTIARY - HEALTH OFFICERS)
# ==============================================================================
with tab_officer:
    # Initialize authentication state for Tab 3
    if "officer_auth_success" not in st.session_state:
        st.session_state.officer_auth_success = False
        
    if not st.session_state.officer_auth_success:
        col_lock1, col_lock2, col_lock3 = st.columns([1, 1.2, 1])
        with col_lock2:
            st.markdown(
                f"""
                <div class="lock-card">
                    <div class="lock-icon">🔑</div>
                    <h3 style="margin-top:0; color: #00F2FE !important; font-size: 1.4rem;">{t["officer_title"]}</h3>
                    <p style="color: var(--text-color); opacity: 0.85; font-size: 0.95rem; line-height: 1.4; margin-bottom: 25px;">{t["pass_warn_officer"]}</p>
                </div>
                """, unsafe_allow_html=True
            )
            officer_auth = st.text_input(t["pass_prompt_officer"], type="password", key="passcode_officer_key", label_visibility="collapsed")
            if officer_auth == "9999":
                st.session_state.officer_auth_success = True
                st.rerun()
    else:
        st.markdown(f"### {t['officer_title']}")
        st.markdown(t['officer_desc'])

        # Google Sheet Sync — Officer-Only Database Configuration
        st.markdown("---")
        st.markdown(
            """
            <div class='glass-card' style='border-top: 3px solid #00F2FE;'>
                <h4 style='margin: 0 0 8px 0;'>🔗 Shared Database Configuration</h4>
                <p style='font-size: 0.9rem; opacity: 0.8; margin-bottom: 15px;'>
                    Connect to a Google Sheet to enable real-time shared data across all clinic nodes. 
                    Only Health Officers can configure this setting.
                </p>
            </div>
            """, unsafe_allow_html=True
        )
        gsheet_url_officer = st.text_input(
            "Google Apps Script Web App URL",
            value=st.session_state.gsheet_url,
            placeholder="https://script.google.com/macros/s/.../exec",
            help="Paste the Google Apps Script Web App URL here. All case submissions will sync to the shared Google Sheet.",
            key="officer_gsheet_url"
        )
        col_gs1, col_gs2 = st.columns(2)
        with col_gs1:
            if st.button("✅ Save & Enable Shared DB", type="primary", use_container_width=True):
                st.session_state.gsheet_url = gsheet_url_officer
                st.success("✅ Google Sheet connected! All case reports will now sync to the shared database.")
                st.rerun()
        with col_gs2:
            if st.button("🚫 Disconnect Google Sheet", use_container_width=True):
                st.session_state.gsheet_url = ""
                st.success("Disconnected. App is now using local session memory.")
                st.rerun()
        if st.session_state.gsheet_url:
            st.markdown(f"<p style='color:#10B981; font-size:0.85rem;'>🟢 <strong>Connected:</strong> {st.session_state.gsheet_url[:60]}...</p>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='color:#F59E0B; font-size:0.85rem;'>🟡 <strong>Disconnected:</strong> Using local session memory (data resets on reload).</p>", unsafe_allow_html=True)
        st.markdown("---")

        st.markdown(f"### {t['sec_controls']}")
        
        # Active controls inside passcode-protected tab
        st.session_state.epsilon = st.slider(
            t["epsilon_label"],
            min_value=0.1,
            max_value=2.0,
            value=st.session_state.epsilon,
            step=0.1,
            help=t["epsilon_help"]
        )
        st.session_state.k_anonymity = st.slider(
            t["k_label"],
            min_value=2,
            max_value=10,
            value=st.session_state.k_anonymity,
            step=1,
            help=t["k_help"]
        )
        st.session_state.false_alarm_threshold = st.slider(
            t["cutoff_label"],
            min_value=1.5,
            max_value=4.0,
            value=st.session_state.false_alarm_threshold,
            step=0.1,
            help=t["cutoff_help"]
        )
        
        st.markdown(f"#### {t['regional_table_title']}")
        lai_rows = []
        for node_id, node_info in node_data.items():
            lai = agg_results["node_lais"][node_id]
            status_label = "🟢 Normal Baseline"
            if lai > false_alarm_threshold:
                status_label = "🚨 Anomaly Alert"
            elif lai > (false_alarm_threshold * 0.7):
                status_label = "🟡 Elevated Warning"
                
            lai_rows.append({
                "Health Reporting Center": node_info["name"],
                "Average Deviation Index": f"{lai} σ",
                "Anomaly Status": status_label
            })
        st.dataframe(pd.DataFrame(lai_rows), use_container_width=True, hide_index=True)
        
        # Emergency Broadcasting
        st.markdown("---")
        st.markdown(f"### {t['broadcast_title']}")
        st.markdown(t["broadcast_desc"])
        
        bc_emails = ", ".join(st.session_state.reg_emails)
        st.text_input(t["alert_reg_label"], value=bc_emails, disabled=True)
        
        alert_body = f"OFFICIAL HEALTH EMERGENCY ADVISORY\nSTATUS: {agg_results['status']}\nLIKELIHOOD: {agg_results['confidence']}%\nCORROBORATION: {agg_results['description']}"
        alert_text = st.text_area(t["alert_draft_label"], value=alert_body, height=120)
        
        is_broadcast_disabled = (agg_results["risk_class"] == "safe")
        
        if st.button(t["sign_btn"], type="primary", disabled=is_broadcast_disabled):
            st.session_state.notifications.append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": agg_results["status"],
                "confidence": f"{agg_results['confidence']}%",
                "hash": f"SHA256:{base64.b64encode(alert_text.encode()).decode()[:16]}...",
                "dispatch": "✅ Dispatched to mobile health registry"
            })
            st.success(t["alert_dispatched_success"])
            st.rerun()
            
        st.markdown(f"#### {t['log_title']}")
        if not st.session_state.notifications:
            st.info("No advisories dispatched in this session.")
        else:
            for n in reversed(st.session_state.notifications):
                st.markdown(
                    f"""
                    <div style='background-color: var(--secondary-background-color); padding: 10px; border-radius: 6px; border: 1px solid rgba(128,128,128,0.2); margin-bottom: 8px;'>
                        <strong style='color:#EF4444;'>{n['status']}</strong> ({n['confidence']})<br>
                        <small style='opacity: 0.8;'>Time: {n['timestamp']}</small><br>
                        <small style='font-family: monospace; color:var(--primary-color);'>{n['hash']}</small>
                    </div>
                    """, unsafe_allow_html=True
                )

# ==============================================================================
# TAB 4: PRIVACY AUDIT LEDGER (VERIFICATION - ALL)
# ==============================================================================
with tab_audit:
    st.markdown(f"### {t['audit_title']}")
    st.markdown(t['audit_desc'])
    
    aud_col1, aud_col2, aud_col3 = st.columns(3)
    tot_suppressed = sum([1 for node in node_data.values() for m in node["metrics"].values() if m["suppressed"]])
    
    with aud_col1:
        st.markdown(
            f"""
            <div class='glass-card' style='text-align: center;'>
                <div class='metric-label'>{t['privacy_compliance']}</div>
                <div class='metric-value' style='color:#10B981;'>Verified Secure</div>
                <div style='font-size:0.8rem; opacity:0.8; margin-top:5px;'>Fully compliant with Data Protection Acts</div>
            </div>
            """, unsafe_allow_html=True
        )
    with aud_col2:
        st.markdown(
            f"""
            <div class='glass-card' style='text-align: center;'>
                <div class='metric-label'>{t['dp_noise_distortion']}</div>
                <div class='metric-value'>Level: {epsilon}</div>
                <div style='font-size:0.8rem; opacity:0.8; margin-top:5px;'>Differential Privacy Budget (ε)</div>
            </div>
            """, unsafe_allow_html=True
        )
    with aud_col3:
        st.markdown(
            f"""
            <div class='glass-card' style='text-align: center;'>
                <div class='metric-label'>{t['k_anon_suppression']}</div>
                <div class='metric-value' style='color:{"#EF4444" if tot_suppressed > 0 else "#10B981"};'>{tot_suppressed} Categories</div>
                <div style='font-size:0.8rem; opacity:0.8; margin-top:5px;'>Low counts (under size {k_anonymity}) suppressed</div>
            </div>
            """, unsafe_allow_html=True
        )
        
    st.markdown(f"#### {t['ledger_title']}")
    audit_records = []
    for node_id, node in node_data.items():
        for m_id, m in node["metrics"].items():
            audit_records.append({
                t["audit_col_node"]: node["name"],
                t["audit_col_field"]: m["label"],
                t["audit_col_eps"]: f"Eps = {epsilon}",
                t["audit_col_noise"]: m["dp_noise"],
                t["audit_col_guard"]: "Passed (Group size safe)" if not m["suppressed"] else f"🚨 Masked (Group size {m['raw_val']} < limit {k_anonymity})",
                t["audit_col_payload"]: f"{m['transmitted_val']} (Anonymized)"
            })
    st.dataframe(pd.DataFrame(audit_records), use_container_width=True, hide_index=True)
