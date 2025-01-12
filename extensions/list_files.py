from langchain_core.tools import tool
from typing import List, Dict
from pathlib import Path
import json

@tool
def list_files() -> List[Dict[str, str]]:
    """List all files and directories in the current working directory."""
    exclude_dirs = {
        '.git',
        'venv',
        '__pycache__',
    }
    exclude_files = set()

    path = Path.cwd()

    result = []
    def recurse(current_path):
        for item in current_path.iterdir():
            if item.is_dir():
                if item.name not in exclude_dirs:
                    result.append({'Directory': str(item)})
                    recurse(item)
            elif item.is_file():
                if item.name not in exclude_files:
                    result.append({'File': str(item)})

    recurse(path)
    return json.dumps(result)
