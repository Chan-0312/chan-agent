from functools import cache
from openai import OpenAI
import instructor
from .base import BaseLLM, register_llm
from chan_agent.llm_track import wrap_create

@cache
def init_openai_client(base_url:str, api_key:str,**kwargs):
    """
    初始化client客户端
    """
    # 定义openai client
    client = OpenAI(
        base_url=base_url,
        api_key=api_key,
        **kwargs
    )

    client.chat.completions.create = wrap_create(create_fn=client.chat.completions.create)

    return client

@register_llm(model_type="openai")
class OpenaiLLM(BaseLLM):
    def __init__(self, model_name: str = 'gpt-4o-mini', base_url:str=None, api_key:str='xxx'):
        super().__init__(model_name)

        self.client = init_openai_client(base_url = base_url, api_key = api_key)
        if self.model_name is not None and self.model_name.startswith("gpt"):
            instructor_mode = instructor.Mode.TOOLS    
        else:
            # 兼任ollama等openai接口模型的其他模型
            instructor_mode = instructor.Mode.JSON
        self.instructor_client = instructor.from_openai(
            self.client,
            mode=instructor_mode
        )

