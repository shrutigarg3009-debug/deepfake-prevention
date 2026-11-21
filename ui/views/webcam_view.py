"""
PulseShield UI View: Live Camera Biometric Cloaking
"""

import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
from modules.face_mesh_detector import FaceMeshDetector
from modules.perturbation_engine import PerturbationEngine
from ui.components import render_metric_card
from config import DEFAULT_DELTA

def render_webcam_view():
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h2>Live Camera Biometric Cloaker</h2>
        <p style="color: #94A3B8;">
            Capture frames directly from your live camera to evaluate real-time FaceMesh skin segmentation,
            green-channel perturbation, and difference heatmap visualization.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_opt1, col_opt2 = st.columns(2)
    with col_opt1:
        delta = st.slider("Live Perturbation Delta (Δ)", 1.0, 4.0, float(DEFAULT_DELTA), 0.5)
    with col_opt2:
        overlay_mode = st.selectbox(
            "Visualization Display Mode",
            ["Protected Cloaked Output", "FaceMesh ROI Debug Wireframe", "Difference Heatmap (Amplified)"]
        )

    camera_image = st.camera_input("Take a snapshot from webcam")

    if camera_image is not None:
        # Read bytes to BGR
        bytes_data = camera_image.getvalue()
        file_bytes = np.asarray(bytearray(bytes_data), dtype=np.uint8)
        frame_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        detector = FaceMeshDetector(max_num_faces=1, refine_landmarks=True)
        engine = PerturbationEngine()

        masks, metadata = detector.process_frame(frame_bgr)
        cloaked_bgr, metrics = engine.apply_perturbation(
            frame_bgr=frame_bgr,
            masks=masks,
            frame_idx=1,
            fps=30.0,
            delta=delta,
            mode="Temporal Sinusoidal Desynchronization"
        )

        diff_heatmap = PerturbationEngine.generate_difference_heatmap(frame_bgr, cloaked_bgr, amplification=25.0)
        wireframe = detector.render_debug_overlay(frame_bgr, masks, metadata)

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

        mcol1, mcol2, mcol3, mcol4 = st.columns(4)
        with mcol1:
            render_metric_card("Live PSNR", f"{metrics['psnr']} dB", "IMPERCEPTIBLE", "green")
        with mcol2:
            render_metric_card("Live SSIM", f"{metrics['ssim']}", "STRUCTURAL INTEGRITY", "green")
        with mcol3:
            render_metric_card("Max Abs Error", f"{metrics['linf']}", "L_inf BOUND", "cyan")
        with mcol4:
            status_text = "FACE LOCKED" if metadata.get("detected") else "NO FACE DETECTED"
            render_metric_card("Tracking Status", status_text, "MEDIAPIPE MESH", "green" if metadata.get("detected") else "red")

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

        vcol1, vcol2 = st.columns(2)
        with vcol1:
            st.subheader("Original Camera Frame")
            st.image(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB), use_container_width=True)

        with vcol2:
            st.subheader(f"Result: {overlay_mode}")
            if overlay_mode == "Protected Cloaked Output":
                display_img = cv2.cvtColor(cloaked_bgr, cv2.COLOR_BGR2RGB)
            elif overlay_mode == "FaceMesh ROI Debug Wireframe":
                display_img = cv2.cvtColor(wireframe, cv2.COLOR_BGR2RGB)
            else:
                display_img = cv2.cvtColor(diff_heatmap, cv2.COLOR_BGR2RGB)

            st.image(display_img, use_container_width=True)

            # Download button for protected snapshot
            is_success, buffer = cv2.imencode(".png", cloaked_bgr)
            if is_success:
                st.download_button(
                    "💾 Download Protected Snapshot (.png)",
                    data=buffer.tobytes(),
                    file_name="pulseshield_live_cloaked.png",
                    mime="image/png",
                    use_container_width=True
                )
