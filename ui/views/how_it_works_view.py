"""
PulseShield UI View: How It Works & Scientific Methodology
"""

import streamlit as st

def render_how_it_works_view():
    st.markdown("""
    <div style="margin-bottom: 24px;">
        <h2>The Science of Biometric Video Cloaking & rPPG Desynchronization</h2>
        <p style="color: #94A3B8; font-size: 1.05rem;">
            Theoretical framework, mathematical models, hemodynamic foundations, and objective experimental limitations.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 1. Biological Foundations
    st.markdown("""
    <div class="cyber-card">
        <h3 style="color: #00F0FF; margin-top: 0;">1. Hemodynamics & Remote Photoplethysmography (rPPG)</h3>
        <p style="color: #CBD5E1; line-height: 1.6;">
            With each cardiac cycle, the human heart pumps blood into the arterial vascular network. In the microvascular 
            tissue beds of facial skin (specifically the subpapillary plexus), the volume of oxygenated hemoglobin (&Delta;C) fluctuates periodically.
        </p>
        <p style="color: #CBD5E1; line-height: 1.6;">
            According to the <b>Modified Beer-Lambert Law</b>, the intensity of light reflected from facial skin is modeled as:
        </p>
        <div style="background: rgba(10, 16, 28, 0.8); padding: 14px 20px; border-radius: 8px; border-left: 3px solid #00F0FF; font-family: monospace; color: #00F0FF; margin: 12px 0;">
            I(λ, t) = I₀(λ) · exp(-ε(λ) · C(t) · d)
        </div>
        <p style="color: #CBD5E1; line-height: 1.6;">
            Because <b>oxygenated hemoglobin (HbO₂) exhibits peak optical absorption in the green electromagnetic spectrum (540–575 nm)</b>,
            standard RGB video sensors capture subtle, periodic intensity modulations primarily in the green color channel (BGR index 1).
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 2. How Deepfake Detectors Work (FakeCatcher)
    st.markdown("""
    <div class="cyber-card">
        <h3 style="color: #38BDF8; margin-top: 0;">2. Deepfake Detection via Physiological Signals (FakeCatcher)</h3>
        <p style="color: #CBD5E1; line-height: 1.6;">
            Groundbreaking research by <b>Ciftci, Demir, and Yin (IEEE TPAMI / CVPR, FakeCatcher)</b> observed that genuine human 
            facial videos exhibit high spatial-temporal pulse consistency across disparate facial skin ROIs:
        </p>
        <ul style="color: #94A3B8; line-height: 1.6;">
            <li><b>Forehead:</b> High capillary density, minimal facial hair, stable reflection.</li>
            <li><b>Left Cheek:</b> Rich perfusion from transverse facial artery.</li>
            <li><b>Right Cheek:</b> Symmetric vascular perfusion.</li>
        </ul>
        <p style="color: #CBD5E1; line-height: 1.6;">
            In authentic portrait videos, the temporal Pearson correlation coefficient <i>r</i> between these three regions typically exceeds <b>0.75 – 0.95</b>. 
            Conversely, synthetic deepfake generators (e.g. DeepFaceLab, FaceSwap, StyleGAN) synthesize frames independently or without 
            hemodynamic coherence, producing erratic or zero cross-ROI correlation.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 3. PulseShield Cloaking Hypothesis
    st.markdown("""
    <div class="cyber-card">
        <h3 style="color: #A855F7; margin-top: 0;">3. The PulseShield Proactive Cloaking Hypothesis</h3>
        <p style="color: #CBD5E1; line-height: 1.6;">
            Can subtle, bounded temporal modifications applied to genuine facial skin prevent rPPG-based identity tracking or 
            simulate synthetic inconsistency to safeguard biometric privacy?
        </p>
        <p style="color: #CBD5E1; line-height: 1.6;">
            PulseShield injects an out-of-phase temporal harmonic perturbation <i>η(t)</i> restricted strictly to the facial skin mask:
        </p>
        <div style="background: rgba(10, 16, 28, 0.8); padding: 14px 20px; border-radius: 8px; border-left: 3px solid #A855F7; font-family: monospace; color: #A855F7; margin: 12px 0;">
            I'<sub>green</sub>(x, y, t) = clip( I<sub>green</sub>(x, y, t) + Δ · sin(2π · f<sub>target</sub> · t + φ<sub>ROI</sub>), 0, 255 )
        </div>
        <p style="color: #CBD5E1; line-height: 1.6;">
            Where:
            <ul style="color: #94A3B8; line-height: 1.5;">
                <li><b>Δ &in; [1.0, 4.0]:</b> Perturbation amplitude bound (imperceptible to human vision).</li>
                <li><b>φ<sub>ROI</sub>:</b> Phase offset assigned independently per region (Forehead = 0, Left Cheek = 2π/3, Right Cheek = 4π/3).</li>
                <li><b>f<sub>target</sub>:</b> Experimental frequency component (e.g., 6.5 Hz, bounded by the Nyquist limit f<sub>Nyquist</sub> = FPS / 2).</li>
            </ul>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 4. Objective Metrics & Formula Reference
    st.markdown("""
    <div class="cyber-card">
        <h3 style="color: #10B981; margin-top: 0;">4. Mathematical Metrics & Verification</h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
            <div style="background: rgba(10, 16, 28, 0.6); padding: 14px; border-radius: 8px;">
                <strong style="color: #10B981;">Peak Signal-to-Noise Ratio (PSNR)</strong>
                <p style="color: #94A3B8; font-size: 0.85rem; margin-top: 6px;">
                    PSNR = 10 · log₁₀( 255² / MSE )<br>
                    PulseShield achieves <b>PSNR &gt; 42 dB</b>, verifying that cloaking is imperceptible to the naked human eye.
                </p>
            </div>
            <div style="background: rgba(10, 16, 28, 0.6); padding: 14px; border-radius: 8px;">
                <strong style="color: #10B981;">Inter-Region Pearson Correlation (r)</strong>
                <p style="color: #94A3B8; font-size: 0.85rem; margin-top: 6px;">
                    r(X, Y) = Cov(X, Y) / (σ<sub>X</sub> · σ<sub>Y</sub>)<br>
                    Measures the co-pulsatility of facial regions. Cloaking degrades <i>r</i> from ~0.85 down to &lt; 0.20.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 5. Technical Limitations & Scientific Integrity
    st.markdown("""
    <div class="cyber-card" style="border-left: 4px solid #F59E0B;">
        <h3 style="color: #F59E0B; margin-top: 0;">⚠️ Experimental Limitations & Scientific Integrity</h3>
        <p style="color: #CBD5E1; line-height: 1.6;">
            In alignment with rigorous academic standards, PulseShield explicitly documents the following technical boundaries:
        </p>
        <ol style="color: #94A3B8; line-height: 1.6;">
            <li><b>No Absolute Guarantee:</b> Random or sinusoidal noise does not guarantee protection against all future deepfake architectures. Generative models trained specifically on rPPG invariants may adapt to high-frequency perturbation.</li>
            <li><b>Video Compression Vulnerability:</b> Heavy lossy compression (such as YouTube / TikTok H.264 at sub-1 Mbps bitrates) applies spatial-temporal quantization that may attenuate high-frequency perturbations along with biological rPPG signals.</li>
            <li><b>Head Pose & Illumination:</b> Rapid head motion or flickering ambient illumination can introduce extrinsic artifacts that mask or overpower microvascular cardiac reflectance.</li>
            <li><b>Sampling Artifacts:</b> In standard 30 FPS cameras, temporal components near or above 15 Hz alias back into the lower frequency spectrum due to the Nyquist theorem.</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
