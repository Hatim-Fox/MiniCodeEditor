import sys
import os
import re
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPlainTextEdit, QFileDialog,
                             QAction, QToolBar, QWidget, QHBoxLayout, QVBoxLayout,
                             QTextEdit, QTabWidget, QLineEdit, QPushButton, QLabel,
                             QMessageBox, QStatusBar, QMenu)
from PyQt5.QtGui import (QColor, QFont, QTextCharFormat,
                         QTextCursor, QPainter, QTextFormat, QFontDatabase, QKeySequence,
                         QSyntaxHighlighter, QTextDocument)
from PyQt5.QtCore import Qt, QSize, QUrl, QDateTime, QPoint, QTimer, pyqtSignal, QRegExp
from PyQt5.QtWidgets import QApplication


# ------------------ Syntax Highlighter ------------------ #
class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.highlightingRules = []

        # Formats for different token types
        formats = {
            "keyword": self.create_format("#569CD6", is_bold=True),       # Blue
            "operator": self.create_format("#D4D4D4", is_bold=True),      # White/Light Gray
            "string": self.create_format("#CE9178"),                      # Orange
            "comment": self.create_format("#6A9955"),                     # Green
            "class": self.create_format("#C678DD", is_bold=True),         # Purple
            "function": self.create_format("#DCDCAA"),                    # Yellow
            "numbers": self.create_format("#B5CEA8"),                     # Light Green
        }

        # Python Keywords
        keywords = [
            'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
            'break', 'class', 'continue', 'def', 'del', 'elif', 'else',
            'except', 'finally', 'for', 'from', 'global', 'if', 'import',
            'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise',
            'return', 'try', 'while', 'with', 'yield'
        ]
        self.add_rules(keywords, formats["keyword"])

        # Add rules for built-in functions, types and constants
        builtins = [
            'print', 'len', 'range', 'list', 'dict', 'tuple', 'set', 'str',
            'int', 'float', 'bool', 'type', 'open', 'range', 'dir',
            'abs', 'id', 'sum'
        ]
        self.add_rules(builtins, formats["function"])

        # Rules for Class definition
        self.highlightingRules.append((r'\bclass\b\s+([A-Za-z_][A-Za-z0-9_]*)', formats["class"]))
        
        # Rules for Function definition
        self.highlightingRules.append((r'\bdef\b\s+([A-Za-z_][A-Za-z0-9_]*)', formats["function"]))
        
        # Operators
        operators = [
            '=', '==', '!=', '<', '<=', '>', '>=', '\\+', '-', '\\*', '/', '//',
            '\\%', '\\*\\*', '\\+=', '-=', '\\*=', '/=', '%=', '//=', '\\*\\*='
        ]
        self.add_rules([r'\\' + op for op in operators], formats["operator"])

        # String literals (single and double quotes)
        self.highlightingRules.append((r'\"[^\"]*\"', formats["string"]))
        self.highlightingRules.append((r'\'[^\']*\'', formats["string"]))

        # Numbers
        self.highlightingRules.append((r'\b[0-9]+\b', formats["numbers"]))

        # Comments
        self.highlightingRules.append((r'#.*', formats["comment"]))

    def create_format(self, color_hex, is_bold=False):
        """Helper to create a QTextCharFormat."""
        text_format = QTextCharFormat()
        text_format.setForeground(QColor(color_hex))
        if is_bold:
            text_format.setFontWeight(QFont.Bold)
        return text_format
        
    def add_rules(self, keywords, format):
        """Helper to add rules for a list of keywords."""
        for keyword in keywords:
            self.highlightingRules.append((r'\b' + re.escape(keyword) + r'\b', format))

    def highlightBlock(self, text):
        # A more efficient way to highlight based on a list of rules
        for pattern, format in self.highlightingRules:
            expression = re.compile(pattern)
            for match in expression.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, format)


class JavaScriptHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlightingRules = []

        formats = {
            "keyword": self.create_format("#C586C0"),       # Purple
            "control_flow": self.create_format("#C586C0"),  # Purple
            "built_in": self.create_format("#569CD6"),      # Blue
            "string": self.create_format("#CE9178"),        # Orange
            "comment": self.create_format("#6A9955"),       # Green
            "numbers": self.create_format("#B5CEA8"),       # Light Green
            "class_function": self.create_format("#DCDCAA"), # Yellow
        }

        keywords = [
            'var', 'let', 'const', 'function', 'class', 'import', 'export', 'of',
            'from', 'as', 'await', 'async'
        ]
        self.add_rules(keywords, formats["keyword"])

        control_flow = [
            'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'break',
            'continue', 'return', 'try', 'catch', 'finally', 'with'
        ]
        self.add_rules(control_flow, formats["control_flow"])

        builtins = [
            'this', 'window', 'document', 'console', 'log', 'new', 'null', 'undefined',
            'true', 'false'
        ]
        self.add_rules(builtins, formats["built_in"])

        # Rules for class/function names
        self.highlightingRules.append((r'\b(?:class|function)\s+([A-Za-z_][A-Za-z0-9_]*)', formats["class_function"]))
        self.highlightingRules.append((r'\b([A-Za-z_][A-Za-z0-9_]*)\s*\(', formats["class_function"]))

        # String literals
        self.highlightingRules.append((r'\"[^\"]*\"', formats["string"]))
        self.highlightingRules.append((r'\'[^\']*\'', formats["string"]))
        self.highlightingRules.append((r'`[^`]*`', formats["string"]))  # Backticks for template literals

        # Numbers
        self.highlightingRules.append((r'\b[0-9]+\b', formats["numbers"]))

        # Single-line comments
        self.highlightingRules.append((r'//.*', formats["comment"]))
        
        # Multi-line comments - this needs a different approach in highlightBlock
        self.comment_format = formats["comment"]
        self.comment_start_expression = QRegExp("/\\*")
        self.comment_end_expression = QRegExp("\\*/")

    def create_format(self, color_hex, is_bold=False):
        text_format = QTextCharFormat()
        text_format.setForeground(QColor(color_hex))
        if is_bold:
            text_format.setFontWeight(QFont.Bold)
        return text_format

    def add_rules(self, keywords, format):
        for keyword in keywords:
            self.highlightingRules.append((r'\b' + re.escape(keyword) + r'\b', format))

    def highlightBlock(self, text):
        # Single-line highlighting
        for pattern, format in self.highlightingRules:
            expression = re.compile(pattern)
            for match in expression.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, format)
        
        # Multi-line comment highlighting
        self.setCurrentBlockState(0)
        start_index = 0
        if self.previousBlockState() != 1:
            start_index = self.comment_start_expression.indexIn(text)
        
        while start_index >= 0:
            end_index = self.comment_end_expression.indexIn(text, start_index)
            if end_index == -1:
                self.setCurrentBlockState(1)
                comment_length = len(text) - start_index
            else:
                comment_length = end_index - start_index + self.comment_end_expression.matchedLength()
            
            self.setFormat(start_index, comment_length, self.comment_format)
            start_index = self.comment_start_expression.indexIn(text, start_index + comment_length)


class CppHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlightingRules = []

        formats = {
            "keyword": self.create_format("#C586C0", is_bold=True),  # Purple
            "type": self.create_format("#569CD6"),                   # Blue
            "string": self.create_format("#CE9178"),                 # Orange
            "comment": self.create_format("#6A9955"),                # Green
            "numbers": self.create_format("#B5CEA8"),                # Light Green
        }
        
        keywords = [
            'alignas', 'alignof', 'and', 'and_eq', 'asm', 'auto', 'bitand', 'bitor', 'bool', 'break',
            'case', 'catch', 'char', 'char16_t', 'char32_t', 'class', 'const', 'constexpr', 'const_cast',
            'continue', 'decltype', 'default', 'delete', 'do', 'double', 'dynamic_cast', 'else', 'enum',
            'explicit', 'export', 'extern', 'false', 'final', 'float', 'for', 'friend', 'goto', 'if',
            'inline', 'int', 'long', 'mutable', 'namespace', 'new', 'noexcept', 'not', 'not_eq', 'nullptr',
            'operator', 'or', 'or_eq', 'private', 'protected', 'public', 'register', 'reinterpret_cast',
            'return', 'short', 'signed', 'sizeof', 'static', 'static_assert', 'static_cast', 'struct',
            'switch', 'template', 'this', 'thread_local', 'throw', 'true', 'try', 'typedef', 'typeid',
            'typename', 'union', 'unsigned', 'using', 'virtual', 'void', 'volatile', 'wchar_t', 'while',
            'xor', 'xor_eq'
        ]
        self.add_rules(keywords, formats["keyword"])

        types = [
            'int', 'long', 'short', 'double', 'float', 'char', 'bool', 'void',
            'string', 'vector', 'map', 'set', 'pair'
        ]
        self.add_rules(types, formats["type"])

        # String literals (double quotes)
        self.highlightingRules.append((r'\"[^\"]*\"', formats["string"]))
        
        # Numbers
        self.highlightingRules.append((r'\b[0-9]+\b', formats["numbers"]))
        
        # Single-line comments
        self.highlightingRules.append((r'//.*', formats["comment"]))

        # Multi-line comment highlighting
        self.comment_format = formats["comment"]
        self.comment_start_expression = QRegExp("/\\*")
        self.comment_end_expression = QRegExp("\\*/")

    def create_format(self, color_hex, is_bold=False):
        text_format = QTextCharFormat()
        text_format.setForeground(QColor(color_hex))
        if is_bold:
            text_format.setFontWeight(QFont.Bold)
        return text_format
        
    def add_rules(self, keywords, format):
        for keyword in keywords:
            self.highlightingRules.append((r'\b' + re.escape(keyword) + r'\b', format))

    def highlightBlock(self, text):
        # Single-line highlighting
        for pattern, format in self.highlightingRules:
            expression = re.compile(pattern)
            for match in expression.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, format)
        
        # Multi-line comment highlighting
        self.setCurrentBlockState(0)
        start_index = 0
        if self.previousBlockState() != 1:
            start_index = self.comment_start_expression.indexIn(text)
        
        while start_index >= 0:
            end_index = self.comment_end_expression.indexIn(text, start_index)
            if end_index == -1:
                self.setCurrentBlockState(1)
                comment_length = len(text) - start_index
            else:
                comment_length = end_index - start_index + self.comment_end_expression.matchedLength()
            
            self.setFormat(start_index, comment_length, self.comment_format)
            start_index = self.comment_start_expression.indexIn(text, start_index + comment_length)


class HtmlHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlightingRules = []

        formats = {
            "tag": self.create_format("#569CD6"),        # Blue for tags like <html>
            "attribute": self.create_format("#9CDCFE"),  # Light Blue for attributes like href
            "string": self.create_format("#CE9178"),     # Orange for attribute values
            "comment": self.create_format("#6A9955"),    # Green for comments
        }
        
        # Tag names: e.g., <p>, <div>, <h1>
        self.highlightingRules.append((r'<([a-zA-Z0-9]+)', formats["tag"]))
        self.highlightingRules.append((r'</([a-zA-Z0-9]+)>', formats["tag"]))
        
        # Attribute names: e.g., href, class, id
        self.highlightingRules.append((r'([a-zA-Z0-9]+)=', formats["attribute"]))
        
        # String literals for attribute values
        self.highlightingRules.append((r'\"[^\"]*\"', formats["string"]))
        self.highlightingRules.append((r'\'[^\']*\'', formats["string"]))

        # HTML Comments
        self.highlightingRules.append((r'<!--.*-->', formats["comment"]))

    def create_format(self, color_hex, is_bold=False):
        text_format = QTextCharFormat()
        text_format.setForeground(QColor(color_hex))
        if is_bold:
            text_format.setFontWeight(QFont.Bold)
        return text_format

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = re.compile(pattern)
            for match in expression.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, format)


class CssHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlightingRules = []

        formats = {
            "selector": self.create_format("#D7BA7D"),       # Yellow
            "property": self.create_format("#9CDCFE"),       # Light Blue
            "value": self.create_format("#CE9178"),          # Orange
            "string": self.create_format("#CE9178"),         # Orange
            "comment": self.create_format("#6A9955"),        # Green
            "at_rule": self.create_format("#C586C0"),        # Purple
        }

        # Selectors (classes and IDs)
        self.highlightingRules.append((r'\.[a-zA-Z0-9_-]+', formats["selector"]))
        self.highlightingRules.append((r'#[a-zA-Z0-9_-]+', formats["selector"]))
        
        # Property names
        self.highlightingRules.append((r'\b[a-zA-Z-]+(?=:)', formats["property"]))
        
        # Values (not strings)
        self.highlightingRules.append((r':\s*([^;]+);', formats["value"]))
        
        # String literals
        self.highlightingRules.append((r'\"[^\"]*\"', formats["string"]))
        self.highlightingRules.append((r'\'[^\']*\'', formats["string"]))
        
        # At-rules like @media, @import
        self.highlightingRules.append((r'@[a-zA-Z]+', formats["at_rule"]))

        # Multi-line comments
        self.comment_format = formats["comment"]
        self.comment_start_expression = QRegExp("/\\*")
        self.comment_end_expression = QRegExp("\\*/")

    def create_format(self, color_hex, is_bold=False):
        text_format = QTextCharFormat()
        text_format.setForeground(QColor(color_hex))
        if is_bold:
            text_format.setFontWeight(QFont.Bold)
        return text_format
    
    def highlightBlock(self, text):
        # Single-line highlighting
        for pattern, format in self.highlightingRules:
            expression = re.compile(pattern)
            for match in expression.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), format)
        
        # Multi-line comment highlighting
        self.setCurrentBlockState(0)
        start_index = 0
        if self.previousBlockState() != 1:
            start_index = self.comment_start_expression.indexIn(text)
        
        while start_index >= 0:
            end_index = self.comment_end_expression.indexIn(text, start_index)
            if end_index == -1:
                self.setCurrentBlockState(1)
                comment_length = len(text) - start_index
            else:
                comment_length = end_index - start_index + self.comment_end_expression.matchedLength()
            
            self.setFormat(start_index, comment_length, self.comment_format)
            start_index = self.comment_start_expression.indexIn(text, start_index + comment_length)


class JsonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlightingRules = []

        formats = {
            "key": self.create_format("#9CDCFE"),          # Light Blue
            "string_value": self.create_format("#CE9178"), # Orange
            "number_value": self.create_format("#B5CEA8"), # Light Green
            "boolean_null": self.create_format("#569CD6"), # Blue
        }
        
        # Keys in double quotes followed by a colon
        self.highlightingRules.append((r'\"[^\"]+\"\s*:', formats["key"]))
        
        # String values
        self.highlightingRules.append((r':\s*\"[^\"]*\"', formats["string_value"]))
        
        # Number values
        self.highlightingRules.append((r'\b[0-9.]+\b', formats["number_value"]))
        
        # Boolean and null values
        self.highlightingRules.append((r'\b(true|false|null)\b', formats["boolean_null"]))

    def create_format(self, color_hex, is_bold=False):
        text_format = QTextCharFormat()
        text_format.setForeground(QColor(color_hex))
        if is_bold:
            text_format.setFontWeight(QFont.Bold)
        return text_format

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = re.compile(pattern)
            for match in expression.finditer(text):
                # For keys and strings, adjust the start position to not include the colon or quotes
                start = match.start()
                if pattern.startswith('\"'):
                    start += 1
                if pattern.endswith(':'):
                    end = match.end() - 1
                else:
                    end = match.end()
                
                self.setFormat(start, end - start, format)


class BashHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlightingRules = []

        formats = {
            "keyword": self.create_format("#C586C0"),       # Purple
            "command": self.create_format("#569CD6"),       # Blue
            "variable": self.create_format("#9CDCFE"),      # Light Blue
            "string": self.create_format("#CE9178"),        # Orange
            "comment": self.create_format("#6A9955"),       # Green
            "numbers": self.create_format("#B5CEA8"),       # Light Green
        }

        # Keywords (control flow)
        keywords = [
            'if', 'then', 'else', 'elif', 'fi', 'for', 'while', 'do', 'done',
            'case', 'esac', 'in', 'until', 'function'
        ]
        self.add_rules(keywords, formats["keyword"])

        # Common shell commands
        commands = [
            'ls', 'cd', 'pwd', 'echo', 'cat', 'grep', 'find', 'sudo', 'apt-get', 'yum', 'git'
        ]
        self.add_rules(commands, formats["command"])

        # Variables
        self.highlightingRules.append((r'\$\b[a-zA-Z_][a-zA-Z0-9_]*\b', formats["variable"]))
        
        # String literals (single and double quotes)
        self.highlightingRules.append((r'\"[^\"]*\"', formats["string"]))
        self.highlightingRules.append((r'\'[^\']*\'', formats["string"]))
        
        # Numbers
        self.highlightingRules.append((r'\b[0-9]+\b', formats["numbers"]))
        
        # Comments
        self.highlightingRules.append((r'#.*', formats["comment"]))

    def create_format(self, color_hex, is_bold=False):
        text_format = QTextCharFormat()
        text_format.setForeground(QColor(color_hex))
        if is_bold:
            text_format.setFontWeight(QFont.Bold)
        return text_format

    def add_rules(self, keywords, format):
        for keyword in keywords:
            self.highlightingRules.append((r'\b' + re.escape(keyword) + r'\b', format))

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = re.compile(pattern)
            for match in expression.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), format)


class MarkdownHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlightingRules = []

        formats = {
            "header": self.create_format("#569CD6", is_bold=True),      # Blue
            "bold": self.create_format("#DCDCAA", is_bold=True),        # Yellow
            "italic": self.create_format("#CE9178", is_italic=True),    # Orange
            "link": self.create_format("#4EC9B0", is_underline=True),   # Teal
            "list_item": self.create_format("#B5CEA8"),                 # Light Green
        }
        
        # Headers: #, ##, ###, etc.
        self.highlightingRules.append((r'^(#+)\s+.*', formats["header"]))
        
        # Bold text: **text** or __text__
        self.highlightingRules.append((r'(\*\*|__)(.*?)\1', formats["bold"]))
        
        # Italic text: *text* or _text_
        self.highlightingRules.append((r'(\*|_)(.*?)\1', formats["italic"]))

        # Links: [text](link)
        self.highlightingRules.append((r'\[(.*?)\]\((.*?)\)', formats["link"]))

        # List items: *, -, +
        self.highlightingRules.append((r'^\s*([*-]|\d+\.)\s+.*', formats["list_item"]))

    def create_format(self, color_hex, is_bold=False, is_italic=False, is_underline=False):
        text_format = QTextCharFormat()
        text_format.setForeground(QColor(color_hex))
        if is_bold:
            text_format.setFontWeight(QFont.Bold)
        if is_italic:
            text_format.setFontItalic(True)
        if is_underline:
            text_format.setFontUnderline(True)
        return text_format

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = re.compile(pattern)
            for match in expression.finditer(text):
                # Apply format to the matched group (e.g., the text inside **bold**)
                if match.groups():
                    start, end = match.span(2)  # Get the span of the content
                    self.setFormat(start, end - start, format)
                else:
                    start, end = match.span(0)  # For full match
                    self.setFormat(start, end - start, format)


class XmlHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlightingRules = []

        formats = {
            "tag": self.create_format("#569CD6"),        # Blue
            "attribute": self.create_format("#9CDCFE"),  # Light Blue
            "string": self.create_format("#CE9178"),     # Orange
            "comment": self.create_format("#6A9955"),    # Green
        }
        
        # Tag names
        self.highlightingRules.append((r'<([a-zA-Z0-9_.-:]+)', formats["tag"]))
        self.highlightingRules.append((r'</([a-zA-Z0-9_.-:]+)>', formats["tag"]))
        
        # Attribute names
        self.highlightingRules.append((r'([a-zA-Z0-9_.-]+)=', formats["attribute"]))
        
        # String literals for attribute values
        self.highlightingRules.append((r'\"[^\"]*\"', formats["string"]))
        self.highlightingRules.append((r'\'[^\']*\'', formats["string"]))

        # XML Comments
        self.highlightingRules.append((r'<!--.*-->', formats["comment"]))

    def create_format(self, color_hex, is_bold=False):
        text_format = QTextCharFormat()
        text_format.setForeground(QColor(color_hex))
        if is_bold:
            text_format.setFontWeight(QFont.Bold)
        return text_format

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = re.compile(pattern)
            for match in expression.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), format)


class JavaHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlightingRules = []

        formats = {
            "keyword": self.create_format("#C586C0"),       # Purple
            "type": self.create_format("#569CD6"),          # Blue
            "string": self.create_format("#CE9178"),        # Orange
            "comment": self.create_format("#6A9955"),       # Green
            "numbers": self.create_format("#B5CEA8"),       # Light Green
            "class_name": self.create_format("#DCDCAA"),    # Yellow
        }
        
        keywords = [
            'abstract', 'assert', 'break', 'case', 'catch', 'class', 'const', 'continue',
            'default', 'do', 'else', 'enum', 'extends', 'final', 'finally', 'for',
            'goto', 'if', 'implements', 'import', 'instanceof', 'interface', 'native',
            'new', 'package', 'private', 'protected', 'public', 'return', 'static',
            'strictfp', 'super', 'switch', 'synchronized', 'this', 'throw', 'throws',
            'transient', 'try', 'void', 'volatile', 'while'
        ]
        self.add_rules(keywords, formats["keyword"])

        types = [
            'boolean', 'byte', 'char', 'double', 'float', 'int', 'long', 'short'
        ]
        self.add_rules(types, formats["type"])

        # Class names
        self.highlightingRules.append((r'\bclass\s+([A-Za-z_][A-Za-z0-9_]*)', formats["class_name"]))
        
        # String literals
        self.highlightingRules.append((r'\"[^\"]*\"', formats["string"]))
        
        # Numbers
        self.highlightingRules.append((r'\b[0-9]+\b', formats["numbers"]))
        
        # Single-line comments
        self.highlightingRules.append((r'//.*', formats["comment"]))

        # Multi-line comment highlighting
        self.comment_format = formats["comment"]
        self.comment_start_expression = QRegExp("/\\*")
        self.comment_end_expression = QRegExp("\\*/")

    def create_format(self, color_hex, is_bold=False):
        text_format = QTextCharFormat()
        text_format.setForeground(QColor(color_hex))
        if is_bold:
            text_format.setFontWeight(QFont.Bold)
        return text_format
        
    def add_rules(self, keywords, format):
        for keyword in keywords:
            self.highlightingRules.append((r'\b' + re.escape(keyword) + r'\b', format))

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = re.compile(pattern)
            for match in expression.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), format)
        
        # Multi-line comment highlighting
        self.setCurrentBlockState(0)
        start_index = 0
        if self.previousBlockState() != 1:
            start_index = self.comment_start_expression.indexIn(text)
        
        while start_index >= 0:
            end_index = self.comment_end_expression.indexIn(text, start_index)
            if end_index == -1:
                self.setCurrentBlockState(1)
                comment_length = len(text) - start_index
            else:
                comment_length = end_index - start_index + self.comment_end_expression.matchedLength()
            
            self.setFormat(start_index, comment_length, self.comment_format)
            start_index = self.comment_start_expression.indexIn(text, start_index + comment_length)


class RubyHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlightingRules = []

        formats = {
            "keyword": self.create_format("#C586C0"),        # Purple
            "method": self.create_format("#DCDCAA"),         # Yellow
            "variable": self.create_format("#9CDCFE"),       # Light Blue
            "string": self.create_format("#CE9178"),         # Orange
            "comment": self.create_format("#6A9955"),        # Green
            "symbol": self.create_format("#4EC9B0"),         # Teal
        }
        
        keywords = [
            'BEGIN', 'END', 'alias', 'and', 'begin', 'break', 'case', 'class', 'def', 'do',
            'else', 'elsif', 'end', 'ensure', 'for', 'if', 'in', 'module', 'next', 'nil',
            'not', 'or', 'redo', 'rescue', 'retry', 'return', 'self', 'super', 'then',
            'unless', 'until', 'when', 'while', 'yield'
        ]
        self.add_rules(keywords, formats["keyword"])

        # Method names
        self.highlightingRules.append((r'\bdef\s+([a-zA-Z_][a-zA-Z0-9_]*)', formats["method"]))

        # Instance and class variables
        self.highlightingRules.append((r'(@[a-zA-Z_][a-zA-Z0-9_]*)', formats["variable"]))
        self.highlightingRules.append((r'(@@[a-zA-Z_][a-zA-Z0-9_]*)', formats["variable"]))
        
        # Global variables
        self.highlightingRules.append((r'(\$[a-zA-Z_][a-zA-Z0-9_]*)', formats["variable"]))
        
        # Symbols
        self.highlightingRules.append((r':([a-zA-Z_][a-zA-Z0-9_]*)', formats["symbol"]))
        
        # String literals (single and double quotes)
        self.highlightingRules.append((r'\"[^\"]*\"', formats["string"]))
        self.highlightingRules.append((r'\'[^\']*\'', formats["string"]))
        
        # Comments
        self.highlightingRules.append((r'#.*', formats["comment"]))

    def create_format(self, color_hex, is_bold=False):
        text_format = QTextCharFormat()
        text_format.setForeground(QColor(color_hex))
        if is_bold:
            text_format.setFontWeight(QFont.Bold)
        return text_format
        
    def add_rules(self, keywords, format):
        for keyword in keywords:
            self.highlightingRules.append((r'\b' + re.escape(keyword) + r'\b', format))

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = re.compile(pattern)
            for match in expression.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), format)


class PhpHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlightingRules = []

        formats = {
            "keyword": self.create_format("#C586C0"),       # Purple
            "builtin": self.create_format("#569CD6"),       # Blue
            "variable": self.create_format("#9CDCFE"),      # Light Blue
            "string": self.create_format("#CE9178"),        # Orange
            "comment": self.create_format("#6A9955"),       # Green
            "numbers": self.create_format("#B5CEA8"),       # Light Green
        }

        # PHP keywords
        keywords = [
            '__halt_compiler', 'abstract', 'and', 'array', 'as', 'break', 'callable', 'case', 'catch',
            'class', 'clone', 'const', 'continue', 'declare', 'default', 'die', 'do', 'echo', 'else',
            'elseif', 'empty', 'enddeclare', 'endfor', 'endforeach', 'endif', 'endswitch', 'endwhile',
            'eval', 'exit', 'extends', 'final', 'for', 'foreach', 'function', 'global', 'goto', 'if',
            'implements', 'include', 'include_once', 'instanceof', 'interface', 'isset', 'list',
            'namespace', 'new', 'or', 'print', 'private', 'protected', 'public', 'require',
            'require_once', 'return', 'static', 'switch', 'throw', 'trait', 'try', 'unset', 'use',
            'var', 'while', 'xor', 'yield'
        ]
        self.add_rules(keywords, formats["keyword"])

        # Built-in functions
        builtins = [
            'printf', 'strlen', 'count', 'isset', 'empty', 'define', 'header', 'session_start'
        ]
        self.add_rules(builtins, formats["builtin"])

        # Variables
        self.highlightingRules.append((r'\$[a-zA-Z_][a-zA-Z0-9_]*', formats["variable"]))
        
        # String literals (single and double quotes)
        self.highlightingRules.append((r'\"[^\"]*\"', formats["string"]))
        self.highlightingRules.append((r'\'[^\']*\'', formats["string"]))
        
        # Numbers
        self.highlightingRules.append((r'\b[0-9]+\b', formats["numbers"]))
        
        # Single-line comments
        self.highlightingRules.append((r'//.*', formats["comment"]))

        # Multi-line comment highlighting
        self.comment_format = formats["comment"]
        self.comment_start_expression = QRegExp("/\\*")
        self.comment_end_expression = QRegExp("\\*/")

    def create_format(self, color_hex, is_bold=False):
        text_format = QTextCharFormat()
        text_format.setForeground(QColor(color_hex))
        if is_bold:
            text_format.setFontWeight(QFont.Bold)
        return text_format

    def add_rules(self, keywords, format):
        for keyword in keywords:
            self.highlightingRules.append((r'\b' + re.escape(keyword) + r'\b', format))

    def highlightBlock(self, text):
        # Single-line highlighting
        for pattern, format in self.highlightingRules:
            expression = re.compile(pattern)
            for match in expression.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), format)
        
        # Multi-line comment highlighting
        self.setCurrentBlockState(0)
        start_index = 0
        if self.previousBlockState() != 1:
            start_index = self.comment_start_expression.indexIn(text)
        
        while start_index >= 0:
            end_index = self.comment_end_expression.indexIn(text, start_index)
            if end_index == -1:
                self.setCurrentBlockState(1)
                comment_length = len(text) - start_index
            else:
                comment_length = end_index - start_index + self.comment_end_expression.matchedLength()
            
            self.setFormat(start_index, comment_length, self.comment_format)
            start_index = self.comment_start_expression.indexIn(text, start_index + comment_length)


class SqlHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlightingRules = []

        formats = {
            "keyword": self.create_format("#C586C0"),       # Purple
            "function": self.create_format("#DCDCAA"),      # Yellow
            "string": self.create_format("#CE9178"),        # Orange
            "comment": self.create_format("#6A9955"),       # Green
            "numbers": self.create_format("#B5CEA8"),       # Light Green
        }
        
        # SQL Keywords
        keywords = [
            'ADD', 'ALTER', 'AND', 'AS', 'ASC', 'BETWEEN', 'BY', 'CASE', 'CAST', 'COLUMN',
            'CREATE', 'DATABASE', 'DEFAULT', 'DELETE', 'DESC', 'DISTINCT', 'DROP', 'EXISTS',
            'FROM', 'GROUP', 'HAVING', 'IN', 'INDEX', 'INSERT', 'INTO', 'IS', 'JOIN', 'LIKE',
            'LIMIT', 'NOT', 'NULL', 'ON', 'OR', 'ORDER', 'OUTER', 'SELECT', 'SET', 'TABLE',
            'UNION', 'UPDATE', 'VALUES', 'WHERE'
        ]
        self.add_rules(keywords, formats["keyword"])

        # Built-in functions
        functions = [
            'COUNT', 'AVG', 'SUM', 'MIN', 'MAX', 'LOWER', 'UPPER', 'TRIM', 'CONCAT'
        ]
        self.add_rules(functions, formats["function"])
        
        # String literals (single quotes)
        self.highlightingRules.append((r'\'[^\']*\'', formats["string"]))
        
        # Numbers
        self.highlightingRules.append((r'\b[0-9]+\b', formats["numbers"]))
        
        # Single-line comments
        self.highlightingRules.append((r'--.*', formats["comment"]))

        # Multi-line comment highlighting
        self.comment_format = formats["comment"]
        self.comment_start_expression = QRegExp("/\\*")
        self.comment_end_expression = QRegExp("\\*/")

    def create_format(self, color_hex, is_bold=False):
        text_format = QTextCharFormat()
        text_format.setForeground(QColor(color_hex))
        if is_bold:
            text_format.setFontWeight(QFont.Bold)
        return text_format
        
    def add_rules(self, keywords, format):
        for keyword in keywords:
            self.highlightingRules.append((r'\b' + re.escape(keyword) + r'\b', format))

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = re.compile(pattern, re.IGNORECASE)
            for match in expression.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), format)
        
        self.setCurrentBlockState(0)
        start_index = 0
        if self.previousBlockState() != 1:
            start_index = self.comment_start_expression.indexIn(text)
        
        while start_index >= 0:
            end_index = self.comment_end_expression.indexIn(text, start_index)
            if end_index == -1:
                self.setCurrentBlockState(1)
                comment_length = len(text) - start_index
            else:
                comment_length = end_index - start_index + self.comment_end_expression.matchedLength()
            
            self.setFormat(start_index, comment_length, self.comment_format)
            start_index = self.comment_start_expression.indexIn(text, start_index + comment_length)


class SwiftHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlightingRules = []

        formats = {
            "keyword": self.create_format("#C586C0"),       # Purple
            "type": self.create_format("#569CD6"),          # Blue
            "string": self.create_format("#CE9178"),        # Orange
            "comment": self.create_format("#6A9955"),       # Green
            "numbers": self.create_format("#B5CEA8"),       # Light Green
        }
        
        keywords = [
            'as', 'async', 'await', 'break', 'case', 'catch', 'class', 'continue', 'convenience',
            'default', 'defer', 'deinit', 'didSet', 'do', 'dynamic', 'else', 'enum', 'extension',
            'fallthrough', 'false', 'final', 'for', 'func', 'if', 'import', 'in', 'init', 'inout',
            'internal', 'is', 'lazy', 'let', 'mutating', 'nonmutating', 'nil', 'open', 'optional',
            'override', 'private', 'protocol', 'public', 'required', 'return', 'self', 'static',
            'struct', 'subscript', 'super', 'switch', 'throw', 'throws', 'true', 'try', 'typealias',
            'var', 'weak', 'where', 'while', 'willSet'
        ]
        self.add_rules(keywords, formats["keyword"])

        types = [
            'Int', 'Double', 'Float', 'String', 'Bool', 'Character', 'Array', 'Dictionary'
        ]
        self.add_rules(types, formats["type"])
        
        # String literals
        self.highlightingRules.append((r'\"[^\"]*\"', formats["string"]))
        
        # Numbers
        self.highlightingRules.append((r'\b[0-9]+\b', formats["numbers"]))
        
        # Single-line comments
        self.highlightingRules.append((r'//.*', formats["comment"]))

        # Multi-line comment highlighting
        self.comment_format = formats["comment"]
        self.comment_start_expression = QRegExp("/\\*")
        self.comment_end_expression = QRegExp("\\*/")

    def create_format(self, color_hex, is_bold=False):
        text_format = QTextCharFormat()
        text_format.setForeground(QColor(color_hex))
        if is_bold:
            text_format.setFontWeight(QFont.Bold)
        return text_format
        
    def add_rules(self, keywords, format):
        for keyword in keywords:
            self.highlightingRules.append((r'\b' + re.escape(keyword) + r'\b', format))

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = re.compile(pattern)
            for match in expression.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), format)
        
        self.setCurrentBlockState(0)
        start_index = 0
        if self.previousBlockState() != 1:
            start_index = self.comment_start_expression.indexIn(text)
        
        while start_index >= 0:
            end_index = self.comment_end_expression.indexIn(text, start_index)
            if end_index == -1:
                self.setCurrentBlockState(1)
                comment_length = len(text) - start_index
            else:
                comment_length = end_index - start_index + self.comment_end_expression.matchedLength()
            
            self.setFormat(start_index, comment_length, self.comment_format)
            start_index = self.comment_start_expression.indexIn(text, start_index + comment_length)


class GoHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlightingRules = []

        formats = {
            "keyword": self.create_format("#C586C0"),       # Purple
            "builtin_func": self.create_format("#DCDCAA"),  # Yellow
            "type": self.create_format("#569CD6"),          # Blue
            "string": self.create_format("#CE9178"),        # Orange
            "comment": self.create_format("#6A9955"),       # Green
            "numbers": self.create_format("#B5CEA8"),       # Light Green
        }
        
        keywords = [
            'break', 'case', 'chan', 'const', 'continue', 'default', 'defer', 'else',
            'fallthrough', 'for', 'func', 'go', 'goto', 'if', 'import', 'interface',
            'map', 'package', 'range', 'return', 'select', 'struct', 'switch', 'type',
            'var'
        ]
        self.add_rules(keywords, formats["keyword"])

        builtin_functions = [
            'make', 'new', 'len', 'cap', 'append', 'copy', 'close', 'delete', 'panic',
            'print', 'println', 'recover'
        ]
        self.add_rules(builtin_functions, formats["builtin_func"])

        types = [
            'bool', 'byte', 'complex64', 'complex128', 'error', 'float32', 'float64',
            'int', 'int8', 'int16', 'int32', 'int64', 'rune', 'string', 'uint',
            'uint8', 'uint16', 'uint32', 'uint64', 'uintptr'
        ]
        self.add_rules(types, formats["type"])
        
        # String literals (double quotes)
        self.highlightingRules.append((r'\"[^\"]*\"', formats["string"]))
        
        # Raw string literals (backticks)
        self.highlightingRules.append((r'`[^`]*`', formats["string"]))

        # Numbers
        self.highlightingRules.append((r'\b[0-9.]+\b', formats["numbers"]))
        
        # Single-line comments
        self.highlightingRules.append((r'//.*', formats["comment"]))

        # Multi-line comment highlighting
        self.comment_format = formats["comment"]
        self.comment_start_expression = QRegExp("/\\*")
        self.comment_end_expression = QRegExp("\\*/")

    def create_format(self, color_hex, is_bold=False):
        text_format = QTextCharFormat()
        text_format.setForeground(QColor(color_hex))
        if is_bold:
            text_format.setFontWeight(QFont.Bold)
        return text_format
        
    def add_rules(self, keywords, format):
        for keyword in keywords:
            self.highlightingRules.append((r'\b' + re.escape(keyword) + r'\b', format))

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = re.compile(pattern)
            for match in expression.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), format)
        
        self.setCurrentBlockState(0)
        start_index = 0
        if self.previousBlockState() != 1:
            start_index = self.comment_start_expression.indexIn(text)
        
        while start_index >= 0:
            end_index = self.comment_end_expression.indexIn(text, start_index)
            if end_index == -1:
                self.setCurrentBlockState(1)
                comment_length = len(text) - start_index
            else:
                comment_length = end_index - start_index + self.comment_end_expression.matchedLength()
            
            self.setFormat(start_index, comment_length, self.comment_format)
            start_index = self.comment_start_expression.indexIn(text, start_index + comment_length)


class CsharpHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlightingRules = []

        # Color palette inspired by VS Code Dark+ theme
        formats = {
            "keyword": self.create_format("#C586C0", is_bold=True),      # Purple: for, if, class, return
            "type_name": self.create_format("#4EC9B0", is_bold=True),    # Teal: string, int, List
            "method_name": self.create_format("#DCDCAA"),                # Yellow: MyFunction(), Console.WriteLine()
            "string": self.create_format("#CE9178"),                     # Orange: "Hello, World!"
            "comment": self.create_format("#6A9955"),                    # Green: // This is a comment
            "numbers": self.create_format("#B5CEA8"),                    # Light Green: 123, 45.6
            "class_struct": self.create_format("#569CD6", is_bold=True), # Blue: class, struct
            "attribute": self.create_format("#9CDCFE"),                  # Light Blue: [Test]
        }
        
        # Keywords
        keywords = [
            'abstract', 'as', 'async', 'await', 'base', 'break', 'case', 'catch', 'checked',
            'const', 'continue', 'default', 'delegate', 'do', 'else', 'enum', 'event', 
            'explicit', 'extern', 'false', 'finally', 'fixed', 'for', 'foreach',
            'goto', 'if', 'implicit', 'in', 'is', 'lock', 'new', 'null', 'out', 'override', 
            'params', 'private', 'protected', 'public', 'readonly', 'ref', 'return', 
            'sealed', 'sizeof', 'stackalloc', 'static', 'this', 'throw', 'true', 'try', 
            'typeof', 'unchecked', 'unsafe', 'using', 'virtual', 'void', 'volatile', 'while', 
            'yield'
        ]
        self.add_rules(keywords, formats["keyword"])

        # Class/Struct/Interface keywords
        class_struct_keywords = [
            'class', 'struct', 'interface'
        ]
        self.add_rules(class_struct_keywords, formats["class_struct"])

        # Built-in types
        types = [
            'bool', 'byte', 'char', 'decimal', 'double', 'float', 'int', 'long', 'object',
            'sbyte', 'short', 'string', 'uint', 'ulong', 'ushort'
        ]
        self.add_rules(types, formats["type_name"])
        
        # String literals (double quotes)
        self.highlightingRules.append((r'\"[^\"]*\"', formats["string"]))
        
        # Verbatim strings
        self.highlightingRules.append((r'@\"[^\"]*\"', formats["string"]))

        # Numbers
        self.highlightingRules.append((r'\b[0-9.]+\b', formats["numbers"]))
        
        # Attributes: [Test], [Serializable]
        self.highlightingRules.append((r'\[.*?\]', formats["attribute"]))

        # Method names (words followed by parentheses)
        self.highlightingRules.append((r'\b[a-zA-Z_][a-zA-Z0-9_]*\s*(?=\()', formats["method_name"]))

        # Single-line comments
        self.highlightingRules.append((r'//.*', formats["comment"]))

        # Multi-line comment highlighting
        self.comment_format = formats["comment"]
        self.comment_start_expression = QRegExp("/\\*")
        self.comment_end_expression = QRegExp("\\*/")

    def create_format(self, color_hex, is_bold=False):
        text_format = QTextCharFormat()
        text_format.setForeground(QColor(color_hex))
        if is_bold:
            text_format.setFontWeight(QFont.Bold)
        return text_format
        
    def add_rules(self, keywords, format):
        for keyword in keywords:
            self.highlightingRules.append((r'\b' + re.escape(keyword) + r'\b', format))

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = re.compile(pattern)
            for match in expression.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, format)
        
        self.setCurrentBlockState(0)
        start_index = 0
        if self.previousBlockState() != 1:
            start_index = self.comment_start_expression.indexIn(text)
        
        while start_index >= 0:
            end_index = self.comment_end_expression.indexIn(text, start_index)
            if end_index == -1:
                self.setCurrentBlockState(1)
                comment_length = len(text) - start_index
            else:
                comment_length = end_index - start_index + self.comment_end_expression.matchedLength()
            
            self.setFormat(start_index, comment_length, self.comment_format)
            start_index = self.comment_start_expression.indexIn(text, start_index + comment_length)


class RustHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlightingRules = []

        formats = {
            "keyword": self.create_format("#C586C0", is_bold=True),
            "type": self.create_format("#569CD6"),
            "function": self.create_format("#DCDCAA"),
            "string": self.create_format("#CE9178"),
            "comment": self.create_format("#6A9955"),
            "numbers": self.create_format("#B5CEA8"),
        }
        
        keywords = [
            'as', 'async', 'await', 'break', 'const', 'continue', 'crate', 'dyn', 'else', 'enum',
            'extern', 'false', 'fn', 'for', 'if', 'impl', 'in', 'let', 'loop', 'match',
            'mod', 'move', 'mut', 'pub', 'ref', 'return', 'self', 'static', 'struct',
            'super', 'trait', 'true', 'type', 'union', 'unsafe', 'use', 'where', 'while'
        ]
        self.add_rules(keywords, formats["keyword"])

        types = [
            'bool', 'char', 'f32', 'f64', 'i8', 'i16', 'i32', 'i64', 'isize', 'str',
            'u8', 'u16', 'u32', 'u64', 'usize'
        ]
        self.add_rules(types, formats["type"])

        # Function names
        self.highlightingRules.append((r'\bfn\s+([a-zA-Z_][a-zA-Z0-9_]*)', formats["function"]))

        # String literals (double quotes)
        self.highlightingRules.append((r'\"[^\"]*\"', formats["string"]))
        
        # Numbers
        self.highlightingRules.append((r'\b[0-9.]+\b', formats["numbers"]))
        
        # Single-line comments
        self.highlightingRules.append((r'//.*', formats["comment"]))

        # Multi-line comment highlighting
        self.comment_format = formats["comment"]
        self.comment_start_expression = QRegExp("/\\*")
        self.comment_end_expression = QRegExp("\\*/")

    def create_format(self, color_hex, is_bold=False):
        text_format = QTextCharFormat()
        text_format.setForeground(QColor(color_hex))
        if is_bold:
            text_format.setFontWeight(QFont.Bold)
        return text_format
        
    def add_rules(self, keywords, format):
        for keyword in keywords:
            self.highlightingRules.append((r'\b' + re.escape(keyword) + r'\b', format))

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = re.compile(pattern)
            for match in expression.finditer(text):
                if pattern == r'\bfn\s+([a-zA-Z_][a-zA-Z0-9_]*)':
                    start, end = match.span(1)
                    self.setFormat(start, end - start, format)
                else:
                    start, end = match.span(0)
                    self.setFormat(start, end - start, format)
        
        self.setCurrentBlockState(0)
        start_index = 0
        if self.previousBlockState() != 1:
            start_index = self.comment_start_expression.indexIn(text)
        
        while start_index >= 0:
            end_index = self.comment_end_expression.indexIn(text, start_index)
            if end_index == -1:
                self.setCurrentBlockState(1)
                comment_length = len(text) - start_index
            else:
                comment_length = end_index - start_index + self.comment_end_expression.matchedLength()
            
            self.setFormat(start_index, comment_length, self.comment_format)
            start_index = self.comment_start_expression.indexIn(text, start_index + comment_length)


class KotlinHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlightingRules = []

        formats = {
            "keyword": self.create_format("#C586C0", is_bold=True),       # Purple
            "type": self.create_format("#569CD6"),                        # Blue
            "function": self.create_format("#DCDCAA"),                    # Yellow
            "string": self.create_format("#CE9178"),                      # Orange
            "comment": self.create_format("#6A9955"),                     # Green
            "numbers": self.create_format("#B5CEA8"),                     # Light Green
        }
        
        keywords = [
            'as', 'as?', 'break', 'by', 'catch', 'class', 'continue', 'do', 'else', 'false',
            'for', 'fun', 'if', 'in', 'is', 'null', 'object', 'package', 'return', 'super',
            'this', 'throw', 'true', 'try', 'typealias', 'var', 'val', 'when', 'while'
        ]
        self.add_rules(keywords, formats["keyword"])

        types = [
            'Any', 'Boolean', 'Byte', 'Char', 'Double', 'Float', 'Int', 'Long', 'Short', 'String'
        ]
        self.add_rules(types, formats["type"])

        # Function names
        self.highlightingRules.append((r'\bfun\s+([a-zA-Z_][a-zA-Z0-9_]*)', formats["function"]))
        
        # String literals
        self.highlightingRules.append((r'\"[^\"]*\"', formats["string"]))
        self.highlightingRules.append((r'\"\"\"[\s\S]*?\"\"\"', formats["string"]))
        
        # Numbers
        self.highlightingRules.append((r'\b[0-9.]+\b', formats["numbers"]))
        
        # Single-line comments
        self.highlightingRules.append((r'//.*', formats["comment"]))

        # Multi-line comment highlighting
        self.comment_format = formats["comment"]
        self.comment_start_expression = QRegExp("/\\*")
        self.comment_end_expression = QRegExp("\\*/")

    def create_format(self, color_hex, is_bold=False):
        text_format = QTextCharFormat()
        text_format.setForeground(QColor(color_hex))
        if is_bold:
            text_format.setFontWeight(QFont.Bold)
        return text_format
        
    def add_rules(self, keywords, format):
        for keyword in keywords:
            self.highlightingRules.append((r'\b' + re.escape(keyword) + r'\b', format))

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = re.compile(pattern)
            for match in expression.finditer(text):
                if pattern == r'\bfun\s+([a-zA-Z_][a-zA-Z0-9_]*)':
                    start, end = match.span(1)
                    self.setFormat(start, end - start, format)
                else:
                    start, end = match.span(0)
                    self.setFormat(start, end - start, format)
        
        self.setCurrentBlockState(0)
        start_index = 0
        if self.previousBlockState() != 1:
            start_index = self.comment_start_expression.indexIn(text)
        
        while start_index >= 0:
            end_index = self.comment_end_expression.indexIn(text, start_index)
            if end_index == -1:
                self.setCurrentBlockState(1)
                comment_length = len(text) - start_index
            else:
                comment_length = end_index - start_index + self.comment_end_expression.matchedLength()
            
            self.setFormat(start_index, comment_length, self.comment_format)
            start_index = self.comment_start_expression.indexIn(text, start_index + comment_length)


class TypeScriptHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlightingRules = []

        formats = {
            "keyword": self.create_format("#C586C0", is_bold=True),       # Purple
            "type": self.create_format("#569CD6"),                        # Blue
            "string": self.create_format("#CE9178"),                      # Orange
            "comment": self.create_format("#6A9955"),                     # Green
            "numbers": self.create_format("#B5CEA8"),                     # Light Green
        }
        
        keywords = [
            'async', 'await', 'break', 'case', 'catch', 'class', 'const', 'continue', 'do',
            'else', 'enum', 'export', 'extends', 'finally', 'for', 'if', 'import', 'in',
            'instanceof', 'new', 'return', 'super', 'switch', 'this', 'throw', 'true',
            'try', 'typeof', 'var', 'void', 'while', 'let', 'interface', 'type', 'implements'
        ]
        self.add_rules(keywords, formats["keyword"])

        types = [
            'string', 'number', 'boolean', 'any', 'void', 'null', 'undefined'
        ]
        self.add_rules(types, formats["type"])

        # String literals (double and single quotes, and backticks for templates)
        self.highlightingRules.append((r'\"[^\"]*\"', formats["string"]))
        self.highlightingRules.append((r'\'[^\']*\'', formats["string"]))
        self.highlightingRules.append((r'`[^`]*`', formats["string"]))
        
        # Numbers
        self.highlightingRules.append((r'\b[0-9.]+\b', formats["numbers"]))
        
        # Single-line comments
        self.highlightingRules.append((r'//.*', formats["comment"]))

        # Multi-line comment highlighting
        self.comment_format = formats["comment"]
        self.comment_start_expression = QRegExp("/\\*")
        self.comment_end_expression = QRegExp("\\*/")

    def create_format(self, color_hex, is_bold=False):
        text_format = QTextCharFormat()
        text_format.setForeground(QColor(color_hex))
        if is_bold:
            text_format.setFontWeight(QFont.Bold)
        return text_format
        
    def add_rules(self, keywords, format):
        for keyword in keywords:
            self.highlightingRules.append((r'\b' + re.escape(keyword) + r'\b', format))

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = re.compile(pattern)
            for match in expression.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, format)
        
        self.setCurrentBlockState(0)
        start_index = 0
        if self.previousBlockState() != 1:
            start_index = self.comment_start_expression.indexIn(text)
        
        while start_index >= 0:
            end_index = self.comment_end_expression.indexIn(text, start_index)
            if end_index == -1:
                self.setCurrentBlockState(1)
                comment_length = len(text) - start_index
            else:
                comment_length = end_index - start_index + self.comment_end_expression.matchedLength()
            
            self.setFormat(start_index, comment_length, self.comment_format)
            start_index = self.comment_start_expression.indexIn(text, start_index + comment_length)


class YamlHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlightingRules = []

        formats = {
            "key": self.create_format("#9CDCFE"),          # Light Blue
            "string_value": self.create_format("#CE9178"), # Orange
            "number_value": self.create_format("#B5CEA8"), # Light Green
            "boolean_null": self.create_format("#569CD6"), # Blue
            "comment": self.create_format("#6A9955"),      # Green
        }
        
        # Keys (words followed by a colon)
        self.highlightingRules.append((r'\b[a-zA-Z0-9_-]+\s*:', formats["key"]))
        
        # String values (in quotes or not)
        self.highlightingRules.append((r'(\'|").*?(\'|")', formats["string_value"]))
        
        # Number values
        self.highlightingRules.append((r'\b[0-9.]+\b', formats["number_value"]))
        
        # Boolean and null values
        self.highlightingRules.append((r'\b(true|false|null)\b', formats["boolean_null"]))
        
        # Comments
        self.highlightingRules.append((r'#.*', formats["comment"]))

    def create_format(self, color_hex, is_bold=False):
        text_format = QTextCharFormat()
        text_format.setForeground(QColor(color_hex))
        if is_bold:
            text_format.setFontWeight(QFont.Bold)
        return text_format

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = re.compile(pattern)
            for match in expression.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), format)


# ------------------ Line Numbers ------------------ #
class LineNumberArea(QWidget):
    """
    Custom widget to display line numbers next to the editor.
    """
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor
        self.setMouseTracking(False)
        self.setStyleSheet("background-color: #252526; color: #858585;")
        self.digits = 1  # عدد الأرقام الافتراضي

    def sizeHint(self):
        """
        Provides a size hint for the widget.
        """
        return QSize(self.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        """
        Draws the line numbers on the widget.
        """
        self.lineNumberAreaPaintEvent(event)

    def lineNumberAreaWidth(self):
        """
        Calculates the required width for the line number area.
        """
        # حساب عدد الأرقام المطلوبة بناءً على عدد الأسطر
        max_lines = max(1, self.code_editor.blockCount())
        digits = 1
        while max_lines >= 10:
            max_lines //= 10
            digits += 1
        
        # تحديث عدد الأرقام إذا تغير
        if digits != self.digits:
            self.digits = digits
            self.updateGeometry()  # إعادة حساب الهندسة
        
        # حساب المساحة المطلوبة مع هامش 10 بكسل من كل جانب
        space = 10 + self.code_editor.fontMetrics().width('9') * self.digits
        return space

    def lineNumberAreaPaintEvent(self, event):
        """
        Paint event for the LineNumberArea widget.
        """
        painter = QPainter(self)
        painter.fillRect(event.rect(), QColor("#252526"))

        block = self.code_editor.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.code_editor.blockBoundingGeometry(block).translated(self.code_editor.contentOffset()).top())
        bottom = top + int(self.code_editor.blockBoundingRect(block).height())

        painter.setPen(QColor("#858585"))
        font_metrics = self.code_editor.fontMetrics()
        line_height = font_metrics.height()
        
        # حساب عرض النص المطلوب لكل رقم مع ترك مسافة متساوية على الجانبين
        text_width = self.width()
        digit_width = font_metrics.width('9')
        total_number_width = self.digits * digit_width
        x_offset = (text_width - total_number_width) // 2

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                # حساب المسافة لمركزة الرقم أفقيًا
                number_width = font_metrics.width(number)
                x_pos = x_offset + (total_number_width - number_width) // 2
                
                painter.drawText(x_pos, top, text_width, line_height,
                                 Qt.AlignVCenter, number)

            block = block.next()
            top = bottom
            bottom = top + int(self.code_editor.blockBoundingRect(block).height())
            block_number += 1


# ------------------ Editor Widget ------------------ #
class EditorWidget(QWidget):
    """A composite widget holding the editor and line number area."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.editor = AutoIndentPlainTextEdit(self)
        self.line_number_area = LineNumberArea(self.editor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.line_number_area)
        layout.addWidget(self.editor)

        # Connect signals for the line numbers
        self.editor.blockCountChanged.connect(self.update_line_number_area_width)
        self.editor.updateRequest.connect(self.update_line_number_area)
        self.editor.cursorPositionChanged.connect(self.highlight_current_line)

        self.update_line_number_area_width(0)

    def update_line_number_area_width(self, _):
        """Update the width of the line number area."""
        # حساب العرض المطلوب وتحديث الهوامش
        width = self.line_number_area.lineNumberAreaWidth()
        self.editor.setViewportMargins(width, 0, 0, 0)
        
        # إعادة رسم منطقة الأرقام
        self.line_number_area.update()

    def update_line_number_area(self, rect, dy):
        """Update the line number area."""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.editor.viewport().rect()):
            self.update_line_number_area_width(0)

    def highlight_current_line(self):
        """Highlight the current line in the editor."""
        extra_selections = []

        if not self.editor.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor("#2A2A2A")
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.editor.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)

        self.editor.setExtraSelections(extra_selections)


# ------------------ Auto Indent Editor ------------------ #
class AutoIndentPlainTextEdit(QPlainTextEdit):
    """
    QPlainTextEdit with an automatic indentation feature and tab to spaces.
    """
    # Define a custom signal to notify parent of text changes
    modified_state_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # Use a monospace font that's commonly available
        fixed_font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        fixed_font.setPointSize(11)
        self.setFont(fixed_font)
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                selection-background-color: #264F78;
                selection-color: #d4d4d4;
                border: none;
            }
        """)
        # Connect text change to emit our custom signal
        self.document().contentsChanged.connect(self._handle_contents_changed)
        self.is_modified = False
        self.syntax_highlighter = None
        self.file_path = None  # مسار الملف المرتبط بهذا المحرر

        # Mapping of opening brackets to their closing counterparts
        self.bracket_pairs = {
            '(': ')',
            '[': ']',
            '{': '}',
            '<': '>',
            '"': '"',
            "'": "'",
            '`': '`'
        }

        # إنشاء قائمة السياق المخصصة
        self.custom_context_menu = QMenu(self)
        self.setup_context_menu()

    def setup_context_menu(self):
        """إعداد قائمة السياق المخصصة بمظهر VS Code"""
        # إعداد ستايل القائمة بحواف مقوسة
        self.custom_context_menu.setStyleSheet("""
            QMenu {
                background-color: #252526;
                border: 1px solid #454545;
                padding: 5px;
                border-radius: 6px;
            }
            QMenu::item {
                color: #cccccc;
                background-color: transparent;
                padding: 5px 25px 5px 25px;
                margin: 2px 5px 2px 5px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #094771;
                color: #ffffff;
                border-radius: 4px;
            }
            QMenu::item:disabled {
                color: #5a5a5a;
                background-color: transparent;
                border-radius: 4px;
            }
            QMenu::separator {
                height: 1px;
                background-color: #454545;
                margin: 5px 8px 5px 8px;
                border-radius: 1px;
            }
            QMenu::indicator {
                width: 13px;
                height: 13px;
                border-radius: 3px;
            }
            QMenu::indicator:checked {
                background-color: #094771;
                border: 1px solid #569cd6;
                border-radius: 3px;
            }
        """)

        # إضافة إجراءات القائمة باللغة الإنجليزية
        actions = [
            ("Undo", "Ctrl+Z", self.undo, self.isUndoAvailable),
            ("Redo", "Ctrl+Y", self.redo, self.isRedoAvailable),
            ("---", None, None, None),  # فاصل
            ("Cut", "Ctrl+X", self.cut, self.can_cut),
            ("Copy", "Ctrl+C", self.copy, self.can_copy),
            ("Paste", "Ctrl+V", self.paste, self.can_paste),
            ("---", None, None, None),  # فاصل
            ("Select All", "Ctrl+A", self.selectAll, lambda: True)
        ]

        for text, shortcut, action, enabled_check in actions:
            if text == "---":
                self.custom_context_menu.addSeparator()
            else:
                menu_action = QAction(text, self)
                if shortcut:
                    menu_action.setShortcut(QKeySequence(shortcut))
                menu_action.triggered.connect(action)
                
                # جعل الإجراء قابلاً للضغط أو غير قابل بناءً على الشرط
                menu_action.setEnabled(enabled_check())
                
                self.custom_context_menu.addAction(menu_action)

    def can_cut(self):
        """التحقق إذا كان القص متاحًا"""
        return self.textCursor().hasSelection() and not self.isReadOnly()

    def can_copy(self):
        """التحقق إذا كان النسخ متاحًا"""
        return self.textCursor().hasSelection()

    def can_paste(self):
        """التحقق إذا كان اللصق متاحًا"""
        clipboard = QApplication.clipboard()
        return clipboard.mimeData().hasText() and not self.isReadOnly()

    def isUndoAvailable(self):
        """التحقق إذا كان التراجع متاحًا"""
        return self.document().isUndoAvailable()

    def isRedoAvailable(self):
        """التحقق إذا كان الإعادة متاحًا"""
        return self.document().isRedoAvailable()

    def contextMenuEvent(self, event):
        """تجاوز حدث قائمة السياق لعرض القائمة المخصصة"""
        # تحديث حالة الإجراءات قبل عرض القائمة
        self.update_context_menu_actions()
        self.custom_context_menu.exec_(event.globalPos())

    def update_context_menu_actions(self):
        """تحديث حالة الإجراءات في قائمة السياق"""
        actions = self.custom_context_menu.actions()
        
        # تحديث حالة كل إجراء
        undo_action = actions[0] if len(actions) > 0 else None
        redo_action = actions[1] if len(actions) > 1 else None
        cut_action = actions[3] if len(actions) > 3 else None
        copy_action = actions[4] if len(actions) > 4 else None
        paste_action = actions[5] if len(actions) > 5 else None
        select_all_action = actions[7] if len(actions) > 7 else None

        if undo_action:
            undo_action.setEnabled(self.isUndoAvailable())
        if redo_action:
            redo_action.setEnabled(self.isRedoAvailable())
        if cut_action:
            cut_action.setEnabled(self.can_cut())
        if copy_action:
            copy_action.setEnabled(self.can_copy())
        if paste_action:
            paste_action.setEnabled(self.can_paste())
        if select_all_action:
            select_all_action.setEnabled(True)  # دائماً متاح

    def _handle_contents_changed(self):
        """
        Internal handler to mark the document as modified and emit the signal.
        """
        if not self.is_modified:
            self.is_modified = True
            self.modified_state_changed.emit()

    def mark_as_saved(self):
        """
        Marks the document as not modified.
        """
        self.is_modified = False
        self.modified_state_changed.emit()

    def set_highlighter(self, highlighter_class):
        """Sets a new syntax highlighter for the document."""
        if self.syntax_highlighter:
            self.syntax_highlighter.setDocument(None)
        
        if highlighter_class:
            self.syntax_highlighter = highlighter_class(self.document())
        else:
            self.syntax_highlighter = None

    def keyPressEvent(self, event):
        """
        Overrides the key press event to handle auto-indentation on 'Enter'
        and convert tabs to 4 spaces.
        """
        # Handle Shift+Tab for unindentation - يجب التحقق من هذا أولاً
        if event.key() == Qt.Key_Backtab:  # Key_Backtab هو Shift+Tab
            cursor = self.textCursor()
            if cursor.hasSelection():
                self.unindent_selected_lines()
                event.accept()
                return
            else:
                event.accept()  # منع السلوك الافتراضي حتى بدون تحديد
                return
        
        # Handle regular Tab key
        if event.key() == Qt.Key_Tab and not (event.modifiers() & Qt.ShiftModifier):
            cursor = self.textCursor()
            
            if cursor.hasSelection():
                # Tab: Add 4 spaces to beginning of each selected line
                self.indent_selected_lines()
                event.accept()
                return
            else:
                # Single tab press - insert 4 spaces
                cursor.insertText(' ' * 4)
                event.accept()
                return
                    
        # Handle Enter key for auto-indentation
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            cursor = self.textCursor()
            # Get the current block (line)
            current_block = cursor.block()
            current_line_text = current_block.text()

            # Count the leading spaces to determine indentation level
            indentation = 0
            for char in current_line_text:
                if char == ' ':
                    indentation += 1
                elif char == '\t':
                    indentation += 4  # Assume tab is 4 spaces
                else:
                    break

            # Insert a newline and the calculated indentation
            cursor.insertText('\n' + ' ' * indentation)
            event.accept()
            return

        # Handle bracket auto-closing
        if event.text() in self.bracket_pairs:
            cursor = self.textCursor()
            selected_text = cursor.selectedText()
            
            if selected_text:
                # If text is selected, wrap it with the brackets
                opening_bracket = event.text()
                closing_bracket = self.bracket_pairs[opening_bracket]
                cursor.insertText(f"{opening_bracket}{selected_text}{closing_bracket}")
                # Move cursor back inside the brackets
                cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, len(closing_bracket))
                self.setTextCursor(cursor)
            else:
                # If no text is selected, insert both brackets and place cursor between them
                opening_bracket = event.text()
                closing_bracket = self.bracket_pairs[opening_bracket]
                cursor.insertText(f"{opening_bracket}{closing_bracket}")
                # Move cursor back between the brackets
                cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, len(closing_bracket))
                self.setTextCursor(cursor)
            event.accept()
            return

        # Handle backspace to remove both brackets if they are empty
        if event.key() == Qt.Key_Backspace:
            cursor = self.textCursor()
            if cursor.hasSelection():
                super().keyPressEvent(event)
                return
                
            # Get current position and text around cursor
            position = cursor.position()
            document = self.document()
            
            # Check if we're between matching brackets
            if position > 0 and position < document.characterCount():
                prev_char = document.characterAt(position - 1)
                next_char = document.characterAt(position)
                
                # Check if previous and next characters form a bracket pair
                for open_bracket, close_bracket in self.bracket_pairs.items():
                    if prev_char == open_bracket and next_char == close_bracket:
                        # Delete both brackets
                        cursor.beginEditBlock()
                        cursor.deleteChar()  # Delete closing bracket
                        cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 1)
                        cursor.deleteChar()  # Delete opening bracket
                        cursor.endEditBlock()
                        self.setTextCursor(cursor)
                        event.accept()
                        return

        # إذا لم نتعامل مع الحدث، نتركه للسلوك الافتراضي
        super().keyPressEvent(event)

    def indent_selected_lines(self):
        """Add 4 spaces to the beginning of each selected line"""
        cursor = self.textCursor()
        start_pos = cursor.selectionStart()
        end_pos = cursor.selectionEnd()
        
        # Get the start and end blocks of the selection
        cursor.setPosition(start_pos)
        start_block = cursor.block()
        cursor.setPosition(end_pos)
        end_block = cursor.block()
        
        # If selection ends at the beginning of a line, don't include that line
        if cursor.positionInBlock() == 0 and end_block != start_block:
            end_block = end_block.previous()
        
        # Begin edit block for undo/redo support
        cursor.beginEditBlock()
        
        # Process each line in the selection
        current_block = start_block
        while current_block.isValid() and current_block.blockNumber() <= end_block.blockNumber():
            cursor.setPosition(current_block.position())
            cursor.insertText(' ' * 4)
            current_block = current_block.next()
        
        # Restore the selection
        cursor.setPosition(start_pos)
        cursor.setPosition(end_pos + (4 * (end_block.blockNumber() - start_block.blockNumber() + 1)), 
                        QTextCursor.KeepAnchor)
        
        cursor.endEditBlock()
        self.setTextCursor(cursor)

    def unindent_selected_lines(self):
        """Remove up to 4 spaces from the beginning of each selected line"""
        cursor = self.textCursor()
        start_pos = cursor.selectionStart()
        end_pos = cursor.selectionEnd()
        
        # Get the start and end blocks of the selection
        cursor.setPosition(start_pos)
        start_block = cursor.block()
        cursor.setPosition(end_pos)
        end_block = cursor.block()
        
        # If selection ends at the beginning of a line, don't include that line
        if cursor.positionInBlock() == 0 and end_block != start_block:
            end_block = end_block.previous()
        
        # Begin edit block for undo/redo support
        cursor.beginEditBlock()
        
        total_removed = 0
        current_block = start_block
        
        # Process each line in the selection
        while current_block.isValid() and current_block.blockNumber() <= end_block.blockNumber():
            line_text = current_block.text()
            spaces_to_remove = 0
            
            # Count leading spaces (up to 4)
            for char in line_text[:4]:
                if char == ' ':
                    spaces_to_remove += 1
                else:
                    break
            
            if spaces_to_remove > 0:
                # Remove the spaces
                cursor.setPosition(current_block.position())
                cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, spaces_to_remove)
                cursor.removeSelectedText()
                total_removed += spaces_to_remove
            
            current_block = current_block.next()
        
        # Adjust selection based on removed spaces
        cursor.setPosition(start_pos)
        new_end_pos = end_pos - total_removed
        cursor.setPosition(new_end_pos, QTextCursor.KeepAnchor)
        
        cursor.endEditBlock()
        self.setTextCursor(cursor)


# ------------------ Find Widget ------------------ #
class FindWidget(QWidget):
    """A widget for search and replace functionality."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QWidget {
                background-color: #252526;
                border: none;
                border-bottom: 1px solid #3c3c3c;
            }
            QLineEdit {
                background-color: #3c3c3c;
                color: #d4d4d4;
                border: none;
                padding: 5px 8px;
                border-radius: 3px;
            }
            QPushButton {
                background-color: transparent;
                color: #ffffff;
                font-weight: bold;
                padding: 4px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QPushButton:pressed {
                background-color: #444444;
            }
            QLabel {
                color: #d4d4d4;
            }
            #close_button {
                font-weight: bold;
                padding: 4px;
            }
            #close_button:hover {
                background-color: #E81123;
                border-radius: 3px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(6)

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        self.search_input.setMinimumWidth(200)

        # Search buttons with clear text
        self.prev_button = QPushButton("<")
        self.prev_button.setToolTip("Previous match")

        self.next_button = QPushButton(">")
        self.next_button.setToolTip("Next match")

        # Results counter
        self.results_label = QLabel("0/0")

        # Close button with clear 'X' text
        self.close_button = QPushButton("X")
        self.close_button.setObjectName("close_button")
        self.close_button.setToolTip("Close Find")

        # Small adjustment for the 'X' button size
        self.close_button.setFixedSize(24, 24)

        layout.addStretch(1)
        layout.addWidget(self.search_input)
        layout.addWidget(self.results_label)
        layout.addWidget(self.prev_button)
        layout.addWidget(self.next_button)
        layout.addWidget(self.close_button)


# ------------------ Custom Tab Widget ------------------ #
class CustomTabWidget(QTabWidget):
    """Custom QTabWidget with double-click to create new file functionality."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.last_click_time = 0
        self.last_click_pos = QPoint()
        self.double_click_threshold = 300  # milliseconds
        self.double_click_distance = 10    # pixels

        # Modified stylesheet to unify close button appearance
        self.setStyleSheet("""
            QTabWidget::pane {
                border-top: 1px solid #252526;
                background-color: #1e1e1e;
            }
            QTabBar::tab {
                background-color: #252526;
                color: #ffffff;
                padding: 8px 20px;
                border: none;
            }
            QTabBar::tab:selected {
                background-color: #1e1e1e;
                border-bottom: 2px solid #569CD6;
            }
            QTabBar::tab:hover {
                background-color: #333333;
            }
            QTabBar::close-button {
                image: none; /* Disable default image */
                background-color: transparent;
                subcontrol-origin: padding;
                subcontrol-position: right;
                width: 15px; /* Adjust size */
                padding: 0px;
                margin-right: 5px; /* Space between text and close button */
            }
            QTabBar::close-button:hover {
                background-color: #E81123;
                border-radius: 3px;
            }
            QTabBar {
                background-color: #252526;
            }
        """)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.tabCloseRequested.connect(self.close_tab)

    def mousePressEvent(self, event):
        """Handle mouse press events for double-click detection."""
        if event.button() == Qt.LeftButton:
            current_time = QDateTime.currentDateTime().toMSecsSinceEpoch()
            current_pos = event.pos()

            # Check if this is a double click
            time_diff = current_time - self.last_click_time
            distance = (current_pos - self.last_click_pos).manhattanLength()

            # Check if clicked on empty tab area
            if (time_diff < self.double_click_threshold and
                distance < self.double_click_distance and
                self.tabBar().tabAt(event.pos()) == -1):
                self.parent.new_file()

            self.last_click_time = current_time
            self.last_click_pos = current_pos

        super().mousePressEvent(event)

    def addTab(self, widget, label):
        index = super().addTab(widget, label)
        close_button = QPushButton("✕")
        close_button.setFixedSize(20, 20)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #ffffff;
                border: none;
                font-size: 14px;
                font-weight: bold;
                padding: 0;
            }
            QPushButton:hover {
                background-color: #E81123;
                border-radius: 3px;
            }
        """)
        close_button.clicked.connect(lambda: self.tabCloseRequested.emit(self.indexOf(widget)))
        self.tabBar().setTabButton(index, self.tabBar().RightSide, close_button)
        return index

    def close_tab(self, index):
        """Handles closing a tab, with a check for unsaved changes."""
        widget = self.widget(index)
        editor = widget.editor if widget else None

        if editor and editor.is_modified:
            response = QMessageBox.warning(self.parent, "Unsaved Changes",
                                           f"File '{self.tabText(index).strip('*')}' has been modified.\nDo you want to save your changes?",
                                           QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            if response == QMessageBox.Cancel:
                return  # Don't close the tab
            elif response == QMessageBox.Save:
                self.parent.save_file(index)

        if widget:
            self.removeTab(index)
            widget.deleteLater()
            # Check if this was the last tab
            if self.count() == 0:
                self.parent.status_bar.hide()


# ------------------ Main Editor ------------------ #
class CodeEditor(QMainWindow):
    """
    Main application window with an editor and tabbed interface.
    """
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Generic Text Editor")
        self.resize(1000, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
        """)

        # Main container widget and layout to hold everything
        self.main_container = QWidget()
        self.main_layout = QVBoxLayout(self.main_container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Custom tab widget to hold multiple editors with double-click functionality
        self.tab_widget = CustomTabWidget(self)
        self.find_widget = FindWidget(self)
        self.find_widget.hide()

        self.main_layout.addWidget(self.find_widget)
        self.main_layout.addWidget(self.tab_widget)
        self.setCentralWidget(self.main_container)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setStyleSheet("QStatusBar { background-color: #333333; color: #ffffff; }")
        self.cursor_label = QLabel("Line: 1, Col: 1")
        self.status_label = QLabel("Saved")
        self.status_bar.addPermanentWidget(self.status_label, 1)
        self.status_bar.addPermanentWidget(self.cursor_label)
        self.status_bar.hide()  # Initially hide the status bar

        # Toolbar - غير قابل للإخفاء
        toolbar = QToolBar("Main Toolbar")
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #333333;
                border: none;
                padding: 5px;
                spacing: 5px;
            }
            QToolButton {
                color: white;
                background-color: transparent;
                border: 1px solid transparent;
                padding: 5px;
            }
            QToolButton:hover {
                background-color: #3C3C3C;
                border: 1px solid #3C3C3C;
            }
        """)
        
        # منع إخفاء شريط الأدوات
        # toolbar.setMovable(False)  # منع تحريك الشريط
        # toolbar.setFloatable(False)  # منع تعويم الشريط
        toolbar.setContextMenuPolicy(Qt.PreventContextMenu)  # منع القائمة السياقية بالزر الأيمن
        
        self.addToolBar(toolbar)

        new_action = QAction("New File", self)
        new_action.triggered.connect(lambda: self.new_file())
        new_action.setShortcut(QKeySequence("Ctrl+N"))
        toolbar.addAction(new_action)

        open_action = QAction("Open", self)
        open_action.triggered.connect(lambda: self.open_file())
        open_action.setShortcut(QKeySequence("Ctrl+O"))
        toolbar.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_file)
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        toolbar.addAction(save_action)

        save_as_action = QAction("Save As", self)
        save_as_action.triggered.connect(self.save_as_file)
        save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        toolbar.addAction(save_as_action)

        # New search action
        find_action = QAction("Find", self)
        find_action.triggered.connect(self.show_find_widget)
        find_action.setShortcut(QKeySequence("Ctrl+F"))
        toolbar.addAction(find_action)

        # Connect find widget signals
        self.find_widget.search_input.textChanged.connect(self.find_text)
        self.find_widget.search_input.returnPressed.connect(lambda: self.find_next())
        self.find_widget.next_button.clicked.connect(self.find_next)
        self.find_widget.prev_button.clicked.connect(self.find_previous)
        self.find_widget.close_button.clicked.connect(self.hide_find_widget)

        # Enable drag and drop
        self.setAcceptDrops(True)

        # Search state variables
        self.search_results = []
        self.current_search_index = -1
        self.last_search_text = ""

        # Initial file
        self.new_file()
        
        # Connect tab change signal
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        # Map file extensions to highlighter classes
        self.highlighters = {
            '.py': PythonHighlighter,
            '.js': JavaScriptHighlighter,
            '.ts': TypeScriptHighlighter,
            '.cpp': CppHighlighter,
            '.h': CppHighlighter, 
            '.html': HtmlHighlighter,
            '.htm': HtmlHighlighter,
            '.css': CssHighlighter,
            '.json': JsonHighlighter,
            '.sh': BashHighlighter,
            '.bash': BashHighlighter,
            '.md': MarkdownHighlighter,
            '.xml': XmlHighlighter,
            '.java': JavaHighlighter,
            '.rb': RubyHighlighter,
            '.php': PhpHighlighter,
            '.sql': SqlHighlighter,
            '.swift': SwiftHighlighter,
            '.go': GoHighlighter,
            '.cs': CsharpHighlighter,
            '.rs': RustHighlighter,
            '.kt': KotlinHighlighter,
            '.yml': YamlHighlighter,
            '.yaml': YamlHighlighter,
        }

    # --- Search Feature ---
    def show_find_widget(self):
        """Shows the find widget and sets focus to it."""
        self.find_widget.show()
        self.find_widget.search_input.setFocus()
        self.find_widget.search_input.selectAll()

    def hide_find_widget(self):
        """Hides the find widget and clears the last search query."""
        self.find_widget.hide()
        self.clear_search_highlights()

    def clear_search_highlights(self):
        """Clear all search highlights from the editor."""
        current_editor = self.get_current_editor()
        if current_editor:
            # Clear extra selections (search highlights)
            current_editor.setExtraSelections([])
            # Restore current line highlight
            self.highlight_current_line()

    def find_all_occurrences(self, text):
        """Find all occurrences of text in the document."""
        current_editor = self.get_current_editor()
        if not current_editor or not text:
            return []

        cursor = current_editor.textCursor()
        cursor.movePosition(QTextCursor.Start)

        occurrences = []
        while True:
            cursor = current_editor.document().find(text, cursor)
            if cursor.isNull():
                break
            occurrences.append((cursor.selectionStart(), cursor.selectionEnd()))

        return occurrences

    def highlight_search_results(self, occurrences):
        """Highlight all search results in the editor."""
        current_editor = self.get_current_editor()
        if not current_editor:
            return

        extra_selections = []

        # Highlight all occurrences
        for start, end in occurrences:
            cursor = QTextCursor(current_editor.document())
            cursor.setPosition(start)
            cursor.setPosition(end, QTextCursor.KeepAnchor)

            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(QColor("#36454F"))  # Dark blue-gray
            selection.format.setForeground(QColor("#FFFFFF"))
            selection.cursor = cursor
            extra_selections.append(selection)

        # Highlight current occurrence
        if 0 <= self.current_search_index < len(occurrences):
            start, end = occurrences[self.current_search_index]
            cursor = QTextCursor(current_editor.document())
            cursor.setPosition(start)
            cursor.setPosition(end, QTextCursor.KeepAnchor)

            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(QColor("#569CD6"))  # Bright blue
            selection.format.setForeground(QColor("#FFFFFF"))
            selection.cursor = cursor
            extra_selections.append(selection)

        current_editor.setExtraSelections(extra_selections)

    def find_text(self, text):
        """Find text in the document and update highlights."""
        if text != self.last_search_text:
            # Reset search if text changed
            self.search_results = self.find_all_occurrences(text)
            self.current_search_index = -1
            self.last_search_text = text

        # Update results label
        total = len(self.search_results)
        if total > 0 and self.current_search_index >= 0:
            self.find_widget.results_label.setText(f"{self.current_search_index + 1}/{total}")
        else:
            self.find_widget.results_label.setText(f"0/{total}")

        # Highlight results
        self.highlight_search_results(self.search_results)

    def find_next(self):
        """Find next occurrence of search text."""
        text = self.find_widget.search_input.text()
        if not text:
            return

        if text != self.last_search_text:
            self.find_text(text)

        if not self.search_results:
            return

        self.current_search_index = (self.current_search_index + 1) % len(self.search_results)
        self.navigate_to_search_result()

    def find_previous(self):
        """Find previous occurrence of search text."""
        text = self.find_widget.search_input.text()
        if not text:
            return

        if text != self.last_search_text:
            self.find_text(text)

        if not self.search_results:
            return

        self.current_search_index = (self.current_search_index - 1) % len(self.search_results)
        self.navigate_to_search_result()

    def navigate_to_search_result(self):
        """Navigate to the current search result."""
        if not self.search_results or self.current_search_index < 0:
            return

        current_editor = self.get_current_editor()
        if not current_editor:
            return

        start, end = self.search_results[self.current_search_index]
        cursor = QTextCursor(current_editor.document())
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.KeepAnchor)
        current_editor.setTextCursor(cursor)
        current_editor.centerCursor()

        # Update highlights and results label
        self.highlight_search_results(self.search_results)
        total = len(self.search_results)
        self.find_widget.results_label.setText(f"{self.current_search_index + 1}/{total}")

    # --- Drag & Drop Methods ---
    def dragEnterEvent(self, event):
        """Accepts the drag event if the item is a file URL."""
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Handles the drop event and opens the dropped file."""
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path:
                self.open_file(file_path)
        event.accept()

    def _get_next_untitled_number(self):
        """
        Finds the lowest available number for a new 'Untitled' tab.
        For example, if 'Untitled-1' and 'Untitled-3' exist, it returns 2.
        """
        used_numbers = set()
        for i in range(self.tab_widget.count()):
            tab_text = self.tab_widget.tabText(i).strip('*')
            if tab_text.startswith("Untitled-"):
                try:
                    num = int(tab_text.split('-')[-1])
                    used_numbers.add(num)
                except (ValueError, IndexError):
                    continue
        
        # Find the first positive integer that's not in the set
        next_number = 1
        while next_number in used_numbers:
            next_number += 1
        
        return next_number

    def new_file(self, content="", path=None):
        """
        Creates a new empty tab with an editor.
        """
        self.status_bar.show()  # Show the status bar if it was hidden

        editor_widget = EditorWidget(self)
        editor = editor_widget.editor
        editor.setPlainText(content)

        # Use a consistent font
        font = QFont("Cascadia Code", 10)
        editor.setFont(font)

        # Disable word wrap and enable horizontal scroll
        editor.setLineWrapMode(QPlainTextEdit.NoWrap)
        editor.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        if path:
            tab_name = os.path.basename(path)
            # Get file extension and apply highlighter
            ext = os.path.splitext(path)[1].lower()
            highlighter_class = self.highlighters.get(ext)
            if highlighter_class:
                editor.set_highlighter(highlighter_class)
            else:
                editor.set_highlighter(None)  # Clear any existing highlighter for unknown file types
            
            # حفظ مسار الملف في المحرر نفسه
            editor.file_path = path
        else:
            new_number = self._get_next_untitled_number()
            tab_name = f"Untitled-{new_number}"
            editor.set_highlighter(None)  # No highlighter for new, untitled files
            editor.file_path = None  # لا يوجد مسار ملف بعد

        tab_index = self.tab_widget.addTab(editor_widget, tab_name)
        self.tab_widget.setCurrentIndex(tab_index)

        # Connect signals for the new tab
        editor.cursorPositionChanged.connect(self.update_status_bar)
        editor.modified_state_changed.connect(self.update_tab_title)

        # لا نحتاج إلى open_files dictionary بعد الآن
        editor.mark_as_saved()

        self.highlight_current_line()
        self.update_status_bar()

    def update_tab_title(self):
        """Updates the tab title to reflect saved or modified status."""
        current_index = self.tab_widget.currentIndex()
        if current_index == -1:
            return

        editor_widget = self.tab_widget.widget(current_index)
        if not editor_widget:
            return

        editor = editor_widget.editor
        if editor.file_path:
            base_name = os.path.basename(editor.file_path)
        else:
            base_name = self.tab_widget.tabText(current_index).strip('*')
            
        if editor.is_modified:
            self.tab_widget.setTabText(current_index, base_name + '*')
            self.status_label.setText("Modified")
        else:
            self.tab_widget.setTabText(current_index, base_name)
            self.status_label.setText("Saved")
        
    def update_status_bar(self):
        """
        Updates the status bar with line and column numbers.
        """
        editor = self.get_current_editor()
        if editor:
            cursor = editor.textCursor()
            line = cursor.blockNumber() + 1
            col = cursor.columnNumber() + 1
            self.cursor_label.setText(f"Line: {line}, Col: {col}")

    def on_tab_changed(self, index):
        """Handles changes in the active tab to update editor state."""
        self.highlight_current_line()
        self.update_status_bar()
        self.update_tab_title()
        # Reset search state when changing tabs
        self.last_search_text = ""
        self.current_search_index = -1
        self.search_results = []
        self.find_widget.results_label.setText("0/0")

    def get_current_editor(self):
        """Returns the editor widget of the current tab."""
        current_widget = self.tab_widget.currentWidget()
        if current_widget:
            return current_widget.editor
        return None

    def highlight_current_line(self):
        """
        Highlights the current line in the active editor.
        """
        editor = self.get_current_editor()
        if editor:
            selection = QTextEdit.ExtraSelection()
            line_color = QColor("#2A2A2A")

            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = editor.textCursor()
            selection.cursor.clearSelection()

            editor.setExtraSelections([selection])

    # ------------------ File Actions ------------------ #
    def open_file(self, path=None):
        """
        Opens a file in a new tab.
        """
        if not path:
            path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*.*);;Python Files (*.py)")

        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Check if the file is already open
                for i in range(self.tab_widget.count()):
                    editor_widget = self.tab_widget.widget(i)
                    if editor_widget and editor_widget.editor.file_path == path:
                        self.tab_widget.setCurrentIndex(i)
                        return
                
                self.new_file(content, path)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not open file: {e}")

    def save_file(self, index=None):
        """
        Saves the content of the current tab.
        """
        # دائماً استخدام التبويب النشط الحالي، تجاهل الفهرس الممرر
        current_index = self.tab_widget.currentIndex()
        
        if current_index == -1:
            return False

        current_widget = self.tab_widget.widget(current_index)
        if not current_widget or not hasattr(current_widget, 'editor'):
            return False

        current_editor = current_widget.editor

        # إذا كان الملف جديداً ولم يتم حفظه من قبل، استخدم Save As
        if current_editor.file_path is None:
            return self.save_as_file(current_index)
        
        path = current_editor.file_path

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(current_editor.toPlainText())
            current_editor.mark_as_saved()
            
            # تحديث عنوان التبويب
            base_name = os.path.basename(path)
            self.tab_widget.setTabText(current_index, base_name)
            self.status_label.setText("Saved")
            self.status_bar.showMessage(f"File saved successfully: {base_name}", 3000)
            return True
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not save file: {e}")
            return False

    def save_as_file(self, index=None):
        """
        Saves the content of the current tab with a new name.
        """
        # دائماً استخدام التبويب النشط الحالي، تجاهل الفهرس الممرر
        current_index = self.tab_widget.currentIndex()
        
        if current_index == -1:
            return False

        current_widget = self.tab_widget.widget(current_index)
        if not current_widget or not hasattr(current_widget, 'editor'):
            return False

        current_editor = current_widget.editor

        # الحصول على الاسم الافتراضي للحفظ
        if current_editor.file_path:
            default_name = os.path.basename(current_editor.file_path)
        else:
            default_name = self.tab_widget.tabText(current_index).strip('*')
        
        path, _ = QFileDialog.getSaveFileName(self, "Save File As", default_name, "All Files (*.*);;Python Files (*.py)")
        
        if not path:
            return False

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(current_editor.toPlainText())
            
            # تحديث مسار الملف في المحرر
            current_editor.file_path = path
            
            # تحديث المميز النحوي بناءً على امتداد الملف الجديد
            ext = os.path.splitext(path)[1].lower()
            highlighter_class = self.highlighters.get(ext)
            if highlighter_class:
                current_editor.set_highlighter(highlighter_class)
            else:
                current_editor.set_highlighter(None)
            
            current_editor.mark_as_saved()
            
            # تحديث عنوان التبويب
            base_name = os.path.basename(path)
            self.tab_widget.setTabText(current_index, base_name)
            self.status_label.setText("Saved")
            
            self.status_bar.showMessage(f"File saved successfully: {base_name}", 3000)
            return True
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not save file: {e}")
            return False
            
    def closeEvent(self, event):
        """Handles closing the application, with a check for unsaved changes."""
        for i in range(self.tab_widget.count() - 1, -1, -1):
            editor_widget = self.tab_widget.widget(i)
            editor = editor_widget.editor if editor_widget else None

            if editor and editor.is_modified:
                self.tab_widget.setCurrentIndex(i)
                response = QMessageBox.warning(self, "Unsaved Changes",
                                               f"File '{self.tab_widget.tabText(i).strip('*')}' has been modified.\nDo you want to save your changes before closing?",
                                               QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
                if response == QMessageBox.Cancel:
                    event.ignore()
                    return
                elif response == QMessageBox.Save:
                    if not self.save_file(i):
                        event.ignore()
                        return
        event.accept()


# ------------------ Main ------------------ #
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set application style to Fusion for a more modern look
    app.setStyle("Fusion")

    # Set application palette to dark theme
    dark_palette = app.palette()
    dark_palette.setColor(dark_palette.Window, QColor(30, 30, 30))
    dark_palette.setColor(dark_palette.WindowText, Qt.white)
    dark_palette.setColor(dark_palette.Base, QColor(25, 25, 25))
    dark_palette.setColor(dark_palette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(dark_palette.ToolTipBase, Qt.white)
    dark_palette.setColor(dark_palette.ToolTipText, Qt.white)
    dark_palette.setColor(dark_palette.Text, Qt.white)
    dark_palette.setColor(dark_palette.Button, QColor(53, 53, 53))
    dark_palette.setColor(dark_palette.ButtonText, Qt.white)
    dark_palette.setColor(dark_palette.BrightText, Qt.red)
    dark_palette.setColor(dark_palette.Link, QColor(42, 130, 218))
    dark_palette.setColor(dark_palette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(dark_palette.HighlightedText, Qt.black)
    app.setPalette(dark_palette)

    # Use a consistent font throughout the application
    app.setFont(QFont("Cascadia Code", 8))

    editor = CodeEditor()
    editor.show()
    sys.exit(app.exec_())