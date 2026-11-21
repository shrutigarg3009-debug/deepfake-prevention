"""
Module: Image Authenticity Verification Engine
Forensic analysis suite incorporating Error Level Analysis (ELA), high-frequency noise
residuals, 2D Fast Fourier Transform (FFT) grid artifact detection, and EXIF metadata checks.
"""

import cv2
import numpy as np
import os
import tempfile
from PIL import Image, ExifTags
from typing import Dict, Any, Tuple, Optional

class AuthenticityVerifier:
    """
    Forensic image analysis for deepfake and manipulation detection.
    """

    @staticmethod
    def error_level_analysis(image_bgr: np.ndarray, quality: int = 90, scale: float = 15.0) -> Tuple[np.ndarray, float]:
        """
        Computes Error Level Analysis (ELA) by re-compressing at specified JPEG quality.
        Returns:
            ela_map: Amplified BGR difference image
            ela_score: Mean error level metric (higher indicates higher compression disparity)
        """
        # Save temporary JPEG recompression
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            cv2.imwrite(tmp_path, image_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
            recompressed = cv2.imread(tmp_path)
            
            # Compute absolute difference
            diff = cv2.absdiff(image_bgr, recompressed).astype(np.float32)
            
            # Amplification for visual evaluation
            amplified = np.clip(diff * scale, 0.0, 255.0).astype(np.uint8)
            ela_score = float(np.mean(diff))
            ela_std = float(np.std(diff))

            # Apply heatmap color
            gray_ela = cv2.cvtColor(amplified, cv2.COLOR_BGR2GRAY)
            ela_colored = cv2.applyColorMap(gray_ela, cv2.COLORMAP_INFERNO)

            return ela_colored, round(ela_score, 2), round(ela_std, 2)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    @staticmethod
    def noise_residual_analysis(image_bgr: np.ndarray) -> Tuple[np.ndarray, float, float]:
        """
        Extracts high-frequency noise residual using Laplacian operator.
        Evaluates texture smoothness vs authentic sensor noise across facial region.
        """
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        laplacian = cv2.Laplacian(gray, cv2.CV_64F, ksize=3)
        variance = float(laplacian.var())

        # Facial center texture variance (deepfakes suffer from unnatural smoothness)
        face_roi = gray[int(h*0.35):int(h*0.75), int(w*0.30):int(w*0.70)]
        face_variance = float(cv2.Laplacian(face_roi, cv2.CV_64F).var()) if face_roi.size > 0 else variance

        # Normalize laplacian to [0, 255] for visual map
        norm_lap = np.clip(np.abs(laplacian) * 3.0, 0.0, 255.0).astype(np.uint8)
        colored_noise = cv2.applyColorMap(norm_lap, cv2.COLORMAP_VIRIDIS)

        return colored_noise, round(variance, 2), round(face_variance, 2)

    @staticmethod
    def fft_spectrum_analysis(image_bgr: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Computes 2D Fast Fourier Transform magnitude spectrum.
        Detects periodic frequency spikes common in GAN upsampling artifacts.
        """
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        
        f = np.fft.fft2(gray)
        fshift = np.fft.fftshift(f)
        magnitude = 20.0 * np.log(np.abs(fshift) + 1.0)
        
        # Normalize to 0-255
        norm_mag = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        colored_fft = cv2.applyColorMap(norm_mag, cv2.COLORMAP_MAGMA)

        # High-frequency energy ratio metric
        crow, ccol = h // 2, w // 2
        r = min(crow, ccol) // 3
        y, x = np.ogrid[:h, :w]
        mask_high = ((x - ccol) ** 2 + (y - crow) ** 2) > (r ** 2)
        
        high_freq_ratio = float(np.mean(np.abs(fshift)[mask_high]) / (np.mean(np.abs(fshift)) + 1e-6))
        return colored_fft, round(high_freq_ratio, 3)

    @staticmethod
    def check_metadata(file_bytes: bytes) -> Dict[str, Any]:
        """Inspects EXIF metadata tags for digital editing software traces."""
        import io
        exif_info = {}
        editing_signatures = [
            "photoshop", "gimp", "canva", "lightroom", "diffusion",
            "midjourney", "dall-e", "deepface", "faceswap", "inpaint", "synthetic"
        ]
        software_found = []

        try:
            image = Image.open(io.BytesIO(file_bytes))
            raw_exif = image._getexif()
            if raw_exif:
                for tag_id, value in raw_exif.items():
                    tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                    exif_info[tag_name] = str(value)[:80]
                    val_str = str(value).lower()
                    for sig in editing_signatures:
                        if sig in val_str:
                            software_found.append(f"{tag_name}: {value}")

            has_camera_data = bool("Make" in exif_info or "Model" in exif_info)
            return {
                "has_exif": bool(raw_exif),
                "has_camera_data": has_camera_data,
                "editing_software_detected": software_found,
                "tags_summary": {k: exif_info[k] for k in list(exif_info.keys())[:8]},
            }
        except Exception:
            return {
                "has_exif": False,
                "has_camera_data": False,
                "editing_software_detected": [],
                "tags_summary": {},
            }

    @classmethod
    def verify_image(cls, image_bgr: np.ndarray, raw_bytes: Optional[bytes] = None) -> Dict[str, Any]:
        """
        Executes complete forensic suite and computes composite authenticity index.
        """
        # 1. ELA
        ela_map, ela_score, ela_std = cls.error_level_analysis(image_bgr)

        # 2. Noise Residual
        noise_map, noise_variance, face_variance = cls.noise_residual_analysis(image_bgr)

        # 3. 2D FFT
        fft_map, fft_ratio = cls.fft_spectrum_analysis(image_bgr)

        # 4. Metadata
        metadata_res = cls.check_metadata(raw_bytes) if raw_bytes else {
            "has_exif": True, "has_camera_data": True, "editing_software_detected": [], "tags_summary": {}
        }

        # 5. Composite Authenticity Score Calculation (0 - 100%)
        # Base authentic score = 88.0
        score = 88.0

        # ELA non-uniformity anomaly evaluation:
        if ela_score > 2.8:
            score -= min(40.0, (ela_score - 2.8) * 12.0)
        if ela_std > 2.5:
            score -= min(25.0, (ela_std - 2.5) * 8.0)

        # Facial texture smoothing penalty (characteristic of GANs and synthetic face-swaps):
        if face_variance < 500.0:
            score -= 35.0  # Synthetic smoothing / deepfake inpainting
        elif face_variance < 800.0:
            score -= 15.0

        # Overall noise variance evaluation:
        if noise_variance > 10000.0:
            score -= 15.0

        # FFT artifact penalty
        if fft_ratio > 0.68 or fft_ratio < 0.05:
            score -= 10.0

        # Metadata editing software penalty
        if metadata_res.get("editing_software_detected"):
            score -= 25.0

        # Clamp score
        final_score = round(float(np.clip(score, 5.0, 99.0)), 1)

        # Verdict
        if final_score >= 75.0:
            verdict = "Authentic Image"
            confidence = "High"
            badge_color = "#10B981"
        elif final_score >= 50.0:
            verdict = "Suspicious / Modified"
            confidence = "Moderate"
            badge_color = "#F59E0B"
        else:
            verdict = "Likely Synthetic / Deepfake"
            confidence = "High"
            badge_color = "#EF4444"

        return {
            "authenticity_score": final_score,
            "verdict": verdict,
            "confidence": confidence,
            "badge_color": badge_color,
            "metrics": {
                "ela_score": ela_score,
                "noise_variance": noise_variance,
                "fft_high_freq_ratio": fft_ratio,
            },
            "metadata": metadata_res,
            "visualizations": {
                "orig_rgb": cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB),
                "ela_rgb": cv2.cvtColor(ela_map, cv2.COLOR_BGR2RGB),
                "noise_rgb": cv2.cvtColor(noise_map, cv2.COLOR_BGR2RGB),
                "fft_rgb": cv2.cvtColor(fft_map, cv2.COLOR_BGR2RGB),
            }
        }
