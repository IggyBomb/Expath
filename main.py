from Connection import Connection
import asyncio
from scraping_script import scrape_properties


def main():
    conn = Connection()
    complete_listings = asyncio.run(scrape_properties())
    conn.insert_new_listings_into_database(complete_listings)
    


if __name__ == '__main__':
    main() 
