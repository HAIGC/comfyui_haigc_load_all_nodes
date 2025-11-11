"""
按名称加载节点 - 无需输入路径，直接选择节点包名称
"""

from pathlib import Path
import json
from typing import Tuple, List, Dict, Any, Optional
from .workflow_generator import WorkflowGenerator


class QuickLoadByName:
    """
    按名称加载节点
    
    功能：
    - 自动扫描 custom_nodes 目录
    - 下拉菜单选择节点包
    - 无需手动输入路径
    - 一键生成工作流
    """
    
    @classmethod
    def get_custom_nodes_list(cls) -> List[str]:
        """获取所有已安装的自定义节点包列表"""
        try:
            # 获取 custom_nodes 目录
            current_file = Path(__file__)
            custom_nodes_dir = current_file.parent.parent
            
            if not custom_nodes_dir.exists():
                return ["(未找到节点包)"]
            
            # 扫描所有子目录
            node_packages = []
            for item in custom_nodes_dir.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    # 检查是否是有效的节点包（包含 __init__.py 或 Python 文件）
                    has_init = (item / "__init__.py").exists()
                    has_py = any(item.glob("*.py"))
                    
                    if has_init or has_py:
                        node_packages.append(item.name)
            
            # 排序并返回
            node_packages.sort()
            
            if not node_packages:
                return ["(未找到节点包)"]
            
            return node_packages
            
        except Exception as e:
            print(f"[ERROR] 获取节点包列表失败: {e}")
            return ["(扫描失败)"]
    
    @classmethod
    def INPUT_TYPES(cls):
        node_packages = ["无", "全部"] + cls.get_custom_nodes_list()
        presets = cls.load_cleanup_presets()
        preset_names = ["无"] + sorted(presets.keys())
        
        return {
            "required": {
                "节点包名称": (node_packages, {
                    "default": node_packages[0] if node_packages else "无"
                }),
                "布局模式": (["智能布局", "紧凑布局", "宽松布局"], {
                    "default": "智能布局"
                }),
                "刷新节点列表": ("BOOLEAN", {
                    "default": False
                }),
            },
            "optional": {
                "分类筛选": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
                "删除预设": (preset_names, {
                    "default": preset_names[1] if len(preset_names) > 1 else "无"
                }),
                "删除前缀": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "输入文件名前缀以删除旧工作流"
                }),
                "删除关键字": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "输入关键字以删除旧工作流"
                }),
                "添加预设": ("BOOLEAN", {
                    "default": False
                }),
                "新预设名称": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
                "新预设前缀": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
                "新预设关键字": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
                "删除预设名称": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "INT")
    RETURN_NAMES = ("工作流JSON", "JSON路径", "操作说明", "节点数量")
    FUNCTION = "quick_load_by_name"
    CATEGORY = "haigc_toolkit/utils"
    OUTPUT_NODE = True
    
    def quick_load_by_name(self, **inputs: Any) -> Tuple[str, str, str, int]:
        """
        按名称加载节点
        
        Returns:
            (工作流JSON, JSON路径, 使用说明, 节点数量)
        """
        try:
            # 读取中英文参数（兼容旧版本）
            node_package = inputs.get("节点包名称") or inputs.get("node_package") or ""
            mode = inputs.get("布局模式") or inputs.get("mode") or "智能布局"
            refresh_list = inputs.get("刷新节点列表")
            if refresh_list is None:
                refresh_list = inputs.get("refresh_list", False)
            filter_category = inputs.get("分类筛选") or inputs.get("filter_category") or ""
            preset_name = inputs.get("删除预设") or inputs.get("cleanup_preset") or "无"
            add_preset = inputs.get("添加预设") or inputs.get("add_preset", False)
            new_preset_name = inputs.get("新预设名称") or inputs.get("new_preset_name", "")
            new_preset_prefix = inputs.get("新预设前缀") or inputs.get("new_preset_prefix", "")
            new_preset_keyword = inputs.get("新预设关键字") or inputs.get("new_preset_keyword", "")
            remove_preset_name = inputs.get("删除预设名称") or inputs.get("remove_preset_name", "")
            cleanup_prefix = inputs.get("删除前缀") or inputs.get("cleanup_prefix") or ""
            cleanup_keyword = inputs.get("删除关键字") or inputs.get("cleanup_keyword") or ""
            
            presets = self.load_cleanup_presets()
            
            if add_preset and new_preset_name.strip():
                presets[new_preset_name.strip()] = {
                    "prefix": new_preset_prefix.strip(),
                    "keyword": new_preset_keyword.strip()
                }
                self.save_cleanup_presets(presets)
                print(f"[预设] 已新增/更新预设: {new_preset_name.strip()}")
                preset_name = new_preset_name.strip()
            
            if remove_preset_name.strip():
                if remove_preset_name.strip() in presets:
                    presets.pop(remove_preset_name.strip())
                    self.save_cleanup_presets(presets)
                    print(f"[预设] 已删除预设: {remove_preset_name.strip()}")
                    if preset_name == remove_preset_name.strip():
                        preset_name = "无"
            
            if preset_name != "无":
                preset_data = presets.get(preset_name, {})
                if preset_data:
                    if not cleanup_prefix:
                        cleanup_prefix = preset_data.get("prefix", "")
                    if not cleanup_keyword:
                        cleanup_keyword = preset_data.get("keyword", "")
            
            print("\n" + "="*70)
            print("[按名称加载] 快速加载模式".center(70))
            print("="*70)
            
            # 验证选择
            if node_package in ["(未找到节点包)", "(扫描失败)"]:
                error = "[错误] 请选择有效的节点包"
                return ("", "", error, 0)
            
            cleanup_prefix = cleanup_prefix.strip()
            cleanup_keyword = cleanup_keyword.strip()
            
            # 使用工作流生成器
            generator = WorkflowGenerator()
            
            deleted_files: List[str] = []
            if cleanup_prefix or cleanup_keyword:
                print("\n[清理] 正在删除旧工作流文件...")
                deleted_files = generator.delete_workflows(
                    prefix=cleanup_prefix,
                    keyword=cleanup_keyword
                )
                print(f"[清理] 删除匹配文件 {len(deleted_files)} 个")
            
            # 获取布局配置
            layout_config = self._get_layout_config(mode)
            layout_label = layout_config.get("label", mode)
            
            # 根据选择处理不同情况
            generated_results: List[Tuple[str, int, str]] = []
            
            if node_package == "无":
                print("\n[提示] 未选择节点包，仅执行清理操作。")
            elif node_package == "全部":
                # 批量处理所有节点包
                all_packages = self.get_custom_nodes_list()
                print(f"\n[目标] 批量处理 {len(all_packages)} 个节点包")
                
                print(f"\n[布局] 模式: {layout_label}")
                print(f"   - 类型: {layout_config['type']}")
                print(f"   - 间距: {layout_config['spacing_x']}x{layout_config['spacing_y']}px")
                
                for pkg in all_packages:
                    pkg_path = self._get_package_path(pkg)
                    if not pkg_path or not pkg_path.exists():
                        print(f"[警告] 节点包路径无效，跳过: {pkg}")
                        continue
                    
                    print(f"\n[目标] 节点包: {pkg}")
                    print(f"[路径] {pkg_path}")
                    if filter_category:
                        print(f"[筛选] 分类: {filter_category}")
                    
                    print("\n[扫描] 正在扫描节点...")
                    
                    try:
                        result = generator.generate_workflow(
                            package_path=str(pkg_path),
                            layout_type=layout_config['type'],
                            spacing_x=layout_config['spacing_x'],
                            spacing_y=layout_config['spacing_y'],
                            save_to_file=True,
                            output_path="",
                            filter_category=filter_category,
                            seed=None
                        )
                        
                        workflow_json, node_count, json_path = result
                        
                        if node_count == 0:
                            print(f"[警告] 未找到节点，跳过: {pkg}")
                            continue
                        
                        print(f"\n[成功] 生成工作流完成！")
                        print(f"   - 节点数量: {node_count}")
                        print(f"   - JSON: {json_path}")
                        
                        generated_results.append((workflow_json, node_count, json_path))
                    except Exception as e:
                        print(f"[错误] 处理节点包失败 {pkg}: {e}")
                        continue
            else:
                # 单个节点包
                package_path = self._get_package_path(node_package)
                if not package_path or not package_path.exists():
                    error = f"[错误] 节点包路径无效: {node_package}"
                    print(f"\n{error}")
                    return ("", "", error, 0)
                
                print(f"\n[目标] 节点包: {node_package}")
                print(f"[路径] {package_path}")
                if filter_category:
                    print(f"[筛选] 分类: {filter_category}")
                
                print(f"\n[布局] 模式: {layout_label}")
                print(f"   - 类型: {layout_config['type']}")
                print(f"   - 间距: {layout_config['spacing_x']}x{layout_config['spacing_y']}px")
                
                print("\n[扫描] 正在扫描节点...")
                
                result = generator.generate_workflow(
                    package_path=str(package_path),
                    layout_type=layout_config['type'],
                    spacing_x=layout_config['spacing_x'],
                    spacing_y=layout_config['spacing_y'],
                    save_to_file=True,
                    output_path="",
                    filter_category=filter_category,
                    seed=None
                )
                
                workflow_json, node_count, json_path = result
                
                if node_count == 0:
                    error = "[错误] 未找到任何节点"
                    print(f"\n{error}")
                    return ("", "", error, 0)
                
                print(f"\n[成功] 生成工作流完成！")
                print(f"   - 节点数量: {node_count}")
                print(f"   - JSON: {json_path}")
                
                generated_results.append((workflow_json, node_count, json_path))
            
            # 处理输出
            if generated_results:
                if node_package == "全部":
                    # 返回批量生成的汇总信息
                    total_nodes = sum(res[1] for res in generated_results)
                    json_paths_list = [res[2] for res in generated_results]
                    workflow_json = ""  # 批量模式不返回单个工作流JSON
                    json_path = "\n".join(json_paths_list)
                else:
                    # 返回单个节点包的结果
                    workflow_json, node_count, json_path = generated_results[0]
                    total_nodes = node_count
                
                instructions = self._generate_instructions(
                    json_path=json_path,
                    package_name=node_package,
                    node_count=total_nodes,
                    deleted_files=deleted_files,
                    cleanup_prefix=cleanup_prefix,
                    cleanup_keyword=cleanup_keyword,
                    preset_name=preset_name,
                    generated=True,
                    batch_results=generated_results if node_package == "全部" else None
                )
                
                return (workflow_json, json_path, instructions, total_nodes)
            else:
                # 没有生成任何工作流（可能是选择了"无"或全部失败）
                instructions = self._generate_instructions(
                    json_path="",
                    package_name=node_package,
                    node_count=0,
                    deleted_files=deleted_files,
                    cleanup_prefix=cleanup_prefix,
                    cleanup_keyword=cleanup_keyword,
                    preset_name=preset_name,
                    generated=False,
                    batch_results=None
                )
                
                return ("", "", instructions, 0)
            
        except Exception as e:
            error_msg = f"[错误] 加载失败: {str(e)}"
            print(f"\n{error_msg}")
            import traceback
            traceback.print_exc()
            return ("", "", error_msg, 0)
    
    def _get_package_path(self, package_name: str) -> Path:
        """根据包名获取完整路径"""
        try:
            current_file = Path(__file__)
            custom_nodes_dir = current_file.parent.parent
            package_path = custom_nodes_dir / package_name
            return package_path
        except Exception as e:
            print(f"[ERROR] 获取路径失败: {e}")
            return None
    
    def _get_layout_config(self, mode: str) -> Dict[str, Any]:
        """获取布局配置"""
        mode_key = {
            "智能布局": "smart",
            "紧凑布局": "compact",
            "宽松布局": "spacious"
        }.get(mode, "smart")
        
        configs = {
            "smart": {
                "type": "grid",
                "spacing_x": 450,
                "spacing_y": 300,
                "description": "智能网格布局，适合大多数情况",
                "label": "智能布局"
            },
            "compact": {
                "type": "compact",
                "spacing_x": 350,
                "spacing_y": 220,
                "description": "紧凑布局，节省空间",
                "label": "紧凑布局"
            },
            "spacious": {
                "type": "grid",
                "spacing_x": 550,
                "spacing_y": 350,
                "description": "宽松布局，节点间距大",
                "label": "宽松布局"
            }
        }
        return configs.get(mode_key, configs["smart"])
    
    def _generate_instructions(
        self,
        json_path: str,
        package_name: str,
        node_count: int,
        deleted_files: Optional[List[str]],
        cleanup_prefix: str,
        cleanup_keyword: str,
        preset_name: str,
        generated: bool,
        batch_results: Optional[List[Tuple[str, int, str]]] = None
    ) -> str:
        """生成使用说明"""
        deleted_files = deleted_files or []
        
        lines = [
            f"[包名] {package_name}",
            f"[节点] {node_count} 个",
        ]
        if preset_name and preset_name != "无":
            lines.append(f"[预设] {preset_name}")
        
        if cleanup_prefix or cleanup_keyword:
            lines.append("")
            lines.append("[清理]")
            condition = []
            if cleanup_prefix:
                condition.append(f"前缀='{cleanup_prefix}'")
            if cleanup_keyword:
                condition.append(f"包含='{cleanup_keyword}'")
            lines.append("条件: " + " 且 ".join(condition))
            lines.append(f"删除 {len(deleted_files)} 个匹配文件")
            preview = deleted_files[:5]
            for path in preview:
                lines.append(f"  - {Path(path).name}")
            if len(deleted_files) > len(preview):
                lines.append("  ...")
        
        if generated:
            if batch_results and len(batch_results) > 0:
                # 批量生成模式
                lines.extend([
                    "",
                    "[批量生成]",
                    f"成功生成 {len(batch_results)} 个工作流文件"
                ])
                for idx, (_, count, path) in enumerate(batch_results, 1):
                    pkg_name = Path(path).stem.replace("workflow_", "").replace("_all_nodes", "")
                    lines.append(f"{idx}. {pkg_name}: {count} 个节点")
                    lines.append(f"   {path}")
                
                lines.extend([
                    "",
                    "[导入方法]",
                    "方法 1: 使用 JSON 文件",
                    "  1. 点击右上角的 'Load' 按钮",
                    "  2. 选择上面列出的任意 JSON 文件",
                    "",
                    "方法 2: 批量导入",
                    "  - 可以依次加载多个工作流文件",
                    "  - 每个文件包含对应节点包的所有节点"
                ])
            elif json_path:
                # 单个文件生成模式
                lines.extend([
                    "",
                    "[文件位置]",
                    "workflow_json: （节点输出，可继续传递）",
                    f"JSON: {json_path}",
                    "",
                    "[导入方法]",
                    "方法 1: 使用 JSON 文件",
                    "  1. 点击右上角的 'Load' 按钮",
                    "  2. 选择上面的 JSON 文件",
                    "",
                    "方法 2: 使用 workflow_json 输出",
                    "  - 将 workflow_json 连接到保存节点（JSON）",
                    "  - 或传递给自定义处理节点"
                ])
        else:
            lines.extend([
                "",
                "[文件位置]",
                "本次未生成新工作流（仅执行清理）"
            ])
        
        return "\n".join(lines)

    @staticmethod
    def load_cleanup_presets() -> Dict[str, Dict[str, str]]:
        """加载删除预设，若不存在则创建默认预设"""
        preset_path = Path(__file__).parent / "cleanup_presets.json"
        if not preset_path.exists():
            presets = {"workflow": {"prefix": "workflow", "keyword": ""}}
            preset_path.write_text(json.dumps(presets, ensure_ascii=False, indent=2), encoding="utf-8")
            return presets
        try:
            data = json.loads(preset_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
            raise ValueError("预设文件格式无效")
        except Exception as exc:
            print(f"[警告] 读取预设失败: {exc}，使用默认预设")
            return {"workflow": {"prefix": "workflow", "keyword": ""}}

    @staticmethod
    def save_cleanup_presets(presets: Dict[str, Dict[str, str]]) -> None:
        """保存删除预设"""
        preset_path = Path(__file__).parent / "cleanup_presets.json"
        preset_path.write_text(json.dumps(presets, ensure_ascii=False, indent=2), encoding="utf-8")


NODE_CLASS_MAPPINGS = {
    "QuickLoadByName": QuickLoadByName,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "QuickLoadByName": "按名称加载节点 📝",
}

