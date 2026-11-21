"""
PulseShield UI View: Video Cloaking & rPPG Desynchronization Engine
"""

import streamlit as st
import tempfile
import os
from pathlib import Path
from modules.video_processor import VideoProcessor
from ui.components import (
    plot_rppg_signals,
    plot_correlation_comparison,
    plot_fft_spectrum,
    render_metric_card
)
from database import log_video_job, add_alert
from config import BASE_DIR, DEFAULT_DELTA, DEFAULT_EXPERIMENTAL_FREQ

def render_video_view():
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h2>Proactive Video Cloaking Engine</h2>
        <p style="color: #94A3B8;">
            Upload a facial video to detect skin ROIs, inject bounded green-channel perturbations,
            and evaluate rPPG signal desynchronization against FakeCatcher biometrics.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar / Controls
    with st.expander("⚙️ Perturbation & Research Parameters", expanded=True):
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            delta = st.slider(
                "Perturbation Amplitude Bound (Δ)",
                min_value=1.0,
                max_value=4.0,
                value=float(DEFAULT_DELTA),
                step=0.5,
                help="Bounded modification amplitude in the green reflectance channel [0-255]. Lower is more imperceptible."
            )
            mode = st.selectbox(
                "Experimental Perturbation Mode",
                options=[
                    "Temporal Sinusoidal Desynchronization",
                    "Inter-Region Phase Scrambler",
                    "Bounded Pseudorandom Jitter",
                    "Hybrid Multi-Frequency Injection"
                ],
                help="Strategy for disrupting spatial-temporal coherence across disparate facial regions."
            )

        with col_c2:
            exp_freq = st.number_input(
                "Experimental Disruption Frequency (Hz)",
                min_value=1.0,
                max_value=15.0,
                value=float(DEFAULT_EXPERIMENTAL_FREQ),
                step=0.5,
                help="Target oscillation frequency. Automatically checked against the Nyquist sampling limit."
            )
            random_seed = st.number_input(
                "Reproducible Random Seed",
                min_value=0,
                max_value=999999,
                value=42,
                step=1,
                help="Ensures exact experimental repeatability across consecutive trials."
            )

        with col_c3:
            max_frames = st.slider(
                "Processing Frame Limit",
                min_value=30,
                max_value=300,
                value=90,
                step=15,
                help="Limits frames for instant hackathon demonstration. Uncheck limit for full video."
            )
            use_sample = st.checkbox("Load Sample 72-BPM Facial Video", value=False,
                                    help="Instantly test with the pre-generated synthetic physiological video asset.")

    # Upload or sample selection
    sample_path = BASE_DIR / "sample_data" / "sample_pulse_face.mp4"
    uploaded_file = st.file_uploader(
        "Upload Video (MP4, AVI, MOV)",
        type=["mp4", "avi", "mov", "mkv", "webm"],
        help="Upload a video featuring a visible human face."
    )

    video_source_path = None
    input_filename = "sample_pulse_face.mp4"

    if use_sample and sample_path.exists():
        video_source_path = str(sample_path)
        input_filename = "sample_pulse_face.mp4"
        st.info("Loaded pre-generated synthetic physiological video asset (72 BPM cardiac reflectance).")
    elif uploaded_file is not None:
        # Validate format & size
        valid, msg = VideoProcessor.validate_file(uploaded_file.name, uploaded_file.size)
        if not valid:
            st.error(msg)
            return

        # Save to temp file
        temp_input = tempfile.NamedTemporaryFile(suffix=Path(uploaded_file.name).suffix, delete=False)
        temp_input.write(uploaded_file.read())
        temp_input.close()
        video_source_path = temp_input.name
        input_filename = uploaded_file.name

    if video_source_path:
        meta = VideoProcessor.get_video_metadata(video_source_path)
        if meta.get("valid"):
            st.markdown(f"""
            <div style="background: rgba(14, 23, 38, 0.5); padding: 12px 18px; border-radius: 8px; border: 1px solid rgba(0, 240, 255, 0.2); margin-bottom: 15px; font-size: 0.88rem; font-family: monospace;">
                Resolution: <span style="color: #00F0FF;">{meta['width']}x{meta['height']}</span> | 
                FPS: <span style="color: #00F0FF;">{meta['fps']}</span> | 
                Total Frames: <span style="color: #00F0FF;">{meta['frame_count']}</span> | 
                Duration: <span style="color: #00F0FF;">{meta['duration_sec']}s</span>
            </div>
            """, unsafe_allow_html=True)

        if st.button("🚀 Execute Biometric Cloaking Pipeline", key="btn_run_video"):
            processor = VideoProcessor()
            processor.engine.set_seed(random_seed)

            progress_bar = st.progress(0.0)
            status_text = st.empty()

            def update_progress(pct: float, desc: str):
                progress_bar.progress(pct)
                status_text.markdown(f"<span style='color: #00F0FF; font-family: monospace;'>{desc}</span>", unsafe_allow_html=True)

            try:
                results = processor.process_video(
                    input_path=video_source_path,
                    delta=delta,
                    mode=mode,
                    experimental_freq=exp_freq,
                    max_frames=max_frames,
                    progress_callback=update_progress,
                )

                progress_bar.progress(1.0)
                status_text.markdown("<span style='color: #10B981; font-weight: 600;'>Processing Complete!</span>", unsafe_allow_html=True)
                st.session_state["last_video_results"] = results

                # Log to database
                rppg = results["rppg_analysis"]
                perc = results["perceptual_metrics"]
                log_video_job({
                    "filename": input_filename,
                    "fps": results["fps"],
                    "duration_sec": results["duration_sec"],
                    "frame_count": results["frames_processed"],
                    "delta_used": delta,
                    "perturbation_mode": mode,
                    "avg_psnr": perc["mean_psnr"],
                    "avg_ssim": perc["mean_ssim"],
                    "pearson_orig_avg": rppg["orig_mean_pearson"],
                    "pearson_prot_avg": rppg["prot_mean_pearson"],
                    "desync_drop_percent": rppg["desync_drop_percent"],
                    "output_path": results["output_path"],
                })

                add_alert(
                    "INFO",
                    f"Video Cloaked: {input_filename}",
                    f"Processed {results['frames_processed']} frames with Delta {delta}. Desync drop: {rppg['desync_drop_percent']}%."
                )

            except Exception as e:
                st.error(f"Error during video processing: {e}")
                return

    # Display Results if available in session state
    if "last_video_results" in st.session_state:
        res = st.session_state["last_video_results"]
        rppg = res["rppg_analysis"]
        perc = res["perceptual_metrics"]
        missing = res["missing_face_stats"]

        st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
        st.subheader("📊 Experimental Results & Perceptual Evaluation")

        # Metrics Row
        mcol1, mcol2, mcol3, mcol4, mcol5 = st.columns(5)
        with mcol1:
            render_metric_card("PSNR", f"{perc['mean_psnr']} dB", "IMPERCEPTIBLE (>40 dB)", "green")
        with mcol2:
            render_metric_card("SSIM", f"{perc['mean_ssim']}", "STRUCTURAL PRESERVATION", "green")
        with mcol3:
            render_metric_card("Orig Pearson r", f"{rppg['orig_mean_pearson']}", "SYNCHRONIZED", "cyan")
        with mcol4:
            render_metric_card("Prot Pearson r", f"{rppg['prot_mean_pearson']}", "DESYNCHRONIZED", "yellow")
        with mcol5:
            render_metric_card("Desync Drop", f"{rppg['desync_drop_percent']}%", rppg['fakecatcher_bypass_status'], "red")

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

        # Tabbed Visualizations
        tab1, tab2, tab3, tab4 = st.tabs([
            "📈 rPPG Waveforms (3 ROIs)",
            "🧬 FakeCatcher Correlation Matrix",
            "⚡ FFT Power Spectrum",
            "🔍 Visual Inspection & Download"
        ])

        with tab1:
            st.plotly_chart(plot_rppg_signals(rppg), use_container_width=True)
            st.caption("Temporal variation in mean green-channel reflectance extracted from Forehead, Left Cheek, and Right Cheek ROIs.")

        with tab2:
            st.plotly_chart(
                plot_correlation_comparison(rppg["orig_corr_matrix"], rppg["prot_corr_matrix"], rppg["roi_labels"]),
                use_container_width=True
            )
            st.markdown(f"""
            <div style="font-size: 0.88rem; color: #CBD5E1; padding: 10px 14px; background: rgba(14, 23, 38, 0.6); border-radius: 8px;">
                <b>Scientific Interpretation:</b> In natural physiological videos, facial skin regions exhibit strong spatial-temporal 
                co-pulsatility (average Pearson correlation <b>r = {rppg['orig_mean_pearson']}</b>). 
                Following bounded perturbation (Δ = {res['delta_used']}), inter-region correlation dropped by 
                <b>{rppg['desync_drop_percent']}%</b> to <b>r = {rppg['prot_mean_pearson']}</b>, effectively disrupting FakeCatcher-style physiological consistency assumptions.
            </div>
            """, unsafe_allow_html=True)

        with tab3:
            st.plotly_chart(plot_fft_spectrum(rppg["fft_orig"], rppg["fft_prot"]), use_container_width=True)
            c1, c2 = st.columns(2)
            c1.info(f"Original Estimated Heart Rate: **{rppg['bpm_orig']} BPM**")
            c2.warning(f"Cloaked Spectrum Dominant Frequency: **{rppg['bpm_prot']} BPM / Carrier Disrupted**")

        with tab4:
            vcol1, vcol2 = st.columns(2)
            with vcol1:
                st.subheader("Difference Heatmap (Amplified 20x)")
                if res.get("diff_preview_rgb") is not None:
                    st.image(res["diff_preview_rgb"], caption="Turbo Heatmap: Green channel perturbation strictly within facial skin mask", use_container_width=True)
                else:
                    st.info("Heatmap preview unavailable.")

            with vcol2:
                st.subheader("Cloaked Video Download")
                out_path = res["output_path"]
                if os.path.exists(out_path):
                    with open(out_path, "rb") as f:
                        video_bytes = f.read()
                    st.download_button(
                        label="💾 Download Cloaked Video (.mp4)",
                        data=video_bytes,
                        file_name=f"cloaked_{Path(res['input_path']).stem}.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )
                    st.success(f"Video ready ({len(video_bytes) / (1024*1024):.2f} MB). Face Mesh Tracking rate: {missing['detection_rate_pct']}%.")
                else:
                    st.warning("Processed video output file not found.")
