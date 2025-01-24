# api/google_api.py
import os
import re
from api.api import API
import google.generativeai as genai


class GoogleAPI(API):
    """
    Concrete class for interactions with the Google API.
    """

    MODEL_NAME = "models/gemini-2.0-flash-thinking-exp"

    def __init__(self, api_key=None):
        """
        Initializes the GoogleAPI object.

        :param api_key: Can be either an actual API key string or a path to a file containing the API key.
        """
        super().__init__(api_key, api_env="GOOGLEAI_API_KEY")
        self.client = None
        if not self.api_key:
            raise ValueError(
                "No valid GoogleAI API key found. Provide it as a string, file path, "
                "or set GOOGLEAI_API_KEY in the environment."
            )
        genai.configure(api_key=self.api_key)

    async def generate_text(self, prompt, timeout=10, **kwargs):
        """
        Generates text using the Google API.

        Args:
            prompt (str): The input prompt for text generation.
            timeout (int): Timeout in seconds for the API call.
            **kwargs: Additional keyword arguments for the API call.

        Returns:
            str: The generated text.

        Raises:
             NotImplementedError: This method is not yet implemented for Google API.
        """
        model = genai.GenerativeModel(self.MODEL_NAME)
        try:
            response = model.generate_content(prompt)
            return extract_xml_from_markdown(response.text)
        except Exception as e:
            self.log_output({"error": str(e)}, self.LOG_FILE)
            print(f"Error generating text with Google API: {e}")
            raise

    def list_models(self):
        print("List of models that support generateContent:\n")
        for m in genai.list_models():
            if "generateContent" in m.supported_generation_methods:
                print(m.name)

    def get_model_info(self, model: str):
        model_info = genai.get_model(model)
        print(model_info)


def extract_xml_from_markdown(markdown_response: str) -> str:
    """
    Extract XML content from a Markdown response.

    Parameters:
        markdown_response (str): The Markdown response containing XML in a code block.
    Returns:
        str: Extracted XML content or the input if no XML is found.
    """
    # Regex to extract content within the XML code block
    match = re.search(r"```xml\n(.*?)\n```", markdown_response, re.DOTALL)
    if match:
        return match.group(
            1
        ).strip()  # Return the XML content, stripped of extra whitespace
    return markdown_response  # Return input if no XML is found


if __name__ == "__main__":
    api = GoogleAPI()
    api.list_models()
