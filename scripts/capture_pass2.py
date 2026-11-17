import os
import urllib.parse
from playwright.sync_api import sync_playwright
from capture_all import get_cookie, set_session_cookie, BASE, OUT_RAW

STRICT_SANITIZE_JS = r"""
() => {
  const SAFE_TOKENS = [
    'ELSON STUDENT ACC', 'GOH MEI MEI', 'TS-011960', 'TS-016493',
    'TEST-45253', 'TEST-50956', 'TS2610001097', 'TS2610001103',
    'cht8987@gmail.com', 'operation.topscholar@gmail.com',
    'INV-2026-017209', '[TEST]'
  ];
  const isSafe = (txt) => {
    if (!txt) return false;
    return SAFE_TOKENS.some(tok => txt.includes(tok));
  };

  const url = location.pathname;
  const isSingleTestDetail = /\/admin\/ts-crm\/students\/(11960|16493)/.test(url)
    || /\/admin\/ts-crm\/enrollment\/(5375953|5387771|5390306|5390328)/.test(url)
    || /\/admin\/ts-care\/student\/(11960|16493)/.test(url)
    || /\/admin\/ts-homework\/\d+\/submissions\/(45253|50956)/.test(url)
    || /\/admin\/users\/(45253|50956)/.test(url);

  if (isSingleTestDetail) return;

  // 1. On enrollments list, mask aggregate totals if not filtered to TEST, and mask every non-test row
  document.querySelectorAll('table tbody tr').forEach((tr, idx) => {
    const rowText = tr.innerText || '';
    if (isSafe(rowText)) return;
    // Mask every cell in non-test rows if table looks like enrollments, students, submissions, or class records
    const isPiiTable = /\/enrollments|\/students|\/submissions|\/class-records/.test(url);
    if (!isPiiTable) return;

    const demoNames = ['Demo Student A', 'Demo Student B', 'Demo Student C', 'Demo Student D', 'Demo Student E', 'Demo Student F'];
    const dName = demoNames[idx % demoNames.length];
    const dCode = `TS-00010${idx + 1}`;

    tr.querySelectorAll('td').forEach((td) => {
      const t = td.innerText.trim();
      if (!t || isSafe(t)) return;
      // Walk text nodes inside td
      const walker = document.createTreeWalker(td, NodeFilter.SHOW_TEXT);
      const nodes = [];
      let n;
      while (n = walker.nextNode()) nodes.push(n);
      nodes.forEach(tn => {
        const s = tn.textContent.trim();
        if (!s) return;
        if (/^TS-\d+/.test(s)) tn.textContent = dCode;
        else if (/^INV-/.test(s)) tn.textContent = `INV-2026-00000${idx + 1}`;
        else if (/^TS\d{6,}/.test(s)) tn.textContent = `TS2611000${idx + 1}`;
        else if (/@/.test(s)) tn.textContent = `demo${idx + 1}@example.com`;
        else if (/\+?6?01\d[\d\s-]{5,}/.test(s)) tn.textContent = `012-000 000${idx + 1}`;
        else if (/RM\s*[\d,]+\.\d{2}/.test(s)) tn.textContent = s.replace(/RM\s*[\d,]+\.\d{2}/g, 'RM ***.00');
        else if (s.length > 3 && /^[A-Za-z\s.'\-/@()]+$/.test(s) && !/^(Not submitted|Submitted|Completed|Marking|Paid|Pending|Waived|All|View|Edit|Mark|COACH|G\d+)$/i.test(s)) {
          // Check if this td is student column or name-like
          if (td.cellIndex <= 2 || td.querySelector('a')) {
            tn.textContent = dName;
          }
        }
      });
    });
  });

  // 2. Mask any group-finder / class-records student rows (divs/cards)
  document.querySelectorAll('[data-student-id], .gf-row, .ts-gf-row, .ts-stu-row, tr[data-id]').forEach((row, idx) => {
    if (isSafe(row.innerText || '')) return;
    const walker = document.createTreeWalker(row, NodeFilter.SHOW_TEXT);
    let n;
    let replacedName = false;
    while (n = walker.nextNode()) {
      const s = n.textContent.trim();
      if (!s) continue;
      if (/^TS-\d+/.test(s)) n.textContent = `TS-00010${idx + 1}`;
      else if (/@/.test(s)) n.textContent = `demo${idx + 1}@example.com`;
      else if (/\+?6?01\d[\d\s-]{5,}/.test(s)) n.textContent = `012-000 000${idx + 1}`;
      else if (!replacedName && s.length > 3 && /^[A-Za-z\s.'\-]+$/.test(s) && !/^(View|Save|Saved|Present|Absent|Late|G\d+)$/i.test(s)) {
        n.textContent = `Demo Student ${String.fromCharCode(65 + (idx % 12))}`;
        replacedName = true;
      }
    }
  });
}
"""

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

        # Admin 1440x900
        adm = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
        set_session_cookie(adm, adm_cookie)
        page = adm.new_page()

        # T1-01: Enrollments list filtered to TEST via UI search box
        page.goto(BASE + "/admin/ts-crm/enrollments", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(800)
        search_inp = page.locator('input[name="search"], input[name="q"], input[placeholder*="Order no."]').first
        if search_inp.count() > 0:
            search_inp.fill("TEST-")
            filter_btn = page.locator('button:has-text("Filter")').first
            if filter_btn.count() > 0:
                filter_btn.click()
                page.wait_for_timeout(1200)
        save(page, "t1_01_enrollments_list.png")

        # T1-02b: New student -> reveals AI parse box!
        page.goto(BASE + "/admin/ts-crm/enrollment/create", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(800)
        new_btn = page.locator('button:has-text("New student"), label:has-text("New student")').first
        if new_btn.count() > 0:
            new_btn.click()
            page.wait_for_timeout(600)
        save(page, "t1_02b_enrollment_ai_parse.png", full_page=False)

        # T1-02c/d/e: Existing test student -> Step 2 (Package) -> Step 3 (Add-on) -> Step 4 (Payment)
        page.goto(BASE + "/admin/ts-crm/enrollment/create", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(800)
        stu_search = page.locator('input[placeholder*="Search by name"]').first
        stu_search.fill("TS-011960")
        page.wait_for_timeout(1000)
        # Click first dropdown result containing ELSON STUDENT ACC
        opt = page.locator('text=[TEST] ELSON STUDENT ACC').first
        if opt.count() > 0:
            opt.click()
            page.wait_for_timeout(700)
            next_btn = page.locator('button:has-text("Next")').first
            if next_btn.count() > 0:
                next_btn.click()
                page.wait_for_timeout(600)
                save(page, "t1_02c_enrollment_step2_package.png")
                # Pick first package option so Step 3 & Step 4 unlock cleanly
                pkg_sel = page.locator('select[name="package_id"]').first
                if pkg_sel.count() > 0:
                    vals = pkg_sel.locator('option').evaluate_all("els => els.map(e => e.value).filter(v => v)")
                    if vals:
                        pkg_sel.select_option(vals[0])
                        page.wait_for_timeout(600)
                next_btn.click()
                page.wait_for_timeout(600)
                save(page, "t1_02d_enrollment_step3_addon.png")
                next_btn.click()
                page.wait_for_timeout(600)
                save(page, "t1_02e_enrollment_step4_payment.png")

        # T2-01b: Student 11960 scrolled to Classes & Actions buttons
        page.goto(BASE + "/admin/ts-crm/students/11960", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(800)
        btn = page.locator('a:has-text("Change time")').first
        if btn.count() > 0:
            btn.scroll_into_view_if_needed()
            page.wait_for_timeout(400)
        save(page, "t2_01b_student_classes_actions.png")

        # T2-05: Transfer on 16493 (GOH MEI MEI has 2027-1)
        page.goto(BASE + "/admin/ts-crm/students/16493/transfer", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(800)
        save(page, "t2_05_transfer.png")

        # T3-03: Submissions list filtered cleanly to GOH MEI MEI
        page.goto(BASE + "/admin/ts-homework/190/submissions", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(800)
        sub_search = page.locator('input[placeholder*="Search student"]').first
        if sub_search.count() > 0:
            sub_search.fill("GOH MEI MEI")
            page.wait_for_timeout(500)
        # Also remove/mask any non-test rows that remain
        page.evaluate(r"""() => {
          document.querySelectorAll('table tbody tr').forEach((tr, i) => {
            if (!tr.innerText.includes('GOH MEI MEI') && !tr.innerText.includes('ELSON STUDENT')) {
              tr.style.display = 'none';
            }
          });
        }""")
        save(page, "t3_03_admin_submissions.png")

        # T3-04b: Grade page for submitted (2351/50956)
        page.goto(BASE + "/admin/ts-homework/2351/submissions/50956", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(800)
        save(page, "t3_04b_admin_grade_submitted.png")

        # T4-01b: Class records -> pick Y1-Y3 -> pick first class -> mask all non-test rows!
        page.goto(BASE + "/admin/ts-care/class-records", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(800)
        band = page.locator('a:has-text("Y1-Y3"), button:has-text("Y1-Y3")').first
        if band.count() > 0:
            band.click()
            page.wait_for_timeout(800)
            cls_btn = page.locator('a[href*="class-records"], button:has-text("BM"), a:has-text("BM")').first
            if cls_btn.count() > 0:
                cls_btn.click()
                page.wait_for_timeout(1000)
        save(page, "t4_01b_class_records_roster.png")

        # T5-02b: Admin user edit scrolled to Email & Password
        page.goto(BASE + "/admin/users/45253/edit", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(800)
        email_inp = page.locator('input[name="email"]').first
        if email_inp.count() > 0:
            email_inp.scroll_into_view_if_needed()
            page.wait_for_timeout(400)
        save(page, "t5_02b_admin_user_email_pwd.png")

        adm.close()

        # Student Desktop 1440x900
        stu = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
        set_session_cookie(stu, stu_mei_cookie)
        sp = stu.new_page()

        # T3-05b / 05c: Homework tabs
        sp.goto(BASE + "/panel/ts-homework", wait_until="domcontentloaded", timeout=30000)
        sp.wait_for_timeout(800)
        tab_m = sp.locator('button:has-text("批改中"), a:has-text("批改中")').first
        if tab_m.count() > 0:
            tab_m.click()
            sp.wait_for_timeout(500)
            save(sp, "t3_05b_student_hw_marking_tab.png", is_admin=False)
        tab_d = sp.locator('button:has-text("改好了"), a:has-text("改好了")').first
        if tab_d.count() > 0:
            tab_d.click()
            sp.wait_for_timeout(500)
            save(sp, "t3_05c_student_hw_marked_tab.png", is_admin=False)

        # T3-07b: Student submitted homework 2351 (can edit/change before marking starts!)
        sp.goto(BASE + "/panel/ts-homework/2351", wait_until="domcontentloaded", timeout=30000)
        sp.wait_for_timeout(800)
        save(sp, "t3_07b_student_hw_edit_submitted.png", is_admin=False)

        # T6-03: Click Bana link (/panel/bana/go) -> screenshot Bana World landing
        sp.goto(BASE + "/panel", wait_until="domcontentloaded", timeout=30000)
        sp.wait_for_timeout(1200)
        bana_link = sp.locator('[data-ts-bana-link]').first
        if bana_link.count() > 0:
            bana_link.click()
            sp.wait_for_timeout(4000)
            save(sp, "t6_03_bana_world.png", is_admin=False)

        stu.close()
        browser.close()

if __name__ == "__main__":
    main()
