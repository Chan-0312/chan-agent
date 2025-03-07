import re
import json
from .logger import logger
from textwrap import dedent
from .llms import BaseLLM
from .base_tool import BaseTool
from .schema import *
from .utils.messages_processing import get_messages_conversation
from typing import List, Union, Optional, Iterator, Literal

# TODO 后期可以考虑内存记忆

PROMPT_ROLE_SECTION = dedent("""\
# Role
{role}

""")

PROMPT_SKILLS_SECTION = dedent("""\
# Skills
You can utilize the following tools to assist the user effectively:

{tools}

Tool responses should follow this format: 🛠️ {{"name": $TOOL_NAME, "args": $TOOL_INPUT}} 🔚

""")

PROMPT_RULES_SECTION = dedent("""\
# Rules
- Maintain a polite and professional tone at all times
{rules}

{extra_info}

""")

PROMPT_CONVERSATION_START_SECTION = dedent("""\
# Conversation Start
{conversation}""")



class BaseAgent:

    def __init__(
        self, 
        llm: BaseLLM,
        role: str, 
        tools: List[BaseTool],
        rules: List[str],
        static_extra_info: Optional[str] = "",
        agent_type: Literal["user", "assistant"] = "assistant",
        max_content_chat_length: int = 6,
        max_llm_call_per_run: int = 3,
    ):

        self.role = role
        self.tools_map = {tool.name: tool for tool in tools}
        self.tools_desc = "\n".join([str(tool) for tool in tools])
        self.rules_desc = "\n".join([f"- {rule}" for rule in rules])
        self.static_extra_info = static_extra_info

        # 最大每一轮工具使用的轮数
        self.max_llm_call_per_run = max_llm_call_per_run
        # 最大对话上下文的轮数
        self.max_content_chat_length = max_content_chat_length
        # agent类型
        self.agent_type = agent_type

        self.llm = llm
        self.usage = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        }

    def record_usage(self, usage: dict):
        """
        缓存usage
        """
        if usage:
            self.usage["total_tokens"] += usage.get("total_tokens", 0)
            self.usage["prompt_tokens"] += usage.get("prompt_tokens", 0)
            self.usage["completion_tokens"] += usage.get("completion_tokens", 0)
    
    def clear_usage(self):
        """
        清除usage
        """
        self.usage = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        }

    def get_usage(self):
        """
        获取usage
        """
        return self.usage


    def make_agent_prompt(self, messages:List[AgentMessage], **kwargs) -> str:
        """
        构建agent prompt
        """

        # 仅保留max_content_chat_length长度的上下文
        conversation = get_messages_conversation(messages, max_content_chat_length=self.max_content_chat_length, show_tool_call=True)

        # 加上agent回复的前缀
        conversation += f"[{self.agent_type}]:\n"

        prompt = ""
        prompt += PROMPT_ROLE_SECTION.format(role=self.role)
        prompt += PROMPT_SKILLS_SECTION.format(tools=self.tools_desc) if len(self.tools_map) else ""
        prompt += PROMPT_RULES_SECTION.format(
            rules=self.rules_desc, 
            extra_info=self.static_extra_info + kwargs.get("dynamic_extra_info", "")
        )
        prompt += PROMPT_CONVERSATION_START_SECTION.format(conversation=conversation)

        return prompt
    
    def __detect_tool(self, content:str) -> Union[ToolCall, SystemError, None]:
        """
        检测工具
        """
        pattern = r'🛠️\s*(\{.*?\})\s*🔚'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            # 提取 JSON 字符串
            json_str = match.group(1)
            try:
                json_data = json.loads(json_str)

                if json_data['name'] in self.tools_map:
                    return ToolCall(
                        name=json_data['name'],
                        args=json_data['args']
                    )
                else:
                    available_tools = ", ".join(self.tools_map.keys())
                    error_msg = f"Tool '{json_data['name']}' not found. Available tools: {available_tools}"
                    logger.error(error_msg)
                    return SystemError(error=error_msg)
                    
            except json.JSONDecodeError as e:
                error_msg = 'JSON decode error. Tool responses should follow this format: 🛠️ {{"name": $TOOL_NAME, "args": $TOOL_INPUT}} 🔚'
                logger.error(error_msg)
                return SystemError(error=error_msg)

        return None

    def chat(self, messages:List[AgentMessage], do_tool_call:bool=True, **kwargs) -> List[AgentMessage]:
        """
        对话
        """
        # 清除usage
        self.clear_usage()

        num_llm_calls_available = self.max_llm_call_per_run
        response = []
        while True and num_llm_calls_available > 0:
            system_error = None

            num_llm_calls_available -= 1

            # 生成agent prompt
            prompt = self.make_agent_prompt(messages=messages+response, **kwargs)

            # 发起llm请求
            out_dict = self.llm.text_completions(
                prompt=prompt, 
                instructions=None, 
                temperature=kwargs.get('temperature', 0.3),
                top_p=kwargs.get('top_p', None),
                max_tokens=kwargs.get('max_tokens', None),
                return_usage=True
            )

            # 记录usage
            self.record_usage(out_dict.get('usage', {}))

            # 检测使用的工具
            tool_call = self.__detect_tool(out_dict['content'])

            # 去处工具后面的内容
            content = out_dict['content'].split("🛠️")[0]

            response.append(AgentMessage(
                role=self.agent_type,
                content=content,
                tool_call=None if isinstance(tool_call, SystemError) else tool_call,
            ))
            if isinstance(tool_call, SystemError):
                system_error = tool_call
                

            if do_tool_call and isinstance(tool_call, ToolCall):
                # 执行工具
                logger.info(tool_call)
                tool_result = self.tools_map[tool_call.name].call(params=tool_call.args, **kwargs)
                response.append(AgentMessage(
                    role=tool_call.name,
                    content=tool_result.response,
                    extra=tool_result.extra,
                ))
                if tool_result.use_tool_response:
                    response.append(AgentMessage(
                        role=self.agent_type,
                        content=tool_result.response,
                    ))
            elif system_error:
                response.append(AgentMessage(
                    role="system",
                    content=tool_call.error,
                ))
            else:
                break 
                
        return response


    def chat_with_stream(self, messages:List[AgentMessage], do_tool_call:bool=True, **kwargs) -> Iterator[List[AgentMessage]]:
        """
        流式对话
        """
        # 清除usage
        self.clear_usage()
        num_llm_calls_available = self.max_llm_call_per_run
        response = []
        while True and num_llm_calls_available > 0:
            system_error = None
            
            num_llm_calls_available -= 1

            # 生成agent prompt
            prompt = self.make_agent_prompt(messages=messages+response, **kwargs)

            # 发起llm请求
            llm_out = self.llm.text_completions_with_stream(
                prompt=prompt, 
                instructions=None, 
                temperature=kwargs.get('temperature', 0.3),
                top_p=kwargs.get('top_p', None),
                max_tokens=kwargs.get('max_tokens', None),
                return_usage=True
            )

            agent_output = AgentMessage(role=self.agent_type, content='')
            for out_dict in llm_out:
                # 检测使用的工具
                tool_call = self.__detect_tool(out_dict['content'])
                agent_output.content = out_dict['content'].split("🛠️")[0]
                agent_output.tool_call = None if isinstance(tool_call, SystemError) else tool_call
                self.record_usage(out_dict.get('usage', {}))

                yield response + [agent_output]

                if tool_call is not None:
                    # 已经识别到工具直接截断
                    if isinstance(tool_call, SystemError):
                        system_error = tool_call
                    # break
            
            response += [agent_output]
            
            if do_tool_call and isinstance(agent_output.tool_call, ToolCall):
                # 执行工具
                logger.info(agent_output.tool_call)

                tool_result = self.tools_map[tool_call.name].call(params=tool_call.args, **kwargs)
                response.append(AgentMessage(
                    role=tool_call.name,
                    content=tool_result.response,
                    extra=tool_result.extra,
                ))
                yield response
                if tool_result.use_tool_response:
                    # 使用工具的回复
                    response.append(AgentMessage(
                        role=self.agent_type,
                        content=tool_result.response,
                    ))
                    yield response
                    break
            elif system_error:
                response.append(AgentMessage(
                    role="system",
                    content=system_error.error,
                ))
                yield response
            else:
                break 
                        
        