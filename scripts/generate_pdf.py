from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        headless=True
    )
    page = browser.new_page()
    page.goto("file:///Users/elson/Documents/ts-lms-staff-training-1117/guide.html", wait_until="networkidle")
    page.wait_for_timeout(2000)
    
    pdf_path = "/Users/elson/Documents/ts-lms-staff-training-1117/guide.pdf"
    page.pdf(
        path=pdf_path,
        format="A4",
        print_background=True,
        margin={"top": "20mm", "bottom": "20mm", "left": "15mm", "right": "15mm"}
    )
    print("PDF generated successfully at:", pdf_path)
    browser.close()
