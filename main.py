from Connection import Connection
import asyncio
from scraping_script import scrape_properties


def main():
    conn = Connection()
    complete_listings = asyncio.run(scrape_properties(1500, 1000))
    conn.remove_non_existing_listings_from_database(complete_listings)
    


if __name__ == '__main__':
    main() 
