import google.generativeai as genai
from instructor import Instructor
from pydantic import BaseModel
from typing import Union, Iterator
import instructor
from .base import BaseLLM, register_llm
from chan_agent.logger import logger

@register_llm(model_type="gemini")
class GeminiLLM(BaseLLM):
    """
    GeminiClient is a class that wraps the Google Gemini API.
    """

    def __init__(self, model_name: str = 'gemini-1.5-flash', base_url:str=None, api_key:str='xxx'):
        super().__init__(model_name)
        
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(model_name=self.model_name)
        self.instructor_client: Instructor = instructor.from_gemini(
            self.client,
            mode=instructor.Mode.GEMINI_JSON
        )


    def text_completions(
            self, prompt: str, 
            instructions: str = None, 
            temperature: float = None, 
            top_p: float = None,
            max_tokens: int = None,
            timeout: int = 30,
            return_usage: bool = False,
        ) -> str:
        """
        使用prompt生成文本 completions
        """
        try:
            response = self.client.generate_content(
                contents=prompt,
            )
            return response.text
        except Exception as e:
            logger.error(f"text_completions | Error: {e}")
            raise "error"

    def text_completions_with_messages(
            self, 
            messages: list, 
            temperature: float = None,
            top_p: float = None,
            max_tokens: int = None,
            timeout: int = 30,
            return_usage: bool = False,
        ) -> str:
        """
        使用 messages 列表生成文本 completions。
        """
        try:
            history = []
            for msg in messages:
                if msg['role'] == 'user':
                    history.append({"role": "user", "parts": msg['content']})
                elif msg['role'] == 'assistant':
                    history.append({"role": "model", "parts": msg['content']})
            
            user_input = history[-1]
            history = history[:-1]        
            
            
            chat = self.client.start_chat(
                history=history
            )

            response = chat.send_message(user_input['parts'], stream=False)
            return response.text
        except Exception as e:
            logger.error(f"text_completions_with_messages | Error: {e}")
            return "error"

    def text_completions_with_messages_stream(
            self, 
            messages: list, 
            temperature: float = None,
            top_p: float = None,
            max_tokens: int = None,
            timeout: int = 30,
            return_usage: bool = False,
        ) -> Iterator[str]:
        """
        使用 messages 列表生成文本 completions。
        """

        history = []
        for msg in messages:
            if msg['role'] == 'user':
                history.append({"role": "user", "parts": msg['content']})
            elif msg['role'] == 'assistant':
                history.append({"role": "model", "parts": msg['content']})
        
        user_input = history[-1]
        history = history[:-1]        
        
        
        chat = self.client.start_chat(
            history=history
        )

        # 流式返回部分文本
        full_response = ""
        # 向聊天实例发送消息并处理流式返回
        for chunk in chat.send_message(user_input['parts'], stream=True):
            content = chunk.text
            full_response += content
            yield full_response  # 每次返回更新的部分内容
    
    def basemodel_completions_with_messages(self, basemodel: type[BaseModel], messages: list) -> Union[BaseModel,None]:
        try:
            res = self.instructor_client.chat.completions.create(
                response_model=basemodel,
                messages=messages
            )
            return res
        except Exception as e:
            logger.error(f'basemodel_completions_with_messages | Error: {e}')
            return None
