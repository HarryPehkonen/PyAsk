from langchain_core.tools import tool

@tool
def import_tool(module_name: str, tool_name: str) -> str:
    """Import a tool from a module."""
    global tools
    global llm_with_tools
    if module_name not in module_manager:
        success = module_manager.import_module(extensionDirectory, module_name)
        if not success:
            return f"Failed to import module {module_name}."

    tool = getattr(module_manager[module_name], tool_name)
    tools.append(tool)
    llm_with_tools = llm.bind_tools(tools)
    return f"Tool {tool_name} activated successfully."
