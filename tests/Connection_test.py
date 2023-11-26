import unittest
import sys
import os
from unittest.mock import patch, MagicMock
from mysql.connector import Error

# Get the absolute path of the parent directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(parent_dir)
from Connection import Connection
from Listing import Listing

connection_instance = Connection()

Listing1 = Listing("5497479","Brighton Square,Rathgar, Dublin 6, Terenure", "€1,100 per month", "x", "x", "x", "x", "x")
Listing2 = Listing("5500037", "Apartment 2, Mobhi Court, Glasnevin, Dublin 9", "€1,469 per month", "x", "x", "x", "x", "x")
Listing3 = Listing("5492666", "9 Portland Street North, Dublin 1, Drumcondra", "€1,200 per month", "x", "x", "x", "x", "x")
Listing4 = Listing("5489933", "31 Wood Dale Drive, Ballycullen", "€1,380 per month", "x", "x", "x", "x", "x")

old_listings = [Listing1.id, Listing2.id, Listing3.id]
new_scraped_listings = {Listing1, Listing2, Listing3, Listing4}


class TestConnection(unittest.TestCase):

    @patch('mysql.connector.connect', autospec=True)
    def test_connect_success(self, mock_connect):
        mock_connect.return_value = MagicMock(name='connection')

        conn = Connection()
        result = conn.connect()

        mock_connect.assert_called_once_with(**conn.config)
        self.assertTrue(result)
        self.assertIsNotNone(conn.connection)
        
        
    @patch('Connection.mysql.connector.connect', autospec=True)
    def test_connect_failure(self, mock_connect):
        mock_connect.side_effect = Error("Test connection failure")

        conn = Connection()
        result = conn.connect()

        # Assert the connect function was called and an error was raised
        mock_connect.assert_called_once_with(**conn.config)
        self.assertIsNone(result)
        self.assertIsNone(conn.connection)

    @patch('Connection.mysql.connector.connect', autospec=True)
    def test_listings_for_database(self, mock_connect):
        mock_connect.return_value = MagicMock(name='connection')
        conn = Connection()
        conn.connect()
        result = conn.filter_new_listings(new_scraped_listings)
        self.assertEqual(result, [Listing4])

if __name__ == '__main__':
    unittest.main()


