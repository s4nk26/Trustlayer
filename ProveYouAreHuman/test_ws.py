"""Quick WebSocket test for TrustLayer server"""
import asyncio
import json
import base64
import numpy as np
import cv2

async def test_ws():
    try:
        import websockets
    except ImportError:
        print("Installing websockets...")
        import subprocess, sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "websockets", "-q"])
        import websockets

    uri = "ws://localhost:8000/ws/verify?mode=standard"
    try:
        async with websockets.connect(uri, open_timeout=5, close_timeout=5) as ws:
            # Read initial message
            init = await asyncio.wait_for(ws.recv(), timeout=5)
            msg = json.loads(init)
            print("=== INIT MESSAGE ===")
            print(f"  Status:      {msg.get('status')}")
            print(f"  Session:     {msg.get('session_id')}")
            print(f"  Challenge:   {msg.get('challenge_id')}")
            print(f"  Instruction: {msg.get('challenge')}")
            speech = msg.get("speech", "")
            print(f"  Speech:      {speech[:80]}")
            print(f"  Step:        {msg.get('step')}/{msg.get('total_steps')}")
            print(f"  Time left:   {msg.get('time_left')}")
            print(f"  Gateway:     {msg.get('is_gateway_cleared')}")
            if "spoken_code" in msg:
                print(f"  Spoken code: {msg['spoken_code']}")
            print()

            # Send 3 fake frames to test processing loop
            for i in range(3):
                fake = np.zeros((480, 640, 3), dtype=np.uint8)
                fake[:] = (30 + i*20, 30 + i*20, 30 + i*20)
                _, buf = cv2.imencode(".jpg", fake)
                b64 = base64.b64encode(buf).decode()

                payload = {"image": b64, "spoken_text": ""}
                await ws.send(json.dumps(payload))

                resp = await asyncio.wait_for(ws.recv(), timeout=5)
                r = json.loads(resp)
                if i == 0:
                    print("=== FIRST FRAME RESPONSE ===")
                    print(f"  Status:       {r.get('status')}")
                    print(f"  Challenge:    {r.get('challenge_id')}")
                    print(f"  Met:          {r.get('is_challenge_met')}")
                    print(f"  Passed:       {r.get('is_challenge_passed')}")
                    tel = r.get("telemetry", {})
                    print(f"  Face:         {tel.get('face_detected')}")
                    print(f"  Hand:         {tel.get('hand_detected')}")
                    print(f"  HR:           {tel.get('heart_rate_bpm')}")
                    print(f"  Freeze:       {tel.get('freeze_detected')}")
                    print(f"  Asymmetry:    {tel.get('asymmetry_index')}")
                    print(f"  Power law:    {tel.get('power_law_score')}")
                    lh = r.get("live_health", {})
                    print(f"  Live verdict: {lh.get('verdict')}")
                    print(f"  Live score:   {lh.get('score')}")
                    print()

            print("=== WebSocket processing loop WORKS OK ===")
            await ws.send(json.dumps({"action": "stop"}))

    except Exception as e:
        print(f"WebSocket ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test_ws())
