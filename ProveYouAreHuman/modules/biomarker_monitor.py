"""
=============================================================================
BACKGROUND BIOMARKER MONITORING ENGINE
TrustLayer: Human Verification for the AI Era
Zeal College of Engineering & Research, Pune-41
Department of Electronics and Computer Engineering

Scientific Basis:
  Phase 2 of TrustLayer shifts from active gateway challenges to a passive,
  lightweight, always-on background thread that continuously verifies the
  biological presence of the authenticated user without interrupting the session.

  Two complementary biological channels are monitored simultaneously:

  A. Remote Photoplethysmography (rPPG) - Blood Volume Pulse
     Hemoglobin in facial capillaries absorbs green-spectrum (~540nm) ambient
     light during each systolic pulse wave. The skin surface brightness therefore
     oscillates at the cardiac frequency (45-150 BPM). By tracking per-pixel
     green channel means in a sliding temporal window and applying de Haan &
     Jeanne CHROM projection + FFT bandpass analysis, we recover the blood volume
     pulse waveform and confirm biological cardiac activity.

  B. High-Frequency Skin Micro-Jitter (Ultra-Light Phase 3 fallback)
     Biological skin surface is subject to continuous involuntary sub-pixel
     vibration from respiratory movement, cardiovascular pulse pressure, and
     motor neuron noise. At sampling rates >= 24 FPS, the variance of skin-patch
     mean intensity fluctuates at 0.3-3.0 Hz (respiration-cardiac band). Static
     photos, screen replays, and synthetic render pipelines produce near-zero
     micro-jitter variance in multi-frame windows.

Phase Selection Logic:
  Phase 2 (STREAM_MONITOR): Both rPPG + micro-jitter active. Targets high-stakes
    sessions (live exams, board calls). Slightly higher CPU: ~2-4% on i5.
  Phase 3 (LIGHT_SHIELD): rPPG pipeline bypassed. Only micro-jitter thread
    active. Minimal CPU: <1%. Suitable for standard video calls.
=============================================================================
"""

import math
import time
import threading
import numpy as np
import cv2
from collections import deque
from typing import Optional, Dict, Any, List, Tuple


# ============================================================================
# CONSTANTS
# ============================================================================

RPPG_BUFFER_SEC      = 5.0    # Sliding window length in seconds
RPPG_MIN_FPS         = 20.0   # Below this FPS, rPPG is unreliable
RPPG_HR_LOW_HZ       = 0.75   # 45 BPM
RPPG_HR_HIGH_HZ      = 2.5    # 150 BPM
RPPG_VALID_SNR       = 0.15   # Minimum SNR for valid pulse detection
RPPG_MIN_BPM         = 45.0
RPPG_MAX_BPM         = 145.0

JITTER_WINDOW        = 40     # Frames for micro-jitter variance window
JITTER_RESP_LOW_HZ   = 0.15   # 9 BPM respiratory low
JITTER_RESP_HIGH_HZ  = 3.0    # Upper biological jitter frequency
JITTER_STATIC_THRESH = 0.008  # Std below this = suspicious static source

# Landmark ROI sets (MediaPipe Face Mesh indices)
FOREHEAD_IDS  = [10, 67, 109, 108, 151, 9, 8, 337, 338, 297]
LEFT_CHEEK    = [117, 118, 101, 205, 50, 123, 147, 187]
RIGHT_CHEEK   = [346, 347, 330, 425, 280, 352, 376, 411]


# ============================================================================
# SKIN ROI EXTRACTOR
# ============================================================================

class SkinROIExtractor:
    """
    Extracts mean RGB values from the facial skin ROI (forehead + cheeks)
    using MediaPipe landmark indices to avoid hair, eyes, and mouth regions.
    """

    def __init__(self, circle_radius: int = 6):
        self.circle_radius = circle_radius
        self._roi_ids = FOREHEAD_IDS + LEFT_CHEEK + RIGHT_CHEEK

    def extract_rgb(self, frame_bgr: np.ndarray,
                    landmarks) -> Tuple[float, float, float]:
        """
        Returns (R, G, B) mean intensities from the skin ROI mask.
        frame_bgr: OpenCV BGR frame (uint8).
        landmarks: MediaPipe NormalizedLandmarkList.
        """
        h, w = frame_bgr.shape[:2]
        pts = []
        for idx in self._roi_ids:
            lm = landmarks[idx]
            px = int(np.clip(lm.x * w, 0, w - 1))
            py = int(np.clip(lm.y * h, 0, h - 1))
            pts.append((px, py))

        if not pts:
            return 0.0, 0.0, 0.0

        mask = np.zeros((h, w), dtype=np.uint8)
        for (px, py) in pts:
            cv2.circle(mask, (px, py), self.circle_radius, 255, -1)

        mean_bgr = cv2.mean(frame_bgr, mask=mask)[:3]
        b, g, r  = float(mean_bgr[0]), float(mean_bgr[1]), float(mean_bgr[2])
        return r, g, b

    def extract_forehead_patch(self, frame_bgr: np.ndarray,
                                landmarks) -> Optional[np.ndarray]:
        """
        Returns a tight forehead crop for micro-jitter analysis.
        """
        h, w = frame_bgr.shape[:2]
        pts = []
        for idx in FOREHEAD_IDS:
            lm = landmarks[idx]
            pts.append((int(lm.x * w), int(lm.y * h)))
        if not pts:
            return None
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        x1 = max(0, min(xs) - 5)
        y1 = max(0, min(ys) - 5)
        x2 = min(w, max(xs) + 5)
        y2 = min(h, max(ys) + 5)
        if (x2 - x1) < 10 or (y2 - y1) < 6:
            return None
        return frame_bgr[y1:y2, x1:x2].copy()


# ============================================================================
# CHROM rPPG ENGINE (de Haan & Jeanne, 2013)
# ============================================================================

class CHROMrPPGEngine:
    """
    Implements the chrominance-projection method for remote photoplethysmography.

    The CHROM method eliminates specular reflection and rigid motion artifacts
    by projecting the normalised RGB skin signal onto two orthogonal colour
    difference planes (Xs, Ys), then combining them with a scaling coefficient
    alpha = std(Xs) / std(Ys) to cancel specular components.
    """

    def __init__(self, fps: float = 30.0):
        self.fps = fps
        buffer_frames = int(RPPG_BUFFER_SEC * fps) + 30

        self._r_buf: deque = deque(maxlen=buffer_frames)
        self._g_buf: deque = deque(maxlen=buffer_frames)
        self._b_buf: deque = deque(maxlen=buffer_frames)
        self._ts_buf: deque = deque(maxlen=buffer_frames)

        # Output state
        self.bvp_signal:     List[float] = []
        self.bpm:            float = 0.0
        self.snr:            float = 0.0
        self.bpm_history:    List[float] = []
        self.is_pulse_valid: bool  = False
        self.liveness_score: float = 0.5

    def push_rgb(self, r: float, g: float, b: float,
                 ts: Optional[float] = None) -> None:
        now = ts if ts is not None else time.time()
        self._r_buf.append(r)
        self._g_buf.append(g)
        self._b_buf.append(b)
        self._ts_buf.append(now)

        # Update effective FPS
        if len(self._ts_buf) >= 10:
            span = self._ts_buf[-1] - self._ts_buf[0]
            if span > 0:
                self.fps = max(RPPG_MIN_FPS,
                               min(60.0, (len(self._ts_buf) - 1) / span))

    def _chrom_bvp(self, r: np.ndarray, g: np.ndarray,
                   b: np.ndarray) -> np.ndarray:
        """CHROM chrominance projection - returns raw BVP signal."""
        mr = np.mean(r); mg = np.mean(g); mb = np.mean(b)
        if mr < 1e-4 or mg < 1e-4 or mb < 1e-4:
            return np.zeros_like(r)

        rn = r / mr; gn = g / mg; bn = b / mb

        xs = 3.0 * rn - 2.0 * gn
        ys = 1.5 * rn + gn - 1.5 * bn

        std_xs = np.std(xs); std_ys = np.std(ys)
        alpha  = std_xs / max(std_ys, 1e-6)

        return xs - alpha * ys

    def _bandpass_fft(self, signal: np.ndarray) -> np.ndarray:
        """Zero-phase FFT bandpass: retains only cardiac frequency range."""
        n = len(signal)
        if n < 30:
            return signal - np.mean(signal)
        f     = np.fft.rfft(signal - np.mean(signal))
        freqs = np.fft.rfftfreq(n, d=1.0 / self.fps)
        mask  = (freqs >= RPPG_HR_LOW_HZ) & (freqs <= RPPG_HR_HIGH_HZ)
        f    *= mask
        return np.fft.irfft(f, n=n)

    def _estimate_hr(self, bvp: np.ndarray) -> Tuple[float, float]:
        """Returns (BPM, SNR) from the filtered BVP waveform."""
        n = len(bvp)
        if n < 40:
            return 0.0, 0.0
        fft_mag = np.abs(np.fft.rfft(bvp)) ** 2
        freqs   = np.fft.rfftfreq(n, d=1.0 / self.fps)
        valid   = (freqs >= 0.80) & (freqs <= 2.33)
        if not np.any(valid):
            return 0.0, 0.0
        vf = freqs[valid]; vm = fft_mag[valid]
        peak_freq  = vf[np.argmax(vm)]
        peak_power = vm[np.argmax(vm)]
        total_pwr  = np.sum(vm)
        bpm = peak_freq * 60.0
        snr = float(peak_power / max(total_pwr - peak_power, 1e-5))
        return float(bpm), snr

    def compute(self) -> Dict[str, Any]:
        """
        Processes the current buffer and returns rPPG metrics.
        Call once per frame after push_rgb().
        """
        n = len(self._r_buf)
        min_frames = int(self.fps * 2.0)  # Need at least 2 seconds

        if n < min_frames:
            return {
                "bpm": round(self.bpm, 1),
                "snr": round(self.snr, 2),
                "is_pulse_valid": False,
                "liveness_score": 0.4,
                "bvp_waveform": [],
                "buffer_fill_pct": round(n / max(int(self.fps * RPPG_BUFFER_SEC), 1), 3),
                "status": "BUFFERING"
            }

        r_arr = np.array(self._r_buf, dtype=np.float32)
        g_arr = np.array(self._g_buf, dtype=np.float32)
        b_arr = np.array(self._b_buf, dtype=np.float32)

        raw_bvp      = self._chrom_bvp(r_arr, g_arr, b_arr)
        filtered_bvp = self._bandpass_fft(raw_bvp)
        self.bvp_signal = filtered_bvp.tolist()

        est_bpm, snr = self._estimate_hr(filtered_bvp)

        if RPPG_MIN_BPM <= est_bpm <= RPPG_MAX_BPM and snr > RPPG_VALID_SNR:
            self.bpm = (0.7 * self.bpm + 0.3 * est_bpm) if self.bpm > 0 else est_bpm
            self.snr = snr
            self.is_pulse_valid  = True
            self.liveness_score  = min(0.98, max(0.72, 0.68 + min(snr, 2.0) * 0.15))
            self.bpm_history.append(self.bpm)
            if len(self.bpm_history) > 30:
                self.bpm_history.pop(0)
        else:
            self.is_pulse_valid = False
            self.liveness_score = 0.38

        return {
            "bpm": round(self.bpm, 1),
            "snr": round(self.snr, 3),
            "is_pulse_valid": self.is_pulse_valid,
            "liveness_score": round(self.liveness_score, 3),
            "bvp_waveform": self.bvp_signal[-60:] if self.bvp_signal else [],
            "buffer_fill_pct": round(n / max(int(self.fps * RPPG_BUFFER_SEC), 1), 3),
            "status": "ACTIVE"
        }

    def reset(self) -> None:
        self._r_buf.clear(); self._g_buf.clear()
        self._b_buf.clear(); self._ts_buf.clear()
        self.bvp_signal = []; self.bpm = 0.0; self.snr = 0.0
        self.is_pulse_valid = False; self.liveness_score = 0.5
        self.bpm_history = []


# ============================================================================
# MICRO-JITTER DETECTOR (Phase 2 and Phase 3)
# ============================================================================

class MicroJitterDetector:
    """
    Detects high-frequency skin micro-jitter via temporal intensity variance
    in the forehead patch green channel.

    Biological skin exhibits micro-vibrations from:
    - Cardiac pulse pressure transmitted through skin tissues
    - Respiratory intercostal muscle movement
    - Autonomous nervous system motor noise

    Static photographs, pre-recorded replays, and deepfake renders produce
    near-zero inter-frame intensity variance (std < JITTER_STATIC_THRESH).
    """

    def __init__(self, fps: float = 30.0):
        self.fps = fps
        self._green_means: deque = deque(maxlen=JITTER_WINDOW)
        self._ts:          deque = deque(maxlen=JITTER_WINDOW)

        self.jitter_std:     float = 0.0
        self.jitter_freq_hz: float = 0.0
        self.liveness_score: float = 0.5
        self.is_suspicious:  bool  = False

    def push_patch(self, patch_bgr: Optional[np.ndarray],
                   ts: Optional[float] = None) -> None:
        """Ingest one forehead patch frame."""
        now = ts if ts is not None else time.time()
        if patch_bgr is None or patch_bgr.size == 0:
            return
        green_mean = float(np.mean(patch_bgr[:, :, 1]))  # Green channel
        self._green_means.append(green_mean)
        self._ts.append(now)

        if len(self._ts) >= 10:
            span = self._ts[-1] - self._ts[0]
            if span > 0:
                self.fps = (len(self._ts) - 1) / span

    def compute(self) -> Dict[str, Any]:
        """
        Computes micro-jitter metrics from the green channel variance series.
        """
        n = len(self._green_means)
        if n < 8:
            return {
                "jitter_std": 0.0,
                "jitter_freq_hz": 0.0,
                "is_suspicious": False,
                "liveness_score": 0.5,
                "status": "BUFFERING"
            }

        arr = np.array(self._green_means, dtype=np.float32)
        self.jitter_std = float(np.std(arr))

        # FFT to extract dominant jitter frequency
        if n >= 16:
            demeaned = arr - np.mean(arr)
            fft_mag  = np.abs(np.fft.rfft(demeaned)) ** 2
            freqs    = np.fft.rfftfreq(n, d=1.0 / self.fps)
            bio_mask = (freqs >= JITTER_RESP_LOW_HZ) & (freqs <= JITTER_RESP_HIGH_HZ)
            if np.any(bio_mask):
                self.jitter_freq_hz = float(freqs[bio_mask][np.argmax(fft_mag[bio_mask])])

        # Biological threshold check
        if self.jitter_std < JITTER_STATIC_THRESH:
            self.is_suspicious  = True
            self.liveness_score = max(0.15, self.jitter_std / JITTER_STATIC_THRESH * 0.45)
        else:
            self.is_suspicious  = False
            # Score scales with how far above the threshold we are (capped at 0.95)
            ratio = min(self.jitter_std / (JITTER_STATIC_THRESH * 3.0), 1.0)
            self.liveness_score = 0.50 + 0.45 * ratio

        return {
            "jitter_std":     round(self.jitter_std, 6),
            "jitter_freq_hz": round(self.jitter_freq_hz, 2),
            "is_suspicious":  self.is_suspicious,
            "liveness_score": round(self.liveness_score, 3),
            "status":         "ACTIVE"
        }

    def reset(self) -> None:
        self._green_means.clear()
        self._ts.clear()
        self.jitter_std = 0.0; self.jitter_freq_hz = 0.0
        self.liveness_score = 0.5; self.is_suspicious = False


# ============================================================================
# HUD RENDERER
# ============================================================================

def render_biomarker_hud(frame: np.ndarray,
                          rppg_data: Dict,
                          jitter_data: Dict,
                          phase: int = 2,
                          x: int = 20, y: int = 20,
                          w: int = 290, h: int = 150) -> None:
    """
    Renders the Biomarker Monitor HUD panel onto an OpenCV BGR frame.
    phase: 2 = Stream Monitor (rPPG + jitter), 3 = Light Shield (jitter only).
    """
    overlay = frame.copy()
    cv2.rectangle(overlay, (x, y), (x + w, y + h), (15, 18, 26), -1)
    cv2.addWeighted(overlay, 0.82, frame, 0.18, 0, frame)
    cv2.rectangle(frame, (x, y), (x + w, y + h), (60, 60, 80), 1)

    title_col = (0, 220, 255)
    phase_tag = "PHASE 2: STREAM MONITOR" if phase == 2 else "PHASE 3: LIGHT SHIELD"
    cv2.putText(frame, phase_tag, (x + 8, y + 18), cv2.FONT_HERSHEY_SIMPLEX, 0.38, title_col, 1)

    if phase == 2:
        # rPPG row
        valid     = rppg_data.get("is_pulse_valid", False)
        bpm       = rppg_data.get("bpm", 0.0)
        snr       = rppg_data.get("snr", 0.0)
        fill_pct  = rppg_data.get("buffer_fill_pct", 0.0)
        rppg_col  = (80, 230, 80) if valid else (0, 180, 255)

        if valid:
            rppg_text = f"rPPG PULSE: {int(bpm)} BPM  SNR:{snr:.2f}  [LIVE]"
        else:
            rppg_text = f"rPPG: Buffering... {int(fill_pct * 100)}%"
        cv2.putText(frame, rppg_text, (x + 8, y + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.40, rppg_col, 1)

        # BVP waveform
        bvp = rppg_data.get("bvp_waveform", [])
        if len(bvp) >= 20:
            samples  = bvp[-50:]
            mn, mx   = min(samples), max(samples)
            spread   = max(mx - mn, 1e-5)
            gcy      = y + 75; gh = 20
            step_x   = (w - 20) / max(len(samples) - 1, 1)
            pts      = []
            for i, v in enumerate(samples):
                norm = (v - mn) / spread
                pts.append((int(x + 10 + i * step_x),
                             int(gcy - (norm - 0.5) * gh)))
            for i in range(len(pts) - 1):
                cv2.line(frame, pts[i], pts[i + 1], rppg_col, 1)
        else:
            cv2.putText(frame, "Acquiring BVP waveform...",
                        (x + 8, y + 72), cv2.FONT_HERSHEY_SIMPLEX, 0.34, (120, 120, 140), 1)

    # Micro-jitter row (both phases)
    jitter_std  = jitter_data.get("jitter_std", 0.0)
    jitter_susp = jitter_data.get("is_suspicious", False)
    jitter_col  = (60, 240, 60) if not jitter_susp else (60, 60, 240)
    jitter_status = "SUSPICIOUS" if jitter_susp else "NORMAL"
    jitter_text = f"MICRO-JITTER  std:{jitter_std:.5f}  [{jitter_status}]"
    jitter_y = y + 108 if phase == 2 else y + 45
    cv2.putText(frame, jitter_text, (x + 8, jitter_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, jitter_col, 1)

    # Combined liveness bar
    rppg_ls   = rppg_data.get("liveness_score", 0.5) if phase == 2 else 0.5
    jitter_ls = jitter_data.get("liveness_score", 0.5)
    combined  = (rppg_ls * 0.65 + jitter_ls * 0.35) if phase == 2 else jitter_ls

    bar_y     = y + h - 22
    bar_w     = int((w - 20) * combined)
    bar_col   = (60, 200, 60) if combined >= 0.55 else (60, 60, 240)
    cv2.rectangle(frame, (x + 10, bar_y), (x + 10 + w - 20, bar_y + 12), (40, 40, 50), -1)
    cv2.rectangle(frame, (x + 10, bar_y), (x + 10 + bar_w, bar_y + 12), bar_col, -1)
    cv2.putText(frame, f"Biomarker Score: {int(combined * 100)}%",
                (x + 10, bar_y - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (180, 180, 200), 1)


# ============================================================================
# BIOMARKER MONITOR (Thread-Safe Phase Switcher)
# ============================================================================

class BiomarkerMonitor:
    """
    Top-level passive biomarker engine with phase-switching logic.

    Phase 2 (STREAM_MONITOR): rPPG blood pulse + micro-jitter.
    Phase 3 (LIGHT_SHIELD):   Micro-jitter only (minimum CPU).

    Thread safety: The update() method is designed to be called from the main
    video capture loop. No background thread is spawned; the caller controls
    the execution context to avoid GIL contention with MediaPipe.

    Usage:
        monitor = BiomarkerMonitor(phase=2)

        # Each frame (MediaPipe landmarks required for rPPG):
        result = monitor.update(frame_bgr, landmarks)

        # Render HUD:
        monitor.render_hud(frame)

        # Switch phase:
        monitor.set_phase(3)
    """

    def __init__(self, phase: int = 2, fps: float = 30.0):
        self._phase = phase
        self.roi_extractor  = SkinROIExtractor()
        self.rppg_engine    = CHROMrPPGEngine(fps=fps)
        self.jitter_engine  = MicroJitterDetector(fps=fps)

        # Last computed results (cached for rendering)
        self._last_rppg:   Dict[str, Any] = {}
        self._last_jitter: Dict[str, Any] = {}
        self._lock = threading.Lock()

    @property
    def phase(self) -> int:
        return self._phase

    def set_phase(self, phase: int) -> None:
        """Dynamically switch between Phase 2 and Phase 3."""
        assert phase in (2, 3), "Phase must be 2 or 3"
        with self._lock:
            self._phase = phase
            if phase == 3:
                self.rppg_engine.reset()   # Free memory from rPPG buffers

    def update(self, frame_bgr: np.ndarray,
               landmarks) -> Dict[str, Any]:
        """
        Process one video frame.

        Parameters:
            frame_bgr  : Full BGR video frame from OpenCV.
            landmarks  : MediaPipe NormalizedLandmarkList (from face landmarker).
                         May be None if face is momentarily occluded.

        Returns:
            Biomarker result dict with composite liveness score.
        """
        rppg_result   = {}
        jitter_result = {}

        with self._lock:
            phase = self._phase

        # -- Skin patch extraction --
        patch = None
        if landmarks is not None:
            try:
                patch = self.roi_extractor.extract_forehead_patch(frame_bgr, landmarks)
            except Exception:
                patch = None

        # -- Phase 2: rPPG + Micro-jitter --
        if phase == 2:
            if landmarks is not None:
                try:
                    r, g, b = self.roi_extractor.extract_rgb(frame_bgr, landmarks)
                    self.rppg_engine.push_rgb(r, g, b)
                    rppg_result = self.rppg_engine.compute()
                except Exception:
                    rppg_result = {"bpm": 0.0, "snr": 0.0, "is_pulse_valid": False,
                                   "liveness_score": 0.4, "bvp_waveform": [],
                                   "buffer_fill_pct": 0.0, "status": "ERROR"}
            else:
                rppg_result = {"bpm": self.rppg_engine.bpm, "snr": self.rppg_engine.snr,
                                "is_pulse_valid": self.rppg_engine.is_pulse_valid,
                                "liveness_score": self.rppg_engine.liveness_score,
                                "bvp_waveform": [], "buffer_fill_pct": 0.0,
                                "status": "NO_FACE"}

        # -- Micro-jitter (both phases) --
        self.jitter_engine.push_patch(patch)
        jitter_result = self.jitter_engine.compute()

        # -- Composite liveness fusion --
        if phase == 2:
            rppg_ls   = rppg_result.get("liveness_score", 0.4)
            jitter_ls = jitter_result.get("liveness_score", 0.5)
            composite = rppg_ls * 0.65 + jitter_ls * 0.35
        else:
            composite = jitter_result.get("liveness_score", 0.5)

        is_suspicious = (
            jitter_result.get("is_suspicious", False) or
            (phase == 2 and not rppg_result.get("is_pulse_valid", False)
             and rppg_result.get("buffer_fill_pct", 0.0) >= 0.90)
        )

        anomaly_flags = []
        if jitter_result.get("is_suspicious", False):
            anomaly_flags.append("LOW_SKIN_MICRO_JITTER")
        if phase == 2 and not rppg_result.get("is_pulse_valid", False):
            if rppg_result.get("buffer_fill_pct", 0.0) >= 0.90:
                anomaly_flags.append("NO_CARDIAC_PULSE_DETECTED")

        result = {
            "phase":              phase,
            "composite_score":    round(float(composite), 4),
            "is_suspicious":      is_suspicious,
            "anomaly_flags":      anomaly_flags,
            "rppg":               rppg_result,
            "jitter":             jitter_result,
        }

        with self._lock:
            self._last_rppg   = rppg_result
            self._last_jitter = jitter_result

        return result

    def render_hud(self, frame: np.ndarray,
                   x: int = 20, y: int = 20,
                   w: int = 290, h: int = 150) -> None:
        """Convenience wrapper to render the HUD using the last computed results."""
        with self._lock:
            rppg   = dict(self._last_rppg)
            jitter = dict(self._last_jitter)
            phase  = self._phase

        if not rppg:
            rppg = {"bpm": 0.0, "snr": 0.0, "is_pulse_valid": False,
                    "liveness_score": 0.4, "bvp_waveform": [], "buffer_fill_pct": 0.0}
        if not jitter:
            jitter = {"jitter_std": 0.0, "is_suspicious": False, "liveness_score": 0.5}

        render_biomarker_hud(frame, rppg, jitter, phase=phase, x=x, y=y, w=w, h=h)

    def reset(self) -> None:
        """Full state reset (call between sessions)."""
        with self._lock:
            self.rppg_engine.reset()
            self.jitter_engine.reset()
            self._last_rppg   = {}
            self._last_jitter = {}
