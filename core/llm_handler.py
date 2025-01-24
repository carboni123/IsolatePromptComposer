# core/llm_handler.py
import json
from datetime import datetime
from api.google_api import GoogleAPI
import re
import asyncio

class LLMHandler:
    def __init__(self, warning_message):
        self.warning_message = warning_message
        self.LOG_FILE = "output_log.json"
        self.MODEL_NAME = "models/gemini-2.0-flash-thinking-exp"
        self.enable_logging = True
        self.api = None

    def load_api_key(self, key:str):
        # Define constants
        try:
            self.api = GoogleAPI(key)
        except FileNotFoundError:
            self.warning_message.message_box("Error", f"API key file '{key}' not found. Please create this file with your API key.")
        except Exception as e:
            self.warning_message.message_box("Error", f"Error reading API key file: {e}")

    # Utility function to output
    def save_output(self, data, out_file):
         if self.enable_logging:
            try:
                with open(out_file, "w") as f:
                    f.write(json.dumps(data, indent=4) + "\n")
            except Exception as e:
                self.warning_message.message_box("Error", f"Error saving output to {out_file}: {e}")

    # Utility function to log output
    def log_output(self, data, log_file):
        if self.enable_logging:
            try:
                with open(log_file, "a") as f:
                    log_entry = {
                        "timestamp": datetime.now().isoformat(),
                        "log_data": data
                    }
                    f.write(json.dumps(log_entry, indent=4) + "\n")
            except Exception as e:
                self.warning_message.message_box("Error", f"Error logging output to {log_file}: {e}")

    def remove_markdown(self, text: str) -> str:
        """Removes markdown syntax from a string."""
        # Regex to extract content within the Json code block
        match = re.search(r"```json\n(.*?)\n```", text, re.DOTALL)
        if match:
            return match.group(
                1
            ).strip()  # Return the XML content, stripped of extra whitespace
        return text

    # Make API call using google.generativeai
    def call_api(self, user_input, role_data, structure_data):
        prompt = f"""
        You are a prompt enhancement agent. Your role is defined as follows:
        {role_data}

        Your structured output must conform to the following JSON schema:
        {structure_data}
        
        User Input: {user_input}
        
        Please enhance the user input based on your role and provide the structured output in JSON format.
        Do not include any markdown or text formatting in the JSON. 
        """
        try:
            response = asyncio.run(self.api.generate_text(prompt))
            structured_response_text = self.remove_markdown(response)
            try:
                response_json = json.loads(structured_response_text)
                return None, response_json
            except json.JSONDecodeError as e:
                self.log_output({"error": f"Could not decode json output from LLM: {structured_response_text}, error: {e}"}, self.LOG_FILE)
                raise ValueError(f"Could not decode JSON: {e}")
        except Exception as e:
            self.log_output({"error": str(e)}, self.LOG_FILE)
            raise
