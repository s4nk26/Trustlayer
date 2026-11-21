"""
Face Liveness & Biometric Verification Module (Calibrated)
TrustLayer: Human Verification for the AI Era
Zeal College of Engineering & Research, Pune-41
"""

import math
import time
import numpy as np
import cv2
import mediapipe as mp


class FaceLivenessDetector:
    def __init__(self, model_path="face_landmarker.task"):
        self.model_path = model_path
        
        # Initialize MediaPipe Face Landmarker
        face_options = mp.tasks.vision.FaceLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=self.model_path),
            running_mode=mp.tasks.vision.RunningMode.IMAGE,
            num_faces=1,
            output_face_blendshapes=True,
            output_facial_transformation_matrixes=True
        )
        self.landmarker = mp.tasks.vision.FaceLandmarker.create_from_options(face_options)
        
        # Eye Aspect Ratio (EAR) Thresholds & State
        self.EAR_THRESHOLD = 0.22
        self.EAR_CONSEC_FRAMES = 1
        self.blink_frame_counter = 0
        self.total_blinks = 0
        self.blink_history = []
        self.blink_durations = []
        self.blink_start_time = None
        
        # Smile Detection
        self.SMILE_RATIO_THRESHOLD = 0.47
        self.baseline_mouth_ratio = None
        self.is_smiling = False
        self.smile_intensity = 0.0
        
        # Head Pose Thresholds (Degrees)
        self.YAW_LEFT_THRESH = -5.0
        self.YAW_RIGHT_THRESH = 5.0
        self.PITCH_UP_THRESH = -5.0
        self.PITCH_DOWN_THRESH = 5.0
        
        # Micro-movement & Tremor Tracking (Mathematical Vector System)
        self.nose_positions = []
        self.displacement_history = []
        self.tremor_variance = 0.000000
        self.depth_parallax = 0.00
        self.micro_movement_score = 0.95
        self.max_history = 40
        
        # Generic 3D model points for PnP
        self.model_points_3d = np.array([
            (0.0, 0.0, 0.0),             # Nose tip
            (0.0, -330.0, -65.0),        # Chin
            (-225.0, 170.0, -135.0),     # Left eye left corner
            (225.0, 170.0, -135.0),      # Right eye right corner
            (-150.0, -150.0, -125.0),    # Left Mouth corner
            (150.0, -150.0, -125.0)      # Right mouth corner
        ], dtype=np.float64)

    def _euclidean_dist(self, p1, p2, width, height):
        return math.hypot((p1.x - p2.x) * width, (p1.y - p2.y) * height)

    def calculate_ear(self, landmarks, width, height):
        """
        Calculate Eye Aspect Ratio (EAR) for both eyes.
        """
        l_p1, l_p4 = landmarks[33], landmarks[133]
        l_p2, l_p6 = landmarks[160], landmarks[144]
        l_p3, l_p5 = landmarks[158], landmarks[153]

        l_v1 = self._euclidean_dist(l_p2, l_p6, width, height)
        l_v2 = self._euclidean_dist(l_p3, l_p5, width, height)
        l_h = self._euclidean_dist(l_p1, l_p4, width, height)
        left_ear = (l_v1 + l_v2) / (2.0 * max(l_h, 1e-5))

        r_p1, r_p4 = landmarks[362], landmarks[263]
        r_p2, r_p6 = landmarks[385], landmarks[380]
        r_p3, r_p5 = landmarks[387], landmarks[373]

        r_v1 = self._euclidean_dist(r_p2, r_p6, width, height)
        r_v2 = self._euclidean_dist(r_p3, r_p5, width, height)
        r_h = self._euclidean_dist(r_p1, r_p4, width, height)
        right_ear = (r_v1 + r_v2) / (2.0 * max(r_h, 1e-5))

        avg_ear = (left_ear + right_ear) / 2.0
        return left_ear, right_ear, avg_ear

    def update_blink_detection(self, avg_ear):
        """
        Tracks eye closures and natural blink cycles.
        """
        now = time.time()
        new_blink = False
        is_closed = avg_ear < self.EAR_THRESHOLD

        if is_closed:
            if self.blink_frame_counter == 0:
                self.blink_start_time = now
            self.blink_frame_counter += 1
        else:
            if self.blink_frame_counter >= self.EAR_CONSEC_FRAMES:
                duration = now - (self.blink_start_time if self.blink_start_time else now)
                if 0.04 <= duration <= 1.2:
                    self.total_blinks += 1
                    self.blink_history.append(now)
                    self.blink_durations.append(duration)
                    new_blink = True
            self.blink_frame_counter = 0
            self.blink_start_time = None

        return is_closed, new_blink, self.total_blinks

    def calculate_smile(self, landmarks, width, height):
        """
        Calculates smile metric based on lip width vs face width.
        """
        m_left = landmarks[61]
        m_right = landmarks[291]
        mouth_width = self._euclidean_dist(m_left, m_right, width, height)

        eye_left = landmarks[33]
        eye_right = landmarks[263]
        face_width = self._euclidean_dist(eye_left, eye_right, width, height)

        smile_ratio = mouth_width / max(face_width, 1e-5)
        
        if self.baseline_mouth_ratio is None:
            self.baseline_mouth_ratio = smile_ratio
        else:
            if smile_ratio < self.baseline_mouth_ratio * 1.10:
                self.baseline_mouth_ratio = 0.96 * self.baseline_mouth_ratio + 0.04 * smile_ratio

        diff = smile_ratio - self.baseline_mouth_ratio
        norm_intensity = diff / 0.06
        self.smile_intensity = max(0.0, min(1.0, norm_intensity))
        self.is_smiling = smile_ratio > (self.baseline_mouth_ratio * 1.12) or smile_ratio > self.SMILE_RATIO_THRESHOLD

        return self.is_smiling, self.smile_intensity, smile_ratio

    def estimate_head_pose(self, face_result, landmarks, width, height):
        """
        Computes (yaw, pitch, roll) in degrees.
        """
        if face_result.facial_transformation_matrixes:
            try:
                matrix = face_result.facial_transformation_matrixes[0]
                r00, r10, r20 = matrix[0][0], matrix[1][0], matrix[2][0]
                r21, r22 = matrix[2][1], matrix[2][2]

                yaw = math.degrees(math.atan2(-r20, math.sqrt(r00 * r00 + r10 * r10)))
                pitch = math.degrees(math.atan2(r21, r22))
                roll = math.degrees(math.atan2(r10, r00))
                return yaw, pitch, roll
            except Exception:
                pass

        try:
            image_points = np.array([
                (landmarks[1].x * width, landmarks[1].y * height),     # Nose tip
                (landmarks[152].x * width, landmarks[152].y * height), # Chin
                (landmarks[33].x * width, landmarks[33].y * height),   # Left eye corner
                (landmarks[263].x * width, landmarks[263].y * height), # Right eye corner
                (landmarks[61].x * width, landmarks[61].y * height),   # Left mouth
                (landmarks[291].x * width, landmarks[291].y * height)  # Right mouth
            ], dtype=np.float64)

            focal_length = width
            center = (width / 2, height / 2)
            camera_matrix = np.array([
                [focal_length, 0, center[0]],
                [0, focal_length, center[1]],
                [0, 0, 1]
            ], dtype=np.float64)
            dist_coeffs = np.zeros((4, 1))

            success, rot_vec, trans_vec = cv2.solvePnP(
                self.model_points_3d, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE
            )

            if success:
                rmat, _ = cv2.Rodrigues(rot_vec)
                angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)
                pitch, yaw, roll = angles[0], angles[1], angles[2]
                return yaw, pitch, roll
        except Exception:
            pass

        return 0.0, 0.0, 0.0

    def check_micro_movements(self, nose_landmark, width, height):
        nx, ny = nose_landmark.x, nose_landmark.y
        self.nose_positions.append((nx, ny, time.time()))
        if len(self.nose_positions) > self.max_history:
            self.nose_positions.pop(0)

        if len(self.nose_positions) >= 2:
            dx = self.nose_positions[-1][0] - self.nose_positions[-2][0]
            dy = self.nose_positions[-1][1] - self.nose_positions[-2][1]
            disp = math.hypot(dx, dy)
            self.displacement_history.append(disp)
            if len(self.displacement_history) > 25:
                self.displacement_history.pop(0)

            # Mathematical vector standard deviation (Biological Tremor Noise)
            if len(self.displacement_history) >= 5:
                self.tremor_variance = float(np.std(self.displacement_history))
            else:
                self.tremor_variance = 0.000000

        # Heuristic scoring based on biological vector variance
        if len(self.displacement_history) >= 10:
            if 0.00010 <= self.tremor_variance <= 0.025:
                self.micro_movement_score = 0.95
            elif self.tremor_variance < 0.00008:
                self.micro_movement_score = 0.40  # Static printed photo / frozen replay
            else:
                self.micro_movement_score = 0.85
        else:
            self.micro_movement_score = 0.95

        return self.micro_movement_score

    def process_frame(self, rgb_frame):
        height, width = rgb_frame.shape[:2]
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        detection_result = self.landmarker.detect(mp_image)

        if not detection_result.face_landmarks:
            return {
                "detected": False,
                "landmarks": None,
                "yaw": 0.0, "pitch": 0.0, "roll": 0.0,
                "turn_ratio": 0.5,
                "depth_parallax": 0.00,
                "tremor_variance": 0.000000,
                "ear": 0.0, "is_eye_closed": False, "total_blinks": self.total_blinks,
                "is_smiling": False, "smile_intensity": 0.0,
                "micro_movement_score": self.micro_movement_score,
                "face_box": None
            }

        landmarks = detection_result.face_landmarks[0]

        # 1. EAR & Blink
        left_ear, right_ear, avg_ear = self.calculate_ear(landmarks, width, height)
        is_closed, new_blink, blinks = self.update_blink_detection(avg_ear)

        # 2. Smile
        is_smiling, smile_intensity, smile_ratio = self.calculate_smile(landmarks, width, height)

        # 3. Head Pose & Turn Ratio
        yaw, pitch, roll = self.estimate_head_pose(detection_result, landmarks, width, height)
        nx = landmarks[1].x
        ny = landmarks[1].y
        lx = landmarks[33].x
        rx = landmarks[263].x
        eye_w = abs(rx - lx)
        turn_ratio = (nx - min(lx, rx)) / max(eye_w, 1e-5)

        # Mathematical Vector: 3D Spatial Parallax (Nose vector relative to ocular midpoint)
        eye_mid_x = (lx + rx) / 2.0
        eye_mid_y = (landmarks[33].y + landmarks[263].y) / 2.0
        v_parallax = math.hypot(nx - eye_mid_x, ny - eye_mid_y)
        self.depth_parallax = round(float(v_parallax / max(eye_w, 1e-4)), 3)

        # 4. Micro-movements & Vector Tremor Variance
        micro_score = self.check_micro_movements(landmarks[1], width, height)

        # 5. Face Bounding Box
        xs = [lm.x * width for lm in landmarks]
        ys = [lm.y * height for lm in landmarks]
        x_min, x_max = max(0, int(min(xs))), min(width, int(max(xs)))
        y_min, y_max = max(0, int(min(ys))), min(height, int(max(ys)))
        face_box = (x_min, y_min, x_max - x_min, y_max - y_min)

        return {
            "detected": True,
            "landmarks": landmarks,
            "yaw": yaw,
            "pitch": pitch,
            "roll": roll,
            "turn_ratio": turn_ratio,
            "depth_parallax": self.depth_parallax,
            "tremor_variance": self.tremor_variance,
            "ear": avg_ear,
            "left_ear": left_ear,
            "right_ear": right_ear,
            "is_eye_closed": is_closed,
            "new_blink": new_blink,
            "total_blinks": blinks,
            "is_smiling": is_smiling,
            "smile_intensity": smile_intensity,
            "smile_ratio": smile_ratio,
            "micro_movement_score": micro_score,
            "face_box": face_box
        }

    def reset_counters(self):
        self.total_blinks = 0
        self.blink_frame_counter = 0
        self.blink_history = []
        self.blink_durations = []
        self.nose_positions = []
        self.baseline_mouth_ratio = None

    def close(self):
        self.landmarker.close()
