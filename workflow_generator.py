"""
工作流生成器
根据节点包中的节点自动生成包含所有节点的工作流文件
"""

import json
import random
from pathlib import Path
from typing import Tuple, Dict, Any, List, Optional, Set
from .node_package_loader import NodePackageLoader


class WorkflowGenerator:
    """
    工作流生成器
    
    功能：
    - 扫描节点包获取所有节点
    - 自动生成包含所有节点的工作流 JSON
    - 智能布局节点位置
    - 支持保存到文件或输出 JSON 字符串
    
    输入：
    - package_path: 节点包路径
    - layout_type: 布局类型（grid/vertical/horizontal）
    - spacing: 节点间距
    - save_to_file: 是否保存到文件
    - output_path: 输出文件路径
    
    输出：
    - workflow_json: 工作流 JSON 字符串
    - node_count: 节点数量
    - file_path: 保存的文件路径
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "package_path": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "输入节点包路径",
                    "label": "节点包路径"
                }),
                "layout_type": (["grid", "vertical", "horizontal", "compact"], {
                    "default": "grid",
                    "label": "布局类型"
                }),
                "spacing_x": ("INT", {
                    "default": 450,
                    "min": 200,
                    "max": 1500,
                    "step": 50,
                    "display": "number",
                    "label": "水平间距"
                }),
                "spacing_y": ("INT", {
                    "default": 300,
                    "min": 150,
                    "max": 1000,
                    "step": 50,
                    "display": "number",
                    "label": "垂直间距"
                }),
                "save_to_file": ("BOOLEAN", {
                    "default": True,
                    "label_on": "保存文件",
                    "label_off": "仅输出",
                    "label": "保存到文件"
                }),
            },
            "optional": {
                "output_path": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "留空则自动生成文件名",
                    "label": "输出路径"
                }),
                "filter_category": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "填写关键词进行分类筛选",
                    "label": "分类筛选"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "INT", "STRING")
    RETURN_NAMES = ("workflow_json", "node_count", "json_path")
    FUNCTION = "generate_workflow"
    CATEGORY = "haigc_toolkit/utils"
    OUTPUT_NODE = True
    
    def generate_workflow(
        self,
        package_path: str,
        layout_type: str = "grid",
        spacing_x: int = 450,
        spacing_y: int = 300,
        save_to_file: bool = True,
        output_path: str = "",
        filter_category: str = "",
        seed: Optional[int] = None
    ) -> Tuple[str, int, str]:
        """
        生成工作流
        
        Args:
            package_path: 节点包路径
            layout_type: 布局类型
            spacing_x: 水平间距
            spacing_y: 垂直间距
            save_to_file: 是否保存 JSON 文件
            output_path: 输出文件路径
            filter_category: 分类筛选
            seed: 随机种子（None 表示不启用随机）
            
        Returns:
            (工作流JSON, 节点数量, JSON文件路径)
        """
        try:
            print("\n" + "="*60)
            print("[工作流生成器] 开始生成工作流")
            print("="*60)
            
            # 使用节点包加载器扫描节点
            loader = NodePackageLoader()
            result = loader.load_nodes(
                package_path=package_path,
                output_format="json",
                scan_subdirs=True,
                show_categories=False,
                filter_category=filter_category
            )
            
            nodes_info_json = result[0]
            node_count = result[1]
            
            if node_count == 0:
                error_msg = "[ERROR] 未找到任何节点"
                return (error_msg, 0, "")
            
            # 解析节点数据
            nodes_data = json.loads(nodes_info_json)
            nodes_list = nodes_data.get("nodes", [])
            package_name = nodes_data.get("package_name", "unknown")
            
            print(f"[信息] 找到 {len(nodes_list)} 个节点")
            print(f"[布局] 使用 {layout_type} 布局")
            print(f"[间距] X={spacing_x}px, Y={spacing_y}px")
            if seed is not None:
                print(f"[随机] 使用种子 {seed}")
            else:
                print("[随机] 未启用，按默认顺序布局")
            
            # 生成工作流
            workflow = self._create_workflow(
                nodes_list,
                layout_type,
                spacing_x,
                spacing_y,
                seed=seed
            )
            
            # 转换为 JSON 字符串
            workflow_json = json.dumps(workflow, ensure_ascii=False, indent=2)
            
            # 保存文件
            json_path = ""
            if save_to_file:
                json_path = self._save_workflow(
                    workflow,
                    package_name,
                    output_path
                )
                print(f"[保存] JSON: {json_path}")
            
            print(f"[完成] 工作流生成完成")
            print("="*60 + "\n")
            
            return (workflow_json, len(nodes_list), json_path)
            
        except Exception as e:
            error_msg = f"[ERROR] 生成失败: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            return (error_msg, 0, "")
    
    def _create_workflow(
        self,
        nodes_list: List[Dict],
        layout_type: str,
        spacing_x: int,
        spacing_y: int,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """创建工作流数据结构"""
        
        nodes_order = list(nodes_list)
        rng: Optional[random.Random] = None
        if seed is not None:
            rng = random.Random(seed)
            rng.shuffle(nodes_order)
        
        total_nodes = len(nodes_order)
        
        workflow = {
            "last_node_id": total_nodes,
            "last_link_id": 0,
            "nodes": [],
            "links": [],
            "groups": [],
            "config": {},
            "extra": {
                "ds": {
                    "scale": 0.8,
                    "offset": [0, 0]
                }
            },
            "version": 0.4
        }
        
        # 根据布局类型计算位置
        for idx, node_info in enumerate(nodes_order):
            position = self._calculate_position(
                idx,
                total_nodes,
                layout_type,
                spacing_x,
                spacing_y
            )
            
            node_data = {
                "id": idx + 1,
                "type": node_info["class_name"],
                "class_type": node_info["class_name"],
                "pos": position,
                "size": [280, 120],
                "flags": {},
                "order": idx,
                "mode": 0,
                "inputs": [],
                "outputs": [],
                "properties": {
                    "Node name for S&R": node_info["class_name"]
                },
                "widgets_values": []
            }
            
            # 添加注释
            if node_info.get("description"):
                node_data["properties"]["description"] = node_info["description"]
            
            workflow["nodes"].append(node_data)
        
        return workflow
    
    def _calculate_position(
        self,
        index: int,
        total: int,
        layout_type: str,
        spacing_x: int,
        spacing_y: int
    ) -> List[int]:
        """计算节点位置"""
        
        start_x = 50
        start_y = 50
        
        if layout_type == "grid":
            # 网格布局：自动计算列数
            cols = max(3, int((total ** 0.5) + 0.5))
            row = index // cols
            col = index % cols
            x = start_x + col * spacing_x
            y = start_y + row * spacing_y
            
        elif layout_type == "vertical":
            # 垂直布局：单列
            x = start_x
            y = start_y + index * spacing_y
            
        elif layout_type == "horizontal":
            # 水平布局：单行
            x = start_x + index * spacing_x
            y = start_y
            
        elif layout_type == "compact":
            # 紧凑布局：更小的间距，更多列
            cols = max(5, int((total ** 0.5) * 1.5))
            row = index // cols
            col = index % cols
            x = start_x + col * (spacing_x * 0.7)
            y = start_y + row * (spacing_y * 0.7)
        
        else:
            # 默认网格
            cols = 3
            row = index // cols
            col = index % cols
            x = start_x + col * spacing_x
            y = start_y + row * spacing_y
        
        return [int(x), int(y)]
    
    def _save_workflow(
        self,
        workflow: Dict[str, Any],
        package_name: str,
        output_path: str
    ) -> str:
        """保存工作流到文件"""
        
        # 确定输出路径
        if output_path and output_path.strip():
            file_path = Path(output_path)
        else:
            # 自动生成文件名
            possible_dirs = self.get_workflow_directories()
            
            # 选择第一个可创建的目录
            workflows_dir = None
            for dir_path in possible_dirs:
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    workflows_dir = dir_path
                    break
                except:
                    continue
            
            # 如果都失败，使用当前目录
            if workflows_dir is None:
                workflows_dir = Path(__file__).parent / "workflows"
                workflows_dir.mkdir(parents=True, exist_ok=True)
            
            file_name = f"workflow_{package_name}_all_nodes.json"
            file_path = workflows_dir / file_name
        
        # 确保目录存在
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(workflow, f, ensure_ascii=False, indent=2)
        
        return str(file_path.absolute())

    def get_workflow_directories(self) -> List[Path]:
        """返回保存工作流时使用的目录列表（按优先级排序）"""
        comfyui_root = Path(__file__).parent.parent.parent
        dirs = [
            comfyui_root / "user" / "default" / "workflows",
            comfyui_root / "output" / "workflows",
            Path(__file__).parent / "workflows",
        ]
        unique_dirs: List[Path] = []
        seen: Set[str] = set()
        for dir_path in dirs:
            key = str(dir_path.resolve()) if dir_path.exists() else str(dir_path)
            if key not in seen:
                seen.add(key)
                unique_dirs.append(dir_path)
        return unique_dirs
    
    def delete_workflows(self, prefix: str = "", keyword: str = "") -> List[str]:
        """
        删除已有的工作流 JSON 文件。
        
        Args:
            prefix: 文件名需匹配的前缀（可选）
            keyword: 文件名需包含的关键字（可选）
            
        Returns:
            删除成功的文件路径列表
        """
        prefix = prefix.strip()
        keyword = keyword.strip()
        if not prefix and not keyword:
            return []
        
        deleted: List[str] = []
        for dir_path in self.get_workflow_directories():
            if not dir_path.exists():
                continue
            for file_path in dir_path.glob("*.json"):
                name = file_path.name
                if prefix and not name.startswith(prefix):
                    continue
                if keyword and keyword not in name:
                    continue
                try:
                    file_path.unlink()
                    deleted.append(str(file_path))
                    print(f"[删除] 已移除旧工作流: {file_path}")
                except Exception as err:
                    print(f"[警告] 无法删除 {file_path}: {err}")
        return deleted
    


class WorkflowFromList:
    """
    从节点列表生成工作流
    
    直接输入节点类名列表，生成包含这些节点的工作流
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "node_class_names": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "placeholder": "输入节点类名，每行一个\n例如:\nLoadImage\nSaveImage\nKSampler"
                }),
                "layout_type": (["grid", "vertical", "horizontal", "compact"], {
                    "default": "grid"
                }),
                "spacing_x": ("INT", {
                    "default": 450,
                    "min": 200,
                    "max": 1500,
                    "step": 50
                }),
                "spacing_y": ("INT", {
                    "default": 300,
                    "min": 150,
                    "max": 1000,
                    "step": 50
                }),
                "save_to_file": ("BOOLEAN", {
                    "default": True
                }),
            },
            "optional": {
                "output_path": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "INT", "STRING")
    RETURN_NAMES = ("workflow_json", "node_count", "file_path")
    FUNCTION = "generate_workflow"
    CATEGORY = "haigc_toolkit/utils"
    OUTPUT_NODE = True
    
    def generate_workflow(
        self,
        node_class_names: str,
        layout_type: str = "grid",
        spacing_x: int = 450,
        spacing_y: int = 300,
        save_to_file: bool = True,
        output_path: str = ""
    ) -> Tuple[str, int, str]:
        """从节点列表生成工作流"""
        
        try:
            # 解析节点类名列表
            class_names = [
                name.strip()
                for name in node_class_names.strip().split('\n')
                if name.strip()
            ]
            
            if not class_names:
                return ("[ERROR] 节点列表为空", 0, "")
            
            print(f"\n[工作流生成] 从 {len(class_names)} 个节点类名生成工作流")
            
            # 转换为节点信息格式
            nodes_list = [
                {
                    "class_name": name,
                    "display_name": name,
                    "category": "custom",
                    "source_file": "manual_input"
                }
                for name in class_names
            ]
            
            # 创建生成器实例
            generator = WorkflowGenerator()
            
            # 创建工作流
            workflow = generator._create_workflow(
                nodes_list,
                layout_type,
                spacing_x,
                spacing_y,
                seed=None
            )
            
            workflow_json = json.dumps(workflow, ensure_ascii=False, indent=2)
            
            # 保存文件
            saved_path = ""
            if save_to_file:
                saved_path = generator._save_workflow(
                    workflow,
                    "custom_nodes",
                    output_path
                )
                print(f"[保存] 工作流已保存: {saved_path}")
            
            print(f"[完成] 工作流生成完成\n")
            
            return (workflow_json, len(class_names), saved_path)
            
        except Exception as e:
            error_msg = f"[ERROR] 生成失败: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            return (error_msg, 0, "")


# 节点注册
NODE_CLASS_MAPPINGS = {
    "WorkflowGenerator": WorkflowGenerator,
    "WorkflowFromList": WorkflowFromList,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WorkflowGenerator": "工作流生成器 🎨",
    "WorkflowFromList": "从列表生成工作流 📝",
}

