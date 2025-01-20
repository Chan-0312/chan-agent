[中文](README.md) ｜ English 

# Chan-Agent

A simple and efficient Agent framework designed to provide developers with flexible and easy-to-use tools, supporting various LLM models and task automation.

## Features
- **Lightweight**: Efficient and fast, suitable for various application scenarios.
- **Compatible with multiple LLM models**: Supports mainstream LLM models, flexible configuration, and easy replacement.
- **Supports LLM task execution**: Built-in flexible task execution functions, making it easy to perform various LLM tasks.
- **Supports Agent execution**: Supports Agent task execution, enhancing the system's intelligence and automation through collaboration.

## Installation

Install via `pip`:

```bash
pip install chan-agent
```

## Usage Examples

### Initialize LLM
```python
from chan_agent.llms import get_llm

llm = get_llm(
    llm_type='openai', 
    model_name='gpt-4o-mini', 
    base_url='https://api.openai.com/v1', 
    api_key='your-api-key'
)
```

### Create a Task
```python
from chan_agent.task_llm import TaskLLM
from chan_agent.schema import TaskOutputs, TaskInputItem

class TranslationOutput(TaskOutputs):
    translation: str

task = "Translate the following text to French."
rules = ["Keep the original meaning.", "Use formal language."]

task_llm = TaskLLM(llm=llm, task=task, rules=rules, output_model=TranslationOutput)
```

### Execute the Task
```python
inputs = [
    TaskInputItem(key="text", key_name="Text to translate", value="Hello, how are you?")
]

result = task_llm.call(inputs=inputs)
print(result)
```

### Use Tools
```python
from chan_agent.llms import get_llm
from chan_agent.base_agent import BaseAgent
from chan_agent.base_tool import BaseTool, ToolResult
from chan_agent.schema import AgentMessage

llm = get_llm(
    llm_type='openai', 
    model_name='gpt-4o-mini', 
    base_url='https://api.openai.com/v1', 
    api_key='your-api-key'
)


class WeatherTool(BaseTool):
    name = "weather_tool"
    description = "A tool that fetches weather information for a given city."
    parameters = {
        'city': {
            'type': 'string',
            'description': 'city name',
            'required': True
        },
    }

    def call(self, params, **kwargs) -> ToolResult:
        city = params.get("city")
        
        # Return a fixed fake weather response
        return ToolResult(response=f"The weather in {city} is sunny with a high of 25°C.", use_tool_response=False)
        

tools = [WeatherTool()]
agent = BaseAgent(llm=llm, role="Assistant", tools=tools, rules=["Be polite."])

messages = []
messages.append(AgentMessage(role="user", content="Hello, can you tell me the weather in New York?"))

response = agent.chat(messages)
print(response)
```

## Notes
- Some code references [Qwen-Agent](https://github.com/QwenLM/Qwen-Agent)