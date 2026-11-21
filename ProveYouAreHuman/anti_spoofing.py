"""
=============================================================================
ANTI-SPOOFING & ACTIVE CHROMATIC REFLECTION DEFENSE MODULE
TrustLayer: Human Verification for the AI Era
Zeal College of Engineering & Research, Pune-41
Department of Electronics and Computer Engineering

Features:
1. Active Screen Flash Reflection Test (Chromatic Illumination Liveness)
   - Emits random 400ms chromatic flash pulses (#00FFCC, #FF007F, #FFB800, etc.)
   - Measures forehead & cheek skin diffuse reflection vector in RGB & HSV
   - Rejects virtual camera injection, prerecorded replays, and static deepfakes
2. 2D FFT Moiré Pattern Grid Detection (Physical Phone/Monitor Replay)
3. Laplacian Texture Sharpness & Focus Variance
4. Standalone Interactive Demonstration & API Integrations
=============================================================================
"""

import math
import time
import random
import cv2
import numpy as np


# ============================================================================
# 1. CHROMATIC SCREEN FLASH CHALLENGE ENGINE
# ============================================================================

class ScreenFlashChallenge:
    """
    Active Optical Challenge: Commands the screen to emit a synchronized
    narrowband chromatic light pulse to verify physical photometric interaction.
    """
    # Palette of high-contrast distinct chromatic hues (Name, HEX, RGB, BGR)
    FLASH_PALETTE = [
        {"name": "CYAN", "hex": "#00FFCC", "rgb": (0, 255, 204), "bgr": (204, 255, 0)},
        {"name": "MAGENTA", "hex": "#FF007F", "rgb": (255, 0, 127), "bgr": (127, 0, 255)},
        {"name": "AMBER", "hex": "#FFB800", "rgb": (255, 184, 0), "bgr": (0, 184, 255)},
        {"name": "EMERALD", "hex": "#00FF66", "rgb": (0, 255, 102), "bgr": (102, 255, 0)},
        {"name": "ELECTRIC_BLUE", "hex": "#0088FF", "rgb": (0, 136, 255), "bgr": (255, 136, 0)},
        {"name": "CRIMSON", "hex": "#FF2244", "rgb": (255, 34, 68), "bgr": (68, 34, 255)}
    ]

    def __init__(self, duration_ms: int = 400):
        self.duration_ms = duration_ms
        self.duration_sec = duration_ms / 1000.0
        
        self.active_challenge = None
        self.flash_start_time = None
        self.is_flashing = False
        
        # Skin ROI Landmark Indices (MediaPipe Face Mesh)
        # Forehead & Glabella
        self.FOREHEAD_LANDMARKS = [10, 67, 109, 108, 151, 9, 8, 337, 338, 297]
        # Left Cheek
        self.LEFT_CHEEK_LANDMARKS = [117, 118, 101, 205, 50, 123, 147, 187]
        # Right Cheek
        self.RIGHT_CHEEK_LANDMARKS = [346, 347, 330, 425, 280, 352, 376, 411]
        # Nose Bridge
        self.NOSE_BRIDGE_LANDMARKS = [168, 6, 197, 195, 5]

        # Historical buffers for baseline vs active comparison
        self.baseline_colors_rgb = []
        self.flash_colors_rgb = []
        self.baseline_colors_hsv = []
        self.flash_colors_hsv = []
        self.max_baseline_buffer = 15

    def generate_challenge(self) -> dict:
        """
        Picks a randomized chromatic color challenge.
        """
        choice = random.choice(self.FLASH_PALETTE)
        self.active_challenge = {
            "name": choice["name"],
            "hex": choice["hex"],
            "rgb": choice["rgb"],
            "bgr": choice["bgr"],
            "duration_ms": self.duration_ms
        }
        return self.active_challenge

    def start_flash(self, challenge: dict = None) -> dict:
        """
        Triggers the synchronized 400ms flash window.
        """
        if challenge:
            self.active_challenge = challenge
        elif not self.active_challenge:
            self.generate_challenge()

        self.flash_start_time = time.time()
        self.is_flashing = True
        self.flash_colors_rgb = []
        self.flash_colors_hsv = []
        return self.active_challenge

    def _extract_skin_roi_mean(self, frame_bgr, landmarks) -> tuple[np.ndarray, np.ndarray]:
        """
        Extracts mean RGB & HSV color from facial forehead and cheek regions.
        """
        h, w = frame_bgr.shape[:2]
        all_ids = (self.FOREHEAD_LANDMARKS + self.LEFT_CHEEK_LANDMARKS + 
                   self.RIGHT_CHEEK_LANDMARKS + self.NOSE_BRIDGE_LANDMARKS)

        pts = []
        for idx in all_ids:
            lm = landmarks[idx]
            px = int(np.clip(lm.x * w, 0, w - 1))
            py = int(np.clip(lm.y * h, 0, h - 1))
            pts.append((px, py))

        if not pts:
            return np.array([0.0, 0.0, 0.0]), np.array([0.0, 0.0, 0.0])

        # Create mask for skin sampling
        mask = np.zeros((h, w), dtype=np.uint8)
        for px, py in pts:
            cv2.circle(mask, (px, py), 6, 255, -1)

        mean_bgr = cv2.mean(frame_bgr, mask=mask)[:3]
        mean_rgb = np.array([mean_bgr[2], mean_bgr[1], mean_bgr[0]], dtype=np.float32)

        hsv_frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
        mean_hsv = np.array(cv2.mean(hsv_frame, mask=mask)[:3], dtype=np.float32)

        return mean_rgb, mean_hsv

    def update_frame(self, frame_bgr, landmarks) -> dict:
        """
        Processes each video frame during baseline or active flash window.
        """
        if landmarks is None:
            return {"is_flashing": self.is_flashing, "time_left_ms": 0}

        mean_rgb, mean_hsv = self._extract_skin_roi_mean(frame_bgr, landmarks)

        now = time.time()
        if self.is_flashing and self.flash_start_time is not None:
            elapsed = now - self.flash_start_time
            time_left_ms = max(0, int((self.duration_sec - elapsed) * 1000))

            if elapsed <= self.duration_sec:
                self.flash_colors_rgb.append(mean_rgb)
                self.flash_colors_hsv.append(mean_hsv)
                return {
                    "is_flashing": True,
                    "challenge": self.active_challenge,
                    "time_left_ms": time_left_ms,
                    "current_rgb": mean_rgb
                }
            else:
                # Flash duration completed
                self.is_flashing = False
                return {
                    "is_flashing": False,
                    "challenge": self.active_challenge,
                    "time_left_ms": 0,
                    "flash_complete": True
                }
        else:
            # Baseline tracking
            self.baseline_colors_rgb.append(mean_rgb)
            self.baseline_colors_hsv.append(mean_hsv)
            if len(self.baseline_colors_rgb) > self.max_baseline_buffer:
                self.baseline_colors_rgb.pop(0)
                self.baseline_colors_hsv.pop(0)

            return {
                "is_flashing": False,
                "time_left_ms": 0
            }

    def evaluate_reflection_test(self) -> dict:
        """
        Evaluates the active chromatic reflection test.
        Computes cosine similarity between skin delta shift and target flash color.
        """
        if not self.baseline_colors_rgb or not self.flash_colors_rgb or not self.active_challenge:
            return {
                "passed": False,
                "score": 0.0,
                "verdict": "REPLAY_ATTACK_DETECTED",
                "reason": "INSUFFICIENT_FLASH_FRAMES",
                "cosine_similarity": 0.0,
                "delta_magnitude": 0.0
            }

        base_mean_rgb = np.mean(self.baseline_colors_rgb, axis=0)
        flash_mean_rgb = np.mean(self.flash_colors_rgb, axis=0)

        # Delta shift vector on user's skin
        delta_rgb = flash_mean_rgb - base_mean_rgb
        delta_mag = float(np.linalg.norm(delta_rgb))

        # Target flash color normalized vector
        target_rgb = np.array(self.active_challenge["rgb"], dtype=np.float32)
        target_norm = target_rgb / max(np.linalg.norm(target_rgb), 1e-5)

        # Delta normalized vector
        if delta_mag > 1e-3:
            delta_norm = delta_rgb / delta_mag
            cosine_sim = float(np.dot(delta_norm, target_norm))
        else:
            cosine_sim = 0.0

        # Liveness Decision Logic
        # Genuine 3D human in front of monitor exhibits:
        # 1. Minimum luminance/chrominance shift (delta_mag >= 1.5)
        # 2. Positive directional correlation with the emitted wavelength (cosine_sim >= 0.35)
        passed = False
        flags = []

        if delta_mag < 1.2:
            flags.append("NO_PHOTOMETRIC_ILLUMINATION_SHIFT")
        if cosine_sim < 0.30:
            flags.append("COLOR_REFLECTION_MISMATCH")

        if delta_mag >= 1.2 and cosine_sim >= 0.30:
            passed = True
            # Score scaling from 0.70 to 0.99
            score = min(0.99, max(0.70, (cosine_sim * 0.6) + (min(delta_mag, 15.0) / 15.0 * 0.4)))
            verdict = "AUTHENTIC_HUMAN_REFLECTION"
        else:
            passed = False
            score = max(0.05, min(0.40, (cosine_sim * 0.3) + (delta_mag / 20.0 * 0.1)))
            verdict = "REPLAY_ATTACK_DETECTED"

        return {
            "passed": passed,
            "score": round(score * 100.0, 1),
            "verdict": verdict,
            "target_color": self.active_challenge["name"],
            "target_hex": self.active_challenge["hex"],
            "delta_rgb": [round(float(x), 2) for x in delta_rgb],
            "delta_magnitude": round(delta_mag, 2),
            "cosine_similarity": round(cosine_sim, 3),
            "flags": flags
        }

    def reset(self):
        self.active_challenge = None
        self.flash_start_time = None
        self.is_flashing = False
        self.baseline_colors_rgb = []
        self.flash_colors_rgb = []


# ============================================================================
# 2. PHYSICAL PHONE SCREEN MOIRÉ & BLUR DETECTOR
# ============================================================================

class ScreenArtifactDetector:
    """
    Detects physical monitor/smartphone screens held in front of the camera
    using 2D FFT spatial frequency Moiré grid peaks and Laplacian focus.
    """
    def __init__(self):
        self.MOIRE_PEAK_THRESHOLD = 8.0
        self.MIN_LAPLACIAN_VAR = 18.0
        self.MAX_LAPLACIAN_VAR = 1200.0

    def detect_moire_pattern(self, face_gray: np.ndarray) -> tuple[bool, float, np.ndarray]:
        """
        Computes 2D Fast Fourier Transform (FFT) power spectral density.
        Periodic screen subpixel grids produce distinct high-frequency spikes (Moiré fringes).
        """
        h, w = face_gray.shape
        if h < 32 or w < 32:
            return False, 0.0, None

        resized = cv2.resize(face_gray, (128, 128)).astype(np.float32)
        hann_2d = np.outer(np.hanning(128), np.hanning(128))
        windowed = (resized - np.mean(resized)) * hann_2d

        f = np.fft.fft2(windowed)
        fshift = np.fft.fftshift(f)
        magnitude_spectrum = np.abs(fshift)
        power_spectrum = magnitude_spectrum ** 2

        # Radial high-frequency ring mask (35 <= r <= 60)
        center = (64, 64)
        y, x = np.ogrid[:128, :128]
        dist = np.sqrt((x - center[0]) ** 2 + (y - center[1]) ** 2)
        hf_mask = (dist >= 35) & (dist <= 60)

        hf_values = power_spectrum[hf_mask]
        mean_hf = np.mean(hf_values)
        max_hf = np.max(hf_values)
        peak_prominence = max_hf / max(mean_hf, 1e-5)

        has_moire = peak_prominence > self.MOIRE_PEAK_THRESHOLD

        # Visual thumbnail of FFT spectrum
        vis_spec = 20 * np.log(magnitude_spectrum + 1e-5)
        vis_norm = cv2.normalize(vis_spec, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        vis_color = cv2.applyColorMap(vis_norm, cv2.COLORMAP_MAGMA)

        return has_moire, float(peak_prominence), vis_color

    def check_laplacian_sharpness(self, face_bgr: np.ndarray) -> tuple[bool, float]:
        """
        Calculates Laplacian focus variance.
        """
        gray = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2GRAY)
        lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        is_natural = self.MIN_LAPLACIAN_VAR <= lap_var <= self.MAX_LAPLACIAN_VAR
        return is_natural, lap_var

    def inspect_frame(self, frame_bgr: np.ndarray, face_box: tuple) -> dict:
        """
        Full screen spoof inspection on detected face ROI.
        """
        if face_box is None:
            return {"is_spoof": False, "flags": [], "moire_peak": 0.0, "lap_var": 0.0}

        x, y, w, h = face_box
        fh, fw = frame_bgr.shape[:2]
        x1, y1 = max(0, x), max(0, y)
        x2, y2 = min(fw, x + w), min(fh, y + h)

        if (x2 - x1) < 40 or (y2 - y1) < 40:
            return {"is_spoof": False, "flags": [], "moire_peak": 0.0, "lap_var": 0.0}

        roi = frame_bgr[y1:y2, x1:x2]
        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        has_moire, peak_ratio, fft_vis = self.detect_moire_pattern(roi_gray)
        is_natural_focus, lap_var = self.check_laplacian_sharpness(roi)

        flags = []
        if has_moire:
            flags.append("PHONE_SCREEN_MOIRE_GRID_DETECTED")
        if lap_var < self.MIN_LAPLACIAN_VAR:
            flags.append("ABNORMAL_BLUR_OR_PRINTED_PHOTO")
        elif lap_var > self.MAX_LAPLACIAN_VAR:
            flags.append("DIGITAL_DISPLAY_OVER_SHARPENED")

        is_spoof = len(flags) > 0

        return {
            "is_spoof": is_spoof,
            "has_moire": has_moire,
            "moire_peak": round(peak_ratio, 2),
            "lap_var": round(lap_var, 1),
            "flags": flags,
            "fft_vis": fft_vis
        }


# ============================================================================
# 3. UNIFIED ANTI-SPOOFING SHIELD (EASY INTEGRATION API)
# ============================================================================

class AntiSpoofingShield:
    """
    Unified Anti-Spoofing & Liveness Shield combining:
    - Active Chromatic Reflection Flash Challenge
    - 2D FFT Moiré Pattern Analysis
    - Laplacian Texture Focus Variance
    """
    def __init__(self, flash_duration_ms: int = 400):
        self.flash_challenge = ScreenFlashChallenge(duration_ms=flash_duration_ms)
        self.screen_detector = ScreenArtifactDetector()

    def start_flash_challenge(self) -> dict:
        return self.flash_challenge.start_flash()

    def process_frame(self, frame_bgr: np.ndarray, landmarks, face_box) -> dict:
        """
        Process a live camera frame through the anti-spoofing pipeline.
        """
        flash_status = self.flash_challenge.update_frame(frame_bgr, landmarks)
        artifact_status = self.screen_detector.inspect_frame(frame_bgr, face_box)

        return {
            "flash_status": flash_status,
            "artifact_status": artifact_status
        }

    def evaluate_flash_liveness(self) -> dict:
        return self.flash_challenge.evaluate_reflection_test()


# ============================================================================
# 4. STANDALONE INTERACTIVE DEMONSTRATION
# ============================================================================

def run_standalone_demo():
    """
    Launches an interactive OpenCV demo showing the active screen flash test
    and real-time Moiré & Laplacian texture inspection.
    """
    import mediapipe as mp

    print("==================================================================")
    print("      ANTI-SPOOFING & CHROMATIC FLASH REFLECTION TEST (DEMO)      ")
    print("==================================================================")
    print(" Controls:")
    print("   [SPACE] : Trigger 400ms Chromatic Screen Flash Challenge")
    print("   [Q]     : Quit")
    print("==================================================================")

    # Initialize MediaPipe Face Landmarker
    model_path = "face_landmarker.task"
    if not os.path.exists(model_path):
        candidates = [os.path.join(r"C:\Users\User", "face_landmarker.task"),
                      os.path.join(r"C:\Users\User\ProveYouAreHuman", "face_landmarker.task")]
        for c in candidates:
            if os.path.exists(c):
                model_path = c
                break

    face_options = mp.tasks.vision.FaceLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=model_path),
        running_mode=mp.tasks.vision.RunningMode.IMAGE,
        num_faces=1
    )
    landmarker = mp.tasks.vision.FaceLandmarker.create_from_options(face_options)

    shield = AntiSpoofingShield(flash_duration_ms=400)
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    flash_result = None
    flash_card_timer = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        
        result = landmarker.detect(mp_image)
        landmarks = result.face_landmarks[0] if result.face_landmarks else None

        face_box = None
        if landmarks:
            xs = [lm.x * w for lm in landmarks]
            ys = [lm.y * h for lm in landmarks]
            face_box = (int(min(xs)), int(min(ys)), int(max(xs) - min(xs)), int(max(ys) - min(ys)))

        # Process through AntiSpoofing Shield
        status = shield.process_frame(frame, landmarks, face_box)
        flash_status = status["flash_status"]
        artifact_status = status["artifact_status"]

        # Active Screen Flash Overlay (simulating monitor flash glow)
        if flash_status.get("is_flashing"):
            chal = flash_status["challenge"]
            flash_bgr = chal["bgr"]
            
            # Flash glowing border & top banner
            cv2.rectangle(frame, (0, 0), (w, h), flash_bgr, 28)
            cv2.putText(frame, f"FLASH ACTIVE: {chal['name']} ({chal['hex']})", (40, 60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 3)
        elif flash_status.get("flash_complete"):
            flash_result = shield.evaluate_flash_liveness()
            flash_card_timer = time.time()
            print(f"[+] Flash Evaluation: {flash_result['verdict']} | Score: {flash_result['score']}% | CosineSim: {flash_result['cosine_similarity']}")

        # HUD Overlay
        cv2.rectangle(frame, (20, h - 140), (460, h - 20), (24, 24, 30), -1)
        cv2.rectangle(frame, (20, h - 140), (460, h - 20), (50, 50, 60), 1)

        cv2.putText(frame, "ANTI-REPLAY DEFENSE METRICS", (34, h - 115), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 220, 255), 1)
        cv2.putText(frame, f"Moiré Peak Ratio: {artifact_status.get('moire_peak', 0.0)} (Max: 8.0)", (34, h - 90), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (240, 240, 250), 1)
        cv2.putText(frame, f"Laplacian Sharpness: {artifact_status.get('lap_var', 0.0)}", (34, h - 68), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (240, 240, 250), 1)
        cv2.putText(frame, "Press [SPACE] to trigger Screen Flash Reflection Test", (34, h - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (0, 255, 150), 1)

        # Show result card if recently tested
        if flash_result and (time.time() - flash_card_timer < 5.0):
            rc_col = (80, 230, 80) if flash_result["passed"] else (60, 60, 240)
            cv2.rectangle(frame, (w - 420, 20), (w - 20, 160), (24, 24, 30), -1)
            cv2.rectangle(frame, (w - 420, 20), (w - 20, 160), rc_col, 2)
            cv2.putText(frame, flash_result["verdict"], (w - 400, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.58, rc_col, 2)
            cv2.putText(frame, f"Reflection Score: {flash_result['score']}%", (w - 400, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
            cv2.putText(frame, f"Cosine Sim: {flash_result['cosine_similarity']} | Delta: {flash_result['delta_magnitude']}", (w - 400, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (180, 180, 190), 1)
            cv2.putText(frame, f"Target Hue: {flash_result['target_color']}", (w - 400, 145), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (0, 220, 255), 1)

        cv2.imshow("Anti-Spoofing & Screen Flash Reflection Test", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):
            shield.start_flash_challenge()
            print("[*] Screen Flash Challenge Triggered...")
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    landmarker.close()


if __name__ == "__main__":
    import os
    run_standalone_demo()
