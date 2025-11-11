"""
节点包加载器
扫描指定节点包目录，提取并显示所有可用节点的信息
"""

import os
import sys
import importlib.util
from pathlib import Path
from typing import Tuple, Dict, Any, List
import json


class NodePackageLoader:
    """
    节点包加载器
    
    功能：
    - 扫描指定节点包目录
    - 提取所有节点类和显示名称
    - 生成详细的节点信息列表
    - 支持导出为 JSON 格式
    
    输入：
    - package_path: 节点包的完整路径
    - output_format: 输出格式（text/json）
    - include_details: 是否包含详细信息
    
    输出：
    - nodes_info: 节点信息文本
    - node_count: 节点数量
    - node_list: 节点名称列表（JSON字符串）
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "package_path": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "label": "节点包路径"
                }),
                "output_format": (["text", "json", "detailed"], {
                    "default": "detailed",
                    "label": "输出格式"
                }),
                "scan_subdirs": ("BOOLEAN", {
                    "default": True,
                    "label": "扫描子目录"
                }),
                "show_categories": ("BOOLEAN", {
                    "default": True,
                    "label": "显示分类信息"
                }),
            },
            "optional": {
                "filter_category": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "label": "分类筛选"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "INT", "STRING")
    RETURN_NAMES = ("nodes_info", "node_count", "node_list_json")
    FUNCTION = "load_nodes"
    CATEGORY = "haigc_toolkit/utils"
    OUTPUT_NODE = True
    
    def load_nodes(
        self,
        package_path: str,
        output_format: str = "detailed",
        scan_subdirs: bool = True,
        show_categories: bool = True,
        filter_category: str = ""
    ) -> Tuple[str, int, str]:
        """
        加载并分析节点包
        
        Args:
            package_path: 节点包路径
            output_format: 输出格式
            scan_subdirs: 是否扫描子目录
            show_categories: 是否显示分类
            filter_category: 分类筛选
            
        Returns:
            (节点信息文本, 节点数量, 节点列表JSON)
        """
        try:
            # 验证路径
            path = Path(package_path.strip())
            if not path.exists():
                error_msg = f"[ERROR] 路径不存在: {package_path}"
                return (error_msg, 0, "[]")
            
            if not path.is_dir():
                error_msg = f"[ERROR] 不是有效的目录: {package_path}"
                return (error_msg, 0, "[]")
            
            print(f"\n{'='*60}")
            print(f"[扫描] 开始扫描节点包: {path.name}")
            print(f"[路径] {path}")
            print(f"{'='*60}\n")
            
            # 扫描节点
            nodes_data = self._scan_package(path, scan_subdirs, filter_category)
            
            # 生成输出
            if output_format == "json":
                info_text = self._format_json(nodes_data)
            elif output_format == "text":
                info_text = self._format_simple(nodes_data, show_categories)
            else:  # detailed
                info_text = self._format_detailed(nodes_data, show_categories)
            
            # 生成节点列表JSON
            node_list = [node["class_name"] for node in nodes_data["nodes"]]
            node_list_json = json.dumps(node_list, ensure_ascii=False, indent=2)
            
            node_count = len(nodes_data["nodes"])
            
            print(f"\n[完成] 扫描完成，共找到 {node_count} 个节点\n")
            
            return (info_text, node_count, node_list_json)
            
        except Exception as e:
            error_msg = f"[ERROR] 加载失败: {str(e)}"
            print(f"[ERROR] NodePackageLoader: {error_msg}")
            import traceback
            traceback.print_exc()
            return (error_msg, 0, "[]")
    
    def _scan_package(self, package_path: Path, scan_subdirs: bool, filter_category: str) -> Dict[str, Any]:
        """扫描节点包目录"""
        nodes_data = {
            "package_name": package_path.name,
            "package_path": str(package_path),
            "nodes": [],
            "categories": {},
            "errors": []
        }
        
        node_map: Dict[str, Dict[str, Any]] = {}
        
        def add_nodes(node_list: List[Dict[str, Any]]):
            for node in node_list or []:
                class_name = node.get("class_name")
                if not class_name:
                    continue
                if class_name not in node_map:
                    node_map[class_name] = node
        
        # 尝试通过导入包直接获取映射（优先保证准确性）
        imported_nodes = self._load_via_import(package_path)
        add_nodes(imported_nodes)
        
        # 查找 __init__.py（作为备选方案，防止导入失败）
        init_file = package_path / "__init__.py"
        if init_file.exists():
            nodes_info = self._load_from_init(init_file, package_path)
            add_nodes(nodes_info)
        
        # 扫描 Python 文件
        if scan_subdirs:
            py_files = list(package_path.rglob("*.py"))
        else:
            py_files = list(package_path.glob("*.py"))
        
        for py_file in py_files:
            if py_file.name == "__init__.py":
                continue
            
            try:
                nodes_info = self._load_from_file(py_file, package_path)
                if nodes_info:
                    add_nodes(nodes_info)
            except Exception as e:
                nodes_data["errors"].append({
                    "file": str(py_file.relative_to(package_path)),
                    "error": str(e)
                })
        
        # 转换为列表以便后续处理
        nodes_data["nodes"] = sorted(
            node_map.values(),
            key=lambda node: (
                node.get("category", ""),
                node.get("display_name") or node.get("class_name", ""),
                node.get("class_name", "")
            )
        )
        
        # 筛选分类
        if filter_category:
            nodes_data["nodes"] = [
                node for node in nodes_data["nodes"]
                if filter_category.lower() in node.get("category", "").lower()
            ]
        
        # 统计分类
        for node in nodes_data["nodes"]:
            category = node.get("category", "未分类")
            if category not in nodes_data["categories"]:
                nodes_data["categories"][category] = []
            nodes_data["categories"][category].append(node["class_name"])
        
        return nodes_data
    
    def _load_via_import(self, package_path: Path) -> List[Dict[str, Any]]:
        """
        通过 importlib 导入节点包以获取 NODE_CLASS_MAPPINGS。
        对于复杂节点包，此方式比正则解析更可靠。
        """
        nodes: List[Dict[str, Any]] = []
        init_file = package_path / "__init__.py"
        if not init_file.exists():
            return nodes
        
        module_name = package_path.name
        full_name = f"custom_nodes.{module_name}"
        parent_dir = str(package_path.parent)
        added_path = False
        spec = None
        
        try:
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
                added_path = True
            
            spec = importlib.util.spec_from_file_location(full_name, init_file)
            if spec is None or spec.loader is None:
                return nodes
            
            module = importlib.util.module_from_spec(spec)
            module.__package__ = full_name
            module.__path__ = [str(package_path)]
            sys.modules[module_name] = module
            sys.modules[full_name] = module
            spec.loader.exec_module(module)  # type: ignore[attr-defined]
            
            mappings = getattr(module, "NODE_CLASS_MAPPINGS", None)
            display_names = getattr(module, "NODE_DISPLAY_NAME_MAPPINGS", {}) or {}
            
            if isinstance(mappings, dict) and mappings:
                for key, node_class in mappings.items():
                    node_info = {
                        "class_name": key,
                        "display_name": display_names.get(key, key),
                        "source_file": "__init__.py",
                        "category": getattr(node_class, "CATEGORY", "未分类") if hasattr(node_class, "CATEGORY") else "未分类",
                    }
                    
                    if hasattr(node_class, "RETURN_TYPES"):
                        node_info["return_types"] = str(node_class.RETURN_TYPES)
                    if hasattr(node_class, "FUNCTION"):
                        node_info["function"] = node_class.FUNCTION
                    if getattr(node_class, "__doc__", None):
                        node_info["description"] = (node_class.__doc__ or "").strip().split("\n")[0]
                    
                    nodes.append(node_info)
        except Exception as e:
            print(f"[WARNING] 导入节点包失败 ({module_name}): {e}")
        finally:
            if spec is not None:
                to_remove = [
                    name for name in list(sys.modules.keys())
                    if name == module_name
                    or name == full_name
                    or name.startswith(f"{module_name}.")
                    or name.startswith(f"{full_name}.")
                ]
                for name in to_remove:
                    sys.modules.pop(name, None)
            if added_path:
                try:
                    sys.path.remove(parent_dir)
                except ValueError:
                    pass
        
        return nodes
    
    def _load_from_init(self, init_file: Path, package_path: Path) -> List[Dict[str, Any]]:
        """从 __init__.py 加载节点映射"""
        nodes = []
        
        try:
            # 读取文件内容
            with open(init_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 尝试执行获取映射（安全性有限，仅用于分析）
            local_vars = {}
            try:
                exec(content, {"__name__": "__main__"}, local_vars)
            except:
                pass
            
            # 提取 NODE_CLASS_MAPPINGS
            if "NODE_CLASS_MAPPINGS" in local_vars:
                mappings = local_vars["NODE_CLASS_MAPPINGS"]
                display_names = local_vars.get("NODE_DISPLAY_NAME_MAPPINGS", {})
                
                for class_name, node_class in mappings.items():
                    node_info = {
                        "class_name": class_name,
                        "display_name": display_names.get(class_name, class_name),
                        "source_file": "__init__.py",
                        "category": getattr(node_class, "CATEGORY", "未分类") if hasattr(node_class, "CATEGORY") else "未分类"
                    }
                    
                    # 尝试获取更多信息
                    if hasattr(node_class, "RETURN_TYPES"):
                        node_info["return_types"] = str(node_class.RETURN_TYPES)
                    if hasattr(node_class, "FUNCTION"):
                        node_info["function"] = node_class.FUNCTION
                    if hasattr(node_class, "__doc__"):
                        node_info["description"] = (node_class.__doc__ or "").strip().split('\n')[0]
                    
                    nodes.append(node_info)
        
        except Exception as e:
            print(f"[WARNING] 无法解析 {init_file.name}: {str(e)}")
        
        return nodes
    
    def _load_from_file(self, py_file: Path, package_path: Path) -> List[Dict[str, Any]]:
        """从单个 Python 文件加载节点"""
        nodes = []
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否包含节点定义
            if "NODE_CLASS_MAPPINGS" not in content:
                return nodes
            
            # 尝试提取节点类定义（简单的文本分析）
            import re
            
            # 查找 NODE_CLASS_MAPPINGS
            mapping_match = re.search(
                r'NODE_CLASS_MAPPINGS\s*=\s*\{([^}]+)\}',
                content,
                re.DOTALL
            )
            
            if mapping_match:
                mapping_content = mapping_match.group(1)
                # 提取类名
                class_matches = re.findall(r'["\'](\w+)["\']:\s*(\w+)', mapping_content)
                
                # 查找显示名称
                display_match = re.search(
                    r'NODE_DISPLAY_NAME_MAPPINGS\s*=\s*\{([^}]+)\}',
                    content,
                    re.DOTALL
                )
                display_names = {}
                if display_match:
                    display_content = display_match.group(1)
                    display_matches = re.findall(r'["\'](\w+)["\']:\s*["\']([^"\']+)["\']', display_content)
                    display_names = dict(display_matches)
                
                # 为每个类提取信息
                for key, class_name in class_matches:
                    # 查找类定义和 CATEGORY
                    class_pattern = rf'class\s+{class_name}.*?CATEGORY\s*=\s*["\']([^"\']+)["\']'
                    category_match = re.search(class_pattern, content, re.DOTALL)
                    category = category_match.group(1) if category_match else "未分类"
                    
                    # 查找文档字符串
                    doc_pattern = rf'class\s+{class_name}.*?"""(.*?)"""'
                    doc_match = re.search(doc_pattern, content, re.DOTALL)
                    description = doc_match.group(1).strip().split('\n')[0] if doc_match else ""
                    
                    node_info = {
                        "class_name": key,
                        "display_name": display_names.get(key, key),
                        "source_file": str(py_file.relative_to(package_path)),
                        "category": category,
                        "description": description
                    }
                    nodes.append(node_info)
        
        except Exception as e:
            print(f"[WARNING] 解析文件失败 {py_file.name}: {str(e)}")
        
        return nodes
    
    def _format_detailed(self, data: Dict[str, Any], show_categories: bool) -> str:
        """详细格式输出"""
        lines = []
        lines.append("=" * 80)
        lines.append(f"[节点包] {data['package_name']}")
        lines.append(f"[路径] {data['package_path']}")
        lines.append(f"[节点数] {len(data['nodes'])}")
        lines.append(f"[分类数] {len(data['categories'])}")
        lines.append("=" * 80)
        lines.append("")
        
        if show_categories and data["categories"]:
            lines.append("[节点分类]")
            lines.append("-" * 80)
            for category, node_list in sorted(data["categories"].items()):
                lines.append(f"\n[{category}] ({len(node_list)} 个节点)")
                for node_name in sorted(node_list):
                    # 查找完整信息
                    node_data = next((n for n in data["nodes"] if n["class_name"] == node_name), None)
                    if node_data:
                        display = node_data.get("display_name", node_name)
                        desc = node_data.get("description", "")
                        source = node_data.get("source_file", "")
                        
                        lines.append(f"   - {display}")
                        lines.append(f"     类名: {node_name}")
                        if desc:
                            lines.append(f"     描述: {desc}")
                        lines.append(f"     来源: {source}")
            lines.append("")
        
        lines.append("\n" + "=" * 80)
        lines.append("📋 完整节点列表:")
        lines.append("-" * 80)
        
        for i, node in enumerate(data["nodes"], 1):
            lines.append(f"\n{i}. {node.get('display_name', node['class_name'])}")
            lines.append(f"   类名: {node['class_name']}")
            lines.append(f"   分类: {node.get('category', '未分类')}")
            lines.append(f"   文件: {node.get('source_file', 'N/A')}")
            
            if node.get('description'):
                lines.append(f"   描述: {node['description']}")
            if node.get('function'):
                lines.append(f"   函数: {node['function']}")
            if node.get('return_types'):
                lines.append(f"   返回: {node['return_types']}")
        
        if data["errors"]:
            lines.append("\n" + "=" * 80)
            lines.append("[警告] 扫描错误:")
            lines.append("-" * 80)
            for error in data["errors"]:
                lines.append(f"  * {error['file']}: {error['error']}")
        
        lines.append("\n" + "=" * 80)
        
        return "\n".join(lines)
    
    def _format_simple(self, data: Dict[str, Any], show_categories: bool) -> str:
        """简单格式输出"""
        lines = []
        lines.append(f"节点包: {data['package_name']}")
        lines.append(f"节点数: {len(data['nodes'])}")
        lines.append(f"分类数: {len(data['categories'])}\n")
        
        if show_categories:
            for category, node_list in sorted(data["categories"].items()):
                lines.append(f"{category}: {', '.join(sorted(node_list))}")
        else:
            node_names = [node["display_name"] for node in data["nodes"]]
            lines.append(", ".join(sorted(node_names)))
        
        return "\n".join(lines)
    
    def _format_json(self, data: Dict[str, Any]) -> str:
        """JSON 格式输出"""
        return json.dumps(data, ensure_ascii=False, indent=2)


# 节点注册（如果直接导入此文件）
NODE_CLASS_MAPPINGS = {
    "NodePackageLoader": NodePackageLoader
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "NodePackageLoader": "节点包加载器 📦"
}

