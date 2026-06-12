"""自描述工具 —— 一份数据定义一个完整工具"""

from dataclasses import dataclass
from typing import Callable, Optional, Literal
from google.genai import types

TYPE_MAP = {
    "object":  types.Type.OBJECT,
    "number":  types.Type.NUMBER,
    "string":  types.Type.STRING,
    "boolean": types.Type.BOOLEAN,
    "array":   types.Type.ARRAY,
}        


@dataclass
class Tool:
    """一个可被 LLM 调用的工具"""

    name: str
    description: str
    schema: dict
    handler: Optional[Callable] = None
    location: Literal["local", "freecad"] = "local"

    @staticmethod
    def to_schema(d:dict)-> types.Schema:
        """dict到types.Schema 的递归转换"""
        kwargs = {"type": TYPE_MAP.get(d.get("type", ""), types.Type.STRING)}
        if "description" in d:
            kwargs["description"] = d["description"]
        if "properties" in d:
            kwargs["properties"] = {k: Tool.to_schema(v) for k, v in d["properties"].items()}
        if "required" in d:
            kwargs["required"] = d["required"]
        if "items" in d:
            kwargs["items"] = Tool.to_schema(d["items"])
        return types.Schema(**kwargs)

    def to_gemini_declaration(self) -> types.FunctionDeclaration:
        """转成 Gemini API 认识的 FunctionDeclaration"""
        return types.FunctionDeclaration(
            name=self.name,
            description=self.description,
            parameters=self.to_schema(self.schema),
        )
    
    def to_openai_declaration(self) -> dict:
        """转成 OpenAI/DeepSeek 认识的 格式"""
        return{
            "type":"function",
            "function":{
                "name":self.name,
                "description":self.description,
                "parameters":self.schema,
            },
        }
