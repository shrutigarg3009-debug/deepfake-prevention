"""
PulseShield UI View: AI Misuse Scanner & Identity Registry
"""

import streamlit as st
import cv2
import numpy as np
import hashlib
from pathlib import Path
from modules.misuse_scanner import MisuseScanner
from database import register_identity, get_all_identities
from ui.components import render_metric_card
from config import BASE_DIR

def render_scanner_view():
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h2>AI Misuse Scanner & Identity Registry</h2>
        <p style="color: #94A3B8;">
            Audit suspect web media against registered biometric identities.
            Detect unauthorized deepfake face-swaps, synthetic impersonation, and unconsented cloning.
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab_scan, tab_reg = st.tabs(["🔍 Scan Suspect Media", "👤 Register New Facial Identity"])

    scanner = MisuseScanner()

    # TAB 1: SCANNER
    with tab_scan:
        sample_deepfake = BASE_DIR / "sample_data" / "sample_deepfake_suspect.jpg"

        scol1, scol2 = st.columns([2, 1])
        with scol1:
            uploaded_suspect = st.file_uploader(
                "Upload Suspect Image (JPG, PNG, WEBP)",
                type=["jpg", "jpeg", "png", "webp"],
                key="uploader_suspect"
            )
        with scol2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            use_sample_fake = st.checkbox("Load Sample Deepfake Suspect Asset", value=False)

        suspect_bgr = None
        if use_sample_fake and sample_deepfake.exists():
            suspect_bgr = cv2.imread(str(sample_deepfake))
            st.info("Loaded pre-generated synthetic face-swap artifact test image.")
        elif uploaded_suspect is not None:
            file_bytes = np.asarray(bytearray(uploaded_suspect.read()), dtype=np.uint8)
            suspect_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        if suspect_bgr is not None:
            if st.button("🚨 Analyze Suspect Media", key="btn_scan_suspect"):
                with st.spinner("Extracting biometric landmarks, matching identity database, and calculating deepfake risk..."):
                    res = scanner.scan_suspect_media(suspect_bgr)
                    st.session_state["last_scan_res"] = res

        if "last_scan_res" in st.session_state:
            res = st.session_state["last_scan_res"]
            forensic = res["forensic_report"]

            st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

            # Alert Banner
            st.markdown(f"""
            <div style="padding: 18px 24px; border-radius: 10px; background: rgba(14, 23, 38, 0.85); border: 2px solid {res['badge_color']}; box-shadow: 0 0 20px {res['badge_color']}33; margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <h3 style="margin: 0; color: {res['badge_color']};">THREAT LEVEL: {res['threat_level']}</h3>
                    <span style="background: {res['badge_color']}22; color: {res['badge_color']}; border: 1px solid {res['badge_color']}; padding: 4px 12px; border-radius: 6px; font-weight: 700; font-family: monospace;">
                        AUTHENTICITY: {forensic['authenticity_score']}%
                    </span>
                </div>
                <div style="color: #F8FAFC; font-size: 0.96rem; line-height: 1.5;">{res['summary']}</div>
            </div>
            """, unsafe_allow_html=True)

            # Metrics
            m1, m2, m3, m4 = st.columns(4)
            highest = res["highest_match"]
            with m1:
                render_metric_card("Identity Match", f"{highest['match_confidence']}%" if highest else "N/A", highest["name"] if highest else "Unregistered", "cyan")
            with m2:
                render_metric_card("Authenticity Score", f"{forensic['authenticity_score']}%", forensic["verdict"], "green" if forensic["authenticity_score"] >= 70 else "red")
            with m3:
                render_metric_card("ELA Disparity", f"{forensic['metrics']['ela_score']}", "COMPRESSION ANOMALY", "yellow")
            with m4:
                render_metric_card("Noise Variance", f"{forensic['metrics']['noise_variance']}", "TEXTURE SMOOTHNESS", "cyan")

            st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

            # Images
            icol1, icol2, icol3 = st.columns(3)
            with icol1:
                st.subheader("Suspect Media")
                st.image(res["suspect_rgb"], use_container_width=True)
            with icol2:
                st.subheader("ELA Compression Map")
                st.image(forensic["visualizations"]["ela_rgb"], caption="Highlights recompression error disparities", use_container_width=True)
            with icol3:
                st.subheader("2D Fourier Spectrum")
                st.image(forensic["visualizations"]["fft_rgb"], caption="High-frequency periodic GAN artifacts", use_container_width=True)

    # TAB 2: REGISTER IDENTITY
    with tab_reg:
        st.subheader("Register Verified Facial Identity")
        st.write("Register genuine identity photographs to enable automated monitoring and proactive deepfake auditing.")

        with st.form("form_register_identity"):
            name = st.text_input("Full Name", placeholder="e.g. Alex Rivera")
            email = st.text_input("Notification Email", placeholder="e.g. user@organization.com")
            reg_photo = st.file_uploader("Upload Genuine Reference Photo", type=["jpg", "jpeg", "png"])
            submit = st.form_submit_button("🔒 Securely Register Identity")

            if submit:
                if not name:
                    st.error("Please provide a name.")
                elif reg_photo is None:
                    st.error("Please upload a reference portrait.")
                else:
                    file_bytes = np.asarray(bytearray(reg_photo.read()), dtype=np.uint8)
                    reg_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

                    descriptor = scanner.extract_face_descriptor(reg_bgr)
                    if descriptor is None:
                        st.error("No clear human face was detected in the uploaded photo. Please try another image.")
                    else:
                        photo_hash = hashlib.sha256(file_bytes).hexdigest()
                        new_id = register_identity(
                            name=name,
                            email=email,
                            photo_hash=photo_hash,
                            face_embedding=descriptor
                        )
                        st.success(f"Identity registered successfully! (ID: PS-{new_id:04d}). Face embedding secured in SQLite.")

        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        st.subheader("Registered User Identities")
        identities = get_all_identities()
        if identities:
            for ident in identities:
                st.markdown(f"""
                <div style="background: rgba(14, 23, 38, 0.5); padding: 12px 18px; border-radius: 8px; border: 1px solid rgba(0, 240, 255, 0.15); margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="color: #F8FAFC;">{ident['name']}</strong> 
                        <span style="color: #94A3B8; font-size: 0.85rem; margin-left: 10px;">{ident['email'] or 'No email'}</span>
                        <div style="color: #64748B; font-size: 0.75rem; font-family: monospace; margin-top: 3px;">Registered: {ident['registered_at']} | Hash: {ident['photo_hash'][:12]}...</div>
                    </div>
                    <span class="badge-green">{ident['protection_status']}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No identities registered yet.")
