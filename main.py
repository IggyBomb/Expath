from Connection import Connection
import asyncio
from scraping_script import scrape_properties


def main():
    conn = Connection()
    complete_listings = asyncio.run(scrape_properties("test@example.com"))
    print(complete_listings[1].price)
    


if __name__ == '__main__':
    main() 
