"""
PulseShield Sample Media Generator
Generates synthetic facial video clips and test images containing simulated physiological
cardiac pulses (72 BPM) for instantaneous testing and hackathon demonstration.
"""

import cv2
import numpy as np
from pathlib import Path

SAMPLE_DIR = Path(__file__).resolve().parent

def create_synthetic_face_frame(width: int = 480, height: int = 480, pulse_val: float = 0.0) -> np.ndarray:
    """Renders a stylized synthetic face with realistic skin tones and subtle physiological pulse."""
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    # Background: dark studio navy gradient
    for y in range(height):
        ratio = y / height
        frame[y, :] = [int(30 + 15 * ratio), int(20 + 10 * ratio), int(15 + 8 * ratio)]

    center = (width // 2, height // 2)
    
    # Base skin tone in BGR: [B=145, G=175, R=225]
    b = 145
    g = int(np.clip(175 + pulse_val, 0, 255))
    r = 225
    skin_color = (b, g, r)

    # Face Oval
    face_axes = (int(width * 0.28), int(height * 0.38))
    cv2.ellipse(frame, center, face_axes, 0, 0, 360, skin_color, -1)
    
    # Forehead skin highlight
    forehead_center = (width // 2, int(height * 0.32))
    forehead_axes = (int(width * 0.18), int(height * 0.10))
    cv2.ellipse(frame, forehead_center, forehead_axes, 0, 0, 360, (b + 5, int(np.clip(g + 5, 0, 255)), r + 5), -1)

    # Left & Right cheek blush
    left_cheek = (int(width * 0.38), int(height * 0.54))
    right_cheek = (int(width * 0.62), int(height * 0.54))
    cheek_axes = (int(width * 0.09), int(height * 0.07))
    cv2.ellipse(frame, left_cheek, cheek_axes, 0, 0, 360, (b - 10, int(np.clip(g - 5, 0, 255)), r + 15), -1)
    cv2.ellipse(frame, right_cheek, cheek_axes, 0, 0, 360, (b - 10, int(np.clip(g - 5, 0, 255)), r + 15), -1)

    # Eyes
    eye_y = int(height * 0.44)
    cv2.ellipse(frame, (int(width * 0.38), eye_y), (22, 12), 0, 0, 360, (245, 245, 245), -1)
    cv2.ellipse(frame, (int(width * 0.62), eye_y), (22, 12), 0, 0, 360, (245, 245, 245), -1)
    cv2.circle(frame, (int(width * 0.38), eye_y), 8, (60, 40, 20), -1)
    cv2.circle(frame, (int(width * 0.62), eye_y), 8, (60, 40, 20), -1)

    # Eyebrows
    cv2.ellipse(frame, (int(width * 0.38), eye_y - 18), (26, 6), -10, 0, 180, (40, 25, 15), -1)
    cv2.ellipse(frame, (int(width * 0.62), eye_y - 18), (26, 6), 10, 0, 180, (40, 25, 15), -1)

    # Nose
    cv2.line(frame, (width // 2, eye_y), (width // 2, int(height * 0.58)), (b - 25, g - 25, r - 25), 3)
    cv2.ellipse(frame, (width // 2, int(height * 0.59)), (14, 6), 0, 0, 180, (b - 30, g - 30, r - 30), 2)

    # Lips
    mouth_y = int(height * 0.70)
    cv2.ellipse(frame, (width // 2, mouth_y), (32, 12), 0, 0, 360, (110, 110, 200), -1)
    cv2.line(frame, (width // 2 - 28, mouth_y), (width // 2 + 28, mouth_y), (70, 70, 150), 2)

    # Hair
    hair_color = (30, 20, 15)
    cv2.ellipse(frame, (width // 2, int(height * 0.22)), (int(width * 0.30), int(height * 0.16)), 0, 180, 360, hair_color, -1)
    cv2.ellipse(frame, (int(width * 0.22), int(height * 0.35)), (int(width * 0.07), int(height * 0.15)), 0, 0, 360, hair_color, -1)
    cv2.ellipse(frame, (int(width * 0.78), int(height * 0.35)), (int(width * 0.07), int(height * 0.15)), 0, 0, 360, hair_color, -1)

    # Subtle camera sensor and skin pore noise for authentic photo
    noise = np.random.normal(0, 3.0, frame.shape).astype(np.float32)
    frame = np.clip(frame.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    return frame

def generate_sample_assets():
    """Generates sample video and sample images in the sample_data directory."""
    sample_video_path = SAMPLE_DIR / "sample_pulse_face.mp4"
    sample_photo_path = SAMPLE_DIR / "sample_portrait.jpg"
    sample_fake_path = SAMPLE_DIR / "sample_deepfake_suspect.jpg"

    fps = 30
    duration_sec = 4
    total_frames = fps * duration_sec
    w, h = 480, 480

    # 1. Generate Video
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(sample_video_path), fourcc, fps, (w, h))
    
    heart_rate_hz = 1.2  # 72 BPM

    for i in range(total_frames):
        t = i / fps
        # Synchronized physiological pulse wave (higher absorption -> subtle green modulation)
        pulse = 2.5 * np.sin(2.0 * np.pi * heart_rate_hz * t)
        frame = create_synthetic_face_frame(w, h, pulse_val=pulse)
        out.write(frame)
    out.release()
    print(f"Generated sample video: {sample_video_path}")

    # 2. Generate Clean Sample Portrait
    portrait = create_synthetic_face_frame(w, h, pulse_val=0.0)
    cv2.imwrite(str(sample_photo_path), portrait, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    print(f"Generated sample photo: {sample_photo_path}")

    # 3. Generate Sample Deepfake / Spliced Suspect Image
    fake = portrait.copy()
    # High-intensity localized splicing manipulation
    center_roi = fake[int(h*0.35):int(h*0.75), int(w*0.30):int(w*0.70)].copy()
    # Blurring destroys sensor noise in face
    smoothed_face = cv2.GaussianBlur(center_roi, (17, 17), 6.0)
    # Inject heavy localized ELA disparity and synthetic artifacts
    spliced_seam = np.random.uniform(25, 45, size=center_roi.shape).astype(np.float32)
    manipulated_roi = np.clip(smoothed_face.astype(np.float32) + spliced_seam * 0.4, 0, 255).astype(np.uint8)
    fake[int(h*0.35):int(h*0.75), int(w*0.30):int(w*0.70)] = manipulated_roi
    
    # Sharp splicing boundary border
    cv2.ellipse(fake, (w // 2, int(h * 0.55)), (int(w * 0.20), int(h * 0.25)), 0, 0, 360, (255, 255, 255), 2)
    cv2.imwrite(str(sample_fake_path), fake, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
    print(f"Generated sample deepfake suspect: {sample_fake_path}")

if __name__ == "__main__":
    generate_sample_assets()
