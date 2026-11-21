"""
PulseShield UI View: Dashboard / Mission Control
"""

import streamlit as st
from ui.components import render_metric_card
from database import get_dashboard_stats, get_alerts

def render_dashboard():
    st.markdown("""
    <div style="margin-bottom: 24px;">
        <h1 style="margin-bottom: 6px;">Biometric Security Mission Control</h1>
        <p style="color: #94A3B8; font-size: 1.05rem;">
            Proactive identity defense against generative AI, deepfake manipulation, and unauthorized facial scraping.
        </p>
    </div>
    """, unsafe_allow_html=True)

    stats = get_dashboard_stats()

    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("Registered Identities", stats["identities_count"], "ACTIVE PROTECTION", "green")
    with col2:
        render_metric_card("Cloaked Videos", stats["videos_cloaked"], "rPPG SCRAMBLED", "cyan")
    with col3:
        render_metric_card("Protected Photos", stats["photos_protected"], "WATERMARKED", "cyan")
    with col4:
        render_metric_card("Avg Desync Drop", f"{stats['avg_desync']}%", "FAKECATCHER MITIGATION", "yellow")

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    # Main Grid: Quick Actions & Scientific Overview
    col_main, col_alerts = st.columns([2, 1])

    with col_main:
        st.markdown("""
        <div class="cyber-card cyber-card-highlight">
            <h3 style="color: #00F0FF; margin-bottom: 12px;">🛡️ Proactive Video Cloaking Architecture</h3>
            <p style="color: #CBD5E1; line-height: 1.6; font-size: 0.95rem;">
                PulseShield implements <b>temporal remote photoplethysmography (rPPG) desynchronization</b>. 
                State-of-the-art deepfake detectors (such as <i>FakeCatcher</i> by Ciftci et al.) distinguish authentic 
                human faces from synthetic videos by analyzing biological pulse consistency across disparate facial skin ROIs.
            </p>
            <p style="color: #94A3B8; line-height: 1.6; font-size: 0.92rem;">
                By injecting imperceptible, bounded modifications (&Delta; &in; [1.0, 4.0]) strictly within the green 
                reflectance spectrum of the forehead and cheeks, PulseShield dismantles inter-region correlation while 
                preserving visual video fidelity (PSNR &gt; 42 dB, SSIM &gt; 0.98).
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("⚡ Core Defense Modules")
        mcol1, mcol2 = st.columns(2)
        with mcol1:
            st.markdown("""
            <div class="cyber-card">
                <h4 style="color: #38BDF8;">📹 Video Cloaking Engine</h4>
                <p style="color: #94A3B8; font-size: 0.88rem;">
                    MediaPipe 468-point FaceMesh tracking, automated skin ROI segmentation, and phase-scrambled green channel modulation.
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="cyber-card">
                <h4 style="color: #A855F7;">📸 Photo Protection Suite</h4>
                <p style="color: #94A3B8; font-size: 0.88rem;">
                    Spatial frequency disruption and invisible cryptographic watermarking to neutralize AI facial training scraping.
                </p>
            </div>
            """, unsafe_allow_html=True)

        with mcol2:
            st.markdown("""
            <div class="cyber-card">
                <h4 style="color: #10B981;">🔍 AI Misuse Scanner</h4>
                <p style="color: #94A3B8; font-size: 0.88rem;">
                    Pose-invariant biometric vector matching against registered user identities with deepfake artifact scoring.
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="cyber-card">
                <h4 style="color: #F59E0B;">🔬 Forensic Authenticity Lab</h4>
                <p style="color: #94A3B8; font-size: 0.88rem;">
                    Error Level Analysis (ELA), 2D Fourier spectral grid detection, and noise residual variance forensics.
                </p>
            </div>
            """, unsafe_allow_html=True)

    with col_alerts:
        st.markdown("""
        <div class="cyber-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <h3 style="margin: 0; font-size: 1.15rem;">🚨 Security Feed</h3>
                <span class="badge-red">LIVE</span>
            </div>
        """, unsafe_allow_html=True)

        alerts = get_alerts(limit=5)
        if alerts:
            for alert in alerts:
                sev = alert["severity"]
                badge_class = "badge-red" if sev == "CRITICAL" else ("badge-yellow" if sev == "WARNING" else "badge-cyan")
                st.markdown(f"""
                <div style="border-bottom: 1px solid rgba(255, 255, 255, 0.08); padding-bottom: 10px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        <strong style="color: #F8FAFC; font-size: 0.88rem;">{alert['title']}</strong>
                        <span class="{badge_class}">{sev}</span>
                    </div>
                    <div style="color: #94A3B8; font-size: 0.80rem; line-height: 1.4;">{alert['message']}</div>
                    <div style="color: #64748B; font-size: 0.72rem; margin-top: 4px; font-family: monospace;">{alert['created_at']}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No security alerts logged.")

        st.markdown("</div>", unsafe_allow_html=True)

    # Scientific Disclaimer Notice
    st.markdown("""
    <div style="margin-top: 25px; padding: 14px 20px; border-radius: 8px; background: rgba(15, 23, 42, 0.6); border-left: 3px solid #00F0FF; font-size: 0.85rem; color: #94A3B8;">
        <strong style="color: #00F0FF;">RESEARCH NOTICE:</strong> PulseShield is an experimental computer vision security system. 
        Biometric cloaking disrupts physiological signal consistency to evaluate defense against rPPG-based classifiers. 
        It does not guarantee complete prevention of all future deepfake architectures. All results are measured objectively via PSNR, SSIM, and Pearson correlation coefficients.
    </div>
    """, unsafe_allow_html=True)
