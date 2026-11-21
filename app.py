"""
PulseShield: Proactive Biometric Video Cloaking & Facial Identity Protection
Main Streamlit Application Entrypoint
"""

import streamlit as st
import sys
from pathlib import Path

# Ensure root directory is in python search path
APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

# Initialize database schema
from database import init_db, get_dashboard_stats
init_db()

# Page configuration
st.set_page_config(
    page_title="PulseShield: Biometric Video Cloaking",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS Styles
from ui.styles import CUSTOM_CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Components and Views
from ui.components import render_header
from ui.views import (
    render_dashboard,
    render_video_view,
    render_webcam_view,
    render_photo_view,
    render_scanner_view,
    render_verification_view,
    render_history_view,
    render_notifications_view,
    render_how_it_works_view,
)

def main():
    stats = get_dashboard_stats()
    unread_alerts = stats.get("unread_alerts", 0)

    # Sidebar Navigation
    with st.sidebar:
        st.markdown("""
        <div style="padding: 10px 0 15px 0; border-bottom: 1px solid rgba(0, 240, 255, 0.2); margin-bottom: 15px;">
            <div style="font-size: 1.5rem; font-weight: 800; background: linear-gradient(135deg, #00F0FF, #A855F7); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                ⚡ PULSESHIELD
            </div>
            <div style="color: #64748B; font-size: 0.75rem; letter-spacing: 0.05em; font-family: monospace; margin-top: 2px;">
                v2.4 RESEARCH EDITION
            </div>
        </div>
        """, unsafe_allow_html=True)

        nav_options = [
            "Dashboard",
            "Protect Video (Upload)",
            "Live Webcam Protection",
            "Protect Photos",
            "AI Misuse Scanner",
            "Image Verification",
            "Scan History",
            f"Notifications ({unread_alerts})" if unread_alerts > 0 else "Notifications",
            "How It Works",
        ]

        # Sync selection
        selected_nav = st.radio(
            "SYSTEM NAVIGATION",
            nav_options,
            index=0,
            label_visibility="collapsed"
        )

        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="cyber-card" style="padding: 14px; font-size: 0.78rem;">
            <div style="color: #00F0FF; font-weight: 700; margin-bottom: 4px;">● DEFENSE STATUS</div>
            <div style="color: #94A3B8;">FaceMesh: <span style="color: #10B981;">Online (468 pts)</span></div>
            <div style="color: #94A3B8;">rPPG Cloak: <span style="color: #10B981;">Active (Δ = 2.0)</span></div>
            <div style="color: #94A3B8;">SQLite DB: <span style="color: #10B981;">Connected</span></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="color: #475569; font-size: 0.72rem; text-align: center; margin-top: 20px;">
            PulseShield &copy; 2026<br>Experimental Biometric Cloaking
        </div>
        """, unsafe_allow_html=True)

    # Clean active section title
    clean_section = selected_nav.split(" (")[0]

    # Render Header Banner
    render_header(clean_section)

    # Route Views
    if clean_section == "Dashboard":
        render_dashboard()
    elif clean_section == "Protect Video (Upload)":
        render_video_view()
    elif clean_section == "Live Webcam Protection":
        render_webcam_view()
    elif clean_section == "Protect Photos":
        render_photo_view()
    elif clean_section == "AI Misuse Scanner":
        render_scanner_view()
    elif clean_section == "Image Verification":
        render_verification_view()
    elif clean_section == "Scan History":
        render_history_view()
    elif clean_section.startswith("Notifications"):
        render_notifications_view()
    elif clean_section == "How It Works":
        render_how_it_works_view()

if __name__ == "__main__":
    main()
