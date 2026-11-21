"""
Module D: Remote Photoplethysmography (rPPG) Extraction & Evaluation Engine
Extracts temporal mean green-channel reflectance signals from facial ROIs (Forehead, Left Cheek,
Right Cheek), computes bandpass filtering, Fast Fourier Transform (FFT) power spectra, and
evaluates physiological consistency via Pearson inter-region correlation matrices (FakeCatcher metric).
"""

import numpy as np
import scipy.signal as signal
from typing import Dict, List, Tuple, Any, Optional

class RPPGExtractor:
    """
    Extracts and evaluates rPPG cardiac signals from original and cloaked facial skin regions.
    """

    def __init__(self, fps: float = 30.0):
        self.fps = max(fps, 10.0)

    @staticmethod
    def extract_mean_roi_green(frame_bgr: np.ndarray, mask: np.ndarray) -> float:
        """
        Extracts the spatial mean green-channel intensity within the given binary mask.
        Returns 0.0 if mask has no pixels.
        """
        green_channel = frame_bgr[:, :, 1]
        valid_pixels = green_channel[mask > 0]
        if len(valid_pixels) == 0:
            return 0.0
        return float(np.mean(valid_pixels))

    @staticmethod
    def detrend_signal(raw_signal: np.ndarray, fps: float, low_cut: float = 0.7, high_cut: float = 3.5) -> np.ndarray:
        """
        Applies zero-phase Butterworth bandpass filter in the physiological cardiac range (0.7 - 3.5 Hz).
        If the signal is too short for filtering, falls back to mean-centering and linear detrending.
        """
        if len(raw_signal) < 15:
            return raw_signal - np.mean(raw_signal)

        # Basic linear detrend
        detrended = signal.detrend(raw_signal)

        # Check Nyquist condition
        nyquist = fps / 2.0
        if high_cut >= nyquist:
            high_cut = nyquist * 0.95
        if low_cut >= high_cut:
            low_cut = high_cut * 0.2

        try:
            # 3rd-order Butterworth bandpass filter
            b, a = signal.butter(3, [low_cut / nyquist, high_cut / nyquist], btype='bandpass')
            filtered = signal.filtfilt(b, a, detrended)
            return filtered
        except Exception:
            # Fallback to normalized moving average subtraction
            window = max(3, int(fps * 0.5))
            if window % 2 == 0:
                window += 1
            smooth = np.convolve(detrended, np.ones(window) / window, mode='same')
            return detrended - smooth

    @staticmethod
    def compute_pearson_matrix(signals_dict: Dict[str, np.ndarray]) -> Tuple[np.ndarray, List[str], float]:
        """
        Computes pairwise Pearson correlation coefficients between facial ROIs.
        Returns:
            matrix: 3x3 correlation matrix
            labels: ROI region names
            mean_cross_correlation: Average off-diagonal correlation (FakeCatcher consistency metric)
        """
        labels = ["Forehead", "Left Cheek", "Right Cheek"]
        sigs = [signals_dict.get("forehead", np.zeros(10)),
                signals_dict.get("left_cheek", np.zeros(10)),
                signals_dict.get("right_cheek", np.zeros(10))]

        # Ensure all signals have equal length
        min_len = min(len(s) for s in sigs)
        if min_len < 3:
            return np.eye(3), labels, 0.0

        sigs_trimmed = [s[:min_len] for s in sigs]
        data = np.array(sigs_trimmed)

        # Handle zero-variance / constant signal safely
        stds = np.std(data, axis=1)
        if np.any(stds == 0):
            # Add tiny epsilon to avoid division by zero
            data = data + np.random.normal(0, 1e-6, data.shape)

        corr_matrix = np.corrcoef(data)
        np.nan_to_num(corr_matrix, copy=False, nan=0.0)

        # Off-diagonal elements (0,1), (0,2), (1,2)
        off_diag = [corr_matrix[0, 1], corr_matrix[0, 2], corr_matrix[1, 2]]
        mean_cross = float(np.mean(off_diag))

        return corr_matrix, labels, round(mean_cross, 3)

    @staticmethod
    def compute_fft_spectrum(sig: np.ndarray, fps: float) -> Tuple[np.ndarray, np.ndarray, float]:
        """
        Computes the Fast Fourier Transform (FFT) power spectrum and identifies the dominant frequency.
        Returns:
            freqs: Array of positive frequencies (Hz)
            power: Normalized magnitude spectrum
            peak_bpm: Estimated heart rate in beats per minute (BPM)
        """
        n = len(sig)
        if n < 4:
            return np.array([1.0]), np.array([0.0]), 72.0

        # Zero-pad for higher frequency resolution
        n_fft = max(n, 256)
        fft_vals = np.fft.rfft(sig, n=n_fft)
        freqs = np.fft.rfftfreq(n_fft, d=1.0 / fps)
        magnitude = np.abs(fft_vals)

        # Restrict peak search to physiological band (0.7 - 3.5 Hz -> 42 - 210 bpm)
        valid_idx = np.where((freqs >= 0.7) & (freqs <= 3.5))[0]
        if len(valid_idx) > 0:
            peak_idx = valid_idx[np.argmax(magnitude[valid_idx])]
            peak_freq = freqs[peak_idx]
            peak_bpm = peak_freq * 60.0
        else:
            peak_bpm = 72.0

        # Normalize magnitude to [0, 1]
        max_mag = np.max(magnitude)
        power = magnitude / max_mag if max_mag > 0 else magnitude

        return freqs, power, round(float(peak_bpm), 1)

    @classmethod
    def evaluate_video_pair(
        cls,
        orig_signals: Dict[str, np.ndarray],
        prot_signals: Dict[str, np.ndarray],
        fps: float
    ) -> Dict[str, Any]:
        """
        Full scientific comparative evaluation of original vs cloaked rPPG signals.
        Calculates filtered waveforms, correlation matrices, FakeCatcher drop, and FFT spectra.
        """
        # Detrend and filter
        orig_filtered = {k: cls.detrend_signal(v, fps) for k, v in orig_signals.items()}
        prot_filtered = {k: cls.detrend_signal(v, fps) for k, v in prot_signals.items()}

        # Correlation matrices
        orig_corr, labels, orig_mean_r = cls.compute_pearson_matrix(orig_filtered)
        prot_corr, _, prot_mean_r = cls.compute_pearson_matrix(prot_filtered)

        # Desynchronization Drop %
        # In natural human skin, inter-region r is high (0.75 - 0.95).
        # Cloaking introduces phase/amplitude disruption, causing r to drop towards 0 or negative.
        if orig_mean_r > 0:
            desync_drop = max(0.0, ((orig_mean_r - prot_mean_r) / orig_mean_r) * 100.0)
        else:
            desync_drop = 0.0

        # FFT Power spectra for Forehead
        freqs_orig, fft_orig, bpm_orig = cls.compute_fft_spectrum(orig_filtered.get("forehead", np.zeros(10)), fps)
        freqs_prot, fft_prot, bpm_prot = cls.compute_fft_spectrum(prot_filtered.get("forehead", np.zeros(10)), fps)

        return {
            "fps": fps,
            "orig_raw": orig_signals,
            "prot_raw": prot_signals,
            "orig_filtered": orig_filtered,
            "prot_filtered": prot_filtered,
            "orig_corr_matrix": orig_corr,
            "prot_corr_matrix": prot_corr,
            "roi_labels": labels,
            "orig_mean_pearson": orig_mean_r,
            "prot_mean_pearson": prot_mean_r,
            "desync_drop_percent": round(desync_drop, 1),
            "bpm_orig": bpm_orig,
            "bpm_prot": bpm_prot,
            "fft_orig": {"freqs": freqs_orig, "power": fft_orig},
            "fft_prot": {"freqs": freqs_prot, "power": fft_prot},
            "fakecatcher_bypass_status": (
                "CLOAKED (rPPG Desynchronized)" if prot_mean_r < 0.35 else "PARTIAL PROTECTION"
            )
        }
