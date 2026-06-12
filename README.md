# CAD Agent

基于 LLM Agent 的 3D CAD 建模系统。用户用自然语言描述需求，AI 自动规划、调用 FreeCAD 工具执行建模，最终输出可渲染的 3D 模型。

## 架构

```
用户输入（自然语言）
    │
    ▼
┌──────────────────────────────────────────────┐
│  Base_Planner                                │
│  - 工具注册 + 派发 + 子进程通信 + 短期记忆      │
└──────┬────────────────────┬──────────────────┘
       │                    │
       ▼                    ▼
┌──────────────┐   ┌──────────────────┐
│ Gemini       │   │ DeepSeek         │
│ Planner      │   │ Planner          │
│ (google-genai)│  │ (OpenAI SDK)     │
└──────┬───────┘   └────────┬─────────┘
       │                    │
       └────────┬───────────┘
                ▼
┌──────────────────────────────┐
│  ToolRegistry                │
│  - 9 个工具，schema 纯 dict   │
│  - to_gemini() / to_openai() │
└──────┬───────────────────────┘
       │
  ┌────┴────┐
  ▼         ▼
┌─────┐  ┌──────────────────────┐
│本地  │  │ FreeCAD 子进程        │
│render│  │ (Python 3.11)        │
│STL→ │  │ create_*  boolean_*  │
│PNG  │  │ export_stl list_obj  │
└─────┘  └──────────────────────┘
```

## 工具列表 (9 个)

| 工具 | 位置 | 功能 |
|------|------|------|
| `create_box` | FreeCAD | 创建立方体 |
| `create_cylinder` | FreeCAD | 创建圆柱体 |
| `create_sphere` | FreeCAD | 创建球体 |
| `create_cone` | FreeCAD | 创建圆锥/圆台 |
| `boolean_cut` | FreeCAD | 布尔减法（打孔/开槽） |
| `boolean_fuse` | FreeCAD | 布尔加法（合并） |
| `export_stl` | FreeCAD | 导出 STL 文件 |
| `list_objects` | FreeCAD | 查询当前文档状态 |
| `render_view` | 本地 | STL 渲染为 PNG 预览 |

## 快速开始

```bash
# 1. 安装依赖
uv sync

# 2. 安装 FreeCAD
#    https://www.freecad.org/downloads.php

# 3. 配置 API Key（选其一）
#    .env: GOOGLE_API_KEY   ← Gemini, https://aistudio.google.com
#    .env: DEEPSEEK_API_KEY  ← DeepSeek, https://platform.deepseek.com

# 4. 切换 Planner（修改 src/main.py）
#    from src.planner.Gemini_Planner import Gemini_Planner as Planner
#    from src.planner.DeepSeek_Planner import DeepSeek_Planner as Planner

# 5. 运行
python src/main.py
```

## 项目结构

```
src/
├── main.py                     # 入口
├── planner/
│   ├── Base_Planner.py         # 基类：注册、派发、子进程、短期记忆
│   ├── Gemini_Planner.py       # Gemini Agent (google-genai SDK)
│   └── DeepSeek_Planner.py     # DeepSeek Agent (OpenAI SDK)
├── tools/
│   ├── Tool.py                 # 自描述工具 (schema纯dict，SDK无关)
│   ├── ToolRegistry.py         # 注册中心 → Gemini / OpenAI 格式
│   ├── cad_tools.py            # 8 个 CAD 工具 schema
│   └── local_tools.py          # 本地渲染工具
└── CAD/
    ├── freecad_worker.py       # 子进程入口 + 工具分发
    └── FreeCADTools.py         # FreeCAD API 实现 + 状态持久化
```

## 当前状态

- [x] Agent 循环（LLM ↔ 工具）
- [x] 双模型支持（Gemini + DeepSeek）
- [x] 9 个工具 schema，纯 dict，SDK 无关
- [x] FreeCAD 基础建模（创建、布尔运算、导出、查询）
- [x] 子进程通信 + 状态持久化
- [x] STL 渲染为 PNG 预览
- [x] 短期记忆（自动注入文档上下文）
- [ ] 异常处理完善

## 迭代计划

### V2 — 长期记忆

当前已实现短期记忆（每次对话自动感知文档状态）。下一步：

- 使用向量数据库（如 ChromaDB）存储历史设计模式
- 检索式增强生成："和上次那个底座差不多"自动匹配历史设计
- 用户偏好学习：常用参数、风格倾向

### V3 — 手绘草图输入

- Gemini 多模态能力支持图片输入
- 用户拍照/手绘 → LLM 理解几何意图 → 自动参数化建模

### V4 — 错误自愈

- Worker 返回的异常自动分析
- LLM 根据错误信息修正代码，自动重试
