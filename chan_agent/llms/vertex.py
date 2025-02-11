import os
from functools import cache
from typing import Any
from openai import OpenAI
import instructor
from .base import BaseLLM, register_llm
from chan_agent.llm_track import wrap_create

import google.auth
import google.auth.transport.requests


# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "TODO"


class OpenAICredentialsRefresher:
    def __init__(self, **kwargs: Any) -> None:
        # Set a dummy key here
        self.client = OpenAI(**kwargs, api_key="DUMMY")
        self.creds, self.project = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )

    def __getattr__(self, name: str) -> Any:
        if not self.creds.valid:
            auth_req = google.auth.transport.requests.Request()
            self.creds.refresh(auth_req)

            if not self.creds.valid:
                raise RuntimeError("Unable to refresh auth")

            self.client.api_key = self.creds.token
        return getattr(self.client, name)

@cache
def init_openai_client(base_url:str, api_key:str):
    """
    初始化client客户端
    """
    # TODO 
    project_id = "trim-sum-437705-u7"
    location = "asia-east1"
    
    # 定义openai client
    client = OpenAICredentialsRefresher(
        base_url=f"https://{location}-aiplatform.googleapis.com/v1beta1/projects/{project_id}/locations/{location}/endpoints/openapi",
    )

    client.chat.completions.create = wrap_create(create_fn=client.chat.completions.create)

    return client

@register_llm(model_type='vertexai')
class VertexLLM(BaseLLM):
    def __init__(self, model_name: str = 'google/gemini-1.5-flash-002'):
        super().__init__(model_name)
        
        self.client = init_openai_client()
     
        self.instructor_client = instructor.from_openai(
            self.client.client,
            mode=instructor.Mode.JSON
        )
        
    


    


