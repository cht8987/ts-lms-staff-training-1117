import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
from playwright.sync_api import sync_playwright
from probe_urls import get_cookie
import urllib.parse

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

def main():
    adm_c = get_cookie(1)
    stu_c = get_cookie(50956)
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True)
        ac = b.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
        set_c(ac, adm_c)
        ap = ac.new_page()
        ap.goto(BASE + "/admin/ts-care/class-records?stage=Y1-Y3&term=62", wait_until="domcontentloaded", timeout=30000)
        ap.wait_for_timeout(600)
        hrefs = ap.eval_on_selector_all("a", "els => els.map(e => e.getAttribute('href')).filter(h => h && h.includes('class-records'))")
        cls_links = [h for h in hrefs if "stage=" in h and "term=" in h and ("course=" in h or "class=" in h or h.count("&") >= 2)]
        print("cls_links:", cls_links[:5])
        if cls_links:
            u = cls_links[0] if cls_links[0].startswith("http") else BASE + cls_links[0]
            ap.goto(u, wait_until="domcontentloaded", timeout=30000)
            ap.wait_for_timeout(1000)
            ap.evaluate(r"""() => {
              const SAFE = ["ELSON STUDENT", "GOH MEI MEI", "TS-011960", "TS-016493", "[TEST]"];
              document.querySelectorAll("table tbody tr").forEach((tr, idx) => {
                if (SAFE.some(s => tr.innerText.includes(s))) return;
                tr.querySelectorAll("td").forEach((td, ci) => {
                  td.querySelectorAll("a, strong, div, span, small").forEach(el => {
                    if (el.children.length > 0) return;
                    const s = el.textContent.trim();
                    if (!s) return;
                    if (/^TS-\d+/.test(s)) el.textContent = "TS-00010" + (idx+1);
                    else if (/@/.test(s)) el.textContent = "demo" + (idx+1) + "@example.com";
                    else if (/\+?6?01\d[\d\s-]{5,}/.test(s)) el.textContent = "012-000 000" + (idx+1);
                    else if (ci <= 1 && s.length > 2 && !/^(View|Save|Group|G\d+|—|-|\d+)$/i.test(s) && !/^G\d+$/.test(s)) {
                      el.textContent = "Demo Student " + String.fromCharCode(65 + (idx % 20));
                    }
                  });
                });
              });
            }""")
            ap.screenshot(path=os.path.join(OUT_RAW, "t4_01b_class_records_roster.png"))
            print("Saved roster:", ap.url)
        ac.close()

        sc = b.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
        set_c(sc, stu_c)
        sp = sc.new_page()
        sp.goto(BASE + "/panel/ts-homework", wait_until="domcontentloaded", timeout=30000)
        sp.wait_for_timeout(600)
        tabs = sp.eval_on_selector_all("[data-ts-hwk-tab]", "els => els.map(e => e.getAttribute('data-ts-hwk-tab'))")
        print("HW tabs:", tabs)
        for t in tabs:
            if t != "todo":
                sp.locator(f'[data-ts-hwk-tab="{t}"]').first.click()
                sp.wait_for_timeout(400)
                sp.screenshot(path=os.path.join(OUT_RAW, f"t3_05_{t}_tab.png"))

        sp.goto(BASE + "/panel", wait_until="domcontentloaded", timeout=30000)
        sp.wait_for_timeout(900)
        sp.locator("[data-ts-bana-link]").first.click()
        try:
            sp.wait_for_url(lambda u: "sso.html" not in u and "game.topscholar.cloud" in u, timeout=12000)
            sp.wait_for_timeout(2500)
        except Exception as e:
            print("Bana wait:", e, sp.url)
        sp.screenshot(path=os.path.join(OUT_RAW, "t6_03_bana_world.png"))
        print("Bana final url:", sp.url)
        sc.close()
        b.close()

if __name__ == "__main__":
    main()
