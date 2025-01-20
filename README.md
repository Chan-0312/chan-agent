# Chan-Agent

一个简洁高效的 Agent 架构，旨在为开发者提供灵活、易用的工具，支持多种 LLM 模型与任务自动化。

## 特点
- **轻量级**：高效且快速，适合多种应用场景。
- **兼容多种 LLM 模型**：支持主流的 LLM 模型，灵活配置，方便替换。
- **支持 LLM 任务执行**：内置灵活的任务执行功能，可以方便地执行各种 LLM 任务。
- **支持 Agent 执行**：支持 Agent 执行任务，并通过协作提升系统的智能化与自动化水平。

## 安装

通过 `pip` 安装：

```bash
pip install chan-agent
```

## 使用示例

### 初始化LLM
```python
from chan_agent.llms import get_llm

llm = get_llm(
    llm_type='openai', 
    model_name='gpt-4o-mini', 
    base_url='https://api.openai.com/v1', 
    api_key='your-api-key'
)
```

### 创建任务
```python
from chan_agent.task_llm import TaskLLM
from chan_agent.schema import TaskOutputs, TaskInputItem

class TranslationOutput(TaskOutputs):
    translation: str

task = "Translate the following text to French."
rules = ["Keep the original meaning.", "Use formal language."]

task_llm = TaskLLM(llm=llm, task=task, rules=rules, output_model=TranslationOutput)
```

### 执行任务
```python
inputs = [
    TaskInputItem(key="text", key_name="Text to translate", value="Hello, how are you?")
]

result = task_llm.call(inputs=inputs)
print(result)
```

### 使用工具
```python
from chan_agent.base_agent import BaseAgent
from chan_agent.base_tool import BaseTool, ToolResult

class ExampleTool(BaseTool):
    name = "example_tool"
    description = "An example tool that echoes the input."

    def call(self, params, **kwargs):
        return ToolResult(response=params, use_tool_response=True)

tools = [ExampleTool()]
agent = BaseAgent(llm=llm, role="Assistant", tools=tools, rules=["Be polite."])

messages = [
    {"role": "user", "content": "Hello, can you use the example tool?"}
]

response = agent.chat(messages)
print(response)
```

## 说明
- 部分代码参考了[Qwen-Agent](https://github.com/QwenLM/Qwen-Agent)
