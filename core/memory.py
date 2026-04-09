import json
import os
from google.genai import types

class Memory:
    def __init__(self, file_path: str = "memory.json"):
        self.file_path = file_path
        self.history = []
        self.load()

    def add(self, role: str, text: str = None, parts: list = None):
        """Add a new simple text or mult-part message format context."""
        if parts:
            content = types.Content(role=role, parts=parts)
        elif text:
            content = types.Content(role=role, parts=[types.Part(text=text)])
        else:
            return
        
        self.history.append(content)
        self.save()

    def append(self, content: types.Content):
        """Append an existent google.genai.types.Content object."""
        self.history.append(content)
        self.save()

    def clear(self):
        """Clear memory cache entirely."""
        self.history = []
        self.save()

    def get_history(self):
        """Return the running array of interactions."""
        return self.history

    def save(self):
        """Safely extract basic fields into JSON schema map mapping for student persistence sake."""
        out = []
        for content in self.history:
            parts_data = []
            for p in getattr(content, "parts", []):
                if getattr(p, "text", None):
                    parts_data.append({"text": p.text})
                elif getattr(p, "function_call", None):
                    parts_data.append({"function_call": {"name": p.function_call.name}})
                elif getattr(p, "function_response", None):
                    parts_data.append({"function_response": {"name": p.function_response.name}})
            
            out.append({
                "role": getattr(content, "role", ""),
                "parts": parts_data,
            })
            
        with open(self.file_path, "w") as f:
            json.dump(out, f, indent=4)

    def load(self):
        """Loads text based context backwards into Google types."""
        if not os.path.exists(self.file_path):
            return
            
        try:
            with open(self.file_path, "r") as f:
                data = json.load(f)
            
            for item in data:
                role = item.get("role")
                parts = []
                for p in item.get("parts", []):
                    if "text" in p:
                        parts.append(types.Part(text=p["text"]))
                    # We skip fully reloading the function call objects from previous sessions 
                    # as old sessions only need context semantics, not tool re-triggering logic.
                
                if parts:
                    self.history.append(types.Content(role=role, parts=parts))
        except Exception as e:
            print(f"Warning: Could not load history from {self.file_path}: {e}")
