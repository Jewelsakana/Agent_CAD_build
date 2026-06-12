import asyncio
from src.planner.Gemini_Planner import Gemini_Planner
from src.planner.DeepSeek_Planner import DeepSeek_Planner
async def main():
    Planner = DeepSeek_Planner()
    try:
        await Planner.chat_loop()
    finally:
        await Planner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
