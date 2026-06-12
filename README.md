# CAD Agent

基于 LLM Agent 的 3D CAD 建模系统。用户用自然语言描述需求，AI 自动规划、生成 FreeCAD 操作代码并执行，最终输出可渲染的 3D 模型。

## 架构

```
用户输入（自然语言）
    │
    ▼
┌─────────────────────────────────────────────┐
│  Gemini_Planner (LLM Agent)                 │
│  - 理解需求、规划步骤                        │
│  - 调用工具、分析反馈、迭代修正               │
│  - 模型: gemini-2.5-flash                   │
└──────────────┬──────────────────────────────┘
               │
    ┌──────────┴──────────┐
    ▼                     ▼
┌──────────┐      ┌──────────────────┐
│ 本地工具  │      │  FreeCAD 子进程   │
│ render   │      │  (Python 3.11)   │
│ STL→PNG  │      │  create_*        │
└──────────┘      │  boolean_*       │
                  │  export_stl      │
                  └──────────────────┘
```

## 工具列表

| 工具 | 位置 | 功能 |
|------|------|------|
| `create_box` | FreeCAD | 创建立方体 |
| `create_cylinder` | FreeCAD | 创建圆柱体 |
| `create_sphere` | FreeCAD | 创建球体 |
| `create_cone` | FreeCAD | 创建圆锥/圆台 |
| `boolean_cut` | FreeCAD | 布尔减法（打孔/开槽） |
| `boolean_fuse` | FreeCAD | 布尔加法（合并） |
| `export_stl` | FreeCAD | 导出 STL 文件 |
| `render_view` | 本地 | STL 渲染为 PNG 预览 |

## 快速开始

```bash
# 1. 安装依赖
uv sync

# 2. 安装 FreeCAD
#    https://www.freecad.org/downloads.php

# 3. 配置 API Key
#    在 .env 中填入 GOOGLE_API_KEY
#    获取地址: https://aistudio.google.com

# 4. 运行
python src/main.py
```

## 项目结构

```
src/
├── main.py                     # 入口
├── planner/
│   ├── Base_Planner.py         # Agent 抽象基类
│   └── Gemini_Planner.py       # Gemini Agent 实现
├── tools/
│   ├── Tool.py                 # 自描述工具数据类
│   ├── ToolRegistry.py         # 工具注册中心
│   ├── cad_tools.py            # 7 个 CAD 工具 schema
│   └── local_tools.py          # 本地渲染工具
└── CAD/
    ├── freecad_worker.py       # 子进程入口 + 分发
    └── FreeCADTools.py         # FreeCAD API 实现
```

## 当前状态

- [x] Agent 循环（LLM ↔ 工具）
- [x] 8 个工具的 Gemini Schema 定义
- [x] FreeCAD 基础建模（创建、布尔运算、导出）
- [x] 子进程通信 + 状态持久化
- [x] STL 渲染为 PNG 预览
- [ ] 异常处理完善

## 迭代计划

### V2 — 对话记忆与上下文

当前每次启动 Agent 都是全新对话，无法记住之前的建模历史。

**短期记忆**：
- 利用已有的 `.FCStd` 状态持久化，启动时加载上次模型
- 在系统提示词中注入当前文档对象列表，让 LLM 感知已存在的几何体

**长期记忆**：
- 使用向量数据库（如 ChromaDB）存储历史设计模式
- 检索式增强生成：用户说 "和上次那个底座差不多"，自动检索相关设计
- 用户偏好学习：常用参数、风格倾向

### V3 — 手绘草图输入

- Gemini 多模态能力支持图片输入
- 用户拍照/手绘 → LLM 理解几何意图 → 自动参数化建模

### V4 — 错误自愈

- Worker 返回的异常自动分析
- LLM 根据错误信息修正代码，自动重试
