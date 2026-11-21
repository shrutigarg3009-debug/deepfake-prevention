# ⚡ PulseShield: Proactive Biometric Video Cloaking & AI-Powered Facial Identity Protection

[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.41.1-red.svg)](https://streamlit.io/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.21-teal.svg)](https://mediapipe.dev/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.10.0-green.svg)](https://opencv.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

---

## 1. Project Overview

**PulseShield** is a cybersecurity-oriented research application designed to evaluate proactive facial identity protection against unauthorized AI manipulation, generative deepfakes, and automated facial scraping.

The platform investigates **remote photoplethysmography (rPPG)**: human blood volume variations during the cardiac cycle produce subtle reflectance shifts in facial skin, primarily in the green-light spectrum (540–575 nm) due to hemoglobin absorption. Contemporary deepfake detectors (such as *FakeCatcher* by Ciftci et al.) exploit cross-region physiological consistency to identify synthetic faces.

PulseShield explores whether subtle, bounded temporal modifications ($\Delta \in [1.0, 4.0]$) restricted strictly to facial skin ROIs (Forehead, Left Cheek, Right Cheek) can intentionally desynchronize physiological signals—dismantling classifier assumptions—while preserving visual quality (PSNR $> 42\text{ dB}$, SSIM $> 0.98$).

---

## 2. Key Architecture & Features

### 🛡️ Module Highlights
1. **Interactive Cybersecurity UI**: Dark navy/black theme (`#0A0E17`), electric cyan (`#00F0FF`) and purple highlights, glassmorphism dashboard cards, and monospace performance telemetry.
2. **Proactive Video Cloaking Engine (Modules A–D)**:
   - MediaPipe 468-point FaceMesh tracking with validated anatomical ROIs:
     - Left cheek: `[116, 123, 147, 213, 138, 135, 169, 170]`
     - Right cheek: `[345, 352, 376, 433, 367, 364, 394, 395]`
     - Forehead: `[10, 338, 297, 332, 284, 9, 54, 103, 67, 109]`
   - Binary skin mask generation via `cv2.fillPoly`.
   - Missing-face tracking cache ($K=5$ stale frames) with displacement verification.
   - Bounded green-channel perturbation engine ($\Delta \in [1.0, 4.0]$).
   - 4 Perturbation modes: Temporal Sinusoidal Desync, Inter-Region Phase Scrambler, Bounded Jitter, Hybrid Multi-Frequency Injection.
   - 3-ROI rPPG extraction, Butterworth bandpass filtering (0.7–3.5 Hz), and Fast Fourier Transform (FFT) power spectra.
   - FakeCatcher inter-region Pearson correlation comparison heatmaps and desynchronization drop % metric.
   - Objective quality verification: PSNR, SSIM, MSE, Max Error ($L_\infty$), and visual difference heatmap (Turbo colormap).
3. **Live Webcam Biometric Cloaker**: Real-time snapshot cloaking with live wireframe debug overlay and difference heatmap.
4. **Photo Protection Suite**: Static portrait cloaking with Fourier phase modulation and invisible C2PA-style cryptographic watermarks.
5. **AI Misuse Scanner**: Geometric facial landmark descriptor matching against SQLite registered identities with automated deepfake threat rating (CRITICAL, WARNING, LOW, VERIFIED).
6. **Forensic Image Authenticity Lab**: Error Level Analysis (ELA), Laplacian noise residual modeling, 2D Fourier high-frequency grid detection, and EXIF software tampering audit.
7. **SQLite Database Explorer**: Complete persistent audit trail of cloaking jobs, scans, registered identities, and security alerts.
8. **Live Security Threat Feed**: Alert center with severity badges and incident logging.
9. **Interactive Whitepaper & Research Guide**: Hemodynamic theory (Beer-Lambert law), mathematical formulations, and explicit technical limitations.

---

## 3. Technology Stack & Pinned Baseline

```txt
streamlit==1.41.1
opencv-python==4.10.0.84
mediapipe==0.10.21
numpy==1.26.4
scipy==1.13.1
plotly==5.24.1
Pillow==10.4.0
```

---

## 4. Quick Start & Execution

### Running the Application

Double-click `run_pulseshield.bat` or run:

```powershell
streamlit run app.py --server.port=8501
```

Then open your browser at:
```
http://localhost:8501
```

### Running the Automated Test Suite

```powershell
python test_pulseshield.py
```

---

## 5. Directory Structure

```
pulseshield/
├── app.py                      # Main Streamlit application and view router
├── config.py                   # Landmark definitions, parameters, theme colors
├── database.py                 # SQLite database models, CRUD, and initial seed
├── requirements.txt            # Pinned dependencies
├── run_pulseshield.bat         # Single-click Windows launcher
├── test_pulseshield.py         # End-to-end automated test suite
├── modules/
│   ├── face_mesh_detector.py   # MediaPipe FaceMesh, ROI masking, missing-face cache
│   ├── perturbation_engine.py  # Green-channel cloaking engine & perceptual metrics
│   ├── rppg_extractor.py       # rPPG signal extraction, filtering, FFT, Pearson correlation
│   ├── video_processor.py      # Video I/O pipeline, tempfile management, progress reporting
│   ├── photo_protector.py      # Static photo cloaking & cryptographic provenance
│   ├── image_authenticity.py   # ELA, noise residual, 2D FFT, EXIF inspector
│   └── misuse_scanner.py       # Biometric identity matcher & deepfake risk evaluator
├── ui/
│   ├── styles.py               # Dark cyberpunk & glassmorphism custom CSS
│   ├── components.py           # Header, metric cards, Plotly waveforms, heatmaps, gauges
│   └── views/
│       ├── dashboard_view.py
│       ├── video_view.py
│       ├── webcam_view.py
│       ├── photo_view.py
│       ├── scanner_view.py
│       ├── verification_view.py
│       ├── history_view.py
│       ├── notifications_view.py
│       └── how_it_works_view.py
└── sample_data/                # Pre-generated synthetic media for instant 1-click testing
    ├── sample_pulse_face.mp4   # 72 BPM synthetic physiological face video
    ├── sample_portrait.jpg     # Authentic portrait benchmark
    ├── sample_deepfake_suspect.jpg # Synthetic face-swap test image
    └── generate_sample_media.py
```

---

## 6. Experimental Findings & Disclaimers

> **RESEARCH NOTICE**:
> 1. PulseShield is an experimental prototype investigating biometric signal cloaking.
> 2. Perturbation of the green reflectance channel is evaluated as a potential countermeasure against physiological signal detectors (e.g. FakeCatcher). It does **not** guarantee prevention of all generative AI, GAN, or diffusion-based deepfake architectures.
> 3. Visual quality remains virtually lossless (PSNR $> 42\text{ dB}$, SSIM $> 0.98$).
> 4. Real-world performance may vary under non-uniform illumination, dynamic head motion, or extreme video compression quantization.
