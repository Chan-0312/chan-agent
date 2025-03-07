import time
import datetime
from .db_tracker import llm_log as db_llm_log
from .json_tracker import llm_log as json_llm_log
from chan_agent.config import DEFAULT_LLM_TRACKER

logger_map = {
    "db_tracker": db_llm_log,
    "json_tracker": json_llm_log,
}

def wrap_create(create_fn):
    """
    修饰器：支持openai的接口格式
    """
    logger_fn = logger_map.get(DEFAULT_LLM_TRACKER, None)

    def create(*args, **kwargs):

        # 获取原始输入参数
        user = kwargs.get("user", None)
        functions = kwargs.get("functions", None)
        tools = kwargs.get("tools", None)
        top_p = kwargs.get("top_p", None)
        temperature = kwargs.get("temperature", None)
        input_messages = kwargs.get("messages", None)
        stream = kwargs.get("stream", False)
        max_tokens = kwargs.get("max_tokens", None)
        response_format = kwargs.get("response_format", None)

        wrap_cached = {
            'user': user,
            'stream': stream,
            'top_p': top_p,
            'temperature': temperature,
            'max_tokens': max_tokens,
            'response_format': response_format,
            'functions': functions,
            'tools': tools,
            'input_messages': input_messages,
        }

        start_time = time.perf_counter()
        timestamp = datetime.datetime.now().isoformat()  # 记录调用时间

        if stream:
            # Stream 模式处理逻辑
            response = create_fn(*args, **kwargs)
            outputs_messages = []
            current_message = {"role": None, "content": None, "function_call": None, "tool_calls": None}
            model = None
            usage = None

            def gen():
                nonlocal outputs_messages, current_message, model, usage
                try:
                    for chunk in response:
                        # 提取模型名称
                        if model is None:
                            model = chunk.model

                        usage = {
                            'completion_tokens': chunk.usage.completion_tokens,
                            'prompt_tokens': chunk.usage.prompt_tokens,
                            'total_tokens': chunk.usage.total_tokens
                        } if chunk.usage else None
                        
                        for choice in chunk.choices:
                            delta = choice.delta

                            # 更新 role（通常出现在第一块）
                            if delta.role:
                                if current_message["role"] is None:
                                    if delta.role == "model":
                                        delta.role = "assistant"
                                    current_message["role"] = delta.role

                            # 累积内容
                            if delta.content:
                                if current_message["content"] is None:
                                    current_message["content"] = delta.content
                                else:
                                    current_message["content"] += delta.content

                            
                            # 处理工具调用
                            if delta.function_call:
                                if current_message['function_call'] is None:
                                    current_message['function_call'] = {
                                        "name": delta.function_call.name,
                                        "arguments": delta.function_call.arguments
                                    }
                                else:
                                    current_message['function_call']['arguments'] += delta.function_call.arguments

                            if delta.tool_calls:
                                if current_message['tool_calls'] is None:
                                    current_message['tool_calls'] = [{'name': '', 'arguments': ''} for _ in range(len(delta.tool_calls))]

                                
                                for tool_call in delta.tool_calls:
                                    if tool_call.function:
                                        if tool_call.function.name:
                                            current_message['tool_calls'][tool_call.index]['name'] += tool_call.function.name
                                        if tool_call.function.arguments:
                                            current_message['tool_calls'][tool_call.index]['arguments'] += tool_call.function.arguments
                                    
                            # 完成一条消息
                            if choice.finish_reason in ["stop", "function_call", "tool_calls"]:
                                outputs_messages.append(current_message)
                                current_message = {"role": None, "content": "", "function_call": None, "tool_calls": None}

                        yield chunk
                finally:
                    # 收集最后一条未完成的消息
                    if current_message["content"]:
                        outputs_messages.append(current_message)

                    elapsed_time = time.perf_counter() - start_time
                    wrap_cached.update({
                        "outputs_messages": outputs_messages,
                        "model": model,
                        "usage": usage,
                        "timestamp": timestamp,
                        "elapsed_time": elapsed_time,
                    })
                    
                    if logger_fn is not None:
                        logger_fn(wrap_cached)
                
            return gen()

        else:
            # 非 Stream 模式处理逻辑
            response = create_fn(*args, **kwargs)
            elapsed_time = time.perf_counter() - start_time
            usage = {
                'completion_tokens': response.usage.completion_tokens,
                'prompt_tokens': response.usage.prompt_tokens,
                'total_tokens': response.usage.total_tokens
            } if response.usage else None

            model = response.model if response.model else kwargs.get('model', 'unknown')
            outputs_messages = [
                {
                    'role': i.message.role if i.message.role != 'model' else 'assistant',
                    'content': i.message.content,
                    'tool_calls': [{'name': j.function.name, 'arguments': j.function.arguments} for j in
                                   i.message.tool_calls] if i.message.tool_calls else None,
                    'function_call': {
                        'name': i.message.function_call.name,
                        'arguments': i.message.function_call.arguments
                    } if i.message.function_call else None,
                }
                for i in response.choices
            ]

            wrap_cached.update({
                'outputs_messages': outputs_messages,
                'model': model,
                'usage': usage,
                'timestamp': timestamp,
                'elapsed_time': elapsed_time
            })

            if logger_fn is not None:
                logger_fn(wrap_cached)

            return response

    return create