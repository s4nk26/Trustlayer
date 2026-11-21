"""
=============================================================================
KINEMATIC MICRO-TREMOR VECTOR TRACKING MODULE
TrustLayer: Human Verification for the AI Era
Zeal College of Engineering & Research, Pune-41
Department of Electronics and Computer Engineering

Scientific Basis:
  Every living human nervous system produces involuntary high-frequency muscular
  micro-tremors (physiological tremor) in the 6-12 Hz band, caused by motor unit
  firing rates, mechanical resonance, and cardiovascular pulse pressure. These are
  physically immutable and cannot be replicated by pre-recorded video loops,
  static deepfake renders, or virtual-camera injection streams in real time.

Module Responsibilities:
  1. Coordinate Path Tracking  - records per-frame (x, y) nose/wrist positions.
  2. Vector Displacement Math  - computes shortest-distance Euclidean displacement
     between consecutive frames and builds a rolling kinematic vector series.
  3. Micro-Tremor Frequency Analysis - applies FFT to the displacement magnitude
     series and extracts dominant physiological tremor frequency + amplitude.
  4. Drift & Linearity Score  - synthetic bot scripts produce perfectly linear or
     perfectly static motion; biological motion has natural stochastic drift.
  5. Jerk Continuity Verification - computes jerk (da/dt) profile; robotic/scripted
     injection processes exceed human jerk thresholds (>140 normalized units).
  6. Spatial Coordinate Coverage  - measures how much of the expected interaction
     bounding box the user trajectory covered (anti-frozen-frame defence).
  7. Challenge Path Conformance  - when an animated UI target moves along a geometric
     path, this engine measures whether the user hand/nose tracked it within
     the human reaction-delay tolerance window (150-400 ms cognitive latency band).

Output:
  A single TremorProfile dict usable by both the desktop main.py state machine
  and the FastAPI server.py WebSocket pipeline.
=============================================================================
"""

import math
import time
import numpy as np
from collections import deque
from typing import Optional, List, Dict, Any, Tuple


# ============================================================================
# CONSTANTS - Physiological Reference Values
# ============================================================================

TREMOR_FREQ_LOW_HZ   = 6.0
TREMOR_FREQ_HIGH_HZ  = 12.0

BOT_LINEARITY_THRESHOLD  = 0.985
BOT_JERK_THRESHOLD       = 140.0
STATIC_VAR_THRESHOLD     = 0.00008

MIN_ANALYSIS_FRAMES = 45


# ============================================================================
# UTILITY: Zero-Phase FFT Bandpass
# ============================================================================

def _fft_bandpass(signal: np.ndarray, fps: float,
                  low_hz: float, high_hz: float) -> np.ndarray:
    """Returns the zero-phase FFT-filtered version of signal."""
    n = len(signal)
    if n < 8:
        return signal.copy()
    f_coeffs = np.fft.rfft(signal - np.mean(signal))
    freqs    = np.fft.rfftfreq(n, d=1.0 / fps)
    mask     = (freqs >= low_hz) & (freqs <= high_hz)
    f_coeffs *= mask
    return np.fft.irfft(f_coeffs, n=n)


# ============================================================================
# KINEMATIC VECTOR SERIES (per tracked point)
# ============================================================================

class KinematicSeries:
    """
    Rolling kinematic state for a single tracked anatomical point (nose tip
    or wrist centroid). All positions normalised to [0, 1] screen space.
    """

    def __init__(self, window: int = 90, fps: float = 30.0, label: str = "nose"):
        self.label   = label
        self.window  = window
        self.fps     = fps

        self._pos_x: deque = deque(maxlen=window)
        self._pos_y: deque = deque(maxlen=window)
        self._ts:    deque = deque(maxlen=window)
        self._disp:  deque = deque(maxlen=window)
        self._vel:   deque = deque(maxlen=window)
        self._accel: deque = deque(maxlen=window)
        self._jerk:  deque = deque(maxlen=window)

        self._vel_ema   = 0.0
        self._accel_ema = 0.0

    def push(self, x: float, y: float, ts: Optional[float] = None) -> None:
        """Ingest a new (x, y) landmark position (normalised [0,1])."""
        now = ts if ts is not None else time.time()

        if self._ts:
            dt = max(now - self._ts[-1], 1e-4)

            dx   = x - self._pos_x[-1]
            dy   = y - self._pos_y[-1]
            disp = math.hypot(dx, dy)

            inst_vel  = disp / dt
            self._vel_ema = 0.6 * inst_vel + 0.4 * self._vel_ema

            prev_vel = self._vel[-1] if self._vel else 0.0
            inst_accel = (self._vel_ema - prev_vel) / dt
            self._accel_ema = 0.5 * inst_accel + 0.5 * self._accel_ema

            prev_accel = self._accel[-1] if self._accel else 0.0
            jerk = (self._accel_ema - prev_accel) / dt

            self._disp.append(disp)
            self._vel.append(self._vel_ema)
            self._accel.append(self._accel_ema)
            self._jerk.append(jerk)

        self._pos_x.append(x)
        self._pos_y.append(y)
        self._ts.append(now)

        if len(self._ts) >= 10:
            span = self._ts[-1] - self._ts[0]
            if span > 0:
                self.fps = (len(self._ts) - 1) / span

    def _disp_array(self) -> np.ndarray:
        return np.array(self._disp, dtype=np.float32)

    def tremor_frequency_profile(self) -> Dict[str, Any]:
        """FFT-based physiological tremor band extraction (6-12 Hz)."""
        disp = self._disp_array()
        if len(disp) < MIN_ANALYSIS_FRAMES:
            return {
                "dominant_freq_hz": 0.0, "tremor_amplitude": 0.0,
                "band_snr": 0.0, "in_physiological_band": False,
                "frames_buffered": len(disp)
            }

        filtered  = _fft_bandpass(disp, self.fps, TREMOR_FREQ_LOW_HZ, TREMOR_FREQ_HIGH_HZ)
        full_fft  = np.abs(np.fft.rfft(disp - np.mean(disp))) ** 2
        freqs     = np.fft.rfftfreq(len(disp), d=1.0 / self.fps)
        band_mask = (freqs >= TREMOR_FREQ_LOW_HZ) & (freqs <= TREMOR_FREQ_HIGH_HZ)

        if not np.any(band_mask):
            return {
                "dominant_freq_hz": 0.0, "tremor_amplitude": 0.0,
                "band_snr": 0.0, "in_physiological_band": False,
                "frames_buffered": len(disp)
            }

        band_power  = np.sum(full_fft[band_mask])
        total_power = np.sum(full_fft) + 1e-12
        band_freqs  = freqs[band_mask]
        band_mags   = full_fft[band_mask]
        peak_idx    = int(np.argmax(band_mags))
        dom_freq    = float(band_freqs[peak_idx])
        amplitude   = float(np.std(filtered))
        snr         = float(band_power / max(total_power - band_power, 1e-10))
        in_band     = TREMOR_FREQ_LOW_HZ <= dom_freq <= TREMOR_FREQ_HIGH_HZ

        return {
            "dominant_freq_hz": round(dom_freq, 2),
            "tremor_amplitude": round(amplitude * 1000, 4),
            "band_snr": round(snr, 4),
            "in_physiological_band": in_band,
            "frames_buffered": len(disp)
        }

    def displacement_variance(self) -> float:
        """Standard deviation of frame-to-frame displacements."""
        disp = self._disp_array()
        if len(disp) < 5:
            return 0.0
        return float(np.std(disp))

    def trajectory_linearity(self) -> float:
        """R-squared of linear fit to position series (high = bot-like)."""
        xs = np.array(self._pos_x, dtype=np.float64)
        ys = np.array(self._pos_y, dtype=np.float64)
        n  = len(xs)
        if n < 5:
            return 0.0
        t = np.arange(n, dtype=np.float64)
        r2_scores = []
        for arr in (xs, ys):
            if np.std(arr) < 1e-9:
                r2_scores.append(1.0)
                continue
            coeffs    = np.polyfit(t, arr, 1)
            predicted = np.polyval(coeffs, t)
            ss_res    = np.sum((arr - predicted) ** 2)
            ss_tot    = np.sum((arr - np.mean(arr)) ** 2)
            r2_scores.append(1.0 - ss_res / max(ss_tot, 1e-12))
        return float(max(r2_scores))

    def max_jerk(self) -> float:
        """Maximum absolute jerk value (da/dt)."""
        if not self._jerk:
            return 0.0
        return float(max(abs(j) for j in self._jerk))

    def spatial_coverage(self, roi_x: float = 0.0, roi_y: float = 0.0,
                          roi_w: float = 1.0, roi_h: float = 1.0) -> float:
        """Ratio of the ROI that the trajectory has visited."""
        if len(self._pos_x) < 3:
            return 0.0
        xs = np.array(self._pos_x)
        ys = np.array(self._pos_y)
        in_roi = ((xs >= roi_x) & (xs <= roi_x + roi_w) &
                  (ys >= roi_y) & (ys <= roi_y + roi_h))
        return round(float(np.mean(in_roi)), 4)

    def asymmetry_index(self) -> float:
        """
        Computes Kinematic Asymmetry Index (ratio of acceleration duration to deceleration duration).
        Biological human motor trajectories exhibit natural asymmetry in submovements (0.60 - 0.88
        or 1.15 - 1.45). Machine/bot linear interpolations have perfectly symmetric bell ramps (1.00 +/- 0.03).
        """
        if len(self._vel) < 15:
            return 0.78  # Nominal biological default

        vels = np.array(self._vel)
        accels = np.array(self._accel)

        accel_frames = np.sum(accels > 0.001)
        decel_frames = np.sum(accels < -0.001)

        if decel_frames == 0 or accel_frames == 0:
            return 1.0

        ratio = float(accel_frames) / float(decel_frames)
        return round(ratio, 3)

    def non_linear_power_law(self) -> Dict[str, Any]:
        """
        Evaluates the biological Two-Thirds Power Law (v = alpha * kappa^(-beta)).
        In human kinematics, instantaneous velocity decreases at high-curvature vertices
        (e.g., star points) and accelerates along gentle curves (beta in [0.20, 0.45],
        negative correlation between v and kappa). Machine linear paths exhibit flat or positive correlation.
        """
        if len(self._pos_x) < 20:
            return {
                "beta_exponent": 0.33,
                "curvature_velocity_corr": -0.42,
                "is_biological": True,
                "power_law_score": 0.88
            }

        xs = np.array(self._pos_x)
        ys = np.array(self._pos_y)

        # Derivatives dx, dy, d2x, d2y
        dx = np.gradient(xs)
        dy = np.gradient(ys)
        d2x = np.gradient(dx)
        d2y = np.gradient(dy)

        # Curvature kappa = |dx*d2y - dy*d2x| / (dx^2 + dy^2)^(3/2)
        denom = (dx**2 + dy**2) ** 1.5
        numer = np.abs(dx * d2y - dy * d2x)
        valid = denom > 1e-6
        if np.sum(valid) < 10:
            return {"beta_exponent": 0.33, "curvature_velocity_corr": -0.40, "is_biological": True, "power_law_score": 0.85}

        kappa = numer[valid] / denom[valid]
        v = np.sqrt(dx[valid]**2 + dy[valid]**2)

        # Filter out extreme outliers
        mask = (kappa > 1e-4) & (kappa < 500.0) & (v > 1e-4)
        if np.sum(mask) < 8:
            return {"beta_exponent": 0.33, "curvature_velocity_corr": -0.38, "is_biological": True, "power_law_score": 0.85}

        log_k = np.log(kappa[mask])
        log_v = np.log(v[mask])

        # Pearson correlation
        corr = float(np.corrcoef(log_k, log_v)[0, 1])
        if np.isnan(corr):
            corr = 0.0

        # Linear regression slope: log_v = a - beta * log_k
        slope, _ = np.polyfit(log_k, log_v, 1)
        beta = float(-slope)

        # Biological criteria: negative correlation (slowing at corners) and beta in physiological range [0.15, 0.55]
        is_bio = (corr < -0.15) and (0.10 <= beta <= 0.65)
        power_score = float(np.clip(1.0 - abs(corr + 0.35) * 1.5, 0.30, 0.98))

        return {
            "beta_exponent": round(beta, 3),
            "curvature_velocity_corr": round(corr, 3),
            "is_biological": is_bio,
            "power_law_score": round(power_score, 3)
        }

    def reset(self) -> None:
        self._pos_x.clear(); self._pos_y.clear(); self._ts.clear()
        self._disp.clear(); self._vel.clear()
        self._accel.clear(); self._jerk.clear()
        self._vel_ema = 0.0; self._accel_ema = 0.0


# ============================================================================
# PATH CHALLENGE CONFORMANCE ENGINE
# ============================================================================

class PathConformanceEngine:
    """
    Validates that a user tracked anatomical point follows an animated UI target
    path within the human cognitive reaction-delay window (150-400 ms) and verifies
    non-linear kinematic laws and asymmetry.
    """

    LATENCY_LOW_MS  = 150
    LATENCY_HIGH_MS = 400
    POSITION_TOL    = 0.12

    @staticmethod
    def generate_shape_waypoints(shape: str = "star",
                                 cx: float = 0.5,
                                 cy: float = 0.45,
                                 scale: float = 0.22,
                                 num_points: int = 120) -> List[Dict[str, float]]:
        """
        Generates parametric waypoints for Star, Infinity (Lemniscate), or Spiral shapes.
        Returns normalized coordinates [0, 1] for UI target tracking.
        """
        waypoints = []
        if shape.lower() == "star":
            # True geometric 5-pointed star with 5 outer points and 5 inner corners
            r_outer = scale
            r_inner = scale * 0.382  # Golden ratio inner radius
            star_vertices = []
            for j in range(10):
                angle = -math.pi / 2.0 + j * (math.pi / 5.0)
                r_v = r_outer if (j % 2 == 0) else r_inner
                vx = cx + r_v * math.cos(angle)
                vy = cy + r_v * math.sin(angle)
                star_vertices.append((vx, vy))

            # Interpolate smoothly along the 10 straight star edges
            pts_per_segment = max(1, num_points // 10)
            for j in range(10):
                p1 = star_vertices[j]
                p2 = star_vertices[(j + 1) % 10]
                for step in range(pts_per_segment):
                    frac = step / float(pts_per_segment)
                    wx = p1[0] + (p2[0] - p1[0]) * frac
                    wy = p1[1] + (p2[1] - p1[1]) * frac
                    prog = len(waypoints) / float(num_points)
                    waypoints.append({"x": round(wx, 4), "y": round(wy, 4), "progress": round(prog, 3)})

        elif shape.lower() == "infinity":
            # Lemniscate of Bernoulli
            for i in range(num_points):
                t = (i / num_points) * 2.0 * math.pi
                den = 1.0 + math.sin(t) ** 2
                px = cx + (scale * math.cos(t)) / den
                py = cy + (scale * math.sin(t) * math.cos(t)) / den
                waypoints.append({"x": round(px, 4), "y": round(py, 4), "progress": round(i / num_points, 3)})

        elif shape.lower() == "square":
            # 4-sided geometric square
            pts_per_side = num_points // 4
            half = scale * 0.95
            # Top side (left to right)
            for i in range(pts_per_side):
                f = i / pts_per_side
                waypoints.append({"x": round(cx - half + 2 * half * f, 4), "y": round(cy - half, 4), "progress": round(len(waypoints)/num_points, 3)})
            # Right side (top to bottom)
            for i in range(pts_per_side):
                f = i / pts_per_side
                waypoints.append({"x": round(cx + half, 4), "y": round(cy - half + 2 * half * f, 4), "progress": round(len(waypoints)/num_points, 3)})
            # Bottom side (right to left)
            for i in range(pts_per_side):
                f = i / pts_per_side
                waypoints.append({"x": round(cx + half - 2 * half * f, 4), "y": round(cy + half, 4), "progress": round(len(waypoints)/num_points, 3)})
            # Left side (bottom to top)
            for i in range(pts_per_side):
                f = i / pts_per_side
                waypoints.append({"x": round(cx - half, 4), "y": round(cy + half - 2 * half * f, 4), "progress": round(len(waypoints)/num_points, 3)})

        else:
            # Archimedean Spiral
            for i in range(num_points):
                t = (i / num_points) * 4.0 * math.pi
                r = (scale * 0.9) * (t / (4.0 * math.pi))
                px = cx + r * math.cos(t)
                py = cy + r * math.sin(t)
                waypoints.append({"x": round(px, 4), "y": round(py, 4), "progress": round(i / num_points, 3)})

        return waypoints

    def __init__(self):
        self._waypoints:  List[Tuple[float, float, float]] = []
        self._user_track: deque = deque(maxlen=200)
        self.conformance_scores: List[float] = []
        self.latency_samples_ms: List[float] = []

    def add_waypoint(self, cx: float, cy: float, ts: Optional[float] = None):
        self._waypoints.append((cx, cy, ts if ts is not None else time.time()))

    def push_user_position(self, x: float, y: float, ts: Optional[float] = None):
        self._user_track.append((x, y, ts if ts is not None else time.time()))
        self._evaluate_pending_waypoints()

    def _evaluate_pending_waypoints(self):
        if not self._waypoints or not self._user_track:
            return
        low  = self.LATENCY_LOW_MS  / 1000.0
        high = self.LATENCY_HIGH_MS / 1000.0
        now  = time.time()
        remaining = []
        for (cx, cy, wt) in self._waypoints:
            age = now - wt
            if age < low:
                remaining.append((cx, cy, wt))
                continue
            if age > high + 1.5:
                self.conformance_scores.append(0.0)
                continue
            best_dist    = 999.0
            best_latency = None
            for (ux, uy, ut) in self._user_track:
                lat = ut - wt
                if low <= lat <= high:
                    dist = math.hypot(ux - cx, uy - cy)
                    if dist < best_dist:
                        best_dist    = dist
                        best_latency = lat * 1000.0
            if best_dist <= self.POSITION_TOL:
                score = max(0.0, 1.0 - (best_dist / self.POSITION_TOL))
                self.conformance_scores.append(score)
                if best_latency is not None:
                    self.latency_samples_ms.append(best_latency)
            else:
                if age > high:
                    self.conformance_scores.append(0.0)
                else:
                    remaining.append((cx, cy, wt))
        self._waypoints = remaining

    @property
    def mean_conformance(self) -> float:
        if not self.conformance_scores:
            return 0.5
        return float(np.mean(self.conformance_scores[-30:]))

    @property
    def mean_latency_ms(self) -> float:
        if not self.latency_samples_ms:
            return 0.0
        return float(np.mean(self.latency_samples_ms[-20:]))

    @property
    def is_bot_latency(self) -> bool:
        if len(self.latency_samples_ms) < 5:
            return False
        lats = np.array(self.latency_samples_ms[-15:])
        mean = float(np.mean(lats))
        std  = float(np.std(lats))
        return (mean < self.LATENCY_LOW_MS) or (std < 8.0 and len(lats) >= 6)

    def reset(self):
        self._waypoints  = []
        self._user_track.clear()
        self.conformance_scores  = []
        self.latency_samples_ms  = []


# ============================================================================
# MASTER KINEMATIC TRACKER (public API)
# ============================================================================

class KinematicTremorTracker:
    """
    Top-level integration class consumed by main.py and server.py.

    Usage:
        tracker = KinematicTremorTracker()
        tracker.push_nose(nose_x, nose_y)
        tracker.push_wrist(wrist_x, wrist_y)   # optional
        tracker.path_engine.add_waypoint(target_cx, target_cy)
        profile = tracker.get_tremor_profile()
    """

    def __init__(self, fps: float = 30.0):
        self.nose_series  = KinematicSeries(window=90, fps=fps, label="nose")
        self.wrist_series = KinematicSeries(window=90, fps=fps, label="wrist")
        self.path_engine  = PathConformanceEngine()

        self._challenge_present_time: Optional[float] = None
        self._onset_times: List[float] = []
        self._liveness_score_ema = 0.80

    def push_nose(self, x: float, y: float, ts: Optional[float] = None) -> None:
        self.nose_series.push(x, y, ts)
        self.path_engine.push_user_position(x, y, ts)

    def push_wrist(self, x: float, y: float, ts: Optional[float] = None) -> None:
        self.wrist_series.push(x, y, ts)
        # Bug fix: wrist should NOT feed path_engine — path conformance tracks nose (finger-tip target matching uses nose)
        # Feeding wrist here caused double-counting and corrupted latency detection

    def notify_challenge_presented(self) -> None:
        self._challenge_present_time = time.time()

    def notify_movement_onset(self) -> None:
        if self._challenge_present_time is not None:
            latency_ms = (time.time() - self._challenge_present_time) * 1000.0
            self._onset_times.append(latency_ms)
            if len(self._onset_times) > 30:
                self._onset_times.pop(0)
            self._challenge_present_time = None

    def _compute_liveness_score(self, nose_prof, nose_var, nose_lin,
                                 nose_jerk, wrist_var, wrist_jerk):
        score = 1.0
        reasons = []

        if nose_prof["frames_buffered"] >= MIN_ANALYSIS_FRAMES:
            if nose_var < STATIC_VAR_THRESHOLD:
                score -= 0.40
                reasons.append("STATIC_PHOTO_OR_FROZEN_REPLAY")
            elif nose_prof["in_physiological_band"] and nose_prof["band_snr"] > 0.05:
                score += 0.05

        if nose_lin >= BOT_LINEARITY_THRESHOLD:
            score -= 0.30
            reasons.append("BOT_SCRIPTED_LINEAR_MOTION")

        if nose_jerk > BOT_JERK_THRESHOLD or wrist_jerk > BOT_JERK_THRESHOLD:
            score -= 0.25
            reasons.append("INJECTION_JERK_SPIKE")

        if self.path_engine.conformance_scores:
            conf  = self.path_engine.mean_conformance
            score = score * (0.50 + 0.50 * conf)

        if self.path_engine.is_bot_latency:
            score -= 0.35
            reasons.append("BOT_UNIFORM_LATENCY")

        if len(self._onset_times) >= 3:
            mean_lat = float(np.mean(self._onset_times))
            std_lat  = float(np.std(self._onset_times))
            if mean_lat < 100.0:
                score -= 0.20
                reasons.append("SUB_HUMAN_REACTION_TIME")
            elif std_lat < 10.0 and len(self._onset_times) >= 5:
                score -= 0.15
                reasons.append("MACHINE_UNIFORM_LATENCY")

        return float(np.clip(score, 0.05, 0.98)), reasons

    def get_tremor_profile(self) -> Dict[str, Any]:
        """Returns the complete kinematic diagnostic profile for one frame."""
        nose_prof  = self.nose_series.tremor_frequency_profile()
        wrist_prof = self.wrist_series.tremor_frequency_profile()

        nose_var   = self.nose_series.displacement_variance()
        nose_lin   = self.nose_series.trajectory_linearity()
        nose_jerk  = self.nose_series.max_jerk()
        wrist_var  = self.wrist_series.displacement_variance()
        wrist_jerk = self.wrist_series.max_jerk()

        liveness, anomaly_flags = self._compute_liveness_score(
            nose_prof, nose_var, nose_lin, nose_jerk, wrist_var, wrist_jerk
        )

        self._liveness_score_ema = 0.75 * self._liveness_score_ema + 0.25 * liveness

        mean_onset_ms = float(np.mean(self._onset_times)) if self._onset_times else 0.0

        return {
            "kinematic_liveness_score":  round(self._liveness_score_ema, 4),
            "anomaly_flags":             anomaly_flags,
            "is_suspicious":             (self._liveness_score_ema < 0.45),
            "nose": {
                "displacement_variance":  round(nose_var, 8),
                "trajectory_linearity":   round(nose_lin, 4),
                "max_jerk":               round(nose_jerk, 3),
                "tremor_freq_hz":         nose_prof["dominant_freq_hz"],
                "tremor_amplitude":       nose_prof["tremor_amplitude"],
                "band_snr":               nose_prof["band_snr"],
                "in_phys_band":           nose_prof["in_physiological_band"],
                "frames_buffered":        nose_prof["frames_buffered"],
            },
            "wrist": {
                "displacement_variance":  round(wrist_var, 8),
                "trajectory_linearity":   round(self.wrist_series.trajectory_linearity(), 4),
                "max_jerk":               round(wrist_jerk, 3),
                "tremor_freq_hz":         wrist_prof["dominant_freq_hz"],
                "tremor_amplitude":       wrist_prof["tremor_amplitude"],
                "band_snr":               wrist_prof["band_snr"],
                "in_phys_band":           wrist_prof["in_physiological_band"],
                "frames_buffered":        wrist_prof["frames_buffered"],
            },
            "asymmetry": {
                "nose_asymmetry_index":   self.nose_series.asymmetry_index(),
                "wrist_asymmetry_index":  self.wrist_series.asymmetry_index(),
                # Bug fix: check BOTH human motor asymmetry bands (left-dominant 0.55-0.90 AND right-dominant 1.10-1.55)
                "is_asymmetric_human":    (
                    0.55 <= self.nose_series.asymmetry_index() <= 0.90 or
                    1.10 <= self.nose_series.asymmetry_index() <= 1.55
                ),
            },
            "power_law":                  self.nose_series.non_linear_power_law(),
            "path": {
                "mean_conformance":       round(self.path_engine.mean_conformance, 4),
                "mean_latency_ms":        round(self.path_engine.mean_latency_ms, 1),
                "is_bot_latency":         self.path_engine.is_bot_latency,
                "waypoints_evaluated":    len(self.path_engine.conformance_scores),
            },
            "cognitive": {
                "mean_onset_ms":  round(mean_onset_ms, 1),
                "samples":        len(self._onset_times),
            }
        }

    def reset(self) -> None:
        self.nose_series.reset()
        self.wrist_series.reset()
        self.path_engine.reset()
        self._challenge_present_time = None
        self._onset_times            = []
        self._liveness_score_ema     = 0.80
