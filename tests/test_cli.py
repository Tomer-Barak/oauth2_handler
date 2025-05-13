"""
Test for command-line interface
"""
import unittest
from unittest.mock import patch, MagicMock
import sys
import tempfile
import os

from oauth2handler.cli import main, setup_parser


class TestCLI(unittest.TestCase):
    """Tests for CLI functionality"""
    
    def test_parser_setup(self):
        """Test the argument parser setup"""
        parser = setup_parser()
        args = parser.parse_args(["--list"])
        self.assertTrue(args.list)
        
    @patch("oauth2handler.cli.OAuth2Client")
    @patch("sys.exit")
    def test_list_command(self, mock_exit, mock_oauth2_client):
        """Test the --list command"""
        # Mock clients
        mock_clients = {
            "test1": MagicMock(),
            "test2": MagicMock()
        }
        mock_oauth2_client.from_config_file.return_value = mock_clients
        
        # Call main with list argument
        with patch("sys.argv", ["oauth2", "--list"]):
            main()
            
        # Verify OAuth2Client.from_config_file was called
        mock_oauth2_client.from_config_file.assert_called_once()
        
        # Verify sys.exit was not called with error
        mock_exit.assert_not_called()


if __name__ == "__main__":
    unittest.main()
