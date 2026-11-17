import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
import urllib.parse
from playwright.sync_api import sync_playwright
from probe_urls import get_cookie

BASE = "https://lms.topscholar.edu.my"
OUT_RAW = os.path.expanduser("~/Documents/ts-lms-staff-training-1117/assets/raw")

def set_c(ctx, c):
    ctx.add_cookies([{
        "name": "rocket_lms_session",
        "value": urllib.parse.quote(c),
        "domain": "lms.topscholar.edu.my",
        "path": "/",
        "httpOnly": True,
        "secure": True,
        "sameSite": "Lax",
    }])

MASK_LIVE_JS = r"""
() => {
  const SAFE = ['ELSON STUDENT', 'GOH MEI MEI', 'TS-011960', 'TS-016493', '[TEST]', 'Elson'];
  // Mask any student roster rows or student search options or chat names
  document.querySelectorAll('table tbody tr, [data-student-id], .ts-live-stu, .ts-live-row, .list-group-item').forEach((row, idx) => {
    const t = row.innerText || '';
    if (!t.trim() || SAFE.some(s => t.includes(s))) return;
    if (/TS-\d+|G\d+|Present|Absent|Attended|@|01\d/.test(t) || row.tagName === 'TR') {
      const walker = document.createTreeWalker(row, NodeFilter.SHOW_TEXT);
      let n;
      let named = false;
      while (n = walker.nextNode()) {
        const s = n.textContent.trim();
        if (!s) continue;
        if (/^TS-\d+/.test(s)) n.textContent = 'TS-00010' + (idx + 1);
        else if (/@/.test(s)) n.textContent = 'demo' + (idx + 1) + '@example.com';
        else if (/\+?6?01\d[\d\s-]{5,}/.test(s)) n.textContent = '012-000 000' + (idx + 1);
        else if (!named && s.length > 2 && !/^(G\d+|Present|Absent|Late|Yes|No|Mark|Save|Undo|All|Live|Online|Offline|Points|—|-|\d+|\+\d+)$/i.test(s)) {
          n.textContent = 'Demo Student ' + String.fromCharCode(65 + (idx % 20));
          named = true;
        }
      }
    }
  });
}
"""

def main():
    adm_c = get_cookie(1)
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True)
        ac = b.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
        set_c(ac, adm_c)
        ap = ac.new_page()

        # 1. Pause & Convert for Topic 2
        ap.goto(BASE + "/admin/ts-crm/students/16493/pause", wait_until="domcontentloaded", timeout=30000)
        ap.wait_for_timeout(700)
        ap.screenshot(path=os.path.join(OUT_RAW, "t2_06_pause.png"))
        print("Saved t2_06_pause.png")

        ap.goto(BASE + "/admin/ts-crm/enrollment/5375953/convert", wait_until="domcontentloaded", timeout=30000)
        ap.wait_for_timeout(700)
        ap.screenshot(path=os.path.join(OUT_RAW, "t2_07_convert.png"))
        print("Saved t2_07_convert.png")

        # 2. Care Live Index (/admin/ts-care/live)
        ap.goto(BASE + "/admin/ts-care/live", wait_until="domcontentloaded", timeout=30000)
        ap.wait_for_timeout(800)
        ap.screenshot(path=os.path.join(OUT_RAW, "t4_03_care_live_index.png"))
        print("Saved t4_03_care_live_index.png", ap.url)

        # Find first Enter class link or fallback session 26764 / 26336
        live_links = ap.eval_on_selector_all("a", "els => els.map(e => e.getAttribute('href')).filter(h => h && /\\/ts-care\\/live\\/\\d+/.test(h))")
        print("Live links found:", live_links[:5])
        target_live = live_links[0] if live_links else "/admin/ts-care/live/26764"
        if not target_live.startswith("http"):
            target_live = BASE + target_live
        ap.goto(target_live, wait_until="domcontentloaded", timeout=30000)
        ap.wait_for_timeout(1000)
        ap.evaluate(MASK_LIVE_JS)
        ap.wait_for_timeout(200)
        ap.screenshot(path=os.path.join(OUT_RAW, "t4_04_care_live_show.png"))
        print("Saved t4_04_care_live_show.png", ap.url, ap.title())

        ac.close()
        b.close()

if __name__ == "__main__":
    main()
