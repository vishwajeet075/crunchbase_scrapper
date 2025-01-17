# enricher.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import logging
import time
import random
from typing import Dict, Optional
from urllib.parse import quote

logger = logging.getLogger(__name__)

class StartupEnricher:
    def __init__(self, search_engine):
        self.search_engine = search_engine
        
        # Common patterns for company information
        self.patterns = {
            'employees': [
                'employees',
                'team size',
                'company size',
                'workforce'
            ],
            'funding': [
                'funding',
                'raised',
                'investment',
                'series'
            ],
            'mission': [
                'mission',
                'about us',
                'our mission'
            ],
            'vision': [
                'vision',
                'our vision',
                'what we do'
            ],
            'email': [
                'contact@',
                'info@',
                'hello@',
                'support@'
            ],
            'product': [
                'our product',
                'products',
                'solutions',
                'what we offer'
            ]
        }

    def enrich_company_data(self, company_name: str) -> Dict[str, str]:
        """Search for and extract enriched data for a given company."""
        driver = None
        try:
            driver = self.search_engine.get_chrome_driver()
            
            # Search for company
            search_query = f"{company_name} company about"
            driver.get(f"https://www.google.com/search?q={quote(search_query)}")
            time.sleep(random.uniform(2, 4))
            
            # Get the first relevant result
            company_url = self._get_company_url(driver)
            if not company_url:
                return self._empty_result()
            
            # Visit company website
            driver.get(company_url)
            time.sleep(random.uniform(3, 5))
            
            # Extract information
            soup = BeautifulSoup(driver.page_source, 'lxml')
            
            return {
                'company_url': company_url,
                'employees': self._extract_employees(soup),
                'funding': self._extract_funding(soup),
                'mission': self._extract_mission(soup),
                'vision': self._extract_vision(soup),
                'email': self._extract_email(soup),
                'product': self._extract_product(soup)
            }
            
        except Exception as e:
            logger.error(f"Error enriching data for {company_name}: {str(e)}")
            return self._empty_result()
        finally:
            if driver:
                driver.quit()

    def _get_company_url(self, driver) -> Optional[str]:
        """Extract the first relevant company URL from search results."""
        try:
            # Get all search result links
            links = driver.find_elements(By.CSS_SELECTOR, 'div.g div.yuRUbf > a')
            
            # Filter out unwanted domains
            blacklist = {'linkedin.com', 'facebook.com', 'twitter.com', 'crunchbase.com'}
            
            for link in links:
                url = link.get_attribute('href')
                if not any(domain in url for domain in blacklist):
                    return url
            
            return None
            
        except Exception:
            return None

    def _extract_by_patterns(self, soup: BeautifulSoup, patterns: list) -> str:
        """Extract text based on common patterns."""
        for pattern in patterns:
            # Try different selectors
            selectors = [
                f'[id*="{pattern}"]',
                f'[class*="{pattern}"]',
                f'h1:contains("{pattern}")',
                f'h2:contains("{pattern}")',
                f'h3:contains("{pattern}")',
                f'p:contains("{pattern}")'
            ]
            
            for selector in selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text(strip=True)
                    if text and len(text) > 10:  # Avoid very short snippets
                        return text
        
        return ""

    def _extract_employees(self, soup: BeautifulSoup) -> str:
        """Extract employee count information."""
        return self._extract_by_patterns(soup, self.patterns['employees'])

    def _extract_funding(self, soup: BeautifulSoup) -> str:
        """Extract funding information."""
        return self._extract_by_patterns(soup, self.patterns['funding'])

    def _extract_mission(self, soup: BeautifulSoup) -> str:
        """Extract company mission."""
        return self._extract_by_patterns(soup, self.patterns['mission'])

    def _extract_vision(self, soup: BeautifulSoup) -> str:
        """Extract company vision."""
        return self._extract_by_patterns(soup, self.patterns['vision'])

    def _extract_email(self, soup: BeautifulSoup) -> str:
        """Extract contact email."""
        return self._extract_by_patterns(soup, self.patterns['email'])

    def _extract_product(self, soup: BeautifulSoup) -> str:
        """Extract product information."""
        return self._extract_by_patterns(soup, self.patterns['product'])

    def _empty_result(self) -> Dict[str, str]:
        """Return empty result structure."""
        return {
            'company_url': '',
            'employees': '',
            'funding': '',
            'mission': '',
            'vision': '',
            'email': '',
            'product': ''
        }