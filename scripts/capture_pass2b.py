import os
import urllib.parse
from playwright.sync_api import sync_playwright
from capture_all import get_cookie, set_session_cookie, BASE, OUT_RAW
from capture_pass2 import STRICT_SANITIZE_JS

def save(page, name, full_page=False, is_admin=True):
    if is_admin:
        page.evaluate(STRICT_SANITIZE_JS)
        page.wait_for_timeout(150)
    out = os.path.join(OUT_RAW, name)
    page.screenshot(path=out, full_page=full_page)
    print(f"Saved {name} ({page.url})")

def main():
    adm_cookie = get_cookie(1)
    stu_mei_cookie = get_cookie(50956)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)

        adm = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
        set_session_cookie(adm, adm_cookie)
        page = adm.new_page()
        page.set_default_timeout(8000)

        # T1-02b: Click "New student" first, then "#ts-paste-open" to reveal AI parse textarea!
        try:
            page.goto(BASE + "/admin/ts-crm/enrollment/create", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(600)
            page.locator('button:has-text("New student"), label:has-text("New student")').first.click()
            page.wait_for_timeout(400)
            page.locator('#ts-paste-open').first.click()
            page.wait_for_timeout(500)
            save(page, "t1_02b_enrollment_ai_parse.png", full_page=False)
        except Exception as e:
            print("WARN t1_02b:", e)

        # T1-02c/d/e: Existing test student -> Step 2 (click 国英特训 package) -> Step 3 -> Step 4
        try:
            page.goto(BASE + "/admin/ts-crm/enrollment/create", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(600)
            stu_search = page.locator('input[placeholder*="Search by name"]').first
            stu_search.fill("TS-011960")
            page.wait_for_timeout(900)
            page.locator('text=[TEST] ELSON STUDENT ACC').first.click()
            page.wait_for_timeout(600)
            next_btn = page.locator('button:has-text("Next")').first
            next_btn.click()
            page.wait_for_timeout(500)
            page.locator('text=国英特训 package').first.click()
            page.wait_for_timeout(600)
            page.evaluate("""() => {
              const s = document.getElementById('ts-package');
              if (s && s.options.length > 1) {
                for (let i = 1; i < s.options.length; i++) {
                  if (s.options[i].value) { s.value = s.options[i].value; break; }
                }
                if (window.jQuery) jQuery(s).trigger('change');
                else s.dispatchEvent(new Event('change', {bubbles:true}));
              }
            }""")
            page.wait_for_timeout(700)
            save(page, "t1_02c_enrollment_step2_package.png")
            next_btn.click()
            page.wait_for_timeout(600)
            save(page, "t1_02d_enrollment_step3_addon.png")
            # Select one subject if needed so Step 4 shows properly
            page.evaluate("""() => {
              const chk = document.querySelector('#ts-step-3 input[type="checkbox"], #ts-step-3 select');
              if (chk && chk.type === 'checkbox' && !chk.checked) { chk.click(); }
            }""")
            page.wait_for_timeout(400)
            next_btn.click()
            page.wait_for_timeout(600)
            save(page, "t1_02e_enrollment_step4_payment.png")
        except Exception as e:
            print("WARN t1_02cde:", e)

        # T2-01b: Student 11960 scrolled to Classes & Actions buttons
        try:
            page.goto(BASE + "/admin/ts-crm/students/11960", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(600)
            page.locator('a:has-text("Change time")').first.scroll_into_view_if_needed()
            page.wait_for_timeout(400)
            save(page, "t2_01b_student_classes_actions.png")
        except Exception as e:
            print("WARN t2_01b:", e)

        # T2-05: Transfer on 16493
        try:
            page.goto(BASE + "/admin/ts-crm/students/16493/transfer", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(600)
            save(page, "t2_05_transfer.png")
        except Exception as e:
            print("WARN t2_05:", e)

        # T3-03: Submissions list filtered cleanly to GOH MEI MEI
        try:
            page.goto(BASE + "/admin/ts-homework/190/submissions", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(600)
            sub_search = page.locator('input[placeholder*="Search student"]').first
            if sub_search.count() > 0:
                sub_search.fill("GOH MEI MEI")
                page.wait_for_timeout(400)
            page.evaluate(r"""() => {
              document.querySelectorAll('table tbody tr').forEach((tr) => {
                if (!tr.innerText.includes('GOH MEI MEI') && !tr.innerText.includes('ELSON STUDENT')) {
                  tr.style.display = 'none';
                }
              });
            }""")
            save(page, "t3_03_admin_submissions.png")
        except Exception as e:
            print("WARN t3_03:", e)

        # T3-04b: Grade page for submitted (2351/50956)
        try:
            page.goto(BASE + "/admin/ts-homework/2351/submissions/50956", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(600)
            save(page, "t3_04b_admin_grade_submitted.png")
        except Exception as e:
            print("WARN t3_04b:", e)

        # T4-01b: Class records -> pick Y1-Y3 -> pick first class -> mask all non-test rows!
        try:
            page.goto(BASE + "/admin/ts-care/class-records", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(600)
            page.locator('a:has-text("Y1-Y3"), button:has-text("Y1-Y3")').first.click()
            page.wait_for_timeout(700)
            page.locator('a[href*="class-records"], button:has-text("BM"), a:has-text("BM")').first.click()
            page.wait_for_timeout(800)
            save(page, "t4_01b_class_records_roster.png")
        except Exception as e:
            print("WARN t4_01b:", e)

        # T5-02b: Admin user edit scrolled to Email & Password
        try:
            page.goto(BASE + "/admin/users/45253/edit", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(600)
            page.locator('input[name="email"]').first.scroll_into_view_if_needed()
            page.wait_for_timeout(400)
            save(page, "t5_02b_admin_user_email_pwd.png")
        except Exception as e:
            print("WARN t5_02b:", e)

        adm.close()

        # Student Desktop 1440x900
        stu = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
        set_session_cookie(stu, stu_mei_cookie)
        sp = stu.new_page()
        sp.set_default_timeout(8000)

        try:
            sp.goto(BASE + "/panel/ts-homework", wait_until="domcontentloaded", timeout=30000)
            sp.wait_for_timeout(600)
            sp.locator('button:has-text("批改中"), a:has-text("批改中")').first.click()
            sp.wait_for_timeout(400)
            save(sp, "t3_05b_student_hw_marking_tab.png", is_admin=False)
            sp.locator('button:has-text("改好了"), a:has-text("改好了")').first.click()
            sp.wait_for_timeout(400)
            save(sp, "t3_05c_student_hw_marked_tab.png", is_admin=False)
        except Exception as e:
            print("WARN t3_05bc:", e)

        try:
            sp.goto(BASE + "/panel/ts-homework/2351", wait_until="domcontentloaded", timeout=30000)
            sp.wait_for_timeout(600)
            save(sp, "t3_07b_student_hw_edit_submitted.png", is_admin=False)
        except Exception as e:
            print("WARN t3_07b:", e)

        try:
            sp.goto(BASE + "/panel", wait_until="domcontentloaded", timeout=30000)
            sp.wait_for_timeout(1000)
            sp.locator('[data-ts-bana-link]').first.click()
            sp.wait_for_timeout(3500)
            save(sp, "t6_03_bana_world.png", is_admin=False)
        except Exception as e:
            print("WARN t6_03:", e)

        stu.close()
        browser.close()

if __name__ == "__main__":
    main()
