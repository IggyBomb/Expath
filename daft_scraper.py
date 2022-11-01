from bs4 import BeautifulSoup
from playsound import playsound
import re
import requests
import pickle
import threading




def play_sound():  
    playsound("./nuclear_launch.mp3", block = False)
    
play_sound()
#play = threading.Thread(target=playsound, args=('/home/kang/daft_scraper/nuclear_launch.mp3'))
#play.start()



def scrape_latest():
    URL = "https://www.daft.ie/property-for-rent/dublin-city?sort=publishDateDesc&rentalPrice_to=1500"
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find_all(class_="SearchPage__Result-gg133s-2")

    for listing in results:
        listing_ele = {
            "address" : listing.find(attrs={"data-testid" : "address"}).text.strip(),
            "price" : listing.find(attrs={"data-testid" : "price"}).text.strip(),
            "property_type" : listing.find(attrs={"data-testid" : "property-type"}).text.strip(),
            "link" : "https://www.daft.ie" + listing.find('a', {'href': re.compile(r'\/for-rent\/')}).get("href")
        }

        print(listing_ele["address"])
        print(listing_ele["price"])
        print(listing_ele["property_type"])
        print(listing_ele["link"])
        print()

scrape_latest()

def save_pickle(data):
    file = open("pickle", "wb")
    pickle.dump(data, file)
    file.close()

def load_pickle():
    file = open("pickle", "wb")
    data = pickle.load(file)
    file.close()
    return data