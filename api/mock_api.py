# api/mock_api.py
from api.api import API
import asyncio

class MockAPI(API):
    """
    Mock implementation of the API class for testing without real API calls.
    """

    def __init__(self, api_key=None):
        """
        Initializes the MockAPI object.

        :param api_key: Can be either an actual API key string or a path to a file containing the API key.
        """
        super().__init__(api_key)

    async def generate_text(self, prompt, timeout=10, **kwargs):
        """
        Mocks text generation based on the given prompt.

        :param prompt: The input prompt for the mock API.
        :param timeout: Timeout for the mock response (default is 10 seconds).
        :param kwargs: Additional parameters (ignored in this mock implementation).
        :return: The mocked response (either a review or a book).
        """
        try:
            if "<reviewer_prompt>" in prompt:
                # Simulate reviewer response
                with open("mock/review.txt", "r", encoding="utf-8") as file:
                    return file.read()

            if "<writer_prompt>" in prompt:
                # Simulate writer response
                with open("mock/book.txt", "r", encoding="utf-8") as file:
                    return file.read()

            # Default behavior: echo the prompt
            return f"Mock response for prompt: {prompt}"
        except FileNotFoundError as e:
            return f"Error: {e}. Ensure the necessary mock files (review.txt, book.txt) exist."
        except Exception as e:
            return f"An unexpected error occurred: {e}"

if __name__ == "__main__":
    # Example usage of MockAPI
    api = MockAPI("google_api.key")
    response = asyncio.run(api.generate_text("<reviewer_prompt>Sample review text"))
    print(response)
