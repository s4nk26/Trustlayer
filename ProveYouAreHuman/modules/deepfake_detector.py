"""
Deepfake & Anti-Spoofing Artifact Detection Module (Calibrated)
TrustLayer: Human Verification for the AI Era
Zeal College of Engineering & Research, Pune-41

Calibrated for realistic webcams, diverse lighting conditions, and robust temporal smoothing.
"""

import math
import cv2
import numpy as np


class DeepfakeArtifactDetector:
    def __init__(self):
        # Rolling temporal buffers
        self.auth_scores = []
        self.fft_history = []
        self.laplacian_history = []
        self.moire_peaks = []
        self.max_buffer = 40
        
        # Calibrated realistic thresholds
        self.MIN_LAPLACIAN_VAR = 18.0      # Lowered for soft indoor lighting
        self.MAX_LAPLACIAN_VAR = 1200.0    # Accommodate HD webcams
        self.MAX_SCREEN_PEAK_RATIO = 8.5   # True screen Moire has high periodic peaks (>8.5)
        self.MIN_CHROMINANCE_VAR = 4.5     # Handles indoor LED/CFL lighting & white balance

    def compute_fft_metrics(self, face_gray):
        """
        Calculates 2D FFT Power Spectrum, High-Frequency Spectral Ratio (HFSR),
        and Screen Moire Periodic Spike Prominence.
        """
        h, w = face_gray.shape
        if h < 32 or w < 32:
            return 0.5, 0.0, None

        # Resize to standard size for consistent frequency analysis
        resized = cv2.resize(face_gray, (128, 128)).astype(np.float32)
        
        # Apply Hanning window
        hann_2d = np.outer(np.hanning(128), np.hanning(128))
        windowed = (resized - np.mean(resized)) * hann_2d

        # 2D FFT
        f = np.fft.fft2(windowed)
        fshift = np.fft.fftshift(f)
        magnitude_spectrum = np.abs(fshift)
        power_spectrum = magnitude_spectrum ** 2

        # Radial masks
        center_y, center_x = 64, 64
        y, x = np.ogrid[:128, :128]
        dist_from_center = np.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)

        low_med_mask = (dist_from_center < 35) & (dist_from_center > 4)
        high_mask = (dist_from_center >= 35) & (dist_from_center <= 60)

        low_med_energy = np.sum(power_spectrum[low_med_mask])
        high_energy = np.sum(power_spectrum[high_mask])

        hfsr = high_energy / max(low_med_energy, 1e-5)

        # Detect periodic spikes (Screen Moire grid lines)
        high_freq_vals = power_spectrum[high_mask]
        mean_hf = np.mean(high_freq_vals)
        max_hf = np.max(high_freq_vals)
        peak_prominence = max_hf / max(mean_hf, 1e-5)

        # Color visualization of magnitude spectrum
        vis_spec = 20 * np.log(magnitude_spectrum + 1e-5)
        vis_norm = cv2.normalize(vis_spec, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        vis_color = cv2.applyColorMap(vis_norm, cv2.COLORMAP_MAGMA)

        return float(hfsr), float(peak_prominence), vis_color

    def compute_texture_metrics(self, face_bgr):
        """
        Calculates Laplacian variance (sharpness/focus).
        """
        gray = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2GRAY)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        lap_var = float(laplacian.var())
        return lap_var

    def compute_color_consistency(self, face_bgr):
        """
        Calculates chrominance distribution in YCrCb color space.
        """
        ycrcb = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2YCrCb)
        _, cr, cb = cv2.split(ycrcb)
        cr_std = float(np.std(cr))
        cb_std = float(np.std(cb))
        chroma_var = (cr_std + cb_std) / 2.0
        return chroma_var

    def analyze_face(self, bgr_frame, face_box):
        """
        Performs deepfake and anti-spoofing analysis with temporal smoothing.
        """
        if face_box is None:
            # If face is momentarily occluded, return smoothed average from history
            smoothed_auth = np.mean(self.auth_scores) if self.auth_scores else 0.85
            return {
                "authenticity_score": float(smoothed_auth),
                "fft_hfsr": 0.1,
                "moire_peak": 2.0,
                "laplacian_var": 80.0,
                "chroma_var": 10.0,
                "flags": [],
                "fft_vis": None
            }

        x, y, w, h = face_box
        fh, fw = bgr_frame.shape[:2]
        
        x1, y1 = max(0, x), max(0, y)
        x2, y2 = min(fw, x + w), min(fh, y + h)

        if (x2 - x1) < 40 or (y2 - y1) < 40:
            smoothed_auth = np.mean(self.auth_scores) if self.auth_scores else 0.85
            return {
                "authenticity_score": float(smoothed_auth),
                "fft_hfsr": 0.1,
                "moire_peak": 2.0,
                "laplacian_var": 80.0,
                "chroma_var": 10.0,
                "flags": [],
                "fft_vis": None
            }

        face_roi = bgr_frame[y1:y2, x1:x2]
        face_gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)

        # 1. FFT Metrics
        hfsr, moire_peak, fft_vis = self.compute_fft_metrics(face_gray)

        # 2. Texture & Laplacian
        lap_var = self.compute_texture_metrics(face_roi)

        # 3. Color consistency
        chroma_var = self.compute_color_consistency(face_roi)

        # Track history
        self.fft_history.append(hfsr)
        self.laplacian_history.append(lap_var)
        self.moire_peaks.append(moire_peak)

        if len(self.fft_history) > self.max_buffer:
            self.fft_history.pop(0)
            self.laplacian_history.pop(0)
            self.moire_peaks.pop(0)

        # Frame Authenticity Evaluation
        frame_score = 0.95
        flags = []

        # Persistent Screen Moire check (>8.5 peak ratio in multiple frames)
        avg_moire = np.mean(self.moire_peaks[-5:]) if len(self.moire_peaks) >= 5 else moire_peak
        if avg_moire > self.MAX_SCREEN_PEAK_RATIO:
            flags.append("SCREEN_MOIRE_GRID_DETECTED")
            frame_score -= 0.35

        # Extreme blur check
        if lap_var < self.MIN_LAPLACIAN_VAR:
            flags.append("SYNTHETIC_SMOOTHING_OR_BLUR")
            frame_score -= 0.25

        # Extreme chrominance flatness
        if chroma_var < self.MIN_CHROMINANCE_VAR:
            flags.append("FLAT_CHROMINANCE_DISTRIBUTION")
            frame_score -= 0.15

        frame_score = max(0.1, min(0.98, frame_score))

        # Temporal smoothing
        self.auth_scores.append(frame_score)
        if len(self.auth_scores) > self.max_buffer:
            self.auth_scores.pop(0)

        smoothed_auth = float(np.mean(self.auth_scores))

        return {
            "authenticity_score": smoothed_auth,
            "fft_hfsr": hfsr,
            "moire_peak": moire_peak,
            "laplacian_var": lap_var,
            "chroma_var": chroma_var,
            "flags": flags,
            "fft_vis": fft_vis
        }

    def reset(self):
        self.auth_scores = []
        self.fft_history = []
        self.laplacian_history = []
        self.moire_peaks = []
