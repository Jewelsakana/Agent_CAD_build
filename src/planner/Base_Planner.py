"""所有规划器的基类"""

from contextlib import AsyncExitStack 

class Base_Planner:
    def __init__(self):
        self.client = None
        self.exit_stack = AsyncExitStack()

    async def execute_tool(self,tool_name,tool_args):
        """工具调用"""
        pass

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
