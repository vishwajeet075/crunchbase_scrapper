# scraper.py
import logging
import time
from typing import List, Set
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException

logger = logging.getLogger(__name__)

class StartupScraper:
    def __init__(self, search_engine):
        self.search_engine = search_engine
        self.timeout = 15  # Reduced timeout

        # Simplified selectors for better reliability
        self.company_selectors = [
            "h1", "h2", "h3",  # Headers often contain company names
            ".company-name", 
            ".startup-name",
            ".organization-name",
            "a[href*='/company/']",
            "a[href*='/startup/']"
        ]

    def scrape_site(self, url: str) -> List[str]:
        """Scrape a website for startup names with improved reliability."""
        companies = set()
        driver = None

        try:
            logger.info(f"Starting scrape of {url}")
            driver = self.search_engine.get_chrome_driver()
            driver.set_page_load_timeout(self.timeout)
            
            # Load the page
            driver.get(url)
            
            # Wait for any dynamic content
            time.sleep(3)
            
            # Scroll down a bit to trigger lazy loading
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
            time.sleep(2)
            
            # Get page content
            soup = BeautifulSoup(driver.page_source, 'lxml')
            
            # Try multiple extraction methods
            for selector in self.company_selectors:
                elements = soup.select(selector)
                for elem in elements:
                    name = self._clean_company_name(elem.get_text())
                    if self._validate_company_name(name):
                        companies.add(name)
            
            # If no companies found, try extracting from all links
            if not companies:
                links = soup.find_all('a')
                for link in links:
                    name = self._clean_company_name(link.get_text())
                    if self._validate_company_name(name):
                        companies.add(name)

            logger.info(f"Found {len(companies)} companies from {url}")
            return sorted(list(companies))

        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return []
        finally:
            if driver:
                driver.quit()

    def _clean_company_name(self, name: str) -> str:
        """Improved company name cleaning."""
        if not name:
            return ""
        
        # Convert to string and clean
        name = str(name).strip()
        
        # Remove common prefixes/suffixes
        prefixes = ['About ', 'The ', 'Company: ', 'Name: ']
        for prefix in prefixes:
            if name.lower().startswith(prefix.lower()):
                name = name[len(prefix):]
        
        # Remove common suffixes
        suffixes = [' Inc', ' LLC', ' Ltd', ' Limited', ' Corp']
        for suffix in suffixes:
            if name.lower().endswith(suffix.lower()):
                name = name[:-len(suffix)]
        
        # Clean extra whitespace
        name = ' '.join(name.split())
        
        return name.strip()

    def _validate_company_name(self, name: str) -> bool:
        """Enhanced validation of company names."""
        if not name or len(name) < 2 or len(name) > 100:
            return False

        # Skip invalid names
        invalid_patterns = [
            'login', 'sign in', 'register', 'about', 'contact',
            'privacy', 'terms', 'cookie', 'menu', 'home'
        ]
        
        if any(pattern in name.lower() for pattern in invalid_patterns):
            return False

        # Must contain at least one letter
        if not any(c.isalpha() for c in name):
            return False

        # Avoid names that are just numbers or single words
        if name.replace(' ', '').isdigit() or len(name.split()) < 2:
            return False

        return True