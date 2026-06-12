"""FreeCAD 工具定义"""

from src.tools.Tool import Tool


# 1 ── 立方体 ──────────────────────────────────────────
create_box = Tool(
    name="create_box",
    description="在FreeCAD中创建一个长方体/立方体。用途：底座、外壳、垫块、平板等基础几何体。",
    schema={
        "type": "object",
        "properties": {
            "length": {"type": "number", "description": "X方向长度 (mm)"},
            "width":  {"type": "number", "description": "Y方向宽度 (mm)"},
            "height": {"type": "number", "description": "Z方向高度 (mm)"},
            "name":   {"type": "string", "description": "可选的对象名称"},
        },
        "required": ["length", "width", "height"],
    },
    location="freecad",
)

# 2 ── 圆柱体 ──────────────────────────────────────────
create_cylinder = Tool(
    name="create_cylinder",
    description="在FreeCAD中创建一个圆柱体。用途：轴、销钉、柱子、孔的初始形状等。",
    schema={
        "type": "object",
        "properties": {
            "radius": {"type": "number", "description": "底面半径 (mm)"},
            "height": {"type": "number", "description": "圆柱高度 (mm)"},
            "name":   {"type": "string", "description": "可选的对象名称"},
        },
        "required": ["radius", "height"],
    },
    location="freecad",
)

# 3 ── 球体 ────────────────────────────────────────────
create_sphere = Tool(
    name="create_sphere",
    description="在FreeCAD中创建一个球体。用途：球头、滚珠、装饰球等。",
    schema={
        "type": "object",
        "properties": {
            "radius": {"type": "number", "description": "球体半径 (mm)"},
            "name":   {"type": "string", "description": "可选的对象名称"},
        },
        "required": ["radius"],
    },
    location="freecad",
)

# 4 ── 圆锥/圆台 ──────────────────────────────────────
create_cone = Tool(
    name="create_cone",
    description="在FreeCAD中创建一个圆锥体（或圆台）。radius1=radius2时为圆柱，其中一个为0时为圆锥。用途：锥形轴、漏斗、过渡段等。",
    schema={
        "type": "object",
        "properties": {
            "radius1": {"type": "number", "description": "底面半径 (mm)"},
            "radius2": {"type": "number", "description": "顶面半径 (mm)，0=尖端"},
            "height":  {"type": "number", "description": "高度 (mm)"},
            "name":    {"type": "string", "description": "可选的对象名称"},
        },
        "required": ["radius1", "radius2", "height"],
    },
    location="freecad",
)

# 5 ── 布尔减法 ───────────────────────────────────────
boolean_cut = Tool(
    name="boolean_cut",
    description="从一个物体（base）中减去另一个物体（tool）。用途：打孔、开槽、切除、雕刻。注意：需先创建 base 和 tool 两个物体。",
    schema={
        "type": "object",
        "properties": {
            "base_name": {"type": "string", "description": "被切削的主体对象名"},
            "tool_name": {"type": "string", "description": "作为切削工具的对象名"},
        },
        "required": ["base_name", "tool_name"],
    },
    location="freecad",
)

# 6 ── 布尔加法 ───────────────────────────────────────
boolean_fuse = Tool(
    name="boolean_fuse",
    description="将两个物体合并为一个整体。用途：组合多个简单形状成复杂零件。注意：两个物体需先通过 create_* 创建好。",
    schema={
        "type": "object",
        "properties": {
            "object1": {"type": "string", "description": "第一个对象名"},
            "object2": {"type": "string", "description": "第二个对象名"},
        },
        "required": ["object1", "object2"],
    },
    location="freecad",
)

# 7 ── 导出 STL ───────────────────────────────────────
export_stl = Tool(
    name="export_stl",
    description="将FreeCAD中的对象导出为STL格式文件。STL可用于3D打印、或其他渲染器查看。应在所有建模操作完成后调用。",
    schema={
        "type": "object",
        "properties": {
            "object_name": {"type": "string", "description": "要导出的对象名"},
            "output_path": {"type": "string", "description": "输出路径，默认 output/model.stl"},
        },
        "required": ["object_name"],
    },
    location="freecad",
)

# 8 ── 查询当前文档 ───────────────────────────────────
list_objects = Tool(
    name="list_objects",
    description="列出当前FreeCAD文档中已有的所有对象（名称、类型、体积）。在开始建模或修改已有模型前调用此工具了解当前状态。",
    schema={
        "type": "object",
        "properties": {},
        "required": [],
    },
    location="freecad",
)

# ── 批量注册用 ────────────────────────────────────────
cad_tools = [
    create_box,
    create_cylinder,
    create_sphere,
    create_cone,
    boolean_cut,
    boolean_fuse,
    export_stl,
    list_objects,
]
