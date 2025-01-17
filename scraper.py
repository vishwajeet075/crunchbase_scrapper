# scraper.py
import logging
import time
from typing import List, Set
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StartupScraper:
    def __init__(self, search_engine, timeout: int = 30):
        self.search_engine = search_engine
        self.timeout = timeout

        # Table-specific selectors for startup directories
        self.table_selectors = [
            "table tr td:nth-child(2) a",  # StartupRanking.com pattern
            "table.startups-table td.startup-name",
            ".startup-list tr td.name",
            "table[class*='company'] td:nth-child(2)",
            ".ranking-table tr td:nth-child(2)"
        ]

        # List and card selectors
        self.list_selectors = [
            ".startup-card .name",
            ".company-card .title",
            "div[class*='startup-list'] .name",
            "div[class*='company-grid'] .title"
        ]

        # Link patterns that likely contain company names
        self.link_selectors = [
            "a[href*='/startup/']",
            "a[href*='/company/']",
            "a[href*='/profile/']"
        ]

    def scrape_site(self, url: str) -> List[str]:
        """Scrape a website for startup names using multiple methods."""
        companies = set()
        driver = None

        try:
            logger.info(f"Starting scrape of {url}")
            driver = self.search_engine.get_chrome_driver()
            driver.set_page_load_timeout(self.timeout)
            
            # Load the page
            driver.get(url)
            self._wait_for_page_load(driver)
            
            # Get page content
            soup = BeautifulSoup(driver.page_source, 'lxml')
            
            # Try multiple extraction methods
            companies.update(self._extract_from_tables(soup))
            companies.update(self._extract_from_lists(soup))
            companies.update(self._extract_from_links(soup))
            
            # For StartupRanking.com specific pattern
            if 'startupranking.com' in url:
                companies.update(self._extract_startupranking_specific(soup))

            # Clean and validate
            validated_companies = {
                name for name in companies 
                if self._validate_company_name(name)
            }

            logger.info(f"Found {len(validated_companies)} companies from {url}")
            return sorted(list(validated_companies))

        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return []
        finally:
            if driver:
                driver.quit()

    def _wait_for_page_load(self, driver) -> None:
        """Wait for key elements to load."""
        try:
            # Wait for common table or list containers
            selectors = [
                "table", 
                "div[class*='startup']",
                "div[class*='company']",
                ".ranking-table"
            ]
            
            for selector in selectors:
                try:
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    break
                except TimeoutException:
                    continue

        except TimeoutException:
            logger.warning("Timeout waiting for page elements")

    def _extract_startupranking_specific(self, soup) -> Set[str]:
        """Extract specifically from StartupRanking.com format."""
        companies = set()
        
        # Try to find the startup name column
        startup_cells = soup.select("tr td:nth-child(2)")
        for cell in startup_cells:
            # Look for the startup name link
            name_link = cell.find('a')
            if name_link:
                name = name_link.get_text(strip=True)
                if name:
                    companies.add(self._clean_company_name(name))

        return companies

    def _extract_from_tables(self, soup) -> Set[str]:
        """Extract company names from table structures."""
        companies = set()
        
        # Try all table selectors
        for selector in self.table_selectors:
            elements = soup.select(selector)
            for elem in elements:
                name = elem.get_text(strip=True)
                if name:
                    companies.add(self._clean_company_name(name))
        
        return companies

    def _extract_from_lists(self, soup) -> Set[str]:
        """Extract company names from list and card structures."""
        companies = set()
        
        for selector in self.list_selectors:
            elements = soup.select(selector)
            for elem in elements:
                name = elem.get_text(strip=True)
                if name:
                    companies.add(self._clean_company_name(name))
        
        return companies

    def _extract_from_links(self, soup) -> Set[str]:
        """Extract company names from relevant links."""
        companies = set()
        
        for selector in self.link_selectors:
            links = soup.select(selector)
            for link in links:
                # Get text from link or title attribute
                name = link.get_text(strip=True) or link.get('title', '').strip()
                if name:
                    companies.add(self._clean_company_name(name))
        
        return companies

    def _clean_company_name(self, name: str) -> str:
        """Clean and normalize company names."""
        if not name or len(name) < 2:
            return ""
        
        # Remove extra whitespace
        name = ' '.join(name.split())
        
        # Remove common prefixes and suffixes
        prefixes = ['About ', 'The ', 'Company: ', 'Name: ']
        for prefix in prefixes:
            if name.lower().startswith(prefix.lower()):
                name = name[len(prefix):]
        
        return name.strip()

    def _validate_company_name(self, name: str) -> bool:
        """Basic validation of company names."""
        if not name or len(name) < 2 or len(name) > 100:
            return False

        # Skip pure numbers or single letters
        if name.isdigit() or len(name) <= 1:
            return False

        # Skip common navigation text
        invalid_names = {'home', 'about', 'contact', 'privacy', 'terms'}
        if name.lower() in invalid_names:
            return False

        return True