"""
文本转换节点
Text Transform Nodes
"""
import base64
import hashlib
import random
import string


class TextToLines:
    """文本转行列表 / Text to lines"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True}),
                "remove_empty": ("BOOLEAN", {"default": True}),
                "strip_lines": ("BOOLEAN", {"default": True}),
            }
        }
    
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("lines", "count")
    FUNCTION = "to_lines"
    CATEGORY = "HAIGC/Text/Transform"
    
    def to_lines(self, text, remove_empty, strip_lines):
        lines = text.splitlines()
        
        if strip_lines:
            lines = [line.strip() for line in lines]
        
        if remove_empty:
            lines = [line for line in lines if line]
        
        result = "\n".join(lines)
        count = len(lines)
        
        return (result, count)


class TextFromLines:
    """行列表转文本 / Lines to text"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "lines": ("STRING", {"default": "", "multiline": True}),
                "separator": ("STRING", {"default": "\n"}),
                "add_numbering": ("BOOLEAN", {"default": False}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    FUNCTION = "from_lines"
    CATEGORY = "HAIGC/Text/Transform"
    
    def from_lines(self, lines, separator, add_numbering):
        line_list = lines.splitlines()
        
        if add_numbering:
            line_list = [f"{i+1}. {line}" for i, line in enumerate(line_list)]
        
        result = separator.join(line_list)
        return (result,)


class TextSort:
    """排序文本行 / Sort text lines"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True}),
                "mode": (["alphabetical", "reverse", "length", "random"], {"default": "alphabetical"}),
                "case_sensitive": ("BOOLEAN", {"default": False}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    FUNCTION = "sort_text"
    CATEGORY = "HAIGC/Text/Transform"
    
    def sort_text(self, text, mode, case_sensitive):
        lines = [line for line in text.splitlines() if line.strip()]
        
        if mode == "alphabetical":
            if case_sensitive:
                lines.sort()
            else:
                lines.sort(key=str.lower)
        
        elif mode == "reverse":
            if case_sensitive:
                lines.sort(reverse=True)
            else:
                lines.sort(key=str.lower, reverse=True)
        
        elif mode == "length":
            lines.sort(key=len)
        
        elif mode == "random":
            random.shuffle(lines)
        
        result = "\n".join(lines)
        return (result,)


class TextUnique:
    """去重文本行 / Remove duplicate lines"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True}),
                "case_sensitive": ("BOOLEAN", {"default": True}),
                "preserve_order": ("BOOLEAN", {"default": True}),
            }
        }
    
    RETURN_TYPES = ("STRING", "INT", "INT")
    RETURN_NAMES = ("result", "original_count", "unique_count")
    FUNCTION = "unique_lines"
    CATEGORY = "HAIGC/Text/Transform"
    
    def unique_lines(self, text, case_sensitive, preserve_order):
        lines = text.splitlines()
        original_count = len(lines)
        
        if preserve_order:
            seen = set()
            unique_lines = []
            for line in lines:
                check_line = line if case_sensitive else line.lower()
                if check_line not in seen:
                    seen.add(check_line)
                    unique_lines.append(line)
        else:
            if case_sensitive:
                unique_lines = list(set(lines))
            else:
                seen = {}
                for line in lines:
                    if line.lower() not in seen:
                        seen[line.lower()] = line
                unique_lines = list(seen.values())
        
        result = "\n".join(unique_lines)
        unique_count = len(unique_lines)
        
        return (result, original_count, unique_count)


class TextFilter:
    """过滤文本行 / Filter text lines"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True}),
                "mode": (["contains", "not_contains", "starts_with", "ends_with", 
                         "regex_match", "min_length", "max_length"], {"default": "contains"}),
                "filter_value": ("STRING", {"default": ""}),
            },
            "optional": {
                "length": ("INT", {"default": 0, "min": 0, "max": 9999}),
            }
        }
    
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("result", "count")
    FUNCTION = "filter_lines"
    CATEGORY = "HAIGC/Text/Transform"
    
    def filter_lines(self, text, mode, filter_value, length=0):
        import re
        lines = text.splitlines()
        filtered = []
        
        for line in lines:
            if mode == "contains":
                if filter_value in line:
                    filtered.append(line)
            
            elif mode == "not_contains":
                if filter_value not in line:
                    filtered.append(line)
            
            elif mode == "starts_with":
                if line.startswith(filter_value):
                    filtered.append(line)
            
            elif mode == "ends_with":
                if line.endswith(filter_value):
                    filtered.append(line)
            
            elif mode == "regex_match":
                try:
                    if re.search(filter_value, line):
                        filtered.append(line)
                except re.error:
                    pass
            
            elif mode == "min_length":
                if len(line) >= length:
                    filtered.append(line)
            
            elif mode == "max_length":
                if len(line) <= length:
                    filtered.append(line)
        
        result = "\n".join(filtered)
        count = len(filtered)
        
        return (result, count)


class TextMap:
    """映射转换文本行 / Map transform text lines"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True}),
                "operation": (["add_prefix", "add_suffix", "wrap", "quote", 
                              "number", "bullet", "indent"], {"default": "add_prefix"}),
                "value": ("STRING", {"default": ""}),
            },
            "optional": {
                "value2": ("STRING", {"default": ""}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    FUNCTION = "map_lines"
    CATEGORY = "HAIGC/Text/Transform"
    
    def map_lines(self, text, operation, value, value2=""):
        lines = text.splitlines()
        result_lines = []
        
        for i, line in enumerate(lines, 1):
            if operation == "add_prefix":
                result_lines.append(value + line)
            
            elif operation == "add_suffix":
                result_lines.append(line + value)
            
            elif operation == "wrap":
                suffix = value2 if value2 else value
                result_lines.append(value + line + suffix)
            
            elif operation == "quote":
                quote_char = value if value else '"'
                result_lines.append(f"{quote_char}{line}{quote_char}")
            
            elif operation == "number":
                separator = value if value else ". "
                result_lines.append(f"{i}{separator}{line}")
            
            elif operation == "bullet":
                bullet = value if value else "• "
                result_lines.append(bullet + line)
            
            elif operation == "indent":
                indent = value if value else "    "
                result_lines.append(indent + line)
        
        result = "\n".join(result_lines)
        return (result,)


class TextEncodeBase64:
    """Base64编码 / Base64 encode"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True}),
                "encoding": (["utf-8", "ascii", "latin-1"], {"default": "utf-8"}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    FUNCTION = "encode"
    CATEGORY = "HAIGC/Text/Transform"
    
    def encode(self, text, encoding):
        try:
            encoded = base64.b64encode(text.encode(encoding)).decode('ascii')
            return (encoded,)
        except Exception as e:
            return (f"Encoding Error: {str(e)}",)


class TextDecodeBase64:
    """Base64解码 / Base64 decode"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": ""}),
                "encoding": (["utf-8", "ascii", "latin-1"], {"default": "utf-8"}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    FUNCTION = "decode"
    CATEGORY = "HAIGC/Text/Transform"
    
    def decode(self, text, encoding):
        try:
            decoded = base64.b64decode(text).decode(encoding)
            return (decoded,)
        except Exception as e:
            return (f"Decoding Error: {str(e)}",)


class TextHash:
    """文本哈希 / Text hash"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True}),
                "algorithm": (["md5", "sha1", "sha256", "sha512"], {"default": "sha256"}),
                "output_format": (["hex", "base64"], {"default": "hex"}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    FUNCTION = "hash_text"
    CATEGORY = "HAIGC/Text/Transform"
    
    def hash_text(self, text, algorithm, output_format):
        try:
            if algorithm == "md5":
                h = hashlib.md5(text.encode('utf-8'))
            elif algorithm == "sha1":
                h = hashlib.sha1(text.encode('utf-8'))
            elif algorithm == "sha256":
                h = hashlib.sha256(text.encode('utf-8'))
            elif algorithm == "sha512":
                h = hashlib.sha512(text.encode('utf-8'))
            
            if output_format == "hex":
                result = h.hexdigest()
            else:
                result = base64.b64encode(h.digest()).decode('ascii')
            
            return (result,)
        except Exception as e:
            return (f"Hash Error: {str(e)}",)


class TextRandomString:
    """生成随机字符串 / Generate random string"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "length": ("INT", {"default": 10, "min": 1, "max": 10000}),
                "charset": (["alphanumeric", "letters", "digits", "lowercase", 
                           "uppercase", "hex", "custom"], {"default": "alphanumeric"}),
            },
            "optional": {
                "custom_chars": ("STRING", {"default": ""}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 999999}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    FUNCTION = "generate"
    CATEGORY = "HAIGC/Text/Transform"
    
    def generate(self, length, charset, custom_chars="", seed=0):
        if seed > 0:
            random.seed(seed)
        
        if charset == "alphanumeric":
            chars = string.ascii_letters + string.digits
        elif charset == "letters":
            chars = string.ascii_letters
        elif charset == "digits":
            chars = string.digits
        elif charset == "lowercase":
            chars = string.ascii_lowercase
        elif charset == "uppercase":
            chars = string.ascii_uppercase
        elif charset == "hex":
            chars = string.hexdigits.lower()[:16]
        elif charset == "custom":
            chars = custom_chars if custom_chars else string.ascii_letters
        
        result = ''.join(random.choice(chars) for _ in range(length))
        
        # Reset random seed
        if seed > 0:
            random.seed()
        
        return (result,)
