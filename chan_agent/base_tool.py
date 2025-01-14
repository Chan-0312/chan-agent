import json
from abc import ABC, abstractmethod
from typing import List, Optional, Union
from .logger import logger
from .schema import ToolResult

TOOL_REGISTRY = {}


def register_tool(name, allow_overwrite=False):

    def decorator(cls):
        if name in TOOL_REGISTRY:
            if allow_overwrite:
                logger.warning(f'Tool `{name}` already exists! Overwriting with class {cls}.')
            else:
                raise ValueError(f'Tool `{name}` already exists! Please ensure that the tool name is unique.')
        if cls.name and (cls.name != name):
            raise ValueError(f'{cls.__name__}.name="{cls.name}" conflicts with @register_tool(name="{name}").')
        cls.name = name
        TOOL_REGISTRY[name] = cls

        return cls

    return decorator


def schema_to_str(schema: Union[List[dict], dict], indent_level=0):
    """
    转换为字符串描述
    """
    output = []
    
    # 设置缩进
    indent = "  " * indent_level

    for key in schema:
        type_ = schema[key].get('type')
        description = schema[key].get('description', '')
        items = schema[key].get('items', {})
        properties = schema[key].get('properties', {})
        required = schema[key].get('required', True)

        if type_ == 'array' and items:
            # 数组
            item_type = items.get('type')
            item_properties = items.get('properties', {})
            if item_type == 'object' and item_properties:
                output.append(f"{indent}- `{key}`: list[object] {description}, each object with the following properties:")
                output.extend(schema_to_str(item_properties, indent_level + 1))
            else:
                output.append(f"{indent}- `{key}`: list[{item_type}], {description}")

        elif type_ == 'object' and properties:
            # 如果是对象
            output.append(f"{indent}- `{key}`: object {description}, with the following properties:")
            output.extend(schema_to_str(properties, indent_level + 1))
        else:
            output.append(f"{indent}- `{key}`: {type_ if required else f'Optional[{type_}]'} {description}")
        
    return output

    

class BaseTool(ABC):
    name: str = ''
    description: str = ''
    parameters: List[dict] = {
        'your_key_name': {
            'type': 'array',
            'items': {
                'type': 'number',
            },
            'description': 'your key description',
            'required': True
        },
    }

    def __init__(self, cfg: Optional[dict] = None):
        self.cfg = cfg or {}
        if not self.name:
            raise ValueError(
                f'You must set {self.__class__.__name__}.name, either by @register_tool(name=...) or explicitly setting {self.__class__.__name__}.name'
            )

    def __str__(self):
        output = []
        
        # 名称和描述
        output.append(f"- {self.name}: {self.description}, with the following input parameters:")

        output.extend(schema_to_str(self.parameters, 1))

        return '\n'.join(output)

    @abstractmethod
    def call(self, params: Union[str, dict], **kwargs) -> ToolResult:
        """The interface for calling tools.

        Each tool needs to implement this function, which is the workflow of the tool.

        Args:
            params: The parameters of func_call.
            kwargs: Additional parameters for calling tools.

        Returns:
            The result returned by the tool, implemented in the subclass.
        """
        raise NotImplementedError

    def _verify_json_format_args(self, params: Union[str, dict]) -> dict:
        """Verify the parameters of the function call"""
        if isinstance(params, str):
            try:
                params_json: dict = json.loads(params)
            except json.decoder.JSONDecodeError:
                raise ValueError('Parameters must be formatted as a valid JSON!')
        else:
            params_json: dict = params
        
        # TODO 验证参数格式

        return params_json

