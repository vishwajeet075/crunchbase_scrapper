# main.py
import logging
import time
import random
from db1 import EnhancedDatabaseManager
from search import SearchEngine
from scraper import StartupScraper
from enricher import StartupEnricher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        # Initialize components
        db_manager = EnhancedDatabaseManager()
        db_manager.init_db()
        
        search_engine = SearchEngine()
        scraper = StartupScraper(search_engine)
        enricher = StartupEnricher(search_engine)
        
        # First phase: Find and scrape startup names
        sites = search_engine.find_potential_sites()
        logger.info(f"Found {len(sites)} potential sites to scrape")
        
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
        
        logger.info(f"Initial scraping completed. Total companies collected: {total_companies}")
        
        # Second phase: Enrich startup data
        startups_to_enrich = db_manager.get_startups_without_enrichment()
        logger.info(f"Found {len(startups_to_enrich)} startups to enrich")
        
        for startup_id, company_name in startups_to_enrich:
            try:
                # Add random delay between requests
                time.sleep(random.uniform(10, 15))
                
                logger.info(f"Enriching data for: {company_name}")
                enriched_data = enricher.enrich_company_data(company_name)
                
                if enriched_data:
                    db_manager.save_enriched_data(startup_id, enriched_data)
                
            except Exception as e:
                logger.error(f"Error enriching {company_name}: {str(e)}")
                continue
        
        logger.info("Data enrichment completed")
        
    except Exception as e:
        logger.error(f"Process failed: {str(e)}")

if __name__ == "__main__":
    main()