import sys,json
from src.CAD.FreeCADTools import create_box,create_cylinder,create_sphere,create_cone,boolean_cut,boolean_fuse,export_stl,save_doc,list_objects

handlers = {
        "create_box":      create_box,
        "create_cylinder": create_cylinder,
        "create_sphere":   create_sphere,
        "create_cone":     create_cone,
        "boolean_cut":     boolean_cut,
        "boolean_fuse":    boolean_fuse,
        "export_stl":      export_stl,
        "list_objects":    list_objects,
    }

def main():
    tool_name = sys.argv[1]
    tool_args = json.loads(sys.argv[2])
    results = execute(tool_name,tool_args)
    print(json.dumps(results))

def execute(name:str,args:dict)->dict:
    handler = handlers.get(name)
    if handler is None:
        return {"status":"error","message":f"未知工具{name}"}
    results = handler(args)
    if results.get("status") == "success":
        save_doc()
    return results

if __name__ == "__main__":
    main()