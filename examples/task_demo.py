from chan_agent.llms import get_llm
from chan_agent.task_llm import TaskLLM
from chan_agent.schema import TaskOutputs, TaskInputItem

llm = get_llm(
    llm_type='openai', 
    model_name='gpt-4o-mini', 
    base_url='https://api.openai.com/v1', 
    api_key='your-api-key'
)

class TranslationOutput(TaskOutputs):
    translation: str

task = "Translate the following text to French."
rules = ["Keep the original meaning.", "Use formal language."]

task_llm = TaskLLM(llm=llm, task=task, rules=rules, output_model=TranslationOutput)


inputs = [
    TaskInputItem(key="text", key_name="Text to translate", value="Hello, how are you?")
]

result = task_llm.call(inputs=inputs)
print(result)