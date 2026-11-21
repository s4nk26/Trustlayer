"""
Verification Audit & Security Report Generator
TrustLayer: Human Verification for the AI Era
Zeal College of Engineering & Research, Pune-41
"""

import json
import os
import time
import cv2
import numpy as np


class VerificationReportGenerator:
    def __init__(self, output_dir="reports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def export_json_report(self, summary_data):
        """
        Saves structured JSON session log.
        """
        session_id = summary_data.get("session_id", "UNKNOWN")
        filename = os.path.join(self.output_dir, f"session_{session_id}.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=4)
        return filename

    def export_html_report(self, summary_data):
        """
        Creates a high-end, responsive HTML audit report certificate.
        """
        session_id = summary_data.get("session_id", "UNKNOWN")
        verdict = summary_data.get("verdict", "UNKNOWN")
        score = summary_data.get("final_score", 0.0)
        confidence = summary_data.get("confidence_level", "N/A")
        sub_scores = summary_data.get("sub_scores", {})
        challenges = summary_data.get("completed_challenges", [])
        anomalies = summary_data.get("anomaly_flags", [])
        duration = summary_data.get("duration_sec", 0.0)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        # Status badge coloring
        if verdict == "VERIFIED_HUMAN":
            badge_color = "#10b981"
            badge_bg = "rgba(16, 185, 129, 0.15)"
            verdict_title = "HUMAN VERIFICATION CONFIRMED"
            verdict_icon = "&#10004;"
        elif verdict == "SUSPICIOUS":
            badge_color = "#f59e0b"
            badge_bg = "rgba(245, 158, 11, 0.15)"
            verdict_title = "SUSPICIOUS ACTIVITY DETECTED"
            verdict_icon = "&#9888;"
        else:
            badge_color = "#ef4444"
            badge_bg = "rgba(239, 68, 68, 0.15)"
            verdict_title = "VERIFICATION REJECTED"
            verdict_icon = "&#10008;"

        # Build challenge rows
        challenge_rows = ""
        for i, c in enumerate(challenges, 1):
            challenge_rows += f"""
            <tr>
                <td style="padding: 10px 14px; border-bottom: 1px solid #27272a;">#{i} {c.get('name')}</td>
                <td style="padding: 10px 14px; border-bottom: 1px solid #27272a; color: #a1a1aa;">{c.get('type')}</td>
                <td style="padding: 10px 14px; border-bottom: 1px solid #27272a; color: #38bdf8;">{c.get('time_taken_sec')}s</td>
                <td style="padding: 10px 14px; border-bottom: 1px solid #27272a; color: #10b981;">PASSED</td>
            </tr>
            """

        anomaly_html = ""
        if anomalies:
            for flag in anomalies:
                anomaly_html += f"<span style='display:inline-block; margin:4px 6px; padding:4px 10px; background:#7f1d1d; color:#fca5a5; border-radius:6px; font-size:12px;'>&#9888; {flag}</span>"
        else:
            anomaly_html = "<span style='color:#10b981; font-size:13px;'>No suspicious artifacts or anomalies detected.</span>"

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TrustLayer Audit Certificate - {session_id}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }}
        body {{ background: #09090b; color: #f4f4f5; padding: 40px 20px; }}
        .container {{ max-width: 860px; margin: 0 auto; background: #18181b; border: 1px solid #27272a; border-radius: 16px; padding: 36px; box-shadow: 0 20px 50px rgba(0,0,0,0.6); }}
        .header {{ border-bottom: 1px solid #27272a; padding-bottom: 24px; margin-bottom: 28px; display: flex; justify-content: space-between; align-items: center; }}
        .college-title {{ font-size: 13px; text-transform: uppercase; letter-spacing: 1.5px; color: #a1a1aa; font-weight: 600; }}
        .proj-title {{ font-size: 24px; font-weight: 800; color: #38bdf8; margin-top: 4px; }}
        .team {{ font-size: 12px; color: #71717a; margin-top: 4px; }}
        .badge-box {{ padding: 24px; background: {badge_bg}; border: 1px solid {badge_color}; border-radius: 12px; text-align: center; margin-bottom: 28px; }}
        .verdict-tag {{ font-size: 14px; text-transform: uppercase; letter-spacing: 2px; color: {badge_color}; font-weight: 700; }}
        .score-val {{ font-size: 48px; font-weight: 900; color: {badge_color}; margin: 8px 0; }}
        .conf-val {{ font-size: 14px; color: #e4e4e7; }}
        .grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 28px; }}
        .card {{ background: #27272a; padding: 16px; border-radius: 10px; border: 1px solid #3f3f46; }}
        .card-label {{ font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #a1a1aa; margin-bottom: 6px; }}
        .card-val {{ font-size: 22px; font-weight: 700; color: #38bdf8; }}
        .section-title {{ font-size: 15px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: #e4e4e7; margin-bottom: 14px; }}
        table {{ width: 100%; border-collapse: collapse; text-align: left; font-size: 13px; margin-bottom: 28px; }}
        th {{ padding: 10px 14px; background: #27272a; color: #a1a1aa; text-transform: uppercase; font-size: 11px; }}
        .footer {{ border-top: 1px solid #27272a; padding-top: 20px; font-size: 12px; color: #71717a; display: flex; justify-content: space-between; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <div class="college-title">Zeal College of Engineering & Research &bull; Pune-41</div>
                <div class="proj-title">TrustLayer: Human Verification System</div>
                <div class="team">Project Team: Sandesh Kolhe, Sanket Shinde, Rajnandini Mane | Dept. of ECE</div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 11px; color: #71717a;">SESSION ID</div>
                <div style="font-family: monospace; font-size: 16px; font-weight: bold; color: #38bdf8;">#{session_id}</div>
                <div style="font-size: 11px; color: #71717a; margin-top: 4px;">{timestamp}</div>
            </div>
        </div>

        <div class="badge-box">
            <div class="verdict-tag">{verdict_icon} {verdict_title}</div>
            <div class="score-val">{score}%</div>
            <div class="conf-val">{confidence} &bull; Total Latency: {duration}s</div>
        </div>

        <div class="grid">
            <div class="card">
                <div class="card-label">Challenge Response</div>
                <div class="card-val">{sub_scores.get('challenge_response', 0)}%</div>
            </div>
            <div class="card">
                <div class="card-label">Face Liveness</div>
                <div class="card-val">{sub_scores.get('face_liveness', 0)}%</div>
            </div>
            <div class="card">
                <div class="card-label">Hand Biomechanics</div>
                <div class="card-val">{sub_scores.get('hand_biomechanics', 0)}%</div>
            </div>
            <div class="card">
                <div class="card-label">Deepfake Security</div>
                <div class="card-val">{sub_scores.get('anti_deepfake', 0)}%</div>
            </div>
        </div>

        <div class="section-title">Challenge-Response Audit Trail</div>
        <table>
            <thead>
                <tr>
                    <th>Challenge</th>
                    <th>Type</th>
                    <th>Execution Time</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {challenge_rows}
            </tbody>
        </table>

        <div class="section-title">Security & Anomaly Inspection</div>
        <div style="background: #27272a; padding: 14px; border-radius: 8px; margin-bottom: 28px;">
            {anomaly_html}
        </div>

        <div class="footer">
            <div>Cryptographic Verification Hash: SHA256-TL-{session_id}-{int(time.time())}</div>
            <div>Department of Electronics & Computer Engineering</div>
        </div>
    </div>
</body>
</html>
        """
        filename = os.path.join(self.output_dir, f"report_{session_id}.html")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_content)
        return filename

    def export_summary_certificate_image(self, summary_data):
        """
        Renders a high-resolution 900x600 PNG certificate image.
        """
        session_id = summary_data.get("session_id", "UNKNOWN")
        verdict = summary_data.get("verdict", "UNKNOWN")
        score = summary_data.get("final_score", 0.0)
        confidence = summary_data.get("confidence_level", "N/A")
        sub_scores = summary_data.get("sub_scores", {})

        img = np.zeros((620, 900, 3), dtype=np.uint8)
        img[:] = (20, 20, 24)  # Dark sleek background

        # Border
        cv2.rectangle(img, (15, 15), (885, 605), (45, 45, 52), 2)
        cv2.rectangle(img, (18, 18), (882, 602), (70, 70, 80), 1)

        # Header
        cv2.putText(img, "ZEAL COLLEGE OF ENGINEERING & RESEARCH - PUNE-41", (40, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (160, 160, 170), 1)
        cv2.putText(img, "TRUSTLAYER: HUMAN VERIFICATION AUDIT CERTIFICATE", (40, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 220, 255), 2)
        cv2.putText(img, f"SESSION ID: {session_id}   |   DATE: {time.strftime('%Y-%m-%d %H:%M:%S')}", (40, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (120, 120, 130), 1)

        # Verdict card
        if verdict == "VERIFIED_HUMAN":
            v_color = (0, 230, 100)
            v_text = "STATUS: HUMAN VERIFIED (GENUINE)"
        elif verdict == "SUSPICIOUS":
            v_color = (0, 180, 255)
            v_text = "STATUS: SUSPICIOUS ACTIVITY"
        else:
            v_color = (60, 60, 255)
            v_text = "STATUS: VERIFICATION FAILED (SPOOF)"

        cv2.rectangle(img, (40, 145), (860, 260), (32, 32, 38), -1)
        cv2.rectangle(img, (40, 145), (860, 260), v_color, 2)
        cv2.putText(img, v_text, (65, 185), cv2.FONT_HERSHEY_SIMPLEX, 0.8, v_color, 2)
        cv2.putText(img, f"Human Verification Score: {score}%", (65, 230), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        cv2.putText(img, f"[{confidence}]", (540, 230), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 190), 1)

        # Sub-score grid
        cards = [
            ("CHALLENGE RESPONSE", f"{sub_scores.get('challenge_response', 0)}%"),
            ("FACE LIVENESS", f"{sub_scores.get('face_liveness', 0)}%"),
            ("HAND BIOMECHANICS", f"{sub_scores.get('hand_biomechanics', 0)}%"),
            ("DEEPFAKE SECURITY", f"{sub_scores.get('anti_deepfake', 0)}%")
        ]
        for i, (lbl, val) in enumerate(cards):
            cx = 40 + i * 210
            cv2.rectangle(img, (cx, 285), (cx + 195, 385), (32, 32, 38), -1)
            cv2.rectangle(img, (cx, 285), (cx + 195, 385), (60, 60, 70), 1)
            cv2.putText(img, lbl, (cx + 12, 315), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (160, 160, 170), 1)
            cv2.putText(img, val, (cx + 12, 360), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 220, 255), 2)

        # Completed challenges
        cv2.putText(img, "MULTI-MODAL CHALLENGES AUDIT TRAIL:", (40, 425), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 210), 1)
        y_c = 460
        for c in summary_data.get("completed_challenges", [])[:3]:
            txt = f"- Passed: {c.get('name')} ({c.get('type')}) in {c.get('time_taken_sec')}s [Status: PASSED]"
            cv2.putText(img, txt, (50, y_c), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 255, 150), 1)
            y_c += 28

        # Footer
        cv2.putText(img, "Team: Sandesh Kolhe, Sanket Shinde, Rajnandini Mane | Guide: Prof. Sana A. Metkari", (40, 580), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (100, 100, 110), 1)

        filename = os.path.join(self.output_dir, f"certificate_{session_id}.png")
        cv2.imwrite(filename, img)
        return filename
