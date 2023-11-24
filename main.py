from Connection import Connection
import asyncio
from scraping_script import scrape_properties


def main():
    conn = Connection()
    complete_listings = asyncio.run(scrape_properties("test@example.com"))
    conn.insert_Listing_MySQL(complete_listings, "test@example.com")
    


if __name__ == '__main__':
    main() 
