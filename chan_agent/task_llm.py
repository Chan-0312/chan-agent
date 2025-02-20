from .llms import BaseLLM
from .schema import TaskOutputs, TaskInputItem
from typing import List, Union
from pydantic import BaseModel
from textwrap import dedent


PROMPT_TASK_BACKBONE = dedent("""\
# Task 
{task}
                               
# Outputs Format
{outputs}

{rules}
                              
# Inputs
Please reference the following data and adhere to the rules as much as possible to complete the task:
{inputs}
""")

class TaskLLM:

    def __init__(
        self, 
        llm: BaseLLM, 
        task: str,
        rules: List[str], 
        output_model: TaskOutputs,
    ):
        self.llm = llm
        self.task = task
        self.rules = ""
        if len(rules):
            self.rules = "# Rules\n"
            for rule in rules:
                self.rules += f"- {rule}\n"
        self.output_model = output_model

    def call(self, inputs: List[TaskInputItem], **kwargs) -> Union[BaseModel, None]:
        
        prompt = PROMPT_TASK_BACKBONE.format(
            task = self.task,
            inputs = "\n\n".join([str(ip) for ip in inputs]),
            outputs = self.output_model.get_scheme(),
            rules = self.rules
        )

        return self.llm.basemodel_completions(self.output_model, prompt)
    


class ImageTaskLLM(TaskLLM):

    def call(self, inputs: List[TaskInputItem], images: List[str], **kwargs):

        inputs.append(
            TaskInputItem(
                key="images",
                key_name="images",
                value="See attached images",
            ))
        
        prompt = PROMPT_TASK_BACKBONE.format(
            task = self.task,
            inputs = "\n\n".join([str(ip) for ip in inputs]),
            outputs = self.output_model.get_scheme(),
            rules = self.rules
        )
        
        return self.llm.image_basemodel_completions(
            self.output_model,
            prompt = prompt,
            images = images
        )

        
