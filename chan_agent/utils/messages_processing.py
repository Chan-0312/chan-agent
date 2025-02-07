from chan_agent.schema import AgentMessage, ChatMessage, ToolCall
from typing import List, Union
from pydantic import BaseModel

def convert_to_serializable(obj):
    """
    递归地将对象转换为 JSON 可序列化的格式。
    如果对象是 BaseModel 或其他不支持序列化的类型，则将其转换为字典。
    """
    if isinstance(obj, BaseModel):
        return obj.dict()  # 如果是 Pydantic BaseModel，转换为字典
    elif isinstance(obj, list):
        return [convert_to_serializable(item) for item in obj]  # 递归处理列表
    elif isinstance(obj, dict):
        return {key: convert_to_serializable(value) for key, value in obj.items()}  # 递归处理字典
    else:
        return obj  # 直接返回原始值

def messages_dict_to_chat_messages(
        messages: List[dict]
    ) -> List[Union[AgentMessage, ChatMessage]]:

    return [
        AgentMessage(
            role=message['role'],
            content=str(message['content']),
            tool_call=(
                ToolCall.from_str(message['tool_call'])
                if isinstance(message.get('tool_call'), str) else None
            ),            
            extra=message.get('extra', None)
        ) if 'tool_call' in message or 'extra' in message else ChatMessage(
            role=message['role'],
            content=str(message['content'])
        )
        for message in messages
    ]

def chat_messages_to_messages_dict(
        messages: List[Union[AgentMessage, ChatMessage]],
        tool_call_in_content: bool = False,
    ) -> List[dict]:
    return [
        {
            'role': message.role,
            'content': message.content + (f"🛠️{message.tool_call.name}🔚" if tool_call_in_content and isinstance(message, AgentMessage) and message.tool_call else ''),
            **({'tool_call': str(message.tool_call)} if isinstance(message, AgentMessage) and message.tool_call else {}),
            **({
                'extra': convert_to_serializable(message.extra)
            } if isinstance(message, AgentMessage) and message.extra else {}),
        }
        for message in messages
    ]


def get_messages_conversation(
        messages: List[Union[AgentMessage, ChatMessage]], 
        max_content_chat_length:int = 6,
        show_tool_call:bool = True
    ) -> str:
    """
    Get the conversation of the messages.
    """

    num_content_chat_available = max_content_chat_length
    conversation = ""
    for m in messages[::-1]:
        # 倒序获取
        if isinstance(m, AgentMessage):
            conversation = f"[{m.role}]:\n{m.content} {m.tool_call if m.tool_call and show_tool_call else ''}\n\n" + conversation
        else:
            conversation = f"[{m.role}]:\n{m.content}\n\n" + conversation
        if m.role == 'user':
            num_content_chat_available -= 1
            if num_content_chat_available <= 0:
                break

    return conversation
    
