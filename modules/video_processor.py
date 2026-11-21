"""
Module A: Video Processing Pipeline
Handles video ingestion (MP4, AVI, MOV), validation, frame extraction, MediaPipe FaceMesh
tracking, green-channel perturbation injection, rPPG signal accumulation, and safe H.264/MP4 encoding.
Handles Windows file locking, tempfile cleanup, and progress reporting.
"""

import cv2
import os
import tempfile
import numpy as np
from pathlib import Path
from typing import Dict, Any, Callable, Optional, Tuple, List

from modules.face_mesh_detector import FaceMeshDetector
from modules.perturbation_engine import PerturbationEngine
from modules.rppg_extractor import RPPGExtractor
from config import DEFAULT_DELTA, DEFAULT_EXPERIMENTAL_FREQ, TEMP_MEDIA_DIR

class VideoProcessor:
    SUPPORTED_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
    MAX_FILE_SIZE_MB = 100.0

    def __init__(self):
        self.detector = FaceMeshDetector(max_num_faces=1, refine_landmarks=True)
        self.engine = PerturbationEngine()

    @classmethod
    def validate_file(cls, file_name: str, file_size_bytes: int) -> Tuple[bool, str]:
        ext = Path(file_name).suffix.lower()
        if ext not in cls.SUPPORTED_EXTENSIONS:
            return False, f"Unsupported video format '{ext}'. Supported: {', '.join(cls.SUPPORTED_EXTENSIONS)}"
        
        size_mb = file_size_bytes / (1024 * 1024)
        if size_mb > cls.MAX_FILE_SIZE_MB:
            return False, f"File size ({size_mb:.1f} MB) exceeds maximum allowed limit ({cls.MAX_FILE_SIZE_MB} MB)."
        
        return True, "File valid"

    @staticmethod
    def get_video_metadata(video_path: str) -> Dict[str, Any]:
        """Extracts resolution, FPS, total frame count, and duration from video file."""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return {"valid": False, "error": "Unable to open video stream."}

        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = float(cap.get(cv2.CAP_PROP_FPS))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Fallback if FPS is reported as 0 or nan
        if fps <= 0 or np.isnan(fps):
            fps = 30.0
            
        duration = frame_count / fps if frame_count > 0 else 0.0
        cap.release()

        return {
            "valid": True,
            "width": w,
            "height": h,
            "fps": round(fps, 2),
            "frame_count": frame_count,
            "duration_sec": round(duration, 2),
        }

    def process_video(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        delta: float = DEFAULT_DELTA,
        mode: str = "Temporal Sinusoidal Desynchronization",
        experimental_freq: float = DEFAULT_EXPERIMENTAL_FREQ,
        max_frames: Optional[int] = None,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> Dict[str, Any]:
        """
        Executes end-to-end video cloaking and rPPG extraction.
        
        Returns a rich dictionary containing:
            - output_path: path to the cloaked video
            - metadata: video dimensions, FPS, frames processed
            - rppg_analysis: RPPGExtractor evaluation report
            - perceptual_metrics: mean PSNR, SSIM, MSE, Max Error
            - missing_face_stats: missing face frames and detection rate
        """
        meta = self.get_video_metadata(input_path)
        if not meta.get("valid"):
            raise ValueError(f"Failed to read input video: {meta.get('error')}")

        w, h = meta["width"], meta["height"]
        fps = meta["fps"]
        total_frames = meta["frame_count"]
        if max_frames and max_frames > 0:
            total_frames = min(total_frames, max_frames)

        # Prepare output path safely
        if output_path is None:
            # Create a unique temp file in TEMP_MEDIA_DIR
            out_fd, output_path = tempfile.mkstemp(suffix="_cloaked.mp4", dir=str(TEMP_MEDIA_DIR))
            os.close(out_fd)

        # Determine VideoWriter FourCC codec
        # mp4v is universally supported on Windows OpenCV builds
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

        if not writer.isOpened():
            # Fallback to MJPG or XVID
            fourcc = cv2.VideoWriter_fourcc(*"MJPG")
            output_path = output_path.replace(".mp4", ".avi")
            writer = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

        cap = cv2.VideoCapture(input_path)
        self.detector.reset_tracking()

        # Signal storage
        orig_signals = {"forehead": [], "left_cheek": [], "right_cheek": []}
        prot_signals = {"forehead": [], "left_cheek": [], "right_cheek": []}

        # Perceptual metric accumulators
        psnr_list: List[float] = []
        ssim_list: List[float] = []
        mse_list: List[float] = []
        linf_list: List[float] = []

        frame_idx = 0
        preview_frames: List[np.ndarray] = []
        diff_preview: Optional[np.ndarray] = None

        try:
            while cap.isOpened():
                if max_frames and frame_idx >= max_frames:
                    break

                ret, frame = cap.read()
                if not ret:
                    break

                # 1. Detect facial skin masks with missing-face tracking
                masks, det_meta = self.detector.process_frame(frame)

                # 2. Extract original green reflectance signals
                orig_fh = RPPGExtractor.extract_mean_roi_green(frame, masks["forehead"])
                orig_lc = RPPGExtractor.extract_mean_roi_green(frame, masks["left_cheek"])
                orig_rc = RPPGExtractor.extract_mean_roi_green(frame, masks["right_cheek"])

                orig_signals["forehead"].append(orig_fh)
                orig_signals["left_cheek"].append(orig_lc)
                orig_signals["right_cheek"].append(orig_rc)

                # 3. Apply experimental perturbation engine
                cloaked_frame, metrics = self.engine.apply_perturbation(
                    frame_bgr=frame,
                    masks=masks,
                    frame_idx=frame_idx,
                    fps=fps,
                    delta=delta,
                    mode=mode,
                    experimental_freq=experimental_freq,
                )

                # 4. Extract cloaked green reflectance signals
                prot_fh = RPPGExtractor.extract_mean_roi_green(cloaked_frame, masks["forehead"])
                prot_lc = RPPGExtractor.extract_mean_roi_green(cloaked_frame, masks["left_cheek"])
                prot_rc = RPPGExtractor.extract_mean_roi_green(cloaked_frame, masks["right_cheek"])

                prot_signals["forehead"].append(prot_fh)
                prot_signals["left_cheek"].append(prot_lc)
                prot_signals["right_cheek"].append(prot_rc)

                # Record metrics
                psnr_list.append(metrics["psnr"])
                ssim_list.append(metrics["ssim"])
                mse_list.append(metrics["mse"])
                linf_list.append(metrics["linf"])

                # Store sample preview frame for UI comparison
                if frame_idx == total_frames // 2 or frame_idx == 10:
                    preview_frames.append(cv2.cvtColor(cloaked_frame, cv2.COLOR_BGR2RGB))
                    diff_preview = PerturbationEngine.generate_difference_heatmap(frame, cloaked_frame)

                # Write processed frame to output video
                writer.write(cloaked_frame)
                frame_idx += 1

                # Update progress
                if progress_callback and total_frames > 0:
                    pct = min(1.0, float(frame_idx) / float(total_frames))
                    progress_callback(pct, f"Cloaking frame {frame_idx}/{total_frames} (PSNR: {metrics['psnr']:.1f} dB)...")

        finally:
            cap.release()
            writer.release()

        # Convert signal lists to numpy arrays
        orig_signals_np = {k: np.array(v, dtype=np.float32) for k, v in orig_signals.items()}
        prot_signals_np = {k: np.array(v, dtype=np.float32) for k, v in prot_signals.items()}

        # 5. Evaluate rPPG desynchronization and consistency metrics
        rppg_eval = RPPGExtractor.evaluate_video_pair(orig_signals_np, prot_signals_np, fps)

        # 6. Overall perceptual metrics
        mean_psnr = round(float(np.mean(psnr_list)), 2) if psnr_list else 100.0
        mean_ssim = round(float(np.mean(ssim_list)), 4) if ssim_list else 1.0
        mean_mse = round(float(np.mean(mse_list)), 4) if mse_list else 0.0
        max_linf = round(float(np.max(linf_list)), 2) if linf_list else 0.0

        missing_count = self.detector.total_missing_frames
        detection_rate = round(100.0 * (1.0 - (missing_count / max(1, frame_idx))), 1)

        return {
            "input_path": input_path,
            "output_path": output_path,
            "frames_processed": frame_idx,
            "fps": fps,
            "duration_sec": round(frame_idx / max(1.0, fps), 2),
            "delta_used": delta,
            "perturbation_mode": mode,
            "perceptual_metrics": {
                "mean_psnr": mean_psnr,
                "mean_ssim": mean_ssim,
                "mean_mse": mean_mse,
                "max_linf": max_linf,
            },
            "missing_face_stats": {
                "missing_frames": missing_count,
                "detection_rate_pct": detection_rate,
            },
            "rppg_analysis": rppg_eval,
            "sample_preview_rgb": preview_frames[0] if preview_frames else None,
            "diff_preview_rgb": cv2.cvtColor(diff_preview, cv2.COLOR_BGR2RGB) if diff_preview is not None else None,
        }
