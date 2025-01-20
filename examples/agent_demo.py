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