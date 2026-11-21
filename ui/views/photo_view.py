"""
PulseShield UI View: Static Photo Protection & Anti-Scraping
"""

import streamlit as st
import cv2
import numpy as np
from pathlib import Path
from modules.photo_protector import PhotoProtector
from ui.components import render_metric_card
from database import log_photo_job, add_alert
from config import BASE_DIR, DEFAULT_DELTA

def render_photo_view():
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h2>AI-Based Facial Photo Protection</h2>
        <p style="color: #94A3B8;">
            Protect your facial portraits against unauthorized web scraping, facial recognition scraping,
            and AI identity model fine-tuning with bounded cloaking and invisible cryptographic signatures.
        </p>
    </div>
    """, unsafe_allow_html=True)

    sample_portrait = BASE_DIR / "sample_data" / "sample_portrait.jpg"

    with st.expander("⚙️ Protection Parameters & Provenance", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            delta = st.slider("Cloaking Delta (Δ)", 1.0, 5.0, float(DEFAULT_DELTA), 0.5)
            mode = st.selectbox("Protection Mode", PhotoProtector.CLOAKING_MODES)
        with col2:
            owner_tag = st.text_input("Owner Identity Tag", value="Alex Rivera (ID: PS-9942)")
            use_sample = st.checkbox("Load Sample Portrait Asset", value=False)
        with col3:
            st.markdown("""
            <div style="color: #94A3B8; font-size: 0.82rem; padding: 10px; background: rgba(14, 23, 38, 0.4); border-radius: 6px;">
                <b>Feature Disruption:</b> Fourier Phase Modulation perturbs high-frequency spatial gradients utilized by FaceNet and ArcFace deep feature extractors without visible distortion.
            </div>
            """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload Portrait Image (JPG, PNG, WEBP)", type=["jpg", "jpeg", "png", "webp"])

    img_bgr = None
    filename = "photo.jpg"

    if use_sample and sample_portrait.exists():
        img_bgr = cv2.imread(str(sample_portrait))
        filename = "sample_portrait.jpg"
        st.info("Loaded pre-generated synthetic portrait asset.")
    elif uploaded_file is not None:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        img_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        filename = uploaded_file.name

    if img_bgr is not None:
        if st.button("🛡️ Cloak & Watermark Photograph", key="btn_cloak_photo"):
            protector = PhotoProtector()
            with st.spinner("Applying biometric perturbation and cryptographic watermark..."):
                res = protector.protect_photo(
                    image_bgr=img_bgr,
                    delta=delta,
                    mode=mode,
                    owner_signature=owner_tag,
                )
                st.session_state["last_photo_res"] = res
                st.session_state["last_photo_filename"] = filename

                # Save to database
                log_photo_job({
                    "filename": filename,
                    "delta_used": delta,
                    "mode": mode,
                    "psnr": res["metrics"]["psnr"],
                    "ssim": res["metrics"]["ssim"],
                    "watermark_signature": res["watermark_signature"],
                    "output_path": "",
                })

                add_alert(
                    "INFO",
                    f"Photo Protected: {filename}",
                    f"Cloaked with {mode} (PSNR: {res['metrics']['psnr']} dB). Signature: {res['watermark_signature']}."
                )

    if "last_photo_res" in st.session_state:
        res = st.session_state["last_photo_res"]
        fname = st.session_state.get("last_photo_filename", "protected_photo.png")
        metrics = res["metrics"]

        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        mcol1, mcol2, mcol3, mcol4 = st.columns(4)
        with mcol1:
            render_metric_card("PSNR Fidelity", f"{metrics['psnr']} dB", "VIRTUALLY LOSSLESS", "green")
        with mcol2:
            render_metric_card("SSIM Index", f"{metrics['ssim']}", "STRUCTURAL ACCURACY", "green")
        with mcol3:
            render_metric_card("Max Abs Delta", f"{metrics['linf']}", "BOUNDED PIXELS", "cyan")
        with mcol4:
            render_metric_card("Provenance ID", res["watermark_signature"][:10] + "...", "C2PA-STYLE SIGNATURE", "purple")

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

        vcol1, vcol2, vcol3 = st.columns(3)
        with vcol1:
            st.subheader("Original Image")
            st.image(res["orig_rgb"], use_container_width=True)

        with vcol2:
            st.subheader("Cloaked Image")
            st.image(res["cloaked_rgb"], use_container_width=True)

            is_success, buffer = cv2.imencode(".png", res["cloaked_bgr"])
            if is_success:
                st.download_button(
                    "💾 Download Cloaked Photo (.png)",
                    data=buffer.tobytes(),
                    file_name=f"cloaked_{Path(fname).stem}.png",
                    mime="image/png",
                    use_container_width=True
                )

        with vcol3:
            st.subheader("Difference Map (25x)")
            st.image(res["diff_heatmap_rgb"], caption="Turbo Heatmap: Perturbations localized strictly on facial skin", use_container_width=True)
