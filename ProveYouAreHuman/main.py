"""
=============================================================================
TRUSTLAYER: AI-Powered Real-Time Human Verification & Deepfake Detection
Zeal Education Society's Zeal College of Engineering & Research, Pune-41
Department of Electronics and Computer Engineering
Project Based Learning (PBL)

Team Members:
1. Sandesh Kolhe (EC2212 - 125UEC1017)
2. Sanket Shinde (EC2209 - 125UEC1162)
3. Rajnandini Mane (EC2202 - 125UEC1145)

Guide: Prof. Sana A. Metkari | HOD: Dr. Mahesh S. Navale
=============================================================================
"""

import os
import sys
import time
import random
import math
import cv2
import numpy as np

import argparse

# Import Modular Pipeline
from modules.face_liveness import FaceLivenessDetector
from modules.hand_biomechanics import HandBiomechanicsDetector
from modules.deepfake_detector import DeepfakeArtifactDetector
from modules.scoring_engine import VerificationScoringEngine
from modules.report_generator import VerificationReportGenerator
from modules.ui_hud import UIOverlayRenderer
from modules.kinematic_tracker import KinematicTremorTracker
from modules.biomarker_monitor import BiomarkerMonitor


def find_model_path(filename):
    candidates = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), filename),
        os.path.join(os.getcwd(), filename),
        os.path.join(r"C:\Users\User", filename),
        os.path.join(r"C:\Users\User\ProveYouAreHuman", filename)
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return filename


class TrustLayerSystem:
    def __init__(self, mode="standard"):
        print("=======================================================")
        print(" TRUSTLAYER: AI HUMAN VERIFICATION & DEEPFAKE SYSTEM   ")
        print(" Zeal College of Engineering & Research, Pune-41      ")
        print("=======================================================")

        self.mode = mode  # "standard" (System 1: with end certificate) or "live" (System 2: continuous 24/7)

        face_model_path = find_model_path("face_landmarker.task")
        hand_model_path = find_model_path("hand_landmarker.task")

        if not os.path.exists(face_model_path):
            print(f"[-] ERROR: Face landmarker model not found at {face_model_path}")
            sys.exit(1)
        if not os.path.exists(hand_model_path):
            print(f"[-] ERROR: Hand landmarker model not found at {hand_model_path}")
            sys.exit(1)

        print(f"[+] Loaded Face Model: {face_model_path}")
        print(f"[+] Loaded Hand Model: {hand_model_path}")

        # Subsystems
        self.face_detector = FaceLivenessDetector(model_path=face_model_path)
        self.hand_detector = HandBiomechanicsDetector(model_path=hand_model_path)
        self.deepfake_detector = DeepfakeArtifactDetector()
        self.scoring_engine = VerificationScoringEngine()
        self.report_generator = VerificationReportGenerator(output_dir="reports")
        self.ui_renderer = UIOverlayRenderer()
        # New: Kinematic micro-tremor vector tracker
        self.kinematic_tracker = KinematicTremorTracker(fps=30.0)
        # New: Passive biomarker monitor (Phase 2 / Phase 3)
        self.biomarker_monitor = BiomarkerMonitor(phase=2, fps=30.0)

        # Challenge Definitions (Natural, comfortable hold times)
        self.CHALLENGE_POOL = [
            {"id": "TURN_LEFT", "type": "FACE_POSE", "title": "Turn Head LEFT", "desc": "Rotate head gently to the left", "hold": 0.55},
            {"id": "TURN_RIGHT", "type": "FACE_POSE", "title": "Turn Head RIGHT", "desc": "Rotate head gently to the right", "hold": 0.55},
            {"id": "SMILE", "type": "FACE_EXPRESSION", "title": "Smile at Camera", "desc": "Smile naturally showing facial movement", "hold": 0.60},
            {"id": "BLINK_TWICE", "type": "EYE_LIVENESS", "title": "Blink Twice", "desc": "Blink both eyes naturally twice", "target_blinks": 2},
            {"id": "HAND_RIGHT", "type": "HAND_BIO", "title": "Move Hand RIGHT", "desc": "Wave palm steadily to the right", "hold": 0.35},
            {"id": "HAND_LEFT", "type": "HAND_BIO", "title": "Move Hand LEFT", "desc": "Wave palm steadily to the left", "hold": 0.35},
            {"id": "HAND_UP", "type": "HAND_BIO", "title": "Move Hand UP", "desc": "Raise palm smoothly upwards", "hold": 0.35},
            {"id": "OPEN_PALM", "type": "HAND_GESTURE", "title": "Show OPEN Palm", "desc": "Extend all 5 fingers towards camera", "hold": 0.50}
        ]

        # State machine
        self.active_challenges = []
        self.current_step = 0
        self.step_start_time = 0
        self.step_hold_start = None
        self.target_blinks_baseline = 0
        self.challenge_timeout = 25.0
        self.session_verdict_data = None
        self.report_saved = False

        # Inter-step transition pacing
        self.is_transitioning = False
        self.transition_start_time = 0
        self.transition_duration = 1.2
        self.last_passed_title = ""

        self.reset_session()

    def reset_session(self):
        face_choices = [c for c in self.CHALLENGE_POOL if c["type"] in ["FACE_POSE", "FACE_EXPRESSION"]]
        blink_choice = [c for c in self.CHALLENGE_POOL if c["id"] == "BLINK_TWICE"]
        hand_choices = [c for c in self.CHALLENGE_POOL if c["type"] in ["HAND_BIO", "HAND_GESTURE"]]

        if self.mode == "standard":
            # SYSTEM 1: Structured 3-step sequence with final verification certificate
            selected = [
                random.choice(face_choices),
                blink_choice[0],
                random.choice(hand_choices)
            ]
        else:
            # SYSTEM 2: Continuous live monitoring rolling sequence
            selected = [
                random.choice(face_choices)
            ]

        self.active_challenges = selected
        self.current_step = 0
        self.step_start_time = time.time()
        self.step_hold_start = None
        self.session_verdict_data = None
        self.report_saved = False
        self.is_transitioning = False

        self.face_detector.reset_counters()
        self.hand_detector.reset_tracking()
        self.deepfake_detector.reset()
        self.scoring_engine.reset()
        self.kinematic_tracker.reset()
        self.biomarker_monitor.reset()
        # Phase 2 for standard/live modes (drop to Phase 3 via [P] key)
        self.biomarker_monitor.set_phase(2)

        self.target_blinks_baseline = 0
        print(f"\n[*] Initialized [{self.mode.upper()} SYSTEM]: Session #{self.scoring_engine.session_id}")
        if self.mode == "standard":
            print(f"[*] Standard 3-Step Sequence: {[c['id'] for c in self.active_challenges]}")
        else:
            print("[*] Continuous Live Shield Active: Real-time low-bar anomaly monitoring")

    def evaluate_current_challenge(self, face_data, hand_data):
        if self.current_step >= len(self.active_challenges):
            return False, 0.0, False

        chal = self.active_challenges[self.current_step]
        c_id = chal["id"]
        now = time.time()
        condition_met = False

        # 1. Face Pose / Expression
        if c_id in ["TURN_LEFT", "TURN_RIGHT"]:
            yaw = face_data.get("yaw", 0.0)
            tr = face_data.get("turn_ratio", 0.5)
            condition_met = (abs(yaw) >= 4.5) or (abs(tr - 0.5) >= 0.08)
        elif c_id == "SMILE":
            condition_met = face_data.get("is_smiling", False) or face_data.get("smile_intensity", 0.0) > 0.45

        # 2. Eye Blink
        elif c_id == "BLINK_TWICE":
            blinks_done = face_data.get("total_blinks", 0) - self.target_blinks_baseline
            if blinks_done >= chal.get("target_blinks", 2):
                return True, 1.0, True
            return False, min(1.0, blinks_done / 2.0), False

        # 3. Hand Biomechanics
        elif c_id in ["HAND_LEFT", "HAND_RIGHT", "HAND_UP", "HAND_DOWN"]:
            direction_key = c_id.replace("HAND_", "")
            if hand_data.get("challenge_passed", False):
                return True, 1.0, True
            condition_met = self.hand_detector.check_challenge_movement(
                direction_key,
                hand_data.get("total_dx", 0.0),
                hand_data.get("total_dy", 0.0),
                hand_data.get("finger_state") or {}
            )

        elif c_id == "OPEN_PALM":
            f_state = hand_data.get("finger_state") or {}
            condition_met = f_state.get("is_open_palm", False)

        # Hold Duration Check
        hold_time_req = chal.get("hold", 0.50)
        hold_ratio = 0.0

        if condition_met:
            if self.step_hold_start is None:
                self.step_hold_start = now
            held = now - self.step_hold_start
            hold_ratio = min(1.0, held / hold_time_req)
            if held >= hold_time_req:
                return True, 1.0, True
        else:
            self.step_hold_start = None
            hold_ratio = 0.0

        return condition_met, hold_ratio, False

    def run(self):
        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        if not camera.isOpened():
            print("[-] WARNING: Physical webcam index 0 could not be opened.")
            print("[*] Creating a synthetic validation stream...")
            use_synthetic = True
        else:
            use_synthetic = False

        prev_frame_time = time.time()
        fps = 30.0

        print("\n[+] Verification system running. Controls: [Q] Quit, [R] Restart, [S] Save Report\n")

        while True:
            cur_time = time.time()
            dt = cur_time - prev_frame_time
            if dt > 0:
                fps = 0.9 * fps + 0.1 * (1.0 / dt)
            prev_frame_time = cur_time

            if not use_synthetic:
                ret, frame = camera.read()
                if not ret:
                    break
                frame = cv2.flip(frame, 1)
            else:
                frame = np.zeros((720, 1280, 3), dtype=np.uint8)
                frame[:] = (25, 25, 30)
                cv2.putText(frame, "SYNTHETIC DEMO STREAM (No physical camera attached)", (320, 360), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)
                time.sleep(0.03)

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Determine active hand challenge for detector
            active_hand_chal = None
            if not self.is_transitioning and self.current_step < len(self.active_challenges):
                c_id = self.active_challenges[self.current_step]["id"]
                if c_id.startswith("HAND_"):
                    active_hand_chal = c_id.replace("HAND_", "")
                elif c_id in ["OPEN_PALM", "FIST"]:
                    active_hand_chal = c_id

            # -------------------------------------------------------------
            # 1. RUN PARALLEL VERIFICATION INFERENCE
            # -------------------------------------------------------------
            face_data = self.face_detector.process_frame(rgb)
            hand_data = self.hand_detector.process_frame(rgb, current_challenge=active_hand_chal)
            df_data   = self.deepfake_detector.analyze_face(frame, face_data.get("face_box"))

            # Feed kinematic tracker from nose + wrist landmarks
            if face_data.get("detected") and face_data.get("landmarks"):
                lm = face_data["landmarks"]
                self.kinematic_tracker.push_nose(lm[1].x, lm[1].y)
            if hand_data.get("detected") and hand_data.get("palm"):
                px, py = hand_data["palm"]
                self.kinematic_tracker.push_wrist(px, py)

            # Notify onset when hand starts moving (velocity threshold)
            if hand_data.get("velocity", 0.0) > 0.04:
                self.kinematic_tracker.notify_movement_onset()

            # Kinematic profile
            kinematic_data = self.kinematic_tracker.get_tremor_profile()

            # Biomarker monitor (passive, always running)
            biomarker_data = self.biomarker_monitor.update(
                frame, face_data.get("landmarks")
            )

            # -------------------------------------------------------------
            # 2. CHALLENGE STATE MACHINE (SYSTEM 1 vs SYSTEM 2)
            # -------------------------------------------------------------
            if self.mode == "standard":
                # SYSTEM 1: STANDARD 3-STEP VERIFICATION (WITH FINAL RESULT CERTIFICATE)
                if self.is_transitioning:
                    trans_elapsed = cur_time - self.transition_start_time
                    if trans_elapsed >= self.transition_duration:
                        self.is_transitioning = False
                        self.current_step += 1
                        self.step_start_time = cur_time
                        self.step_hold_start = None
                        self.target_blinks_baseline = face_data.get("total_blinks", 0)
                        self.hand_detector.reset_tracking()
                    else:
                        self.ui_renderer.draw_challenge_card(
                            frame,
                            prompt_title=f"PASSED: {self.last_passed_title}!",
                            prompt_desc="Get ready for the next challenge...",
                            progress_str=f"{self.current_step + 1}/{len(self.active_challenges)}",
                            hold_pct=1.0,
                            time_left=self.challenge_timeout
                        )

                elif self.current_step < len(self.active_challenges):
                    active_chal = self.active_challenges[self.current_step]
                    elapsed = cur_time - self.step_start_time
                    time_left = max(0.0, self.challenge_timeout - elapsed)

                    if time_left <= 0.0:
                        self.scoring_engine.add_anomaly("CHALLENGE_TIMEOUT_EXPIRED")
                        self.current_step += 1
                        self.step_start_time = cur_time
                        self.step_hold_start = None
                        self.target_blinks_baseline = face_data.get("total_blinks", 0)
                        self.hand_detector.reset_tracking()
                    else:
                        hold_ratio = 0.0  # always initialize before evaluate
                        is_met, hold_ratio, passed = self.evaluate_current_challenge(face_data, hand_data)
                        if passed:
                            duration = cur_time - self.step_start_time
                            print(f"[+] STEP {self.current_step + 1} PASSED: {active_chal['id']} ({duration:.2f}s)")
                            self.scoring_engine.record_challenge_completion(
                                challenge_name=active_chal["title"],
                                challenge_type=active_chal["type"],
                                time_taken=duration
                            )
                            self.is_transitioning = True
                            self.transition_start_time = cur_time
                            self.last_passed_title = active_chal["title"]

                    if not self.is_transitioning and self.current_step < len(self.active_challenges):
                        chal_curr = self.active_challenges[self.current_step]
                        step_str = f"{self.current_step + 1}/{len(self.active_challenges)}"
                        self.ui_renderer.draw_challenge_card(
                            frame,
                            prompt_title=chal_curr["title"],
                            prompt_desc=chal_curr["desc"],
                            progress_str=step_str,
                            hold_pct=hold_ratio,
                            time_left=time_left,
                            challenge_timeout=self.challenge_timeout
                        )
                else:
                    # SYSTEM 1 END RESULT: COMPUTE DECISION FUSION & SHOW CERTIFICATE MODAL
                    if self.session_verdict_data is None:
                        self.session_verdict_data = self.scoring_engine.compute_final_verdict(
                            face_metrics=face_data,
                            hand_metrics=hand_data,
                            deepfake_metrics=df_data,
                            total_challenges_req=len(self.active_challenges),
                            kinematic_metrics=kinematic_data
                        )
                        print("\n=======================================================")
                        print(" FINAL VERIFICATION AUDIT RESULT")
                        print("=======================================================")
                        print(f" Session ID:   #{self.session_verdict_data['session_id']}")
                        print(f" Score:        {self.session_verdict_data['final_score']}%")
                        print(f" Verdict:      {self.session_verdict_data['verdict']}")
                        print(f" Confidence:   {self.session_verdict_data['confidence_level']}")
                        print("=======================================================\n")

                        if not self.report_saved:
                            j_file = self.report_generator.export_json_report(self.session_verdict_data)
                            h_file = self.report_generator.export_html_report(self.session_verdict_data)
                            c_file = self.report_generator.export_summary_certificate_image(self.session_verdict_data)
                            print(f"[+] JSON Log saved:        {j_file}")
                            print(f"[+] HTML Audit Cert saved: {h_file}")
                            print(f"[+] PNG Certificate saved: {c_file}")
                            self.report_saved = True

                    self.ui_renderer.draw_final_verdict(frame, self.session_verdict_data)

            else:
                # SYSTEM 2: CONTINUOUS LIVE SHIELD (24/7 RUNNING - NEVER ENDS)
                if self.is_transitioning:
                    trans_elapsed = cur_time - self.transition_start_time
                    if trans_elapsed >= self.transition_duration:
                        self.is_transitioning = False
                        self.current_step += 1
                        self.active_challenges.append(random.choice(self.CHALLENGE_POOL))
                        self.step_start_time = cur_time
                        self.step_hold_start = None
                        self.target_blinks_baseline = face_data.get("total_blinks", 0)
                        self.hand_detector.reset_tracking()
                    else:
                        self.ui_renderer.draw_challenge_card(
                            frame,
                            prompt_title=f"PASSED: {self.last_passed_title}!",
                            prompt_desc="Biometrics confirmed. Preparing next challenge...",
                            progress_str=f"{self.current_step + 1}",
                            hold_pct=1.0,
                            time_left=self.challenge_timeout
                        )
                else:
                    if self.current_step >= len(self.active_challenges):
                        self.active_challenges.append(random.choice(self.CHALLENGE_POOL))

                    active_chal = self.active_challenges[self.current_step]
                    elapsed = cur_time - self.step_start_time
                    time_left = max(0.0, self.challenge_timeout - elapsed)

                    if time_left <= 0.0:
                        self.scoring_engine.add_anomaly("CHALLENGE_TIMEOUT_EXPIRED")
                        self.current_step += 1
                        self.active_challenges.append(random.choice(self.CHALLENGE_POOL))
                        self.step_start_time = cur_time
                        self.step_hold_start = None
                        self.target_blinks_baseline = face_data.get("total_blinks", 0)
                        self.hand_detector.reset_tracking()
                    else:
                        hold_ratio = 0.0  # always initialize before evaluate
                        is_met, hold_ratio, passed = self.evaluate_current_challenge(face_data, hand_data)
                        if passed:
                            duration = cur_time - self.step_start_time
                            self.scoring_engine.record_challenge_completion(
                                challenge_name=active_chal["title"],
                                challenge_type=active_chal["type"],
                                time_taken=duration
                            )
                            self.is_transitioning = True
                            self.transition_start_time = cur_time
                            self.last_passed_title = active_chal["title"]

                    if not self.is_transitioning and self.current_step < len(self.active_challenges):
                        chal_curr = self.active_challenges[self.current_step]
                        self.ui_renderer.draw_challenge_card(
                            frame,
                            prompt_title=chal_curr["title"],
                            prompt_desc=chal_curr["desc"],
                            progress_str=f"{self.current_step + 1}",
                            hold_pct=hold_ratio,
                            time_left=time_left,
                            challenge_timeout=self.challenge_timeout
                        )

            # -------------------------------------------------------------
            # 3. REAL-TIME LIVE EVALUATION (ALL MODULES FUSED)
            # -------------------------------------------------------------
            is_face    = face_data.get("detected", False)
            yaw        = abs(face_data.get("yaw", 0.0))
            tremor_var = face_data.get("tremor_variance", 0.0)
            parallax   = face_data.get("depth_parallax", 0.0)
            auth_score = df_data.get("authenticity_score", 0.90) if isinstance(df_data, dict) else 0.90

            # Kinematic & Biomarker supplementary scores
            kin_score    = kinematic_data.get("kinematic_liveness_score", 0.85)
            kin_flags    = kinematic_data.get("anomaly_flags", [])
            bio_score    = biomarker_data.get("composite_score", 0.80)
            bio_flags    = biomarker_data.get("anomaly_flags", [])

            live_is_suspicious = False
            live_alert    = "All biometric vectors normal & healthy"
            low_bar_title = None
            live_score    = 96.0

            if not is_face:
                live_is_suspicious = True
                low_bar_title = "Face Presence Bar (0%)"
                live_alert    = "NO HUMAN FACE DETECTED"
                live_score    = 0.0
            elif len(self.face_detector.displacement_history) >= 8 and tremor_var < 0.00010:
                live_is_suspicious = True
                low_bar_title = f"Micro-Jitter Bar ({tremor_var:.6f})"
                live_alert    = "LOW BIOLOGICAL JITTER: Static Photo / Screen Replay"
                live_score    = 25.0
            elif parallax < 0.035 and yaw > 6.0:
                live_is_suspicious = True
                low_bar_title = f"3D Parallax Bar ({parallax:.2f})"
                live_alert    = "LOW 3D PARALLAX: Flat 2D Display Replay"
                live_score    = 30.0
            elif auth_score < 0.45:
                live_is_suspicious = True
                low_bar_title = f"Authenticity Bar ({int(auth_score * 100)}%)"
                live_alert    = "AUTHENTICITY LOW: Deepfake Artifact Detected"
                live_score    = 35.0
            elif kinematic_data.get("is_suspicious", False):
                live_is_suspicious = True
                flag_str      = ", ".join(kin_flags[:2]) if kin_flags else "KINEMATIC ANOMALY"
                low_bar_title = f"Kinematic Score ({int(kin_score * 100)}%)"
                live_alert    = f"KINEMATIC ANOMALY: {flag_str}"
                live_score    = max(10.0, kin_score * 60.0)
            elif biomarker_data.get("is_suspicious", False):
                live_is_suspicious = True
                flag_str      = ", ".join(bio_flags[:2]) if bio_flags else "BIOMARKER ANOMALY"
                low_bar_title = f"Biomarker Score ({int(bio_score * 100)}%)"
                live_alert    = f"BIOMARKER: {flag_str}"
                live_score    = max(15.0, bio_score * 65.0)
            else:
                # Fuse all sub-scores into composite
                live_score = min(99.0, (
                    auth_score * 30.0 +
                    kin_score  * 35.0 +
                    bio_score  * 25.0 +
                    (0.95 if not live_is_suspicious else 0.5) * 10.0
                ))

            live_health = {
                "is_suspicious": live_is_suspicious,
                "low_bar_title": low_bar_title,
                "score": int(live_score),
                "alert": live_alert,
                "verdict": "SUSPICIOUS: NO HUMAN DETECTED" if live_is_suspicious else "LIVE: VERIFIED GENUINE HUMAN"
            }

            # -------------------------------------------------------------
            # 4. DRAW OVERLAYS, TELEMETRY & ALERT BORDERS
            # -------------------------------------------------------------
            # Only draw standard HUD if not showing final verdict certificate card
            if not (self.mode == "standard" and self.current_step >= len(self.active_challenges)):
                self.ui_renderer.draw_face_landmarks(frame, face_data.get("landmarks"))
                self.ui_renderer.draw_hand_landmarks(frame, hand_data.get("landmarks"), hand_data.get("palm"), hand_data.get("start_palm"))
                self.ui_renderer.draw_top_bar(frame, self.scoring_engine.session_id, fps, live_health=live_health, mode=self.mode)
                # Bug fix: cognitive latency = onset time since FIRST movement (kinematic), not full session elapsed
                onset_ms = kinematic_data.get("cognitive", {}).get("mean_onset_ms", 0.0)
                face_data["cognitive_latency_ms"] = int(onset_ms) if onset_ms > 0 else int(max(0, (cur_time - self.step_start_time) * 500.0))
                self.ui_renderer.draw_telemetry_hud(frame, face_data, hand_data, df_data, live_health=live_health, kinematic_data=kinematic_data)
                # Bug fix: render biomarker (rPPG + micro-jitter) HUD panel — was never called before
                self.biomarker_monitor.render_hud(frame, x=20, y=185, w=295, h=140)
                self.ui_renderer.draw_footer_controls(frame)

                # Prominent Red Alert Visual Warning when any bar gets low
                if live_is_suspicious:
                    h_f, w_f = frame.shape[:2]
                    cv2.rectangle(frame, (0, 0), (w_f - 1, h_f - 1), (60, 60, 240), 4)
                    cv2.putText(frame, f"[ALERT] {live_alert}", (24, 185), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (60, 60, 240), 2)

            cv2.imshow("TRUSTLAYER: AI HUMAN VERIFICATION SYSTEM", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                self.reset_session()
            elif key == ord('m'):
                self.mode = "live" if self.mode == "standard" else "standard"
                print(f"\n[!] Switched System Mode to: {self.mode.upper()}")
                self.reset_session()
            elif key == ord('s'):
                if self.session_verdict_data:
                    h_file = self.report_generator.export_html_report(self.session_verdict_data)
                    c_file = self.report_generator.export_summary_certificate_image(self.session_verdict_data)
                    print(f"[+] Report re-exported: {h_file}")
            elif key == ord('p'):
                # Toggle Phase 2 <-> Phase 3 for biomarker monitor
                new_phase = 3 if self.biomarker_monitor.phase == 2 else 2
                self.biomarker_monitor.set_phase(new_phase)
                print(f"[!] Biomarker Monitor switched to Phase {new_phase}")

        if not use_synthetic:
            camera.release()
        cv2.destroyAllWindows()
        self.face_detector.close()
        self.hand_detector.close()
        print("\n[+] TrustLayer engine terminated cleanly.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TrustLayer Biometric Verification System")
    parser.add_argument("--mode", choices=["standard", "live"], default="standard",
                        help="Operating mode: standard (System 1: with end certificate) or live (System 2: 24/7 continuous)")
    args = parser.parse_args()
    app = TrustLayerSystem(mode=args.mode)
    app.run()