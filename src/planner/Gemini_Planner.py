"""使用Gemini的规划器"""

import asyncio
import json
import os

from src.planner.Base_Planner import Base_Planner
from src.tools.ToolRegistry import ToolRegistry
from src.tools.local_tools import local_tools
from src.tools.cad_tools import cad_tools
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

_BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FREECAD_PYTHON_PATH = r"D:\FreeCAD\bin\python.exe"
FREECAD_WORKER_PATH = os.path.join(_BASE, "src", "CAD", "freecad_worker.py")
class Gemini_Planner(Base_Planner):

    def __init__(self):
        # Gemini初始化
        super().__init__()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("未找到GOOGLE_API_KEY，请在 .env 中设置")
        self.client = genai.Client(api_key=api_key)

        # 工具自注册
        self.registry = ToolRegistry()
        self.registry.register_many(cad_tools)
        self.registry.register_many(local_tools)
        
        print(f"已注册{len(self.registry)}个工具：{self.registry.list_all()}")

    async def execute_tool(self,tool_name:str,tool_args:dict)->dict:
        tool = self.registry.get(tool_name)
        if tool is None:
            return {"status": "error", "message": f"未知工具: {tool_name}"}

        if tool.location == "local":
            return await tool.handler(**tool_args)
        else:
            return await self.run_freecad(tool_name,tool_args)
        
    async def run_freecad(self,tool_name:str,tool_args:dict)->dict:
        # 传入干净的环境
        env = os.environ.copy()
        env.pop("PYTHONHOME",None)
        env.pop("VIRTUAL_ENV", None)
        proc = await asyncio.create_subprocess_exec(
                FREECAD_PYTHON_PATH ,
                FREECAD_WORKER_PATH,
                tool_name,
                json.dumps(tool_args),
                stdout= asyncio.subprocess.PIPE,
                env=env,
            )
        stdout, _ = await proc.communicate()
        return json.loads(stdout)

    async def process_query(self,query:str) -> str:
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=query)]
            )
        ]
        tools = [self.registry.get_gemini_tool()] # 工具列表
        while True:
            # 调用模型进行回复
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=contents,
                config=types.GenerateContentConfig(tools=tools)
            )

            candidate = response.candidates[0]
            parts = candidate.content.parts

            model_parts = []
            function_calls = []
            # 处理回复中的文本和工具调用
            for part in parts:
                if part.text is not None:
                    model_parts.append(types.Part.from_text(text=part.text))
                elif part.function_call is not None:
                    model_parts.append(types.Part.from_function_call(
                        name=part.function_call.name,
                        args=part.function_call.args,
                    ))
                    function_calls.append(part.function_call)
            # 把模型回复添加到历史中
            contents.append(types.Content(
                role="model",
                parts=model_parts
            ))
            # 没有工具调用，返回
            if not function_calls:
                return "\n".join(p.text for p in parts if p.text)

            # 执行工具，构造返回
            tool_response_parts = []
            for fc in function_calls:
                result = await self.execute_tool(fc.name,fc.args)
                tool_response_parts.append(
                    types.Part.from_function_response(
                        name = fc.name,
                        response = result
                    )
                )
            # 把工具的结果加入历史中
            contents.append(types.Content(
                role="user",
                parts=tool_response_parts
            ))



