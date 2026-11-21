"""
Decision Engine & Multi-Factor Scoring Module (Calibrated)
TrustLayer: Human Verification for the AI Era
Zeal College of Engineering & Research, Pune-41
"""

import time
import uuid


class VerificationScoringEngine:
    def __init__(self):
        self.session_id = str(uuid.uuid4())[:8].upper()
        self.start_time = time.time()
        
        # Sub-scores (0.0 to 1.0)
        self.face_liveness_score = 0.0
        self.challenge_score = 0.0
        self.biomechanics_score = 0.0
        self.anti_deepfake_score = 0.0
        
        # Final weighted score (0 to 100)
        self.final_score = 0.0
        self.verdict = "IN_PROGRESS"
        self.confidence_level = "PENDING"
        
        # Logs
        self.completed_challenges = []
        self.anomaly_flags = []

    def record_challenge_completion(self, challenge_name, challenge_type, time_taken, accuracy=1.0):
        entry = {
            "name": challenge_name,
            "type": challenge_type,
            "time_taken_sec": round(time_taken, 2),
            "accuracy": round(accuracy, 2),
            "timestamp": time.strftime("%H:%M:%S")
        }
        self.completed_challenges.append(entry)

    def add_anomaly(self, flag_name):
        if flag_name not in self.anomaly_flags:
            self.anomaly_flags.append(flag_name)

    def compute_final_verdict(self, face_metrics, hand_metrics, deepfake_metrics, total_challenges_req=3, kinematic_metrics=None):
        """
        Fuses all parallel verification modules into a calibrated Human Verification Score (0-100%).
        
        Weights:
        - Challenge-Response (Accuracy & Speed): 35%
        - Face Liveness (Blink, EAR, Micro-movement): 22%
        - Hand Biomechanics (Kinematic naturalness + Power Law): 18%
        - Deepfake / Anti-Replay Artifacts: 13%
        - Kinematic Two-Thirds Power Law + Asymmetry (biomechanical engine): 12%
        """
        # 1. Challenge-Response Score (0.0 - 1.0)
        num_completed = len(self.completed_challenges)
        completion_ratio = min(1.0, num_completed / max(1, total_challenges_req))
        
        speed_multiplier = 1.0
        if self.completed_challenges:
            avg_time = sum(c["time_taken_sec"] for c in self.completed_challenges) / len(self.completed_challenges)
            if avg_time <= 6.0:
                speed_multiplier = 1.0
            else:
                speed_multiplier = max(0.85, 1.0 - ((avg_time - 6.0) * 0.02))

        self.challenge_score = completion_ratio * speed_multiplier

        # 2. Face Liveness Score (0.0 - 1.0)
        blinks = face_metrics.get("total_blinks", 0)
        micro_score = face_metrics.get("micro_movement_score", 0.95)
        blink_score = 1.0 if blinks >= 1 else 0.90
        self.face_liveness_score = (blink_score * 0.5) + (micro_score * 0.5)

        # 3. Hand Biomechanics Score (0.0 - 1.0)
        self.biomechanics_score = hand_metrics.get("bio_score", 0.95)

        # 4. Deepfake & Screen Replay Score (0.0 - 1.0)
        self.anti_deepfake_score = deepfake_metrics.get("authenticity_score", 0.95)

        # 5. Kinematic Two-Thirds Power Law + Biological Asymmetry Score (Bug fix: was ignored before)
        kinematic_score = 0.85  # Healthy default
        if kinematic_metrics:
            power_law = kinematic_metrics.get("power_law", {})
            asym = kinematic_metrics.get("asymmetry", {})
            pl_score = power_law.get("power_law_score", 0.85)
            is_bio = power_law.get("is_biological", True)
            is_human_asym = asym.get("is_asymmetric_human", True)
            kin_liveness = kinematic_metrics.get("kinematic_liveness_score", 0.85)
            # Biological motor motion score fusion
            kinematic_score = (pl_score * 0.40 + kin_liveness * 0.40 + (0.90 if is_human_asym else 0.50) * 0.20)
            if not is_bio:
                kinematic_score *= 0.60  # Heavy penalty for non-biological movement pattern

        # Weighted raw calculation (re-distributed weights to include kinematic engine)
        raw_weighted = (
            (0.35 * self.challenge_score) +
            (0.22 * self.face_liveness_score) +
            (0.18 * self.biomechanics_score) +
            (0.13 * self.anti_deepfake_score) +
            (0.12 * kinematic_score)
        ) * 100.0

        # Penalties only for serious persistent violations
        penalty = 0.0
        if "CHALLENGE_TIMEOUT_EXPIRED" in self.anomaly_flags:
            penalty += 10.0
        if "SCREEN_MOIRE_GRID_DETECTED" in self.anomaly_flags:
            penalty += 15.0

        self.final_score = max(5.0, min(99.0, round(raw_weighted - penalty, 1)))

        # Classification
        if self.final_score >= 70.0 and self.challenge_score >= 0.75:
            self.verdict = "VERIFIED_HUMAN"
            self.confidence_level = "HIGH CONFIDENCE (GENUINE LIVE HUMAN)"
        elif self.final_score >= 45.0:
            self.verdict = "SUSPICIOUS"
            self.confidence_level = "MEDIUM CONFIDENCE (MANUAL REVIEW)"
        else:
            self.verdict = "VERIFICATION_FAILED"
            self.confidence_level = "LOW CONFIDENCE (SPOOF / DEEPFAKE DETECTED)"

        return {
            "session_id": self.session_id,
            "final_score": self.final_score,
            "verdict": self.verdict,
            "confidence_level": self.confidence_level,
            "sub_scores": {
                "challenge_response": round(self.challenge_score * 100, 1),
                "face_liveness": round(self.face_liveness_score * 100, 1),
                "hand_biomechanics": round(self.biomechanics_score * 100, 1),
                "anti_deepfake": round(self.anti_deepfake_score * 100, 1),
                "kinematic_power_law": round(kinematic_score * 100, 1)
            },
            "completed_challenges": self.completed_challenges,
            "anomaly_flags": self.anomaly_flags,
            "duration_sec": round(time.time() - self.start_time, 2)
        }

    def reset(self):
        self.session_id = str(uuid.uuid4())[:8].upper()
        self.start_time = time.time()
        self.face_liveness_score = 0.0
        self.challenge_score = 0.0
        self.biomechanics_score = 0.0
        self.anti_deepfake_score = 0.0
        self.final_score = 0.0
        self.verdict = "IN_PROGRESS"
        self.confidence_level = "PENDING"
        self.completed_challenges = []
        self.anomaly_flags = []
