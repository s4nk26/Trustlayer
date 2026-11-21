# Zeal Education Society’s
## ZEAL COLLEGE OF ENGINEERING & RESEARCH, PUNE-41
**(An Autonomous Institute Affiliated to Savitribai Phule Pune University)**  
*NBA Accredited, NAAC Accredited with A+ Grade / ISO 21001:2018*  
### DEPARTMENT OF ELECTRONICS AND COMPUTER ENGINEERING
### PROJECT BASED LEARNING (PBL)
---
# PROJECT SYNOPSIS

---

### 1. Project Title:
**TrustLayer: Dual-Engine Kinematic Human Verification and Continuous Passive Biosignal Monitoring for the Generative AI Era**

---

### 2. Team Members:

| Sr. No. | Name of Student | Roll No. | ZPRN |
| :---: | :--- | :---: | :---: |
| **1** | Sandesh Kolhe | EC2212 | 125UEC1017 |
| **2** | Sanket Shinde | EC2209 | 125UEC1162 |
| **3** | Rajnandini Mane | EC2202 | 125UEC1145 |

---

### 3. Domain:
**Selected Domain:** Artificial Intelligence, Machine Learning, Computer Vision, Cyber Security, Digital Signal Processing (DSP), and Modern Web Applications.

---

### 4. Introduction:
The rapid proliferation of Generative Artificial Intelligence (GenAI), diffusion-based facial reenactment models, neural voice cloning, and virtual camera video injection drivers has introduced existential threats to remote digital authentication. Traditional authentication vectors such as static facial recognition, passwords, and SMS/TOTP one-time passwords verify *identity credentials* rather than physical *human presence*. Consequently, remote banking (e-KYC), proctored online examinations, remote interviews, and corporate video conferencing are acutely vulnerable to deepfake injection, printed/screen photo spoofing, and video replay attacks.

**TrustLayer** addresses these security vectors through a dual-engine human authentication framework:
1. **Engine 1: Active Multimodal Kinematic Challenge-Response Verification** — Executes a randomized, non-repeatable sequence comprising rapid head rotations, simultaneous facial-finger coordinated actions, randomized alphanumeric code dictation with phoneme-to-viseme lip synchronization ($MAR$), and dynamic 3D air-drawing trajectory tracing (Star, Infinity, Square) evaluated against human motor control laws (Two-Thirds Power Law $v \propto \kappa^{-1/3}$).
2. **Engine 2: Continuous Passive Bio-Kinematic Live Monitoring** — Designed for sustained sessions (online exams, confidential video streams) where active challenges cease upon initial clearance. The engine transitions completely into silent, non-intrusive background telemetry, continuously validating remote photoplethysmography (rPPG) capillary pulse waveforms, 6–12 Hz involuntary micro-tremors, 2D FFT Moiré screen artifact detection, and 3D depth parallax to prevent camera hijacking, looped video replay, or static photo presentations.

The system computes an aggregate **Human Verification Index (HVI)**, classifying interactions into **Verified Human**, **Suspicious Interaction**, or **Replay/Spoof Attack Detected**.

---

### 5. Problem Statement:
Existing authentication systems suffer from three critical architectural vulnerabilities:
1. **Static and Predictable Liveness Deficits:** Conventional systems rely on isolated, predictable challenges (e.g., standard blinking or smiling), allowing adversaries to construct pre-rendered conditional deepfakes or trigger replayed video loops.
2. **Susceptibility to Presentation & Screen Replays:** Standard computer vision models fail to discriminate between a genuine human face and a high-resolution smartphone/tablet screen displaying a prerecorded selfie video or high-definition photograph.
3. **Absence of Continuous Session Integrity:** Most platforms authenticate once at login and remain blind to mid-session impersonation or virtual camera injection hijacking during examinations or video calls.

Therefore, an urgent need exists for a real-time, low-latency, dual-split verification system capable of enforcing randomized multi-limb biomechanical challenges at entry, followed by continuous, passive, non-intrusive biological telemetry during live operation.

---

### 6. Objectives:
1. **To eliminate replay attacks** by engineering randomized, system-generated multimodal challenge sequences (rotational head poses, hand-face gestures, and 7–8 character alphanumeric code vocalizations).
2. **To validate biological motor control** in air-drawing trajectories using the kinematic Two-Thirds Power Law ($v = \alpha \cdot \kappa^{-\beta}$) and motor asymmetry analysis.
3. **To detect digital screen presentation attacks** using 2D Fast Fourier Transform (FFT) high-frequency Moiré spectral peak ratios and subpixel grid analysis.
4. **To separate handheld device shaking from biological vitality** by inspecting intrinsic involuntary micro-nystagmus ($std(EAR)$) and resting lip micro-variations ($std(MAR)$).
5. **To provide continuous, non-intrusive live monitoring** for proctored environments via contactless facial rPPG pulse extraction and 6–12 Hz micro-tremor tracking without prompting the user with repeated tasks.
6. **To implement a low-latency, responsive web architecture** using FastAPI, asynchronous WebSockets, and OpenCV/MediaPipe for real-time edge-to-server inference under 35 ms frame latency.

---

### 7. Literature Survey & Research Gap:

| Author(s) & Year | Proposed Methodology | Identified Limitations |
| :--- | :--- | :--- |
| **Kollreider et al. (2007)** | Optical flow field evaluation for facial motion and blink detection. | Vulnerable to 2D photographic warping and print cutouts. |
| **Pan et al. (2007)** | Real-time eye-blink sequence analysis using Conditional Random Fields. | Easily bypassed by looping a 3-second prerecorded video segment. |
| **Li et al. (2020) — Face X-Ray** | Detects blending boundaries between manipulated faces and background images. | Struggles with fully synthesized end-to-end diffusion faces where no blending boundary exists. |
| **Ahmed et al. (2023)** | Randomized facial prompt-response framework. | Lacks multi-limb coordination; relies solely on facial movement, allowing replay stitching. |
| **Zheng et al. (2025) — D3** | Training-free AI-generated video detection via second-order spatial features. | Computationally heavy for real-time browser streams (>120 ms latency per frame). |

**Research Gap:**  
Prior research treats facial liveness, speech verification, and continuous monitoring as disjointed systems. Crucially, existing methods ignore **multi-effector kinematic coupling** (e.g., coordinating facial expressions with hand digits) and the **invariant physical laws of human neuromuscular motor execution** (Two-Thirds Power Law in hand kinematics). Furthermore, existing solutions lack a split architecture that seamlessly pivots from active onboarding verification to silent, passive live proctoring.

---

### 8. Proposed System Architecture (Dual-Split Framework):

TrustLayer splits the authentication pipeline into two operational modes:

```
                            +-----------------------------------------+
                            |       Live Video & Audio Ingestion      |
                            |       (Webcam + Web Audio via WS)       |
                            +--------------------+--------------------+
                                                 |
                                                 v
                            +-----------------------------------------+
                            |       Anti-Spoofing & Replay Guard      |
                            |   * 2D FFT Moiré Screen Peak Detector   |
                            |   * 3D Depth Parallax vs 2D Flat Plane  |
                            |   * Micro-Nystagmus Involuntary Jitter  |
                            +--------------------+--------------------+
                                                 |
                         +-----------------------+-----------------------+
                         |                                               |
                         v                                               v
       [SYSTEM 1: Active Verification]                 [SYSTEM 2: Live Monitor Guardian]
       (Onboarding / Entrance Gate)                    (Exams / Video Call Proctoring)
                         |                                               |
  1. Head Pose Invariant (Yaw/Pitch)              1. Silent Background Telemetry
     * Short 6.0s timeout, 0.75s hold                * ZERO prompts or user interruptions
  2. Multi-Effector Gesture (10.0s)               2. Capillary rPPG Pulse Waveform
     * Blink + Hand Digit Transition                 * Temporal green-channel chrominance
  3. Phonetic Code Dictation (25.0s)              3. Involuntary 6-12 Hz Body Micro-Tremor
     * 7-8 char code + TTS + Viseme Sync             * Butterworth bandpass filter
  4. 3D Air-Drawing Kinematics (30.0s)            4. Anti-Freeze & Video Loop Guard
     * Star / Infinity / Square                      * Frame-to-frame SSIM & diff variance
     * Two-Thirds Power Law (v ~ κ^-1/3)                                 |
                         |                                               |
                         +-----------------------+-----------------------+
                                                 |
                                                 v
                            +-----------------------------------------+
                            |       Multimodal Scoring Engine         |
                            |       Human Verification Index (HVI)    |
                            |    Verified (>75%) | Suspicious | Failed |
                            +-----------------------------------------+
```

#### Detailed Breakdown of the Two Split Systems:

#### **Split 1: Active Multimodal Kinematic Challenge-Response (Onboarding Gate)**
* **Stage 1 — Rapid Head Pose Calibration (6s limit):** Directs the user to voluntarily tilt/turn head (Left, Right, Up, Down). Requires sustained angle threshold for 0.75s to verify natural vestibular kinetics.
* **Stage 2 — Multi-Effector Neuromuscular Coordination (10s limit):** Prompts simultaneous dual-limb action (e.g., *"Show 2 fingers, blink twice, then switch to 3 fingers"*). Deepfake video generators fail to coordinate multi-class landmark tracking across disparate regions simultaneously.
* **Stage 3 — Spoken Alphanumeric Code Reading (25s limit):** Prompts a randomized 7–8 character security string spoken aloud by Web Speech TTS. Evaluates phonetic speech-to-text transcript accuracy alongside mouth aspect ratio ($MAR$) cross-correlation to defeat static photo voice-overs.
* **Stage 4 — 3D Air-Drawing Shape Kinematics (30s limit):** Requires the user to trace a geometric shape (Star, Infinity, Square) in 3D air with their index fingertip. Evaluates:
  * Trajectory perimeter coverage ($\ge 70\%$).
  * The **Two-Thirds Power Law** ($v = \alpha \cdot \kappa^{-\beta}$), where movement slows inversely to trajectory curvature.
  * Natural biological motor asymmetry between ascending and descending strokes.

#### **Split 2: Continuous Passive Bio-Kinematic Live Monitoring (Proctoring/Video Call)**
* **Zero User Interruption:** Once the user clears Split 1, **all challenge tasks permanently cease**.
* **Remote Photoplethysmography (rPPG):** Measures sub-dermal blood absorption fluctuations in the facial forehead and cheek regions across the green color channel ($G$), extracting cardiac pulse waveforms ($0.75\text{--}2.5\text{ Hz}$).
* **Physiological Involuntary Micro-Tremor:** Monitors fine 6–12 Hz involuntary head and neck tremors via frequency domain bandpass filtering. Prerecorded video loops or frozen virtual camera frames exhibit zero or erratic spectral power in this biological band.
* **Screen Artifact & Replay Defense:** Continuous 2D FFT spectral analysis detects if a mobile phone or physical photograph is introduced into the frame mid-session.

---

### 9. Hardware and Software Requirements:

#### Hardware Requirements:
| Sr. No. | Component | Minimum Specification | Recommended Specification |
| :---: | :--- | :--- | :--- |
| **1** | Host Processor | Intel Core i5 / AMD Ryzen 5 (Dual-Core 2.4 GHz) | Intel Core i7 / AMD Ryzen 7 (Hexa-Core or higher) |
| **2** | System Memory (RAM) | 8 GB DDR4 | 16 GB DDR4/DDR5 |
| **3** | Optical Ingestion | Integrated HD Webcam (720p @ 30 FPS) | 1080p FHD Webcam @ 30–60 FPS |
| **4** | Audio Ingestion | Integrated Microphone Array | Omnidirectional Noise-Canceling Microphone |
| **5** | Network Interface | 2 Mbps broadband uplink | 10 Mbps low-jitter broadband uplink |

#### Software Requirements:
| Sr. No. | Software / Framework | Version | Purpose |
| :---: | :--- | :--- | :--- |
| **1** | Operating System | Windows 10/11 or Ubuntu 22.04 LTS | Core Host Environment |
| **2** | Programming Language | Python 3.10+ / ES6+ JavaScript | Core Backend & Frontend Development |
| **3** | Backend Web Framework | FastAPI (ASGI) + Uvicorn | High-throughput Asynchronous Microservice |
| **4** | Computer Vision Engine | OpenCV 4.10+ & MediaPipe 0.10+ | Real-time Facial (478 pts) & Hand (21 pts) Mesh Extraction |
| **5** | Digital Signal Processing | NumPy & SciPy | 2D FFT, Butterworth Bandpass Filtering, rPPG |
| **6** | Audio / Speech Pipeline | Web Speech API & SpeechRecognition | Local Speech-to-Text & Synthetic TTS Dictation |
| **7** | Client-Side Transport | Native HTML5 Canvas & WebSockets | Low-overhead 30 FPS Bi-directional Binary Streaming |

---

### 10. Technologies and Tools Used:
* **Languages:** Python, JavaScript (ES6+), HTML5, CSS3.
* **Libraries:** MediaPipe FaceLandmarker, MediaPipe HandLandmarker, OpenCV-Python, NumPy, SciPy Signal, FastAPI, WebSockets.
* **Architectural Protocols:** Full-Duplex WebSockets (`ws://`), RESTful API endpoints.
* **Development Tools:** Visual Studio Code, Git, GitHub, Chrome DevTools.

---

### 11. Expected Outcomes:
1. A fully functioning, production-ready web platform operating on localhost/cloud capable of accurately distinguishing real live humans from synthetic media.
2. Complete rejection of presentation spoofing attempts (e.g., displaying photos or selfie videos on mobile phone screens) via Fourier Moiré peak detection and micro-nystagmus verification.
3. Accurate evaluation of air-drawn geometric shapes against human biological motor control principles (Two-Thirds Power Law).
4. Seamless transition into passive, non-intrusive continuous live proctoring for examination and enterprise video environments without interrupting the participant.
5. Generation of real-time telemetry, session forensic logs, and an objective Human Verification Score (0–100%).

---

### 12. Scope of the Project:

#### Current Scope:
* Real-time dual-mode verification through any standard modern web browser without requiring third-party plugins.
* Robust defense against physical presentation attacks, 2D photograph prints, screen replay videos, and virtual camera software hijackers.
* Applicable to:
  * High-stakes remote online academic examinations.
  * Digital banking customer onboarding (Video KYC).
  * Remote hiring technical interviews and identity verification.
  * Defense against synthetic corporate espionage in executive video calls.

#### Future Scope:
* Multi-spectral infrared (IR) and depth (ToF) sensor fusion for mobile devices.
* Deep neural voice biometrics with synthetic vocoder artifact classification.
* Cryptographic Zero-Knowledge Proof (ZKP) attestation for privacy-preserving verification tokens.
* Integration into WebRTC conferencing stacks (Zoom, Google Meet, Microsoft Teams) as a native real-time security plugin.

---

### 13. References:
1. **Kollreider, K., Fronthaler, H., & Bigun, J. (2007).** Verifying liveness by evaluating dynamic facial traits. *IEEE Transactions on Information Forensics and Security*, 2(3), 521–531.
2. **Li, Y., & Lyu, S. (2018).** Exposing DeepFake Videos by Detecting Face Warping Artifacts. *arXiv preprint arXiv:1811.00656*.
3. **Li, L., Bao, J., Zhang, T., Yang, H., Chen, D., Wen, F., & Guo, B. (2020).** Face X-Ray for More General Face Forgery Detection. *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)*, 5001–5010.
4. **Xie, Y., & Luo, J. (2024).** Shaking the Fake: Exploring Involuntary Micro-tremor for Face Forgery Detection. *arXiv preprint arXiv:2409.10889*.
5. **Zheng, X., et al. (2025).** D3: Training-Free AI-Generated Video Detection Using Second-Order Features. *International Conference on Computer Vision (ICCV 2025)*.
6. **Mao, X., et al. (2021).** A Survey on Deepfake and Face Presentation Attack Detection. *IEEE Access / PMC8321190*.
7. **Viviani, P., & Terzuolo, C. (1982).** Trajectory formation in handwriting: Evidence for the 2/3 power law. *Neuroscience*, 7(2), 431–442.
8. **Verkruysse, W., Svaasand, L. O., & Nelson, J. S. (2008).** Remote plethysmographic imaging using ambient light. *Optics Express*, 16(26), 21434–21445.
9. **OpenCV Open Source Computer Vision Library Documentation:** `https://docs.opencv.org/`
10. **Google MediaPipe Solutions Guide:** `https://developers.google.com/mediapipe`

---

### 14. Faculty Guide Remarks:
\
\____________________________________________________________________________________________________  
\____________________________________________________________________________________________________  
\
\
**Prof. Sana A. Metkari** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Prof. Sana A. Metkari** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Dr. Mahesh S. Navale**  
*Project Guide* &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; *Project Coordinator* &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; *HOD*
