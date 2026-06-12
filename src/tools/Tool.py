"""自描述工具 —— 一份数据定义一个完整工具"""

from dataclasses import dataclass
from typing import Callable, Optional, Literal
from google.genai import types


@dataclass
class Tool:
    """一个可被 LLM 调用的工具"""

    name: str
    description: str
    schema: types.Schema
    handler: Optional[Callable] = None
    location: Literal["local", "freecad"] = "local"

    def to_gemini_declaration(self) -> types.FunctionDeclaration:
        """转成 Gemini API 认识的 FunctionDeclaration"""
        return types.FunctionDeclaration(
            name=self.name,
            description=self.description,
            parameters=self.schema,
        )
