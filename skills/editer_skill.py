import os

from google.genai import types

# Define the file_editor tool
editor_decl = types.FunctionDeclaration(
            name="editor",
            description="Allows you to read, create, overwrite, or append text to files on the local file system. Use this for writing code, generating documents, or analyzing local file contents.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "operation": types.Schema(
                        type=types.Type.STRING,
                        description="The file operation to perform.",
                        enum=["read", "write", "append"]
                    ),
                    "file_path": types.Schema(
                        type=types.Type.STRING,
                        description="The relative or absolute path to the file, e.g., './app.py' or '/Users/name/docs/notes.txt'."
                    ),
                    "content": types.Schema(
                        type=types.Type.STRING,
                        description="The exact string content to write or append. Omit this parameter if the operation is 'read'."
                    )
                },
                # Enforce that the model MUST provide these two parameters
                required=["operation", "file_path"]
            )
)


def editor(operation : str , file_path : str, content : str):
    """Handles reading, writing, and appending to local files."""
    if not operation or not file_path:
        return " Error: Missing operation or file_path for file_editor."


    # Clean up the path just in case
    file_path = os.path.abspath(file_path)

    if operation == "read":
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                file_content = file.read()
                return  file_content
        except FileNotFoundError:
            return  f"Error: Could not find file at {file_path}"
        except Exception as e:
            return  f"Error reading file: {e}"

    elif operation == "write":
        try:
            # Ensure the directory exists before writing
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)
            return  "File successfully written!"
        except Exception as e:
            return  f"Error writing file: {e}"

    elif operation == "append":
        try:
            with open(file_path, "a", encoding="utf-8") as file:
                # Adding a newline to ensure it doesn't merge with the last line
                file.write("\n" + content)
            return  "Content successfully appended!"
        except Exception as e:
            return  f"Error appending to file: {e}"

    else:
        return f"Unknown file operation requested: {operation}"
