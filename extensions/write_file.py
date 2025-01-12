from langchain_core.tools import tool

@tool
def write_file(file_path: str, content: str) -> str:
    """Write content to a file."""
    print(f"Writing content to file: {file_path}")
    print(f"Content: {content}")

    with open(file_path, 'w') as f:
        f.write(content)

    return "File written successfully."


