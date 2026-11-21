"""
PulseShield UI View: Scan History & SQLite Database Explorer
"""

import streamlit as st
import pandas as pd
import json
from database import (
    get_video_jobs,
    get_photo_jobs,
    get_forensic_scans,
    get_all_identities,
)

def render_history_view():
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h2>Biometric Audit History & Database</h2>
        <p style="color: #94A3B8;">
            Query persistent SQLite records for video cloaking runs, protected photo archives,
            forensic authenticity assessments, and registered identities.
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab_vid, tab_photo, tab_forensic, tab_ident = st.tabs([
        "📹 Video Cloaking Jobs",
        "📸 Photo Protection Jobs",
        "🔬 Forensic Scans",
        "👤 Registered Identities"
    ])

    # 1. Videos
    with tab_vid:
        st.subheader("Video Cloaking Audit Trail")
        vjobs = get_video_jobs(limit=100)
        if vjobs:
            df_v = pd.DataFrame(vjobs)
            st.dataframe(
                df_v[[
                    "id", "filename", "processed_at", "fps", "frame_count",
                    "delta_used", "perturbation_mode", "avg_psnr", "avg_ssim",
                    "desync_drop_percent"
                ]],
                use_container_width=True
            )

            # JSON export
            json_str = json.dumps(vjobs, indent=2)
            st.download_button(
                "📥 Export Video Jobs (JSON)",
                data=json_str,
                file_name="pulseshield_video_jobs.json",
                mime="application/json"
            )
        else:
            st.info("No video cloaking jobs recorded yet.")

    # 2. Photos
    with tab_photo:
        st.subheader("Photo Cloaking Audit Trail")
        pjobs = get_photo_jobs(limit=100)
        if pjobs:
            df_p = pd.DataFrame(pjobs)
            st.dataframe(
                df_p[["id", "filename", "processed_at", "delta_used", "mode", "psnr", "ssim", "watermark_signature"]],
                use_container_width=True
            )
            json_str = json.dumps(pjobs, indent=2)
            st.download_button(
                "📥 Export Photo Jobs (JSON)",
                data=json_str,
                file_name="pulseshield_photo_jobs.json",
                mime="application/json"
            )
        else:
            st.info("No photo cloaking jobs recorded yet.")

    # 3. Forensics
    with tab_forensic:
        st.subheader("Forensic Image Verification Scans")
        fscans = get_forensic_scans(limit=100)
        if fscans:
            df_f = pd.DataFrame(fscans)
            st.dataframe(
                df_f[["id", "filename", "scanned_at", "authenticity_score", "verdict", "ela_score", "noise_score", "exif_tampered"]],
                use_container_width=True
            )
            json_str = json.dumps(fscans, indent=2)
            st.download_button(
                "📥 Export Forensic Scans (JSON)",
                data=json_str,
                file_name="pulseshield_forensic_scans.json",
                mime="application/json"
            )
        else:
            st.info("No forensic scans recorded yet.")

    # 4. Identities
    with tab_ident:
        st.subheader("Registered User Identities")
        idents = get_all_identities()
        if idents:
            df_i = pd.DataFrame(idents)
            st.dataframe(
                df_i[["id", "name", "email", "registered_at", "photo_hash", "protection_status"]],
                use_container_width=True
            )
        else:
            st.info("No registered identities found.")
