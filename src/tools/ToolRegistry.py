"""工具注册中心 —— 统一管理工具的注册、查询和 Gemini schema 导出"""

from google.genai import types
from src.tools.Tool import Tool


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool):
        """注册单个工具"""
        self._tools[tool.name] = tool

    def register_many(self, tools: list[Tool]):
        """批量注册"""
        for t in tools:
            self.register(t)

    def get(self, name: str) -> Tool | None:
        """按名称获取工具"""
        return self._tools.get(name)

    def get_gemini_tool(self) -> types.Tool:
        """返回 types.Tool，可直接放进 config.tools"""
        declarations = [t.to_gemini_declaration() for t in self._tools.values()]
        return types.Tool(function_declarations=declarations)

    def list_all(self) -> list[str]:
        return list(self._tools.keys())

    def __len__(self):
        return len(self._tools)
