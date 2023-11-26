import mysql.connector
from mysql.connector import Error
from flask import Flask
import os
from datetime import datetime
from threading import Lock


#create an instance of flask
app = Flask(__name__)

# Static set and lock for thread safety
id_set = set()
id_set_lock = Lock()

class Connection:
    def __init__(self):
        self.connection = None
        """
        print(os.environ.get('DB_PASSWORD'))
        print(os.environ.get('Expath_host'))
        """
        # Set the configuration to connect to MySQL
        self.config = {
            'user': 'admin',
            'password': os.environ.get('DB_PASSWORD'),
            'host': os.environ.get('Expath_host'),
            'database': 'expath',
            'raise_on_warnings': True
        }
    
    def connect(self):
        is_connected = False
        try:
            self.connection = mysql.connector.connect(**self.config)
            is_connected = True
            print(f"Connection to MySQL: {is_connected}")
        except Error as e:
            print(f"Error: {e}")
        return self.connection


    def close_connection(self):
        try:
            self.connection.close()
            print("connection to MySQL closed")
        except Error as e:
            print(f"Error : {e}")
            

    def insert_user_MySQL(self, user_email, password):
        """Insert a new user in the database
        Parameters:
        user_email(str),
        password(str)
        """
        date_of_subscription = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        connection = self.connect()
        cursor = connection.cursor()
        insert_query = """INSERT INTO User (email, password, date_subscription)
                          VALUES(%s,%s,%s)"""
        try:
            cursor.execute(insert_query, (user_email, password, date_of_subscription))
            connection.commit()
            print(f"User : {user_email} has been inserted into the DB")
        except Error as e:
            connection.rollback()
            print(f"Error : {e}")
        finally:
            cursor.close()
            connection.close()
    
    
    def initialize_listings_IDs_set(self):
        """
        Initialize the listings IDs set by fetching the IDs from the database and storing them in a static set.
        """
        global id_set
        try:
            connection = self.connect()
            cursor = connection.cursor()
            select_query = "SELECT id FROM Listings"
            cursor.execute(select_query)
            ids = cursor.fetchall()
            with id_set_lock:
                id_set = {id_tuple[0] for id_tuple in ids}
            print("Listings IDs set initialized successfully.")
        except Error as e:
            print(f"Error while initializing listings IDs set: {e}")
        finally:
            cursor.close()
            self.close_connection()
        
    

    def insert_new_listings_into_database(self, new_scraped_listings):
        """
        Insert the data of all the new listings into the database.
        Parameters:
        new_scraped_listings (list): List of new Listing objects.
        """
        connection = self.connect()
        cursor = connection.cursor()
        current_date = datetime.now()
    
        insert_query = """
        INSERT INTO Listings (id, title, link, price, DateOfResearch, NumberOfBedRooms, PropertyType, SellerName)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
    
        self.initialize_listings_IDs_set()
        filtered_listings = self.filter_new_listings(new_scraped_listings)

        for listing in filtered_listings:
            try:
                cursor.execute(insert_query, (listing.id, listing.title, listing.path, listing.price, current_date, listing.nb_bedrooms, listing.property_type, listing.seller_name))
                connection.commit()
                print(f"Inserted listing successfully: ID: {listing.id} - Title: {listing.title}")
            except mysql.connector.Error as e:
                if e.errno == 1062:  # Duplicate entry error code
                    print(f"Ignored duplicate entry for ID: {listing.id}")
                else:
                    print(f"Error : {e}")
        cursor.close()
        self.close_connection()
        print("finished")
        
            
            
    
    def remove_non_existing_listings_from_database(self, scraped_listings):
        """remove the listings in the database that are not on the website anymore.
        Parameters: scraped_listings (list): A list of Listing objects.
        """
        connection = self.connect()
        cursor = connection.cursor()
        to_remove_ids = self.filter_non_existing_listings(scraped_listings)
        print(f"Removing {len(to_remove_ids)} listings from the database." )
        
        delete_query = "DELETE FROM Listings WHERE id = %s"
        try:
            for listing_id in to_remove_ids:
                cursor.execute(delete_query, (listing_id,))
                print(f"Listing removed - ID : {listing_id}")
                connection.commit()
        except Error as e:
            print(f"Error while removing listings: {e}")
        
            
            
        
    def filter_new_listings(self, new_scraped_listings):
        """
        Compare the new listings found from scraping with the existing ones in the global ID set and
        return a list of Listing objects that are not in the database.

        Parameters:
        new_scraped_listings (list): A list of Listing objects to be checked against the database.
        """
        new_listings = []
        with id_set_lock:
            for listing in new_scraped_listings:
                if listing.id not in id_set:
                    new_listings.append(listing)
        print(f"Found {len(new_listings)} new listings.")
        return new_listings
    
    
    
    def filter_non_existing_listings(self, scraped_listings):
        """ 
        Compare the listings in the database with the scraped listings and
        return a list of Listing objects that are not in the database.
        Parameter : scraped_listings (list): A list of Listing objects to be checked against the database.
        """
        self.initialize_listings_IDs_set()
        non_existing_listings = []
        new_id_set = set()
        for listing in scraped_listings:
            id = str(listing.id)
            new_id_set.add(id)
        old_id_set = id_set
        print(f"Found {len(old_id_set)} listings in the database.")
        print(f"Found {len(new_id_set)} listings on the website.")

        # Get the IDs that are in old_id_set but not in new_id_set
        non_existing_ids = old_id_set - new_id_set
        print(f"Found {len(non_existing_ids)} non-existing listings.")
        return non_existing_ids


    def create_report(self, added_listings, user_email):
        """Create a new report with the new listings found on the website.
        Parameters:
        added_listings (list): A list of listings objects.
        user_email (str): The email of the user who scraped the listings.
        """
        timestamp = datetime.now().strftime("%d-%m-%Y -- %H_%M")
        filename = f"new_listings_{timestamp}.txt" 
        try:
            with open(filename, 'w', encoding='utf-8') as file:  
                file.write(f"User: {user_email}\n{timestamp}\n\n")
                for listing in added_listings:
                    file.write(f"ID: {listing.id},\nTitle: {listing.title},\nPrice: {listing.price},\nLink: {listing.path},\nBedrooms: {listing.nb_bedrooms},\nType: {listing.property_type},\nSeller: {listing.seller_name}\n\n")
                print(f"Report created: {filename}")
        except Exception as e:
            print(f"Failed to create report: {e}")