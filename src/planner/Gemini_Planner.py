"""使用Gemini的规划器"""
import os

from src.planner.Base_Planner import Base_Planner
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

class Gemini_Planner(Base_Planner):

    def __init__(self):
        # Gemini初始化
        super().__init__()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("未找到GOOGLE_API_KEY，请在 .env 中设置")
        self.client = genai.Client(api_key=api_key)


    async def process_query(self,query:str) -> str:
        query = await self.short_memory(query)
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



