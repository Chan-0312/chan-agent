from pydantic import BaseModel, Field
from typing import List, Optional, Any
import json

class ToolCall(BaseModel):
    name: str = Field(..., description="tool name")
    args: Any = Field(None, description="tool args")

    def __str__(self):
        return f'🛠️ {self.model_dump_json()} 🔚'
    
    @classmethod
    def from_str(cls, formatted_str: str):
        """
        Initializes a ToolCall object from a formatted string in the format:
        🛠️ {json_data} 🔚. Returns None if parsing fails.
        """
        try:
            # Split the string using delimiters
            parts = formatted_str.split('🛠️ ', 1)
            if len(parts) != 2 or ' 🔚' not in parts[1]:
                return None  # Return None if format doesn't match
            
            json_data = parts[1].rsplit(' 🔚', 1)[0].strip()  # Extract the JSON part
            
            # Attempt to parse JSON
            data = json.loads(json_data)
            return cls(**data)
        except (ValueError, json.JSONDecodeError):
            return None  # Return None if any error occurs
    
class ToolResult(BaseModel):
    response: str = Field(..., description="tool content result")
    use_tool_response: bool = Field(False, description="use tool response")
    extra: Any = Field(None, description="extra info")

class ChatMessage(BaseModel):
    role: str = Field(..., description="role")
    content: str = Field(..., description="content")


class AgentMessage(ChatMessage):
    tool_call: Optional[ToolCall] = Field(None, description="tool calls")
    extra: Optional[Any] = Field(None, description="extra info")

class SystemError(BaseModel):
    error: str = Field(..., description="error message")    

class TaskInputItem(BaseModel):
    key: str = Field(..., description="key")
    key_name: str = Field(..., description="key name")
    value: str = Field(..., description="value")
    format_as_code: bool = Field(False, description="Format value as code block if true")

    def __str__(self) -> str:
        if self.format_as_code:
            return f"- **{self.key_name}**:\n```\n{self.value}```"
        return f"- **{self.key_name}**: {self.value}"
    

class TaskOutputs(BaseModel):

    @classmethod
    def get_scheme(cls) -> str:
        return str(cls.model_json_schema())