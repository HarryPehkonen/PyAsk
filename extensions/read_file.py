from langchain_core.tools import tool
import json

@tool
def read_file(file_path: str) -> str:
    """Read the contents of a file."""
    with open(file_path, 'r') as f:
        contents = f.read()
        return json.dumps(contents)
