# search.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import random
import time
import logging
from urllib.parse import urlparse, urljoin

logger = logging.getLogger(__name__)

class SearchEngine:
    def __init__(self):
        self.search_queries = [
            "directory of technology startups",
            "list of software companies",
            "top tech startups list",
            "innovative companies directory",
            "startup companies database"
        ]
        
        self.blacklisted_domains = {
            'linkedin.com', 'facebook.com', 'twitter.com', 
            'instagram.com', 'youtube.com', 'wikipedia.org'
        }

    def get_chrome_driver(self):
        """Initialize Chrome driver with Docker-compatible settings."""
        options = Options()
        options.add_argument('--headless=new')  # Use new headless mode
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        # Required for running in Docker
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--disable-extensions')
        options.add_argument('--single-process')  # Important for Docker
        options.add_argument('--remote-debugging-port=9222')
        
        # Set window size
        options.add_argument('--window-size=1920,1080')
        
        # Set a stable user agent
        options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Create service with increased timeout
        service = Service(log_output=":stderr")
        
        return webdriver.Chrome(options=options, service=service)

    def find_potential_sites(self):
        """Discover potential startup listing sites with improved reliability."""
        potential_sites = []
        
        try:
            # Create a new driver instance
            driver = self.get_chrome_driver()
            
            try:
                # Use a simpler search engine - Bing tends to be more reliable
                base_url = "https://www.bing.com/search?q="
                
                # Try each query
                for query in random.sample(self.search_queries, 2):
                    logger.info(f"Searching with query: {query}")
                    
                    try:
                        # Construct search URL
                        search_url = base_url + query.replace(' ', '+')
                        driver.get(search_url)
                        
                        # Wait for results
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.TAG_NAME, "body"))
                        )
                        
                        # Let the page settle
                        time.sleep(3)
                        
                        # Get all links
                        links = driver.find_elements(By.TAG_NAME, "a")
                        urls = []
                        
                        for link in links:
                            try:
                                url = link.get_attribute('href')
                                if url and url.startswith('http'):
                                    urls.append(url)
                            except:
                                continue
                        
                        # Filter and add valid URLs
                        for url in urls:
                            if self.is_valid_source(url):
                                potential_sites.append(url)
                        
                        # Small delay between searches
                        time.sleep(2)
                        
                    except Exception as e:
                        logger.error(f"Error in search iteration: {str(e)}")
                        continue
                    
            finally:
                # Make sure to quit the driver
                try:
                    driver.quit()
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Error in finding sites: {str(e)}")
        
        # Return unique, filtered sites
        filtered_sites = list(set(potential_sites))
        logger.info(f"Found {len(filtered_sites)} potential sites")
        return filtered_sites[:3]

    def is_valid_source(self, url):
        """Validate potential startup listing sources."""
        try:
            domain = urlparse(url).netloc.lower()
            
            # Check against blacklist
            if any(blocked in domain for blocked in self.blacklisted_domains):
                return False
                
            # Avoid search result pages
            if any(term in url.lower() for term in ['search?', 'query=', 'find?', 'login', 'signin']):
                return False
                
            # Prefer business-related URLs
            preferred_terms = ['company', 'business', 'tech', 'startup']
            if any(term in domain.lower() for term in preferred_terms):
                return True
                
            return False
            
        except:
            return False