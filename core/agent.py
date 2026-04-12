import os
import sys
from pathlib import Path
import importlib
import importlib.util
import inspect
import builtins

from typing import List, Dict, Tuple, Any

from google import genai
from google.genai import types

import skills

from .speech_to_text import listen_and_transcribe
from .memory import Memory

class Agent:

    def __init__(self, api_key : str  , skill_dir : str, memory : str , model_name : str) -> None:
        self.__system_prompt : str = ""

        self.model_name: str = model_name
        self.skill_dir: str = skill_dir
        self.tools: List[types.FunctionDeclaration] = list() # function name
        self.available_tools: Dict[str, Callable] = dict()
        self.memory = Memory(memory if memory else "memory.json")
        self.llm_api_key: str = api_key

        self.llm = genai.Client(api_key=self.llm_api_key)
        self.config : types.GenerateContentConfig
        self.load_config()


    def load_system_prompt(self, prompt) -> None:
        self.__system_prompt = prompt


    def load_tools(self):
        skillFiles = Path(self.skill_dir).rglob("*.py")
        for file_path in skillFiles:
            if file_path.is_dir() or file_path.name.startswith("__"):
                continue
            
            spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                try:
                    spec.loader.exec_module(mod)
                except Exception as e:
                    print(f"Error loading tool module {file_path}: {e}")
                    continue
                
                for name, obj in inspect.getmembers(mod):
                    if isinstance(obj, types.FunctionDeclaration):
                        print(name)
                        if obj.name in self.available_tools.keys():
                            continue
                        
                        func = getattr(mod, obj.name, None)
                        if func and callable(func):
                            self.tools.append(obj)
                            self.available_tools[obj.name] = func
    def load_config(self) -> None:
        self.load_tools()
        allTools = types.Tool(
            google_search=types.GoogleSearch(),
            function_declarations=self.tools,
        )
        self.config = types.GenerateContentConfig(
            tools=[allTools],
            system_instruction=self.__system_prompt,
        )


    def run(self, max_iters:int =10, stop_command : str = "exit",wake_word : str = "Hey, Jarvis", input_mode : str = "chat"):
        print("Agent ready. Type 'exit' to quit.")
        self.memory.add(role="user",text=wake_word)

        input_mode_func = builtins.input if input_mode == "chat" else listen_and_transcribe
        while True:
            try:
                prompt = input_mode_func()
            except EOFError:
                break
            
            if prompt.lower() == stop_command:
                break
            if not prompt: continue
            
            # 1. Add user prompt to memory
            self.memory.add(role="user", text=prompt)
            
            # 2. Agentic loop with tool calls
            for iters in range(1, max_iters + 1):
                # Call LLM with the whole conversation history
                try :
                    response = self.llm.models.generate_content(
                            model=self.model_name,
                            contents=self.memory.get_history(),
                            config=self.config
                    )
                except Exception as e:
                    print(f"API Error encountered: {e}")
                    import time
                    time.sleep(5)
                    print("Retrying...")
                    continue
                
                # Append model response representation into memory
                if getattr(response, "candidates", None) and response.candidates:
                    model_content = response.candidates[0].content
                    self.memory.append(model_content)
                else:
                    break
                
                # Check for function calls
                if response.function_calls:
                    for func in response.function_calls:
                        args_dict = func.args if isinstance(func.args, dict) else (dict(func.args) if func.args else {})
                        print(f"\\n[Agent Executing Tool: {func.name} with args {args_dict}]")
                        tool_content_response = self.action(func.name, args_dict)
                        self.memory.append(tool_content_response)
                        
                    # Continue loop to send tool response back to LLM context
                    continue 
                else:
                    # Final text response
                    print(f"\\nAgent: {response.text}")
                    self.memory.append(types.Content(role="model", parts=[types.Part(text=response.text)]))
                    break

    def action(self, tool_name : str, tool_args : Dict[str , Any]):
        determinedTools = self.available_tools.get(tool_name)
        responseResult : Dict[str, str]
        
        if determinedTools:
            try:
                result = determinedTools(**(tool_args or {}))
                
                if result:
                    responseResult = {"result": str(result)}
                else:
                    responseResult = {"result": "Success but no output."}
            except Exception as e:
                responseResult = {"error": f"Error executing {tool_name}: {str(e)}"}
        else:
            responseResult = {"error": f"Tool {tool_name} is not available."}

        # Google API structured part for response
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=tool_name,
                    response=responseResult
                )
            ]
        )


