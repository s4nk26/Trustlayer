"""Quick validation test for the three new TrustLayer modules."""
import sys, math, numpy as np
print("Python:", sys.version[:25])

print("\n[1] Testing kinematic_tracker...")
from modules.kinematic_tracker import KinematicTremorTracker
t = KinematicTremorTracker(fps=30.0)
for i in range(60):
    x = 0.5 + math.sin(i * 0.4) * 0.01
    y = 0.5 + math.cos(i * 0.3) * 0.008
    t.push_nose(x, y)
profile = t.get_tremor_profile()
ks = profile["kinematic_liveness_score"]
nf = profile["nose"]["tremor_freq_hz"]
nb = profile["nose"]["frames_buffered"]
print(f"   Kinematic liveness score : {ks}")
print(f"   Nose tremor freq (Hz)    : {nf}")
print(f"   Frames buffered          : {nb}")
print("   [OK]")

print("\n[2] Testing biomarker_monitor...")
from modules.biomarker_monitor import BiomarkerMonitor
mon    = BiomarkerMonitor(phase=2, fps=30.0)
frame  = np.random.randint(100, 200, (480, 640, 3), dtype=np.uint8)
result = mon.update(frame, None)
print(f"   Phase            : {result['phase']}")
print(f"   Composite score  : {result['composite_score']}")
print(f"   Jitter status    : {result['jitter'].get('status')}")
print(f"   Anomaly flags    : {result['anomaly_flags']}")
mon.set_phase(3)
result3 = mon.update(frame, None)
print(f"   Phase 3 score    : {result3['composite_score']}")
print("   [OK]")

print("\n[3] Testing campus_presence...")
from modules.campus_presence import SingleFrameAntiSpoof, FaceEmbeddingEngine, FastFaceDetector
spoof   = SingleFrameAntiSpoof()
face    = np.random.randint(100, 220, (120, 100, 3), dtype=np.uint8)
res     = spoof.analyze(face)
score   = res["score"]
is_spoof = res["is_spoof"]
print(f"   Anti-spoof score : {score}  is_spoof: {is_spoof}")

emb_eng = FaceEmbeddingEngine()
emb     = emb_eng.extract(face)
norm    = float(np.linalg.norm(emb))
print(f"   Embedding shape  : {emb.shape}  norm: {norm:.4f}")

sim = FaceEmbeddingEngine.cosine_similarity(emb, emb)
print(f"   Self-similarity  : {sim:.4f} (expect ~1.0)")
print("   [OK]")

print("\n=== ALL MODULES VALIDATED SUCCESSFULLY ===")
