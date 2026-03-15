# src/tools/batch_scraper.py 
import os
import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse

class BatchScraper:
    def __init__(self, output_dir="scraped_data"):
        """Initialize the batch scraper"""
        self.output_dir = output_dir
        self.setup_directories()
        self.stats = {
            "total_urls": 0,
            "successful": 0,
            "failed": 0,
            "start_time": None,
            "end_time": None
        }
        
    def setup_directories(self):
        """Create necessary directories"""
        # Create main output directory (this will be src/data/policies or src/data/effects)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create subdirectories for reports and logs (but NOT for policies)
        os.makedirs(os.path.join(self.output_dir, "reports"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "logs"), exist_ok=True)
        
        print(f"Output directories created in: {self.output_dir}")
        print(f"  • Text files will be saved directly to: {self.output_dir}")
        print(f"  • Reports will be saved to: {self.output_dir}/reports/")
        print(f"  • Logs will be saved to: {self.output_dir}/logs/")
    
    def get_driver(self):
        """Create and return a Chrome driver instance"""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        
        # Add user agent to avoid being blocked
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        return driver
    
    def extract_content(self, driver, url):
        """Extract content from a webpage"""
        content = {
            "url": url,
            "title": "",
            "headings": [],
            "paragraphs": [],
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Wait for page to load
            wait = WebDriverWait(driver, 15)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
            
            # Extract title
            try:
                content["title"] = driver.find_element(By.TAG_NAME, "h1").text.strip()
            except:
                content["title"] = "No title found"
            
            # Extract all headings (h1, h2, h3)
            for tag in ["h1", "h2", "h3"]:
                elements = driver.find_elements(By.TAG_NAME, tag)
                for elem in elements:
                    text = elem.text.strip()
                    if text:
                        content["headings"].append({
                            "level": tag,
                            "text": text
                        })
            
            # Extract paragraphs
            paragraphs = driver.find_elements(By.TAG_NAME, "p")
            for p in paragraphs:
                text = p.text.strip()
                if text and len(text) > 30:  # Filter out short/empty paragraphs
                    content["paragraphs"].append(text)
            
            return content
            
        except Exception as e:
            print(f"   Error extracting content: {str(e)}")
            return None
    
    def save_content(self, content, filename=None):
        """Save scraped content to file - saves directly to output_dir, not in subfolder"""
        if not filename:
            # Generate filename from title or URL
            if content["title"] and content["title"] != "No title found":
                filename = content["title"].replace(" ", "_").replace("/", "_")[:50]
            else:
                # Use domain and timestamp
                parsed_url = urlparse(content["url"])
                domain = parsed_url.netloc.replace("www.", "")
                filename = f"{domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Clean filename
        filename = "".join(c for c in filename if c.isalnum() or c in "._-").rstrip()
        
        # Save as text file DIRECTLY in output_dir (NOT in policies subfolder)
        txt_path = os.path.join(self.output_dir, f"{filename}.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(f"TITLE: {content['title']}\n")
            f.write(f"SOURCE: {content['url']}\n")
            f.write(f"SCRAPED: {content['timestamp']}\n")
            f.write("=" * 70 + "\n\n")
            
            f.write("HEADINGS:\n")
            for h in content["headings"]:
                f.write(f"{h['level'].upper()}: {h['text']}\n")
            
            f.write("\n" + "=" * 70 + "\n\n")
            f.write("CONTENT:\n\n")
            
            for i, p in enumerate(content["paragraphs"], 1):
                f.write(f"[Paragraph {i}]\n{p}\n\n")
        
        # Save as JSON for structured data in reports directory
        json_path = os.path.join(self.output_dir, "reports", f"{filename}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
        
        return txt_path, json_path
    
    def scrape_urls(self, urls, delay=3):
        """Scrape multiple URLs with delay between requests"""
        self.stats["start_time"] = datetime.now()
        self.stats["total_urls"] = len(urls)
        
        print("\n" + "=" * 70)
        print(f"Starting batch scrape of {len(urls)} URLs")
        print("=" * 70)
        
        driver = self.get_driver()
        
        try:
            for i, url in enumerate(urls, 1):
                print(f"\n[{i}/{len(urls)}] Processing: {url}")
                
                try:
                    # Load page
                    driver.get(url)
                    print(f"   Page loaded")
                    
                    # Extract content
                    content = self.extract_content(driver, url)
                    
                    if content and content["paragraphs"]:
                        # Save content
                        txt_path, json_path = self.save_content(content)
                        print(f"   Saved: {os.path.basename(txt_path)}")
                        print(f"     - {len(content['paragraphs'])} paragraphs")
                        print(f"     - {len(content['headings'])} headings")
                        self.stats["successful"] += 1
                    else:
                        print(f"   No content extracted")
                        self.stats["failed"] += 1
                        
                        # Log failed URL
                        with open(os.path.join(self.output_dir, "logs", "failed_urls.txt"), "a") as f:
                            f.write(f"{url}\n")
                    
                except Exception as e:
                    print(f"   Error: {str(e)}")
                    self.stats["failed"] += 1
                    
                    # Log error
                    with open(os.path.join(self.output_dir, "logs", "errors.txt"), "a") as f:
                        f.write(f"{url}: {str(e)}\n")
                
                # Delay between requests to be respectful
                if i < len(urls):
                    print(f"   Waiting {delay} seconds before next request...")
                    time.sleep(delay)
        
        finally:
            driver.quit()
        
        self.stats["end_time"] = datetime.now()
        self.print_stats()
        
        # Generate summary report
        self.generate_report()
    
    def scrape_to_target(self, urls, target_dir, delay=3):
        """Scrape URLs and save directly to target directory
        Files will be saved directly in target_dir, not in a subfolder
        """
        print(f"\n{'='*70}")
        print(f"SCRAPING TO TARGET DIRECTORY: {target_dir}")
        print(f"{'='*70}")
        
        # Set output directory to target
        self.output_dir = target_dir
        self.setup_directories()
        
        # Run the scrape
        self.scrape_urls(urls, delay)
        
        print(f"\nFiles saved directly to: {target_dir}/")
    
    def print_stats(self):
        """Print scraping statistics"""
        duration = self.stats["end_time"] - self.stats["start_time"]
        
        print("\n" + "=" * 70)
        print("SCRAPING COMPLETE - STATISTICS")
        print("=" * 70)
        print(f"Total URLs:     {self.stats['total_urls']}")
        print(f"Successful:     {self.stats['successful']}")
        print(f"Failed:         {self.stats['failed']}")
        print(f"Success rate:   {(self.stats['successful']/self.stats['total_urls']*100):.1f}%")
        print(f"Time taken:     {duration.total_seconds():.1f} seconds")
        print("=" * 70)
    
    def generate_report(self):
        """Generate a summary report"""
        report_path = os.path.join(self.output_dir, "logs", f"scrape_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("BATCH SCRAPING REPORT\n")
            f.write("=" * 50 + "\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total URLs: {self.stats['total_urls']}\n")
            f.write(f"Successful: {self.stats['successful']}\n")
            f.write(f"Failed: {self.stats['failed']}\n")
            f.write(f"Duration: {(self.stats['end_time'] - self.stats['start_time']).total_seconds():.1f} seconds\n")
        
        print(f"\nReport saved to: {report_path}")