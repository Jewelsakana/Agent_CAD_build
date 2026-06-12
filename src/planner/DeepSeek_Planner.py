import os
import json
from openai import AsyncOpenAI
from src.planner.Base_Planner import Base_Planner
from dotenv import load_dotenv

load_dotenv() #从.env中导入环境变量

class DeepSeek_Planner(Base_Planner):
    def __init__(self):
        super().__init__()
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("未找到DEEPSEEK_API_KEY，请在 .env 中设置")
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )       


    async def process_query(self,query:str)->str:
        query = self.short_memory(query)
        messages = [
            {
                "role":"user",
                "content":query
            }
        ]
        tools = self.registry.get_openai_tools() # 工具列表
        while True:
            # 将用户问题+工具定义发给Deepseek
            response = await self.client.chat.completions.create(
                model="deepseek-v4-flash",
                max_tokens=1000,
                messages=messages,
                tools=tools
            )

            msg= response.choices[0].message
            # 处理回复中的文本和工具调用
            assistant_msg = {
                "role":"assistant",
                "content":msg.content or ""
            }
            if msg.tool_calls:
                assistant_msg["tool_calls"]=[
                {
                    "id":tc.id,
                    "type":"function",
                    "function":{
                        "name":tc.function.name,
                        "arguments":tc.function.arguments
                    }
                }
                for tc in msg.tool_calls
            ]

            # 将完整的信息加入历史
            messages.append(assistant_msg)

            # 如果没有工具调用了则说明最终答案已经生成，返回所有的文本
            if not msg.tool_calls:
                return msg.content

            # 执行工具，构造返回
            for fc in msg.tool_calls:
                name = fc.function.name
                args = json.loads(fc.function.arguments)
                result = await self.execute_tool(name,args)
                # 把工具的结果加入历史中
                messages.append(            
                {
                    "role":"tool",
                    "tool_call_id":fc.id,
                    "content":json.dumps(result,ensure_ascii=False),
                }
            )



