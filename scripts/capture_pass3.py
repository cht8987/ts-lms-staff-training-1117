import os
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

        # 1. Class Records: Grade -> Term -> Class -> Roster + Points Panel
        page.goto(BASE + "/admin/ts-care/class-records", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(600)
        # Click Y1-Y3 card inside main content (not sidebar)
        page.locator('main a:has-text("Y1-Y3"), .main-content a:has-text("Y1-Y3"), a:has-text("Y1-Y3")').first.click()
        page.wait_for_timeout(800)
        # Click 2026-10 term card
        term_card = page.locator('.main-content a:has-text("2026-10"), a:has-text("2026-10")').first
        if term_card.count() > 0:
            term_card.click()
            page.wait_for_timeout(800)
        # Click first class card (e.g. Y1-Y3 BM or BI)
        cls_card = page.locator('.main-content a[href*="course_id"], a[href*="course_id"]').first
        if cls_card.count() > 0:
            cls_card.click()
            page.wait_for_timeout(1000)
        # Mask ALL non-test student rows strictly on Class Records!
        page.evaluate(r"""() => {
          const SAFE = ['ELSON STUDENT', 'GOH MEI MEI', 'TS-011960', 'TS-016493', '[TEST]'];
          document.querySelectorAll('table tbody tr').forEach((tr, idx) => {
            if (SAFE.some(s => tr.innerText.includes(s))) return;
            const tds = tr.querySelectorAll('td');
            tds.forEach((td, ci) => {
              const txt = td.innerText.trim();
              if (!txt) return;
              // Student column usually has name + code + phone + email
              if (ci === 0 || ci === 1 || /TS-\d+|@|01\d/.test(txt)) {
                td.querySelectorAll('a, strong, div, span, small').forEach(el => {
                  if (el.children.length > 0) return;
                  const s = el.textContent.trim();
                  if (!s) return;
                  if (/^TS-\d+/.test(s)) el.textContent = `TS-00010${idx+1}`;
                  else if (/@/.test(s)) el.textContent = `demo${idx+1}@example.com`;
                  else if (/\+?6?01\d[\d\s-]{5,}/.test(s)) el.textContent = `012-000 000${idx+1}`;
                  else if (s.length > 2 && !/^(View|Save|Group|G\d+|—|-|\d+)$/i.test(s) && !/^G\d+$/.test(s)) {
                    el.textContent = `Demo Student ${String.fromCharCode(65 + (idx % 20))}`;
                  }
                });
              }
            });
          });
        }""")
        save(page, "t4_01b_class_records_roster.png", full_page=False)

        # 2. Grade page bottom (Save / Release / Return to student buttons) on 2351/50956
        page.goto(BASE + "/admin/ts-homework/2351/submissions/50956", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(700)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(400)
        save(page, "t3_04c_admin_grade_actions.png", full_page=False)

        adm.close()

        # Student Desktop
        stu = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
        set_session_cookie(stu, stu_mei_cookie)
        sp = stu.new_page()
        sp.set_default_timeout(8000)

        sp.goto(BASE + "/panel/ts-homework", wait_until="domcontentloaded", timeout=30000)
        sp.wait_for_timeout(700)
        sp.locator('[data-ts-hwk-tab="marking"]').first.click()
        sp.wait_for_timeout(400)
        save(sp, "t3_05b_student_hw_marking_tab.png", is_admin=False)
        sp.locator('[data-ts-hwk-tab="marked"]').first.click()
        sp.wait_for_timeout(400)
        save(sp, "t3_05c_student_hw_marked_tab.png", is_admin=False)

        # Bana World: navigate via /panel/bana/go and wait for redirect off sso.html
        sp.goto(BASE + "/panel", wait_until="domcontentloaded", timeout=30000)
        sp.wait_for_timeout(1200)
        sp.locator('[data-ts-bana-link]').first.click()
        try:
            sp.wait_for_url(lambda u: "sso.html" not in u and "game.topscholar.cloud" in u, timeout=10000)
            sp.wait_for_timeout(2000)
        except Exception as e:
            print("Bana wait note:", e, sp.url)
        save(sp, "t6_03_bana_world.png", is_admin=False)

        stu.close()
        browser.close()

if __name__ == "__main__":
    main()
