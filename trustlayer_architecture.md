# TrustLayer & CampusPresence — Project Architecture

> **Zeal College of Engineering & Research, Pune-41 | PBL Project**
> Team: Sandesh Kolhe (EC2212) · Sanket Shinde (EC2209) · Rajnandini Mane (EC2202)
> Guide: Prof. Sana A. Metkari | HOD: Dr. Mahesh S. Navale

---

## Module Map

```
ProveYouAreHuman/
├── main.py                        ← Desktop app (System 1 + 2 state machine)
├── server.py                      ← FastAPI WebSocket server (web client + dashboard)
├── anti_spoofing.py               ← Chromatic screen flash reflection challenge
├── database.py                    ← SQLite audit log helpers
├── face_landmarker.task           ← MediaPipe Face Mesh model (3.6 MB)
├── hand_landmarker.task           ← MediaPipe Hand Landmarker model (7.8 MB)
│
└── modules/
    ├── face_liveness.py           ← [EXISTING] EAR blink, smile, head pose, 3D parallax
    ├── hand_biomechanics.py       ← [EXISTING] Kinematic displacement, gesture hold
    ├── deepfake_detector.py       ← [EXISTING] FFT Moiré, Laplacian, chrominance
    ├── scoring_engine.py          ← [EXISTING] Weighted multi-factor fusion (0–100%)
    ├── report_generator.py        ← [EXISTING] JSON/HTML/PNG certificate export
    ├── ui_hud.py                  ← [EXISTING] OpenCV HUD renderer
    ├── rppg_liveness.py           ← [EXISTING] CHROM rPPG BVP + FFT heart rate
    │
    ├── kinematic_tracker.py       ← [NEW ✅] Micro-tremor FFT + path conformance
    ├── biomarker_monitor.py       ← [NEW ✅] Phase 2/3 passive biomarker engine
    └── campus_presence.py         ← [NEW ✅] CampusPresence attendance stack
```

---

## New Modules — Technical Detail

### `modules/kinematic_tracker.py` — Kinematic Micro-Tremor Vector Tracking

| Class | Responsibility |
|---|---|
| `KinematicSeries` | Rolling per-point kinematic state: displacement, velocity, acceleration, jerk |
| `PathConformanceEngine` | Validates user tracking of animated UI waypoints within 150–400 ms cognitive window |
| `KinematicTremorTracker` | **Public API** — fuses all signals into one `get_tremor_profile()` dict |

**Detection Signals:**
- **FFT physiological tremor band** (6–12 Hz) via displacement magnitude series
- **Trajectory linearity R²** — R² ≥ 0.985 flags bot-scripted linear motion
- **Jerk spike detector** — `|da/dt| > 140` flags injection-speed anomalies
- **Static variance gate** — `σ < 8×10⁻⁵` flags frozen photo/replay
- **Cognitive onset latency** — reaction time < 100 ms or σ < 10 ms across samples → bot signature

---

### `modules/biomarker_monitor.py` — Background Passive Biomarker Engine

| Class | Responsibility |
|---|---|
| `SkinROIExtractor` | Extracts per-frame mean RGB from forehead + cheek landmark patches |
| `CHROMrPPGEngine` | de Haan & Jeanne (2013) CHROM projection → BVP waveform → FFT heart rate |
| `MicroJitterDetector` | High-frequency green-channel variance → biological jitter vs. static source |
| `BiomarkerMonitor` | **Public API** — phase switcher + composite liveness score |

**Phase Selection:**

| Phase | Mode | CPU Impact | Active Pipelines |
|---|---|---|---|
| **Phase 2** | `STREAM_MONITOR` | ~2–4% | rPPG (CHROM+FFT) + Micro-jitter |
| **Phase 3** | `LIGHT_SHIELD` | <1% | Micro-jitter only |

Toggle with `[P]` key during desktop session.

---

### `modules/campus_presence.py` — CampusPresence Attendance Stack

| Class | Responsibility |
|---|---|
| `AttendanceDatabase` | SQLite WAL-mode students + attendance tables, cooldown dedup |
| `SingleFrameAntiSpoof` | Laplacian + Chrominance + FFT Moiré pre-gate (fast, no DNN) |
| `FaceEmbeddingEngine` | HOG 128-dim L2-normalised face descriptor (DeepFace-ready stub) |
| `FastFaceDetector` | Haar cascade multi-scale face detection (real-time, ≥25 FPS) |
| `CampusPresenceSystem` | **Public API** — register/process/render/report |

**Attendance Workflow:**
```
Frame → Face Detection → Anti-Spoof Gate → HOG Embedding →
Cosine Similarity (≥0.72) → SQLite Mark (5-min cooldown) → HUD Overlay
```

---

## System Flow (Updated)

```
Webcam Frame
     │
     ├── FaceLivenessDetector   → face_data (EAR, yaw, parallax, blinks)
     ├── HandBiomechanicsDetector → hand_data (velocity, jerk, gesture)
     ├── DeepfakeArtifactDetector → df_data (Moiré, Laplacian, chroma)
     │
     ├── KinematicTremorTracker   ← nose_tip + wrist coords (NEW)
     │      └─ get_tremor_profile() → kinematic_data
     │
     ├── BiomarkerMonitor         ← full frame + landmarks (NEW)
     │      └─ update() → biomarker_data
     │
     └── Live Score Fusion
            auth_score × 30%
          + kin_score  × 35%
          + bio_score  × 25%
          + baseline   × 10%
            ──────────────────
            live_score (0–99)
```

---

## Desktop Controls (`main.py`)

| Key | Action |
|---|---|
| `Q` | Quit |
| `R` | Reset session |
| `M` | Toggle System 1 ↔ System 2 |
| `S` | Save / export audit certificate |
| **`P`** | **Toggle Biomarker Phase 2 ↔ Phase 3** *(new)* |

---

## Running the System

```powershell
# Desktop — System 1 (Gateway audit with certificate)
python main.py --mode standard

# Desktop — System 2 (Continuous live shield)
python main.py --mode live

# Web server (client + dashboard)
python server.py
# Client:    http://localhost:8000/client
# Dashboard: http://localhost:8000/dashboard
```

---

## Next Steps to Implement

- [ ] **Lip-Sync Engine** (`modules/lip_sync_validator.py`) — bimodal audio-visual phase matching
- [ ] **Voice Clone Detector** — alphanumeric mic frequency ↔ lip boundary kinematic matching
- [ ] **CampusPresence CLI** — `campus_presence.py --register` / `--session` entry points
- [ ] **DeepFace ArcFace** swap into `FaceEmbeddingEngine.extract()` for production-grade accuracy
- [ ] **WebSocket integration** of `kinematic_tracker` and `biomarker_monitor` into `server.py`
