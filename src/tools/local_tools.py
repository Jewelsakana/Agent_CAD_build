"""Local 工具定义和实现"""

import matplotlib.pyplot as plt
from stl import mesh
from src.tools.Tool import Tool
from google.genai import types

def render_stl_to_image(stl_path:str,output_path:str)->dict:
    """ 把STL文件渲染成PNG"""
    # 导入STl文件
    m = mesh.Mesh.from_file(stl_path)
    fig = plt.figure(figsize=(8,6))
    ax = fig.add_subplot(111,projection='3d')

    # 画三角面片
    for i in range(len(m.vectors)):
        tri = m.vectors[i]
        ax.plot_trisurf(tri[:, 0], tri[:, 1], tri[:, 2],
                         color='steelblue', alpha=0.8, shade=True)

    ax.set_box_aspect([1,1,1])
    plt.savefig(output_path,dpi = 150)
    plt.close()
    return {"status": "success", "message": output_path}

render_view = Tool(
    name="render_view",
    description="将STL模型渲染为2D预览图片，用于视觉反馈和检查。",
    schema=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "stl_path": types.Schema(type=types.Type.STRING, description="STL 文件路径"),
            "output_path": types.Schema(type=types.Type.STRING, description="输出 PNG 路径"),
        },
        required=["stl_path"],
    ),
    handler=render_stl_to_image,
    location="local",
)

local_tools = [render_view]