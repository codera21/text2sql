import unittest
from unittest.mock import patch, MagicMock
from src.services.gemini_service import GeminiService


class TestGeminiService(unittest.TestCase):
    def setUp(self):
        self.gemini_service = GeminiService()

    @patch("src.services.gemini_service.genai.Client")
    def test_generate_suitable_sql(self, MockClient):
        mock_client_instance = MockClient.return_value
        mock_response = MagicMock()
        mock_response.text = "SELECT * FROM `flights`"
        mock_client_instance.models.generate_content.return_value = mock_response

        user_prompt = "Show all flights"
        result = self.gemini_service.generate_suitable_sql(user_prompt)

        self.assertEqual(result, "SELECT * FROM `flights`")
        mock_client_instance.models.generate_content.assert_called_once()


if __name__ == "__main__":
    unittest.main()
