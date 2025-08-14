# imports_check.py
import importlib, traceback, sys

def try_import(module_name, obj_name=None):
    try:
        mod = importlib.import_module(module_name)
        if obj_name and not hasattr(mod, obj_name):
            raise ImportError(f"'{module_name}' lacks attribute '{obj_name}'")
        return mod
    except Exception as e:
        print(f"[IMPORT ERROR] {module_name} (needed: {obj_name}): {type(e).__name__}: {e}")
        traceback.print_exc()
        raise

def check_all():
    try_import("src.make_shp.pipeline", "pipeline")
    try_import("src.run_full_pipeline", "run_full_pipeline")
    try_import("src.full_pipline_gui", "FullPipelineApp")
    try_import("src.common.help_txt_read", "load_help_text")
    try_import("src.common.imports_check", "check_all")
    

if __name__ == "__main__":
    check_all()

