"""
Module C: Experimental Green-Channel Biometric Perturbation Engine
Implements bounded, temporal, and region-specific perturbations in the green reflectance
channel to experimentally evaluate rPPG signal desynchronization and FakeCatcher robustness.
Preserves non-skin pixels, geometry, and calculates perceptual quality metrics (PSNR, SSIM, MSE).
"""

import numpy as np
import cv2
from typing import Dict, Tuple, Optional, Any
from config import DEFAULT_DELTA, DEFAULT_EXPERIMENTAL_FREQ

class PerturbationEngine:
    """
    Experimental green-channel cloaking engine.
    Investigates bounded temporal modifications restricted strictly to facial skin ROIs.
    """

    MODES = [
        "Temporal Sinusoidal Desynchronization",
        "Inter-Region Phase Scrambler",
        "Bounded Pseudorandom Jitter",
        "Hybrid Multi-Frequency Injection",
    ]

    def __init__(self, seed: Optional[int] = 42):
        self.seed = seed
        self.rng = np.random.RandomState(seed) if seed is not None else np.random.RandomState()

    def set_seed(self, seed: Optional[int]) -> None:
        self.seed = seed
        self.rng = np.random.RandomState(seed) if seed is not None else np.random.RandomState()

    def apply_perturbation(
        self,
        frame_bgr: np.ndarray,
        masks: Dict[str, np.ndarray],
        frame_idx: int,
        fps: float,
        delta: float = DEFAULT_DELTA,
        mode: str = "Temporal Sinusoidal Desynchronization",
        experimental_freq: float = DEFAULT_EXPERIMENTAL_FREQ,
    ) -> Tuple[np.ndarray, Dict[str, float]]:
        """
        Applies subtle green-channel perturbation exclusively within the facial skin masks.
        
        Args:
            frame_bgr: uint8 BGR image (H, W, 3)
            masks: Dict of binary uint8 masks ('forehead', 'left_cheek', 'right_cheek', 'combined')
            frame_idx: Current temporal frame index (0, 1, 2, ...)
            fps: Frame rate of the video sequence
            delta: Perturbation amplitude bound (1.0 to 4.0, default 2.0)
            mode: Perturbation strategy name
            experimental_freq: Target disruption frequency (Hz), default 6.5 Hz

        Returns:
            cloaked_frame_bgr: uint8 modified BGR image
            metrics: Dict containing PSNR, SSIM, MSE, Max Absolute Difference (L_inf)
        """
        # Ensure delta is within bounds
        delta = float(np.clip(delta, 0.5, 6.0))
        h, w = frame_bgr.shape[:2]
        
        # 1. Convert frame to float32
        frame_float = frame_bgr.astype(np.float32)
        cloaked_float = frame_float.copy()

        # Extract green channel (BGR index 1)
        green_channel = frame_float[:, :, 1]
        green_cloaked = green_channel.copy()

        # Time parameter in seconds
        t = float(frame_idx) / max(fps, 1.0)
        
        # Check Nyquist frequency condition for scientific accuracy
        nyquist = fps / 2.0
        effective_freq = min(experimental_freq, nyquist * 0.95) if nyquist > 0 else experimental_freq

        # Retrieve region masks
        forehead_mask = (masks.get("forehead", np.zeros((h, w), dtype=np.uint8)) > 0)
        left_mask = (masks.get("left_cheek", np.zeros((h, w), dtype=np.uint8)) > 0)
        right_mask = (masks.get("right_cheek", np.zeros((h, w), dtype=np.uint8)) > 0)
        combined_mask = (masks.get("combined", np.zeros((h, w), dtype=np.uint8)) > 0)

        # Skip if no skin region is detected
        if not np.any(combined_mask):
            return frame_bgr.copy(), {"psnr": 100.0, "ssim": 1.0, "mse": 0.0, "linf": 0.0}

        # 2 & 3. Generate Perturbation according to selected mode
        if mode == "Temporal Sinusoidal Desynchronization":
            # Inject out-of-phase temporal sinusoidal waves across disparate facial regions:
            # Forehead: sin(2*pi*f*t)
            # Left cheek: sin(2*pi*f*t + 2*pi/3)
            # Right cheek: sin(2*pi*f*t + 4*pi/3)
            # This directly dismantles the cross-ROI Pearson correlation assumed by FakeCatcher
            val_forehead = delta * np.sin(2.0 * np.pi * effective_freq * t)
            val_left = delta * np.sin(2.0 * np.pi * effective_freq * t + (2.0 * np.pi / 3.0))
            val_right = delta * np.sin(2.0 * np.pi * effective_freq * t + (4.0 * np.pi / 3.0))

            green_cloaked[forehead_mask] += val_forehead
            green_cloaked[left_mask] += val_left
            green_cloaked[right_mask] += val_right

        elif mode == "Inter-Region Phase Scrambler":
            # Anti-phase modulation between bilateral cheeks and forehead
            # Forehead modulated with f1, cheeks counter-modulated with inverted phase and subtle spatial gradient
            val_f = delta * np.sin(2.0 * np.pi * 3.2 * t)
            val_l = -delta * np.sin(2.0 * np.pi * 3.2 * t + np.pi / 4.0)
            val_r = -delta * np.cos(2.0 * np.pi * 3.2 * t - np.pi / 4.0)

            green_cloaked[forehead_mask] += val_f
            green_cloaked[left_mask] += val_l
            green_cloaked[right_mask] += val_r

        elif mode == "Bounded Pseudorandom Jitter":
            # High-frequency temporal bounded uniform noise ~ U(-delta, delta)
            noise_map = self.rng.uniform(-delta, delta, size=(h, w)).astype(np.float32)
            green_cloaked[combined_mask] += noise_map[combined_mask]

        elif mode == "Hybrid Multi-Frequency Injection":
            # Combines pseudo-cardiac deceptive frequency (~1.3 Hz) with 6.5 Hz bounded carrier
            carrier = 0.6 * delta * np.sin(2.0 * np.pi * effective_freq * t)
            spoofed_cardiac_f = 0.4 * delta * np.sin(2.0 * np.pi * 1.3 * t)
            spoofed_cardiac_l = 0.4 * delta * np.sin(2.0 * np.pi * 1.3 * t + np.pi)  # Counter-phase
            spoofed_cardiac_r = 0.4 * delta * np.sin(2.0 * np.pi * 2.1 * t)          # Incoherent frequency

            green_cloaked[forehead_mask] += (carrier + spoofed_cardiac_f)
            green_cloaked[left_mask] += (carrier + spoofed_cardiac_l)
            green_cloaked[right_mask] += (carrier + spoofed_cardiac_r)

        else:
            # Fallback default: Sinusoidal
            val = delta * np.sin(2.0 * np.pi * effective_freq * t)
            green_cloaked[combined_mask] += val

        # 4 & 5. Enforce boundaries strictly within [0, 255]
        green_cloaked = np.clip(green_cloaked, 0.0, 255.0)
        cloaked_float[:, :, 1] = green_cloaked

        # 6. Convert back to uint8
        cloaked_frame_bgr = np.clip(cloaked_float, 0.0, 255.0).astype(np.uint8)

        # Compute objective perceptual quality metrics
        metrics = self.calculate_metrics(frame_bgr, cloaked_frame_bgr)
        return cloaked_frame_bgr, metrics

    @staticmethod
    def calculate_metrics(img_orig: np.ndarray, img_mod: np.ndarray) -> Dict[str, float]:
        """
        Calculates MSE, PSNR, SSIM, and L_inf maximum absolute error.
        """
        diff = img_orig.astype(np.float64) - img_mod.astype(np.float64)
        mse = float(np.mean(diff ** 2))
        linf = float(np.max(np.abs(diff)))

        if mse == 0:
            return {"psnr": 100.0, "ssim": 1.0, "mse": 0.0, "linf": 0.0}

        # PSNR in decibels (dB)
        psnr = float(10.0 * np.log10((255.0 ** 2) / mse))

        # Structural Similarity Index (SSIM) approximation across channels
        ssim = float(PerturbationEngine._calculate_ssim(img_orig, img_mod))

        return {
            "psnr": round(psnr, 2),
            "ssim": round(ssim, 4),
            "mse": round(mse, 4),
            "linf": round(linf, 2),
        }

    @staticmethod
    def _calculate_ssim(img1: np.ndarray, img2: np.ndarray) -> float:
        """Computes mean SSIM across all color channels."""
        C1 = (0.01 * 255) ** 2
        C2 = (0.03 * 255) ** 2

        img1 = img1.astype(np.float64)
        img2 = img2.astype(np.float64)

        ssim_channels = []
        for c in range(img1.shape[2]):
            ch1 = img1[:, :, c]
            ch2 = img2[:, :, c]

            mu1 = cv2.GaussianBlur(ch1, (11, 11), 1.5)
            mu2 = cv2.GaussianBlur(ch2, (11, 11), 1.5)

            mu1_sq = mu1 ** 2
            mu2_sq = mu2 ** 2
            mu1_mu2 = mu1 * mu2

            sigma1_sq = cv2.GaussianBlur(ch1 ** 2, (11, 11), 1.5) - mu1_sq
            sigma2_sq = cv2.GaussianBlur(ch2 ** 2, (11, 11), 1.5) - mu2_sq
            sigma12 = cv2.GaussianBlur(ch1 * ch2, (11, 11), 1.5) - mu1_mu2

            ssim_map = ((2 * mu1_mu2 + C1) * (2 * sigma12 + C2)) / (
                (mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2)
            )
            ssim_channels.append(np.mean(ssim_map))

        return float(np.mean(ssim_channels))

    @staticmethod
    def generate_difference_heatmap(
        img_orig: np.ndarray, img_mod: np.ndarray, amplification: float = 20.0
    ) -> np.ndarray:
        """
        Creates an amplified visual difference heatmap for debugging and UX demonstration.
        """
        # Absolute difference in green channel
        diff = np.abs(img_orig[:, :, 1].astype(np.float32) - img_mod[:, :, 1].astype(np.float32))
        
        # Amplify for human visibility
        amplified = np.clip(diff * amplification, 0.0, 255.0).astype(np.uint8)
        
        # Apply COLORMAP_JET or COLORMAP_TURBO for cybersecurity visual aesthetics
        heatmap = cv2.applyColorMap(amplified, cv2.COLORMAP_TURBO)
        return heatmap
