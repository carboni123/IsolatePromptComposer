
# <div align="center">Isolate Prompt Composer</div>

# Overview
Isolate Prompt Composer is a specialized application designed to assist users in creating complex and effective prompts for Large Language Models (LLMs). By providing an intuitive interface, users can compile detailed prompts from various text inputs, enhancing interaction with AI models. It does not rely on online interfaces, meaning you have full control and privacy over your prompt engineering on your own machine.

# Documentation
This README.md serves as the primary documentation for the Isolate Prompt Composer application. Here, you will find all necessary information to get started, use, and understand the features of the application.

# Running the Program

## Installation
To get started, follow these steps:
1. Clone the repository or download the source code.
2. Navigate to the project directory in your command line.
3. Install the required dependencies by running:
    ```sh
    pip install -r requirements.txt
    ```

Execute the main script to run the application with:
```sh
python main.py
```
# How to Use
## Creating Prompts
* **Prompt Assembly**: 
Users can type or paste text into designated text boxes. Once satisfied, clicking the "Compile Prompt" button will combine all inputs into a single, coherent prompt, which is then copied to the clipboard for immediate use.  

* **Markdown Integration**: 
Place markdown files in the `/data/{prompt_type}` directory. These files can be quickly accessed within the application to include pre-written content or structures in your prompts.  

* **Project Folder and Filtering**:
Select a project folder using the application interface. The app will look for a .ignore file in this directory to filter out files or directories not relevant to the project.
If no .ignore file exists, users are prompted to create one or load an existing filter file (like .gitignore) through the "Add filter" button. This filter helps manage project scope by excluding unnecessary files, leading to a cleaner workspace.

# Loading API Key
The application supports Google API keys for interaction with LLMs.

### API Key Setup
* **File Format**: 
Create a text file with your Google API key and save it with the extension `.key` (e.g., `google_api.key`).

* **Loading the Key**: 
Within the application, click on the "API Key" text to open a file selector. Navigate to and select your .key file to load the API key.

* **Persistence**: 
Once loaded, the path to your API key file is saved with your project settings. This ensures that the next time you open the project, the API key is automatically recognized without needing re-entry.

# Acknowledgements
Special thanks to Google AI Studio for providing access to the advanced capabilities of the Gemini 2.0 model.
