"""所有规划器的基类"""
import os
import json
import asyncio
from contextlib import AsyncExitStack 
from src.tools.ToolRegistry import ToolRegistry
from src.tools.local_tools import local_tools
from src.tools.cad_tools import cad_tools

_BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FREECAD_PYTHON_PATH = r"D:\FreeCAD\bin\python.exe"
FREECAD_WORKER_PATH = os.path.join(_BASE, "src", "CAD", "freecad_worker.py")

class Base_Planner:
    def __init__(self):
        self.client = None
        self.exit_stack = AsyncExitStack()
        # 工具自注册
        self.registry = ToolRegistry()
        self.registry.register_many(cad_tools)
        self.registry.register_many(local_tools)
        
        print(f"已注册{len(self.registry)}个工具：{self.registry.list_all()}")

    async def short_memory(self,query:str)->str:
        """注入短期记忆：当前文档中已有的对象"""
        if not os.path.exists("output/cad_state.FCStd"):
            return query
        doc_info = await self.run_freecad("list_objects", {})
        if doc_info.get("status") == "success" and doc_info.get("objects"):
            lines = []
            for o in doc_info["objects"]:
                lines.append(f"- {o['name']} ({o.get('type','?')}, 体积 {o.get('volume',0):.1f} mm³)")
            context = "\n".join(lines)
            query = f"当前已有对象：\n{context}\n\n用户请求：{query}"

        return query

    async def execute_tool(self,tool_name:str,tool_args:dict)->dict:
        """工具调用"""
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
                cwd=_BASE,
            )
        stdout, _ = await proc.communicate()
        return json.loads(stdout)

    async def process_query(self,query:str):
        """处理查询"""
        pass

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery:").strip()

                if query.lower() == 'quit':
                    break
                response =await self.process_query(query)
                print("\n"+response)
            except Exception as e:
                print(f"\nError:{str(e)}")

    async def cleanup(self):
        await self.exit_stack.aclose()
