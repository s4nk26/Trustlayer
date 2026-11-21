# TrustLayer: AI-Powered Real-Time Human Verification & Deepfake Detection

**Project Based Learning (PBL) - Project Synopsis & System Implementation**  
*Zeal Education Society's Zeal College of Engineering & Research, Pune-41*  
*Department of Electronics and Computer Engineering*

---

## 👥 Team Members
1. **Sandesh Kolhe** (Roll No: EC2212 | ZPRN: 125UEC1017)
2. **Sanket Shinde** (Roll No: EC2209 | ZPRN: 125UEC1162)
3. **Rajnandini Mane** (Roll No: EC2202 | ZPRN: 125UEC1145)

**Project Guide:** Prof. Sana A. Metkari  
**HOD:** Dr. Mahesh S. Navale

---

## 🌟 Core System Highlights

### 1. 📊 Full Admin & Analytics Web Dashboard (`/dashboard`)
* **URL:** `http://localhost:8000/dashboard`
* **Real-Time KPIs:** Total Verifications, Pass Rate %, Average Multi-Factor Score, Average Latency.
* **Visual Breakdown:** Pass/Suspicious/Failed classification ratios and confidence score distributions.
* **Session Audit Log:** Interactive searchable/filterable table of all sessions saved in SQLite (`verifications.db`).
* **Certificate Viewer Modal:** Instantly inspect, review, or print official audit certificates with sub-scores and challenge trails.

### 2. ❤️ rPPG Contactless Blood Flow Pulse Liveness (`modules/rppg_liveness.py`)
* **Remote Photoplethysmography (rPPG):** Measures micro-chromatic absorption of green light (~540nm) by hemoglobin in facial capillaries.
* **De Haan & Jeanne Chrominance (CHROM) Projection:** Projects normalized RGB skin signals orthogonal to skin tone to eliminate motion artifacts.
* **Bandpass Filtering & FFT Peak Extraction:** Isolates biological heart rate (45–150 BPM) and computes Signal-to-Noise Ratio (SNR).
* **Anti-Deepfake Defense:** 3D silicone masks, printed photos, and synthetic AI deepfakes lack biological blood flow, triggering spoof alerts.

### 3. 🛡️ Active Screen Flash Reflection Defense (`anti_spoofing.py`)
* Emits 400ms narrowband chromatic flash pulses (`#00FFCC`, `#FF007F`, etc.) to measure diffuse skin reflection vs. target color vector (cosine similarity), blocking virtual camera injections and prerecorded video replays.

### 4. 🌐 FastAPI WebSocket Verification Server (`server.py`)
* **Live Client Portal:** `http://localhost:8000/client`
* **WebSocket Endpoint:** `ws://localhost:8000/ws/verify`

## 🚀 Dual Verification Architecture: System 1 & System 2

TrustLayer provides two independent, coexisting verification architectures:

### ⚡ System 1: Standard Verification Audit (Finite 3 Challenges + Final Certificate)
* **Goal**: Conducts a structured biometric audit, guides the user through 3 dynamic challenges, evaluates multi-factor scoring fusion, and displays the **Official Verdict Certificate** (VERIFIED HUMAN / SUSPICIOUS / FAILED) with sub-scores.
* **Outputs**: Automatically generates JSON audit records, HTML audit reports, and PNG certificate cards in the `reports/` directory and SQLite database.
* **How to run Desktop**:
  ```powershell
  python main.py --mode standard
  # Or double-click: run_system1_standard.bat
  ```
* **How to run Web**: Click the **System 1: Standard Verification** tab on `http://localhost:8000/client`.

---

### 🟢 System 2: Live Continuous Shield (24/7 Vector Telemetry & Low Bar Alert)
* **Goal**: Runs continuously without an end-state completion screen. Continuously evaluates biological micro-jitter, 3D spatial parallax, and cognitive latency using real-time mathematical vector graphs.
* **Behavior**: Displays the **Master Live Human Trust Bar** (96% Verified Green). Only when a metric bar drops low (e.g. flat 2D replay, static photo jitter < 0.00010, face lost) does it trigger **`⚠️ SUSPICIOUS: NO HUMAN DETECTED`** and a crimson alert border.
* **How to run Desktop**:
  ```powershell
  python main.py --mode live
  # Or double-click: run_system2_live.bat
  ```
* **How to run Web**: Click the **System 2: Live Continuous Shield** tab on `http://localhost:8000/client`.

---

## 🎮 Desktop Keyboard Controls (`main.py`)
* `[M]` : **Switch Mode** instantaneously between **System 1 (Standard Audit)** and **System 2 (Live Shield)**.
* `[R]` : **Reset / Restart** the active verification session.
* `[S]` : **Save / Export** audit report and summary certificate.
* `[Q]` : **Quit** the application.

---

## 📊 Admin Analytics Dashboard (`/dashboard`)
* **URL:** `http://localhost:8000/dashboard`
* **Real-Time KPIs:** Total Verifications, Pass Rate %, Average Multi-Factor Score, Average Latency.
* **Visual Breakdown:** Pass/Suspicious/Failed classification ratios and confidence score distributions.
* **Session Audit Log:** Interactive searchable/filterable table of all sessions saved in SQLite (`verifications.db`).
* **Certificate Viewer Modal:** Instantly inspect, review, or print official audit certificates with sub-scores and challenge trails.

