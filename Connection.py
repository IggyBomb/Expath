import mysql.connector
from mysql.connector import Error
from flask import Flask
import os
from datetime import datetime


#create an instance of flask
app = Flask(__name__)

class Connection:
    def __init__(self):
        self.connection = None
        print(os.environ.get('DB_PASSWORD'))
        print(os.environ.get('Expath_host'))
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
        
    

    def insert_Listing_MySQL(self, listings, user_email):
        """
        insert the data of the listings in the database and create a report with all the new found listings
        Parameters:
        listings (list): list of objects Listings
        user_email (str): the email of the user
        """
        connection = self.connect()
        cursor = connection.cursor()
        current_date = datetime.now()
        added_listings = []
        
        insert_query = """
        INSERT INTO Listings (id, title, link, price, DateOfResearch,  NumberOfBedRooms, PropertyType, SellerName, user_email)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        for listing in listings:
            try:
                cursor.execute(insert_query, (listing.id, listing.title, listing.path, listing.price, current_date, listing.nb_bedrooms, listing.property_type, listing.seller_name, user_email))
                added_listings.append(listing)
                print(f"Inserted listing successfully: \nID: {listing.id}, \n \n")
                
            except Error as e:
                print(f"Error : {e}")
                
        if added_listings: 
            self.create_report(added_listings, user_email) 
        else:
            print("No new listings after the scraping.")
    
        connection.commit()
        cursor.close()
        self.close_connection()
    

    def create_report(added_listings, user_email):
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