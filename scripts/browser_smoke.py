"""An actual Chromium-to-Vite-to-PostgreSQL smoke test, not a mocked API test."""
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
from pypdf import PdfWriter


def main():
    pdf = Path("/tmp/cvguard-e2e-resume.pdf")
    writer = PdfWriter()
    writer.add_blank_page(width=595, height=842)
    with pdf.open("wb") as out:
        writer.write(out)

    errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 850})
        page.on("pageerror", lambda error: errors.append(str(error)))

        page.goto("http://127.0.0.1:5173/", wait_until="domcontentloaded")
        expect(page.get_by_role("heading", name="Create your recruiting workspace")).to_be_visible()
        page.get_by_label("Organization").fill("Browser Smoke Company")
        page.get_by_label("Email").fill("smoke@example.com")
        page.get_by_label("Password").fill("StrongPassword123!")
        page.get_by_role("button", name="Create workspace").click()
        expect(page.get_by_role("heading", name="Review candidates with clear evidence.")).to_be_visible(timeout=20000)

        page.get_by_role("button", name="Jobs", exact=True).click()
        page.get_by_role("button", name="New job").click()
        page.get_by_label("Job title").fill("Backend Python Engineer")
        page.get_by_label("Description").fill("Build reliable Python and PostgreSQL API services.")
        page.get_by_label("Required skills").fill("Python, PostgreSQL")
        page.get_by_role("button", name="Create job", exact=True).click()
        expect(page.get_by_role("heading", name="Backend Python Engineer")).to_be_visible(timeout=12000)

        page.get_by_role("button", name="Candidates", exact=True).click()
        page.get_by_role("button", name="New candidate").click()
        page.get_by_label("Name", exact=True).fill("Test Candidate")
        page.get_by_label("Email", exact=True).last.fill("candidate@example.com")
        page.get_by_label("Role").select_option(label="Backend Python Engineer")
        page.locator('input[type="file"]').set_input_files(str(pdf))
        page.get_by_role("button", name="Create candidate", exact=True).click()
        expect(page.get_by_text("Test Candidate")).to_be_visible(timeout=15000)

        page.get_by_role("button", name="Sign out").click()
        page.get_by_role("button", name="Already have an account? Sign in").click()
        page.get_by_label("Email").fill("smoke@example.com")
        page.get_by_label("Password").fill("StrongPassword123!")
        page.get_by_role("button", name="Sign in", exact=True).click()
        expect(page.get_by_text("Test Candidate")).to_be_visible(timeout=15000)

        if errors:
            raise AssertionError("Browser JS exceptions:\n" + "\n".join(errors))
        browser.close()
        print("PASS actual Chromium registration, PostgreSQL job, PDF candidate upload, logout/login and persistence")


if __name__ == "__main__":
    main()
