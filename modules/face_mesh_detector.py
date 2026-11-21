"""
Module B: MediaPipe Face Detection & Facial Skin ROI Masking
Detects facial landmarks using MediaPipe FaceMesh, extracts anatomically validated
skin regions (Forehead, Left Cheek, Right Cheek), and generates binary masks with
robust missing-face temporal caching and displacement tracking.
"""

import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from config import (
    LEFT_CHEEK_LANDMARKS,
    RIGHT_CHEEK_LANDMARKS,
    FOREHEAD_LANDMARKS,
    MAX_STALE_FRAMES,
    MAX_FACE_DISPLACEMENT_PX,
)

class FaceMeshDetector:
    def __init__(
        self,
        max_num_faces: int = 1,
        refine_landmarks: bool = True,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ):
        self.max_num_faces = max_num_faces
        self.refine_landmarks = refine_landmarks
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        
        self.mp_face_mesh = None
        self.face_mesh = None
        self._init_mediapipe()

        # Temporal tracking state
        self.last_valid_masks: Optional[Dict[str, np.ndarray]] = None
        self.last_face_center: Optional[Tuple[float, float]] = None
        self.stale_frame_count: int = 0
        self.total_missing_frames: int = 0
        self.total_frames_processed: int = 0

    def _init_mediapipe(self) -> None:
        try:
            import mediapipe as mp
            self.mp_face_mesh = mp.solutions.face_mesh
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                max_num_faces=self.max_num_faces,
                refine_landmarks=self.refine_landmarks,
                min_detection_confidence=self.min_detection_confidence,
                min_tracking_confidence=self.min_tracking_confidence,
            )
        except Exception as e:
            # Will be logged or initialized when mediapipe is ready
            self.face_mesh = None

    def reset_tracking(self) -> None:
        """Reset temporal mask cache and counters for a new video or stream."""
        self.last_valid_masks = None
        self.last_face_center = None
        self.stale_frame_count = 0
        self.total_missing_frames = 0
        self.total_frames_processed = 0

    def _landmarks_to_points(
        self, landmarks: Any, indices: List[int], frame_w: int, frame_h: int
    ) -> np.ndarray:
        """Convert normalized MediaPipe landmark coordinates to pixel (x, y) integers."""
        points = []
        for idx in indices:
            if idx < len(landmarks):
                lm = landmarks[idx]
                px = int(np.clip(lm.x * frame_w, 0, frame_w - 1))
                py = int(np.clip(lm.y * frame_h, 0, frame_h - 1))
                points.append([px, py])
        return np.array(points, dtype=np.int32)

    def _calculate_face_center(self, landmarks: Any, frame_w: int, frame_h: int) -> Tuple[float, float]:
        """Compute face centroid using key central landmarks (nose tip 1, glabella 9, chin 152)."""
        center_indices = [1, 9, 152, 168]
        xs = [landmarks[idx].x * frame_w for idx in center_indices if idx < len(landmarks)]
        ys = [landmarks[idx].y * frame_h for idx in center_indices if idx < len(landmarks)]
        if xs and ys:
            return float(np.mean(xs)), float(np.mean(ys))
        return (frame_w / 2.0, frame_h / 2.0)

    def process_frame(
        self, frame_bgr: np.ndarray
    ) -> Tuple[Dict[str, np.ndarray], Dict[str, Any]]:
        """
        Processes a single BGR frame.
        Returns:
            masks: Dict with keys 'forehead', 'left_cheek', 'right_cheek', 'combined'
                   (each is a uint8 binary mask of shape (H, W), values 0 or 255)
            metadata: Dict containing face detection status, landmarks, displacement, etc.
        """
        self.total_frames_processed += 1
        h, w = frame_bgr.shape[:2]
        
        # Blank masks if detection fails
        empty_mask = np.zeros((h, w), dtype=np.uint8)
        empty_masks = {
            "forehead": empty_mask.copy(),
            "left_cheek": empty_mask.copy(),
            "right_cheek": empty_mask.copy(),
            "combined": empty_mask.copy(),
        }

        if self.face_mesh is None:
            self._init_mediapipe()
            if self.face_mesh is None:
                return empty_masks, {"detected": False, "reason": "FaceMesh not initialized", "cached": False}

        # MediaPipe expects RGB
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(frame_rgb)

        if results.multi_face_landmarks and len(results.multi_face_landmarks) > 0:
            face_landmarks = results.multi_face_landmarks[0].landmark
            current_center = self._calculate_face_center(face_landmarks, w, h)

            # Extract ROI polygons
            forehead_pts = self._landmarks_to_points(face_landmarks, FOREHEAD_LANDMARKS, w, h)
            left_cheek_pts = self._landmarks_to_points(face_landmarks, LEFT_CHEEK_LANDMARKS, w, h)
            right_cheek_pts = self._landmarks_to_points(face_landmarks, RIGHT_CHEEK_LANDMARKS, w, h)

            # Generate individual binary masks via cv2.fillPoly
            forehead_mask = np.zeros((h, w), dtype=np.uint8)
            left_cheek_mask = np.zeros((h, w), dtype=np.uint8)
            right_cheek_mask = np.zeros((h, w), dtype=np.uint8)

            if len(forehead_pts) >= 3:
                cv2.fillPoly(forehead_mask, [forehead_pts], 255)
            if len(left_cheek_pts) >= 3:
                cv2.fillPoly(left_cheek_mask, [left_cheek_pts], 255)
            if len(right_cheek_pts) >= 3:
                cv2.fillPoly(right_cheek_mask, [right_cheek_pts], 255)

            # Combined valid skin mask
            combined_mask = cv2.bitwise_or(forehead_mask, cv2.bitwise_or(left_cheek_mask, right_cheek_mask))

            masks = {
                "forehead": forehead_mask,
                "left_cheek": left_cheek_mask,
                "right_cheek": right_cheek_mask,
                "combined": combined_mask,
            }

            # Update temporal tracking cache
            self.last_valid_masks = masks
            self.last_face_center = current_center
            self.stale_frame_count = 0

            return masks, {
                "detected": True,
                "cached": False,
                "face_center": current_center,
                "forehead_points": forehead_pts.tolist(),
                "left_cheek_points": left_cheek_pts.tolist(),
                "right_cheek_points": right_cheek_pts.tolist(),
                "stale_frames": 0,
            }

        # Detection failed for current frame -> Temporal Fallback Logic
        self.total_missing_frames += 1
        self.stale_frame_count += 1

        if (
            self.last_valid_masks is not None
            and self.stale_frame_count <= MAX_STALE_FRAMES
        ):
            # Mask reuse with stale tracking
            return self.last_valid_masks, {
                "detected": False,
                "cached": True,
                "reason": f"Face detection missed; reusing valid mask (stale frame {self.stale_frame_count}/{MAX_STALE_FRAMES})",
                "stale_frames": self.stale_frame_count,
            }

        # Invalidate cache if face has been missing beyond threshold
        self.last_valid_masks = None
        self.last_face_center = None
        return empty_masks, {
            "detected": False,
            "cached": False,
            "reason": f"Face missing for {self.stale_frame_count} consecutive frames; stale mask invalidated",
            "stale_frames": self.stale_frame_count,
        }

    def render_debug_overlay(
        self, frame_bgr: np.ndarray, masks: Dict[str, np.ndarray], metadata: Dict[str, Any]
    ) -> np.ndarray:
        """Draws visual debugging contours and ROI highlights over the frame."""
        overlay = frame_bgr.copy()
        
        # Color coding: Forehead (Cyan), Left Cheek (Purple), Right Cheek (Electric Blue)
        cyan = (255, 240, 0)
        purple = (247, 85, 168)
        blue = (255, 102, 0)

        # Draw transparent colored highlights for ROIs
        colored_rois = np.zeros_like(frame_bgr)
        colored_rois[masks["forehead"] > 0] = cyan
        colored_rois[masks["left_cheek"] > 0] = purple
        colored_rois[masks["right_cheek"] > 0] = blue

        # Alpha blend
        cv2.addWeighted(colored_rois, 0.45, overlay, 0.55, 0, overlay)

        # Draw contour boundaries
        for key, color in [("forehead", cyan), ("left_cheek", purple), ("right_cheek", blue)]:
            contours, _ = cv2.findContours(masks[key], cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(overlay, contours, -1, color, 2)

        # Overlay status badge
        status_text = "FACE DETECTED" if metadata.get("detected") else (
            f"MASK CACHED ({metadata.get('stale_frames')})" if metadata.get("cached") else "NO FACE"
        )
        badge_color = (0, 255, 0) if metadata.get("detected") else ((0, 165, 255) if metadata.get("cached") else (0, 0, 255))
        
        cv2.putText(overlay, f"PulseShield Mesh: {status_text}", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, badge_color, 2)
        return overlay

    def close(self) -> None:
        if self.face_mesh:
            self.face_mesh.close()
            self.face_mesh = None
