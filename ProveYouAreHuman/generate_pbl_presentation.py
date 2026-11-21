import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Color Palette - Modern Cyber Security Tech
    DARK_BG = RGBColor(10, 15, 29)          # #0a0f1d
    CARD_BG = RGBColor(17, 24, 44)          # #11182c
    BORDER_CYAN = RGBColor(14, 165, 233)    # #0ea5e9
    BORDER_MUTED = RGBColor(30, 41, 69)     # #1e2945
    CYAN_ACCENT = RGBColor(56, 189, 248)    # #38bdf8
    EMERALD_GREEN = RGBColor(16, 185, 129)  # #10b981
    AMBER_ALERT = RGBColor(245, 158, 11)    # #f59e0b
    ROSE_RED = RGBColor(244, 63, 94)        # #f43f5e
    TEXT_WHITE = RGBColor(248, 250, 252)    # #f8fafc
    TEXT_MUTED = RGBColor(148, 163, 184)    # #94a3b8
    WHITE = RGBColor(255, 255, 255)

    def set_slide_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = DARK_BG
        bg.line.fill.background()
        return bg

    def add_header(slide, title_text, category_text="ZEAL COLLEGE OF ENGINEERING & RESEARCH // PBL 2026"):
        # Header banner text box
        tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(1.0))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        p_cat = tf.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.name = "Segoe UI"
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = CYAN_ACCENT

        p_title = tf.add_paragraph()
        p_title.text = title_text
        p_title.font.name = "Segoe UI"
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_WHITE
        p_title.space_before = Pt(4)

        # Thin divider rule
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.45), Inches(11.733), Inches(0.02))
        line.fill.solid()
        line.fill.fore_color.rgb = BORDER_MUTED
        line.line.fill.background()

    def add_card(slide, left, top, width, height, title="", title_color=CYAN_ACCENT, bg_color=CARD_BG, border_color=BORDER_MUTED):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1.2)
        
        if title:
            tb = slide.shapes.add_textbox(Inches(left + 0.25), Inches(top + 0.2), Inches(width - 0.5), Inches(0.45))
            tf = tb.text_frame
            tf.word_wrap = True
            tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
            p = tf.paragraphs[0]
            p.text = title
            p.font.name = "Segoe UI"
            p.font.size = Pt(13)
            p.font.bold = True
            p.font.color.rgb = title_color
        return shape

    # ==========================================
    # SLIDE 1: TITLE SLIDE
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s1)

    # Accent glow top bar
    bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.1))
    bar.fill.solid()
    bar.fill.fore_color.rgb = CYAN_ACCENT
    bar.line.fill.background()

    # Title box
    tb = s1.shapes.add_textbox(Inches(1.0), Inches(1.0), Inches(11.333), Inches(2.6))
    tf = tb.text_frame
    tf.word_wrap = True

    p0 = tf.paragraphs[0]
    p0.text = "ZEAL EDUCATION SOCIETY'S ZEAL COLLEGE OF ENGINEERING & RESEARCH, PUNE-41"
    p0.font.name = "Segoe UI"
    p0.font.size = Pt(12)
    p0.font.bold = True
    p0.font.color.rgb = CYAN_ACCENT

    p1 = tf.add_paragraph()
    p1.text = "DEPARTMENT OF ELECTRONICS & COMPUTER ENGINEERING"
    p1.font.name = "Segoe UI"
    p1.font.size = Pt(11)
    p1.font.color.rgb = TEXT_MUTED
    p1.space_before = Pt(4)

    p2 = tf.add_paragraph()
    p2.text = "TrustLayer: Human Verification for the AI Era"
    p2.font.name = "Segoe UI"
    p2.font.size = Pt(32)
    p2.font.bold = True
    p2.font.color.rgb = WHITE
    p2.space_before = Pt(14)

    p3 = tf.add_paragraph()
    p3.text = "AI-Powered Real-Time Liveness Detection, Challenge-Response & Anti-Deepfake System"
    p3.font.name = "Segoe UI"
    p3.font.size = Pt(15)
    p3.font.color.rgb = EMERALD_GREEN
    p3.space_before = Pt(6)

    # Team Card
    add_card(s1, 1.0, 3.8, 5.4, 2.8, title="PROJECT TEAM MEMBERS", title_color=CYAN_ACCENT)
    tb_team = s1.shapes.add_textbox(Inches(1.25), Inches(4.35), Inches(4.9), Inches(2.0))
    tf_team = tb_team.text_frame
    tf_team.word_wrap = True
    
    members = [
        ("Sandesh Kolhe", "Roll No: EC2212", "ZPRN: 125UEC1017"),
        ("Sanket Shinde", "Roll No: EC2209", "ZPRN: 125UEC1162"),
        ("Rajnandini Mane", "Roll No: EC2202", "ZPRN: 125UEC1145"),
    ]
    for i, (name, roll, zprn) in enumerate(members):
        p = tf_team.paragraphs[0] if i == 0 else tf_team.add_paragraph()
        p.text = f"{i+1}. {name}  |  {roll}  |  {zprn}"
        p.font.name = "Segoe UI"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_WHITE
        if i > 0:
            p.space_before = Pt(10)

    # Faculty Card
    add_card(s1, 6.9, 3.8, 5.4, 2.8, title="FACULTY GUIDES & LEADERSHIP", title_color=CYAN_ACCENT)
    tb_guide = s1.shapes.add_textbox(Inches(7.15), Inches(4.35), Inches(4.9), Inches(2.0))
    tf_guide = tb_guide.text_frame
    tf_guide.word_wrap = True
    
    guides = [
        ("Prof. Sana A. Metkari", "Project Guide & Project Coordinator"),
        ("Dr. Mahesh S. Navale", "Head of Department (HOD)"),
        ("Domain", "AI/ML, Cyber Security & Real-Time Computer Vision")
    ]
    for i, (role, title) in enumerate(guides):
        p = tf_guide.paragraphs[0] if i == 0 else tf_guide.add_paragraph()
        p.text = f"{role}"
        p.font.name = "Segoe UI"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE
        if i > 0:
            p.space_before = Pt(8)
        
        p_sub = tf_guide.add_paragraph()
        p_sub.text = title
        p_sub.font.name = "Segoe UI"
        p_sub.font.size = Pt(11)
        p_sub.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 2: PROBLEM STATEMENT & MOTIVATION
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s2)
    add_header(s2, "Problem Statement & Industry Context")

    # 3 Column Cards
    col_w = 3.65
    add_card(s2, 0.8, 1.7, col_w, 5.0, title="THE DEEPFAKE CRISIS", title_color=ROSE_RED)
    tb = s2.shapes.add_textbox(Inches(1.05), Inches(2.3), Inches(col_w - 0.5), Inches(4.0))
    tf = tb.text_frame
    tf.word_wrap = True
    bullets1 = [
        "Hyper-realistic generative AI models can synthesize live faces and clone voices in real time.",
        "High risk of digital impersonation in remote exams, job interviews, digital banking, and e-KYC onboarding.",
        "Traditional passwords and static OTPs only verify knowledge, NOT the live physical presence of a genuine human."
    ]
    for i, b in enumerate(bullets1):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"- {b}"
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_MUTED
        if i > 0: p.space_before = Pt(14)

    add_card(s2, 4.8, 1.7, col_w, 5.0, title="LIMITATIONS OF 2D AUTH", title_color=AMBER_ALERT)
    tb = s2.shapes.add_textbox(Inches(5.05), Inches(2.3), Inches(col_w - 0.5), Inches(4.0))
    tf = tb.text_frame
    tf.word_wrap = True
    bullets2 = [
        "Replay Attacks: Attackers stream prerecorded MP4 videos directly through virtual webcams (OBS Studio).",
        "Printed Photo & Mask Spoofs: 2D static photos bypass traditional face recognition without depth validation.",
        "Predictable Challenges: Fixed challenge routines (e.g. only blink) can be prerecorded and replayed easily."
    ]
    for i, b in enumerate(bullets2):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"- {b}"
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_MUTED
        if i > 0: p.space_before = Pt(14)

    add_card(s2, 8.8, 1.7, col_w, 5.0, title="OUR PROPOSED SOLUTION", title_color=EMERALD_GREEN)
    tb = s2.shapes.add_textbox(Inches(9.05), Inches(2.3), Inches(col_w - 0.5), Inches(4.0))
    tf = tb.text_frame
    tf.word_wrap = True
    bullets3 = [
        "Multi-Layer Verification: Synchronous fusion of 4 distinct verification vectors.",
        "Randomized Challenge-Response: Strict latency constraints (4s timeout) against replay attacks.",
        "Contactless Biological Liveness: rPPG pulse extraction verifies living human blood capillaries.",
        "Active Optical Challenge: Screen-flash chromatic reflection blocks virtual cameras."
    ]
    for i, b in enumerate(bullets3):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"- {b}"
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_MUTED
        if i > 0: p.space_before = Pt(14)

    # ==========================================
    # SLIDE 3: LITERATURE SURVEY & RESEARCH GAP
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s3)
    add_header(s3, "Literature Survey & Identified Research Gap")

    add_card(s3, 0.8, 1.7, 5.6, 5.0, title="PRIOR ART ANALYSIS", title_color=CYAN_ACCENT)
    tb = s3.shapes.add_textbox(Inches(1.05), Inches(2.3), Inches(5.1), Inches(4.0))
    tf = tb.text_frame
    tf.word_wrap = True
    surveys = [
        ("Kollreider et al. (2007) & Pan et al. (2007)", "Optical flow & eye-blink detection. Vulnerable to video replays of blinking humans."),
        ("Ahmed et al. (2023) - Challenge-Response", "Randomized action prompts. Effective against static attacks, but struggles against real-time 3D generative avatars."),
        ("Li & Lyu (2018) / Li et al. (2020) Face X-Ray", "Artifact & blending boundary detection. Deepfake generators rapidly evolve to eliminate visible boundary seams."),
        ("Zheng et al. (2025) - D3 Anti-Spoofing", "Frequency and second-order temporal features. High compute overhead; unsuitable for real-time web clients.")
    ]
    for i, (author, desc) in enumerate(surveys):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"{i+1}. {author}"
        p.font.bold = True
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_WHITE
        if i > 0: p.space_before = Pt(10)
        p_sub = tf.add_paragraph()
        p_sub.text = desc
        p_sub.font.size = Pt(10)
        p_sub.font.color.rgb = TEXT_MUTED

    add_card(s3, 6.9, 1.7, 5.6, 5.0, title="IDENTIFIED RESEARCH GAPS & INNOVATION", title_color=EMERALD_GREEN)
    tb = s3.shapes.add_textbox(Inches(7.15), Inches(2.3), Inches(5.1), Inches(4.0))
    tf = tb.text_frame
    tf.word_wrap = True
    gaps = [
        ("Gap 1: Neglect of Hand/Wrist Biomechanics", "Existing verification systems focus only on the face oval. Face-swap models fail completely when hands interact with or obscure facial regions."),
        ("Gap 2: Lack of Biological Physiology Checks", "Software-generated avatars have perfect textures but zero blood flow. Incorporating rPPG pulse telemetry creates a non-forgeable biometric heartbeat signal."),
        ("Gap 3: Passive vs. Active Optical Verification", "Passive models cannot distinguish high-res screen replays. TrustLayer actively flashes narrow-spectrum light to measure skin diffuse reflectance.")
    ]
    for i, (gap, sol) in enumerate(gaps):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = gap
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = CYAN_ACCENT
        if i > 0: p.space_before = Pt(14)
        p_sub = tf.add_paragraph()
        p_sub.text = sol
        p_sub.font.size = Pt(11)
        p_sub.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 4: SYSTEM ARCHITECTURE & DATA FLOW
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s4)
    add_header(s4, "Multi-Layer System Architecture")

    # Workflow blocks
    steps = [
        ("1. CLIENT TIER", "HTML5 / WebRTC\nWebcam Capture\nFrame Canvas\nWebSocket Client", CYAN_ACCENT),
        ("2. FASTAPI SERVER", "Asynchronous WS\nFrame Router\nSession Manager\nState Machine", CYAN_ACCENT),
        ("3. BIOMETRIC PIPELINE", "MediaPipe FaceMesh\nEye Aspect Ratio\nHead Pose (Yaw/Pitch)\nHand Gestures (0-5)", EMERALD_GREEN),
        ("4. ANTI-SPOOF ENGINE", "rPPG Pulse (CHROM)\nActive Screen Flash\nLaplacian Blur Check\nMoiré Screen Filter", AMBER_ALERT),
        ("5. DECISION & AUDIT", "Weighted Multi-Score\nThreshold Classifier\nSQLite verifications.db\nPDF / PNG Certificate", ROSE_RED),
    ]
    box_w = 2.15
    for i, (title, content, col) in enumerate(steps):
        left_pos = 0.8 + i * 2.4
        add_card(s4, left_pos, 1.8, box_w, 4.8, title=title, title_color=col)
        tb = s4.shapes.add_textbox(Inches(left_pos + 0.15), Inches(2.4), Inches(box_w - 0.3), Inches(4.0))
        tf = tb.text_frame
        tf.word_wrap = True
        for j, line_txt in enumerate(content.split("\n")):
            p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
            p.text = f"• {line_txt}"
            p.font.size = Pt(11)
            p.font.color.rgb = TEXT_WHITE
            p.space_before = Pt(8)

    # ==========================================
    # SLIDE 5: MODULE 1 - FACIAL LIVENESS & POSE
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s5)
    add_header(s5, "Biometric Liveness: Eye Aspect Ratio & Head Pose")

    add_card(s5, 0.8, 1.7, 5.6, 5.0, title="EYE ASPECT RATIO (EAR) BLINK ANALYSIS", title_color=CYAN_ACCENT)
    tb = s5.shapes.add_textbox(Inches(1.05), Inches(2.3), Inches(5.1), Inches(4.0))
    tf = tb.text_frame
    tf.word_wrap = True
    ear_text = [
        ("Mathematical Formulation:", "EAR = ( ||p2 - p6|| + ||p3 - p5|| ) / ( 2 * ||p1 - p4|| )"),
        ("Landmark Extraction:", "Extracts 6 specific 3D coordinates per eye from MediaPipe 468-point Face Mesh."),
        ("Dynamic Blink Logic:", "Open eye EAR: ~0.28 - 0.35. Closed eye EAR: < 0.20."),
        ("Duration Validation:", "Blink must occur within 100ms - 400ms to filter out squinting or artificial video cuts.")
    ]
    for i, (head, desc) in enumerate(ear_text):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = head
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = CYAN_ACCENT
        if i > 0: p.space_before = Pt(10)
        p_sub = tf.add_paragraph()
        p_sub.text = desc
        p_sub.font.size = Pt(11)
        p_sub.font.color.rgb = TEXT_MUTED

    add_card(s5, 6.9, 1.7, 5.6, 5.0, title="HEAD POSE ESTIMATION (cv2.solvePnP)", title_color=EMERALD_GREEN)
    tb = s5.shapes.add_textbox(Inches(7.15), Inches(2.3), Inches(5.1), Inches(4.0))
    tf = tb.text_frame
    tf.word_wrap = True
    pose_text = [
        ("3D-to-2D Perspective Correspondence:", "Maps 6 2D image coordinates to canonical 3D facial model (Nose tip, Chin, Eye corners, Mouth corners)."),
        ("Rotation & Translation Vectors:", "Computes Pitch (Up/Down), Yaw (Left/Right), and Roll (Tilt) in real time."),
        ("Challenge Validation:", "Detects intentional head turns (e.g. Yaw > +18 deg for Left, < -18 deg for Right)."),
        ("Natural Micro-movement Check:", "Ensures natural human tremor (~1-2Hz); static pictures or rigid 3D models are immediately rejected.")
    ]
    for i, (head, desc) in enumerate(pose_text):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = head
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = EMERALD_GREEN
        if i > 0: p.space_before = Pt(10)
        p_sub = tf.add_paragraph()
        p_sub.text = desc
        p_sub.font.size = Pt(11)
        p_sub.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 6: MODULE 2 - BIOMECHANICS & OPTICAL DEFENSE
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s6)
    add_header(s6, "Hand Biomechanics & Active Screen Flash Defense")

    add_card(s6, 0.8, 1.7, 5.6, 5.0, title="HAND/WRIST BIOMECHANICS (RESEARCH GAP)", title_color=CYAN_ACCENT)
    tb = s6.shapes.add_textbox(Inches(1.05), Inches(2.3), Inches(5.1), Inches(4.0))
    tf = tb.text_frame
    tf.word_wrap = True
    hand_text = [
        ("Why Hand Gestures?:", "Current GAN/Diffusion face swaps are isolated to the face bounding box. Occluding the face with a hand causes synthetic face models to glitch or warp severely."),
        ("MediaPipe Hands Pipeline:", "Extracts 21 3D hand joints. Analyzes finger extension angles and palm orientation."),
        ("Randomized Finger Challenges:", "Prompts user to display random finger counts (e.g. 'Show 2 fingers' or 'Show 3 fingers near chin')."),
        ("Temporal Verification:", "Hand entry, gesture hold, and exit must match challenge prompt timings.")
    ]
    for i, (head, desc) in enumerate(hand_text):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = head
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = CYAN_ACCENT
        if i > 0: p.space_before = Pt(10)
        p_sub = tf.add_paragraph()
        p_sub.text = desc
        p_sub.font.size = Pt(11)
        p_sub.font.color.rgb = TEXT_MUTED

    add_card(s6, 6.9, 1.7, 5.6, 5.0, title="ACTIVE SCREEN-FLASH CHROMATIC DEFENSE", title_color=AMBER_ALERT)
    tb = s6.shapes.add_textbox(Inches(7.15), Inches(2.3), Inches(5.1), Inches(4.0))
    tf = tb.text_frame
    tf.word_wrap = True
    flash_text = [
        ("Narrowband Optical Probe:", "Server triggers client browser to emit a 400ms color flash (#00FFCC Cyan or #FF007F Magenta)."),
        ("Diffuse Skin Reflectance:", "Calculates mean RGB chromatic shift across forehead and cheek skin patches during flash."),
        ("Cosine Similarity Vector Check:", "Skin chromatic shift vector delta_C must align with target light vector (> 0.82 similarity)."),
        ("Defeats Virtual Webcams:", "Prerecorded videos and synthetic deepfakes piped through OBS Studio cannot reflect random screen flashes!")
    ]
    for i, (head, desc) in enumerate(flash_text):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = head
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = AMBER_ALERT
        if i > 0: p.space_before = Pt(10)
        p_sub = tf.add_paragraph()
        p_sub.text = desc
        p_sub.font.size = Pt(11)
        p_sub.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 7: MODULE 3 - rPPG BIOLOGICAL HEART PULSE
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s7)
    add_header(s7, "rPPG: Contactless Biological Capillary Liveness")

    add_card(s7, 0.8, 1.7, 5.6, 5.0, title="THE SCIENCE OF CONTACTLESS PULSE", title_color=ROSE_RED)
    tb = s7.shapes.add_textbox(Inches(1.05), Inches(2.3), Inches(5.1), Inches(4.0))
    tf = tb.text_frame
    tf.word_wrap = True
    rppg_info = [
        ("Hemoglobin Light Absorption:", "Oxygenated hemoglobin absorbs green light (~540nm) more than red/blue. With each heartbeat, capillary volume expands, causing imperceptible light attenuation."),
        ("Forehead Skin ROI Extraction:", "MediaPipe landmarks isolate forehead capillaries without hair/eyebrow interference."),
        ("The De Haan & Jeanne CHROM Method:", "Projects RGB signals onto chrominance planes orthogonal to skin tone to eliminate motion artifacts."),
        ("Temporal Windowing:", "Applies 90-frame rolling window at 30 FPS to extract biological periodicity.")
    ]
    for i, (head, desc) in enumerate(rppg_info):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = head
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = ROSE_RED
        if i > 0: p.space_before = Pt(10)
        p_sub = tf.add_paragraph()
        p_sub.text = desc
        p_sub.font.size = Pt(11)
        p_sub.font.color.rgb = TEXT_MUTED

    add_card(s7, 6.9, 1.7, 5.6, 5.0, title="FFT SIGNAL PROCESSING & SPOOF REJECTION", title_color=EMERALD_GREEN)
    tb = s7.shapes.add_textbox(Inches(7.15), Inches(2.3), Inches(5.1), Inches(4.0))
    tf = tb.text_frame
    tf.word_wrap = True
    fft_info = [
        ("Butterworth Bandpass Filter:", "Passband of 0.75 Hz - 2.5 Hz isolates physiological heart rates (45 BPM - 150 BPM)."),
        ("Fast Fourier Transform (FFT):", "Extracts dominant spectral frequency peak corresponding to human cardiac cycle."),
        ("Signal-to-Noise Ratio (SNR):", "Calculates ratio of heart peak energy to background noise. Live humans exhibit SNR > 3.5 dB."),
        ("Complete Deepfake Defense:", "3D silicone masks, paper printouts, and AI deepfakes exhibit ZERO blood volume pulse. Liveness = 0%!")
    ]
    for i, (head, desc) in enumerate(fft_info):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = head
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = EMERALD_GREEN
        if i > 0: p.space_before = Pt(10)
        p_sub = tf.add_paragraph()
        p_sub.text = desc
        p_sub.font.size = Pt(11)
        p_sub.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 8: DECISION ENGINE & SCORING MODEL
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s8)
    add_header(s8, "Decision Engine & Multi-Factor Scoring Formula")

    add_card(s8, 0.8, 1.7, 11.733, 2.2, title="FUSED CONFIDENCE SCORING FORMULA", title_color=CYAN_ACCENT)
    tb = s8.shapes.add_textbox(Inches(1.05), Inches(2.3), Inches(11.2), Inches(1.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Human_Score = (0.35 * S_Challenge) + (0.35 * S_Liveness) + (0.15 * S_rPPG) + (0.15 * S_AntiSpoof)"
    p.font.name = "Consolas"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = EMERALD_GREEN

    p_sub = tf.add_paragraph()
    p_sub.text = "• S_Challenge: Completion accuracy and latency within 4-second randomized challenge windows.\n• S_Liveness: Natural blink cadence (EAR) and natural head tremor variance.\n• S_rPPG: Biological cardiac pulse SNR extracted via contactless chrominance blood flow.\n• S_AntiSpoof: Screen flash color reflectance consistency, Laplacian sharpness, and Moiré screen detection."
    p_sub.font.size = Pt(11)
    p_sub.font.color.rgb = TEXT_WHITE
    p_sub.space_before = Pt(8)

    # 3 Classification Tiers
    tiers = [
        ("VERIFIED HUMAN", "Score >= 80%", "All biometric and challenge thresholds passed. Natural blood pulse and optical response verified. Cryptographic audit certificate generated.", EMERALD_GREEN),
        ("SUSPICIOUS", "Score: 50% - 79%", "Marginal compliance. Slow challenge response time, lighting glare, or borderline pulse SNR. Flagged for secondary administrator review.", AMBER_ALERT),
        ("VERIFICATION FAILED", "Score < 50%", "High probability of spoof. Prerecorded replay, face absence, silicone mask, or virtual camera injection detected. Immediate alert logged.", ROSE_RED)
    ]
    for i, (name, score_range, desc, col) in enumerate(tiers):
        left_pos = 0.8 + i * 4.0
        add_card(s8, left_pos, 4.2, 3.75, 2.5, title=name, title_color=col)
        tb_t = s8.shapes.add_textbox(Inches(left_pos + 0.2), Inches(4.7), Inches(3.35), Inches(1.8))
        tf_t = tb_t.text_frame
        tf_t.word_wrap = True
        
        p = tf_t.paragraphs[0]
        p.text = score_range
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = col

        p_desc = tf_t.add_paragraph()
        p_desc.text = desc
        p_desc.font.size = Pt(10)
        p_desc.font.color.rgb = TEXT_MUTED
        p_desc.space_before = Pt(6)

    # ==========================================
    # SLIDE 9: DUAL WEB INTERFACES (CLIENT & ADMIN)
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s9)
    add_header(s9, "Dual Portals: Client Verification & Admin Dashboard")

    add_card(s9, 0.8, 1.7, 5.6, 5.0, title="CLIENT VERIFICATION PORTAL (/client)", title_color=CYAN_ACCENT)
    tb = s9.shapes.add_textbox(Inches(1.05), Inches(2.3), Inches(5.1), Inches(4.0))
    tf = tb.text_frame
    tf.word_wrap = True
    c_features = [
        ("Live Video Viewfinder:", "Hardware-accelerated HTML5 video canvas streaming frames to WebSocket server."),
        ("Dynamic Challenge HUD:", "Real-time action banner ('Turn Left', 'Blink Twice', 'Show 2 Fingers') with visual timer bar."),
        ("Live Biometric Telemetry:", "Real-time on-screen indicators for Head Pose, EAR blink state, rPPG pulse status, and finger counts."),
        ("Instant Verification Modal:", "Displays final Human Verification Score % and pass/fail badge immediately upon test completion.")
    ]
    for i, (head, desc) in enumerate(c_features):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = head
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = CYAN_ACCENT
        if i > 0: p.space_before = Pt(10)
        p_sub = tf.add_paragraph()
        p_sub.text = desc
        p_sub.font.size = Pt(11)
        p_sub.font.color.rgb = TEXT_MUTED

    add_card(s9, 6.9, 1.7, 5.6, 5.0, title="ADMIN ANALYTICS DASHBOARD (/dashboard)", title_color=EMERALD_GREEN)
    tb = s9.shapes.add_textbox(Inches(7.15), Inches(2.3), Inches(5.1), Inches(4.0))
    tf = tb.text_frame
    tf.word_wrap = True
    a_features = [
        ("Real-Time System KPIs:", "Total Verifications, Pass Rate %, Average Multi-Factor Score, Average Pipeline Latency."),
        ("SQLite Audit Session Log:", "Searchable, filterable audit trail of every verification attempt with unique Session IDs."),
        ("Digital Audit Certificates:", "Built-in certificate modal displaying cryptographic hashes, sub-scores, and challenge logs."),
        ("Threat Monitoring:", "Detailed flags for detected spoofing vectors (Replay, Mask, Avatar, Virtual Cam).")
    ]
    for i, (head, desc) in enumerate(a_features):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = head
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = EMERALD_GREEN
        if i > 0: p.space_before = Pt(10)
        p_sub = tf.add_paragraph()
        p_sub.text = desc
        p_sub.font.size = Pt(11)
        p_sub.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 10: EXPERIMENTAL TESTING & RESULTS
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s10)
    add_header(s10, "Empirical Testing & Attack Defense Results")

    tests = [
        ("TEST CASE 1: LIVE GENUINE HUMAN", "Verdict: VERIFIED HUMAN (94.2%)", "Completed all 3 random challenges in 2.1s average. Natural blink EAR = 0.16. rPPG pulse detected (74 BPM, SNR 4.8 dB). Skin flash cosine similarity = 0.91.", EMERALD_GREEN),
        ("TEST CASE 2: HIGH-RES 2D PRINT PHOTO", "Verdict: VERIFICATION FAILED (12.5%)", "Zero eye blink activity (EAR fixed). Head pose static. Zero rPPG blood capillary signal. Failed first random turn challenge immediately.", ROSE_RED),
        ("TEST CASE 3: SMARTPHONE VIDEO REPLAY", "Verdict: VERIFICATION FAILED (28.0%)", "Prerecorded video failed to anticipate randomized challenge sequence. Moiré screen texture detected. Optical flash reflection mismatch.", ROSE_RED),
        ("TEST CASE 4: SYNTHETIC AI DEEPFAKE / FACE-SWAP", "Verdict: SUSPICIOUS / FAILED (41.0%)", "Face-swap model glitched when hand entered frame for finger challenge. Zero biological pulse detected in rPPG spectrum.", AMBER_ALERT),
    ]
    for i, (t_title, t_verdict, t_desc, col) in enumerate(tests):
        y_pos = 1.7 + i * 1.3
        add_card(s10, 0.8, y_pos, 11.733, 1.15, title=t_title, title_color=CYAN_ACCENT)
        tb_t = s10.shapes.add_textbox(Inches(1.05), Inches(y_pos + 0.45), Inches(11.2), Inches(0.6))
        tf_t = tb_t.text_frame
        tf_t.word_wrap = True
        p = tf_t.paragraphs[0]
        p.text = f"{t_verdict}  |  {t_desc}"
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_WHITE

    # ==========================================
    # SLIDE 11: CONCLUSION & FUTURE SCOPE
    # ==========================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s11)
    add_header(s11, "Project Summary, Impact & Future Scope")

    add_card(s11, 0.8, 1.7, 5.6, 5.0, title="KEY PROJECT ACHIEVEMENTS", title_color=EMERALD_GREEN)
    tb = s11.shapes.add_textbox(Inches(1.05), Inches(2.3), Inches(5.1), Inches(4.0))
    tf = tb.text_frame
    tf.word_wrap = True
    achievements = [
        "Delivered a production-ready, real-time AI verification platform combining computer vision and web technologies.",
        "Successfully addressed the research gap by integrating hand biomechanics and rPPG blood capillary pulse extraction.",
        "Engineered an active screen-flash optical defense completely blocking virtual webcams and replay attacks.",
        "Created an end-to-end audit architecture with live user portal, admin telemetry dashboard, and SQLite session logging."
    ]
    for i, a in enumerate(achievements):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"✓ {a}"
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_WHITE
        if i > 0: p.space_before = Pt(14)

    add_card(s11, 6.9, 1.7, 5.6, 5.0, title="FUTURE SCOPE & COMMERCIAL HORIZONS", title_color=CYAN_ACCENT)
    tb = s11.shapes.add_textbox(Inches(7.15), Inches(2.3), Inches(5.1), Inches(4.0))
    tf = tb.text_frame
    tf.word_wrap = True
    future = [
        "Multimodal Voice Liveness: Phoneme-viseme synchronization and voice-clone frequency analysis.",
        "Mobile SDK: React Native / Flutter SDK for banking e-KYC and digital exam proctoring applications.",
        "Continuous Call Verification: Background daemon monitoring video meetings (Zoom / Google Meet) for live face-swaps.",
        "Decentralized Blockchain Notarization: Hashing verification certificates onto Ethereum / Polygon for tamper-proof credentials."
    ]
    for i, f in enumerate(future):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"→ {f}"
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_MUTED
        if i > 0: p.space_before = Pt(14)

    # ==========================================
    # SLIDE 12: REFERENCES & THANK YOU
    # ==========================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s12)
    add_header(s12, "References & Acknowledgements")

    add_card(s12, 0.8, 1.7, 7.5, 5.0, title="KEY LITERATURE REFERENCES", title_color=CYAN_ACCENT)
    tb = s12.shapes.add_textbox(Inches(1.05), Inches(2.3), Inches(7.0), Inches(4.0))
    tf = tb.text_frame
    tf.word_wrap = True
    refs = [
        "1. Kollreider et al. (2007) - Real-time face inner movement tracking for liveness evaluation.",
        "2. Pan et al. (2007) - Eyeblink-based anti-spoofing in face recognition from a generic webcamera.",
        "3. Li & Lyu (2018) - Exposing DeepFake Videos By Detecting Face Warping Artifacts, arXiv.",
        "4. De Haan & Jeanne (2013) - Robust Pulse Rate From Chrominance-Based rPPG, IEEE TBME.",
        "5. Ahmed et al. (2023) - Dynamic Challenge-Response Authentication Protocols in Biometrics.",
        "6. Zheng et al. (2025) - D3: Training-Free AI-Generated Video Detection, ICCV 2025."
    ]
    for i, r in enumerate(refs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = r
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_MUTED
        if i > 0: p.space_before = Pt(10)

    add_card(s12, 8.6, 1.7, 3.933, 5.0, title="PROJECT DEFENSE", title_color=EMERALD_GREEN)
    tb = s12.shapes.add_textbox(Inches(8.85), Inches(2.5), Inches(3.433), Inches(3.5))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "THANK YOU!"
    p.font.bold = True
    p.font.size = Pt(26)
    p.font.color.rgb = WHITE
    p.alignment = PP_ALIGN.CENTER

    p_sub = tf.add_paragraph()
    p_sub.text = "\nQuestions & Technical Discussion\n\nTrustLayer System Ready for Live Demonstration"
    p_sub.font.size = Pt(13)
    p_sub.font.color.rgb = CYAN_ACCENT
    p_sub.alignment = PP_ALIGN.CENTER

    output_path = r"C:\Users\User\ProveYouAreHuman\TrustLayer_PBL_Presentation.pptx"
    prs.save(output_path)
    print(f"Presentation saved successfully to {output_path}")

if __name__ == "__main__":
    create_presentation()
