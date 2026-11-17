import os
import time
from playwright.sync_api import sync_playwright

RAW_DIR = "/Users/elson/Documents/ts-lms-staff-training-1117/assets/raw"
os.makedirs(RAW_DIR, exist_ok=True)

MASK_JS = """
() => {
    // Mask sensitive phone numbers, emails, and student names if not test student
    const walk = (node) => {
        if (node.nodeType === 3) {
            let text = node.nodeValue;
            text = text.replace(/(\\+?6?01\\d{1})[- ]?\\d{3,4}[- ]?\\d{4}/g, '$1-**** ***');
            text = text.replace(/([a-zA-Z0-9_.+-]+)@([a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+)/g, (match, p1, p2) => {
                if (match.includes('topscholar') || match.includes('cht8987')) return match;
                return p1.substring(0, 2) + '***@' + p2;
            });
            node.nodeValue = text;
        } else if (node.nodeType === 1 && node.nodeName !== 'SCRIPT' && node.nodeName !== 'STYLE') {
            for (let child of node.childNodes) {
                walk(child);
            }
        }
    };
    walk(document.body);
}
"""

with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        headless=True
    )

    # 1. ADMIN CONTEXT
    admin_context = browser.new_context(
        storage_state="/Users/elson/Documents/ts-lms-staff-training-1117/scripts/admin_state.json",
        viewport={"width": 1440, "height": 900}
    )
    admin_page = admin_context.new_page()

    print("--- Capturing Topic 1: Enrolment ---")
    # 1.1 Enrolments List
    admin_page.goto("https://lms.topscholar.edu.my/admin/ts-crm/enrollments")
    admin_page.wait_for_timeout(2500)
    admin_page.evaluate(MASK_JS)
    admin_page.screenshot(path=f"{RAW_DIR}/01_enrolment_list.png")
    print("1.1 Captured 01_enrolment_list.png")

    # 1.2 Enrolment Create (AI Parse & Student Info)
    admin_page.goto("https://lms.topscholar.edu.my/admin/ts-crm/enrollment/create")
    admin_page.wait_for_timeout(2500)
    try:
        parse_box = admin_page.query_selector('textarea[name="raw_text"], textarea#raw_text, textarea')
        if parse_box:
            parse_box.fill("家长姓名：陈妈妈\n联络电话：012-3456789\n学生姓名：[TEST] ELSON STUDENT ACC\n年级：Primary 4\n报读科目：BM, BI, BC, Math, Science")
    except Exception as e:
        print("Textarea fill skipped:", e)
    admin_page.screenshot(path=f"{RAW_DIR}/02_enrolment_create_ai_parse.png")
    print("1.2 Captured 02_enrolment_create_ai_parse.png")

    # 1.3 Enrolment Packages & Add-on (scroll down)
    admin_page.evaluate("window.scrollBy(0, 600)")
    admin_page.wait_for_timeout(1000)
    admin_page.screenshot(path=f"{RAW_DIR}/03_enrolment_packages_addons.png")
    print("1.3 Captured 03_enrolment_packages_addons.png")

    # 1.4 Enrolment Payment & Save review (scroll to bottom)
    admin_page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    admin_page.wait_for_timeout(1000)
    admin_page.screenshot(path=f"{RAW_DIR}/04_enrolment_payment_review.png")
    print("1.4 Captured 04_enrolment_payment_review.png")

    # 1.5 Enrolment Detail Invoice (Test Student Enrollment)
    admin_page.goto("https://lms.topscholar.edu.my/admin/ts-crm/enrollment/5375953/invoice")
    admin_page.wait_for_timeout(2500)
    admin_page.screenshot(path=f"{RAW_DIR}/05_enrolment_detail_invoice.png")
    print("1.5 Captured 05_enrolment_detail_invoice.png")

    print("--- Capturing Topic 2: Student Page & Changes ---")
    # 2.1 Student Profile (11960)
    admin_page.goto("https://lms.topscholar.edu.my/admin/ts-crm/students/11960")
    admin_page.wait_for_timeout(2500)
    admin_page.screenshot(path=f"{RAW_DIR}/06_student_profile_title_group.png")
    print("2.1 Captured 06_student_profile_title_group.png")

    # 2.2 Change Time
    admin_page.goto("https://lms.topscholar.edu.my/admin/ts-crm/students/11960/change-time")
    admin_page.wait_for_timeout(2000)
    admin_page.screenshot(path=f"{RAW_DIR}/07_student_change_time.png")
    print("2.2 Captured 07_student_change_time.png")

    # 2.3 Swap Class
    admin_page.goto("https://lms.topscholar.edu.my/admin/ts-crm/students/11960/swap-class")
    admin_page.wait_for_timeout(2000)
    admin_page.screenshot(path=f"{RAW_DIR}/08_student_swap_class.png")
    print("2.3 Captured 08_student_swap_class.png")

    # 2.4 Transfer
    admin_page.goto("https://lms.topscholar.edu.my/admin/ts-crm/students/11960/transfer")
    admin_page.wait_for_timeout(2000)
    admin_page.screenshot(path=f"{RAW_DIR}/09_student_transfer.png")
    print("2.4 Captured 09_student_transfer.png")

    print("--- Capturing Topic 3: Homework (Teacher & Grading) ---")
    # 3.1 Homework list
    admin_page.goto("https://lms.topscholar.edu.my/admin/ts-homework")
    admin_page.wait_for_timeout(2500)
    admin_page.evaluate(MASK_JS)
    admin_page.screenshot(path=f"{RAW_DIR}/10_homework_admin_list.png")
    print("3.1 Captured 10_homework_admin_list.png")

    # 3.2 Homework Marking
    admin_page.goto("https://lms.topscholar.edu.my/admin/ts-homework/marking")
    admin_page.wait_for_timeout(2500)
    admin_page.evaluate(MASK_JS)
    admin_page.screenshot(path=f"{RAW_DIR}/11_homework_marking_list.png")
    print("3.2 Captured 11_homework_marking_list.png")

    # 3.3 Homework Assignation & Options
    admin_page.goto("https://lms.topscholar.edu.my/admin/ts-homework/assignation")
    admin_page.wait_for_timeout(2500)
    admin_page.screenshot(path=f"{RAW_DIR}/12_homework_assignation.png")
    print("3.3 Captured 12_homework_assignation.png")

    print("--- Capturing Topic 4: Students Behaviour & Care ---")
    # 4.1 Class Records
    admin_page.goto("https://lms.topscholar.edu.my/admin/ts-care/class-records")
    admin_page.wait_for_timeout(2500)
    admin_page.evaluate(MASK_JS)
    admin_page.screenshot(path=f"{RAW_DIR}/13_class_records_list.png")
    print("4.1 Captured 13_class_records_list.png")

    # 4.2 Care List
    admin_page.goto("https://lms.topscholar.edu.my/admin/ts-care")
    admin_page.wait_for_timeout(2500)
    admin_page.evaluate(MASK_JS)
    admin_page.screenshot(path=f"{RAW_DIR}/14_care_list.png")
    print("4.2 Captured 14_care_list.png")

    print("--- Capturing Topic 5: Student Email & Password (Staff side) ---")
    # 5.1 Admin edit student
    admin_page.goto("https://lms.topscholar.edu.my/admin/ts-crm/students/11960/edit")
    admin_page.wait_for_timeout(2500)
    admin_page.screenshot(path=f"{RAW_DIR}/15_student_edit_credentials.png")
    print("5.1 Captured 15_student_edit_credentials.png")

    admin_context.close()

    # 2. STUDENT CONTEXT (Desktop & Mobile)
    print("--- Capturing Student Views (Desktop & Mobile) ---")
    student_desktop = browser.new_context(
        storage_state="/Users/elson/Documents/ts-lms-staff-training-1117/scripts/student_state.json",
        viewport={"width": 1440, "height": 900}
    )
    s_page = student_desktop.new_page()

    # 6.1 Student Home (Bana Games entry & overview)
    s_page.goto("https://lms.topscholar.edu.my/panel")
    s_page.wait_for_timeout(2500)
    s_page.screenshot(path=f"{RAW_DIR}/16_student_home_bana_entry.png")
    print("6.1 Captured 16_student_home_bana_entry.png")

    # 5.2 Student Setting (Change password)
    s_page.goto("https://lms.topscholar.edu.my/panel/setting")
    s_page.wait_for_timeout(2500)
    s_page.screenshot(path=f"{RAW_DIR}/17_student_setting_password.png")
    print("5.2 Captured 17_student_setting_password.png")

    # 3.4 Student Homeworks
    s_page.goto("https://lms.topscholar.edu.my/panel/homeworks")
    s_page.wait_for_timeout(2500)
    s_page.screenshot(path=f"{RAW_DIR}/18_student_homeworks_desktop.png")
    print("3.4 Captured 18_student_homeworks_desktop.png")

    # 6.2 Bana Go redirect / launch
    s_page.goto("https://lms.topscholar.edu.my/bana/go")
    s_page.wait_for_timeout(2500)
    s_page.screenshot(path=f"{RAW_DIR}/22_bana_go_launch.png")
    print("6.2 Captured 22_bana_go_launch.png")

    student_desktop.close()

    # Student Mobile (390 x 844)
    student_mobile = browser.new_context(
        storage_state="/Users/elson/Documents/ts-lms-staff-training-1117/scripts/student_state.json",
        viewport={"width": 390, "height": 844},
        is_mobile=True
    )
    m_page = student_mobile.new_page()

    # Mobile Student Home
    m_page.goto("https://lms.topscholar.edu.my/panel")
    m_page.wait_for_timeout(2500)
    m_page.screenshot(path=f"{RAW_DIR}/19_student_home_mobile.png")
    print("Mobile 19_student_home_mobile.png")

    # Mobile Student Homeworks
    m_page.goto("https://lms.topscholar.edu.my/panel/homeworks")
    m_page.wait_for_timeout(2500)
    m_page.screenshot(path=f"{RAW_DIR}/20_student_homeworks_mobile.png")
    print("Mobile 20_student_homeworks_mobile.png")

    student_mobile.close()

    # 3. PUBLIC GUEST (Forgot Password)
    guest_context = browser.new_context(viewport={"width": 1440, "height": 900})
    g_page = guest_context.new_page()
    g_page.goto("https://lms.topscholar.edu.my/forget-password")
    g_page.wait_for_timeout(2000)
    g_page.screenshot(path=f"{RAW_DIR}/21_forgot_password.png")
    print("5.3 Captured 21_forgot_password.png")
    guest_context.close()

    browser.close()
    print("ALL RAW SCREENSHOTS SUCCESSFULLY CAPTURED!")
