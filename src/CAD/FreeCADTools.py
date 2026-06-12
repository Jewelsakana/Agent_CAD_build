import FreeCAD as App
import Part
import os

DOC_PATH = "output/cad_state.FCStd"

def ensure_doc():
    """加载已有文档 or 新建"""
    if os.path.exists(DOC_PATH):
        App.loadFile(DOC_PATH)
        return App.ActiveDocument
    return App.newDocument("CAD_Model")

def save_doc():
    """保存文档"""
    os.makedirs("output",exist_ok=True)
    App.ActiveDocument.saveAs(DOC_PATH)

def list_objects(args):
    """返回文档中所有对象的信息"""
    doc = ensure_doc()
    objects = []

    for obj in doc.Objects:
        objects.append(
            {
                "name": obj.Name,
                "label": obj.Label,
                "type": obj.Shape.ShapeType if hasattr(obj.Shape, 'ShapeType') else "unknown",
                "volume": round(obj.Shape.Volume, 2) if obj.Shape else 0,                
            }
        )
    return {"status":"success","objects":objects,"count":len(objects)}

# 1 ── 立方体 ──────────────────────────────────────────
def create_box(args:dict)->dict:
    doc = ensure_doc()
    name = args.get("name","Box")

    # 在文档中建一个 Part 对象
    obj = doc.addObject("Part::Feature", name)
    # 直接造一个立方体
    obj.Shape = Part.makeBox(
        args["length"],
        args["width"],
        args["height"]
    )
    # 刷新文档
    doc.recompute()
    return {"status":"success","object_name":name,
            "volume":obj.Shape.Volume}

# 2 ── 圆柱体 ──────────────────────────────────────────
def create_cylinder(args:dict)->dict:
    doc = ensure_doc()
    name = args.get("name", "Cylinder")    
    # 在文档中建一个 Part 对象
    obj = doc.addObject("Part::Feature", name)
    # 直接造一个圆柱体
    obj.Shape = Part.makeCylinder(
        args["radius"],
        args["height"]
    )
    # 刷新文档
    doc.recompute()
    return {"status":"success","object_name":name,
            "volume":obj.Shape.Volume}

# 3 ── 球体 ────────────────────────────────────────────
def create_sphere(args:dict)->dict:
    doc = ensure_doc()
    name = args.get("name", "Sphere")    
    # 在文档中建一个 Part 对象
    obj = doc.addObject("Part::Feature", name)
    # 直接造一个球
    obj.Shape = Part.makeSphere(
        args["radius"],
    )
    # 刷新文档
    doc.recompute()
    return {"status":"success","object_name":name,
            "volume":obj.Shape.Volume}

# 4 ── 圆锥/圆台 ──────────────────────────────────────
def create_cone(args:dict)->dict:
    doc = ensure_doc()
    name = args.get("name", "Cone")    
    # 在文档中建一个 Part 对象
    obj = doc.addObject("Part::Feature", name)
    # 直接造一个圆锥或者圆台
    obj.Shape = Part.makeCone(
        args["radius1"], # 底半径
        args["radius2"], # 顶半径
        args["height"] # 高
    )
    # 刷新文档
    doc.recompute()
    return {"status":"success","object_name":name,
            "volume":obj.Shape.Volume}

# 5 ── 布尔减法 ───────────────────────────────────────
def boolean_cut(args:dict)->dict:
    doc = ensure_doc()

    base = doc.getObject(args["base_name"])
    tool = doc.getObject(args["tool_name"])   
    if base is None or tool is None:
        return {"status":"error","message":"找不到指定的对象"}
    
    # 布尔减法
    result_shape = base.Shape.cut(tool.Shape) 
    result_name = f"{args['base_name']}_cut"
    # 在文档中建一个 Part 对象
    result_obj = doc.addObject("Part::Feature", result_name)
    result_obj.Shape = result_shape
    # 刷新文档
    doc.recompute()
    return {"status":"success","object_name":result_name,
            "volume":result_obj.Shape.Volume}

# 6 ── 布尔加法 ───────────────────────────────────────
def boolean_fuse(args:dict)->dict:
    doc = ensure_doc()

    obj1 = doc.getObject(args["object1"])
    obj2 = doc.getObject(args["object2"])   
    if obj1 is None or obj2 is None:
        return {"status":"error","message":"找不到指定的对象"}
    
    # 布尔加法
    result_shape = obj1.Shape.fuse(obj2.Shape) 
    result_name = f"{args['object1']}_fused"
    # 在文档中建一个 Part 对象
    result_obj = doc.addObject("Part::Feature", result_name)
    result_obj.Shape = result_shape
    # 刷新文档
    doc.recompute()
    return {"status":"success","object_name":result_name,
            "volume":result_obj.Shape.Volume}

# 7 ── 导出 STL ───────────────────────────────────────
def export_stl(args):
    doc = ensure_doc()
    obj = doc.getObject(args["object_name"])

    if obj is None:
        return {"status": "error", "message": f"找不到对象: {args['object_name']}"}

    output = args.get("output_path","output/model.stl")
    os.makedirs(os.path.dirname(output) or ".",exist_ok=True)

    obj.Shape.exportStl(output)
    return {"status":"success","stl_path":output,
            "file_size_kb": round(os.path.getsize(output) / 1024, 1)}


