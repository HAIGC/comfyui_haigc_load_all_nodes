"""
基础字符串操作节点
Basic String Operation Nodes
"""

class StringConcatenate:
    """连接多个字符串 / Concatenate multiple strings"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "文本1": ("STRING", {"default": "", "multiline": True}),
                "文本2": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "文本3": ("STRING", {"default": "", "multiline": True}),
                "文本4": ("STRING", {"default": "", "multiline": True}),
                "分隔符": ("STRING", {"default": ""}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    FUNCTION = "concatenate"
    CATEGORY = "HAIGC/Text/Basic"
    
    def concatenate(self, 文本1, 文本2, 文本3="", 文本4="", 分隔符=""):
        texts = [文本1, 文本2]
        if 文本3:
            texts.append(文本3)
        if 文本4:
            texts.append(文本4)
        result = 分隔符.join(texts)
        return (result,)


class StringSplit:
    """分割字符串 / Split string"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "文本": ("STRING", {"default": "", "multiline": True}),
                "分隔符": ("STRING", {"default": ","}),
                "索引": ("INT", {"default": 0, "min": -1, "max": 9999}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("结果", "所有部分", "数量")
    FUNCTION = "split"
    CATEGORY = "HAIGC/Text/Basic"
    
    def split(self, 文本, 分隔符, 索引):
        parts = 文本.split(分隔符)
        count = len(parts)
        
        # index = -1 means return all parts joined with newline
        if 索引 == -1:
            result = "\n".join(parts)
        else:
            result = parts[索引] if 索引 < count else ""
        
        all_parts = "\n".join(parts)
        return (result, all_parts, count)


class StringReplace:
    """替换字符串 / Replace string"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "文本": ("STRING", {"default": "", "multiline": True}),
                "旧文本": ("STRING", {"default": ""}),
                "新文本": ("STRING", {"default": ""}),
                "次数": ("INT", {"default": -1, "min": -1, "max": 9999}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    FUNCTION = "replace"
    CATEGORY = "HAIGC/Text/Basic"
    
    def replace(self, 文本, 旧文本, 新文本, 次数):
        if 次数 == -1:
            result = 文本.replace(旧文本, 新文本)
        else:
            result = 文本.replace(旧文本, 新文本, 次数)
        return (result,)


class StringTrim:
    """修剪字符串空白 / Trim string whitespace"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "文本": ("STRING", {"default": "", "multiline": True}),
                "模式": (["两端", "左侧", "右侧", "所有空白"], {"default": "两端"}),
            },
            "optional": {
                "字符": ("STRING", {"default": ""}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    FUNCTION = "trim"
    CATEGORY = "HAIGC/Text/Basic"
    
    def trim(self, 文本, 模式, 字符=""):
        if 模式 == "所有空白":
            result = " ".join(文本.split())
        elif 字符:
            if 模式 == "两端":
                result = 文本.strip(字符)
            elif 模式 == "左侧":
                result = 文本.lstrip(字符)
            elif 模式 == "右侧":
                result = 文本.rstrip(字符)
        else:
            if 模式 == "两端":
                result = 文本.strip()
            elif 模式 == "左侧":
                result = 文本.lstrip()
            elif 模式 == "右侧":
                result = 文本.rstrip()
        return (result,)


class StringLength:
    """获取字符串长度 / Get string length"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "文本": ("STRING", {"default": "", "multiline": True}),
                "模式": (["字符", "单词", "行", "字节"], {"default": "字符"}),
            }
        }
    
    RETURN_TYPES = ("INT", "STRING")
    RETURN_NAMES = ("长度", "信息")
    FUNCTION = "get_length"
    CATEGORY = "HAIGC/Text/Basic"
    
    def get_length(self, 文本, 模式):
        if 模式 == "字符":
            length = len(文本)
        elif 模式 == "单词":
            length = len(文本.split())
        elif 模式 == "行":
            length = len(文本.splitlines())
        elif 模式 == "字节":
            length = len(文本.encode('utf-8'))
        
        info = f"长度: {length} {模式}"
        return (length, info)


class StringRepeat:
    """重复字符串 / Repeat string"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "文本": ("STRING", {"default": ""}),
                "次数": ("INT", {"default": 1, "min": 0, "max": 1000}),
            },
            "optional": {
                "分隔符": ("STRING", {"default": ""}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    FUNCTION = "repeat"
    CATEGORY = "HAIGC/Text/Basic"
    
    def repeat(self, 文本, 次数, 分隔符=""):
        if 分隔符:
            result = 分隔符.join([文本] * 次数)
        else:
            result = 文本 * 次数
        return (result,)


class StringSlice:
    """切片字符串 / Slice string"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "文本": ("STRING", {"default": "", "multiline": True}),
                "起始": ("INT", {"default": 0, "min": -9999, "max": 9999}),
                "结束": ("INT", {"default": -1, "min": -9999, "max": 9999}),
                "步长": ("INT", {"default": 1, "min": -100, "max": 100}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    FUNCTION = "slice"
    CATEGORY = "HAIGC/Text/Basic"
    
    def slice(self, 文本, 起始, 结束, 步长):
        if 结束 == -1:
            result = 文本[起始::步长]
        else:
            result = 文本[起始:结束:步长]
        return (result,)


class StringReverse:
    """反转字符串 / Reverse string"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "文本": ("STRING", {"default": "", "multiline": True}),
                "模式": (["字符", "单词", "行"], {"default": "字符"}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    FUNCTION = "reverse"
    CATEGORY = "HAIGC/Text/Basic"
    
    def reverse(self, 文本, 模式):
        if 模式 == "字符":
            result = 文本[::-1]
        elif 模式 == "单词":
            words = 文本.split()
            result = " ".join(reversed(words))
        elif 模式 == "行":
            lines = 文本.splitlines()
            result = "\n".join(reversed(lines))
        return (result,)


class StringCase:
    """转换字符串大小写 / Convert string case"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "文本": ("STRING", {"default": "", "multiline": True}),
                "模式": ([
                    "全大写", "全小写", "标题", "首字母大写", 
                    "大小写互换", "句子", "驼峰命名", "蛇形命名",
                    "短横线命名", "帕斯卡命名"
                ], {"default": "全小写"}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    FUNCTION = "convert_case"
    CATEGORY = "HAIGC/Text/Basic"
    
    def convert_case(self, 文本, 模式):
        if 模式 == "全大写":
            result = 文本.upper()
        elif 模式 == "全小写":
            result = 文本.lower()
        elif 模式 == "标题":
            result = 文本.title()
        elif 模式 == "首字母大写":
            result = 文本.capitalize()
        elif 模式 == "大小写互换":
            result = 文本.swapcase()
        elif 模式 == "句子":
            sentences = 文本.split('. ')
            result = '. '.join(s.capitalize() for s in sentences)
        elif 模式 == "驼峰命名":
            words = 文本.replace('_', ' ').replace('-', ' ').split()
            result = words[0].lower() + ''.join(w.capitalize() for w in words[1:])
        elif 模式 == "蛇形命名":
            import re
            result = re.sub(r'(?<!^)(?=[A-Z])', '_', 文本).lower()
            result = result.replace(' ', '_').replace('-', '_')
        elif 模式 == "短横线命名":
            import re
            result = re.sub(r'(?<!^)(?=[A-Z])', '-', 文本).lower()
            result = result.replace(' ', '-').replace('_', '-')
        elif 模式 == "帕斯卡命名":
            words = 文本.replace('_', ' ').replace('-', ' ').split()
            result = ''.join(w.capitalize() for w in words)
        
        return (result,)


class StringContains:
    """检查字符串包含 / Check if string contains"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "文本": ("STRING", {"default": "", "multiline": True}),
                "搜索": ("STRING", {"default": ""}),
                "区分大小写": ("BOOLEAN", {"default": True}),
            }
        }
    
    RETURN_TYPES = ("BOOLEAN", "STRING", "INT")
    RETURN_NAMES = ("包含", "结果", "位置")
    FUNCTION = "contains"
    CATEGORY = "HAIGC/Text/Basic"
    
    def contains(self, 文本, 搜索, 区分大小写):
        if not 区分大小写:
            text_check = 文本.lower()
            search_check = 搜索.lower()
        else:
            text_check = 文本
            search_check = 搜索
        
        contains = search_check in text_check
        result = "是" if contains else "否"
        position = text_check.find(search_check)
        
        return (contains, result, position)
