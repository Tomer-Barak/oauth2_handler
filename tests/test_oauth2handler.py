"""
Basic unit tests for OAuth2Handler package
"""
import unittest
import os
import json
from unittest.mock import patch, MagicMock
import tempfile

from oauth2handler import OAuth2Client, OAuth2Config
from oauth2handler.exceptions import ConfigurationError, TokenError, AuthorizationError


class TestOAuth2Config(unittest.TestCase):
    """Tests for OAuth2Config class"""
    
    def test_valid_client_credentials_config(self):
        """Test valid client credentials configuration"""
        config = OAuth2Config(
            flow="client_credentials",
            client_id="test_id",
            client_secret="test_secret",
            token_url="https://example.com/token"
        )
        self.assertEqual(config.flow, "client_credentials")
        self.assertEqual(config.client_id, "test_id")
        
    def test_valid_auth_code_config(self):
        """Test valid authorization code configuration"""
        config = OAuth2Config(
            flow="authorization_code",
            client_id="test_id",
            client_secret="test_secret",
            auth_url="https://example.com/auth",
            token_url="https://example.com/token",
            redirect_uri="http://localhost"
        )
        self.assertEqual(config.flow, "authorization_code")
        
    def test_invalid_flow(self):
        """Test invalid flow raises ConfigurationError"""
        with self.assertRaises(ConfigurationError):
            OAuth2Config(
                flow="invalid_flow",
                client_id="test_id",
                client_secret="test_secret",
                token_url="https://example.com/token"
            )
            
    def test_missing_auth_url(self):
        """Test missing auth_url raises ConfigurationError"""
        with self.assertRaises(ConfigurationError):
            OAuth2Config(
                flow="authorization_code",
                client_id="test_id",
                client_secret="test_secret",
                token_url="https://example.com/token",
                redirect_uri="http://localhost"
            )


class TestOAuth2Client(unittest.TestCase):
    """Tests for OAuth2Client class"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        # Patch token directory to use temp directory
        self.token_dir_patcher = patch("oauth2handler.utils.TOKEN_DIR", self.test_dir)
        self.token_dir_patcher.start()
        
    def tearDown(self):
        """Clean up test environment"""
        self.token_dir_patcher.stop()
        
    def test_client_from_dict(self):
        """Test creating client from dictionary"""
        config_dict = {
            "flow": "client_credentials",
            "client_id": "test_id",
            "client_secret": "test_secret",
            "token_url": "https://example.com/token"
        }
        client = OAuth2Client.from_dict("test_service", config_dict)
        self.assertEqual(client.service_name, "test_service")
        self.assertEqual(client.config.flow, "client_credentials")
        
    @patch("requests.post")
    def test_client_credentials_flow(self, mock_post):
        """Test client credentials flow"""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "mock_token",
            "expires_in": 3600
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        # Create client
        config = OAuth2Config(
            flow="client_credentials",
            client_id="test_id",
            client_secret="test_secret",
            token_url="https://example.com/token"
        )
        client = OAuth2Client("test_service", config)
        
        # Get token
        token = client.get_access_token()
        self.assertEqual(token, "mock_token")
        
        # Verify correct parameters were used
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "https://example.com/token")
        self.assertEqual(kwargs["data"]["grant_type"], "client_credentials")
        self.assertEqual(kwargs["data"]["client_id"], "test_id")
        

if __name__ == "__main__":
    unittest.main()
