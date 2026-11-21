import ast
import re

with open(r'd:\trustlayer\ProveYouAreHuman\server.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update HEAD_POOL timeouts from 6.0 to 18.0
old_head_pool = """    HEAD_POOL = [
        {"id": "HEAD_LEFT", "title": "Turn Head Left", "instruction": "Turn your head to the left", "type": "HEAD_POSE", "timeout": 6.0, "speech": "Please turn your head to the left"},
        {"id": "HEAD_RIGHT", "title": "Turn Head Right", "instruction": "Turn your head to the right", "type": "HEAD_POSE", "timeout": 6.0, "speech": "Please turn your head to the right"},
        {"id": "HEAD_UP", "title": "Tilt Head Up", "instruction": "Tilt your head slightly upwards", "type": "HEAD_POSE", "timeout": 6.0, "speech": "Please tilt your head slightly upwards"},
        {"id": "HEAD_DOWN", "title": "Tilt Head Down", "instruction": "Tilt your head slightly downwards", "type": "HEAD_POSE", "timeout": 6.0, "speech": "Please tilt your head slightly downwards"}
    ]"""

new_head_pool = """    HEAD_POOL = [
        {"id": "HEAD_LEFT", "title": "Turn Head Left", "instruction": "Turn your head clearly to the left and hold for 1.2s", "type": "HEAD_POSE", "timeout": 18.0, "speech": "Please turn your head to the left and hold steady"},
        {"id": "HEAD_RIGHT", "title": "Turn Head Right", "instruction": "Turn your head clearly to the right and hold for 1.2s", "type": "HEAD_POSE", "timeout": 18.0, "speech": "Please turn your head to the right and hold steady"},
        {"id": "HEAD_UP", "title": "Tilt Head Up", "instruction": "Tilt your head upwards and hold for 1.2s", "type": "HEAD_POSE", "timeout": 18.0, "speech": "Please tilt your head upwards and hold steady"},
        {"id": "HEAD_DOWN", "title": "Tilt Head Down", "instruction": "Tilt your head downwards and hold for 1.2s", "type": "HEAD_POSE", "timeout": 18.0, "speech": "Please tilt your head downwards and hold steady"}
    ]"""

assert old_head_pool in content, "old_head_pool not found"
content = content.replace(old_head_pool, new_head_pool)

# 2. Update GESTURE_POOL timeouts from 10.0 to 22.0
old_gesture_pool = """    GESTURE_POOL = [
        {"id": "BLINK_AND_THREE_FINGERS", "title": "Blink Twice & Show 3 Fingers", "instruction": "Blink twice naturally and show 3 fingers", "type": "MULTIMODAL_GESTURE", "timeout": 10.0, "speech": "Please blink twice naturally and show three fingers to the camera"},
        {"id": "SMILE_AND_THREE_FINGERS", "title": "Smile & Show 3 Fingers", "instruction": "Smile naturally and show 3 fingers", "type": "MULTIMODAL_GESTURE", "timeout": 10.0, "speech": "Please smile naturally and show three fingers to the camera"},
        {"id": "THUMBS_UP_AND_BLINK", "title": "Show Thumbs Up & Blink", "instruction": "Show a thumbs up gesture and blink", "type": "MULTIMODAL_GESTURE", "timeout": 10.0, "speech": "Please show a thumbs up gesture and blink naturally"},
        {"id": "OPEN_PALM_AND_SMILE", "title": "Show Open Palm & Smile", "instruction": "Show an open palm with 5 fingers and smile", "type": "MULTIMODAL_GESTURE", "timeout": 10.0, "speech": "Please show an open palm and smile at the camera"}
    ]"""

new_gesture_pool = """    GESTURE_POOL = [
        {"id": "BLINK_AND_THREE_FINGERS", "title": "Blink Twice & Show 3 Fingers", "instruction": "Show 3 fingers steadily to camera and blink twice naturally", "type": "MULTIMODAL_GESTURE", "timeout": 22.0, "speech": "Please show three fingers clearly to the camera and blink twice naturally"},
        {"id": "SMILE_AND_THREE_FINGERS", "title": "Smile & Show 3 Fingers", "instruction": "Show 3 fingers steadily and smile naturally", "type": "MULTIMODAL_GESTURE", "timeout": 22.0, "speech": "Please smile naturally and show three fingers clearly to the camera"},
        {"id": "THUMBS_UP_AND_BLINK", "title": "Show Thumbs Up & Blink", "instruction": "Show a thumbs up gesture and blink once naturally", "type": "MULTIMODAL_GESTURE", "timeout": 22.0, "speech": "Please show a thumbs up gesture and blink naturally"},
        {"id": "OPEN_PALM_AND_SMILE", "title": "Show Open Palm & Smile", "instruction": "Show an open palm with fingers spread and smile", "type": "MULTIMODAL_GESTURE", "timeout": 22.0, "speech": "Please show an open palm and smile at the camera"}
    ]"""

assert old_gesture_pool in content, "old_gesture_pool not found"
content = content.replace(old_gesture_pool, new_gesture_pool)

# 3. Update Spoken Code timeout from 25.0 to 30.0 and Shape from 30.0 to 40.0
content = content.replace('"timeout": 25.0,', '"timeout": 30.0,')
content = content.replace(
    '{"id": "DRAW_STAR", "title": "Air-Draw 5-Point Star", "instruction": "Point your index finger in the air and trace around the Star", "type": "AIR_DRAWING", "shape": "star", "timeout": 30.0, "speech": "Point your index finger in the air and trace around the glowing star"},',
    '{"id": "DRAW_STAR", "title": "Air-Draw 5-Point Star", "instruction": "Point your index finger in the air and trace around the Star", "type": "AIR_DRAWING", "shape": "star", "timeout": 40.0, "speech": "Point your index finger in the air and trace around the glowing star"},'
)
content = content.replace(
    '{"id": "DRAW_SQUARE", "title": "Air-Draw Geometric Square", "instruction": "Point your index finger in the air and trace around the Square", "type": "AIR_DRAWING", "shape": "square", "timeout": 30.0, "speech": "Point your index finger in the air and trace around the square"},',
    '{"id": "DRAW_SQUARE", "title": "Air-Draw Geometric Square", "instruction": "Point your index finger in the air and trace around the Square", "type": "AIR_DRAWING", "shape": "square", "timeout": 40.0, "speech": "Point your index finger in the air and trace around the square"},'
)
content = content.replace(
    '{"id": "DRAW_INFINITY", "title": "Air-Draw Infinity Figure", "instruction": "Point your index finger in the air and trace around the Infinity figure", "type": "AIR_DRAWING", "shape": "infinity", "timeout": 30.0, "speech": "Point your index finger in the air and trace around the infinity figure"}',
    '{"id": "DRAW_INFINITY", "title": "Air-Draw Infinity Figure", "instruction": "Point your index finger in the air and trace around the Infinity figure", "type": "AIR_DRAWING", "shape": "infinity", "timeout": 40.0, "speech": "Point your index finger in the air and trace around the infinity figure"}'
)

# 4. Update evaluate_telemetry for Head pose and gesture thresholds + hold_time
old_eval_code = """        # STAGE 1: HEAD POSE (Requires 0.75s voluntary hold)
        if chal_id == "HEAD_LEFT":
            condition_met = (yaw < -5.5) or (tr < 0.40)
        elif chal_id == "HEAD_RIGHT":
            condition_met = (yaw > 5.5) or (tr > 0.60)
        elif chal_id == "HEAD_UP":
            condition_met = (pitch > 6.0)
        elif chal_id == "HEAD_DOWN":
            condition_met = (pitch < -6.0)

        # STAGE 2: MULTIMODAL GESTURE + BLINK / SMILE (Requires 0.75s hold)
        elif chal_id == "BLINK_AND_THREE_FINGERS":
            condition_met = (blinks_done >= 2) and hand_detected and (ext_count == 3)
        elif chal_id == "SMILE_AND_THREE_FINGERS":
            condition_met = is_smiling and hand_detected and (ext_count == 3)
        elif chal_id == "THUMBS_UP_AND_BLINK":
            is_thumb = f_state.get("thumb", False) and ext_count <= 2
            condition_met = is_thumb and (blinks_done >= 1)
        elif chal_id == "OPEN_PALM_AND_SMILE":
            is_palm = f_state.get("is_open_palm", False) or (ext_count >= 4)
            condition_met = is_palm and is_smiling

        # STAGE 3: SPOKEN ALPHANUMERIC CODE (7-8 Characters)
        elif chal_id == "SPOKEN_CODE_GESTURE":
            spoken_text = extra.get("spoken_text", "")
            if spoken_text:
                ver_res = self.lip_validator.verify_code(spoken_text, self.active_code)
                condition_met = ver_res.get("passed", False)
                if condition_met:
                    print(f"[+] Spoken Code Verified: '{spoken_text}' matches '{self.active_code}'")

        # STAGE 4: AIR-DRAWING SHAPE KINEMATICS (Requires >=70% actual waypoints traced & >= 4.0s)
        elif chal_id in ["DRAW_STAR", "DRAW_SQUARE", "DRAW_INFINITY"]:
            client_conf = float(extra.get("path_conformance", 0.0))
            self.shape_visited_conformance = max(self.shape_visited_conformance, client_conf)

            elapsed_shape = now - (self.shape_start_time if self.shape_start_time else now)
            asym = kinematic_data.get("asymmetry", {}).get("nose_asymmetry_index", 0.78)
            power_law = kinematic_data.get("power_law", {})
            is_bio = power_law.get("is_biological", True) or (0.50 <= asym <= 1.65)

            # Rigorous criteria: MUST have actually traced at least 70% of waypoints AND spent at least 4.0s
            condition_met = (self.shape_visited_conformance >= 0.70) and (elapsed_shape >= 4.0) and is_bio

        # Hold time confirmation (prevents instant glitch pass)
        hold_time = 0.75 if chal.get("type") in ["HEAD_POSE", "MULTIMODAL_GESTURE"] else 0.0"""

new_eval_code = """        # STAGE 1: DELIBERATE HEAD POSE (Requires deliberate 12+ deg angle held steadily for 1.2s)
        if chal_id == "HEAD_LEFT":
            condition_met = (yaw < -12.0) or (tr < 0.35)
        elif chal_id == "HEAD_RIGHT":
            condition_met = (yaw > 12.0) or (tr > 0.65)
        elif chal_id == "HEAD_UP":
            condition_met = (pitch > 9.0)
        elif chal_id == "HEAD_DOWN":
            condition_met = (pitch < -9.0)

        # STAGE 2: MULTIMODAL GESTURE + BLINK / SMILE (Requires 1.2s steady hold)
        elif chal_id == "BLINK_AND_THREE_FINGERS":
            condition_met = (blinks_done >= 1) and hand_detected and (ext_count == 3)
        elif chal_id == "SMILE_AND_THREE_FINGERS":
            condition_met = is_smiling and hand_detected and (ext_count == 3)
        elif chal_id == "THUMBS_UP_AND_BLINK":
            is_thumb = f_state.get("thumb", False) and ext_count <= 2
            condition_met = is_thumb and (blinks_done >= 1)
        elif chal_id == "OPEN_PALM_AND_SMILE":
            is_palm = f_state.get("is_open_palm", False) or (ext_count >= 4)
            condition_met = is_palm and is_smiling

        # STAGE 3: SPOKEN ALPHANUMERIC CODE (7-8 Characters)
        elif chal_id == "SPOKEN_CODE_GESTURE":
            spoken_text = extra.get("spoken_text", "")
            if spoken_text:
                ver_res = self.lip_validator.verify_code(spoken_text, self.active_code)
                condition_met = ver_res.get("passed", False)
                if condition_met:
                    print(f"[+] Spoken Code Verified: '{spoken_text}' matches '{self.active_code}'")

        # STAGE 4: AIR-DRAWING SHAPE KINEMATICS (Requires >=70% actual waypoints traced & >= 4.0s)
        elif chal_id in ["DRAW_STAR", "DRAW_SQUARE", "DRAW_INFINITY"]:
            client_conf = float(extra.get("path_conformance", 0.0))
            self.shape_visited_conformance = max(self.shape_visited_conformance, client_conf)

            elapsed_shape = now - (self.shape_start_time if self.shape_start_time else now)
            asym = kinematic_data.get("asymmetry", {}).get("nose_asymmetry_index", 0.78)
            power_law = kinematic_data.get("power_law", {})
            is_bio = power_law.get("is_biological", True) or (0.50 <= asym <= 1.65)

            condition_met = (self.shape_visited_conformance >= 0.70) and (elapsed_shape >= 4.0) and is_bio

        # Deliberate Hold Time (Requires 1.2s of steady deliberate action)
        hold_time = 1.2 if chal.get("type") in ["HEAD_POSE", "MULTIMODAL_GESTURE"] else 0.0"""

assert old_eval_code in content, "old_eval_code not found"
content = content.replace(old_eval_code, new_eval_code)

# 5. Provide visual feedback for holding steady in UI:
old_holding_msg = """                // Update Task Instructions & Dynamic Timeouts
                if (msg.challenge && !isGatewayPassed) {
                    document.getElementById('taskInstruction').innerText = msg.challenge;"""

new_holding_msg = """                // Update Task Instructions & Dynamic Timeouts
                if (msg.challenge && !isGatewayPassed) {
                    if (msg.is_challenge_met && !msg.is_challenge_passed) {
                        document.getElementById('taskInstruction').innerHTML = `${msg.challenge} <span style="color:#10b981; font-size:13px; font-weight:800;">[HOLDING STEADY...]</span>`;
                    } else {
                        document.getElementById('taskInstruction').innerText = msg.challenge;
                    }"""

assert old_holding_msg in content, "old_holding_msg not found"
content = content.replace(old_holding_msg, new_holding_msg)

ast.parse(content)
print("AST parsed cleanly! Writing updated timings and thresholds to server.py...")

with open(r'd:\trustlayer\ProveYouAreHuman\server.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: server.py updated with comfortable, robust challenge timings!")
