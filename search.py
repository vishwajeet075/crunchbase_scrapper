# search.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import random
import time
import logging
from urllib.parse import urlparse, urljoin

logger = logging.getLogger(__name__)

class SearchEngine:
    def __init__(self):
        # Expanded search queries focused on startup listings
        self.search_queries = [
            "site:startupranking.com top startups",
            "site:growjo.com fastest growing companies",
            "site:eu-startups.com/directory",
            "site:startup.info/startups",
            "site:startupindia.gov.in/content/sih/en/search.html",
            "site:angel.co/companies explore",
            "site:ycombinator.com/companies",
            "site:producthunt.com/products launched:year",
            "startup companies list 2024",
            "emerging technology startups"
        ]
        
        # Updated blacklist to focus on news sites while allowing startup directories
        self.blacklisted_domains = {
            'linkedin.com', 'facebook.com', 'twitter.com', 
            'instagram.com', 'youtube.com', 'wikipedia.org', 
            'wsj.com', 'reuters.com', 'bloomberg.com',
            'news.', 'blog.', 'medium.com'
        }

    def get_chrome_driver(self):
        """Initialize Chrome driver with randomized properties."""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # Randomize window size
        window_width = random.randint(1024, 1920)
        window_height = random.randint(768, 1080)
        options.add_argument(f'--window-size={window_width},{window_height}')
        
        # Expanded user agents list
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0'
        ]
        options.add_argument(f'--user-agent={random.choice(user_agents)}')
        
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        return webdriver.Chrome(options=options)

    def find_potential_sites(self):
        """Discover potential startup listing sites through search."""
        driver = self.get_chrome_driver()
        potential_sites = []
        
        try:
            # Take 3 random queries
            for query in random.sample(self.search_queries, 3):
                logger.info(f"Searching with query: {query}")
                
                # Rotate between search engines
                search_engines = [
                    ("https://www.google.com/search?q=", "div.g div.yuRUbf > a"),
                    ("https://duckduckgo.com/?q=", "article.result__body h2 > a")
                ]
                
                search_engine, selector = random.choice(search_engines)
                driver.get(f"{search_engine}{query}")
                
                # Wait for results to load
                time.sleep(random.uniform(2, 4))
                
                # Extract URLs using JavaScript
                urls = driver.execute_script("""
                    return Array.from(document.querySelectorAll('a'))
                        .map(a => a.href)
                        .filter(url => url.startsWith('http') && !url.includes('google') && !url.includes('duckduckgo'));
                """)
                
                # Filter and add valid URLs
                for url in urls:
                    if self.is_valid_source(url):
                        potential_sites.append(url)
                
                time.sleep(random.uniform(3, 5))
                
        except Exception as e:
            logger.error(f"Error in finding sites: {str(e)}")
        finally:
            driver.quit()
            
        # Return unique, filtered sites
        filtered_sites = list(set(potential_sites))
        return filtered_sites[:5]  # Return top 5 unique sites

    def is_valid_source(self, url):
        """Enhanced validation of potential startup listing sources."""
        try:
            domain = urlparse(url).netloc.lower()
            
            # Check against blacklist
            if any(blocked in domain for blocked in self.blacklisted_domains):
                return False
                
            # Avoid search result pages
            if any(term in url.lower() for term in ['search?', 'query=', 'find?']):
                return False
                
            # Prefer startup-related URLs
            preferred_terms = ['startup', 'company', 'companies', 'business', 
                             'directory', 'list', 'ranking', 'tech', 'innovative']
            if any(term in url.lower() for term in preferred_terms):
                return True
                
            return True
            
        except:
            return False