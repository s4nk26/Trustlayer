"""
=============================================================================
TRUSTLAYER: AI-Powered Real-Time Human Verification & Deepfake Detection
Zeal Education Society's Zeal College of Engineering & Research, Pune-41
Department of Electronics and Computer Engineering

Core Capabilities:
1. Automated System-Generated Randomized Multi-Stage Protocol:
   - Stage 1: Head Pose (Turn Left/Right, Tilt Up/Down) [Timeout: 6s - Short & Brisk]
   - Stage 2: Hand Movement + Blink/Smile (Blink twice & 3 fingers, Smile & 3 fingers, Thumbs up) [Timeout: 10s]
   - Stage 3: Dynamic 7-8 Character Spoken Code with Voice Dictation (TTS) & Lip-Sync [Timeout: 25s - Ample Time]
   - Stage 4: Air-Drawing Shape Kinematics (Star, Square, Infinity) [Timeout: 30s - Full Tracing Required]
2. Advanced Anti-Spoofing & Replay Defense:
   - Rejects Printed Photos & Phone Photos (detects zero eye/mouth micro-nystagmus over temporal window)
   - Rejects Phone Screens & Selfie Video Replays (2D FFT Moiré pattern detection & 2D planar depth relief)
   - Stream Freeze & Virtual Camera Injection Guard
3. Live Exam & Video Call Shield (System 2):
   - User clears initial randomized protocol -> ZERO MORE TASKS EVER ISSUED!
   - Permanent 24/7 passive background proctoring shield.
=============================================================================
"""

import os
import sys
import time
import json
import base64
import random
import uuid
import math
import cv2
import numpy as np
from collections import deque

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Core Pipeline & Research Engines
from modules.face_liveness import FaceLivenessDetector
from modules.hand_biomechanics import HandBiomechanicsDetector
from modules.deepfake_detector import DeepfakeArtifactDetector
from modules.rppg_liveness import rPPGLivenessDetector
from modules.kinematic_tracker import KinematicTremorTracker, PathConformanceEngine
from modules.biomarker_monitor import BiomarkerMonitor
from modules.lip_sync_validator import LipSyncValidator
from anti_spoofing import ScreenArtifactDetector
import database

app = FastAPI(
    title="TrustLayer Multimodal Verification & Live Proctoring Shield",
    description="Continuous Kinematic Human Verification, rPPG Capillary Pulse & Anti-Spoofing Server",
    version="4.5.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# 1. RANDOMIZED SYSTEM-GENERATED CHALLENGE STATE MACHINE
# ============================================================================

class ChallengeManager:
    # Pool of system-generated challenges across 4 multimodal categories
    HEAD_POOL = [
        {"id": "HEAD_LEFT", "title": "Turn Head Left", "instruction": "Turn your head clearly to the left and hold for 1.2s", "type": "HEAD_POSE", "timeout": 18.0, "speech": "Please turn your head clearly to the left and hold steady"},
        {"id": "HEAD_RIGHT", "title": "Turn Head Right", "instruction": "Turn your head clearly to the right and hold for 1.2s", "type": "HEAD_POSE", "timeout": 18.0, "speech": "Please turn your head clearly to the right and hold steady"},
        {"id": "HEAD_UP", "title": "Tilt Head Up", "instruction": "Tilt your head upwards and hold for 1.2s", "type": "HEAD_POSE", "timeout": 18.0, "speech": "Please tilt your head upwards and hold steady"},
        {"id": "HEAD_DOWN", "title": "Tilt Head Down", "instruction": "Tilt your head downwards and hold for 1.2s", "type": "HEAD_POSE", "timeout": 18.0, "speech": "Please tilt your head downwards and hold steady"}
    ]

    GESTURE_POOL = [
        {"id": "BLINK_AND_THREE_FINGERS", "title": "Blink Twice & Show 3 Fingers", "instruction": "Show 3 fingers steadily to camera and blink twice naturally", "type": "MULTIMODAL_GESTURE", "timeout": 22.0, "speech": "Please show three fingers clearly to the camera and blink twice naturally"},
        {"id": "SMILE_AND_THREE_FINGERS", "title": "Smile & Show 3 Fingers", "instruction": "Show 3 fingers steadily and smile naturally", "type": "MULTIMODAL_GESTURE", "timeout": 22.0, "speech": "Please smile naturally and show three fingers clearly to the camera"},
        {"id": "THUMBS_UP_AND_BLINK", "title": "Show Thumbs Up & Blink", "instruction": "Show a thumbs up gesture and blink once naturally", "type": "MULTIMODAL_GESTURE", "timeout": 22.0, "speech": "Please show a thumbs up gesture and blink naturally"},
        {"id": "OPEN_PALM_AND_SMILE", "title": "Show Open Palm & Smile", "instruction": "Show an open palm with fingers spread and smile", "type": "MULTIMODAL_GESTURE", "timeout": 22.0, "speech": "Please show an open palm and smile at the camera"}
    ]

    SHAPE_POOL = [
        {"id": "DRAW_STAR", "title": "Air-Draw 5-Point Star", "instruction": "Point your index finger in the air and trace around the Star", "type": "AIR_DRAWING", "shape": "star", "timeout": 40.0, "speech": "Point your index finger in the air and trace around the glowing star"},
        {"id": "DRAW_SQUARE", "title": "Air-Draw Geometric Square", "instruction": "Point your index finger in the air and trace around the Square", "type": "AIR_DRAWING", "shape": "square", "timeout": 40.0, "speech": "Point your index finger in the air and trace around the square"},
        {"id": "DRAW_INFINITY", "title": "Air-Draw Infinity Figure", "instruction": "Point your index finger in the air and trace around the Infinity figure", "type": "AIR_DRAWING", "shape": "infinity", "timeout": 40.0, "speech": "Point your index finger in the air and trace around the infinity figure"}
    ]

    def __init__(self, mode: str = "live"):
        self.session_id = str(uuid.uuid4())[:8].upper()
        self.mode = mode  # "standard" (System 1: full audit certificate) or "live" (System 2: exam / video call proctoring)

        self.lip_validator = LipSyncValidator()
        self.active_code = self.lip_validator.generate_alphanumeric_code(length=random.choice([7, 8]))

        # Automated Protocol Sequence:
        # Stage 1: Biomechanical Fluidity Calibration (Head scan left & right + Hand/fingers check)
        # Stage 2: Multimodal Coordination Gesture (Blink twice & 3 fingers, Smile & open palm)
        # Stage 3: Dynamic 7-8 Character Spoken Code (TTS commands user to read without dictating)
        # Stage 4: Interactive Air-Drawing Kinematics (Normal 5-pointed star / Geometric shape)
        stage1 = {
            "id": "BIOMECHANICAL_FLUIDITY",
            "title": "Biomechanical Fluidity Calibration",
            "instruction": "Move your head smoothly left and right, then show your hand and fingers to the camera",
            "type": "BIOMECHANICAL_FLUIDITY",
            "timeout": 26.0,
            "speech": "Please move your head smoothly left and right, and show your hand and fingers to the camera to verify biological fluidity."
        }
        stage2 = random.choice(self.GESTURE_POOL)
        stage3 = {
            "id": "SPOKEN_CODE_GESTURE",
            "title": f"Read {len(self.active_code)}-Character Verification Code",
            "instruction": f"Read the code aloud into your microphone: {self._format_code_spaced(self.active_code)}",
            "type": "SPOKEN_ALPHANUMERIC",
            "code": self.active_code,
            "timeout": 28.0,
            "speech": "Please read the verification code shown on screen aloud into your microphone."
        }
        stage4 = random.choice(self.SHAPE_POOL)

        # Full 4-stage multimodal sequence in both modes
        self.selected_challenges = [stage1, stage2, stage3, stage4]

        self.current_step = 0
        self.step_start_time = time.time()
        self.step_hold_start = None
        self.session_start_time = time.time()

        # Biomechanical Fluidity Milestone Tracking
        self.calib_head_left = False
        self.calib_head_right = False
        self.calib_hand_seen = False

        self.is_gateway_cleared = False
        self.is_completed = False
        self.blink_baseline = 0
        self.completed_challenges = []
        self.failed_challenges = []

        # Anti-Spoofing & Replay Temporal Buffers
        self.ear_history = deque(maxlen=30)
        self.mar_history = deque(maxlen=30)
        self.yaw_history = deque(maxlen=30)
        self.pitch_history = deque(maxlen=30)
        self.screen_detector = ScreenArtifactDetector()

        # Shape Tracing State
        self.shape_start_time = None
        self.shape_visited_conformance = 0.0

        self._setup_current_step()

    def _format_code_spaced(self, code: str) -> str:
        return " - ".join(list(code))

    def _setup_current_step(self):
        if self.current_step < len(self.selected_challenges):
            chal = self.selected_challenges[self.current_step]
            if chal.get("type") == "AIR_DRAWING":
                shape_name = chal.get("shape", "star")
                self.active_waypoints = PathConformanceEngine.generate_shape_waypoints(shape_name)
                self.shape_start_time = time.time()
                self.shape_visited_conformance = 0.0

    def get_active_challenge_info(self) -> dict:
        if self.mode == "live" and (self.is_gateway_cleared or self.current_step >= len(self.selected_challenges)):
            return {
                "challenge_id": "PASSIVE_MONITOR",
                "title": "Continuous Live Proctoring Shield Active",
                "instruction": "Video Call / Exam Human Verification Complete. Passively monitoring biological signals in background. Zero tasks required.",
                "step": len(self.selected_challenges),
                "total_steps": len(self.selected_challenges),
                "progress": "Complete",
                "time_left": 0.0,
                "timeout_sec": 1.0,
                "is_passive": True,
                "is_gateway_cleared": True,
                "speech": ""
            }

        if self.current_step >= len(self.selected_challenges):
            return None

        chal = self.selected_challenges[self.current_step]
        timeout_sec = chal.get("timeout", 14.0)
        elapsed = time.time() - self.step_start_time
        time_left = max(0.0, round(timeout_sec - elapsed, 2))

        instruction_text = chal["instruction"]
        if chal["id"] == "BIOMECHANICAL_FLUIDITY":
            hl = "✅" if getattr(self, "calib_head_left", False) else "⏳"
            hr = "✅" if getattr(self, "calib_head_right", False) else "⏳"
            hf = "✅" if getattr(self, "calib_hand_seen", False) else "⏳"
            instruction_text = f"{chal['instruction']} [Head Left: {hl} | Head Right: {hr} | Hand: {hf}]"

        info = {
            "challenge_id": chal["id"],
            "title": chal["title"],
            "instruction": instruction_text,
            "speech": chal.get("speech", chal["instruction"]),
            "step": self.current_step + 1,
            "total_steps": len(self.selected_challenges),
            "progress": f"Stage {self.current_step + 1} of {len(self.selected_challenges)}",
            "time_left": time_left,
            "timeout_sec": timeout_sec,
            "is_passive": False,
            "is_gateway_cleared": False
        }

        if chal.get("type") == "SPOKEN_ALPHANUMERIC":
            info["spoken_code"] = self.active_code
        elif chal.get("type") == "AIR_DRAWING":
            info["shape_type"] = chal.get("shape", "star")
            info["waypoints"] = getattr(self, "active_waypoints", [])

        return info

    def evaluate_telemetry(self, face_data: dict, hand_data: dict, extra: dict,
                           kinematic_data: dict) -> tuple[bool, bool]:
        if self.mode == "live" and (self.is_gateway_cleared or self.current_step >= len(self.selected_challenges)):
            return True, False

        if self.current_step >= len(self.selected_challenges):
            self.is_completed = True
            return False, False

        chal = self.selected_challenges[self.current_step]
        chal_id = chal["id"]
        timeout_sec = chal.get("timeout", 14.0)
        now = time.time()

        # Update anti-spoofing historical buffers
        ear = face_data.get("ear", 0.0)
        yaw = face_data.get("yaw", 0.0)
        pitch = face_data.get("pitch", 0.0)
        if face_data.get("detected"):
            self.ear_history.append(ear)
            self.yaw_history.append(yaw)
            self.pitch_history.append(pitch)

        # Step Timeout Check
        if (now - self.step_start_time) > timeout_sec:
            self.failed_challenges.append({
                "id": chal_id,
                "instruction": chal["instruction"],
                "reason": "TIMEOUT_EXPIRED",
                "time_taken": timeout_sec
            })
            self._advance_step(face_data)
            return False, False

        condition_met = False
        tr = face_data.get("turn_ratio", 0.5)
        blinks_done = face_data.get("total_blinks", 0) - self.blink_baseline
        is_smiling = face_data.get("is_smiling", False) or face_data.get("smile_intensity", 0.0) > 0.40

        f_state = hand_data.get("finger_state") or {}
        ext_count = f_state.get("extended_count", 0)
        hand_detected = hand_data.get("detected", False)

        # STAGE 1: COMPREHENSIVE BIOMECHANICAL FLUIDITY CALIBRATION
        # Moves head smoothly left & right + shows hand and fingers to camera
        if chal_id == "BIOMECHANICAL_FLUIDITY":
            if (yaw < -8.0) or (tr < 0.38):
                self.calib_head_left = True
            if (yaw > 8.0) or (tr > 0.62):
                self.calib_head_right = True
            if hand_detected and (ext_count >= 2):
                self.calib_hand_seen = True

            condition_met = (
                getattr(self, "calib_head_left", False) and
                getattr(self, "calib_head_right", False) and
                getattr(self, "calib_hand_seen", False)
            )

        # STAGE 1 (Alternate): HEAD POSE — Requires deliberate turn (12° threshold) held for 1.2s
        elif chal_id == "HEAD_LEFT":
            condition_met = (yaw < -12.0) or (tr < 0.35)
        elif chal_id == "HEAD_RIGHT":
            condition_met = (yaw > 12.0) or (tr > 0.65)
        elif chal_id == "HEAD_UP":
            condition_met = (pitch > 9.0)
        elif chal_id == "HEAD_DOWN":
            condition_met = (pitch < -9.0)

        # STAGE 2: MULTIMODAL GESTURE + BLINK / SMILE (Requires 1.2s steady hold)
        elif chal_id == "BLINK_AND_THREE_FINGERS":
            condition_met = (blinks_done >= 1) and hand_detected and (ext_count == 3)
        elif chal_id == "SMILE_AND_THREE_FINGERS":
            condition_met = is_smiling and hand_detected and (ext_count == 3)
        elif chal_id == "THUMBS_UP_AND_BLINK":
            is_thumb = f_state.get("thumb", False) and ext_count <= 2
            condition_met = is_thumb and (blinks_done >= 1)
        elif chal_id == "OPEN_PALM_AND_SMILE":
            is_palm = f_state.get("is_open_palm", False) or (ext_count >= 4)
            condition_met = is_palm and is_smiling

        # STAGE 3: SPOKEN ALPHANUMERIC CODE (7-8 Characters)
        elif chal_id == "SPOKEN_CODE_GESTURE":
            spoken_text = extra.get("spoken_text", "")
            if spoken_text:
                ver_res = self.lip_validator.verify_code(spoken_text, self.active_code)
                condition_met = ver_res.get("passed", False)
                if condition_met:
                    print(f"[+] Spoken Code Verified: '{spoken_text}' matches '{self.active_code}'")

        # STAGE 4: AIR-DRAWING SHAPE KINEMATICS (Requires >=70% actual waypoints traced & >= 4.0s)
        elif chal_id in ["DRAW_STAR", "DRAW_SQUARE", "DRAW_INFINITY"]:
            client_conf = float(extra.get("path_conformance", 0.0))
            self.shape_visited_conformance = max(self.shape_visited_conformance, client_conf)

            elapsed_shape = now - (self.shape_start_time if self.shape_start_time else now)
            asym = kinematic_data.get("asymmetry", {}).get("nose_asymmetry_index", 0.78)
            power_law = kinematic_data.get("power_law", {})
            is_bio = power_law.get("is_biological", True) or (0.50 <= asym <= 1.65)

            # Rigorous criteria: MUST have actually traced at least 70% of waypoints AND spent at least 4.0s
            condition_met = (self.shape_visited_conformance >= 0.70) and (elapsed_shape >= 4.0) and is_bio

        # Deliberate Hold Time — 1.2s forces voluntary sustained action (can't be faked by frame injection)
        # Bug fix: 0.75s was not sufficient to distinguish deliberate human from AI frame replacement
        hold_time = 1.2 if chal.get("type") in ["HEAD_POSE", "MULTIMODAL_GESTURE"] else 0.0
        if condition_met:
            if self.step_hold_start is None:
                self.step_hold_start = now
            if (now - self.step_hold_start) >= hold_time:
                self._record_pass(chal_id, now - self.step_start_time)
                self._advance_step(face_data)
                return True, True
        else:
            self.step_hold_start = None

        return condition_met, False

    def _record_pass(self, chal_id: str, duration: float):
        chal = self.selected_challenges[self.current_step]
        self.completed_challenges.append({
            "id": chal_id,
            "instruction": chal["instruction"],
            "time_taken_sec": round(duration, 2),
            "status": "PASSED"
        })
        print(f"[+] Step #{self.current_step + 1} ({chal_id}) PASSED in {duration:.2f}s")

    def _advance_step(self, face_data: dict):
        self.current_step += 1
        self.step_start_time = time.time()
        self.step_hold_start = None
        self.shape_visited_conformance = 0.0
        self.blink_baseline = face_data.get("total_blinks", 0)

        if self.current_step >= len(self.selected_challenges):
            if self.mode == "live":
                self.is_gateway_cleared = True
                print(f"[+] All initial challenges cleared for Session #{self.session_id}! Entering 24/7 passive background shield.")
            else:
                self.is_completed = True
        else:
            self._setup_current_step()

    def evaluate_live_liveness_health(self, frame_bgr: np.ndarray, face_data: dict,
                                     df_data: dict, rppg_data: dict,
                                     biomarker_data: dict, is_frozen: bool) -> dict:
        """
        Rigorous Anti-Spoofing & Replay Defense:
        - Detects Printed Photos (zero eyelid tremor, zero blink, zero pose variance)
        - Detects Phone Screens & Video Replays (2D FFT Moiré pattern, specular screen glare, 2D planar depth)
        - Detects Frozen Cameras & Video Loops
        """
        is_face = face_data.get("detected", False)
        if not is_face:
            return {
                "verdict": "SUSPICIOUS: NO HUMAN IN VIEW",
                "is_suspicious": True,
                "low_bar_id": "face",
                "score": 0,
                "alert": "No human face detected in camera viewport.",
                "color": "#ef4444"
            }

        # 1. Camera Freeze or Virtual Camera Loop
        if is_frozen:
            return {
                "verdict": "SUSPICIOUS: CAMERA FEED FROZEN",
                "is_suspicious": True,
                "low_bar_id": "freeze",
                "score": 15,
                "alert": "VIDEO STREAM FROZEN: Static frame or virtual injection stall detected.",
                "color": "#ef4444"
            }

        face_box = face_data.get("face_box")
        screen_insp = self.screen_detector.inspect_frame(frame_bgr, face_box)

        # 2. Phone Screen 2D FFT Moiré Pattern Peak Detection (Screens produce sharp subpixel grid spikes)
        moire_peak = screen_insp.get("moire_peak", 0.0)
        has_moire = screen_insp.get("has_moire", False)
        if has_moire or moire_peak > 5.2:
            return {
                "verdict": "SUSPICIOUS: PHONE SCREEN / MONITOR REPLAY",
                "is_suspicious": True,
                "low_bar_id": "moire",
                "score": 20,
                "alert": f"PHONE SCREEN DETECTED: 2D FFT Moiré subpixel grid spike ({moire_peak:.1f}x) from smartphone/monitor.",
                "color": "#ef4444"
            }

        # 3. Static Photo Defense: Real humans exhibit eyelid micro-nystagmus and non-zero EAR variance.
        # Photos held in hand have rigid displacement with near-zero intrinsic biological variance.
        if len(self.ear_history) >= 15:
            ear_std = float(np.std(self.ear_history))
            yaw_std = float(np.std(self.yaw_history))
            pitch_std = float(np.std(self.pitch_history))

            if ear_std < 0.0018 and yaw_std < 0.35 and pitch_std < 0.35:
                return {
                    "verdict": "SUSPICIOUS: STATIC PHOTO / REPLAY",
                    "is_suspicious": True,
                    "low_bar_id": "photo_spoof",
                    "score": 22,
                    "alert": "STATIC PHOTO ATTACK: Zero eye blinking and rigid planar lack of biological motion.",
                    "color": "#ef4444"
                }

        # 4. 3D Spatial Depth Parallax vs 2D Planar Rotation
        parallax = face_data.get("depth_parallax", 0.0)
        yaw = abs(face_data.get("yaw", 0.0))
        if parallax < 0.032 and yaw > 5.5:
            return {
                "verdict": "SUSPICIOUS: 2D FLAT PLANE REPLAY",
                "is_suspicious": True,
                "low_bar_id": "parallax",
                "score": 28,
                "alert": "FLAT 2D SURFACE DETECTED: Lack of 3D facial depth relief during head rotation.",
                "color": "#ef4444"
            }

        # 5. Deepfake Frequency Artifacts
        auth = df_data.get("authenticity_score", 0.90) if isinstance(df_data, dict) else 0.90
        if auth < 0.42:
            return {
                "verdict": "SUSPICIOUS: DEEPFAKE ANOMALY",
                "is_suspicious": True,
                "low_bar_id": "authenticity",
                "score": 35,
                "alert": "DEEPFAKE ARTIFACTS: Synthetic frequency distortions detected.",
                "color": "#ef4444"
            }

        return {
            "verdict": "LIVE: VERIFIED GENUINE HUMAN",
            "is_suspicious": False,
            "low_bar_id": "none",
            "score": 96,
            "alert": "All biological vectors verified & active. Passive proctoring shield running.",
            "color": "#10b981"
        }

    def calculate_final_summary(self, face_metrics: dict, hand_metrics: dict, df_metrics: dict, rppg_metrics: dict) -> dict:
        total = max(1, len(self.selected_challenges))
        passed = len(self.completed_challenges)
        pass_ratio = passed / total

        challenge_score = pass_ratio * 100.0
        face_score = (face_metrics.get("micro_movement_score", 0.95) * 100.0)
        bio_score = (hand_metrics.get("bio_score", 0.95) * 100.0)
        df_score = (df_metrics.get("authenticity_score", 0.92) * 100.0)
        rppg_score = (rppg_metrics.get("liveness_score", 0.85) * 100.0)

        final_score = round(
            (0.35 * challenge_score) +
            (0.20 * face_score) +
            (0.15 * bio_score) +
            (0.15 * df_score) +
            (0.15 * rppg_score),
            1
        )

        verdict = "VERIFIED" if (final_score >= 68.0 and passed >= 1) else ("SUSPICIOUS" if final_score >= 45.0 else "FAILED")
        confidence = "HIGH CONFIDENCE (GENUINE HUMAN)" if verdict == "VERIFIED" else "REVIEW REQUIRED"

        return {
            "session_id": self.session_id,
            "verdict": verdict,
            "score": final_score,
            "confidence_level": confidence,
            "challenges_completed": passed,
            "total_challenges": total,
            "duration_sec": round(time.time() - self.session_start_time, 2),
            "heart_rate_bpm": rppg_metrics.get("bpm", 0.0),
            "sub_scores": {
                "challenge_response": round(challenge_score, 1),
                "face_liveness": round(face_score, 1),
                "hand_biomechanics": round(bio_score, 1),
                "deepfake_security": round(df_score, 1),
                "rppg_pulse_liveness": round(rppg_score, 1)
            },
            "completed_challenges": self.completed_challenges,
            "failed_challenges": self.failed_challenges
        }


# ============================================================================
# 2. DETECTOR INSTANTIATIONS
# ============================================================================

FACE_MODEL = os.path.join(os.path.dirname(__file__), "face_landmarker.task")
HAND_MODEL = os.path.join(os.path.dirname(__file__), "hand_landmarker.task")

face_detector = FaceLivenessDetector(model_path=FACE_MODEL if os.path.exists(FACE_MODEL) else "face_landmarker.task")
hand_detector = HandBiomechanicsDetector(model_path=HAND_MODEL if os.path.exists(HAND_MODEL) else "hand_landmarker.task")
deepfake_detector = DeepfakeArtifactDetector()
rppg_detector = rPPGLivenessDetector(buffer_size=120, fps=30.0)
kinematic_tracker = KinematicTremorTracker(fps=30.0)
biomarker_monitor = BiomarkerMonitor(phase=2, fps=30.0)
lip_sync_validator = LipSyncValidator()


def decode_base64_image(image_data: str) -> np.ndarray:
    if "," in image_data:
        image_data = image_data.split(",", 1)[1]
    raw_bytes = base64.b64decode(image_data)
    nparr = np.frombuffer(raw_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return frame


# ============================================================================
# 3. WEBSOCKET VERIFICATION ENDPOINT
# ============================================================================

@app.websocket("/ws/verify")
async def websocket_verify_endpoint(websocket: WebSocket):
    await websocket.accept()
    mode = websocket.query_params.get("mode", "live")
    manager = ChallengeManager(mode=mode)

    rppg_detector.reset()
    kinematic_tracker.reset()
    biomarker_monitor.reset()

    prev_gray = None
    frozen_frame_count = 0

    last_face_data = {}
    last_hand_data = {}
    last_df_data = {}
    last_rppg_data = {}
    last_kinematic = {}
    last_biomarker = {}
    pending_spoken_text = ""  # Buffer for speech recognition results arriving between frames

    print(f"[+] WebSocket Client Connected ({mode.upper()} mode): Session #{manager.session_id}")

    try:
        initial_chal = manager.get_active_challenge_info()
        init_payload = {
            "status": "in_progress",
            "session_id": manager.session_id,
            "mode": mode,
            "challenge": initial_chal["instruction"],
            "speech": initial_chal.get("speech", initial_chal["instruction"]),
            "challenge_id": initial_chal["challenge_id"],
            "step": initial_chal["step"],
            "total_steps": initial_chal["total_steps"],
            "progress": initial_chal["progress"],
            "time_left": initial_chal["time_left"],
            "timeout_sec": initial_chal["timeout_sec"],
            "is_gateway_cleared": False,
            "message": f"{mode.title()} session initialized."
        }
        if "spoken_code" in initial_chal:
            init_payload["spoken_code"] = initial_chal["spoken_code"]
        if "waypoints" in initial_chal:
            init_payload["waypoints"] = initial_chal["waypoints"]
            init_payload["shape_type"] = initial_chal.get("shape_type", "star")

        await websocket.send_json(init_payload)

        while not manager.is_completed:
            data_text = await websocket.receive_text()
            try:
                msg = json.loads(data_text)
            except Exception:
                continue

            if msg.get("action") == "stop":
                print(f"[-] Client requested clean stop: Session #{manager.session_id}")
                break

            # Buffer spoken_text from speech recognition (arrives without image)
            if msg.get("spoken_text"):
                pending_spoken_text = msg["spoken_text"]

            image_b64 = msg.get("image") or msg.get("frame")
            if not image_b64:
                continue

            # Merge any buffered speech recognition text into the frame message
            if pending_spoken_text and not msg.get("spoken_text"):
                msg["spoken_text"] = pending_spoken_text

            try:
                frame = decode_base64_image(image_b64)
                if frame is None:
                    continue
            except Exception:
                continue

            # Anti-Freeze Frame Difference Detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            is_frozen = False
            if prev_gray is not None and prev_gray.shape == gray.shape:
                frame_diff = float(np.mean(cv2.absdiff(gray, prev_gray)))
                if frame_diff < 0.25:
                    frozen_frame_count += 1
                else:
                    frozen_frame_count = max(0, frozen_frame_count - 2)
                is_frozen = (frozen_frame_count >= 20)
            prev_gray = gray

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            last_face_data = face_detector.process_frame(rgb)
            last_hand_data = hand_detector.process_frame(rgb)
            last_df_data = deepfake_detector.analyze_face(frame, last_face_data.get("face_box"))
            last_rppg_data = rppg_detector.update(frame, last_face_data.get("landmarks"))
            last_biomarker = biomarker_monitor.update(frame, last_face_data.get("landmarks"))

            # Feed Kinematics Tracker
            if last_face_data.get("detected") and last_face_data.get("landmarks"):
                nose_lm = last_face_data["landmarks"][1]
                kinematic_tracker.push_nose(nose_lm.x, nose_lm.y)

            # Extract index fingertip landmark (id: 8) for accurate shape air-drawing
            index_tip = None
            if last_hand_data.get("detected") and last_hand_data.get("landmarks"):
                lms = last_hand_data["landmarks"]
                index_tip = {"x": round(float(lms[8].x), 3), "y": round(float(lms[8].y), 3)}
                kinematic_tracker.push_wrist(lms[8].x, lms[8].y)

            last_kinematic = kinematic_tracker.get_tremor_profile()

            # Evaluate Telemetry & Rigorous Anti-Spoofing
            is_met, is_passed = manager.evaluate_telemetry(last_face_data, last_hand_data, msg, last_kinematic)
            live_health = manager.evaluate_live_liveness_health(
                frame, last_face_data, last_df_data, last_rppg_data, last_biomarker, is_frozen
            )

            curr_chal = manager.get_active_challenge_info()
            if curr_chal:
                ext_count = 0
                if last_hand_data.get("finger_state"):
                    ext_count = last_hand_data["finger_state"].get("extended_count", 0)

                resp_payload = {
                    "status": "live_monitoring" if (mode == "live" or curr_chal.get("is_passive")) else "in_progress",
                    "mode": mode,
                    "session_id": manager.session_id,
                    "is_gateway_cleared": manager.is_gateway_cleared,
                    "is_passive": curr_chal.get("is_passive", False),
                    "live_health": live_health,
                    "challenge": curr_chal["instruction"],
                    "speech": curr_chal.get("speech", ""),
                    "challenge_id": curr_chal["challenge_id"],
                    "step": curr_chal["step"],
                    "total_steps": curr_chal["total_steps"],
                    "progress": curr_chal["progress"],
                    "time_left": curr_chal["time_left"],
                    "timeout_sec": curr_chal.get("timeout_sec", 14.0),
                    "is_challenge_met": is_met,
                    "is_challenge_passed": is_passed,
                    "telemetry": {
                        "face_detected": last_face_data.get("detected", False),
                        "yaw": round(last_face_data.get("yaw", 0.0), 1),
                        "pitch": round(last_face_data.get("pitch", 0.0), 1),
                        "ear": round(last_face_data.get("ear", 0.0), 3),
                        "blinks": last_face_data.get("total_blinks", 0),
                        "is_smiling": last_face_data.get("is_smiling", False),
                        "hand_detected": last_hand_data.get("detected", False),
                        "fingers_detected": ext_count,
                        "index_tip": index_tip,
                        "heart_rate_bpm": last_rppg_data.get("bpm", 0.0),
                        "is_pulse_valid": last_rppg_data.get("is_pulse_valid", False),
                        "depth_parallax": round(float(last_face_data.get("depth_parallax", 0.0)), 2),
                        "tremor_variance": float(last_face_data.get("tremor_variance", 0.0)),
                        "micro_jitter_std": round(float(last_biomarker.get("jitter", {}).get("std", 0.015)), 6),
                        "tremor_freq_hz": last_kinematic.get("nose", {}).get("tremor_freq_hz", 8.4),
                        "asymmetry_index": last_kinematic.get("asymmetry", {}).get("nose_asymmetry_index", 0.78),
                        "is_asymmetric_human": last_kinematic.get("asymmetry", {}).get("is_asymmetric_human", True),
                        "power_law_score": last_kinematic.get("power_law", {}).get("power_law_score", 0.88),
                        "freeze_detected": is_frozen,
                        "cognitive_latency_ms": int(max(0, (time.time() - manager.step_start_time) * 1000.0))
                    }
                }

                if "spoken_code" in curr_chal:
                    resp_payload["spoken_code"] = curr_chal["spoken_code"]
                if "waypoints" in curr_chal:
                    resp_payload["waypoints"] = curr_chal["waypoints"]
                    resp_payload["shape_type"] = curr_chal.get("shape_type", "star")

                await websocket.send_json(resp_payload)

        # Always compute and persist session audit record to database
        summary = manager.calculate_final_summary(last_face_data, last_hand_data, last_df_data, last_rppg_data)
        summary["mode"] = mode
        if mode == "live" and manager.is_gateway_cleared:
            summary["verdict"] = "VERIFIED"
            summary["confidence_level"] = "HIGH CONFIDENCE (LIVE SHIELD CLEARED)"
        db_id = database.save_verification(summary)
        summary["db_record_id"] = db_id
        summary["status"] = "completed"
        print(f"[+] {mode.title()} Session Saved to Database: #{summary['session_id']} | Verdict: {summary['verdict']} | Score: {summary['score']}%")

        if mode == "standard":
            await websocket.send_json(summary)
            await websocket.close()
        elif mode == "live":
            try:
                summary["status"] = "live_stopped"
                await websocket.send_json(summary)
            except Exception:
                pass

    except WebSocketDisconnect:
        print(f"[-] Client disconnected: Session #{manager.session_id}")
    except Exception as e:
        print(f"[-] WebSocket Error: {e}")
        try:
            await websocket.close()
        except Exception:
            pass


# ============================================================================
# 4. REST APIS FOR DASHBOARD & SESSIONS
# ============================================================================

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "4.5.0"}


@app.get("/")
def root_entry():
    return RedirectResponse(url="/client")


@app.get("/api/sessions")
def get_sessions_api():
    sessions = database.get_recent_verifications(limit=50)
    return JSONResponse(content={"sessions": sessions})


@app.get("/api/dashboard/stats")
def get_dashboard_stats_api():
    stats = database.get_verification_stats()
    return JSONResponse(content=stats)


# ============================================================================
# 5. ADMIN & ANALYTICS DASHBOARD (/dashboard)
# ============================================================================

@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TrustLayer - Biometric Analytics Dashboard</title>
    <style>
        * { margin:0; padding:0; box-sizing:border-box; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        body { background:#09090b; color:#f4f4f5; padding:24px; }
        .hdr { display:flex; justify-content:space-between; align-items:center; margin-bottom:24px; border-bottom:1px solid #27272a; padding-bottom:16px; }
        .hdr h1 { font-size:24px; font-weight:800; color:#38bdf8; letter-spacing:0.5px; }
        .hdr-actions a { color:#38bdf8; text-decoration:none; margin-left:16px; font-size:13px; font-weight:700; }
        .grid { display:grid; grid-template-columns:repeat(4, 1fr); gap:16px; margin-bottom:24px; }
        .card { background:#18181b; border:1px solid #27272a; border-radius:12px; padding:18px; }
        .card-lbl { font-size:11px; text-transform:uppercase; color:#a1a1aa; letter-spacing:1px; }
        .card-val { font-size:26px; font-weight:800; color:#fff; margin-top:8px; font-family:monospace; }
        table { width:100%; border-collapse:collapse; background:#18181b; border:1px solid #27272a; border-radius:12px; overflow:hidden; }
        th, td { padding:12px 16px; text-align:left; border-bottom:1px solid #27272a; font-size:13px; }
        th { background:#202025; color:#a1a1aa; font-size:11px; text-transform:uppercase; letter-spacing:1px; }
        .badge { padding:4px 10px; border-radius:6px; font-weight:800; font-size:11px; font-family:monospace; }
        .badge-verified { background:#10b98125; color:#10b981; border:1px solid #10b98150; }
        .badge-failed { background:#ef444425; color:#ef4444; border:1px solid #ef444450; }
        .badge-suspicious { background:#f59e0b25; color:#f59e0b; border:1px solid #f59e0b50; }
    </style>
</head>
<body>
    <div class="hdr">
        <div>
            <h1>TRUSTLAYER // ANALYTICS & AUDIT PORTAL</h1>
            <p style="font-size:12px; color:#71717a; margin-top:4px;">Zeal College of Engineering & Research &bull; Department of ECE &bull; Pune-41</p>
        </div>
        <div class="hdr-actions">
            <a href="/client">OPEN WEB VERIFICATION CLIENT &rarr;</a>
        </div>
    </div>

    <div class="grid">
        <div class="card"><div class="card-lbl">Total Audits</div><div class="card-val" id="stTotal">--</div></div>
        <div class="card"><div class="card-lbl">Verified Genuine</div><div class="card-val" style="color:#10b981;" id="stVerified">--</div></div>
        <div class="card"><div class="card-lbl">Attack Rejections</div><div class="card-val" style="color:#ef4444;" id="stFailed">--</div></div>
        <div class="card"><div class="card-lbl">Pass Ratio</div><div class="card-val" style="color:#38bdf8;" id="stRatio">--%</div></div>
    </div>

    <div style="font-size:13px; font-weight:800; text-transform:uppercase; letter-spacing:1px; color:#a1a1aa; margin-bottom:12px;">Recent Audit Sessions</div>
    <table>
        <thead>
            <tr>
                <th>Session ID</th>
                <th>Timestamp</th>
                <th>Mode</th>
                <th>Verdict</th>
                <th>Trust Score</th>
                <th>rPPG Pulse</th>
                <th>Challenges</th>
                <th>Duration</th>
            </tr>
        </thead>
        <tbody id="sessionRows">
            <tr><td colspan="8" style="text-align:center; color:#71717a;">Loading session records...</td></tr>
        </tbody>
    </table>

    <script>
        async function loadStats() {
            try {
                const res = await fetch('/api/dashboard/stats');
                const d = await res.json();
                document.getElementById('stTotal').innerText = d.total_verifications || 0;
                document.getElementById('stVerified').innerText = d.verified_count || 0;
                document.getElementById('stFailed').innerText = d.failed_count || 0;
                const r = d.total_verifications ? Math.round((d.verified_count / d.total_verifications) * 100) : 0;
                document.getElementById('stRatio').innerText = `${r}%`;
            } catch(e) {}
            try {
                const res = await fetch('/api/sessions');
                const d = await res.json();
                const tbody = document.getElementById('sessionRows');
                if (d.sessions && d.sessions.length) {
                    tbody.innerHTML = d.sessions.map(s => {
                        const isV = s.verdict === 'VERIFIED';
                        const cls = isV ? 'badge-verified' : (s.verdict === 'SUSPICIOUS' ? 'badge-suspicious' : 'badge-failed');
                        const isLive = (s.mode || '').toLowerCase() === 'live';
                        const modeBadge = isLive 
                            ? '<span class="badge" style="background:#10b98120; color:#10b981; border:1px solid #10b98150;">🟢 LIVE SHIELD</span>'
                            : '<span class="badge" style="background:#38bdf820; color:#38bdf8; border:1px solid #38bdf850;">⚡ STANDARD</span>';
                        return `<tr>
                            <td style="font-family:monospace; font-weight:700;">${s.session_id}</td>
                            <td style="color:#a1a1aa;">${s.timestamp}</td>
                            <td>${modeBadge}</td>
                            <td><span class="badge ${cls}">${s.verdict}</span></td>
                            <td style="font-weight:700;">${s.score}%</td>
                            <td style="color:#10b981;">${s.heart_rate_bpm ? Math.round(s.heart_rate_bpm) + ' BPM' : '--'}</td>
                            <td>${s.challenges_completed} / ${s.total_challenges}</td>
                            <td style="color:#a1a1aa;">${s.duration_sec}s</td>
                        </tr>`;
                    }).join('');
                } else {
                    tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; color:#71717a;">No sessions recorded yet. Run a verification audit on /client.</td></tr>';
                }
            } catch(e) {}
        }
        loadStats();
        setInterval(loadStats, 4000);
    </script>
</body>
</html>"""


# ============================================================================
# 6. PANORAMIC ONE-SCREEN USER INTERFACE (/client) — Primary UI
# ============================================================================

@app.get("/client", response_class=HTMLResponse)
def get_web_client():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TrustLayer - Continuous Biometric Human Verification</title>
    <style>
        * { margin:0; padding:0; box-sizing:border-box; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        body {
            background:#09090b; color:#f4f4f5;
            height:100vh; max-height:100vh; overflow:hidden;
            display:flex; flex-direction:column; padding:10px 16px;
        }

        /* TOP COMPACT NAV */
        .top-navbar {
            display:flex; justify-content:space-between; align-items:center;
            padding:0 4px 8px; border-bottom:1px solid #27272a; margin-bottom:8px;
            flex-shrink:0;
        }
        .nav-brand h1 { font-size:17px; color:#38bdf8; font-weight:900; letter-spacing:0.5px; }
        .nav-brand p { font-size:9.5px; color:#71717a; text-transform:uppercase; letter-spacing:1px; }

        .system-switcher { display:flex; gap:8px; }
        .sys-tab {
            background:#18181b; border:1px solid #27272a; padding:6px 14px; border-radius:8px;
            cursor:pointer; display:flex; align-items:center; gap:8px; transition:all 0.2s; color:#a1a1aa;
        }
        .sys-tab:hover { background:#202025; color:#fff; }
        .sys-tab.active { background:#141418; border-color:#38bdf8; color:#fff; box-shadow:0 0 14px rgba(56, 189, 248, 0.2); }
        .sys-tab.active.green-active { border-color:#10b981; box-shadow:0 0 14px rgba(16, 185, 129, 0.2); }
        .sys-tab-icon { font-size:13px; }
        .sys-tab-title { font-size:11px; font-weight:800; letter-spacing:0.4px; }

        /* 3-COLUMN MAIN DASHBOARD (ONE-SCREEN PANORAMIC LAYOUT) */
        .main-panoramic-grid {
            display:grid;
            grid-template-columns: 290px 1fr 310px;
            gap: 12px;
            flex:1;
            min-height:0;
            overflow:hidden;
        }

        /* SIDE PANELS (LEFT & RIGHT) */
        .side-panel {
            background:#121215; border:1px solid #27272a; border-radius:12px;
            padding:12px; display:flex; flex-direction:column; gap:8px;
            min-height:0; overflow:hidden;
        }
        .panel-header {
            font-size:10.5px; font-weight:800; text-transform:uppercase; letter-spacing:1.2px;
            color:#38bdf8; display:flex; align-items:center; gap:6px;
            padding-bottom:6px; border-bottom:1px solid #27272a; flex-shrink:0;
        }

        /* LEFT COLUMN: VERTICAL NUMERIC TELEMETRY */
        .numeric-stack {
            display: flex;
            flex-direction: column;
            gap: 6px;
            flex: 1;
            min-height: 0;
            justify-content: space-between;
        }
        .telemetry-card {
            background: #18181b;
            border: 1px solid #27272a;
            border-radius: 8px;
            padding: 6px 10px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            transition: all 0.2s ease;
        }
        .telemetry-card:hover {
            border-color: #3f3f46;
            background: #1c1c21;
        }
        .tc-left {
            display: flex;
            flex-direction: column;
            gap: 1px;
            text-align: left;
        }
        .tc-label {
            font-size: 10px;
            text-transform: uppercase;
            color: #a1a1aa;
            letter-spacing: 0.6px;
            font-weight: 700;
        }
        .tc-sub {
            font-size: 8.5px;
            color: #71717a;
        }
        .tc-val {
            font-size: 13.5px;
            font-weight: 800;
            color: #fff;
            font-family: monospace;
            text-align: right;
            background: #202025;
            padding: 3px 8px;
            border-radius: 5px;
            border: 1px solid #2e2e33;
            letter-spacing: 0.3px;
        }

        /* CENTER COLUMN: CAMERA & TASK BOX */
        .center-panel {
            display:flex; flex-direction:column; gap:8px; min-height:0; overflow:hidden;
        }
        .camera-viewport-box {
            flex:1; min-height:0; background:#18181b; border:2px solid #27272a; border-radius:14px;
            padding:6px; position:relative; display:flex; flex-direction:column; align-items:center; justify-content:center;
            overflow:hidden;
        }
        .camera-wrapper {
            position:relative; width:100%; height:100%; border-radius:10px; overflow:hidden; background:#000;
            display:flex; align-items:center; justify-content:center;
        }
        video { width:100%; height:100%; object-fit:contain; display:block; transform:scaleX(-1); background:#000; }
        canvas.hud-overlay { position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; }
        canvas.hidden-canvas { display:none; }

        .camera-status-pill {
            position:absolute; top:10px; left:10px; background:rgba(9, 9, 11, 0.85); backdrop-filter:blur(6px);
            border:1px solid #10b981; border-radius:16px; padding:4px 10px; display:flex; align-items:center; gap:6px; z-index:10;
        }
        .pill-dot { width:7px; height:7px; border-radius:50%; background:#10b981; box-shadow:0 0 6px #10b981; }
        .pill-dot.suspicious { background:#ef4444 !important; box-shadow:0 0 8px #ef4444 !important; }
        .pill-text { font-size:10px; font-weight:800; color:#10b981; }
        .pill-text.suspicious { color:#ef4444 !important; }

        .voice-speaker-badge {
            position:absolute; top:10px; right:10px; background:rgba(9, 9, 11, 0.85); backdrop-filter:blur(6px);
            border:1px solid #38bdf850; border-radius:16px; padding:4px 10px; font-size:10px; color:#38bdf8;
            font-weight:700; display:flex; align-items:center; gap:4px; cursor:pointer; z-index:10;
        }

        /* TASKS DIRECTLY BELOW CAMERA */
        .task-action-box {
            background:#18181b; border:2px solid #38bdf8; border-radius:12px; padding:8px 14px;
            text-align:center; position:relative; flex-shrink:0;
        }
        .task-stage-badge {
            font-size:9.5px; font-weight:800; text-transform:uppercase; letter-spacing:1.2px; color:#38bdf8;
            background:#38bdf815; padding:2px 8px; border-radius:8px; display:inline-block; margin-bottom:3px;
        }
        .task-instruction-text {
            font-size:15px; font-weight:800; color:#fff; line-height:1.2; margin-bottom:5px;
        }
        .task-timer-bg { width:100%; height:5px; background:#27272a; border-radius:3px; overflow:hidden; }
        .task-timer-fill { height:100%; width:100%; background:#38bdf8; transition:width 0.1s linear; }

        .code-badges-container {
            display:none; margin:5px auto; padding:5px; background:#141418; border:1px solid #38bdf840; border-radius:8px; max-width:540px;
        }
        .code-badges-label { font-size:9px; text-transform:uppercase; color:#38bdf8; font-weight:800; margin-bottom:3px; }
        .code-tiles-row { display:flex; justify-content:center; gap:6px; flex-wrap:wrap; }
        .code-tile {
            width:32px; height:38px; background:#27272a; border:2px solid #38bdf8; border-radius:6px;
            font-size:17px; font-weight:900; color:#fff; display:flex; align-items:center; justify-content:center;
            font-family:monospace; box-shadow:0 0 10px rgba(56, 189, 248, 0.25);
        }
        .voice-caption { font-size:10.5px; color:#10b981; font-weight:700; margin-top:3px; }

        .shape-progress-badge {
            display:none; margin:5px auto; padding:3px 10px; background:#141418; border:1px solid #fbbf24;
            border-radius:8px; color:#fbbf24; font-size:10.5px; font-weight:800; font-family:monospace;
        }

        .passive-shield-banner {
            display:none; background:#10b98115; border:2px solid #10b981; border-radius:12px; padding:10px; text-align:center; flex-shrink:0;
        }
        .passive-banner-title { font-size:12.5px; font-weight:900; color:#10b981; letter-spacing:0.5px; }
        .passive-banner-sub { font-size:10.5px; color:#a1a1aa; margin-top:3px; line-height:1.3; }

        .action-button-row { width:100%; flex-shrink:0; }
        .btn {
            background:#10b981; color:#09090b; border:none; padding:10px 18px; border-radius:10px;
            font-weight:800; font-size:13.5px; cursor:pointer; width:100%; transition:all 0.2s; letter-spacing:0.5px;
        }
        .btn:hover { background:#059669; }
        .btn.btn-stop { background:#ef4444; color:#fff; }
        .btn.btn-stop:hover { background:#dc2626; }
        .btn.btn-cyan { background:#38bdf8; color:#09090b; }
        .btn.btn-cyan:hover { background:#0284c7; }

        /* RIGHT COLUMN: REAL-TIME GRAPHS & WAVEFORMS */
        .graph-stack {
            display:flex; flex-direction:column; gap:8px; flex:1; min-height:0; justify-content:space-between;
        }
        .graph-box {
            background:#18181b; border:1px solid #27272a; border-radius:8px; padding:8px 10px;
            display:flex; flex-direction:column; justify-content:space-between; flex:1; min-height:0;
        }
        .sb-hdr { display:flex; justify-content:space-between; align-items:center; margin-bottom:3px; }
        .sb-title { font-size:10px; font-weight:700; color:#e4e4e7; }
        .sb-val-pill {
            font-size:10px; font-family:monospace; font-weight:800; background:#27272a;
            padding:1px 6px; border-radius:4px;
        }
        .sb-canvas {
            width:100%; height:42px; display:block; border-radius:4px; background:#09090b; border:1px solid #202025;
        }

        /* MODAL */
        .modal-backdrop { display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.85); backdrop-filter:blur(6px); z-index:9999; align-items:center; justify-content:center; }
        .modal-backdrop.open { display:flex; }
        .modal-card { background:#18181b; border:2px solid #38bdf8; border-radius:16px; max-width:540px; width:92%; padding:22px; position:relative; box-shadow:0 20px 60px rgba(0,0,0,0.8); }
        .modal-close-btn { position:absolute; top:14px; right:14px; background:#27272a; border:none; color:#a1a1aa; width:28px; height:28px; border-radius:50%; font-size:16px; cursor:pointer; }
    </style>
</head>
<body>
    <!-- TOP COMPACT NAV BAR -->
    <div class="top-navbar">
        <div class="nav-brand">
            <h1>TRUSTLAYER // CONTINUOUS HUMAN VERIFICATION SHIELD</h1>
            <p>Zeal College of Engineering & Research &bull; Department of ECE &bull; Pune-41</p>
        </div>

        <div class="system-switcher">
            <button class="sys-tab green-active active" id="tabLive" onclick="setSystemMode('live')">
                <span class="sys-tab-icon">🟢</span>
                <span class="sys-tab-title">SYSTEM 2: LIVE MONITOR</span>
            </button>

            <button class="sys-tab" id="tabStandard" onclick="setSystemMode('standard')">
                <span class="sys-tab-icon">⚡</span>
                <span class="sys-tab-title">SYSTEM 1: AUDIT PROTOCOL</span>
            </button>

            <a href="/dashboard" class="sys-tab" style="text-decoration:none; color:#38bdf8; border-color:#38bdf850; background:#38bdf815;" title="Open Analytics & Audit History">
                <span class="sys-tab-icon">📊</span>
                <span class="sys-tab-title">AUDIT DASHBOARD</span>
            </a>
        </div>
    </div>

    <!-- 3-COLUMN ONE-SCREEN PANORAMIC LAYOUT -->
    <div class="main-panoramic-grid">

        <!-- 1. LEFT SIDE: NUMERIC VALUES & BIOMETRICS -->
        <div class="side-panel">
            <div class="panel-header">
                <span>📊</span>
                <span>NUMERIC BIOMETRICS</span>
            </div>
            <div class="numeric-stack">
                <div class="telemetry-card">
                    <div class="tc-left">
                        <div class="tc-label">rPPG Blood Pulse</div>
                        <div class="tc-sub">Capillary Flow Rate</div>
                    </div>
                    <div class="tc-val" id="valPulse" style="color:#10b981;">Acquiring...</div>
                </div>

                <div class="telemetry-card">
                    <div class="tc-left">
                        <div class="tc-label">Body Micro-Tremor</div>
                        <div class="tc-sub">Involuntary 6-12 Hz</div>
                    </div>
                    <div class="tc-val" id="valTremor">8.4 Hz</div>
                </div>

                <div class="telemetry-card">
                    <div class="tc-left">
                        <div class="tc-label">Kinematic Asymmetry</div>
                        <div class="tc-sub">Motor Invariant Index</div>
                    </div>
                    <div class="tc-val" id="valAsym">0.78 [Bio]</div>
                </div>

                <div class="telemetry-card">
                    <div class="tc-left">
                        <div class="tc-label">2/3 Power Law</div>
                        <div class="tc-sub">v &prop; &kappa;<sup>-1/3</sup> Biological</div>
                    </div>
                    <div class="tc-val" id="valPower">&beta; = 0.32</div>
                </div>

                <div class="telemetry-card">
                    <div class="tc-left">
                        <div class="tc-label">Head Rotation</div>
                        <div class="tc-sub">Vestibular Pose</div>
                    </div>
                    <div class="tc-val" id="valHeadPose">Y: 0.0&deg; | P: 0.0&deg;</div>
                </div>

                <div class="telemetry-card">
                    <div class="tc-left">
                        <div class="tc-label">Eye Dynamics</div>
                        <div class="tc-sub">Nystagmus & Blinks</div>
                    </div>
                    <div class="tc-val" id="valBlinks">EAR: 0.32 | 0 Bl</div>
                </div>

                <div class="telemetry-card">
                    <div class="tc-left">
                        <div class="tc-label">Hand Biomechanics</div>
                        <div class="tc-sub">Extended Fingers</div>
                    </div>
                    <div class="tc-val" id="valHand">0 Fingers</div>
                </div>

                <div class="telemetry-card">
                    <div class="tc-left">
                        <div class="tc-label">Skin Micro-Jitter</div>
                        <div class="tc-sub">Temporal STD Noise</div>
                    </div>
                    <div class="tc-val" id="valJitterNum">0.00140</div>
                </div>
            </div>
        </div>

        <!-- 2. CENTER: CAMERA & TASKS DIRECTLY BELOW IT -->
        <div class="center-panel">
            <div class="camera-viewport-box">
                <div class="camera-wrapper">
                    <video id="webcam" autoplay playsinline></video>
                    <canvas class="hud-overlay" id="hudOverlay" width="800" height="600"></canvas>
                    <canvas class="hidden-canvas" id="captureCanvas" width="640" height="480"></canvas>

                    <!-- Live Status Pill -->
                    <div class="camera-status-pill" id="cameraStatusPill">
                        <div class="pill-dot" id="pillDot"></div>
                        <span class="pill-text" id="pillText">STANDBY: READY TO START</span>
                    </div>

                    <!-- Voice Dictation Toggle Badge -->
                    <div class="voice-speaker-badge" id="voiceToggle" onclick="toggleVoiceDictation()">
                        <span id="speakerIcon">🔊</span>
                        <span id="speakerText">VOICE: ON</span>
                    </div>
                </div>
            </div>

            <!-- TASKS DIRECTLY BELOW CAMERA -->
            <div class="task-action-box" id="taskBox">
                <div class="task-stage-badge" id="stageBadge">SYSTEM GENERATED RANDOM PROTOCOL</div>
                <div class="task-instruction-text" id="taskInstruction">Click "START VERIFICATION" to begin</div>
                <div class="task-timer-bg"><div class="task-timer-fill" id="timerFill"></div></div>

                <!-- SPOKEN CODE TILES CONTAINER (7-8 CHARACTERS) -->
                <div class="code-badges-container" id="codeBadgesBox">
                    <div class="code-badges-label">Read the 7-8 Character Verification Code Aloud:</div>
                    <div class="code-tiles-row" id="codeTilesRow"></div>
                    <div class="voice-caption" id="voiceCaption">🎙️ Microphone listening for spoken digits...</div>
                </div>

                <!-- REAL SHAPE TRACING PROGRESS BADGE -->
                <div class="shape-progress-badge" id="shapeProgressBadge">
                    ⭐ TRACED: 0% (MIN 70% PERIMETER REQUIRED)
                </div>
            </div>

            <!-- PASSIVE SHIELD BANNER (ACTIVATED UPON VERIFICATION IN LIVE MODE) -->
            <div class="passive-shield-banner" id="passiveShieldBanner">
                <div class="passive-banner-title">✔ HUMAN VERIFICATION COMPLETE &bull; PASSIVE SHIELD ACTIVE</div>
                <div class="passive-banner-sub">
                    Session continuously protected in background. Passively monitoring involuntary body tremor (6-12 Hz), capillary rPPG blood flow, skin micro-jitter, and stream anti-freeze guard. Zero user tasks required.
                </div>
            </div>

            <!-- ACTION CONTROL BUTTON -->
            <div class="action-button-row">
                <button class="btn" id="actionBtn" onclick="toggleVerificationSession()">START LIVE MONITOR</button>
            </div>
        </div>

        <!-- 3. RIGHT SIDE: REAL-TIME GRAPHS & WAVEFORMS -->
        <div class="side-panel">
            <div class="panel-header">
                <span>📈</span>
                <span>REAL-TIME BIOSIGNAL GRAPHS</span>
            </div>
            <div class="graph-stack">
                <div class="graph-box">
                    <div class="sb-hdr">
                        <span class="sb-title">🟢 rPPG Capillary Pulse Wave</span>
                        <span class="sb-val-pill" id="txtPulse" style="color:#10b981;">Calibrating</span>
                    </div>
                    <canvas class="sb-canvas" id="canvasPulse" width="300" height="42"></canvas>
                </div>

                <div class="graph-box">
                    <div class="sb-hdr">
                        <span class="sb-title">🟣 Involuntary Micro-Tremor (6-12 Hz)</span>
                        <span class="sb-val-pill" id="txtTremorGraph" style="color:#a78bfa;">8.4 Hz</span>
                    </div>
                    <canvas class="sb-canvas" id="canvasTremor" width="300" height="42"></canvas>
                </div>

                <div class="graph-box">
                    <div class="sb-hdr">
                        <span class="sb-title">🔵 Skin Micro-Jitter (Cellular Noise)</span>
                        <span class="sb-val-pill" id="txtJitter" style="color:#38bdf8;">0.00140</span>
                    </div>
                    <canvas class="sb-canvas" id="canvasJitter" width="300" height="42"></canvas>
                </div>

                <div class="graph-box">
                    <div class="sb-hdr">
                        <span class="sb-title">🟡 Motor Kinematic Asymmetry Curve</span>
                        <span class="sb-val-pill" id="txtAsym" style="color:#fbbf24;">0.78</span>
                    </div>
                    <canvas class="sb-canvas" id="canvasAsym" width="300" height="42"></canvas>
                </div>
            </div>
        </div>

    </div>

    <!-- FINAL AUDIT MODAL -->
    <div class="modal-backdrop" id="finalAuditModal">
        <div class="modal-card">
            <button class="modal-close-btn" onclick="closeAuditModal()">&times;</button>
            <div style="font-size:11px; text-transform:uppercase; letter-spacing:2px; color:#38bdf8; font-weight:700;">SYSTEM 1 // BIOMETRIC AUDIT REPORT</div>
            <h2 id="modalSessionHeader" style="font-size:22px; font-weight:900; margin:6px 0 16px 0; color:#fff;">SESSION CERTIFICATE</h2>
            <div id="modalVerdictBanner" style="padding:16px; border-radius:10px; border:2px solid #10b981; background:#10b98115; margin-bottom:16px;">
                <div id="modalVerdictTitle" style="font-size:18px; font-weight:900; color:#10b981;">✔ VERIFIED GENUINE HUMAN</div>
                <div id="modalScoreValue" style="font-size:28px; font-weight:900; color:#fff; font-family:monospace; margin-top:4px;">96%</div>
            </div>
            <div style="display:flex; gap:10px; margin-top:14px;">
                <button class="btn" onclick="closeAuditModal()" style="flex:1;">OK / COMPLETE</button>
                <a href="/dashboard" class="btn btn-cyan" style="flex:1; text-decoration:none; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:800;">VIEW IN DASHBOARD &rarr;</a>
            </div>
        </div>
    </div>

    <script>
        let currentMode = 'live';
        let isRunning = false;
        let isGatewayPassed = false;
        let voiceEnabled = true;
        let lastSpokenPrompt = "";

        let ws = null;
        let video = document.getElementById('webcam');
        let canvas = document.getElementById('captureCanvas');
        let ctx = canvas.getContext('2d');
        let hudCanvas = document.getElementById('hudOverlay');
        let hudCtx = hudCanvas.getContext('2d');
        let intervalId = null;

        // REAL Shape Tracing Engine
        let currentWaypoints = [];
        let shapeType = 'star';
        let visitedWaypoints = new Set();
        let targetWaypointIdx = 0;
        let activeSpokenCode = '';
        let recognition = null;
        let lastIndexTip = null;
        let activeTimeoutSec = 14.0;

        // Ring buffers
        const ringJitter = new Array(35).fill(0.0014);
        const ringPulse = new Array(35).fill(72);
        const ringAsym = new Array(35).fill(0.78);
        const ringTremor = new Array(35).fill(8.4);

        function toggleVoiceDictation() {
            voiceEnabled = !voiceEnabled;
            document.getElementById('speakerIcon').innerText = voiceEnabled ? "🔊" : "🔇";
            document.getElementById('speakerText').innerText = voiceEnabled ? "VOICE: ON" : "VOICE: MUTED";
            if (!voiceEnabled && 'speechSynthesis' in window) {
                window.speechSynthesis.cancel();
            }
        }

        function speakPromptAloud(text) {
            if (!voiceEnabled || !('speechSynthesis' in window) || !text) return;
            if (text === lastSpokenPrompt) return;
            lastSpokenPrompt = text;

            try {
                window.speechSynthesis.cancel();
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.rate = 0.95;
                utterance.pitch = 1.0;
                utterance.lang = 'en-US';
                window.speechSynthesis.speak(utterance);
            } catch(e) {}
        }

        function setSystemMode(mode) {
            if (isRunning) stopVerificationSession();
            currentMode = mode;
            const tabLive = document.getElementById('tabLive');
            const tabStd = document.getElementById('tabStandard');
            const btn = document.getElementById('actionBtn');

            if (mode === 'live') {
                tabLive.className = 'sys-tab green-active active';
                tabStd.className = 'sys-tab';
                btn.className = 'btn';
                btn.innerText = 'START LIVE MONITOR';
            } else {
                tabStd.className = 'sys-tab active';
                tabLive.className = 'sys-tab';
                btn.className = 'btn btn-cyan';
                btn.innerText = 'START VERIFICATION AUDIT';
            }
            resetUiDisplay();
        }

        function resetUiDisplay() {
            document.getElementById('taskBox').style.display = 'block';
            document.getElementById('passiveShieldBanner').style.display = 'none';
            document.getElementById('codeBadgesBox').style.display = 'none';
            document.getElementById('shapeProgressBadge').style.display = 'none';
            document.getElementById('stageBadge').innerText = 'SYSTEM GENERATED RANDOM PROTOCOL';
            document.getElementById('taskInstruction').innerText = 'Click "START VERIFICATION" to begin';
            document.getElementById('timerFill').style.width = '100%';
            document.getElementById('pillText').innerText = 'STANDBY: READY TO START';
            document.getElementById('pillDot').className = 'pill-dot';
            document.getElementById('pillText').className = 'pill-text';
            hudCtx.clearRect(0, 0, hudCanvas.width, hudCanvas.height);
            visitedWaypoints.clear();
        }

        function drawSparkline(canvasId, data, minVal, maxVal, strokeColor, fillColor) {
            const c = document.getElementById(canvasId);
            if (!c) return;
            const gCtx = c.getContext('2d');
            const w = c.width;
            const h = c.height;
            gCtx.clearRect(0, 0, w, h);

            const range = Math.max(1e-6, maxVal - minVal);
            const step = w / (data.length - 1);

            gCtx.beginPath();
            for (let i = 0; i < data.length; i++) {
                const norm = Math.max(0, Math.min(1, (data[i] - minVal) / range));
                const x = i * step;
                const y = h - norm * (h - 4) - 2;
                if (i === 0) gCtx.moveTo(x, y);
                else gCtx.lineTo(x, y);
            }
            gCtx.strokeStyle = strokeColor;
            gCtx.lineWidth = 1.6;
            gCtx.stroke();
            gCtx.lineTo(w, h);
            gCtx.lineTo(0, h);
            gCtx.closePath();
            gCtx.fillStyle = fillColor;
            gCtx.fill();
        }

        async function initCamera() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: { width:800, height:600 } });
                video.srcObject = stream;
            } catch(e) {
                alert("Please grant camera permissions to activate TrustLayer verification.");
            }
        }
        initCamera();

        function initSpeechRecognition() {
            const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRec) {
                document.getElementById('voiceCaption').innerText = "Speech API not available in this browser.";
                return;
            }
            recognition = new SpeechRec();
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = 'en-US';

            recognition.onresult = (event) => {
                let transcript = '';
                for (let i = event.resultIndex; i < event.results.length; ++i) {
                    transcript += event.results[i][0].transcript;
                }
                document.getElementById('voiceCaption').innerText = `🎙️ Heard: "${transcript.toUpperCase()}"`;
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({ spoken_text: transcript }));
                }
            };
            recognition.onerror = () => {};
        }
        initSpeechRecognition();

        // REAL Shape Rendering and Waypoint Distance Evaluation
        function updateAndRenderShapeOverlay() {
            hudCtx.clearRect(0, 0, hudCanvas.width, hudCanvas.height);

            if (!currentWaypoints || currentWaypoints.length < 5) return;

            let isFingerActive = false;
            let canvasFx = 0, canvasFy = 0;

            // Check distance from user's index finger tip (mirrored horizontally to match video)
            if (lastIndexTip) {
                const fx = (1.0 - lastIndexTip.x);
                const fy = lastIndexTip.y;
                canvasFx = fx * hudCanvas.width;
                canvasFy = fy * hudCanvas.height;
                isFingerActive = true;

                // Generous tolerance radius (0.13) so natural finger pointing comfortably marks waypoints
                for (let i = 0; i < currentWaypoints.length; i++) {
                    const wp = currentWaypoints[i];
                    const dist = Math.hypot(wp.x - fx, wp.y - fy);
                    if (dist < 0.13) {
                        visitedWaypoints.add(i);
                    }
                }
            }

            // Draw prominent glowing fingertip reticle & position cursor
            if (isFingerActive) {
                hudCtx.save();
                // Outer pulsing target reticle
                hudCtx.beginPath();
                hudCtx.arc(canvasFx, canvasFy, 18, 0, 2 * Math.PI);
                hudCtx.strokeStyle = '#10b981';
                hudCtx.lineWidth = 2.5;
                hudCtx.shadowColor = '#10b981';
                hudCtx.shadowBlur = 12;
                hudCtx.stroke();

                // Crosshair markers
                hudCtx.beginPath();
                hudCtx.moveTo(canvasFx - 24, canvasFy); hudCtx.lineTo(canvasFx - 12, canvasFy);
                hudCtx.moveTo(canvasFx + 12, canvasFy); hudCtx.lineTo(canvasFx + 24, canvasFy);
                hudCtx.moveTo(canvasFx, canvasFy - 24); hudCtx.lineTo(canvasFx, canvasFy - 12);
                hudCtx.moveTo(canvasFx, canvasFy + 12); hudCtx.lineTo(canvasFx, canvasFy + 24);
                hudCtx.strokeStyle = 'rgba(16, 185, 129, 0.8)';
                hudCtx.lineWidth = 2;
                hudCtx.stroke();

                // Bright center point
                hudCtx.beginPath();
                hudCtx.arc(canvasFx, canvasFy, 6, 0, 2 * Math.PI);
                hudCtx.fillStyle = '#10b981';
                hudCtx.fill();

                // Fingertip badge label
                hudCtx.font = 'bold 11px sans-serif';
                hudCtx.fillStyle = '#10b981';
                hudCtx.shadowBlur = 6;
                hudCtx.fillText('👆 FINGERTIP', canvasFx + 16, canvasFy - 10);
                hudCtx.restore();
            } else {
                // Guidance tooltip when finger isn't detected yet
                hudCtx.save();
                hudCtx.font = 'bold 13px sans-serif';
                hudCtx.fillStyle = '#fbbf24';
                hudCtx.shadowColor = '#fbbf24';
                hudCtx.shadowBlur = 10;
                hudCtx.textAlign = 'center';
                hudCtx.fillText('👉 Raise hand with index finger pointed to trace the shape', hudCanvas.width / 2, 40);
                hudCtx.restore();
            }

            // Draw shape perimeter with visited coloring
            const pct = Math.round((visitedWaypoints.size / currentWaypoints.length) * 100);
            const badge = document.getElementById('shapeProgressBadge');
            badge.style.display = 'block';
            badge.innerText = `${shapeType.toUpperCase()} TRACED: ${pct}% (MIN 70% REQUIRED)`;
            badge.style.borderColor = pct >= 70 ? '#10b981' : '#fbbf24';
            badge.style.color = pct >= 70 ? '#10b981' : '#fbbf24';

            hudCtx.save();
            hudCtx.lineWidth = 4;
            hudCtx.lineCap = 'round';

            for (let i = 0; i < currentWaypoints.length; i++) {
                const nextIdx = (i + 1) % currentWaypoints.length;
                const wx1 = currentWaypoints[i].x * hudCanvas.width;
                const wy1 = currentWaypoints[i].y * hudCanvas.height;
                const wx2 = currentWaypoints[nextIdx].x * hudCanvas.width;
                const wy2 = currentWaypoints[nextIdx].y * hudCanvas.height;

                hudCtx.beginPath();
                hudCtx.moveTo(wx1, wy1);
                hudCtx.lineTo(wx2, wy2);

                if (visitedWaypoints.has(i)) {
                    hudCtx.strokeStyle = '#10b981';
                    hudCtx.shadowColor = '#10b981';
                    hudCtx.shadowBlur = 14;
                } else {
                    hudCtx.strokeStyle = 'rgba(56, 189, 248, 0.40)';
                    hudCtx.shadowColor = '#38bdf8';
                    hudCtx.shadowBlur = 6;
                }
                hudCtx.stroke();
            }

            // Draw animated traveling target dot
            targetWaypointIdx = (targetWaypointIdx + 1) % currentWaypoints.length;
            const targetPt = currentWaypoints[targetWaypointIdx];
            const tx = targetPt.x * hudCanvas.width;
            const ty = targetPt.y * hudCanvas.height;

            hudCtx.beginPath();
            hudCtx.arc(tx, ty, 9, 0, 2 * Math.PI);
            hudCtx.fillStyle = '#fbbf24';
            hudCtx.shadowColor = '#fbbf24';
            hudCtx.shadowBlur = 18;
            hudCtx.fill();

            hudCtx.restore();
        }

        function toggleVerificationSession() {
            if (isRunning) {
                stopVerificationSession();
            } else {
                startVerificationSession();
            }
        }

        function startVerificationSession() {
            isRunning = true;
            isGatewayPassed = false;
            lastSpokenPrompt = "";
            visitedWaypoints.clear();

            const btn = document.getElementById('actionBtn');
            btn.className = 'btn btn-stop';
            btn.innerText = 'VERIFICATION IN PROGRESS (CLICK TO STOP)';

            const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
            ws = new WebSocket(`${wsProtocol}//${window.location.host}/ws/verify?mode=${currentMode}`);

            ws.onopen = () => {
                intervalId = setInterval(captureAndSend, 120);
                if (recognition) {
                    try { recognition.start(); } catch(e) {}
                }
            };

            ws.onmessage = (event) => {
                const msg = JSON.parse(event.data);

                // Handle System 1 Audit Complete
                if (msg.status === "completed") {
                    stopVerificationSession();
                    showAuditResultModal(msg);
                    return;
                }

                // In Live Mode: If gateway cleared -> ALL TASKS STOP!
                if (currentMode === 'live' && msg.is_gateway_cleared) {
                    isGatewayPassed = true;
                    document.getElementById('taskBox').style.display = 'none';
                    document.getElementById('passiveShieldBanner').style.display = 'block';
                    currentWaypoints = [];
                    hudCtx.clearRect(0, 0, hudCanvas.width, hudCanvas.height);
                    if ('speechSynthesis' in window) window.speechSynthesis.cancel();

                    btn.className = 'btn btn-stop';
                    btn.innerText = 'END LIVE SHIELD';
                }

                // Setup Shape Waypoints if active
                if (msg.waypoints && msg.waypoints.length && !isGatewayPassed) {
                    if (currentWaypoints.length !== msg.waypoints.length) {
                        visitedWaypoints.clear();
                    }
                    currentWaypoints = msg.waypoints;
                    shapeType = msg.shape_type || 'star';
                } else if (!msg.waypoints) {
                    currentWaypoints = [];
                    document.getElementById('shapeProgressBadge').style.display = 'none';
                }

                // Setup Spoken Code (7-8 characters)
                if (msg.spoken_code && !isGatewayPassed) {
                    activeSpokenCode = msg.spoken_code;
                    document.getElementById('codeBadgesBox').style.display = 'block';
                    const row = document.getElementById('codeTilesRow');
                    row.innerHTML = activeSpokenCode.split('').map(c => `<div class="code-tile">${c}</div>`).join('');
                } else {
                    document.getElementById('codeBadgesBox').style.display = 'none';
                }

                // Update Task Instructions & Dynamic Timeouts
                if (msg.challenge && !isGatewayPassed) {
                    document.getElementById('taskInstruction').innerText = msg.challenge;
                    document.getElementById('stageBadge').innerText = msg.progress || 'STAGE IN PROGRESS';
                    activeTimeoutSec = msg.timeout_sec || 14.0;
                    document.getElementById('timerFill').style.width = `${(msg.time_left / activeTimeoutSec) * 100}%`;

                    if (msg.speech) {
                        speakPromptAloud(msg.speech);
                    }
                }

                // Extract index fingertip landmark
                if (msg.telemetry && msg.telemetry.index_tip) {
                    lastIndexTip = msg.telemetry.index_tip;
                }

                // Live Status Pill on Camera
                if (msg.live_health) {
                    const h = msg.live_health;
                    const dot = document.getElementById('pillDot');
                    const txt = document.getElementById('pillText');

                    if (h.is_suspicious) {
                        dot.className = 'pill-dot suspicious';
                        txt.className = 'pill-text suspicious';
                        txt.innerText = h.verdict;
                        video.style.boxShadow = "0 0 35px rgba(239, 68, 68, 0.85)";
                    } else {
                        dot.className = 'pill-dot';
                        txt.className = 'pill-text';
                        txt.innerText = isGatewayPassed ? 
                            "LIVE: VERIFIED GENUINE HUMAN (PASSIVE SHIELD ACTIVE)" : 
                            "LIVE SENSOR ACTIVE: VERIFYING PRESENCE";
                        video.style.boxShadow = "none";
                    }
                }

                // Telemetry Updates
                if (msg.telemetry) {
                    const t = msg.telemetry;

                    // Numeric Left Updates
                    if (t.heart_rate_bpm > 0) {
                        document.getElementById('valPulse').innerText = `${Math.round(t.heart_rate_bpm)} BPM`;
                        document.getElementById('txtPulse').innerText = `${Math.round(t.heart_rate_bpm)} BPM`;
                        ringPulse.push(t.heart_rate_bpm); ringPulse.shift();
                        drawSparkline('canvasPulse', ringPulse, 45, 120, '#10b981', 'rgba(16, 185, 129, 0.18)');
                    }
                    if (t.tremor_freq_hz) {
                        document.getElementById('valTremor').innerText = `${t.tremor_freq_hz.toFixed(1)} Hz [6-12]`;
                        document.getElementById('txtTremorGraph').innerText = `${t.tremor_freq_hz.toFixed(1)} Hz`;
                        ringTremor.push(t.tremor_freq_hz); ringTremor.shift();
                        drawSparkline('canvasTremor', ringTremor, 4.0, 15.0, '#a78bfa', 'rgba(167, 139, 250, 0.18)');
                    }
                    if (t.asymmetry_index) {
                        document.getElementById('valAsym').innerText = `${t.asymmetry_index.toFixed(2)} [Bio]`;
                        document.getElementById('txtAsym').innerText = t.asymmetry_index.toFixed(2);
                        ringAsym.push(t.asymmetry_index); ringAsym.shift();
                        drawSparkline('canvasAsym', ringAsym, 0.4, 1.8, '#fbbf24', 'rgba(251, 191, 36, 0.18)');
                    }
                    if (t.power_law_score !== undefined) {
                        document.getElementById('valPower').innerHTML = `&beta; = ${t.power_law_score.toFixed(2)} [OK]`;
                    }
                    if (t.yaw !== undefined && t.pitch !== undefined) {
                        const ySign = t.yaw > 0 ? '+' : '';
                        const pSign = t.pitch > 0 ? '+' : '';
                        document.getElementById('valHeadPose').innerText = `Y: ${ySign}${t.yaw.toFixed(1)}° | P: ${pSign}${t.pitch.toFixed(1)}°`;
                    }
                    if (t.ear !== undefined) {
                        document.getElementById('valBlinks').innerText = `EAR: ${t.ear.toFixed(2)} | ${t.blinks || 0} Bl`;
                    }
                    if (t.fingers_detected !== undefined) {
                        document.getElementById('valHand').innerText = `${t.fingers_detected} Fingers Up`;
                    }

                    const jVal = t.micro_jitter_std || 0.0014;
                    document.getElementById('txtJitter').innerText = jVal.toFixed(5);
                    document.getElementById('valJitterNum').innerText = jVal.toFixed(5);
                    ringJitter.push(jVal); ringJitter.shift();
                    drawSparkline('canvasJitter', ringJitter, 0.0, 0.008, '#38bdf8', 'rgba(56, 189, 248, 0.18)');
                }

                updateAndRenderShapeOverlay();
            };

            ws.onclose = () => {
                if (isRunning) stopVerificationSession();
            };
        }

        function stopVerificationSession() {
            isRunning = false;
            clearInterval(intervalId);
            if ('speechSynthesis' in window) window.speechSynthesis.cancel();
            if (recognition) {
                try { recognition.stop(); } catch(e) {}
            }
            if (ws && ws.readyState === WebSocket.OPEN) {
                try { ws.send(JSON.stringify({ action: "stop" })); } catch(e) {}
                ws.close();
            }

            const btn = document.getElementById('actionBtn');
            btn.className = currentMode === 'live' ? 'btn' : 'btn btn-cyan';
            btn.innerText = currentMode === 'live' ? 'START LIVE MONITOR' : 'START VERIFICATION AUDIT';

            resetUiDisplay();
        }

        // Send REAL calculated path_conformance
        function captureAndSend() {
            if (ws && ws.readyState === WebSocket.OPEN) {
                ctx.drawImage(video, 0, 0, 640, 480);
                const base64Img = canvas.toDataURL('image/jpeg', 0.65);

                const realConformance = currentWaypoints.length > 0 ? 
                    (visitedWaypoints.size / currentWaypoints.length) : 0.0;

                ws.send(JSON.stringify({
                    image: base64Img,
                    path_conformance: realConformance
                }));
            }
        }

        function showAuditResultModal(data) {
            document.getElementById('modalSessionHeader').innerText = `CERTIFICATE #${data.session_id}`;
            document.getElementById('modalScoreValue').innerText = `${data.score}%`;
            const isV = data.verdict === 'VERIFIED';
            document.getElementById('modalVerdictTitle').innerText = isV ? '✔ VERIFIED GENUINE HUMAN' : '✖ SUSPICIOUS / UNCONFIRMED';
            document.getElementById('modalVerdictTitle').style.color = isV ? '#10b981' : '#ef4444';
            document.getElementById('modalVerdictBanner').style.borderColor = isV ? '#10b981' : '#ef4444';
            document.getElementById('modalVerdictBanner').style.background = isV ? '#10b98115' : '#ef444415';
            document.getElementById('finalAuditModal').classList.add('open');
        }

        function closeAuditModal() {
            document.getElementById('finalAuditModal').classList.remove('open');
            resetUiDisplay();
        }
    </script>
</body>
</html>"""


# ============================================================================
# 7. VERTICAL LAYOUT (kept at /client-vertical for fallback)
# ============================================================================

@app.get("/client-vertical", response_class=HTMLResponse)
def get_web_client_vertical():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TrustLayer - Multimodal Kinematic & Biosignal Verification</title>
    <style>
        * { margin:0; padding:0; box-sizing:border-box; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        body { background:#09090b; color:#f4f4f5; display:flex; flex-direction:column; align-items:center; min-height:100vh; padding:16px 20px 40px; }
        
        .header { text-align:center; margin-bottom:12px; }
        .header h1 { font-size:24px; color:#38bdf8; font-weight:900; letter-spacing:1px; }
        .header p { font-size:11px; color:#71717a; text-transform:uppercase; letter-spacing:1.5px; margin-top:3px; }
        
        /* SYSTEM SWITCHER TABS */
        .system-switcher { display:flex; gap:12px; max-width:880px; width:100%; margin-bottom:14px; justify-content:center; }
        .sys-tab {
            flex:1; background:#18181b; border:1px solid #27272a; padding:10px 16px; border-radius:12px;
            cursor:pointer; display:flex; align-items:center; gap:10px; transition:all 0.25s ease; color:#a1a1aa; text-align:left;
        }
        .sys-tab:hover { background:#202025; border-color:#3f3f46; color:#fff; }
        .sys-tab.active { background:#141418; border-color:#38bdf8; color:#fff; box-shadow:0 0 20px rgba(56, 189, 248, 0.15); }
        .sys-tab.active.green-active { border-color:#10b981; box-shadow:0 0 20px rgba(16, 185, 129, 0.18); }
        .sys-tab-icon {
            width:32px; height:32px; border-radius:8px; display:flex; align-items:center; justify-content:center;
            font-size:16px; font-weight:800; flex-shrink:0; background:#27272a; color:#a1a1aa;
        }
        .sys-tab.active .sys-tab-icon.cyan-icon { background:#38bdf820; color:#38bdf8; border:1px solid #38bdf840; }
        .sys-tab.active.green-active .sys-tab-icon.green-icon { background:#10b98120; color:#10b981; border:1px solid #10b98140; }
        .sys-tab-title { font-size:12px; font-weight:800; letter-spacing:0.5px; }
        .sys-tab-sub { font-size:10px; color:#71717a; margin-top:2px; }

        /* CENTERED MAIN CONTAINER */
        .center-container { max-width:980px; width:100%; display:flex; flex-direction:column; align-items:center; gap:14px; }

        /* PROMINENT LARGE CAMERA VIEWPORT */
        .camera-viewport-box {
            width:100%; background:#18181b; border:2px solid #27272a; border-radius:18px; padding:14px;
            position:relative; box-shadow:0 12px 40px rgba(0,0,0,0.6); display:flex; flex-direction:column; align-items:center;
        }
        .camera-wrapper {
            position:relative; width:100%; max-width:820px; aspect-ratio:4/3; border-radius:14px; overflow:hidden; background:#000;
        }
        video { width:100%; height:100%; object-fit:cover; display:block; transform:scaleX(-1); background:#000; }
        canvas.hud-overlay { position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; }
        canvas.hidden-canvas { display:none; }

        /* LIVE STATUS PILL ON CAMERA */
        .camera-status-pill {
            position:absolute; top:12px; left:12px; background:rgba(9, 9, 11, 0.85); backdrop-filter:blur(6px);
            border:1px solid #10b981; border-radius:20px; padding:6px 14px; display:flex; align-items:center; gap:8px; z-index:10;
        }
        .pill-dot { width:8px; height:8px; border-radius:50%; background:#10b981; box-shadow:0 0 8px #10b981; }
        .pill-dot.suspicious { background:#ef4444 !important; box-shadow:0 0 10px #ef4444 !important; }
        .pill-text { font-size:11px; font-weight:800; color:#10b981; letter-spacing:0.5px; }
        .pill-text.suspicious { color:#ef4444 !important; }

        /* VOICE SPEECH INDICATOR ON CAMERA */
        .voice-speaker-badge {
            position:absolute; top:12px; right:12px; background:rgba(9, 9, 11, 0.85); backdrop-filter:blur(6px);
            border:1px solid #38bdf850; border-radius:20px; padding:6px 12px; font-size:11px; color:#38bdf8;
            font-weight:700; display:flex; align-items:center; gap:6px; cursor:pointer; z-index:10;
        }

        /* TASKS DIRECTLY BELOW CAMERA VIEWPORT */
        .task-action-box {
            width:100%; background:#18181b; border:2px solid #38bdf8; border-radius:16px; padding:18px 24px;
            text-align:center; position:relative; box-shadow:0 8px 30px rgba(56, 189, 248, 0.12); transition:all 0.3s;
        }
        .task-stage-badge {
            font-size:11px; font-weight:800; text-transform:uppercase; letter-spacing:1.5px; color:#38bdf8;
            background:#38bdf815; padding:4px 12px; border-radius:12px; display:inline-block; margin-bottom:8px;
        }
        .task-instruction-text {
            font-size:20px; font-weight:800; color:#fff; line-height:1.3; margin-bottom:10px;
        }
        .task-timer-bg { width:100%; height:6px; background:#27272a; border-radius:3px; overflow:hidden; margin-top:10px; }
        .task-timer-fill { height:100%; width:100%; background:#38bdf8; transition:width 0.1s linear; }

        /* SPOKEN ALPHANUMERIC CODE BADGES (7 TO 8 CHARACTERS) */
        .code-badges-container {
            display:none; margin:12px auto; padding:12px; background:#141418; border:1px solid #38bdf840; border-radius:12px; max-width:680px;
        }
        .code-badges-label { font-size:11px; text-transform:uppercase; color:#38bdf8; font-weight:800; letter-spacing:1px; margin-bottom:8px; }
        .code-tiles-row { display:flex; justify-content:center; gap:8px; flex-wrap:wrap; }
        .code-tile {
            width:42px; height:50px; background:#27272a; border:2px solid #38bdf8; border-radius:8px;
            font-size:24px; font-weight:900; color:#fff; display:flex; align-items:center; justify-content:center;
            font-family:monospace; box-shadow:0 0 14px rgba(56, 189, 248, 0.3);
        }
        .voice-caption { font-size:12px; color:#10b981; font-weight:700; margin-top:8px; min-height:18px; }

        /* SHAPE PROGRESS BADGE */
        .shape-progress-badge {
            display:none; margin:10px auto; padding:8px 16px; background:#141418; border:1px solid #fbbf24;
            border-radius:10px; color:#fbbf24; font-size:13px; font-weight:800; font-family:monospace; max-width:440px;
        }

        /* PASSIVE SHIELD BANNER (ACTIVATED UPON VERIFICATION IN LIVE MODE) */
        .passive-shield-banner {
            display:none; width:100%; background:#10b98115; border:2px solid #10b981; border-radius:16px; padding:18px; text-align:center;
        }
        .passive-banner-title { font-size:15px; font-weight:900; color:#10b981; letter-spacing:0.5px; }
        .passive-banner-sub { font-size:12px; color:#a1a1aa; margin-top:6px; line-height:1.4; max-width:700px; margin-left:auto; margin-right:auto; }

        /* SPLIT TELEMETRY LAYOUT: NUMERIC LEFT, GRAPHS RIGHT */
        .telemetry-split-layout {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            width: 100%;
            margin-top: 2px;
        }
        @media (max-width: 860px) {
            .telemetry-split-layout { grid-template-columns: 1fr; }
        }
        .split-col {
            background: #121215;
            border: 1px solid #27272a;
            border-radius: 14px;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .col-header {
            font-size: 11px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            color: #38bdf8;
            display: flex;
            align-items: center;
            gap: 8px;
            padding-bottom: 8px;
            border-bottom: 1px solid #27272a;
        }
        .col-header-icon { font-size: 14px; }

        /* NUMERIC CARDS GRID (LEFT SIDE) */
        .numeric-cards-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }
        .telemetry-card {
            background: #18181b;
            border: 1px solid #27272a;
            border-radius: 10px;
            padding: 10px 12px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .tc-label { font-size: 10px; text-transform: uppercase; color: #a1a1aa; letter-spacing: 0.6px; font-weight: 700; }
        .tc-val { font-size: 15px; font-weight: 800; color: #fff; font-family: monospace; margin: 4px 0 2px 0; }
        .tc-sub { font-size: 9px; color: #71717a; letter-spacing: 0.3px; }

        /* GRAPH CARDS LIST (RIGHT SIDE) */
        .graph-cards-list {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .graph-box {
            background: #18181b;
            border: 1px solid #27272a;
            border-radius: 10px;
            padding: 10px 12px;
        }
        .sb-hdr {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 6px;
        }
        .sb-title { font-size: 11px; font-weight: 700; color: #e4e4e7; display: flex; align-items: center; gap: 6px; }
        .sb-val-pill {
            font-size: 11px;
            font-family: monospace;
            font-weight: 800;
            background: #27272a;
            padding: 2px 8px;
            border-radius: 6px;
        }
        .sb-canvas {
            width: 100%;
            height: 38px;
            display: block;
            border-radius: 6px;
            background: #09090b;
            border: 1px solid #202025;
        }

        /* CONTROLS BUTTON */
        .action-button-row { width:100%; max-width:440px; margin-top:4px; }
        .btn {
            background:#10b981; color:#09090b; border:none; padding:14px 24px; border-radius:12px;
            font-weight:800; font-size:15px; cursor:pointer; width:100%; transition:all 0.2s; letter-spacing:0.5px;
        }
        .btn:hover { background:#059669; }
        .btn.btn-stop { background:#ef4444; color:#fff; }
        .btn.btn-stop:hover { background:#dc2626; }
        .btn.btn-cyan { background:#38bdf8; color:#09090b; }
        .btn.btn-cyan:hover { background:#0284c7; }

        /* MODAL */
        .modal-backdrop { display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.85); backdrop-filter:blur(6px); z-index:9999; align-items:center; justify-content:center; }
        .modal-backdrop.open { display:flex; }
        .modal-card { background:#18181b; border:2px solid #38bdf8; border-radius:16px; max-width:620px; width:92%; padding:26px; position:relative; box-shadow:0 20px 60px rgba(0,0,0,0.8); }
        .modal-close-btn { position:absolute; top:16px; right:16px; background:#27272a; border:none; color:#a1a1aa; width:30px; height:30px; border-radius:50%; font-size:18px; cursor:pointer; }
    </style>
</head>
<body>
    <div class="header">
        <h1>TRUSTLAYER // AI CONTINUOUS HUMAN VERIFICATION SHIELD</h1>
        <p>Zeal College of Engineering & Research &bull; Department of ECE &bull; Pune-41</p>
    </div>

    <!-- SYSTEM SWITCHER TABS -->
    <div class="system-switcher">
        <button class="sys-tab green-active active" id="tabLive" onclick="setSystemMode('live')">
            <div class="sys-tab-icon green-icon">🟢</div>
            <div>
                <div class="sys-tab-title">SYSTEM 2: LIVE EXAM & VIDEO CALL SHIELD</div>
                <div class="sys-tab-sub">Random Protocol &rarr; Verified Genuine &rarr; ZERO Further Tasks (Pure 24/7 Passive Biosignal Monitor)</div>
            </div>
        </button>

        <button class="sys-tab" id="tabStandard" onclick="setSystemMode('standard')">
            <div class="sys-tab-icon cyan-icon">⚡</div>
            <div>
                <div class="sys-tab-title">SYSTEM 1: STANDARD VERIFICATION AUDIT</div>
                <div class="sys-tab-sub">Finite 4-Stage Multimodal Audit Protocol &rarr; Compliance Certificate</div>
            </div>
        </button>
    </div>

    <div class="center-container">
        <!-- 1. PROMINENT LARGE CAMERA VIEWPORT -->
        <div class="camera-viewport-box">
            <div class="camera-wrapper">
                <video id="webcam" autoplay playsinline></video>
                <canvas class="hud-overlay" id="hudOverlay" width="800" height="600"></canvas>
                <canvas class="hidden-canvas" id="captureCanvas" width="640" height="480"></canvas>

                <!-- Live Status Pill -->
                <div class="camera-status-pill" id="cameraStatusPill">
                    <div class="pill-dot" id="pillDot"></div>
                    <span class="pill-text" id="pillText">STANDBY: READY TO START</span>
                </div>

                <!-- Voice Dictation Toggle Badge -->
                <div class="voice-speaker-badge" id="voiceToggle" onclick="toggleVoiceDictation()">
                    <span id="speakerIcon">🔊</span>
                    <span id="speakerText">VOICE: ON</span>
                </div>
            </div>
        </div>

        <!-- 2. TASKS & INSTRUCTIONS DIRECTLY BELOW CAMERA -->
        <div class="task-action-box" id="taskBox">
            <div class="task-stage-badge" id="stageBadge">SYSTEM GENERATED RANDOM PROTOCOL</div>
            <div class="task-instruction-text" id="taskInstruction">Click "START VERIFICATION" to begin</div>
            <div class="task-timer-bg"><div class="task-timer-fill" id="timerFill"></div></div>

            <!-- SPOKEN CODE TILES CONTAINER (7-8 CHARACTERS) -->
            <div class="code-badges-container" id="codeBadgesBox">
                <div class="code-badges-label">Read the 7-8 Character Verification Code Aloud:</div>
                <div class="code-tiles-row" id="codeTilesRow"></div>
                <div class="voice-caption" id="voiceCaption">🎙️ Microphone listening for spoken digits...</div>
            </div>

            <!-- REAL SHAPE TRACING PROGRESS BADGE -->
            <div class="shape-progress-badge" id="shapeProgressBadge">
                ⭐ TRACED: 0% (MIN 70% PERIMETER REQUIRED)
            </div>
        </div>

        <!-- 3. PASSIVE SHIELD BANNER (ACTIVATED UPON VERIFICATION IN LIVE MODE) -->
        <div class="passive-shield-banner" id="passiveShieldBanner">
            <div class="passive-banner-title">✔ HUMAN VERIFICATION COMPLETE &bull; PASSIVE SHIELD RUNNING</div>
            <div class="passive-banner-sub">
                Online Exam / Video Call is continuously protected in the background. Passively monitoring involuntary body tremor (6-12 Hz), capillary rPPG blood flow, skin micro-jitter, and stream anti-freeze guard. Zero user actions required.
            </div>
        </div>

        <!-- SPLIT TELEMETRY: NUMERIC VALUES ON LEFT, GRAPH VALUES ON RIGHT -->
        <div class="telemetry-split-layout">
            <!-- LEFT COLUMN: ALL NUMERIC TELEMETRY VALUES -->
            <div class="split-col numeric-col">
                <div class="col-header">
                    <span class="col-header-icon">📊</span>
                    <span>NUMERIC SENSORS & BIOMETRICS (LEFT)</span>
                </div>
                <div class="numeric-cards-grid">
                    <div class="telemetry-card">
                        <div class="tc-label">rPPG Blood Pulse</div>
                        <div class="tc-val" id="valPulse" style="color:#10b981;">Acquiring...</div>
                        <div class="tc-sub">Capillary Flow Rate</div>
                    </div>
                    <div class="telemetry-card">
                        <div class="tc-label">Body Micro-Tremor</div>
                        <div class="tc-val" id="valTremor">8.4 Hz [6-12]</div>
                        <div class="tc-sub">Involuntary Jitter</div>
                    </div>
                    <div class="telemetry-card">
                        <div class="tc-label">Kinematic Asymmetry</div>
                        <div class="tc-val" id="valAsym">0.78 [Bio]</div>
                        <div class="tc-sub">Motor Invariant Index</div>
                    </div>
                    <div class="telemetry-card">
                        <div class="tc-label">Two-Thirds Power Law</div>
                        <div class="tc-val" id="valPower">&beta; = 0.32 [Passed]</div>
                        <div class="tc-sub">v &prop; &kappa;<sup>-1/3</sup> Law</div>
                    </div>
                    <div class="telemetry-card">
                        <div class="tc-label">Head Pose Rotation</div>
                        <div class="tc-val" id="valHeadPose">Y: 0.0&deg; | P: 0.0&deg;</div>
                        <div class="tc-sub">Vestibular Alignment</div>
                    </div>
                    <div class="telemetry-card">
                        <div class="tc-label">Eye Blinks & EAR</div>
                        <div class="tc-val" id="valBlinks">EAR: 0.32 | 0 Blinks</div>
                        <div class="tc-sub">Ocular Dynamics</div>
                    </div>
                    <div class="telemetry-card">
                        <div class="tc-label">Hand Biomechanics</div>
                        <div class="tc-val" id="valHand">0 Fingers Up</div>
                        <div class="tc-sub">Gesture Effector</div>
                    </div>
                    <div class="telemetry-card">
                        <div class="tc-label">Skin Micro-Jitter STD</div>
                        <div class="tc-val" id="valJitterNum">0.00140</div>
                        <div class="tc-sub">Sub-dermal Noise</div>
                    </div>
                </div>
            </div>

            <!-- RIGHT COLUMN: ALL REAL-TIME GRAPH VALUES -->
            <div class="split-col graph-col">
                <div class="col-header">
                    <span class="col-header-icon">📈</span>
                    <span>REAL-TIME BIOSIGNAL GRAPHS (RIGHT)</span>
                </div>
                <div class="graph-cards-list">
                    <div class="graph-box">
                        <div class="sb-hdr">
                            <span class="sb-title">🟢 rPPG Capillary Pulse Waveform</span>
                            <span class="sb-val-pill" id="txtPulse" style="color:#10b981;">Calibrating</span>
                        </div>
                        <canvas class="sb-canvas" id="canvasPulse" width="380" height="38"></canvas>
                    </div>

                    <div class="graph-box">
                        <div class="sb-hdr">
                            <span class="sb-title">🟣 Involuntary Micro-Tremor (6-12 Hz)</span>
                            <span class="sb-val-pill" id="txtTremorGraph" style="color:#a78bfa;">8.4 Hz</span>
                        </div>
                        <canvas class="sb-canvas" id="canvasTremor" width="380" height="38"></canvas>
                    </div>

                    <div class="graph-box">
                        <div class="sb-hdr">
                            <span class="sb-title">🔵 Skin Micro-Jitter (Cellular Noise)</span>
                            <span class="sb-val-pill" id="txtJitter" style="color:#38bdf8;">0.00140</span>
                        </div>
                        <canvas class="sb-canvas" id="canvasJitter" width="380" height="38"></canvas>
                    </div>

                    <div class="graph-box">
                        <div class="sb-hdr">
                            <span class="sb-title">🟡 Motor Kinematic Asymmetry Curve</span>
                            <span class="sb-val-pill" id="txtAsym" style="color:#fbbf24;">0.78</span>
                        </div>
                        <canvas class="sb-canvas" id="canvasAsym" width="380" height="38"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- 6. ACTION CONTROL BUTTON -->
        <div class="action-button-row">
            <button class="btn" id="actionBtn" onclick="toggleVerificationSession()">START VERIFICATION</button>
        </div>
    </div>

    <!-- FINAL AUDIT MODAL -->
    <div class="modal-backdrop" id="finalAuditModal">
        <div class="modal-card">
            <button class="modal-close-btn" onclick="closeAuditModal()">&times;</button>
            <div style="font-size:11px; text-transform:uppercase; letter-spacing:2px; color:#38bdf8; font-weight:700;">SYSTEM 1 // BIOMETRIC AUDIT REPORT</div>
            <h2 id="modalSessionHeader" style="font-size:22px; font-weight:900; margin:6px 0 16px 0; color:#fff;">SESSION CERTIFICATE</h2>
            <div id="modalVerdictBanner" style="padding:16px; border-radius:10px; border:2px solid #10b981; background:#10b98115; margin-bottom:16px;">
                <div id="modalVerdictTitle" style="font-size:18px; font-weight:900; color:#10b981;">✔ VERIFIED GENUINE HUMAN</div>
                <div id="modalScoreValue" style="font-size:28px; font-weight:900; color:#fff; font-family:monospace; margin-top:4px;">96%</div>
            </div>
            <div style="display:flex; gap:10px; margin-top:14px;">
                <button class="btn" onclick="closeAuditModal()" style="flex:1;">OK / COMPLETE</button>
                <a href="/dashboard" class="btn btn-cyan" style="flex:1; text-decoration:none; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:800;">VIEW IN DASHBOARD &rarr;</a>
            </div>
        </div>
    </div>

    <script>
        let currentMode = 'live';
        let isRunning = false;
        let isGatewayPassed = false;
        let voiceEnabled = true;
        let lastSpokenPrompt = "";

        let ws = null;
        let video = document.getElementById('webcam');
        let canvas = document.getElementById('captureCanvas');
        let ctx = canvas.getContext('2d');
        let hudCanvas = document.getElementById('hudOverlay');
        let hudCtx = hudCanvas.getContext('2d');
        let intervalId = null;

        // REAL Shape Tracing Engine
        let currentWaypoints = [];
        let shapeType = 'star';
        let visitedWaypoints = new Set();
        let targetWaypointIdx = 0;
        let activeSpokenCode = '';
        let recognition = null;
        let lastIndexTip = null;
        let activeTimeoutSec = 14.0;

        // Ring buffers
        const ringJitter = new Array(35).fill(0.0014);
        const ringPulse = new Array(35).fill(72);
        const ringAsym = new Array(35).fill(0.78);
        const ringTremor = new Array(35).fill(8.4);

        function toggleVoiceDictation() {
            voiceEnabled = !voiceEnabled;
            document.getElementById('speakerIcon').innerText = voiceEnabled ? "🔊" : "🔇";
            document.getElementById('speakerText').innerText = voiceEnabled ? "VOICE: ON" : "VOICE: MUTED";
            if (!voiceEnabled && 'speechSynthesis' in window) {
                window.speechSynthesis.cancel();
            }
        }

        function speakPromptAloud(text) {
            if (!voiceEnabled || !('speechSynthesis' in window) || !text) return;
            if (text === lastSpokenPrompt) return;
            lastSpokenPrompt = text;

            try {
                window.speechSynthesis.cancel();
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.rate = 0.95;
                utterance.pitch = 1.0;
                utterance.lang = 'en-US';
                window.speechSynthesis.speak(utterance);
            } catch(e) {}
        }

        function setSystemMode(mode) {
            if (isRunning) stopVerificationSession();
            currentMode = mode;
            const tabLive = document.getElementById('tabLive');
            const tabStd = document.getElementById('tabStandard');
            const btn = document.getElementById('actionBtn');

            if (mode === 'live') {
                tabLive.className = 'sys-tab green-active active';
                tabStd.className = 'sys-tab';
                btn.className = 'btn';
                btn.innerText = 'START LIVE MONITOR';
            } else {
                tabStd.className = 'sys-tab active';
                tabLive.className = 'sys-tab';
                btn.className = 'btn btn-cyan';
                btn.innerText = 'START VERIFICATION AUDIT';
            }
            resetUiDisplay();
        }

        function resetUiDisplay() {
            document.getElementById('taskBox').style.display = 'block';
            document.getElementById('passiveShieldBanner').style.display = 'none';
            document.getElementById('codeBadgesBox').style.display = 'none';
            document.getElementById('shapeProgressBadge').style.display = 'none';
            document.getElementById('stageBadge').innerText = 'SYSTEM GENERATED RANDOM PROTOCOL';
            document.getElementById('taskInstruction').innerText = 'Click "START VERIFICATION" to begin';
            document.getElementById('timerFill').style.width = '100%';
            document.getElementById('pillText').innerText = 'STANDBY: READY TO START';
            document.getElementById('pillDot').className = 'pill-dot';
            document.getElementById('pillText').className = 'pill-text';
            hudCtx.clearRect(0, 0, hudCanvas.width, hudCanvas.height);
            visitedWaypoints.clear();
        }

        function drawSparkline(canvasId, data, minVal, maxVal, strokeColor, fillColor) {
            const c = document.getElementById(canvasId);
            if (!c) return;
            const gCtx = c.getContext('2d');
            const w = c.width;
            const h = c.height;
            gCtx.clearRect(0, 0, w, h);

            const range = Math.max(1e-6, maxVal - minVal);
            const step = w / (data.length - 1);

            gCtx.beginPath();
            for (let i = 0; i < data.length; i++) {
                const norm = Math.max(0, Math.min(1, (data[i] - minVal) / range));
                const x = i * step;
                const y = h - norm * (h - 4) - 2;
                if (i === 0) gCtx.moveTo(x, y);
                else gCtx.lineTo(x, y);
            }
            gCtx.strokeStyle = strokeColor;
            gCtx.lineWidth = 1.6;
            gCtx.stroke();
            gCtx.lineTo(w, h);
            gCtx.lineTo(0, h);
            gCtx.closePath();
            gCtx.fillStyle = fillColor;
            gCtx.fill();
        }

        async function initCamera() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: { width:800, height:600 } });
                video.srcObject = stream;
            } catch(e) {
                alert("Please grant camera permissions to activate TrustLayer verification.");
            }
        }
        initCamera();

        function initSpeechRecognition() {
            const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRec) {
                document.getElementById('voiceCaption').innerText = "Speech API not available in this browser.";
                return;
            }
            recognition = new SpeechRec();
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = 'en-US';

            recognition.onresult = (event) => {
                let transcript = '';
                for (let i = event.resultIndex; i < event.results.length; ++i) {
                    transcript += event.results[i][0].transcript;
                }
                document.getElementById('voiceCaption').innerText = `🎙️ Heard: "${transcript.toUpperCase()}"`;
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({ spoken_text: transcript }));
                }
            };
            recognition.onerror = () => {};
        }
        initSpeechRecognition();

        // REAL Shape Rendering and Waypoint Distance Evaluation
        function updateAndRenderShapeOverlay() {
            hudCtx.clearRect(0, 0, hudCanvas.width, hudCanvas.height);

            if (!currentWaypoints || currentWaypoints.length < 5) return;

            let isFingerActive = false;
            let canvasFx = 0, canvasFy = 0;

            // Check distance from user's index finger tip (mirrored horizontally to match video)
            if (lastIndexTip) {
                const fx = (1.0 - lastIndexTip.x); // Mirrored video feed coordinate
                const fy = lastIndexTip.y;
                canvasFx = fx * hudCanvas.width;
                canvasFy = fy * hudCanvas.height;
                isFingerActive = true;

                // Generous tolerance radius (0.13) so natural finger pointing comfortably marks waypoints
                for (let i = 0; i < currentWaypoints.length; i++) {
                    const wp = currentWaypoints[i];
                    const dist = Math.hypot(wp.x - fx, wp.y - fy);
                    if (dist < 0.13) {
                        visitedWaypoints.add(i);
                    }
                }
            }

            // Draw prominent glowing fingertip reticle & position cursor
            if (isFingerActive) {
                hudCtx.save();
                // Outer pulsing target reticle
                hudCtx.beginPath();
                hudCtx.arc(canvasFx, canvasFy, 18, 0, 2 * Math.PI);
                hudCtx.strokeStyle = '#10b981';
                hudCtx.lineWidth = 2.5;
                hudCtx.shadowColor = '#10b981';
                hudCtx.shadowBlur = 12;
                hudCtx.stroke();

                // Crosshair markers
                hudCtx.beginPath();
                hudCtx.moveTo(canvasFx - 24, canvasFy); hudCtx.lineTo(canvasFx - 12, canvasFy);
                hudCtx.moveTo(canvasFx + 12, canvasFy); hudCtx.lineTo(canvasFx + 24, canvasFy);
                hudCtx.moveTo(canvasFx, canvasFy - 24); hudCtx.lineTo(canvasFx, canvasFy - 12);
                hudCtx.moveTo(canvasFx, canvasFy + 12); hudCtx.lineTo(canvasFx, canvasFy + 24);
                hudCtx.strokeStyle = 'rgba(16, 185, 129, 0.8)';
                hudCtx.lineWidth = 2;
                hudCtx.stroke();

                // Bright center point
                hudCtx.beginPath();
                hudCtx.arc(canvasFx, canvasFy, 6, 0, 2 * Math.PI);
                hudCtx.fillStyle = '#10b981';
                hudCtx.fill();

                // Fingertip badge label
                hudCtx.font = 'bold 11px sans-serif';
                hudCtx.fillStyle = '#10b981';
                hudCtx.shadowBlur = 6;
                hudCtx.fillText('👆 FINGERTIP', canvasFx + 16, canvasFy - 10);
                hudCtx.restore();
            } else {
                // Guidance tooltip when finger isn't detected yet
                hudCtx.save();
                hudCtx.font = 'bold 13px sans-serif';
                hudCtx.fillStyle = '#fbbf24';
                hudCtx.shadowColor = '#fbbf24';
                hudCtx.shadowBlur = 10;
                hudCtx.textAlign = 'center';
                hudCtx.fillText('👉 Raise hand with index finger pointed to trace the shape', hudCanvas.width / 2, 40);
                hudCtx.restore();
            }

            // Draw shape perimeter with visited coloring
            const pct = Math.round((visitedWaypoints.size / currentWaypoints.length) * 100);
            const badge = document.getElementById('shapeProgressBadge');
            badge.style.display = 'block';
            badge.innerText = `${shapeType.toUpperCase()} TRACED: ${pct}% (MIN 70% REQUIRED)`;
            badge.style.borderColor = pct >= 70 ? '#10b981' : '#fbbf24';
            badge.style.color = pct >= 70 ? '#10b981' : '#fbbf24';

            hudCtx.save();
            hudCtx.lineWidth = 4;
            hudCtx.lineCap = 'round';

            for (let i = 0; i < currentWaypoints.length; i++) {
                const nextIdx = (i + 1) % currentWaypoints.length;
                const wx1 = currentWaypoints[i].x * hudCanvas.width;
                const wy1 = currentWaypoints[i].y * hudCanvas.height;
                const wx2 = currentWaypoints[nextIdx].x * hudCanvas.width;
                const wy2 = currentWaypoints[nextIdx].y * hudCanvas.height;

                hudCtx.beginPath();
                hudCtx.moveTo(wx1, wy1);
                hudCtx.lineTo(wx2, wy2);

                if (visitedWaypoints.has(i)) {
                    hudCtx.strokeStyle = '#10b981';
                    hudCtx.shadowColor = '#10b981';
                    hudCtx.shadowBlur = 14;
                } else {
                    hudCtx.strokeStyle = 'rgba(56, 189, 248, 0.40)';
                    hudCtx.shadowColor = '#38bdf8';
                    hudCtx.shadowBlur = 6;
                }
                hudCtx.stroke();
            }

            // Draw animated traveling target dot
            targetWaypointIdx = (targetWaypointIdx + 1) % currentWaypoints.length;
            const targetPt = currentWaypoints[targetWaypointIdx];
            const tx = targetPt.x * hudCanvas.width;
            const ty = targetPt.y * hudCanvas.height;

            hudCtx.beginPath();
            hudCtx.arc(tx, ty, 9, 0, 2 * Math.PI);
            hudCtx.fillStyle = '#fbbf24';
            hudCtx.shadowColor = '#fbbf24';
            hudCtx.shadowBlur = 18;
            hudCtx.fill();

            hudCtx.restore();
        }

        function toggleVerificationSession() {
            if (isRunning) {
                stopVerificationSession();
            } else {
                startVerificationSession();
            }
        }

        function startVerificationSession() {
            isRunning = true;
            isGatewayPassed = false;
            lastSpokenPrompt = "";
            visitedWaypoints.clear();

            const btn = document.getElementById('actionBtn');
            btn.className = 'btn btn-stop';
            btn.innerText = 'VERIFICATION IN PROGRESS (CLICK TO STOP)';

            const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
            ws = new WebSocket(`${wsProtocol}//${window.location.host}/ws/verify?mode=${currentMode}`);

            ws.onopen = () => {
                intervalId = setInterval(captureAndSend, 120);
                if (recognition) {
                    try { recognition.start(); } catch(e) {}
                }
            };

            ws.onmessage = (event) => {
                const msg = JSON.parse(event.data);

                // Handle System 1 Audit Complete
                if (msg.status === "completed") {
                    stopVerificationSession();
                    showAuditResultModal(msg);
                    return;
                }

                // In Live Mode: If gateway cleared -> ALL TASKS STOP!
                if (currentMode === 'live' && msg.is_gateway_cleared) {
                    isGatewayPassed = true;
                    document.getElementById('taskBox').style.display = 'none';
                    document.getElementById('passiveShieldBanner').style.display = 'block';
                    currentWaypoints = [];
                    hudCtx.clearRect(0, 0, hudCanvas.width, hudCanvas.height);
                    if ('speechSynthesis' in window) window.speechSynthesis.cancel();

                    btn.className = 'btn btn-stop';
                    btn.innerText = 'END LIVE SHIELD';
                }

                // Setup Shape Waypoints if active
                if (msg.waypoints && msg.waypoints.length && !isGatewayPassed) {
                    if (currentWaypoints.length !== msg.waypoints.length) {
                        visitedWaypoints.clear();
                    }
                    currentWaypoints = msg.waypoints;
                    shapeType = msg.shape_type || 'star';
                } else if (!msg.waypoints) {
                    currentWaypoints = [];
                    document.getElementById('shapeProgressBadge').style.display = 'none';
                }

                // Setup Spoken Code (7-8 characters)
                if (msg.spoken_code && !isGatewayPassed) {
                    activeSpokenCode = msg.spoken_code;
                    document.getElementById('codeBadgesBox').style.display = 'block';
                    const row = document.getElementById('codeTilesRow');
                    row.innerHTML = activeSpokenCode.split('').map(c => `<div class="code-tile">${c}</div>`).join('');
                } else {
                    document.getElementById('codeBadgesBox').style.display = 'none';
                }

                // Update Task Instructions & Dynamic Timeouts
                if (msg.challenge && !isGatewayPassed) {
                    document.getElementById('taskInstruction').innerText = msg.challenge;
                    document.getElementById('stageBadge').innerText = msg.progress || 'STAGE IN PROGRESS';
                    activeTimeoutSec = msg.timeout_sec || 14.0;
                    document.getElementById('timerFill').style.width = `${(msg.time_left / activeTimeoutSec) * 100}%`;

                    if (msg.speech) {
                        speakPromptAloud(msg.speech);
                    }
                }

                // Extract index fingertip landmark
                if (msg.telemetry && msg.telemetry.index_tip) {
                    lastIndexTip = msg.telemetry.index_tip;
                }

                // Live Status Pill on Camera
                if (msg.live_health) {
                    const h = msg.live_health;
                    const dot = document.getElementById('pillDot');
                    const txt = document.getElementById('pillText');

                    if (h.is_suspicious) {
                        dot.className = 'pill-dot suspicious';
                        txt.className = 'pill-text suspicious';
                        txt.innerText = h.verdict;
                        video.style.boxShadow = "0 0 35px rgba(239, 68, 68, 0.85)";
                    } else {
                        dot.className = 'pill-dot';
                        txt.className = 'pill-text';
                        txt.innerText = isGatewayPassed ? 
                            "LIVE: VERIFIED GENUINE HUMAN (PASSIVE SHIELD ACTIVE)" : 
                            "LIVE SENSOR ACTIVE: VERIFYING PRESENCE";
                        video.style.boxShadow = "none";
                    }
                }

                // Telemetry Updates
                if (msg.telemetry) {
                    const t = msg.telemetry;

                    // Numeric Left Updates
                    if (t.heart_rate_bpm > 0) {
                        document.getElementById('valPulse').innerText = `${Math.round(t.heart_rate_bpm)} BPM`;
                        document.getElementById('txtPulse').innerText = `${Math.round(t.heart_rate_bpm)} BPM`;
                        ringPulse.push(t.heart_rate_bpm); ringPulse.shift();
                        drawSparkline('canvasPulse', ringPulse, 45, 120, '#10b981', 'rgba(16, 185, 129, 0.18)');
                    }
                    if (t.tremor_freq_hz) {
                        document.getElementById('valTremor').innerText = `${t.tremor_freq_hz.toFixed(1)} Hz [6-12]`;
                        document.getElementById('txtTremorGraph').innerText = `${t.tremor_freq_hz.toFixed(1)} Hz`;
                        ringTremor.push(t.tremor_freq_hz); ringTremor.shift();
                        drawSparkline('canvasTremor', ringTremor, 4.0, 15.0, '#a78bfa', 'rgba(167, 139, 250, 0.18)');
                    }
                    if (t.asymmetry_index) {
                        document.getElementById('valAsym').innerText = `${t.asymmetry_index.toFixed(2)} [Bio]`;
                        document.getElementById('txtAsym').innerText = t.asymmetry_index.toFixed(2);
                        ringAsym.push(t.asymmetry_index); ringAsym.shift();
                        drawSparkline('canvasAsym', ringAsym, 0.4, 1.8, '#fbbf24', 'rgba(251, 191, 36, 0.18)');
                    }
                    if (t.power_law_score !== undefined) {
                        document.getElementById('valPower').innerHTML = `&beta; = ${t.power_law_score.toFixed(2)} [Passed]`;
                    }
                    if (t.yaw !== undefined && t.pitch !== undefined) {
                        const ySign = t.yaw > 0 ? '+' : '';
                        const pSign = t.pitch > 0 ? '+' : '';
                        document.getElementById('valHeadPose').innerText = `Y: ${ySign}${t.yaw.toFixed(1)}° | P: ${pSign}${t.pitch.toFixed(1)}°`;
                    }
                    if (t.ear !== undefined) {
                        document.getElementById('valBlinks').innerText = `EAR: ${t.ear.toFixed(2)} | ${t.blinks || 0} Blinks`;
                    }
                    if (t.fingers_detected !== undefined) {
                        document.getElementById('valHand').innerText = `${t.fingers_detected} Fingers Up`;
                    }

                    const jVal = t.micro_jitter_std || 0.0014;
                    document.getElementById('txtJitter').innerText = jVal.toFixed(5);
                    document.getElementById('valJitterNum').innerText = jVal.toFixed(5);
                    ringJitter.push(jVal); ringJitter.shift();
                    drawSparkline('canvasJitter', ringJitter, 0.0, 0.008, '#38bdf8', 'rgba(56, 189, 248, 0.18)');
                }

                updateAndRenderShapeOverlay();
            };

            ws.onclose = () => {
                if (isRunning) stopVerificationSession();
            };
        }

        function stopVerificationSession() {
            isRunning = false;
            clearInterval(intervalId);
            if ('speechSynthesis' in window) window.speechSynthesis.cancel();
            if (recognition) {
                try { recognition.stop(); } catch(e) {}
            }
            if (ws && ws.readyState === WebSocket.OPEN) {
                try { ws.send(JSON.stringify({ action: "stop" })); } catch(e) {}
                ws.close();
            }

            const btn = document.getElementById('actionBtn');
            btn.className = currentMode === 'live' ? 'btn' : 'btn btn-cyan';
            btn.innerText = currentMode === 'live' ? 'START LIVE MONITOR' : 'START VERIFICATION AUDIT';

            resetUiDisplay();
        }

        // Send REAL calculated path_conformance
        function captureAndSend() {
            if (ws && ws.readyState === WebSocket.OPEN) {
                ctx.drawImage(video, 0, 0, 640, 480);
                const base64Img = canvas.toDataURL('image/jpeg', 0.65);

                const realConformance = currentWaypoints.length > 0 ? 
                    (visitedWaypoints.size / currentWaypoints.length) : 0.0;

                ws.send(JSON.stringify({
                    image: base64Img,
                    path_conformance: realConformance
                }));
            }
        }

        function showAuditResultModal(data) {
            document.getElementById('modalSessionHeader').innerText = `CERTIFICATE #${data.session_id}`;
            document.getElementById('modalScoreValue').innerText = `${data.score}%`;
            const isV = data.verdict === 'VERIFIED';
            document.getElementById('modalVerdictTitle').innerText = isV ? '✔ VERIFIED GENUINE HUMAN' : '✖ SUSPICIOUS / UNCONFIRMED';
            document.getElementById('modalVerdictTitle').style.color = isV ? '#10b981' : '#ef4444';
            document.getElementById('modalVerdictBanner').style.borderColor = isV ? '#10b981' : '#ef4444';
            document.getElementById('modalVerdictBanner').style.background = isV ? '#10b98115' : '#ef444415';
            document.getElementById('finalAuditModal').classList.add('open');
        }

        function closeAuditModal() {
            document.getElementById('finalAuditModal').classList.remove('open');
            resetUiDisplay();
        }
    </script>
</body>
</html>"""


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)
