from .base import BaseLLM, LLM_REGISTRY
from .openai import OpenaiLLM
from .gemini import GeminiLLM
from .vertex import VertexLLM
from functools import cache


@cache
def get_llm(llm_type:str, model_name:str,  base_url:str, api_key:str) -> BaseLLM:
    """
    获取llm
    """
    if llm_type not in LLM_REGISTRY:
        raise ValueError(f"Invalid llm_type: {llm_type}. Must be one of {list(LLM_REGISTRY.keys())}.")
   
    return LLM_REGISTRY[llm_type](model_name, base_url, api_key)


__all__ = [
    'BaseLLM',
    'LLM_REGISTRY',
    'get_llm',
]