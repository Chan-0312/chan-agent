from chan_agent import get_llm


llm = get_llm(
    llm_type="openai", 
    model_name="gpt-4o-mini", 
    base_url="https://hk.uniapi.io/v1", 
    api_key="sk-0PIR2qx6KjaQb6D_ERwyQv7iquOr2frdk3uKkyQpB3u40UhVgPhGw6ieUXo",
)

out = llm.text_completions_with_messages_stream(messages=[{'role': 'user', 'content': 'Hello, world!'}], return_usage=True)

for i in out:
    print(i)