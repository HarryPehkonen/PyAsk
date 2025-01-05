#!/usr/bin/env python

import os
import sys
import json
import sqlite3
import importlib.util
from pathlib import Path
from typing import List, Dict, Optional
from langchain_mistralai import ChatMistralAI
from langchain_core.tools import tool

class Ask:
    def __init__(self, ai_code_name: str, model_name: str = "mistral-large-latest", temperature: float = 0.5):
        self.ai_code_name = ai_code_name.lower()
        self.conversation_directory = os.path.join(".", "conversations")
        self.extension_directory = os.path.expanduser("~/extensions")
        self.database_filename = os.path.join(".", "database.db")
        self.conversation_filename = os.path.join(
            self.conversation_directory,
            f"{self.ai_code_name}.json"
        )
        
        # Initialize LLM
        self.llm = ChatMistralAI(
            model=model_name,
            temperature=temperature
        )
        
        # Initialize tools and messages
        self.tools = []
        self.module_manager = ModuleManager()
        self.module_manager.import_all(self)
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.messages = []
        
        # Initialize conversation
        self._initialize_conversation()

    def _initialize_conversation(self):
        """Initialize or load existing conversation"""
        system_prompt = self._get_system_prompt()
        
        if self._have_saved_conversation():
            self.messages = self._load_conversation_from_disk()
        
        if len(self.messages) == 0:
            self.messages.append({"content": system_prompt, "role": "system"})
        elif self.messages[0]["role"] == "system":
            self.messages[0]["content"] = system_prompt
        else:
            self.messages.insert(0, {"content": system_prompt, "role": "system"})
            
        self._save_conversation_to_disk()

    def ask(self, prompt: str) -> str:
        """Process a single prompt and return the response"""
        if not prompt:
            return ""
            
        self.messages.append({"content": prompt, "role": "user"})
        self._save_conversation_to_disk()
        
        while True:
            response = self.llm_with_tools.invoke(self.messages)
            
            if not (hasattr(response, 'additional_kwargs') and 'tool_calls' in response.additional_kwargs):
                break
                
            tool_calls = response.additional_kwargs['tool_calls']
            self._handle_tool_calls(tool_calls)
            
            # always update the system prompt in case it was changed
            if self.messages[0]["role"] == "system":
                self.messages[0]["content"] = self._get_system_prompt()
        
        self.messages.append({"content": response.content, "role": "assistant"})
        self._save_conversation_to_disk()
        
        return response.content

    def _get_system_prompt(self) -> str:
        """Get the current system prompt"""
        with sqlite3.connect(self.database_filename) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT prompt FROM system_prompts WHERE ai_code_name = ?", (self.ai_code_name,))
            prompt = cursor.fetchone()
            prompt = prompt[0] if prompt else "You are a self-modifying AI assistant."
            
            table_descriptions = self._get_table_descriptions()
            column_descriptions = self._get_column_descriptions()
            
            return (
                f"System prompt:\n\n"
                f"{prompt}\n\n"
                f"---\n\n"
                f"Additional information external to the 'system prompt':\n\n"
                f"Your code name is {self.ai_code_name}.\n\n"
                f"Database table descriptions:\n{json.dumps(table_descriptions, indent=2)}\n\n"
                f"Database column descriptions:\n{json.dumps(column_descriptions, indent=2)}"
            )

    def _get_table_descriptions(self) -> List[Dict]:
        """Get database table descriptions"""
        with sqlite3.connect(self.database_filename) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM table_metadata")
            results = cursor.fetchall()
            if not results:
                return []
            column_names = [description[0] for description in cursor.description]
            return [dict(zip(column_names, row)) for row in results]

    def _get_column_descriptions(self) -> List[Dict]:
        """Get database column descriptions"""
        with sqlite3.connect(self.database_filename) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM column_metadata ORDER BY table_name, column_name")
            results = cursor.fetchall()
            if not results:
                return []
            column_names = [description[0] for description in cursor.description]
            return [dict(zip(column_names, row)) for row in results]

    def _have_saved_conversation(self) -> bool:
        """Check if a saved conversation exists"""
        return os.path.exists(self.conversation_filename)

    def _save_conversation_to_disk(self):
        """Save the current conversation to disk"""
        directory = os.path.dirname(self.conversation_filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        with open(self.conversation_filename, "w") as f:
            json.dump(self.messages, f)

    def _load_conversation_from_disk(self) -> List[Dict]:
        """Load conversation from disk"""
        with open(self.conversation_filename, "r") as f:
            return json.load(f)

    def delete_conversation(self):
        """Delete the current conversation"""
        if os.path.exists(self.conversation_filename):
            os.remove(self.conversation_filename)

    def _handle_tool_calls(self, tool_calls: List[Dict]):
        """Handle tool calls and append results to messages"""
        tool_call_requests = []
        tool_call_results = []

        for tool_call in tool_calls:
            tool_name = tool_call['function']['name']
            tool_args = tool_call['function']['arguments']
            tool_call_id = tool_call['id']

            tool_call_requests.append({
                "id": tool_call_id,
                "name": tool_name,
                "type": "function",
                "function": {
                    "name": tool_name,
                    "arguments": tool_args,
                }
            })

            found = False
            for tool in self.tools:
                if tool.name == tool_name:
                    found = True
                    try:
                        args = json.loads(tool_args)
                        function_result = tool.func(**args)
                        tool_call_results.append({
                            "role": "tool",
                            "content": function_result,
                            "name": tool_name,
                            "tool_call_id": tool_call_id
                        })
                    except Exception as e:
                        tool_call_results.append({
                            "role": "tool",
                            "content": f"Error executing tool: {e}",
                            "name": tool_name,
                            "tool_call_id": tool_call_id
                        })
                    break

            if not found:
                tool_call_results.append({
                    "role": "tool",
                    "content": f"Tool {tool_name} not found.",
                    "name": tool_name,
                    "tool_call_id": tool_call_id
                })

        self.messages.append({
            "role": "assistant",
            "content": "",
            "tool_calls": tool_call_requests
        })
        self.messages.extend(tool_call_results)

class ModuleManager:
    """Singleton class to manage imported modules"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModuleManager, cls).__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'modules'):
            self.modules = {}

    def import_all(self, ask_instance):
        """Import all modules from extension directory"""
        want_extension = ".py"
        for filename in os.listdir(ask_instance.extension_directory):
            if filename.endswith(want_extension) and not filename.startswith('_'):
                module_name = filename[:-len(want_extension)]
                module_path = os.path.join(ask_instance.extension_directory, filename)
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    self.modules[module_name] = module
                    tool = getattr(module, module_name)
                    ask_instance.tools.append(tool)
        ask_instance.llm_with_tools = ask_instance.llm.bind_tools(ask_instance.tools)


def get_multiline(txt):
    print(txt, end="")
    lines = []
    while True:
        line = input()
        if line == ".":
            break
        lines.append(line)
    return "\n".join(lines)

def get_single_line(txt):
    return input(txt)

if __name__ == "__main__":

    ai_code_name = None
    input_method = get_single_line
    ai = None

    # go through all arguments one at a time
    for i in range(1, len(sys.argv)):
        arg = sys.argv[i]
        if ai_code_name is None:
            ai_code_name = arg
            ai = Ask(ai_code_name)
            continue

        if arg == "--multiline":
            input_method = get_multiline
            continue

        elif arg == "--new":
            if ai is not None:
                ai.delete_conversation()

        else:
            print(f"Unknown argument: {arg}")
            sys.exit(1)

    while True:
        prompt = input_method("You: ")
        if len(prompt) == 0:
            break
        response = ai.ask(prompt)
        print(f"{ai.ai_code_name}: {response}")
