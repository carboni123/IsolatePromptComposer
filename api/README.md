# API Keys Folder

This folder is used to securely store API key files for integration with various LLM services. Each file contains the API key for a specific service and is loaded directly into the application during runtime. 

## Folder Structure

- `google_api.key`: Stores the API key for Google GenAI.

## Usage

1. **Adding Keys**:  
   Place your API keys in separate `.key` files with descriptive filenames. Ensure the file contains only the API key as plain text.

2. **Loading Keys**:  
   The application reads these files directly at runtime to authenticate requests. Ensure that the folder path and file names match the app's configuration.

## Security

- **Do Not Commit Keys**:  
  Ensure that API key files are excluded from version control by using the `.key` extension or adding the new files to the `.gitignore` file.
