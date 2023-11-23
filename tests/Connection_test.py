import unittest
import sys
import os
from unittest.mock import patch, MagicMock
from mysql.connector import Error

# Get the absolute path of the parent directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(parent_dir)
from Connection import Connection

connection_instance = Connection()


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


if __name__ == '__main__':
    unittest.main()


