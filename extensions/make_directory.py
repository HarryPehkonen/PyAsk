from langchain_core.tools import tool
import os

@tool
def make_directory(path: str) -> str:
    """Create a new directory."""
    os.makedirs(path)
    return "Directory created successfully."
