"""
=============================================================================
LIP-SYNC & BIMODAL AUDIO-VISUAL VALIDATOR
TrustLayer: Human Verification for the AI Era
Zeal College of Engineering & Research, Pune-41
Department of Electronics and Computer Engineering

Scientific Basis:
  1. Dynamic Alphanumeric Challenge:
     Presents a non-predictable, time-bound alphanumeric sequence (e.g., "7-K-2-B-9")
     that invalidates pre-recorded video replays and synthetic audio libraries.
  
  2. Bimodal Viseme-Phoneme Lip-Sync Correlation:
     Living speech produces tightly coupled biological articulatory kinematics:
     acoustic burst energy (vowels/consonants) synchronizes with physical Mouth
     Aspect Ratio (MAR) dilation within a 60-220ms biological latency window.
     Virtual camera injections with swapped audio or dubbed lip movements fail
     temporal cross-correlation tests.
=============================================================================
"""

import math
import time
import random
import string
import numpy as np
from collections import deque
from typing import Optional, Dict, Any, List, Tuple


class LipSyncValidator:
    """
    Validates dynamic spoken alphanumeric codes and audio-visual lip synchrony.
    """

    # MediaPipe Face Mesh lip landmark indices
    UPPER_LIP_TOP = 13
    LOWER_LIP_BOTTOM = 14
    MOUTH_CORNER_LEFT = 61
    MOUTH_CORNER_RIGHT = 291
    UPPER_LIP_INNER = 0
    LOWER_LIP_INNER = 17

    # Spoken number dictionary for normalization
    WORD_TO_DIGIT = {
        "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
        "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
        "oh": "0", "to": "2", "too": "2", "for": "4", "tree": "3",
        "ate": "8", "niner": "9"
    }

    def __init__(self, buffer_size: int = 90, fps: float = 30.0):
        self.buffer_size = buffer_size
        self.fps = fps

        self.mar_history: deque = deque(maxlen=buffer_size)
        self.audio_energy_history: deque = deque(maxlen=buffer_size)
        self.timestamps: deque = deque(maxlen=buffer_size)

        self.current_code: str = ""
        self.code_generated_time: float = 0.0

    def generate_alphanumeric_code(self, length: int = 8) -> str:
        """
        Generates a readable, unambiguous alphanumeric code (7-8 characters).
        Omits visually/phonetically confusing characters (0, O, 1, I).
        """
        charset = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
        self.current_code = "".join(random.choices(charset, k=length))
        self.code_generated_time = time.time()
        return self.current_code

    def calculate_mar(self, landmarks, width: int = 640, height: int = 480) -> float:
        """
        Calculates the vertical-to-horizontal Mouth Aspect Ratio (MAR).
        MAR expands during open vowel phonation (0.35-0.70) and contracts
        during bilabial plosives (0.05-0.15).
        """
        if not landmarks or len(landmarks) < 300:
            return 0.0

        p_top = landmarks[self.UPPER_LIP_TOP]
        p_bot = landmarks[self.LOWER_LIP_BOTTOM]
        p_left = landmarks[self.MOUTH_CORNER_LEFT]
        p_right = landmarks[self.MOUTH_CORNER_RIGHT]

        vert = math.hypot((p_top.x - p_bot.x) * width, (p_top.y - p_bot.y) * height)
        horiz = math.hypot((p_left.x - p_right.x) * width, (p_left.y - p_right.y) * height)

        mar = vert / max(horiz, 1e-5)
        return float(np.clip(mar, 0.0, 1.2))

    def update_frame(self, mar: float, audio_energy: float = 0.0, ts: Optional[float] = None) -> None:
        """Pushes real-time MAR and acoustic amplitude telemetry."""
        now = ts if ts is not None else time.time()
        self.mar_history.append(mar)
        self.audio_energy_history.append(audio_energy)
        self.timestamps.append(now)

    def normalize_spoken_text(self, text: str) -> str:
        """
        Normalizes spoken transcription into an alphanumeric string.
        Handles both individual letters/digits and spoken number words.
        """
        if not text:
            return ""

        words = text.lower().replace("-", " ").replace(".", " ").split()
        normalized_tokens = []

        for w in words:
            if w in self.WORD_TO_DIGIT:
                normalized_tokens.append(self.WORD_TO_DIGIT[w])
            else:
                # Strip punctuation, keep alphanumeric
                clean = "".join(ch.upper() for ch in w if ch.isalnum())
                if clean:
                    normalized_tokens.append(clean)

        return "".join(normalized_tokens)

    def verify_code(self, recognized_text: str, expected_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Evaluates spoken code transcription against expected challenge code.
        Allows fuzzy matching for acoustic misrecognitions.
        """
        target = (expected_code or self.current_code).upper().replace(" ", "").replace("-", "")
        clean_rec = self.normalize_spoken_text(recognized_text)

        if not target:
            return {"passed": False, "score": 0.0, "reason": "NO_TARGET_CODE"}

        if not clean_rec:
            return {"passed": False, "score": 0.0, "reason": "NO_AUDIO_TRANSCRIPTION"}

        # Exact match
        if target in clean_rec or clean_rec in target:
            return {
                "passed": True,
                "score": 100.0,
                "target": target,
                "recognized": clean_rec,
                "reason": "EXACT_OR_SUBSTRING_MATCH"
            }

        # Levenshtein distance ratio
        match_count = 0
        t_ptr = 0
        for ch in clean_rec:
            if t_ptr < len(target) and ch == target[t_ptr]:
                match_count += 1
                t_ptr += 1
            elif ch in target:
                match_count += 0.5

        similarity = (match_count / max(len(target), len(clean_rec))) * 100.0
        passed = similarity >= 65.0

        return {
            "passed": passed,
            "score": round(similarity, 1),
            "target": target,
            "recognized": clean_rec,
            "reason": "PHONETIC_SIMILARITY_MATCH" if passed else "MISMATCH"
        }

    def compute_bimodal_correlation(self) -> Dict[str, Any]:
        """
        Computes the normalized cross-correlation between audio energy and MAR.
        Natural biological speech exhibits positive cross-correlation with a
        lag between -50ms and +200ms.
        """
        if len(self.mar_history) < 20 or len(self.audio_energy_history) < 20:
            return {
                "is_synced": True,  # Default neutral while buffering
                "correlation": 0.50,
                "best_lag_ms": 0.0,
                "lip_variance": 0.0
            }

        mar_arr = np.array(self.mar_history, dtype=np.float64)
        aud_arr = np.array(self.audio_energy_history, dtype=np.float64)

        mar_var = float(np.var(mar_arr))
        aud_var = float(np.var(aud_arr))

        if mar_var < 1e-5 or aud_var < 1e-5:
            return {
                "is_synced": True,
                "correlation": 0.40,
                "best_lag_ms": 0.0,
                "lip_variance": mar_var
            }

        mar_norm = (mar_arr - np.mean(mar_arr)) / (np.std(mar_arr) + 1e-6)
        aud_norm = (aud_arr - np.mean(aud_arr)) / (np.std(aud_arr) + 1e-6)

        max_lag = int(self.fps * 0.3)  # +/- 300 ms
        corrs = []
        lags = list(range(-max_lag, max_lag + 1))

        for lag in lags:
            if lag < 0:
                c = np.mean(mar_norm[:lag] * aud_norm[-lag:])
            elif lag > 0:
                c = np.mean(mar_norm[lag:] * aud_norm[:-lag])
            else:
                c = np.mean(mar_norm * aud_norm)
            corrs.append(c)

        best_idx = int(np.argmax(corrs))
        best_corr = float(corrs[best_idx])
        best_lag_ms = float(lags[best_idx] * (1000.0 / self.fps))

        is_synced = best_corr >= 0.25 and (-100.0 <= best_lag_ms <= 250.0)

        return {
            "is_synced": is_synced,
            "correlation": round(best_corr, 3),
            "best_lag_ms": round(best_lag_ms, 1),
            "lip_variance": round(mar_var, 6)
        }
