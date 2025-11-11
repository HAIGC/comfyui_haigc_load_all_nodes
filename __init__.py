"""
haigc_load_all_nodes - ComfyUI 自定义节点工具包
"""

from .quick_load_by_name import QuickLoadByName

NODE_CLASS_MAPPINGS = {
    "QuickLoadByName": QuickLoadByName,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "QuickLoadByName": "按名称加载节点 📝",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

print("\033[34m[haigc_load_all_nodes]\033[0m 已注册 1 个节点：QuickLoadByName")

