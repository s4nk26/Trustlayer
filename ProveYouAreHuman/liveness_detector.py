"""
=============================================================================
REAL-TIME LIVENESS DETECTION & BIOMETRIC ANALYSIS (STANDALONE)
OpenCV + MediaPipe Vision (Face Landmarker / FaceMesh & Hands)

Features:
1. Eye Blink Detection via Eye Aspect Ratio (EAR) & Live Counter
2. 3D Head Pose Estimation via cv2.solvePnP (Forward, Left, Right, Up, Down)
3. Hand Gesture Detection: Raised Finger Counter (0 to 5)
4. Cyberpunk / Glassmorphism Visual HUD with Live Telemetry & FPS

Requirements:
    pip install opencv-python mediapipe numpy
=============================================================================
"""

import os
import sys
import math
import time
import urllib.request
import cv2
import numpy as np
import mediapipe as mp


# ============================================================================
# 1. MODEL ASSET DOWNLOAD / RESOLUTION HELPER
# ============================================================================

def resolve_or_download_model(filename, url):
    """
    Ensures model asset file exists locally; auto-downloads if missing.
    """
    candidates = [
        filename,
        os.path.join(os.path.dirname(os.path.abspath(__file__)), filename),
        os.path.join(r"C:\Users\User", filename),
        os.path.join(r"C:\Users\User\ProveYouAreHuman", filename)
    ]
    for path in candidates:
        if os.path.exists(path):
            return path

    target_path = os.path.join(os.getcwd(), filename)
    print(f"[*] Model '{filename}' not found locally. Downloading from MediaPipe CDN...")
    try:
        urllib.request.urlretrieve(url, target_path)
        print(f"[+] Download complete: {target_path}")
        return target_path
    except Exception as e:
        print(f"[-] Error downloading model {filename}: {e}")
        return filename


# ============================================================================
# 2. EYE BLINK DETECTOR (EAR STATE MACHINE)
# ============================================================================

class BlinkDetector:
    def __init__(self, ear_threshold=0.22, consec_frames=1):
        self.ear_threshold = ear_threshold
        self.consec_frames = consec_frames
        self.frame_counter = 0
        self.blink_count = 0
        self.is_closed = False
        self.blink_start_time = None
        
        # Landmark indices (MediaPipe Face Mesh 468/478 format)
        # Left Eye: 33 (outer), 133 (inner), 160/144 (top/bot 1), 158/153 (top/bot 2)
        self.LEFT_EYE = [33, 160, 158, 133, 153, 144]
        # Right Eye: 362 (inner), 263 (outer), 385/380 (top/bot 1), 387/373 (top/bot 2)
        self.RIGHT_EYE = [362, 385, 387, 263, 373, 380]

    def _euclidean_dist(self, p1, p2, w, h):
        return math.hypot((p1.x - p2.x) * w, (p1.y - p2.y) * h)

    def calculate_single_ear(self, landmarks, eye_indices, w, h):
        """
        EAR = (||p2 - p6|| + ||p3 - p5||) / (2 * ||p1 - p4||)
        """
        p1 = landmarks[eye_indices[0]]
        p2 = landmarks[eye_indices[1]]
        p3 = landmarks[eye_indices[2]]
        p4 = landmarks[eye_indices[3]]
        p5 = landmarks[eye_indices[4]]
        p6 = landmarks[eye_indices[5]]

        v1 = self._euclidean_dist(p2, p6, w, h)
        v2 = self._euclidean_dist(p3, p5, w, h)
        h_dist = self._euclidean_dist(p1, p4, w, h)

        return (v1 + v2) / (2.0 * max(h_dist, 1e-5))

    def update(self, landmarks, w, h):
        left_ear = self.calculate_single_ear(landmarks, self.LEFT_EYE, w, h)
        right_ear = self.calculate_single_ear(landmarks, self.RIGHT_EYE, w, h)
        avg_ear = (left_ear + right_ear) / 2.0

        now = time.time()
        self.is_closed = avg_ear < self.ear_threshold

        if self.is_closed:
            if self.frame_counter == 0:
                self.blink_start_time = now
            self.frame_counter += 1
        else:
            if self.frame_counter >= self.consec_frames:
                duration = now - (self.blink_start_time if self.blink_start_time else now)
                # Valid biological blink range (50ms - 900ms)
                if 0.04 <= duration <= 1.2:
                    self.blink_count += 1
            self.frame_counter = 0
            self.blink_start_time = None

        return avg_ear, self.is_closed, self.blink_count


# ============================================================================
# 3. 3D HEAD POSE ESTIMATOR (SOLVEPNP)
# ============================================================================

class HeadPoseEstimator:
    def __init__(self):
        # 3D generic facial anthropometric model points in world coordinates
        self.model_points_3d = np.array([
            (0.0, 0.0, 0.0),             # Nose tip (Landmark 1)
            (0.0, -330.0, -65.0),        # Chin (Landmark 152)
            (-225.0, 170.0, -135.0),     # Left eye outer corner (Landmark 33)
            (225.0, 170.0, -135.0),      # Right eye outer corner (Landmark 263)
            (-150.0, -150.0, -125.0),    # Left mouth corner (Landmark 61)
            (150.0, -150.0, -125.0)      # Right mouth corner (Landmark 291)
        ], dtype=np.float64)

        # Key landmark IDs corresponding to 3D model
        self.KEY_LANDMARK_IDS = [1, 152, 33, 263, 61, 291]

        # Pose Classification Thresholds (degrees)
        self.YAW_THRESH = 12.0
        self.PITCH_UP_THRESH = -10.0
        self.PITCH_DOWN_THRESH = 10.0
        self.ROLL_THRESH = 15.0

    def estimate_pose(self, landmarks, w, h):
        """
        Computes (pitch, yaw, roll), orientation label, and nose projection line.
        """
        image_points = np.array([
            (landmarks[idx].x * w, landmarks[idx].y * h) for idx in self.KEY_LANDMARK_IDS
        ], dtype=np.float64)

        # Approximate camera matrix assuming standard FOV
        focal_length = w
        center = (w / 2.0, h / 2.0)
        camera_matrix = np.array([
            [focal_length, 0.0, center[0]],
            [0.0, focal_length, center[1]],
            [0.0, 0.0, 1.0]
        ], dtype=np.float64)
        dist_coeffs = np.zeros((4, 1))

        # Solve Perspective-n-Point
        success, rot_vec, trans_vec = cv2.solvePnP(
            self.model_points_3d, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE
        )

        if not success:
            return 0.0, 0.0, 0.0, "Forward", None, None

        # Rotation matrix & Euler angles
        rot_mat, _ = cv2.Rodrigues(rot_vec)
        angles, _, _, _, _, _ = cv2.RQDecomp3x3(rot_mat)
        
        pitch = float(angles[0])
        yaw = float(angles[1])
        roll = float(angles[2])

        # Project 3D vector forward from nose tip for visual 3D pointer
        nose_end_point_3d = np.array([(0.0, 0.0, 1000.0)], dtype=np.float64)
        nose_end_point_2d, _ = cv2.projectPoints(
            nose_end_point_3d, rot_vec, trans_vec, camera_matrix, dist_coeffs
        )
        p1 = (int(image_points[0][0]), int(image_points[0][1]))
        p2 = (int(nose_end_point_2d[0][0][0]), int(nose_end_point_2d[0][0][1]))

        # Classify Orientation
        if yaw < -self.YAW_THRESH:
            orientation = "Left"
        elif yaw > self.YAW_THRESH:
            orientation = "Right"
        elif pitch < self.PITCH_UP_THRESH:
            orientation = "Up"
        elif pitch > self.PITCH_DOWN_THRESH:
            orientation = "Down"
        else:
            orientation = "Forward"

        return pitch, yaw, roll, orientation, p1, p2


# ============================================================================
# 4. HAND GESTURE & FINGER COUNTER
# ============================================================================

class HandGestureDetector:
    def __init__(self):
        # Finger Tip & PIP joint indices
        # Thumb: Tip 4, IP 3, MCP 2
        # Index: Tip 8, PIP 6
        # Middle: Tip 12, PIP 10
        # Ring: Tip 16, PIP 14
        # Pinky: Tip 20, PIP 18
        self.FINGERS_PIP = [(8, 6), (12, 10), (16, 14), (20, 18)]

    def count_raised_fingers(self, hand_landmarks, w, h):
        """
        Counts raised fingers (0 to 5) and returns individual finger states.
        """
        raised = []

        # 1. Thumb Check (Horizontal/Lateral displacement relative to MCP joint 9 & 2)
        thumb_tip = hand_landmarks[4]
        thumb_ip = hand_landmarks[3]
        index_mcp = hand_landmarks[5]
        
        # Check if thumb tip is extended away from palm center
        thumb_extended = math.hypot(thumb_tip.x - index_mcp.x, thumb_tip.y - index_mcp.y) > 0.12
        raised.append(thumb_extended)

        # 2. 4 Fingers (Index, Middle, Ring, Pinky): Check if Tip is above PIP joint in Y
        for tip_id, pip_id in self.FINGERS_PIP:
            tip = hand_landmarks[tip_id]
            pip = hand_landmarks[pip_id]
            is_raised = tip.y < pip.y
            raised.append(is_raised)

        finger_count = sum(raised)
        return finger_count, {
            "thumb": raised[0],
            "index": raised[1],
            "middle": raised[2],
            "ring": raised[3],
            "pinky": raised[4]
        }


# ============================================================================
# 5. VISUAL HUD & OVERLAY RENDERER
# ============================================================================

class VisualRenderer:
    def __init__(self):
        self.COLOR_BG = (20, 20, 26)
        self.COLOR_PANEL = (30, 30, 38)
        self.COLOR_BORDER = (60, 60, 75)
        self.COLOR_CYAN = (240, 200, 0)
        self.COLOR_GREEN = (80, 230, 100)
        self.COLOR_AMBER = (0, 190, 255)
        self.COLOR_RED = (60, 60, 240)
        self.COLOR_WHITE = (245, 245, 250)
        self.COLOR_GRAY = (140, 140, 150)
        self.COLOR_NEON_PINK = (220, 50, 230)

        # Hand skeleton joints
        self.HAND_CONNECTIONS = [
            (0, 1), (1, 2), (2, 3), (3, 4),        # Thumb
            (0, 5), (5, 6), (6, 7), (7, 8),        # Index
            (5, 9), (9, 10), (10, 11), (11, 12),   # Middle
            (9, 13), (13, 14), (14, 15), (15, 16), # Ring
            (13, 17), (17, 18), (18, 19), (19, 20), (0, 17) # Pinky & Base
        ]

    def draw_face_visuals(self, frame, landmarks, p1, p2):
        h, w = frame.shape[:2]
        xs = [int(lm.x * w) for lm in landmarks]
        ys = [int(lm.y * h) for lm in landmarks]

        # Draw Face Bounding Box
        x_min, x_max = max(0, min(xs) - 15), min(w, max(xs) + 15)
        y_min, y_max = max(0, min(ys) - 25), min(h, max(ys) + 15)
        
        # Bounding box corners
        cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), self.COLOR_CYAN, 1)
        corner_len = 16
        cv2.line(frame, (x_min, y_min), (x_min + corner_len, y_min), self.COLOR_CYAN, 3)
        cv2.line(frame, (x_min, y_min), (x_min, y_min + corner_len), self.COLOR_CYAN, 3)
        cv2.line(frame, (x_max, y_min), (x_max - corner_len, y_min), self.COLOR_CYAN, 3)
        cv2.line(frame, (x_max, y_min), (x_max, y_min + corner_len), self.COLOR_CYAN, 3)
        cv2.line(frame, (x_min, y_max), (x_min + corner_len, y_max), self.COLOR_CYAN, 3)
        cv2.line(frame, (x_min, y_max), (x_min, y_max - corner_len), self.COLOR_CYAN, 3)
        cv2.line(frame, (x_max, y_max), (x_max - corner_len, y_max), self.COLOR_CYAN, 3)
        cv2.line(frame, (x_max, y_max), (x_max, y_max - corner_len), self.COLOR_CYAN, 3)

        # Highlight key landmarks (Eyes, Nose, Lips)
        key_points = [33, 133, 160, 144, 158, 153, 362, 263, 385, 380, 387, 373, 1, 61, 291, 13, 14]
        for idx in key_points:
            cv2.circle(frame, (xs[idx], ys[idx]), 2, self.COLOR_GREEN, -1)

        # 3D Head Pose Direction Vector
        if p1 and p2:
            cv2.arrowedLine(frame, p1, p2, self.COLOR_RED, 2, tipLength=0.25)
            cv2.circle(frame, p1, 4, self.COLOR_RED, -1)

    def draw_hand_visuals(self, frame, hand_landmarks):
        h, w = frame.shape[:2]
        # Draw skeleton lines
        for p1_id, p2_id in self.HAND_CONNECTIONS:
            x1, y1 = int(hand_landmarks[p1_id].x * w), int(hand_landmarks[p1_id].y * h)
            x2, y2 = int(hand_landmarks[p2_id].x * w), int(hand_landmarks[p2_id].y * h)
            cv2.line(frame, (x1, y1), (x2, y2), (0, 220, 120), 2)

        # Draw joints
        for lm in hand_landmarks:
            cx, cy = int(lm.x * w), int(lm.y * h)
            cv2.circle(frame, (cx, cy), 4, self.COLOR_NEON_PINK, -1)
            cv2.circle(frame, (cx, cy), 2, self.COLOR_WHITE, -1)

    def draw_hud(self, frame, fps, ear, is_closed, blink_count, pitch, yaw, roll, orientation, finger_count, hand_detected):
        h, w = frame.shape[:2]

        # Top Header Bar
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 54), (16, 16, 22), -1)
        cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)
        cv2.line(frame, (0, 54), (w, 54), self.COLOR_BORDER, 1)

        cv2.putText(frame, "LIVENESS & BIOMETRIC ANALYZER", (24, 34), cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.COLOR_CYAN, 2)
        cv2.putText(frame, f"FPS: {int(fps)}", (w - 140, 34), cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.COLOR_GREEN, 2)
        cv2.circle(frame, (w - 30, 28), 6, self.COLOR_GREEN, -1)

        # Telemetry HUD Sidebar (Left Side)
        hud_w, hud_h = 320, 280
        x1, y1 = 20, 75
        x2, y2 = x1 + hud_w, y1 + hud_h

        card = frame.copy()
        cv2.rectangle(card, (x1, y1), (x2, y2), self.COLOR_PANEL, -1)
        cv2.addWeighted(card, 0.88, frame, 0.12, 0, frame)
        cv2.rectangle(frame, (x1, y1), (x2, y2), self.COLOR_BORDER, 1)

        cv2.putText(frame, "REAL-TIME BIOMETRIC HUD", (x1 + 16, y1 + 28), cv2.FONT_HERSHEY_SIMPLEX, 0.48, self.COLOR_CYAN, 1)
        cv2.line(frame, (x1 + 16, y1 + 38), (x2 - 16, y1 + 38), self.COLOR_BORDER, 1)

        # 1. Head Pose Entry
        pose_color = self.COLOR_GREEN if orientation == "Forward" else self.COLOR_AMBER
        cv2.putText(frame, f"Head Pose: {orientation.upper()}", (x1 + 16, y1 + 68), cv2.FONT_HERSHEY_SIMPLEX, 0.55, pose_color, 2)
        cv2.putText(frame, f"Yaw: {yaw:+.1f} | Pitch: {pitch:+.1f} | Roll: {roll:+.1f}", (x1 + 16, y1 + 92), cv2.FONT_HERSHEY_SIMPLEX, 0.40, self.COLOR_GRAY, 1)

        # 2. Blink & EAR Entry
        eye_status = "CLOSED" if is_closed else "OPEN"
        eye_col = self.COLOR_AMBER if is_closed else self.COLOR_GREEN
        cv2.putText(frame, f"Blink Count: {blink_count}", (x1 + 16, y1 + 130), cv2.FONT_HERSHEY_SIMPLEX, 0.55, self.COLOR_WHITE, 2)
        cv2.putText(frame, f"EAR: {ear:.3f} [{eye_status}]", (x1 + 16, y1 + 154), cv2.FONT_HERSHEY_SIMPLEX, 0.45, eye_col, 1)
        
        # EAR bar meter
        ear_bar_w = int(min(1.0, ear / 0.40) * 140)
        cv2.rectangle(frame, (x1 + 16, y1 + 164), (x1 + 16 + 140, y1 + 172), (40, 40, 50), -1)
        cv2.rectangle(frame, (x1 + 16, y1 + 164), (x1 + 16 + ear_bar_w, y1 + 172), eye_col, -1)

        # 3. Hand & Finger Counter Entry
        if hand_detected:
            f_col = self.COLOR_GREEN
            f_text = f"Fingers Detected: {finger_count} / 5"
        else:
            f_col = self.COLOR_GRAY
            f_text = "Fingers: No Hand in Frame"

        cv2.putText(frame, f_text, (x1 + 16, y1 + 215), cv2.FONT_HERSHEY_SIMPLEX, 0.52, f_col, 2)
        if hand_detected:
            # Render 5 finger status dots
            for i in range(5):
                dot_col = self.COLOR_GREEN if i < finger_count else (60, 60, 70)
                cv2.circle(frame, (x1 + 22 + (i * 24), y1 + 242), 7, dot_col, -1)
                cv2.putText(frame, str(i + 1), (x1 + 18 + (i * 24), y1 + 246), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 0), 1)

        # Footer
        cv2.putText(frame, "[Q] Quit  |  [R] Reset Blink Counter", (24, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.45, self.COLOR_GRAY, 1)


# ============================================================================
# 6. MAIN APPLICATION CONTROLLER
# ============================================================================

def main():
    print("==================================================================")
    print("      LIVENESS DETECTOR: BLINK + HEAD POSE + HAND GESTURES        ")
    print("==================================================================")

    # Model URLs & Filenames
    FACE_MODEL_NAME = "face_landmarker.task"
    FACE_MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
    HAND_MODEL_NAME = "hand_landmarker.task"
    HAND_MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"

    face_model_path = resolve_or_download_model(FACE_MODEL_NAME, FACE_MODEL_URL)
    hand_model_path = resolve_or_download_model(HAND_MODEL_NAME, HAND_MODEL_URL)

    # Initialize MediaPipe Vision Tasks
    face_options = mp.tasks.vision.FaceLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=face_model_path),
        running_mode=mp.tasks.vision.RunningMode.IMAGE,
        num_faces=1,
        output_facial_transformation_matrixes=True
    )
    face_landmarker = mp.tasks.vision.FaceLandmarker.create_from_options(face_options)

    hand_options = mp.tasks.vision.HandLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=hand_model_path),
        running_mode=mp.tasks.vision.RunningMode.IMAGE,
        num_hands=1
    )
    hand_landmarker = mp.tasks.vision.HandLandmarker.create_from_options(hand_options)

    # Initialize Detection Submodules
    blink_detector = BlinkDetector(ear_threshold=0.22, consec_frames=1)
    pose_estimator = HeadPoseEstimator()
    hand_detector = HandGestureDetector()
    renderer = VisualRenderer()

    # Camera Capture
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not cap.isOpened():
        print("[-] ERROR: Could not open camera at index 0.")
        sys.exit(1)

    print("[+] Camera initialized successfully. Press [Q] to quit.")

    prev_time = time.time()
    fps = 30.0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Mirror for natural interaction
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]

        # Calculate FPS
        curr_time = time.time()
        dt = curr_time - prev_time
        if dt > 0:
            fps = 0.9 * fps + 0.1 * (1.0 / dt)
        prev_time = curr_time

        # RGB for MediaPipe
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        # 1. Run Face & Hand Detection
        face_result = face_landmarker.detect(mp_image)
        hand_result = hand_landmarker.detect(mp_image)

        # Default Telemetry State
        ear = 0.0
        is_closed = False
        pitch, yaw, roll = 0.0, 0.0, 0.0
        orientation = "No Face"
        p1, p2 = None, None

        # 2. Process Face Liveness & Pose
        if face_result.face_landmarks:
            face_landmarks = face_result.face_landmarks[0]
            
            # Eye Blink / EAR
            ear, is_closed, _ = blink_detector.update(face_landmarks, w, h)

            # Head Pose Estimation
            pitch, yaw, roll, orientation, p1, p2 = pose_estimator.estimate_pose(face_landmarks, w, h)

            # Draw visual landmarks and 3D pointer
            renderer.draw_face_visuals(frame, face_landmarks, p1, p2)

        # 3. Process Hand Gesture / Finger Count
        finger_count = 0
        hand_detected = False
        if hand_result.hand_landmarks:
            hand_detected = True
            hand_landmarks = hand_result.hand_landmarks[0]
            finger_count, _ = hand_detector.count_raised_fingers(hand_landmarks, w, h)
            renderer.draw_hand_visuals(frame, hand_landmarks)

        # 4. Render Telemetry HUD
        renderer.draw_hud(
            frame,
            fps=fps,
            ear=ear,
            is_closed=is_closed,
            blink_count=blink_detector.blink_count,
            pitch=pitch,
            yaw=yaw,
            roll=roll,
            orientation=orientation,
            finger_count=finger_count,
            hand_detected=hand_detected
        )

        # Display Window
        cv2.imshow("Real-Time Liveness & Biometric Analyzer", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            blink_detector.blink_count = 0
            print("[*] Blink counter reset.")

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    face_landmarker.close()
    hand_landmarker.close()
    print("[+] Liveness detector terminated cleanly.")


if __name__ == "__main__":
    main()
