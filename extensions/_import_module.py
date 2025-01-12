from langchain_core.tools import tool

@tool
def import_module(module_name: str) -> str:
    """Import a module."""
    success = module_manager.import_module(extensionDirectory, module_name)
    if success:
        return f"Module {module_name} imported successfully."
    else:
        return f"Failed to import module {module_name}."
