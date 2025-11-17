"""
高级字符串操作节点
Advanced String Operation Nodes
"""
import re


class StringRegexReplace:
    """正则表达式替换 / Regex replace"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "文本": ("STRING", {"default": "", "multiline": True}),
                "正则表达式": ("STRING", {"default": ""}),
                "替换为": ("STRING", {"default": ""}),
                "标志": (["无", "忽略大小写", "多行", "匹配所有", "忽略大小写|多行"], {"default": "无"}),
            }
        }
    
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("结果", "数量")
    FUNCTION = "regex_replace"
    CATEGORY = "HAIGC/Text/Advanced"
    
    def regex_replace(self, 文本, 正则表达式, 替换为, 标志):
        flag_value = 0
        if "忽略大小写" in 标志:
            flag_value |= re.IGNORECASE
        if "多行" in 标志:
            flag_value |= re.MULTILINE
        if "匹配所有" in 标志:
            flag_value |= re.DOTALL
        
        try:
            result, count = re.subn(正则表达式, 替换为, 文本, flags=flag_value)
            return (result, count)
        except re.error as e:
            return (f"正则错误: {str(e)}", 0)


class StringRegexMatch:
    """正则表达式匹配 / Regex match"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "文本": ("STRING", {"default": "", "multiline": True}),
                "正则表达式": ("STRING", {"default": ""}),
                "模式": (["第一个", "所有", "捕获组"], {"default": "第一个"}),
                "标志": (["无", "忽略大小写", "多行", "匹配所有"], {"default": "无"}),
            }
        }
    
    RETURN_TYPES = ("STRING", "INT", "BOOLEAN")
    RETURN_NAMES = ("匹配结果", "数量", "找到")
    FUNCTION = "regex_match"
    CATEGORY = "HAIGC/Text/Advanced"
    
    def regex_match(self, 文本, 正则表达式, 模式, 标志):
        flag_value = 0
        if 标志 == "忽略大小写":
            flag_value = re.IGNORECASE
        elif 标志 == "多行":
            flag_value = re.MULTILINE
        elif 标志 == "匹配所有":
            flag_value = re.DOTALL
        
        try:
            if 模式 == "第一个":
                match = re.search(正则表达式, 文本, flags=flag_value)
                if match:
                    result = match.group(0)
                    return (result, 1, True)
                else:
                    return ("", 0, False)
            
            elif 模式 == "所有":
                matches = re.findall(正则表达式, 文本, flags=flag_value)
                count = len(matches)
                result = "\n".join(str(m) for m in matches)
                return (result, count, count > 0)
            
            elif 模式 == "捕获组":
                match = re.search(正则表达式, 文本, flags=flag_value)
                if match:
                    groups = match.groups()
                    result = "\n".join(str(g) for g in groups)
                    return (result, len(groups), True)
                else:
                    return ("", 0, False)
        
        except re.error as e:
            return (f"正则错误: {str(e)}", 0, False)


class StringRegexSplit:
    """正则表达式分割 / Regex split"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True}),
                "pattern": ("STRING", {"default": r"\s+"}),
                "max_split": ("INT", {"default": 0, "min": 0, "max": 1000}),
            }
        }
    
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("result", "count")
    FUNCTION = "regex_split"
    CATEGORY = "HAIGC/Text/Advanced"
    
    def regex_split(self, text, pattern, max_split):
        try:
            if max_split == 0:
                parts = re.split(pattern, text)
            else:
                parts = re.split(pattern, text, maxsplit=max_split)
            
            result = "\n".join(parts)
            count = len(parts)
            return (result, count)
        except re.error as e:
            return (f"Regex Error: {str(e)}", 0)


class StringFormat:
    """格式化字符串 / Format string"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "template": ("STRING", {"default": "Hello {name}!", "multiline": True}),
            },
            "optional": {
                "arg1": ("STRING", {"default": ""}),
                "arg2": ("STRING", {"default": ""}),
                "arg3": ("STRING", {"default": ""}),
                "arg4": ("STRING", {"default": ""}),
                "arg5": ("STRING", {"default": ""}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    FUNCTION = "format_string"
    CATEGORY = "HAIGC/Text/Advanced"
    
    def format_string(self, template, arg1="", arg2="", arg3="", arg4="", arg5=""):
        try:
            # Try positional formatting first
            args = [arg for arg in [arg1, arg2, arg3, arg4, arg5] if arg]
            try:
                result = template.format(*args)
            except (IndexError, KeyError):
                # Try named formatting
                kwargs = {}
                for i, arg in enumerate(args, 1):
                    kwargs[f"arg{i}"] = arg
                    # Also try common names
                    if i == 1:
                        kwargs["name"] = arg
                        kwargs["value"] = arg
                        kwargs["text"] = arg
                result = template.format(**kwargs)
            
            return (result,)
        except Exception as e:
            return (f"Format Error: {str(e)}",)


class StringTemplate:
    """模板字符串 / Template string with variables"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "template": ("STRING", {"default": "Hello $name!", "multiline": True}),
                "variables": ("STRING", {"default": "name=World", "multiline": True}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    FUNCTION = "apply_template"
    CATEGORY = "HAIGC/Text/Advanced"
    
    def apply_template(self, template, variables):
        try:
            # Parse variables (format: key=value, one per line)
            var_dict = {}
            for line in variables.strip().split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    var_dict[key.strip()] = value.strip()
            
            # Replace variables in template
            from string import Template
            t = Template(template)
            result = t.safe_substitute(var_dict)
            
            return (result,)
        except Exception as e:
            return (f"Template Error: {str(e)}",)


class StringJoin:
    """连接字符串列表 / Join string list"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True}),
                "separator": ("STRING", {"default": ", "}),
                "prefix": ("STRING", {"default": ""}),
                "suffix": ("STRING", {"default": ""}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    FUNCTION = "join_strings"
    CATEGORY = "HAIGC/Text/Advanced"
    
    def join_strings(self, text, separator, prefix, suffix):
        lines = text.strip().split('\n')
        lines = [line.strip() for line in lines if line.strip()]
        
        result = separator.join(lines)
        if prefix:
            result = prefix + result
        if suffix:
            result = result + suffix
        
        return (result,)


class StringPad:
    """填充字符串 / Pad string"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": ""}),
                "width": ("INT", {"default": 10, "min": 0, "max": 1000}),
                "mode": (["left", "right", "center"], {"default": "left"}),
                "fill_char": ("STRING", {"default": " "}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    FUNCTION = "pad_string"
    CATEGORY = "HAIGC/Text/Advanced"
    
    def pad_string(self, text, width, mode, fill_char):
        if not fill_char:
            fill_char = " "
        else:
            fill_char = fill_char[0]
        
        if mode == "left":
            result = text.ljust(width, fill_char)
        elif mode == "right":
            result = text.rjust(width, fill_char)
        elif mode == "center":
            result = text.center(width, fill_char)
        
        return (result,)


class StringRemoveChars:
    """移除指定字符 / Remove specified characters"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True}),
                "chars_to_remove": ("STRING", {"default": ""}),
                "mode": (["all", "leading", "trailing", "both_ends"], {"default": "all"}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    FUNCTION = "remove_chars"
    CATEGORY = "HAIGC/Text/Advanced"
    
    def remove_chars(self, text, chars_to_remove, mode):
        if mode == "all":
            result = text
            for char in chars_to_remove:
                result = result.replace(char, "")
        elif mode == "leading":
            result = text.lstrip(chars_to_remove)
        elif mode == "trailing":
            result = text.rstrip(chars_to_remove)
        elif mode == "both_ends":
            result = text.strip(chars_to_remove)
        
        return (result,)


class StringExtract:
    """提取字符串部分 / Extract string parts"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True}),
                "mode": (["between", "before", "after", "lines_range"], {"default": "between"}),
                "start_marker": ("STRING", {"default": ""}),
                "end_marker": ("STRING", {"default": ""}),
            },
            "optional": {
                "line_start": ("INT", {"default": 1, "min": 1, "max": 9999}),
                "line_end": ("INT", {"default": 1, "min": 1, "max": 9999}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    FUNCTION = "extract"
    CATEGORY = "HAIGC/Text/Advanced"
    
    def extract(self, text, mode, start_marker, end_marker, line_start=1, line_end=1):
        if mode == "between":
            if start_marker in text and end_marker in text:
                start_idx = text.find(start_marker) + len(start_marker)
                end_idx = text.find(end_marker, start_idx)
                result = text[start_idx:end_idx]
            else:
                result = ""
        
        elif mode == "before":
            if start_marker in text:
                result = text[:text.find(start_marker)]
            else:
                result = text
        
        elif mode == "after":
            if start_marker in text:
                result = text[text.find(start_marker) + len(start_marker):]
            else:
                result = ""
        
        elif mode == "lines_range":
            lines = text.splitlines()
            result = "\n".join(lines[line_start-1:line_end])
        
        return (result,)


class StringCount:
    """计数字符串出现次数 / Count string occurrences"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True}),
                "search": ("STRING", {"default": ""}),
                "case_sensitive": ("BOOLEAN", {"default": True}),
                "overlap": ("BOOLEAN", {"default": False}),
            }
        }
    
    RETURN_TYPES = ("INT", "STRING")
    RETURN_NAMES = ("count", "info")
    FUNCTION = "count_occurrences"
    CATEGORY = "HAIGC/Text/Advanced"
    
    def count_occurrences(self, text, search, case_sensitive, overlap):
        if not search:
            return (0, "Search string is empty")
        
        if not case_sensitive:
            text = text.lower()
            search = search.lower()
        
        if overlap:
            count = 0
            start = 0
            while True:
                pos = text.find(search, start)
                if pos == -1:
                    break
                count += 1
                start = pos + 1
        else:
            count = text.count(search)
        
        info = f"Found '{search}' {count} times"
        return (count, info)
