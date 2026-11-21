"""
PulseShield UI View: Image Authenticity Verification Lab
"""

import streamlit as st
import cv2
import numpy as np
from pathlib import Path
from modules.image_authenticity import AuthenticityVerifier
from ui.components import plot_authenticity_gauge, render_metric_card
from database import log_forensic_scan, add_alert
from config import BASE_DIR

def render_verification_view():
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h2>Forensic Image Authenticity Verification</h2>
        <p style="color: #94A3B8;">
            Deep digital forensic examination leveraging Error Level Analysis (ELA),
            noise residual modeling, 2D Fast Fourier Transform (FFT) grid analysis, and EXIF integrity.
        </p>
    </div>
    """, unsafe_allow_html=True)

    sample_portrait = BASE_DIR / "sample_data" / "sample_portrait.jpg"
    sample_deepfake = BASE_DIR / "sample_data" / "sample_deepfake_suspect.jpg"

    col_up, col_samples = st.columns([2, 1])
    with col_up:
        uploaded_file = st.file_uploader(
            "Upload Image for Forensic Inspection (JPG, PNG, WEBP)",
            type=["jpg", "jpeg", "png", "webp"],
            key="uploader_verify"
        )
    with col_samples:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        choice = st.radio(
            "Or load sample test asset:",
            ["None", "Clean Authentic Portrait", "Synthetic Deepfake Suspect"],
            horizontal=False
        )

    img_bgr = None
    raw_bytes = None
    filename = "inspect.jpg"

    if choice == "Clean Authentic Portrait" and sample_portrait.exists():
        img_bgr = cv2.imread(str(sample_portrait))
        filename = "sample_portrait.jpg"
        with open(sample_portrait, "rb") as f:
            raw_bytes = f.read()
    elif choice == "Synthetic Deepfake Suspect" and sample_deepfake.exists():
        img_bgr = cv2.imread(str(sample_deepfake))
        filename = "sample_deepfake_suspect.jpg"
        with open(sample_deepfake, "rb") as f:
            raw_bytes = f.read()
    elif uploaded_file is not None:
        raw_bytes = uploaded_file.read()
        file_bytes = np.asarray(bytearray(raw_bytes), dtype=np.uint8)
        img_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        filename = uploaded_file.name

    if img_bgr is not None:
        if st.button("🔬 Execute Multi-Spectrum Forensic Audit", key="btn_run_forensics"):
            with st.spinner("Analyzing JPEG quantization tables, noise variance, and frequency domain..."):
                res = AuthenticityVerifier.verify_image(img_bgr, raw_bytes=raw_bytes)
                st.session_state["last_forensic_res"] = res
                st.session_state["last_forensic_filename"] = filename

                # Save to database
                meta = res["metadata"]
                log_forensic_scan({
                    "filename": filename,
                    "authenticity_score": res["authenticity_score"],
                    "verdict": res["verdict"],
                    "ela_score": res["metrics"]["ela_score"],
                    "fft_score": res["metrics"]["fft_high_freq_ratio"],
                    "noise_score": res["metrics"]["noise_variance"],
                    "exif_tampered": 1 if meta.get("editing_software_detected") else 0,
                    "notes": f"Confidence: {res['confidence']}. EXIF editing tags: {len(meta.get('editing_software_detected', []))}"
                })

                if res["authenticity_score"] < 50.0:
                    add_alert(
                        "WARNING",
                        f"Synthetic Media Detected: {filename}",
                        f"Authenticity Score: {res['authenticity_score']}%. Verdict: {res['verdict']}."
                    )

    if "last_forensic_res" in st.session_state:
        res = st.session_state["last_forensic_res"]
        fname = st.session_state.get("last_forensic_filename", "inspect.jpg")
        metrics = res["metrics"]
        meta = res["metadata"]
        viz = res["visualizations"]

        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

        gcol, mcol = st.columns([1, 2])
        with gcol:
            st.plotly_chart(
                plot_authenticity_gauge(res["authenticity_score"], res["verdict"]),
                use_container_width=True
            )

        with mcol:
            st.markdown(f"""
            <div style="background: rgba(14, 23, 38, 0.7); padding: 18px 22px; border-radius: 10px; border: 1px solid rgba(0, 240, 255, 0.2); height: 260px; display: flex; flex-direction: column; justify-content: center;">
                <h3 style="color: {res['badge_color']}; margin-top: 0; margin-bottom: 8px;">VERDICT: {res['verdict'].upper()}</h3>
                <div style="color: #CBD5E1; font-size: 0.92rem; margin-bottom: 12px;">
                    Forensic confidence: <b>{res['confidence']}</b>. Composite index based on pixel error variance, 
                    Laplacian high-frequency texture, and 2D FFT spectral energy.
                </div>
                <div style="font-family: monospace; font-size: 0.82rem; color: #94A3B8;">
                    • ELA Mean Difference: <span style="color: #00F0FF;">{metrics['ela_score']}</span><br>
                    • Laplacian Noise Variance: <span style="color: #00F0FF;">{metrics['noise_variance']}</span><br>
                    • 2D FFT High-Freq Energy: <span style="color: #00F0FF;">{metrics['fft_high_freq_ratio']}</span><br>
                    • EXIF Camera Sensor Data: <span style="color: {'#10B981' if meta.get('has_camera_data') else '#F59E0B'};">{'PRESENT' if meta.get('has_camera_data') else 'ABSENT / STRIPPED'}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        st.subheader("🖼️ Forensic Diagnostic Visualizations")

        p1, p2, p3, p4 = st.columns(4)
        with p1:
            st.markdown("**1. Original Media**")
            st.image(viz["orig_rgb"], use_container_width=True)
        with p2:
            st.markdown("**2. Error Level Analysis (ELA)**")
            st.image(viz["ela_rgb"], caption="Inferno colormap: highlights localized compression seams", use_container_width=True)
        with p3:
            st.markdown("**3. Noise Residual Map**")
            st.image(viz["noise_rgb"], caption="Viridis colormap: evaluates natural sensor grain vs synthetic smoothing", use_container_width=True)
        with p4:
            st.markdown("**4. 2D FFT Spectrum**")
            st.image(viz["fft_rgb"], caption="Magma colormap: reveals periodic upsampling spikes and grid artifacts", use_container_width=True)
