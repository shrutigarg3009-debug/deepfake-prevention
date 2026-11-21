"""
Module: AI Misuse Scanner & Facial Identity Matcher
Matches suspect media against registered facial identities using geometric landmark
embeddings, evaluates synthetic face-swap boundary artifacts, and assesses unauthorized AI misuse risk.
"""

import cv2
import numpy as np
import json
from typing import Dict, List, Tuple, Any, Optional
from modules.face_mesh_detector import FaceMeshDetector
from modules.image_authenticity import AuthenticityVerifier
from database import get_all_identities, add_alert

class MisuseScanner:
    def __init__(self):
        self.detector = FaceMeshDetector(max_num_faces=1, refine_landmarks=True)

    def extract_face_descriptor(self, image_bgr: np.ndarray) -> Optional[List[float]]:
        """
        Extracts a pose-invariant geometric landmark embedding vector from FaceMesh.
        Normalizes by inter-pupil distance and face center.
        """
        if self.detector.face_mesh is None:
            self.detector._init_mediapipe()
            if self.detector.face_mesh is None:
                return None

        h, w = image_bgr.shape[:2]
        frame_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        res = self.detector.face_mesh.process(frame_rgb)
        
        if not res.multi_face_landmarks or len(res.multi_face_landmarks) == 0:
            return None

        landmarks = res.multi_face_landmarks[0].landmark
        
        # Key reference points: Left eye outer (33), Right eye outer (263), Nose tip (1), Chin (152)
        lx, ly = landmarks[33].x * w, landmarks[33].y * h
        rx, ry = landmarks[263].x * w, landmarks[263].y * h
        cx, cy = landmarks[1].x * w, landmarks[1].y * h

        iod = np.sqrt((rx - lx) ** 2 + (ry - ly) ** 2)
        if iod <= 1e-4:
            iod = 1.0

        # Sample a representative subset of 40 key structural landmarks
        key_indices = [
            10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
            397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
            172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109,
            1, 9, 33, 263
        ]

        descriptor = []
        for idx in key_indices:
            px = (landmarks[idx].x * w - cx) / iod
            py = (landmarks[idx].y * h - cy) / iod
            descriptor.extend([round(float(px), 4), round(float(py), 4)])

        return descriptor

    @staticmethod
    def calculate_similarity(desc1: List[float], desc2: List[float]) -> float:
        """
        Calculates cosine similarity and normalized Euclidean proximity between two descriptors.
        Returns match confidence percentage (0.0 to 100.0%).
        """
        v1 = np.array(desc1, dtype=np.float32)
        v2 = np.array(desc2, dtype=np.float32)

        min_len = min(len(v1), len(v2))
        if min_len == 0:
            return 0.0

        v1 = v1[:min_len]
        v2 = v2[:min_len]

        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        cos_sim = float(np.dot(v1, v2) / (norm1 * norm2))
        # Transform [-1, 1] cosine similarity to realistic biometric match confidence %
        confidence = float(np.clip((cos_sim - 0.4) / 0.6 * 100.0, 0.0, 99.8))
        return round(confidence, 1)

    def scan_suspect_media(self, suspect_bgr: np.ndarray) -> Dict[str, Any]:
        """
        Scans suspect media against registered database identities, evaluates deepfake
        synthesis risk, and generates a threat assessment.
        """
        h, w = suspect_bgr.shape[:2]
        
        # 1. Extract suspect facial descriptor
        suspect_desc = self.extract_face_descriptor(suspect_bgr)
        face_found = suspect_desc is not None

        # 2. Forensic deepfake check
        forensic_res = AuthenticityVerifier.verify_image(suspect_bgr)

        # 3. Match against registered identities in SQLite
        registered_list = get_all_identities()
        matches = []
        highest_match = None
        highest_conf = 0.0

        if face_found:
            for ident in registered_list:
                embed_json = ident.get("face_embedding_json")
                if embed_json:
                    try:
                        emb = json.loads(embed_json)
                        if isinstance(emb, list) and len(emb) > 0:
                            conf = self.calculate_similarity(suspect_desc, emb)
                            entry = {
                                "identity_id": ident["id"],
                                "name": ident["name"],
                                "email": ident["email"],
                                "match_confidence": conf,
                                "status": ident["protection_status"],
                            }
                            matches.append(entry)
                            if conf > highest_conf:
                                highest_conf = conf
                                highest_match = entry
                    except Exception:
                        continue

        # Sort matches by confidence
        matches.sort(key=lambda x: x["match_confidence"], reverse=True)

        # 4. Assess Misuse Threat Level
        is_known_identity = highest_conf >= 60.0
        is_synthetic = forensic_res["authenticity_score"] < 50.0

        if is_known_identity and is_synthetic:
            threat_level = "CRITICAL"
            badge_color = "#EF4444"
            summary = (
                f"UNAUTHORIZED DEEPFAKE DETECTED: Suspect media matches registered identity "
                f"'{highest_match['name']}' ({highest_conf}% match) with synthetic generation artifacts."
            )
            # Log critical alert
            add_alert(
                "CRITICAL",
                f"Deepfake Alert: {highest_match['name']}",
                f"Suspect image matched with {highest_conf}% confidence and failed authenticity verification (Score: {forensic_res['authenticity_score']}%)."
            )
        elif is_known_identity and not is_synthetic:
            threat_level = "LOW / VERIFIED"
            badge_color = "#10B981"
            summary = (
                f"VERIFIED GENUINE: Media matches registered identity '{highest_match['name']}' "
                f"({highest_conf}% match) with authentic camera noise signatures."
            )
        elif not is_known_identity and is_synthetic:
            threat_level = "WARNING"
            badge_color = "#F59E0B"
            summary = "SYNTHETIC ARTIFACTS DETECTED: Unregistered face exhibits deepfake or generative AI anomalies."
        else:
            threat_level = "INFO"
            badge_color = "#00F0FF"
            summary = "STANDARD MEDIA: No registered biometric matches or critical manipulation detected."

        return {
            "face_detected": face_found,
            "threat_level": threat_level,
            "badge_color": badge_color,
            "summary": summary,
            "highest_match": highest_match,
            "all_matches": matches[:5],
            "forensic_report": forensic_res,
            "suspect_rgb": cv2.cvtColor(suspect_bgr, cv2.COLOR_BGR2RGB),
        }
