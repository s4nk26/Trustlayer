"""
=============================================================================
rPPG CONTACTLESS PULSE & BLOOD FLOW LIVENESS DETECTION MODULE
TrustLayer: Human Verification for the AI Era
Zeal College of Engineering & Research, Pune-41
Department of Electronics and Computer Engineering

Scientific Principle:
- Remote Photoplethysmography (rPPG): Hemoglobin in facial capillaries absorbs
  green-spectrum ambient light (~540nm) during systolic pulse waves.
- Tracks micro-chromatic skin color fluctuations in forehead & cheek ROIs.
- Computes Blood Volume Pulse (BVP), Heart Rate (BPM), and Spectral SNR.
- Detects synthetic deepfakes, 3D masks, and photo/video replays (which lack biological pulse).
=============================================================================
"""

import math
import time
import numpy as np
import cv2


class rPPGLivenessDetector:
    def __init__(self, buffer_size: int = 150, fps: float = 30.0):
        """
        buffer_size: Number of frames in sliding window (~5 seconds of video at 30 FPS)
        fps: Sampling rate / frame rate
        """
        self.buffer_size = buffer_size
        self.fps = fps
        
        # Raw RGB signal buffers from facial skin ROI
        self.r_buffer = []
        self.g_buffer = []
        self.b_buffer = []
        self.timestamps = []
        
        # Processed BVP waveform & heart rate state
        self.bvp_signal = []
        self.bpm = 0.0
        self.bpm_history = []
        self.snr = 0.0
        self.is_pulse_valid = False
        self.liveness_score = 0.5

        # MediaPipe landmark indices for clean skin sampling
        self.FOREHEAD_ROI_IDS = [10, 67, 109, 108, 151, 9, 8, 337, 338, 297]
        self.LEFT_CHEEK_ROI_IDS = [117, 118, 101, 205, 50, 123, 147, 187]
        self.RIGHT_CHEEK_ROI_IDS = [346, 347, 330, 425, 280, 352, 376, 411]

    def _extract_skin_channel_means(self, frame_bgr: np.ndarray, landmarks) -> tuple[float, float, float]:
        """
        Extracts mean Blue, Green, Red intensities from facial skin regions.
        """
        h, w = frame_bgr.shape[:2]
        roi_ids = self.FOREHEAD_ROI_IDS + self.LEFT_CHEEK_ROI_IDS + self.RIGHT_CHEEK_ROI_IDS

        pts = []
        for idx in roi_ids:
            lm = landmarks[idx]
            px = int(np.clip(lm.x * w, 0, w - 1))
            py = int(np.clip(lm.y * h, 0, h - 1))
            pts.append((px, py))

        if not pts:
            return 0.0, 0.0, 0.0

        mask = np.zeros((h, w), dtype=np.uint8)
        for px, py in pts:
            cv2.circle(mask, (px, py), 6, 255, -1)

        mean_bgr = cv2.mean(frame_bgr, mask=mask)[:3]
        return float(mean_bgr[0]), float(mean_bgr[1]), float(mean_bgr[2])

    def _apply_chrom_method(self, r_arr: np.ndarray, g_arr: np.ndarray, b_arr: np.ndarray) -> np.ndarray:
        """
        Chrominance-based rPPG method (de Haan & Jeanne, 2013).
        Eliminates specular reflection and motion artifacts by projecting RGB
        into color difference planes orthogonal to skin tone.
        """
        # Temporal normalization
        mean_r = np.mean(r_arr)
        mean_g = np.mean(g_arr)
        mean_b = np.mean(b_arr)

        if mean_r < 1e-4 or mean_g < 1e-4 or mean_b < 1e-4:
            return np.zeros_like(r_arr)

        r_norm = r_arr / mean_r
        g_norm = g_arr / mean_g
        b_norm = b_arr / mean_b

        # Chrominance projection signals
        # Xs = 3*Rn - 2*Gn
        # Ys = 1.5*Rn + Gn - 1.5*Bn
        xs = 3.0 * r_norm - 2.0 * g_norm
        ys = 1.5 * r_norm + g_norm - 1.5 * b_norm

        std_xs = np.std(xs)
        std_ys = np.std(ys)

        if std_ys < 1e-6:
            alpha = 0.0
        else:
            alpha = std_xs / std_ys

        # Blood Volume Pulse (BVP) signal
        bvp = xs - alpha * ys
        return bvp

    def _bandpass_filter(self, signal: np.ndarray, low_hz: float = 0.75, high_hz: float = 2.5) -> np.ndarray:
        """
        Zero-phase FFT bandpass filter selecting physiological human heart rates:
        0.75 Hz (45 BPM) to 2.5 Hz (150 BPM).
        """
        n = len(signal)
        if n < 30:
            return signal - np.mean(signal)

        # FFT
        f = np.fft.rfft(signal - np.mean(signal))
        freqs = np.fft.rfftfreq(n, d=1.0 / self.fps)

        # Bandpass mask
        bandpass_mask = (freqs >= low_hz) & (freqs <= high_hz)
        f_filtered = f * bandpass_mask

        # Inverse FFT
        filtered_signal = np.fft.irfft(f_filtered, n=n)
        return filtered_signal

    def _estimate_heart_rate(self, bvp_filtered: np.ndarray) -> tuple[float, float]:
        """
        Extracts dominant peak frequency and Signal-to-Noise Ratio (SNR).
        Returns: (BPM, SNR)
        """
        n = len(bvp_filtered)
        if n < 40:
            return 0.0, 0.0

        fft_mag = np.abs(np.fft.rfft(bvp_filtered)) ** 2
        freqs = np.fft.rfftfreq(n, d=1.0 / self.fps)

        # Focus within physiological window (48 BPM - 140 BPM)
        valid_mask = (freqs >= 0.8) & (freqs <= 2.33)
        if not np.any(valid_mask):
            return 0.0, 0.0

        valid_freqs = freqs[valid_mask]
        valid_mags = fft_mag[valid_mask]

        max_idx = np.argmax(valid_mags)
        peak_freq = valid_freqs[max_idx]
        peak_power = valid_mags[max_idx]
        total_power = np.sum(valid_mags)

        bpm = peak_freq * 60.0
        # Signal to Noise Ratio in band
        snr = float(peak_power / max(total_power - peak_power, 1e-5))

        return bpm, snr

    def update(self, frame_bgr: np.ndarray, landmarks) -> dict:
        """
        Processes each video frame, updates the sliding window, and computes rPPG metrics.
        """
        if landmarks is None:
            return {
                "detected": False,
                "bpm": self.bpm,
                "snr": self.snr,
                "is_pulse_valid": self.is_pulse_valid,
                "liveness_score": self.liveness_score,
                "bvp_waveform": []
            }

        now = time.time()
        b_val, g_val, r_val = self._extract_skin_channel_means(frame_bgr, landmarks)

        self.b_buffer.append(b_val)
        self.g_buffer.append(g_val)
        self.r_buffer.append(r_val)
        self.timestamps.append(now)

        if len(self.r_buffer) > self.buffer_size:
            self.b_buffer.pop(0)
            self.g_buffer.pop(0)
            self.r_buffer.pop(0)
            self.timestamps.pop(0)

        # Estimate effective FPS from actual timestamps
        if len(self.timestamps) >= 10:
            total_time = self.timestamps[-1] - self.timestamps[0]
            if total_time > 0:
                self.fps = (len(self.timestamps) - 1) / total_time

        # If enough frames are buffered (~2.0 seconds minimum)
        if len(self.r_buffer) >= 60:
            r_arr = np.array(self.r_buffer, dtype=np.float32)
            g_arr = np.array(self.g_buffer, dtype=np.float32)
            b_arr = np.array(self.b_buffer, dtype=np.float32)

            # 1. Chrominance BVP extraction
            raw_bvp = self._apply_chrom_method(r_arr, g_arr, b_arr)

            # 2. Physiological Bandpass filter (45 - 150 BPM)
            filtered_bvp = self._bandpass_filter(raw_bvp, low_hz=0.75, high_hz=2.5)
            self.bvp_signal = filtered_bvp.tolist()

            # 3. Peak Frequency & SNR Heart Rate Estimation
            est_bpm, snr = self._estimate_heart_rate(filtered_bvp)

            if 50.0 <= est_bpm <= 130.0 and snr > 0.15:
                self.bpm = 0.7 * self.bpm + 0.3 * est_bpm if self.bpm > 0 else est_bpm
                self.snr = snr
                self.is_pulse_valid = True
                self.liveness_score = min(0.98, max(0.75, 0.70 + (min(snr, 2.0) * 0.14)))
                self.bpm_history.append(self.bpm)
                if len(self.bpm_history) > 30:
                    self.bpm_history.pop(0)
            else:
                self.is_pulse_valid = False
                self.liveness_score = 0.40

        return {
            "detected": True,
            "bpm": round(self.bpm, 1),
            "snr": round(self.snr, 2),
            "is_pulse_valid": self.is_pulse_valid,
            "liveness_score": round(self.liveness_score, 2),
            "buffer_fill_pct": min(1.0, len(self.r_buffer) / self.buffer_size),
            "bvp_waveform": self.bvp_signal[-60:] if self.bvp_signal else []
        }

    def render_pulse_hud(self, frame: np.ndarray, x: int = 20, y: int = 20, w: int = 280, h: int = 110):
        """
        Renders an ECG / Pulse Waveform on the OpenCV frame.
        """
        overlay = frame.copy()
        cv2.rectangle(overlay, (x, y), (x + w, y + h), (20, 20, 26), -1)
        cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (50, 50, 60), 1)

        # Status & BPM Text
        if self.is_pulse_valid:
            pulse_col = (80, 230, 80)
            status_text = f"PULSE: {int(self.bpm)} BPM [AUTHENTIC]"
        else:
            pulse_col = (0, 180, 255)
            status_text = "PULSE: ACQUIRING BVP..."

        cv2.putText(frame, "rPPG BLOOD FLOW LIVENESS", (x + 12, y + 22), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 220, 255), 1)
        cv2.putText(frame, status_text, (x + 12, y + 44), cv2.FONT_HERSHEY_SIMPLEX, 0.48, pulse_col, 2)

        # Render waveform line
        if len(self.bvp_signal) >= 20:
            samples = self.bvp_signal[-50:]
            min_v, max_v = min(samples), max(samples)
            spread = max_v - min_v if (max_v - min_v) > 1e-5 else 1.0

            graph_y_center = y + 78
            graph_h = 24

            pts = []
            step_x = (w - 24) / max(1, len(samples) - 1)
            for i, val in enumerate(samples):
                norm_val = (val - min_v) / spread
                px = int(x + 12 + i * step_x)
                py = int(graph_y_center - (norm_val - 0.5) * graph_h)
                pts.append((px, py))

            for i in range(len(pts) - 1):
                cv2.line(frame, pts[i], pts[i + 1], pulse_col, 2)
        else:
            cv2.putText(frame, "Buffering facial capillaries...", (x + 12, y + 80), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (140, 140, 150), 1)

    def reset(self):
        self.r_buffer = []
        self.g_buffer = []
        self.b_buffer = []
        self.timestamps = []
        self.bvp_signal = []
        self.bpm = 0.0
        self.snr = 0.0
        self.is_pulse_valid = False
