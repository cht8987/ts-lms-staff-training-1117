import os
from PIL import Image, ImageDraw, ImageFont

RAW_DIR = "/Users/elson/Documents/ts-lms-staff-training-1117/assets/raw"
ANN_DIR = "/Users/elson/Documents/ts-lms-staff-training-1117/assets/annotated"
os.makedirs(ANN_DIR, exist_ok=True)

# Try loading system font or fallback
try:
    font_large = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 28)
    font_badge = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 24)
    font_bold = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 22)
except Exception:
    font_large = ImageFont.load_default()
    font_badge = font_large
    font_bold = font_large

GOLD = "#BA8145"
GOLD_DARK = "#7A4E1B"
GOLD_LIGHT = "#E2A96B"
WHITE = "#FFFFFF"
BG_DARK = "#0F141C"
RED = "#D32F2F"

def draw_annotation(draw, box, label, badge_text="1"):
    x1, y1, x2, y2 = box
    # Highlight outline
    draw.rectangle([x1, y1, x2, y2], outline=GOLD, width=4)
    # Inner glow
    draw.rectangle([x1+2, y1+2, x2-2, y2-2], outline=GOLD_LIGHT, width=1)
    
    # Badge circle
    bx, by = x1 - 18, y1 - 18
    r = 18
    draw.ellipse([bx, by, bx + r*2, by + r*2], fill=GOLD, outline=WHITE, width=2)
    # Badge text
    w = len(badge_text) * 10
    draw.text((bx + r - w//2 + 2, by + 4), badge_text, fill=WHITE, font=font_badge)
    
    # Label banner
    if label:
        lx = x1 + 25
        ly = y1 - 26
        # Background pill
        text_bbox = draw.textbbox((lx + 10, ly + 2), label, font=font_bold)
        pad = 8
        draw.rounded_rectangle([text_bbox[0]-pad, text_bbox[1]-4, text_bbox[2]+pad, text_bbox[3]+4], radius=6, fill=BG_DARK, outline=GOLD, width=2)
        draw.text((lx + 10, ly + 2), label, fill=GOLD_LIGHT, font=font_bold)

def annotate_image(raw_name, out_name, annotations):
    raw_path = os.path.join(RAW_DIR, raw_name)
    if not os.path.exists(raw_path):
        print(f"Skipping {raw_name} (not found)")
        return
    
    im = Image.open(raw_path).convert("RGBA")
    draw = ImageDraw.Draw(im)
    
    for ann in annotations:
        box = ann.get("box")
        label = ann.get("label", "")
        badge = ann.get("badge", "1")
        draw_annotation(draw, box, label, badge)
        
    out_path = os.path.join(ANN_DIR, out_name)
    im.save(out_path, format="PNG")
    print(f"Generated annotated: {out_name}")

# Define annotations for key presentation slides
CONFIGS = [
    # Topic 1: Enrolment
    {
        "raw": "t1_01_enrollments_list.png",
        "out": "ann_01_enrolment_list.png",
        "anns": [
            {"box": [1150, 115, 1380, 160], "badge": "1", "label": "按「New Enrolment」开启录单"},
            {"box": [220, 260, 1400, 320], "badge": "2", "label": "录单总览列表与状态筛选"}
        ]
    },
    {
        "raw": "t1_02b_enrollment_ai_parse.png",
        "out": "ann_02_enrolment_ai_parse.png",
        "anns": [
            {"box": [250, 180, 850, 420], "badge": "1", "label": "贴上家长 WhatsApp 原始文字"},
            {"box": [870, 180, 1400, 420], "badge": "2", "label": "AI 自动拆解并自动填入资料"},
            {"box": [250, 450, 850, 520], "badge": "3", "label": "确认或搜寻匹配已有家长"}
        ]
    },
    {
        "raw": "t1_02c_enrollment_step2_package.png",
        "out": "ann_03_enrolment_packages.png",
        "anns": [
            {"box": [250, 160, 1400, 380], "badge": "1", "label": "选择学期配套（Terms & Bundle）"},
            {"box": [250, 410, 1400, 600], "badge": "2", "label": "加选科目与附加选项 Add-ons"}
        ]
    },
    {
        "raw": "t1_02e_enrollment_step4_payment.png",
        "out": "ann_04_enrolment_payment.png",
        "anns": [
            {"box": [250, 180, 750, 420], "badge": "1", "label": "选择付款方式并填写参考号"},
            {"box": [780, 180, 1400, 420], "badge": "2", "label": "上传汇款凭证收据附件"},
            {"box": [1100, 460, 1400, 520], "badge": "3", "label": "送出前核对金额（按「Save」生效）"}
        ]
    },
    {
        "raw": "t1_06_enrollment_invoice.png",
        "out": "ann_05_enrolment_invoice.png",
        "anns": [
            {"box": [220, 120, 650, 170], "badge": "1", "label": "单据详情页（Detail / Payments / Invoice）"},
            {"box": [950, 120, 1380, 170], "badge": "2", "label": "直接列印或透过 WhatsApp 传发票"}
        ]
    },

    # Topic 2: Student Page & Changes
    {
        "raw": "t2_01_student_profile_top.png",
        "out": "ann_06_student_profile.png",
        "anns": [
            {"box": [250, 160, 800, 360], "badge": "1", "label": "学籍总览卡（学号 TS-011960）"},
            {"box": [820, 160, 1400, 360], "badge": "2", "label": "Title & Group 称号与组别卡"}
        ]
    },
    {
        "raw": "t2_01b_student_classes_actions.png",
        "out": "ann_07_student_classes_actions.png",
        "anns": [
            {"box": [1000, 200, 1380, 260], "badge": "1", "label": "「Change Time」永久调课"},
            {"box": [1000, 280, 1380, 340], "badge": "2", "label": "「Swap Class」单堂临时调课"},
            {"box": [1000, 360, 1380, 420], "badge": "3", "label": "「Transfer」转课程/转学期"}
        ]
    },
    {
        "raw": "t2_03_change_time.png",
        "out": "ann_08_change_time.png",
        "anns": [
            {"box": [280, 180, 1350, 420], "badge": "1", "label": "选择新时段并查看学额与冲突检测"},
            {"box": [980, 460, 1350, 520], "badge": "2", "label": "确认生效日期后按「Confirm Change」"}
        ]
    },
    {
        "raw": "t2_04_swap_class.png",
        "out": "ann_09_swap_class.png",
        "anns": [
            {"box": [280, 180, 1350, 350], "badge": "1", "label": "指定要对调的具体某一堂课次"},
            {"box": [280, 370, 1350, 520], "badge": "2", "label": "选定目标班级（不影响其余课次）"}
        ]
    },

    # Topic 3: Homework
    {
        "raw": "t3_01_admin_homework_list.png",
        "out": "ann_10_homework_admin_list.png",
        "anns": [
            {"box": [220, 120, 1400, 200], "badge": "1", "label": "老师端功课管理列表与科目期数筛选"},
            {"box": [1150, 120, 1380, 170], "badge": "2", "label": "创建新作业或进入批改"}
        ]
    },
    {
        "raw": "t3_02_admin_homework_edit.png",
        "out": "ann_11_homework_options.png",
        "anns": [
            {"box": [300, 260, 950, 380], "badge": "1", "label": "File types 提交格式多选（Photo, PDF）"},
            {"box": [300, 400, 950, 500], "badge": "2", "label": "勾选「Speaking」开启学生录音功能"}
        ]
    },
    {
        "raw": "t3_04c_admin_grade_actions.png",
        "out": "ann_12_homework_grading.png",
        "anns": [
            {"box": [250, 180, 850, 450], "badge": "1", "label": "检视学生提交照片 / 播放录音"},
            {"box": [900, 180, 1400, 400], "badge": "2", "label": "填写评语、分数、指派批改人"},
            {"box": [900, 430, 1400, 500], "badge": "3", "label": "「Return for redo」退回 /「Release」发成绩"}
        ]
    },
    {
        "raw": "t3_05_student_hw_list_desktop.png",
        "out": "ann_13_student_hw_desktop.png",
        "anns": [
            {"box": [280, 140, 900, 220], "badge": "1", "label": "三态标签：「要交」「批改中」「改好了」"},
            {"box": [280, 240, 1350, 550], "badge": "2", "label": "功课卡片：显示截止日与 Speaking 录音标志"}
        ]
    },
    {
        "raw": "t3_08_student_hw_list_mobile.png",
        "out": "ann_14_student_hw_mobile.png",
        "anns": [
            {"box": [20, 140, 370, 200], "badge": "1", "label": "手机端自适应标签切换"},
            {"box": [20, 220, 370, 500], "badge": "2", "label": "一键拍照上传或直接录音提交"}
        ]
    },

    # Topic 4: Students Behaviour
    {
        "raw": "t4_01_class_records.png",
        "out": "ann_15_class_records_list.png",
        "anns": [
            {"box": [250, 140, 1400, 260], "badge": "1", "label": "选择年段与学期（例如 Y1-Y3）"},
            {"box": [250, 280, 1400, 600], "badge": "2", "label": "班级格子：点入即可记录全班课堂表现"}
        ]
    },
    {
        "raw": "t4_01b_class_records_roster.png",
        "out": "ann_16_class_records_roster.png",
        "anns": [
            {"box": [250, 160, 950, 550], "badge": "1", "label": "学生花名册与点名出缺席"},
            {"box": [1000, 160, 1400, 550], "badge": "2", "label": "加分/扣分板与组别积分结算"}
        ]
    },
    {
        "raw": "t4_02_care_student.png",
        "out": "ann_17_care_student.png",
        "anns": [
            {"box": [250, 160, 850, 400], "badge": "1", "label": "学生关怀指标与出勤风险警示"},
            {"box": [880, 160, 1400, 500], "badge": "2", "label": "Care Follow-up 关怀纪录追踪"}
        ]
    },

    # Topic 5: Email & Password
    {
        "raw": "t5_02b_admin_user_email_pwd.png",
        "out": "ann_18_admin_edit_credentials.png",
        "anns": [
            {"box": [300, 180, 1000, 280], "badge": "1", "label": "学生登入 ID 就是 Email（改后需告知家长）"},
            {"box": [300, 300, 1000, 420], "badge": "2", "label": "员工协助重设密码（New Password 栏位）"}
        ]
    },
    {
        "raw": "t5_03_student_setting_desktop.png",
        "out": "ann_19_student_setting_pwd.png",
        "anns": [
            {"box": [350, 220, 1100, 550], "badge": "1", "label": "学生端「Setting」自我修改密码"}
        ]
    },
    {
        "raw": "t5_06_forget_password.png",
        "out": "ann_20_forget_password.png",
        "anns": [
            {"box": [450, 250, 990, 500], "badge": "1", "label": "输入登记 Email 获取密码重设连结"}
        ]
    },

    # Topic 6: Bana Games
    {
        "raw": "t6_01_student_dashboard_bana.png",
        "out": "ann_21_student_bana_entry.png",
        "anns": [
            {"box": [350, 250, 1200, 450], "badge": "1", "label": "学生首页显眼「Bana Games」免密入口卡片"}
        ]
    },
    {
        "raw": "t6_03_bana_world.png",
        "out": "ann_22_bana_world.png",
        "anns": [
            {"box": [100, 80, 1340, 750], "badge": "1", "label": "首次点入自动开号，无缝进入 Bana 互动世界"}
        ]
    }
]

for cfg in CONFIGS:
    annotate_image(cfg["raw"], cfg["out"], cfg["anns"])

print("All annotations completed!")
