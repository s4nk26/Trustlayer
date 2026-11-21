"""
Hand Biomechanics & Kinematic Verification Module (Refined & Smooth)
TrustLayer: Human Verification for the AI Era
Zeal College of Engineering & Research, Pune-41

Fixes hand movement detection for LEFT, RIGHT, UP, and DOWN:
- Eliminates velocity-drop lockout when holding hand at target position
- Responsive displacement threshold (0.06 normalized screen width)
- Smooth hold validation at destination
"""

import math
import time
import numpy as np
import cv2
import mediapipe as mp


class HandBiomechanicsDetector:
    def __init__(self, model_path="hand_landmarker.task"):
        self.model_path = model_path
        
        hand_options = mp.tasks.vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=self.model_path),
            running_mode=mp.tasks.vision.RunningMode.IMAGE,
            num_hands=1,
            min_hand_detection_confidence=0.35,
            min_hand_presence_confidence=0.35,
            min_tracking_confidence=0.35
        )
        self.landmarker = mp.tasks.vision.HandLandmarker.create_from_options(hand_options)
        
        # Kinematic state
        self.start_palm = None
        self.previous_palm = None
        self.previous_time = None
        self.velocity = 0.0
        self.previous_velocity = 0.0
        self.acceleration = 0.0
        self.previous_acceleration = 0.0
        self.jerk = 0.0
        
        self.trajectory = []
        self.max_trajectory_length = 40
        
        # Calibrated Responsive Thresholds
        self.DISPLACEMENT_THRESH = 0.06  # 6% of screen width displacement
        self.HOLD_TIME = 0.25            # Fast, smooth 250ms confirmation
        self.hold_start_time = None
        # target_reached removed: was set but never used (bug fix)

    def calculate_palm_center(self, hand_landmarks):
        """
        Centroid of the palm using wrist and MCP joints (0, 5, 9, 13, 17).
        """
        palm_ids = [0, 5, 9, 13, 17]
        cx = sum(hand_landmarks[i].x for i in palm_ids) / len(palm_ids)
        cy = sum(hand_landmarks[i].y for i in palm_ids) / len(palm_ids)
        return cx, cy

    def detect_finger_extension(self, hand_landmarks):
        """
        Calculates extension state for all 5 fingers.
        """
        thumb_extended = math.hypot(hand_landmarks[4].x - hand_landmarks[9].x, hand_landmarks[4].y - hand_landmarks[9].y) > 0.10
        index_extended = hand_landmarks[8].y < hand_landmarks[6].y
        middle_extended = hand_landmarks[12].y < hand_landmarks[10].y
        ring_extended = hand_landmarks[16].y < hand_landmarks[14].y
        pinky_extended = hand_landmarks[20].y < hand_landmarks[18].y

        extended_count = sum([thumb_extended, index_extended, middle_extended, ring_extended, pinky_extended])
        
        pinch_dist = math.hypot(hand_landmarks[4].x - hand_landmarks[8].x, hand_landmarks[4].y - hand_landmarks[8].y)
        is_pinch = pinch_dist < 0.06

        is_open_palm = extended_count >= 4
        is_fist = extended_count <= 1 and not is_pinch

        return {
            "thumb": thumb_extended,
            "index": index_extended,
            "middle": middle_extended,
            "ring": ring_extended,
            "pinky": pinky_extended,
            "extended_count": extended_count,
            "is_open_palm": is_open_palm,
            "is_fist": is_fist,
            "is_pinch": is_pinch
        }

    def update_kinematics(self, palm):
        """
        Tracks displacement from initial anchor, velocity, and acceleration.
        """
        now = time.time()
        if self.start_palm is None:
            self.start_palm = palm
            self.previous_palm = palm
            self.previous_time = now
            self.velocity = 0.0
            self.acceleration = 0.0
            self.jerk = 0.0
            return 0.0, 0.0, 0.0, 0.0

        dt = now - self.previous_time
        if dt <= 0.0001:
            dt = 0.001

        dx = palm[0] - self.previous_palm[0]
        dy = palm[1] - self.previous_palm[1]
        dist = math.hypot(dx, dy)

        instant_velocity = dist / dt
        self.velocity = 0.6 * instant_velocity + 0.4 * self.previous_velocity

        instant_accel = (self.velocity - self.previous_velocity) / dt
        self.acceleration = 0.5 * instant_accel + 0.5 * self.previous_acceleration
        self.jerk = (self.acceleration - self.previous_acceleration) / dt

        # Total displacement relative to starting anchor
        total_dx = palm[0] - self.start_palm[0]
        total_dy = palm[1] - self.start_palm[1]

        self.trajectory.append((palm[0], palm[1], now, self.velocity, self.acceleration))
        if len(self.trajectory) > self.max_trajectory_length:
            self.trajectory.pop(0)

        self.previous_palm = palm
        self.previous_time = now
        self.previous_velocity = self.velocity
        self.previous_acceleration = self.acceleration

        return total_dx, total_dy, self.velocity, self.acceleration

    def check_biomechanical_authenticity(self):
        if len(self.trajectory) < 5:
            return 0.95

        accels = [p[4] for p in self.trajectory]
        max_jerk = max([abs(a) for a in accels]) if accels else 0.0

        # Bug fix: 140 norm units was too tight — real humans doing fast gestures
        # regularly hit 180-250. Only flag truly robotic jerk spikes > 350.
        if max_jerk > 350.0:
            return 0.50
        elif max_jerk > 220.0:
            return 0.78  # Mildly suspicious — fast but possibly real
        else:
            return 0.96

    def check_challenge_movement(self, challenge, total_dx, total_dy, finger_state):
        """
        Robust directional verification for hand gestures.
        Allows stationary hold once target displacement is achieved.
        """
        matched = False
        
        # 1. MOVE HAND RIGHT
        if challenge == "RIGHT":
            # X displacement must be positive and dominate Y displacement
            if total_dx >= self.DISPLACEMENT_THRESH and abs(total_dx) > (abs(total_dy) * 0.75):
                matched = True

        # 2. MOVE HAND LEFT
        elif challenge == "LEFT":
            # X displacement must be negative and dominate Y displacement
            if total_dx <= -self.DISPLACEMENT_THRESH and abs(total_dx) > (abs(total_dy) * 0.75):
                matched = True

        # 3. MOVE HAND UP
        elif challenge == "UP":
            # Y displacement must be negative (upwards in image coordinates)
            if total_dy <= -self.DISPLACEMENT_THRESH and abs(total_dy) > (abs(total_dx) * 0.75):
                matched = True

        # 4. MOVE HAND DOWN
        elif challenge == "DOWN":
            # Y displacement must be positive (downwards in image coordinates)
            if total_dy >= self.DISPLACEMENT_THRESH and abs(total_dy) > (abs(total_dx) * 0.75):
                matched = True

        # 5. OPEN PALM GESTURE
        elif challenge == "OPEN_PALM":
            matched = finger_state.get("is_open_palm", False)

        # 6. FIST GESTURE
        elif challenge == "FIST":
            matched = finger_state.get("is_fist", False)

        return matched

    def process_frame(self, rgb_frame, current_challenge=None):
        height, width = rgb_frame.shape[:2]
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        detection_result = self.landmarker.detect(mp_image)

        if not detection_result.hand_landmarks:
            return {
                "detected": False,
                "landmarks": None,
                "palm": None,
                "start_palm": self.start_palm,
                "total_dx": 0.0,
                "total_dy": 0.0,
                "velocity": 0.0,
                "acceleration": 0.0,
                "jerk": 0.0,
                "bio_score": 0.95,
                "finger_state": None,
                "challenge_passed": False,
                "displacement_ratio": 0.0
            }

        landmarks = detection_result.hand_landmarks[0]
        palm = self.calculate_palm_center(landmarks)
        total_dx, total_dy, velocity, acceleration = self.update_kinematics(palm)
        finger_state = self.detect_finger_extension(landmarks)
        bio_score = self.check_biomechanical_authenticity()

        challenge_passed = False
        displacement_ratio = 0.0

        if current_challenge:
            matched = self.check_challenge_movement(current_challenge, total_dx, total_dy, finger_state)
            
            # Compute visual displacement progress ratio (0.0 to 1.0)
            if current_challenge == "RIGHT":
                displacement_ratio = max(0.0, min(1.0, total_dx / self.DISPLACEMENT_THRESH))
            elif current_challenge == "LEFT":
                displacement_ratio = max(0.0, min(1.0, -total_dx / self.DISPLACEMENT_THRESH))
            elif current_challenge == "UP":
                displacement_ratio = max(0.0, min(1.0, -total_dy / self.DISPLACEMENT_THRESH))
            elif current_challenge == "DOWN":
                displacement_ratio = max(0.0, min(1.0, total_dy / self.DISPLACEMENT_THRESH))
            elif current_challenge == "OPEN_PALM":
                displacement_ratio = 1.0 if finger_state["is_open_palm"] else 0.0

            if matched:
                if self.hold_start_time is None:
                    self.hold_start_time = time.time()
                held = time.time() - self.hold_start_time
                if held >= self.HOLD_TIME:
                    challenge_passed = True
            else:
                self.hold_start_time = None

        return {
            "detected": True,
            "landmarks": landmarks,
            "palm": palm,
            "start_palm": self.start_palm,
            "total_dx": total_dx,
            "total_dy": total_dy,
            "velocity": velocity,
            "acceleration": acceleration,
            "jerk": self.jerk,
            "bio_score": bio_score,
            "finger_state": finger_state,
            "challenge_passed": challenge_passed,
            "displacement_ratio": displacement_ratio
        }

    def reset_tracking(self):
        """
        Clears previous hand anchor so the new movement is measured fresh.
        """
        self.start_palm = None
        self.previous_palm = None
        self.previous_time = None
        self.velocity = 0.0
        self.previous_velocity = 0.0
        self.acceleration = 0.0
        self.previous_acceleration = 0.0
        self.jerk = 0.0
        self.hold_start_time = None
        self.trajectory = []

    def close(self):
        self.landmarker.close()
