"""
Modern HUD & Visual Telemetry Overlay Module
TrustLayer: Human Verification for the AI Era
Zeal College of Engineering & Research, Pune-41
"""

import math
import cv2
import numpy as np


class UIOverlayRenderer:
    def __init__(self):
        # Color palette (BGR)
        self.COLOR_BG = (18, 18, 22)
        self.COLOR_CARD = (28, 28, 35)
        self.COLOR_BORDER = (50, 50, 60)
        self.COLOR_CYAN = (245, 180, 0)
        self.COLOR_GREEN = (80, 230, 80)
        self.COLOR_AMBER = (0, 180, 255)
        self.COLOR_RED = (60, 60, 240)
        self.COLOR_WHITE = (245, 245, 250)
        self.COLOR_GRAY = (140, 140, 150)
        self.COLOR_NEON_PINK = (220, 50, 230)

        # Mathematical Vector Telemetry Graph Ring-Buffers
        self.history_parallax = [0.0] * 35
        self.history_jitter = [0.0] * 35
        self.history_latency = [0.0] * 35

    def draw_rounded_rect(self, img, pt1, pt2, color, thickness=1, r=10):
        x1, y1 = pt1
        x2, y2 = pt2
        r = min(r, abs(x2 - x1) // 2, abs(y2 - y1) // 2)

        # Draw filled or outline
        if thickness < 0:
            cv2.rectangle(img, (x1 + r, y1), (x2 - r, y2), color, -1)
            cv2.rectangle(img, (x1, y1 + r), (x2, y2 - r), color, -1)
            cv2.circle(img, (x1 + r, y1 + r), r, color, -1)
            cv2.circle(img, (x2 - r, y1 + r), r, color, -1)
            cv2.circle(img, (x1 + r, y2 - r), r, color, -1)
            cv2.circle(img, (x2 - r, y2 - r), r, color, -1)
        else:
            cv2.line(img, (x1 + r, y1), (x2 - r, y1), color, thickness)
            cv2.line(img, (x1 + r, y2), (x2 - r, y2), color, thickness)
            cv2.line(img, (x1, y1 + r), (x1, y2 - r), color, thickness)
            cv2.line(img, (x2, y1 + r), (x2, y2 - r), color, thickness)
            cv2.ellipse(img, (x1 + r, y1 + r), (r, r), 180, 0, 90, color, thickness)
            cv2.ellipse(img, (x2 - r, y1 + r), (r, r), 270, 0, 90, color, thickness)
            cv2.ellipse(img, (x1 + r, y2 - r), (r, r), 90, 0, 90, color, thickness)
            cv2.ellipse(img, (x2 - r, y2 - r), (r, r), 0, 0, 90, color, thickness)

    def draw_top_bar(self, frame, session_id, fps, state_text="SYSTEM ACTIVE", live_health=None, mode="live"):
        w = frame.shape[1]
        
        # Transparent top bar background
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 52), (14, 14, 18), -1)
        cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)
        cv2.line(frame, (0, 52), (w, 52), (45, 45, 55), 1)

        # Title
        cv2.putText(frame, "TRUSTLAYER", (20, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.75, self.COLOR_CYAN, 2)
        
        # Mode Tag
        mode_label = "MODE: LIVE SHIELD" if mode == "live" else "MODE: STANDARD AUDIT"
        mode_color = self.COLOR_GREEN if mode == "live" else self.COLOR_AMBER
        cv2.putText(frame, f"[{mode_label}]", (195, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.44, mode_color, 1)

        # Dynamic Live Status Badge
        if live_health:
            is_susp = live_health.get("is_suspicious", False)
            verdict_text = live_health.get("verdict", "LIVE MONITOR")
            
            if is_susp:
                # Flashing Red Suspicious Badge
                cv2.putText(frame, f"[ {verdict_text} ]", (410, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.50, self.COLOR_RED, 2)
                cv2.circle(frame, (w - 40, 28), 6, self.COLOR_RED, -1)
            else:
                # Glowing Green Verified Human Badge
                cv2.putText(frame, f"[ {verdict_text} ]", (410, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.50, self.COLOR_GREEN, 2)
                cv2.circle(frame, (w - 40, 28), 6, self.COLOR_GREEN, -1)
        else:
            cv2.circle(frame, (w - 40, 28), 5, self.COLOR_GREEN, -1)

        # Session & FPS
        cv2.putText(frame, f"SESSION: #{session_id}", (w - 360, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.45, self.COLOR_WHITE, 1)
        cv2.putText(frame, f"FPS: {int(fps)}", (w - 170, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.45, self.COLOR_GREEN, 1)

    def draw_challenge_card(self, frame, prompt_title, prompt_desc, progress_str, hold_pct=0.0, time_left=10.0, challenge_timeout=25.0):
        w = frame.shape[1]
        card_w = 460
        card_h = 100
        x1 = 20
        y1 = 65
        x2 = x1 + card_w
        y2 = y1 + card_h

        # Semi-transparent card
        overlay = frame.copy()
        cv2.rectangle(overlay, (x1, y1), (x2, y2), self.COLOR_CARD, -1)
        cv2.addWeighted(overlay, 0.88, frame, 0.12, 0, frame)
        self.draw_rounded_rect(frame, (x1, y1), (x2, y2), self.COLOR_BORDER, thickness=1, r=8)

        # Header tag
        cv2.putText(frame, "LIVE ACTION CHALLENGE", (x1 + 16, y1 + 24), cv2.FONT_HERSHEY_SIMPLEX, 0.42, self.COLOR_CYAN, 1)
        cv2.putText(frame, f"CHALLENGE: {progress_str}", (x2 - 140, y1 + 24), cv2.FONT_HERSHEY_SIMPLEX, 0.42, self.COLOR_AMBER, 1)

        # Prompt text
        cv2.putText(frame, prompt_title, (x1 + 16, y1 + 55), cv2.FONT_HERSHEY_SIMPLEX, 0.75, self.COLOR_WHITE, 2)
        cv2.putText(frame, prompt_desc, (x1 + 16, y1 + 78), cv2.FONT_HERSHEY_SIMPLEX, 0.42, self.COLOR_GRAY, 1)

        # Hold / verification progress bar at bottom of card
        if hold_pct > 0.0:
            bar_w = int((card_w - 32) * min(1.0, hold_pct))
            cv2.rectangle(frame, (x1 + 16, y2 - 8), (x1 + 16 + bar_w, y2 - 4), self.COLOR_GREEN, -1)
        else:
            # Time left indicator bar — scale against actual challenge timeout (not hardcoded 12s)
            time_pct = max(0.0, min(1.0, time_left / max(challenge_timeout, 1.0)))
            bar_w = int((card_w - 32) * time_pct)
            t_col = self.COLOR_CYAN if time_pct > 0.35 else self.COLOR_RED
            cv2.rectangle(frame, (x1 + 16, y2 - 8), (x1 + 16 + bar_w, y2 - 4), t_col, -1)
            # Time remaining text
            cv2.putText(frame, f"{time_left:.0f}s", (x2 - 48, y2 - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.38, t_col, 1)

    def draw_telemetry_hud(self, frame, face_data, hand_data, df_data, live_health=None, kinematic_data=None):
        h, w = frame.shape[:2]
        hud_w = 260
        x1 = w - hud_w - 20
        y1 = 65
        x2 = w - 20
        y2 = h - 50

        # Semi-transparent sidebar
        overlay = frame.copy()
        cv2.rectangle(overlay, (x1, y1), (x2, y2), (18, 18, 24), -1)
        cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)
        self.draw_rounded_rect(frame, (x1, y1), (x2, y2), self.COLOR_BORDER, thickness=1, r=8)

        # Title
        cv2.putText(frame, "LIVE BIOMETRIC TELEMETRY", (x1 + 14, y1 + 24), cv2.FONT_HERSHEY_SIMPLEX, 0.42, self.COLOR_CYAN, 1)
        cv2.line(frame, (x1 + 14, y1 + 32), (x2 - 14, y1 + 32), (45, 45, 55), 1)

        cur_y = y1 + 50

        # Master Live Human Trust Bar
        if live_health:
            trust_score = live_health.get("score", 95)
            is_susp = live_health.get("is_suspicious", False)
            t_col = self.COLOR_RED if is_susp else self.COLOR_GREEN
            status_txt = "NO HUMAN" if is_susp else "VERIFIED"
            cv2.putText(frame, f"TRUST BAR: {trust_score}% [{status_txt}]", (x1 + 14, cur_y), cv2.FONT_HERSHEY_SIMPLEX, 0.40, t_col, 1)
            cur_y += 6
            bar_fill_w = int(230 * (max(0, min(100, trust_score)) / 100.0))
            cv2.rectangle(frame, (x1 + 14, cur_y), (x1 + 14 + 230, cur_y + 6), (35, 35, 45), -1)
            cv2.rectangle(frame, (x1 + 14, cur_y), (x1 + 14 + bar_fill_w, cur_y + 6), t_col, -1)
            cur_y += 20

        # 1. Face Metrics
        cv2.putText(frame, "[ FACE LIVENESS ]", (x1 + 14, cur_y), cv2.FONT_HERSHEY_SIMPLEX, 0.38, self.COLOR_GRAY, 1)
        cur_y += 18
        
        yaw = face_data.get("yaw", 0.0)
        pitch = face_data.get("pitch", 0.0)
        cv2.putText(frame, f"Head Pose: Y:{yaw:.1f} P:{pitch:.1f}", (x1 + 14, cur_y), cv2.FONT_HERSHEY_SIMPLEX, 0.40, self.COLOR_WHITE, 1)
        cur_y += 16

        ear = face_data.get("ear", 0.0)
        blinks = face_data.get("total_blinks", 0)
        is_closed = face_data.get("is_eye_closed", False)
        eye_status = "CLOSED" if is_closed else "OPEN"
        eye_color = self.COLOR_AMBER if is_closed else self.COLOR_GREEN
        cv2.putText(frame, f"EAR: {ear:.2f} ({eye_status}) | Blinks: {blinks}", (x1 + 14, cur_y), cv2.FONT_HERSHEY_SIMPLEX, 0.38, eye_color, 1)
        cur_y += 16

        smile_int = face_data.get("smile_intensity", 0.0)
        is_smiling = face_data.get("is_smiling", False)
        smile_text = f"Smile: {int(smile_int * 100)}%" + (" [ACTIVE]" if is_smiling else "")
        smile_col = self.COLOR_GREEN if is_smiling else self.COLOR_WHITE
        cv2.putText(frame, smile_text, (x1 + 14, cur_y), cv2.FONT_HERSHEY_SIMPLEX, 0.38, smile_col, 1)
        cur_y += 22

        # 2. Hand Metrics
        cv2.putText(frame, "[ HAND BIOMECHANICS ]", (x1 + 14, cur_y), cv2.FONT_HERSHEY_SIMPLEX, 0.38, self.COLOR_GRAY, 1)
        cur_y += 18

        h_detected = hand_data.get("detected", False)
        if h_detected:
            f_state = hand_data.get("finger_state") or {}
            ext_count = f_state.get("extended_count", 0)
            vel = hand_data.get("velocity", 0.0)
            bio_sc = hand_data.get("bio_score", 1.0)
            bio_col = self.COLOR_GREEN if bio_sc > 0.80 else self.COLOR_AMBER
            cv2.putText(frame, f"Hand: Active | Fingers:{ext_count}/5 | v:{vel:.3f}", (x1 + 14, cur_y), cv2.FONT_HERSHEY_SIMPLEX, 0.38, self.COLOR_WHITE, 1)
        else:
            cv2.putText(frame, "Hand: No Hand In Frame", (x1 + 14, cur_y), cv2.FONT_HERSHEY_SIMPLEX, 0.38, self.COLOR_GRAY, 1)
        cur_y += 16

        # 2b. Kinematic biomechanics (Two-Thirds Power Law + Asymmetry Index)
        if kinematic_data:
            pl = kinematic_data.get("power_law", {})
            asym = kinematic_data.get("asymmetry", {})
            beta = pl.get("beta_exponent", 0.0)
            corr = pl.get("curvature_velocity_corr", 0.0)
            is_bio = pl.get("is_biological", True)
            asym_idx = asym.get("nose_asymmetry_index", 0.78)
            is_human_asym = asym.get("is_asymmetric_human", True)
            pl_col = self.COLOR_GREEN if is_bio else self.COLOR_RED
            asym_col = self.COLOR_GREEN if is_human_asym else self.COLOR_AMBER
            cv2.putText(frame, f"2/3 Power Law: β={beta:.2f} r={corr:.2f} {'[BIO]' if is_bio else '[BOT?]'}", (x1 + 14, cur_y), cv2.FONT_HERSHEY_SIMPLEX, 0.36, pl_col, 1)
            cur_y += 15
            cv2.putText(frame, f"Motor Asym: {asym_idx:.2f} {'[HUMAN]' if is_human_asym else '[FLAT]'}", (x1 + 14, cur_y), cv2.FONT_HERSHEY_SIMPLEX, 0.36, asym_col, 1)
            cur_y += 6
        cur_y += 10

        # 3. Deepfake / Anti-Spoofing
        cv2.putText(frame, "[ DEEPFAKE ARTIFACTS ]", (x1 + 14, cur_y), cv2.FONT_HERSHEY_SIMPLEX, 0.38, self.COLOR_GRAY, 1)
        cur_y += 18

        auth_score = df_data.get("authenticity_score", 0.85)
        df_col = self.COLOR_GREEN if auth_score > 0.70 else (self.COLOR_AMBER if auth_score > 0.45 else self.COLOR_RED)
        df_tag = " [OPTIMAL]" if auth_score > 0.60 else " [SUSPICIOUS]"
        cv2.putText(frame, f"Authenticity: {int(auth_score * 100)}%{df_tag}", (x1 + 14, cur_y), cv2.FONT_HERSHEY_SIMPLEX, 0.40, df_col, 1)
        cur_y += 22

        # 4. MATHEMATICAL VECTOR GRAPHS (LIGHTWEIGHT CPU-EFFICIENT)
        cv2.putText(frame, "[ VECTOR METRICS (3 GRAPHS) ]", (x1 + 14, cur_y), cv2.FONT_HERSHEY_SIMPLEX, 0.38, self.COLOR_CYAN, 1)
        cur_y += 16

        # Graph 1: 3D Spatial Parallax (Depth Vector)
        p_val = face_data.get("depth_parallax", 0.0)
        self.history_parallax.append(p_val)
        if len(self.history_parallax) > 35:
            self.history_parallax.pop(0)
        
        is_p_low = (p_val < 0.035 and abs(yaw) > 6.0)
        p_col = self.COLOR_RED if is_p_low else self.COLOR_GREEN
        p_label = f"1. Spatial Parallax: {p_val:.2f}" + (" [LOW - 2D SPOOF]" if is_p_low else "")
        cv2.putText(frame, p_label, (x1 + 14, cur_y), cv2.FONT_HERSHEY_SIMPLEX, 0.34, p_col, 1)
        cur_y += 4
        self._draw_mini_sparkline(frame, x1 + 14, cur_y, 230, 14, self.history_parallax, 0.0, 0.8, p_col)
        cur_y += 20

        # Graph 2: Micro-Jitter (Biological Noise Vector)
        j_val = face_data.get("tremor_variance", 0.0)
        self.history_jitter.append(j_val)
        if len(self.history_jitter) > 35:
            self.history_jitter.pop(0)

        is_j_low = (j_val < 0.00010 and len(self.history_jitter) >= 10)
        j_col = self.COLOR_RED if is_j_low else self.COLOR_CYAN
        j_label = f"2. Micro-Jitter: {j_val:.6f}" + (" [LOW - PHOTO SPOOF]" if is_j_low else "")
        cv2.putText(frame, j_label, (x1 + 14, cur_y), cv2.FONT_HERSHEY_SIMPLEX, 0.34, j_col, 1)
        cur_y += 4
        self._draw_mini_sparkline(frame, x1 + 14, cur_y, 230, 14, self.history_jitter, 0.0, 0.005, j_col)
        cur_y += 20

        # Graph 3: Cognitive Latency (Reaction Vector)
        lat_val = face_data.get("cognitive_latency_ms", 0)
        self.history_latency.append(lat_val)
        if len(self.history_latency) > 35:
            self.history_latency.pop(0)
        
        lat_label = f"3. Cognitive Latency: {int(lat_val)} ms"
        cv2.putText(frame, lat_label, (x1 + 14, cur_y), cv2.FONT_HERSHEY_SIMPLEX, 0.34, self.COLOR_WHITE, 1)
        cur_y += 4
        self._draw_mini_sparkline(frame, x1 + 14, cur_y, 230, 14, self.history_latency, 0.0, 1500.0, self.COLOR_AMBER)
        cur_y += 16
        cur_y += 20

    def _draw_mini_sparkline(self, frame, x, y, w, h, values, min_val, max_val, color):
        cv2.rectangle(frame, (x, y), (x + w, y + h), (22, 22, 28), -1)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (45, 45, 55), 1)
        if len(values) < 2:
            return
        n = len(values)
        pts = []
        range_v = max(1e-6, max_val - min_val)
        for i, v in enumerate(values):
            norm_v = np.clip((v - min_val) / range_v, 0.0, 1.0)
            px = int(x + (i / (n - 1)) * w)
            py = int(y + h - norm_v * (h - 2) - 1)
            pts.append((px, py))
        for i in range(len(pts) - 1):
            cv2.line(frame, pts[i], pts[i + 1], color, 1, cv2.LINE_AA)

    def draw_face_landmarks(self, frame, landmarks):
        if not landmarks:
            return
        h, w = frame.shape[:2]

        # Key points to highlight
        # Eyes
        for idx in [33, 133, 160, 144, 158, 153, 362, 263, 385, 380, 387, 373]:
            x = int(landmarks[idx].x * w)
            y = int(landmarks[idx].y * h)
            cv2.circle(frame, (x, y), 2, self.COLOR_CYAN, -1)

        # Nose tip
        nx = int(landmarks[1].x * w)
        ny = int(landmarks[1].y * h)
        cv2.circle(frame, (nx, ny), 4, self.COLOR_RED, -1)

        # Mouth corners
        for idx in [61, 291, 13, 14]:
            x = int(landmarks[idx].x * w)
            y = int(landmarks[idx].y * h)
            cv2.circle(frame, (x, y), 3, self.COLOR_NEON_PINK, -1)

    def draw_hand_landmarks(self, frame, landmarks, palm_pt, start_palm):
        if not landmarks:
            return
        h, w = frame.shape[:2]

        # Skeleton connections
        connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),        # Thumb
            (0, 5), (5, 6), (6, 7), (7, 8),        # Index
            (5, 9), (9, 10), (10, 11), (11, 12),   # Middle
            (9, 13), (13, 14), (14, 15), (15, 16), # Ring
            (13, 17), (17, 18), (18, 19), (19, 20), (0, 17) # Pinky & Base
        ]

        for p1_id, p2_id in connections:
            x1, y1 = int(landmarks[p1_id].x * w), int(landmarks[p1_id].y * h)
            x2, y2 = int(landmarks[p2_id].x * w), int(landmarks[p2_id].y * h)
            cv2.line(frame, (x1, y1), (x2, y2), (0, 200, 100), 1)

        for lm in landmarks:
            x, y = int(lm.x * w), int(lm.y * h)
            cv2.circle(frame, (x, y), 3, self.COLOR_GREEN, -1)

        # Palm center & vector arrow
        if palm_pt:
            px, py = int(palm_pt[0] * w), int(palm_pt[1] * h)
            cv2.circle(frame, (px, py), 7, self.COLOR_RED, -1)
            if start_palm:
                sx, sy = int(start_palm[0] * w), int(start_palm[1] * h)
                cv2.circle(frame, (sx, sy), 5, self.COLOR_CYAN, 2)
                cv2.arrowedLine(frame, (sx, sy), (px, py), self.COLOR_CYAN, 2, tipLength=0.3)

    def draw_final_verdict(self, frame, verdict_data):
        h, w = frame.shape[:2]
        
        # Dark dim background overlay
        dim = np.zeros_like(frame)
        cv2.addWeighted(frame, 0.25, dim, 0.75, 0, frame)

        # Center card
        cw, ch = 680, 420
        cx1 = (w - cw) // 2
        cy1 = (h - ch) // 2
        cx2 = cx1 + cw
        cy2 = cy1 + ch

        cv2.rectangle(frame, (cx1, cy1), (cx2, cy2), (24, 24, 30), -1)
        
        verdict = verdict_data.get("verdict", "UNKNOWN")
        score = verdict_data.get("final_score", 0.0)
        confidence = verdict_data.get("confidence_level", "")
        session_id = verdict_data.get("session_id", "")
        sub_scores = verdict_data.get("sub_scores", {})

        if verdict == "VERIFIED_HUMAN":
            v_col = self.COLOR_GREEN
            v_title = "HUMAN VERIFIED (AUTHENTIC)"
        elif verdict == "SUSPICIOUS":
            v_col = self.COLOR_AMBER
            v_title = "SUSPICIOUS ACTIVITY FLAGGED"
        else:
            v_col = self.COLOR_RED
            v_title = "VERIFICATION FAILED (SPOOF DETECTED)"

        self.draw_rounded_rect(frame, (cx1, cy1), (cx2, cy2), v_col, thickness=2, r=14)

        # Header
        cv2.putText(frame, "TRUSTLAYER AUDIT RESULT", (cx1 + 30, cy1 + 45), cv2.FONT_HERSHEY_SIMPLEX, 0.55, self.COLOR_CYAN, 1)
        cv2.putText(frame, f"SESSION #{session_id}", (cx2 - 180, cy1 + 45), cv2.FONT_HERSHEY_SIMPLEX, 0.45, self.COLOR_GRAY, 1)
        cv2.line(frame, (cx1 + 30, cy1 + 60), (cx2 - 30, cy1 + 60), (45, 45, 55), 1)

        # Big verdict title
        cv2.putText(frame, v_title, (cx1 + 30, cy1 + 105), cv2.FONT_HERSHEY_SIMPLEX, 0.85, v_col, 2)
        cv2.putText(frame, f"Human Verification Score: {score}%", (cx1 + 30, cy1 + 145), cv2.FONT_HERSHEY_SIMPLEX, 0.75, self.COLOR_WHITE, 2)
        cv2.putText(frame, f"Confidence: {confidence}", (cx1 + 30, cy1 + 175), cv2.FONT_HERSHEY_SIMPLEX, 0.45, self.COLOR_GRAY, 1)

        # Metric cards
        sub_items = [
            ("Face Liveness", f"{sub_scores.get('face_liveness', 0)}%"),
            ("Challenge Acc", f"{sub_scores.get('challenge_response', 0)}%"),
            ("Biomechanics", f"{sub_scores.get('hand_biomechanics', 0)}%"),
            ("Deepfake Sec", f"{sub_scores.get('anti_deepfake', 0)}%"),
            ("2/3 Power Law", f"{sub_scores.get('kinematic_power_law', 0)}%"),
        ]
        for i, (lbl, val) in enumerate(sub_items):
            bx = cx1 + 30 + (i % 4) * 155
            by = cy1 + 205 + (i // 4) * 80
            cv2.rectangle(frame, (bx, by), (bx + 145, by + 70), (35, 35, 42), -1)
            cv2.rectangle(frame, (bx, by), (bx + 145, by + 70), (60, 60, 70), 1)
            cv2.putText(frame, lbl, (bx + 10, by + 24), cv2.FONT_HERSHEY_SIMPLEX, 0.36, self.COLOR_GRAY, 1)
            cv2.putText(frame, val, (bx + 10, by + 55), cv2.FONT_HERSHEY_SIMPLEX, 0.75, self.COLOR_CYAN, 2)

        # Instructions / Hotkeys
        cv2.putText(frame, "PRESS [R] TO RESTART SESSION    |    PRESS [S] TO EXPORT REPORT    |    PRESS [Q] TO QUIT", 
                    (cx1 + 45, cy2 - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.42, self.COLOR_WHITE, 1)

    def draw_footer_controls(self, frame):
        h, w = frame.shape[:2]
        cv2.putText(frame, "[Q] Quit  |  [R] Restart  |  [M] Switch Mode (Standard/Live)  |  [S] Save Report", (20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.42, self.COLOR_GRAY, 1)
