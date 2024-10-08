from selenium.webdriver import Remote, ChromeOptions
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

SBR_WEBDRIVER = os.getenv("SBR_WEBDRIVER")
print(f"SBR_WEBDRIVER: {SBR_WEBDRIVER}")  # Debugging line

def scrape_website(website):
    if SBR_WEBDRIVER is None:
        raise ValueError("SBR_WEBDRIVER is not set. Check your .env file.")

    print("Connecting to Scraping Browser...")
    
    # Set up connection to the remote debugging session
    sbr_connection = ChromiumRemoteConnection(SBR_WEBDRIVER, "goog", "chrome")
    options = ChromeOptions()
    options.add_argument("--no-sandbox")  # Recommended for Docker
    options.add_argument("--headless")     # Optional: run in headless mode

    # Connect to the remote debugging session
    with Remote(command_executor=sbr_connection, options=options) as driver:
        driver.get(website)
        
        print("Waiting for captcha to solve...")
        try:
            # This assumes the remote Chrome is set up to handle the captcha
            solve_res = driver.execute(
                "executeCdpCommand",
                {
                    "cmd": "Captcha.waitForSolve",
                    "params": {"detectTimeout": 10000},
                },
            )
            print("Captcha solve status:", solve_res["value"]["status"])
        except Exception as e:
            print(f"Error during captcha solve: {e}")
        
        print("Navigated! Scraping page content...")
        html = driver.page_source
        return html


def extract_body_content(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    body_content = soup.body
    return str(body_content) if body_content else ""


def clean_body_content(body_content):
    soup = BeautifulSoup(body_content, "html.parser")

    # Remove script and style elements
    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()

    # Get text or further process the content
    cleaned_content = soup.get_text(separator="\n")
    cleaned_content = "\n".join(
        line.strip() for line in cleaned_content.splitlines() if line.strip()
    )

    return cleaned_content


def split_dom_content(dom_content, max_length=6000):
    return [
        dom_content[i:i + max_length] for i in range(0, len(dom_content), max_length)
    ]
