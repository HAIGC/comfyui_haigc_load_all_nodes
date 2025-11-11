## 节点概览

### QuickLoadByName · 按名称加载节点 📝

- 通过下拉菜单选择 `custom_nodes` 下的节点包
- 自动调用工作流生成器生成包含所有节点的工作流 JSON
- 支持 `smart`、`compact`、`spacious` 三种布局
- 可选分类筛选
- 提供清理预设，可按预设或自定义前缀/关键字删除旧工作流文件，默认提供 `workflow` 预设并支持在 UI 中新增/删除预设
- 节点包名称支持以下选项：
  - **无**：仅执行清理操作，不生成新工作流
  - **全部**：批量处理所有节点包，为每个节点包单独生成工作流文件
  - **具体节点包名称**：为选定的节点包生成工作流
- 输出项：
  - `工作流JSON`：生成的工作流 JSON 字符串（单个节点包模式）
  - `JSON路径`：保存的 JSON 文件路径（批量模式下返回多个路径，换行分隔）
  - `操作说明`：导入工作流的提示文本
  - `节点数量`：扫描到的节点总数

#### 使用步骤
1. 在 ComfyUI 中添加 `QuickLoadByName` 节点。
2. 选择目标节点包名称与布局模式：
   - 选择 "无" 仅清理历史文件
   - 选择 "全部" 批量生成所有节点包的工作流
   - 选择具体节点包名称生成单个工作流
3. 运行节点，按照输出的说明导入生成的工作流文件或查看清理结果。

## 安装
```bash
cd ComfyUI/custom_nodes
git clone <repo-url> haigc_load_all_nodes
```
重启 ComfyUI 后即可使用。

## 典型使用场景

### 场景 1：生成单个节点包工作流
```
[QuickLoadByName(节点包名称="ComfyMath")]
```
为特定节点包生成工作流文件到 `ComfyUI/workflows` 目录

### 场景 2：批量生成所有节点包工作流
```
[QuickLoadByName(节点包名称="全部")]
```
自动为所有节点包生成工作流文件到 `ComfyUI/workflows` 目录

### 场景 3：清理旧工作流
```
[QuickLoadByName(节点包名称="无", 删除预设="workflow")]
```
# 删除所有以 "workflow" 开头的旧工作流文件
# 刷新网页即可在工作流列表显示加载的节点包工作流

## 目录结构
- `__init__.py`：节点注册入口，仅导出 `QuickLoadByName`
- `quick_load_by_name.py`：节点逻辑实现
- `workflow_generator.py`：内部工作流构建逻辑
- `node_package_loader.py`：扫描节点包的辅助工具
- `cleanup_presets.json`：清理预设配置文件

