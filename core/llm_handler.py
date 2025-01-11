# core/llm_handler.py
import os
import json
from datetime import datetime
import google.generativeai as genai
import re

class LLMHandler:
    def __init__(self, warning_message):
        self.warning_message = warning_message
        self.LOG_FILE = "output_log.json"
        self.MODEL_NAME = "models/gemini-2.0-flash-thinking-exp"
        self.enable_logging = True

    def load_api_key(self, key:str):
        # Define constants
        try:
            with open(key, "r") as f:
                API_KEY = f.read().rstrip()
                genai.configure(api_key=API_KEY)
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
        # Remove bold, italic, and code formatting
        text = re.sub(r'```json', '', text)
        text = re.sub(r'`', '', text)   # Remove code snippets
        # Remove any double spaces
        text = re.sub(r' {2,}', ' ', text)
        return text.strip()

    # Make API call using google.generativeai
    def call_api(self, user_input, role_data, structure_data):
        model = genai.GenerativeModel(self.MODEL_NAME)

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
            response = model.generate_content(prompt)
            
            if not response.candidates or not response.candidates[0].content.parts:
                self.log_output({"error": f"No content parts found in the response: {response}"}, self.LOG_FILE)
                raise ValueError("No content parts found in response")
            
            # Extract the response parts. Part 0 is thought process and part -1 is actual response
            if len(response.candidates[0].content.parts) < 2:
                 self.log_output({"error": f"Expected at least two parts in the response, but got {len(response.candidates[0].content.parts)}: {response}"}, self.LOG_FILE)
                 raise ValueError("Expected at least two parts in the response")

            tought_process_part = response.candidates[0].content.parts[0]
            structured_response_part = response.candidates[0].content.parts[-1]
            
            tought_process = tought_process_part.text if hasattr(tought_process_part, 'text') else str(tought_process_part)
            structured_response_text = structured_response_part.text if hasattr(structured_response_part, 'text') else str(structured_response_part)
            structured_response_text = self.remove_markdown(structured_response_text)

            try:
                response_json = json.loads(structured_response_text)
                return tought_process, response_json
            except json.JSONDecodeError as e:
                self.log_output({"error": f"Could not decode json output from LLM: {structured_response_text}, error: {e}"}, self.LOG_FILE)
                raise ValueError(f"Could not decode JSON: {e}")
                
        except Exception as e:
            self.log_output({"error": str(e)}, self.LOG_FILE)
            raise

    def list_models(self):
        print("List of models that support generateContent:\n")
        for m in genai.list_models():
            if "generateContent" in m.supported_generation_methods:
                print(m.name)

    def get_model_info(self, model:str):
        model_info = genai.get_model(model)
        print(model_info)