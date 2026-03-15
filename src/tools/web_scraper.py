pip install selenium

pip install webdriver-manager

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# STEP 1: Configure Chrome Options 
options = Options()
options.add_argument("--headless")               # Run without opening browser window
options.add_argument("--no-sandbox")             # Bypass OS security model (required for some environments)
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")  # Set window size for proper rendering

# STEP 2: Launch the Browser 
print("Launching Chrome browser...")
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

# STEP 3: Open the Target URL 
URL = "https://www.wind-energie.de/english/policy/rea/"
print(f"Navigating to: {URL}")
driver.get(URL)

# STEP 4: Wait Until Page is Fully Loaded 
# We wait until the <h1> tag (paper title) is visible on screen
wait = WebDriverWait(driver, 15)
wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
print("Page loaded successfully!\n")

# STEP 5: Extract the Paper Title 
title = driver.find_element(By.TAG_NAME, "h1").text.strip()
print(f"ðTITLE: {title}")
print("=" * 70)

# STEP 6: Extract All Section Headings (h2 tags) 
# The article has sections like Abstract, Introduction, etc.
headings = driver.find_elements(By.TAG_NAME, "h2")

# STEP 7: Extract All Paragraph Text (p tags) 
# All body content is wrapped in <p> tags inside the article
paragraphs = driver.find_elements(By.TAG_NAME, "p")

# STEP 8: Collect Section Headings 
print("\nSECTIONS FOUND:")
section_titles = []
for heading in headings:
    text = heading.text.strip()
    if text:  # Skip empty headings
        section_titles.append(text)
        print(f"-{text}")

# 9: Collect All Paragraph Content 
print("\nEXTRACTING FULL CONTENT...\n")
full_content = []
for para in paragraphs:
    text = para.text.strip()
    if text and len(text) > 30:  # Skip tiny/empty paragraphs
        full_content.append(text)

# STEP 10: Display Extracted Content in Terminal 
print(f"\n{'=' * 70}")
print(f"  PAPER: {title}")
print(f"{'=' * 70}\n")

for para in full_content:
    print(para)
    print()  # Blank line between paragraphs

# STEP 11: Save Everything to output.txt 
print("\nSaving content to output.txt...")

with open("output.txt", "w", encoding="utf-8") as f:
    f.write(f"TITLE: {title}\n")
    f.write("=" * 70 + "\n\n")

    f.write("SECTIONS:\n")
    for s in section_titles:
        f.write(f" -{s}\n")
    f.write("\n" + "=" * 70 + "\n\n")

    f.write("FULL CONTENT:\n\n")
    for para in full_content:
        f.write(para + "\n\n")

print("Content successfully saved to output.txt!")

# STEP 12: Always Close the Browser 
driver.quit()
print("Browser closed. Scraping complete!")
