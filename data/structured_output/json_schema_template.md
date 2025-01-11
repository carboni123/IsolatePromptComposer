**Instructions:**
1. The LLM must adhere strictly to the schema provided.
2. Each 'action' must include one of the following values:
   - 'create_file' for creating new files.
   - 'edit_file' for modifying existing files.
   - 'delete_file' for removing files.
3. The 'file_path' must specify the relative path to the file within the project structure.
4. The 'file_contents' must be a string containing the full content of the file (for creation or edits).
5. The 'metadata' object must include:
   - 'commit_message': A concise description of the action.
   - 'author': The name of the person or entity making the changes.

**Schema:**
```json
{
    "actions": [
        {
            "action": "string", // One of: "create_file", "edit_file", "delete_file"
            "file_path": "string", // Path of the file to act upon
            "file_contents": "string", // Contents of the file for creation or edits
            "metadata": {
                "commit_message": "string", // Version control message
                "author": "string"          // Name of the author making changes
            }
        }
    ]
}