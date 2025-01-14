from abc import ABC
from pydantic import BaseModel
from typing import Union, Iterator
from chan_agent.logger import logger

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

    def text_completions_with_messages(
            self, 
            messages: list, 
            temperature: float = None,
            top_p: float = None,
            max_tokens: int = None,
        ) -> str:
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
            )

            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"text_completions_with_messages | Error: {e}")
            return "error"
    
    def text_completions_with_messages_stream(
            self, 
            messages: list, 
            temperature: float = None,
            top_p: float = None,
            max_tokens: int = None,
        ) -> Iterator[str]:
        """
        使用 messages 列表生成文本 completions。
        """

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            stream=True,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
        )

        full_content = ""
        for chunk in response:
            if chunk.choices:
                choices = chunk.choices[0]
                if choices.delta.content:
                    full_content += choices.delta.content
                    yield full_content
        
    
    def text_completions(self, prompt: str, instructions: str = None, temperature: float = None, top_p: float = None, max_tokens: int = None) -> str:
        """
        使用prompt生成文本 completions
        """
        messages = []
        if instructions:
            messages.append({"role": "system", "content": instructions})
        messages.append({"role": "user", "content": prompt})

        return self.text_completions_with_messages(messages, temperature, top_p, max_tokens)
    
    def text_completions_with_stream(self, prompt: str, instructions: str = None, temperature: float = None, top_p: float = None, max_tokens: int = None)-> Iterator[str]:
        """
        使用prompt生成文本 completions 流式返回
        """
        messages = []
        if instructions:
            messages.append({"role": "system", "content": instructions})
        messages.append({"role": "user", "content": prompt})
        return self.text_completions_with_messages_stream(messages, temperature, top_p, max_tokens)
        
    
    def basemodel_completions(self, basemodel: type[BaseModel], prompt: str, instructions: str = None)  -> Union[BaseModel,None]:
        """
        使用prompt生成basemodel
        """
        messages = [{"role": "user", "content": prompt}]
        if instructions:
            messages.append({"role": "system", "content": instructions})

        return self.basemodel_completions_with_messages(basemodel, messages)

    def basemodel_completions_with_messages(self, basemodel: type[BaseModel], messages: list) -> Union[BaseModel,None]:
        """
        使用messages列表生成basemodel
        """
        try:
            res = self.instructor_client.chat.completions.create(
                model=self.model_name,
                response_model=basemodel,
                messages=messages
            )
            return res
        except Exception as e:
            logger.error(f'basemodel_completions_with_messages | Error: {e}')
            return None

    

        
        