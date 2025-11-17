"""
HAIGC Text - 最强大的ComfyUI字符串操作节点包
Powerful String Manipulation Nodes for ComfyUI
"""

from .string_nodes import (
    StringConcatenate,
    StringSplit,
    StringReplace,
    StringTrim,
    StringLength,
    StringRepeat,
    StringSlice,
    StringReverse,
    StringCase,
    StringContains,
)

from .advanced_string_nodes import (
    StringRegexReplace,
    StringRegexMatch,
    StringRegexSplit,
    StringFormat,
    StringTemplate,
    StringJoin,
    StringPad,
    StringRemoveChars,
    StringExtract,
    StringCount,
)

from .text_transform_nodes import (
    TextToLines,
    TextFromLines,
    TextSort,
    TextUnique,
    TextFilter,
    TextMap,
    TextEncodeBase64,
    TextDecodeBase64,
    TextHash,
    TextRandomString,
)

# Node class mappings
NODE_CLASS_MAPPINGS = {
    # Basic String Operations
    "HAIGC_StringConcatenate": StringConcatenate,
    "HAIGC_StringSplit": StringSplit,
    "HAIGC_StringReplace": StringReplace,
    "HAIGC_StringTrim": StringTrim,
    "HAIGC_StringLength": StringLength,
    "HAIGC_StringRepeat": StringRepeat,
    "HAIGC_StringSlice": StringSlice,
    "HAIGC_StringReverse": StringReverse,
    "HAIGC_StringCase": StringCase,
    "HAIGC_StringContains": StringContains,
    
    # Advanced String Operations
    "HAIGC_StringRegexReplace": StringRegexReplace,
    "HAIGC_StringRegexMatch": StringRegexMatch,
    "HAIGC_StringRegexSplit": StringRegexSplit,
    "HAIGC_StringFormat": StringFormat,
    "HAIGC_StringTemplate": StringTemplate,
    "HAIGC_StringJoin": StringJoin,
    "HAIGC_StringPad": StringPad,
    "HAIGC_StringRemoveChars": StringRemoveChars,
    "HAIGC_StringExtract": StringExtract,
    "HAIGC_StringCount": StringCount,
    
    # Text Transform Operations
    "HAIGC_TextToLines": TextToLines,
    "HAIGC_TextFromLines": TextFromLines,
    "HAIGC_TextSort": TextSort,
    "HAIGC_TextUnique": TextUnique,
    "HAIGC_TextFilter": TextFilter,
    "HAIGC_TextMap": TextMap,
    "HAIGC_TextEncodeBase64": TextEncodeBase64,
    "HAIGC_TextDecodeBase64": TextDecodeBase64,
    "HAIGC_TextHash": TextHash,
    "HAIGC_TextRandomString": TextRandomString,
}

# Display name mappings
NODE_DISPLAY_NAME_MAPPINGS = {
    # Basic String Operations
    "HAIGC_StringConcatenate": "String Concatenate 🔗",
    "HAIGC_StringSplit": "String Split ✂️",
    "HAIGC_StringReplace": "String Replace 🔄",
    "HAIGC_StringTrim": "String Trim ✨",
    "HAIGC_StringLength": "String Length 📏",
    "HAIGC_StringRepeat": "String Repeat 🔁",
    "HAIGC_StringSlice": "String Slice 🔪",
    "HAIGC_StringReverse": "String Reverse ↩️",
    "HAIGC_StringCase": "String Case 🔤",
    "HAIGC_StringContains": "String Contains 🔍",
    
    # Advanced String Operations
    "HAIGC_StringRegexReplace": "Regex Replace 🎯",
    "HAIGC_StringRegexMatch": "Regex Match 🎯",
    "HAIGC_StringRegexSplit": "Regex Split 🎯",
    "HAIGC_StringFormat": "String Format 📝",
    "HAIGC_StringTemplate": "String Template 📋",
    "HAIGC_StringJoin": "String Join 🔗",
    "HAIGC_StringPad": "String Pad 📦",
    "HAIGC_StringRemoveChars": "Remove Characters 🗑️",
    "HAIGC_StringExtract": "Extract Text 📤",
    "HAIGC_StringCount": "Count Occurrences 🔢",
    
    # Text Transform Operations
    "HAIGC_TextToLines": "Text To Lines 📄",
    "HAIGC_TextFromLines": "Text From Lines 📄",
    "HAIGC_TextSort": "Text Sort 🔀",
    "HAIGC_TextUnique": "Text Unique 🎲",
    "HAIGC_TextFilter": "Text Filter 🔍",
    "HAIGC_TextMap": "Text Map 🗺️",
    "HAIGC_TextEncodeBase64": "Encode Base64 🔐",
    "HAIGC_TextDecodeBase64": "Decode Base64 🔓",
    "HAIGC_TextHash": "Text Hash #️⃣",
    "HAIGC_TextRandomString": "Random String 🎲",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
