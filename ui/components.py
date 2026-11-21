"""
PulseShield Reusable UI Components & Plotly Chart Builders
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, Any, List

def render_header(current_section: str = "Dashboard") -> None:
    """Renders the top branding header and navigation breadcrumb."""
    st.markdown(f"""
    <div class="ps-header">
        <div>
            <div class="ps-logo-text">⚡ PULSESHIELD</div>
            <div style="color: #94A3B8; font-size: 0.88rem; margin-top: 4px;">
                Proactive Biometric Video Cloaking & AI-Powered Facial Identity Protection
            </div>
        </div>
        <div style="text-align: right;">
            <span class="badge-cyan">● ENGINE ACTIVE</span>
            <div style="color: #64748B; font-size: 0.75rem; margin-top: 6px; font-family: monospace;">
                MODE: {current_section.upper()}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_metric_card(label: str, value: Any, delta_text: str = "", badge: str = "cyan") -> None:
    st.markdown(f"""
    <div class="cyber-card stat-box">
        <div class="stat-value">{value}</div>
        <div class="stat-label">{label}</div>
        {f'<div style="margin-top: 8px;"><span class="badge-{badge}">{delta_text}</span></div>' if delta_text else ''}
    </div>
    """, unsafe_allow_html=True)

def plot_rppg_signals(rppg_data: Dict[str, Any]) -> go.Figure:
    """
    Plots interactive 3-ROI temporal signals comparing original vs cloaked rPPG waves.
    """
    orig = rppg_data.get("orig_filtered", {})
    prot = rppg_data.get("prot_filtered", {})
    fps = rppg_data.get("fps", 30.0)

    n_frames = len(orig.get("forehead", []))
    time_axis = np.arange(n_frames) / fps if n_frames > 0 else np.array([])

    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=("Forehead ROI Reflectance (Green)", "Left Cheek ROI Reflectance", "Right Cheek ROI Reflectance")
    )

    colors = {
        "orig_fh": "#00F0FF", "prot_fh": "#FF007F",
        "orig_lc": "#3B82F6", "prot_lc": "#F59E0B",
        "orig_rc": "#10B981", "prot_rc": "#A855F7",
    }

    # Forehead
    fig.add_trace(go.Scatter(x=time_axis, y=orig.get("forehead", []), mode='lines', name='Original Forehead',
                             line=dict(color=colors["orig_fh"], width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=time_axis, y=prot.get("forehead", []), mode='lines', name='Cloaked Forehead',
                             line=dict(color=colors["prot_fh"], width=1.5, dash='dot')), row=1, col=1)

    # Left Cheek
    fig.add_trace(go.Scatter(x=time_axis, y=orig.get("left_cheek", []), mode='lines', name='Original Left Cheek',
                             line=dict(color=colors["orig_lc"], width=2)), row=2, col=1)
    fig.add_trace(go.Scatter(x=time_axis, y=prot.get("left_cheek", []), mode='lines', name='Cloaked Left Cheek',
                             line=dict(color=colors["prot_lc"], width=1.5, dash='dot')), row=2, col=1)

    # Right Cheek
    fig.add_trace(go.Scatter(x=time_axis, y=orig.get("right_cheek", []), mode='lines', name='Original Right Cheek',
                             line=dict(color=colors["orig_rc"], width=2)), row=3, col=1)
    fig.add_trace(go.Scatter(x=time_axis, y=prot.get("right_cheek", []), mode='lines', name='Cloaked Right Cheek',
                             line=dict(color=colors["prot_rc"], width=1.5, dash='dot')), row=3, col=1)

    fig.update_layout(
        height=520,
        margin=dict(l=40, r=20, t=40, b=30),
        paper_bgcolor='rgba(14, 23, 38, 0.4)',
        plot_bgcolor='rgba(10, 16, 28, 0.6)',
        font=dict(color='#94A3B8', family='JetBrains Mono'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis3=dict(title="Time (seconds)"),
    )
    fig.update_yaxes(gridcolor='rgba(255, 255, 255, 0.06)')
    fig.update_xaxes(gridcolor='rgba(255, 255, 255, 0.06)')
    return fig

def plot_correlation_comparison(orig_matrix: np.ndarray, prot_matrix: np.ndarray, labels: List[str]) -> go.Figure:
    """
    Plots dual heatmaps comparing Pearson inter-region correlation matrices (FakeCatcher feature).
    """
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Original (Synchronized Biometrics)", "Cloaked (Desynchronized / Perturbed)"),
        horizontal_spacing=0.15
    )

    # Original
    fig.add_trace(
        go.Heatmap(
            z=orig_matrix,
            x=labels, y=labels,
            colorscale=[[0, "#0A0E17"], [0.5, "#0066FF"], [1, "#00F0FF"]],
            zmin=-1, zmax=1,
            text=[[f"{val:.2f}" for val in row] for row in orig_matrix],
            texttemplate="%{text}",
            colorbar=dict(title="Pearson r", x=0.45)
        ),
        row=1, col=1
    )

    # Protected
    fig.add_trace(
        go.Heatmap(
            z=prot_matrix,
            x=labels, y=labels,
            colorscale=[[0, "#EF4444"], [0.5, "#1E293B"], [1, "#A855F7"]],
            zmin=-1, zmax=1,
            text=[[f"{val:.2f}" for val in row] for row in prot_matrix],
            texttemplate="%{text}",
            colorbar=dict(title="Pearson r", x=1.02)
        ),
        row=1, col=2
    )

    fig.update_layout(
        height=320,
        margin=dict(l=30, r=30, t=50, b=30),
        paper_bgcolor='rgba(14, 23, 38, 0.4)',
        plot_bgcolor='rgba(10, 16, 28, 0.6)',
        font=dict(color='#94A3B8', family='JetBrains Mono')
    )
    return fig

def plot_fft_spectrum(fft_orig: Dict[str, Any], fft_prot: Dict[str, Any]) -> go.Figure:
    """
    Plots FFT Power Spectra comparing dominant cardiac peaks before and after cloaking.
    """
    freqs_o = fft_orig.get("freqs", np.array([]))
    power_o = fft_orig.get("power", np.array([]))
    freqs_p = fft_prot.get("freqs", np.array([]))
    power_p = fft_prot.get("power", np.array([]))

    # Restrict x-axis to 0 - 8 Hz
    mask_o = (freqs_o <= 8.0)
    mask_p = (freqs_p <= 8.0)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=freqs_o[mask_o], y=power_o[mask_o],
        mode='lines', name='Original Cardiac Power Spectrum',
        line=dict(color='#00F0FF', width=2.5),
        fill='tozeroy', fillcolor='rgba(0, 240, 255, 0.12)'
    ))
    fig.add_trace(go.Scatter(
        x=freqs_p[mask_p], y=power_p[mask_p],
        mode='lines', name='Cloaked / Desynchronized Spectrum',
        line=dict(color='#FF007F', width=2, dash='dot'),
        fill='tozeroy', fillcolor='rgba(255, 0, 127, 0.08)'
    ))

    fig.update_layout(
        height=340,
        title="Fast Fourier Transform (FFT) Normalized Power Spectrum",
        xaxis=dict(title="Frequency (Hz)", gridcolor='rgba(255, 255, 255, 0.06)'),
        yaxis=dict(title="Normalized Power", gridcolor='rgba(255, 255, 255, 0.06)'),
        margin=dict(l=40, r=20, t=50, b=30),
        paper_bgcolor='rgba(14, 23, 38, 0.4)',
        plot_bgcolor='rgba(10, 16, 28, 0.6)',
        font=dict(color='#94A3B8', family='JetBrains Mono'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def plot_authenticity_gauge(score: float, verdict: str) -> go.Figure:
    """
    Renders an authenticity gauge meter from 0% (synthetic) to 100% (authentic).
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"Forensic Authenticity: {verdict.upper()}", 'font': {'color': '#F8FAFC', 'size': 16, 'family': 'Inter'}},
        number={'suffix': "%", 'font': {'color': '#00F0FF', 'family': 'JetBrains Mono', 'size': 32}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#94A3B8"},
            'bar': {'color': "#00F0FF", 'thickness': 0.25},
            'bgcolor': "rgba(10, 16, 28, 0.8)",
            'borderwidth': 2,
            'bordercolor': "rgba(0, 240, 255, 0.3)",
            'steps': [
                {'range': [0, 50], 'color': 'rgba(239, 68, 68, 0.3)'},
                {'range': [50, 75], 'color': 'rgba(245, 158, 11, 0.3)'},
                {'range': [75, 100], 'color': 'rgba(16, 185, 129, 0.3)'}
            ],
            'threshold': {
                'line': {'color': "#F8FAFC", 'width': 3},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    fig.update_layout(
        height=260,
        margin=dict(l=30, r=30, t=40, b=20),
        paper_bgcolor='rgba(14, 23, 38, 0.4)',
        font=dict(color='#94A3B8', family='JetBrains Mono')
    )
    return fig
