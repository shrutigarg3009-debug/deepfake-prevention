"""
PulseShield Comprehensive Test Suite
Validates all modules, algorithms, database operations, and computer vision pipelines.
"""

import sys
from pathlib import Path
import cv2
import numpy as np

# Ensure app directory is in path
APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from database import (
    init_db,
    register_identity,
    get_all_identities,
    log_video_job,
    get_video_jobs,
    log_photo_job,
    get_photo_jobs,
    log_forensic_scan,
    get_forensic_scans,
    add_alert,
    get_alerts,
    get_dashboard_stats,
)
from modules.face_mesh_detector import FaceMeshDetector
from modules.perturbation_engine import PerturbationEngine
from modules.rppg_extractor import RPPGExtractor
from modules.video_processor import VideoProcessor
from modules.photo_protector import PhotoProtector
from modules.image_authenticity import AuthenticityVerifier
from modules.misuse_scanner import MisuseScanner

def test_database():
    print("Testing Database...")
    init_db()
    stats = get_dashboard_stats()
    assert "identities_count" in stats
    assert "unread_alerts" in stats

    alert_id = add_alert("INFO", "Test Alert", "Automated system test notification.")
    assert alert_id > 0
    alerts = get_alerts()
    assert len(alerts) > 0
    print("  -> Database tests PASSED")

def test_face_mesh_and_perturbation():
    print("Testing FaceMesh Detector & Perturbation Engine...")
    sample_portrait = APP_DIR / "sample_data" / "sample_portrait.jpg"
    img = cv2.imread(str(sample_portrait))
    assert img is not None

    detector = FaceMeshDetector(max_num_faces=1)
    masks, meta = detector.process_frame(img)
    assert "forehead" in masks
    assert "left_cheek" in masks
    assert "right_cheek" in masks
    assert "combined" in masks
    assert masks["combined"].shape == img.shape[:2]

    engine = PerturbationEngine()
    cloaked, metrics = engine.apply_perturbation(
        frame_bgr=img,
        masks=masks,
        frame_idx=1,
        fps=30.0,
        delta=2.0,
        mode="Temporal Sinusoidal Desynchronization"
    )
    assert cloaked.shape == img.shape
    assert cloaked.dtype == np.uint8
    assert metrics["psnr"] > 35.0
    assert metrics["ssim"] > 0.95
    print(f"  -> FaceMesh & Perturbation PASSED (PSNR: {metrics['psnr']} dB, SSIM: {metrics['ssim']})")

def test_rppg_extraction():
    print("Testing rPPG Extraction & Desynchronization...")
    t = np.linspace(0, 4, 120)
    # Simulated natural correlated pulse
    sig_f = 2.0 * np.sin(2 * np.pi * 1.2 * t) + np.random.normal(0, 0.2, 120)
    sig_l = 2.0 * np.sin(2 * np.pi * 1.2 * t) + np.random.normal(0, 0.2, 120)
    sig_r = 2.0 * np.sin(2 * np.pi * 1.2 * t) + np.random.normal(0, 0.2, 120)

    # Simulated cloaked desynchronized pulse
    sig_p_f = sig_f + 2.0 * np.sin(2 * np.pi * 6.5 * t)
    sig_p_l = sig_l + 2.0 * np.sin(2 * np.pi * 6.5 * t + 2 * np.pi / 3)
    sig_p_r = sig_r + 2.0 * np.sin(2 * np.pi * 6.5 * t + 4 * np.pi / 3)

    orig = {"forehead": sig_f, "left_cheek": sig_l, "right_cheek": sig_r}
    prot = {"forehead": sig_p_f, "left_cheek": sig_p_l, "right_cheek": sig_p_r}

    eval_res = RPPGExtractor.evaluate_video_pair(orig, prot, fps=30.0)
    assert eval_res["orig_mean_pearson"] > 0.6
    assert eval_res["prot_mean_pearson"] < eval_res["orig_mean_pearson"]
    print(f"  -> rPPG Evaluation PASSED (Orig r: {eval_res['orig_mean_pearson']}, Prot r: {eval_res['prot_mean_pearson']}, Drop: {eval_res['desync_drop_percent']}%)")

def test_video_pipeline():
    print("Testing Video Processing Pipeline...")
    sample_vid = APP_DIR / "sample_data" / "sample_pulse_face.mp4"
    assert sample_vid.exists()

    processor = VideoProcessor()
    res = processor.process_video(
        input_path=str(sample_vid),
        delta=2.0,
        mode="Temporal Sinusoidal Desynchronization",
        max_frames=30
    )
    assert res["frames_processed"] == 30
    assert Path(res["output_path"]).exists()
    assert res["perceptual_metrics"]["mean_psnr"] > 35.0
    print(f"  -> Video Processing Pipeline PASSED (Frames: {res['frames_processed']}, PSNR: {res['perceptual_metrics']['mean_psnr']} dB)")

def test_photo_protection():
    print("Testing Photo Protection...")
    sample_portrait = APP_DIR / "sample_data" / "sample_portrait.jpg"
    img = cv2.imread(str(sample_portrait))

    protector = PhotoProtector()
    res = protector.protect_photo(img, delta=2.0, mode="DeepFace Feature Scrambler (Fourier Phase)")
    assert res["metrics"]["psnr"] > 35.0
    assert res["watermark_signature"].startswith("PS-")
    print(f"  -> Photo Protection PASSED (PSNR: {res['metrics']['psnr']} dB, Sig: {res['watermark_signature']})")

def test_authenticity_and_misuse():
    print("Testing Forensics & AI Misuse Scanner...")
    sample_portrait = APP_DIR / "sample_data" / "sample_portrait.jpg"
    sample_deepfake = APP_DIR / "sample_data" / "sample_deepfake_suspect.jpg"

    clean_img = cv2.imread(str(sample_portrait))
    fake_img = cv2.imread(str(sample_deepfake))

    verifier = AuthenticityVerifier()
    res_clean = verifier.verify_image(clean_img)
    res_fake = verifier.verify_image(fake_img)

    assert res_clean["authenticity_score"] > res_fake["authenticity_score"]
    print(f"  -> Forensics PASSED (Clean Score: {res_clean['authenticity_score']}%, Fake Score: {res_fake['authenticity_score']}%)")

    scanner = MisuseScanner()
    scan_res = scanner.scan_suspect_media(fake_img)
    assert "threat_level" in scan_res
    print(f"  -> Misuse Scanner PASSED (Threat: {scan_res['threat_level']}, Summary: {scan_res['summary'][:60]}...)")

if __name__ == "__main__":
    print("\n" + "="*50)
    print("EXECUTING PULSESHIELD END-TO-END VALIDATION SUITE")
    print("="*50)
    test_database()
    test_face_mesh_and_perturbation()
    test_rppg_extraction()
    test_video_pipeline()
    test_photo_protection()
    test_authenticity_and_misuse()
    print("="*50)
    print("ALL TESTS PASSED SUCCESSFULLY! 100% OPERATIONAL.")
    print("="*50 + "\n")
