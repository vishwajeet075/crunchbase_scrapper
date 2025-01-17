# main.py
import logging
import time
import random
from db import DatabaseManager
from search import SearchEngine
from scraper import StartupScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        # Initialize components
        db_manager = DatabaseManager()
        db_manager.init_db()
        
        search_engine = SearchEngine()
        scraper = StartupScraper(search_engine)
        
        # Find potential sites
        sites = search_engine.find_potential_sites()
        logger.info(f"Found {len(sites)} potential sites to scrape")
        
        # Scrape each site
        total_companies = 0
        for url in sites:
            try:
                time.sleep(random.uniform(5, 10))
                companies = scraper.scrape_site(url)
                if companies:
                    db_manager.save_startups(companies, url)
                    total_companies += len(companies)
            except Exception as e:
                logger.error(f"Error processing {url}: {str(e)}")
                continue
                
        logger.info(f"Scraping completed. Total companies collected: {total_companies}")
            
    except Exception as e:
        logger.error(f"Scraper failed: {str(e)}")

if __name__ == "__main__":
    main()
