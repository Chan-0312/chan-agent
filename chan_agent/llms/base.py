from abc import ABC
from pydantic import BaseModel
from typing import Union, Iterator, List
from chan_agent.logger import logger
from chan_agent.utils.image import encode_image_from_url

LLM_REGISTRY = {}


def register_llm(model_type):

    def decorator(cls):
        LLM_REGISTRY[model_type] = cls
        return cls

    return decorator




class BaseLLM(ABC):

    def __init__(self, model_name: str = 'gpt-4o-mini'):
        self.model_name = model_name
        
        self.client = None
        self.instructor_client = None

    def set_model_name(self, model_name: str):
        """
        修改模型名称
        """
        self.model_name = model_name

    def image_completions(
            self, 
            prompt: str, 
            images: List[str], 
            instructions: str = None, 
            temperature: float = None,
            top_p: float = None,
            max_tokens: int = None,
            timeout: int = 30,
            return_usage: bool = False
        ) -> str | dict:
        """
        图像分析
        """
        if 'gemini' in self.model_name:
            images = [encode_image_from_url(image_url) for image_url in images]

        messages = []
        if instructions:
            messages.append({"role": "system", "content": instructions})

        # 初始化用户内容列表，包含文本提示
        user_content = [{"type": "text", "text": prompt}]
        # 将图片URLs添加到用户内容列表中
        user_content.extend(
            [{"type": "image_url", "image_url": {"url": img_url}} for img_url in images])
        # 构造消息列表，包括系统指令和用户内容
        messages.append({"role": "user", "content": user_content})
        return self.text_completions_with_messages(messages, temperature=temperature, top_p=top_p, max_tokens=max_tokens, timeout=timeout, return_usage=return_usage)

    def image_basemodel_completions(
            self, 
            basemodel: type[BaseModel], 
            prompt: str, 
            images: List[str],
            instructions: str = None, 
            timeout:int=30
        )  -> Union[BaseModel,None]:
        """
        使用prompt生成basemodel
        """
        if 'gemini' in self.model_name:
            images = [encode_image_from_url(image_url) for image_url in images]

        messages = []
        if instructions:
            messages.append({"role": "system", "content": instructions})

        # 初始化用户内容列表，包含文本提示
        user_content = [{"type": "text", "text": prompt}]
        # 将图片URLs添加到用户内容列表中
        user_content.extend(
            [{"type": "image_url", "image_url": {"url": img_url}} for img_url in images])
        # 构造消息列表，包括系统指令和用户内容
        messages.append({"role": "user", "content": user_content})

        return self.basemodel_completions_with_messages(basemodel, messages, timeout)


    def text_completions_with_messages(
            self, 
            messages: list, 
            temperature: float = None,
            top_p: float = None,
            max_tokens: int = None,
            timeout: int = 30,
            return_usage: bool = False,
        ) -> str | dict:
        """
        使用 messages 列表生成文本 completions。
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                stream=False,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
                timeout=timeout,
            )
            usage = {
                'completion_tokens': response.usage.completion_tokens,
                'prompt_tokens': response.usage.prompt_tokens,
                'total_tokens': response.usage.total_tokens
            } if response.usage else None
            content = response.choices[0].message.content

            if return_usage:
                return {
                    'content': content,
                    'usage': usage
                }
            else:
                return content
        except Exception as e:
            logger.error(f"text_completions_with_messages | Error: {e}")
            if return_usage:
                return {
                    'content': "error",
                    'usage': None
                }
            else:
                return "error"
    
    def text_completions_with_messages_stream(
            self, 
            messages: list, 
            temperature: float = None,
            top_p: float = None,
            max_tokens: int = None,
            timeout: int = 30,
            return_usage: bool = False,
        ) -> Iterator[Union[str, dict]]:
        """
        使用 messages 列表生成文本 completions。
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                stream=True,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
                timeout = timeout,
                stream_options={'include_usage': True}
            )

            full_content = ""
            for chunk in response:
                if chunk.choices:
                    choices = chunk.choices[0]
                    if choices.delta.content:
                        full_content += choices.delta.content
                
                if return_usage:
                    usage = {
                        'completion_tokens': chunk.usage.completion_tokens,
                        'prompt_tokens': chunk.usage.prompt_tokens,
                        'total_tokens': chunk.usage.total_tokens
                    } if chunk.usage else None
                    yield {
                        'content': full_content,
                        'usage': usage
                    }
                else:
                    yield full_content                
        except Exception as e:
            logger.error(f"text_completions_with_messages_stream | Error: {e}")
            if return_usage:
                yield {
                    'content': "error",
                    'usage': None
                }
            else:
                yield "error"
        
    
    def text_completions(
            self, 
            prompt: str, 
            instructions: str = None, 
            temperature: float = None, 
            top_p: float = None, 
            max_tokens: int = None, 
            timeout: int = 30,
            return_usage: bool = False,
        ) -> str | dict:
        """
        使用prompt生成文本 completions
        """
        messages = []
        if instructions:
            messages.append({"role": "system", "content": instructions})
        messages.append({"role": "user", "content": prompt})

        return self.text_completions_with_messages(messages, temperature, top_p, max_tokens, timeout, return_usage)
    
    def text_completions_with_stream(
            self, 
            prompt: str, 
            instructions: str = None, 
            temperature: float = None, 
            top_p: float = None, 
            max_tokens: int = None, 
            timeout: int = 30,
            return_usage: bool = False
        )-> Iterator[Union[str, dict]]:
        """
        使用prompt生成文本 completions 流式返回
        """
        messages = []
        if instructions:
            messages.append({"role": "system", "content": instructions})
        messages.append({"role": "user", "content": prompt})
        return self.text_completions_with_messages_stream(messages, temperature, top_p, max_tokens, timeout, return_usage)
        
    
    def basemodel_completions(self, basemodel: type[BaseModel], prompt: str, instructions: str = None, timeout:int=30)  -> Union[BaseModel,None]:
        """
        使用prompt生成basemodel
        """
        messages = [{"role": "user", "content": prompt}]
        if instructions:
            messages.append({"role": "system", "content": instructions})

        return self.basemodel_completions_with_messages(basemodel, messages, timeout)

    def basemodel_completions_with_messages(self, basemodel: type[BaseModel], messages: list, timeout:int=30) -> Union[BaseModel,None]:
        """
        使用messages列表生成basemodel
        """
        # BUG 这里可能回卡死
        try:
            res = self.instructor_client.chat.completions.create(
                model=self.model_name,
                response_model=basemodel,
                messages=messages,
                max_retries=3,
                timeout=timeout  # 内部timeout参数保留，但主要依赖外部超时
            )
            return res
        except TimeoutError:
            logger.error(f'basemodel_completions_with_messages | Timeout after {timeout} seconds')
            return None
        except Exception as e:
            logger.error(f'basemodel_completions_with_messages | Internal Error: {e}')
            return None

    

        
        