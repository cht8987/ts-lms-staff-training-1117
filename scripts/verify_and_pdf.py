import os
from playwright.sync_api import sync_playwright

ROOT = os.path.expanduser("~/Documents/ts-lms-staff-training-1117")
SCRATCH = os.path.join(ROOT, "scripts", "verify_out")
os.makedirs(SCRATCH, exist_ok=True)

def main():
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True)

        # 1. Export guide.pdf from guide.html
        ctx_pdf = b.new_context(viewport={"width": 1200, "height": 900})
        gp = ctx_pdf.new_page()
        gp.goto("file://" + os.path.join(ROOT, "guide.html"), wait_until="networkidle")
        gp.wait_for_timeout(800)
        gp.pdf(
            path=os.path.join(ROOT, "guide.pdf"),
            format="A4",
            print_background=True,
            margin={"top": "14mm", "right": "12mm", "bottom": "14mm", "left": "12mm"},
        )
        print("Generated guide.pdf:", os.path.getsize(os.path.join(ROOT, "guide.pdf")), "bytes")

        # 2. Verify guide.html desktop + interactive tour click
        gp.set_viewport_size({"width": 1440, "height": 900})
        gp.wait_for_timeout(300)
        gp.locator('[data-tour="t1"] [data-next]').click()
        gp.wait_for_timeout(500)
        gp.screenshot(path=os.path.join(SCRATCH, "verify_guide_desktop.png"))

        # Verify guide.html mobile 390px
        gp.set_viewport_size({"width": 390, "height": 844})
        gp.wait_for_timeout(300)
        gp.screenshot(path=os.path.join(SCRATCH, "verify_guide_mobile.png"))
        ctx_pdf.close()

        # 3. Verify slides.html keyboard nav + rendering
        ctx_s = b.new_context(viewport={"width": 1440, "height": 900})
        sp = ctx_s.new_page()
        sp.goto("file://" + os.path.join(ROOT, "slides.html"), wait_until="networkidle")
        sp.wait_for_timeout(400)
        sp.screenshot(path=os.path.join(SCRATCH, "verify_slides_cover.png"))
        sp.keyboard.press("ArrowRight")
        sp.wait_for_timeout(300)
        sp.keyboard.press("ArrowRight")
        sp.wait_for_timeout(400)
        print("Slides counter after 2x ArrowRight:", sp.locator("#slideCounter").inner_text())
        sp.screenshot(path=os.path.join(SCRATCH, "verify_slides_s3.png"))
        ctx_s.close()

        # 4. Verify index.html
        ctx_i = b.new_context(viewport={"width": 1440, "height": 900})
        ip = ctx_i.new_page()
        ip.goto("file://" + os.path.join(ROOT, "index.html"), wait_until="networkidle")
        ip.wait_for_timeout(400)
        ip.screenshot(path=os.path.join(SCRATCH, "verify_index.png"))
        ctx_i.close()

        b.close()

if __name__ == "__main__":
    main()
