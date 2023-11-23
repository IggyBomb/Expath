import asyncio
from bs4 import BeautifulSoup
import config
import re
import aiohttp
import aioconsole
import json
from Listing import Listing
from Connection import Connection



 #function to define the parameters of the research
async def scrape_properties(user_email):
    while True:
        rentMax = await aioconsole.ainput("Price max: ")
        rentMin = await aioconsole.ainput("Price min: ")

        if rentMax and rentMin:
            try:
                rentMax = float(rentMax)
                rentMin = float(rentMin)
                if rentMax>=rentMin:
                    page_size = 20
                    start_index = 0
                    complete_listings = []
                    while True:
                        URL = f"https://www.daft.ie/property-for-rent/dublin-city?rentalPrice_from={rentMin}&rentalPrice_to={rentMax}&pageSize={page_size}&from={start_index}"
                        print(URL)
                        listings = await scrape_latest(URL)
                        if not listings:
                            break
                        complete_listings.extend(listings)
                        start_index += page_size
                    break
                else:
                    print("the max Rent has to be bigger than the min Rent")
            except ValueError:
                print("Please enter valid numbers for price max and min.")
    complete_list_elements = len(complete_listings)
    print("Number of objects in the JSON: " +str(complete_list_elements))
    listings_objects = listings_to_objects(complete_listings, user_email)
    print("Number of objects in the list: " + str(len(listings_objects)))
    return listings_objects



# Function for scraping daft.ie
async def scrape_latest(URL): 
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(URL) as response:
                page_content = await response.text()

                # parse the HTML
                soup = BeautifulSoup(page_content, "html.parser")

                # Find the <script> tag with the JSON data
                script_tag = soup.find('script', {'id': '__NEXT_DATA__'})

                if script_tag:
                    # Extract the JSON string
                    json_string = script_tag.string
                    
                    # Save the JSON string to a file for inspection
                    with open('extracted_json.json', 'w', encoding='utf-8') as json_file:
                        json_file.write(json_string)

                    # Parse the JSON string
                    json_data = json.loads(json_string)

                    # Extract data from the JSON object as needed
                    # For example, if the listings are under ['props']['pageProps']['listings']
                    listings_data = json_data['props']['pageProps']['listings']
                    # Extract the required information from each listing
                    extracted_listings = []
                    for listing in listings_data:
                        listing_info = listing['listing']
                        extracted_listing = {
                            'id': listing_info.get('id'),
                            'title': listing_info.get('title'),
                            'seoFriendlyPath': 'https://www.daft.ie'+listing_info.get('seoFriendlyPath'),
                            'publishDate': listing_info.get('publishDate'),
                            'price': listing_info.get('price'),
                            'numBedrooms': listing_info.get('numBedrooms'),
                            'propertyType': listing_info.get('propertyType'),
                            'sellerName': listing_info['seller'].get('name') if 'seller' in listing_info else 'N/A'
                        }
                        extracted_listings.append(extracted_listing)
                    unique_listings = remove_duplicate_data(extracted_listings)
                return unique_listings
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
        return []


#remove all the duplicates from the JSON file
def remove_duplicate_data(listings):
    unique_listings = {}
    for listing in listings:
        listing_id = listing['id']
        unique_listings[listing_id] = listing
    return list(unique_listings.values())



#Transforms every listing of a JSON in an object and stores them in a list
def listings_to_objects(unique_listings, user_email):
    listings_objects = []
    for listing in unique_listings:
        listing_instance = Listing(
            id = listing['id'],
            title = listing['title'],
            price = listing['price'],
            path = listing['seoFriendlyPath'], 
            nb_bedrooms = listing['numBedrooms'], 
            property_type = listing['propertyType'],
            seller_name = listing['sellerName'],
            user_email = user_email
        )
        listings_objects.append(listing_instance)
    return listings_objects
        
async def main():
    listings = await scrape_properties()
    with open('scraped_listings.json', 'w', encoding='utf-8')as file:
        json_string = json.dumps(listings, indent=4)
        file.write(json_string)

if __name__ == "__main__":
    asyncio.run(main())
