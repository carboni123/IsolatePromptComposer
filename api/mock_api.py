# api/mock_api.py
from api.api import API
from api import register_api
import asyncio


@register_api("mock")
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
            response = "The capital of France is **Paris**. Known for its rich history, iconic landmarks such as the Eiffel Tower, and vibrant culture, Paris is one of the most famous cities in the world."
            # Default behavior: echo the prompt
            return f"Mock response for prompt {prompt}: {response}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"


if __name__ == "__main__":
    # Example usage of MockAPI
    api = MockAPI("google_api.key")
    response = asyncio.run(api.generate_text("What is the capital of Paris?"))
    print(response)
