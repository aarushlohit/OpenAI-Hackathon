import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add backend to path so we can import providers
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))
from providers import elevenlabs_client

class ElevenLabsClientTests(unittest.TestCase):
    @patch('requests.post')
    def test_transcribe_audio_success(self, mock_post) -> None:
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"text": "Hello world, this is a transcribed conversation."}
        mock_post.return_value = mock_response

        # Patch key directly since it's loaded at module import time
        with patch('providers.elevenlabs_client.ELEVENLABS_API_KEY', 'test-key-123'):
            result = elevenlabs_client.transcribe_audio(b"audio-data", "test.mp3", "audio/mpeg")
            self.assertEqual(result, "Hello world, this is a transcribed conversation.")
            
            # Verify the mock post calls
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            self.assertEqual(args[0], "https://api.elevenlabs.io/v1/speech-to-text")
            self.assertEqual(kwargs['headers']['xi-api-key'], "test-key-123")
            self.assertIn('file', kwargs['files'])
            self.assertEqual(kwargs['data']['model_id'], "scribe_v2")

    @patch('requests.post')
    def test_transcribe_audio_failure(self, mock_post) -> None:
        # Mock error API response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "API Key Invalid"
        mock_response.json.side_effect = ValueError("Not JSON")
        
        # When raise_for_status() is called, raise an HTTPError
        import requests
        mock_response.raise_for_status.side_effect = requests.HTTPError("Bad Request")
        mock_post.return_value = mock_response

        with patch('providers.elevenlabs_client.ELEVENLABS_API_KEY', 'test-key-123'):
            with self.assertRaises(RuntimeError) as context:
                elevenlabs_client.transcribe_audio(b"audio-data", "test.mp3", "audio/mpeg")
            self.assertIn("ElevenLabs STT failed: HTTP Error 400: API Key Invalid", str(context.exception))

    def test_model_name(self) -> None:
        self.assertEqual(elevenlabs_client.model_name(), "scribe_v2")

if __name__ == "__main__":
    unittest.main()
