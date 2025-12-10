
import sys
from PyQt6.QtWidgets import QPlainTextEdit, QWidget, QTextEdit
from PyQt6.QtCore import Qt, QRect, QSize
from PyQt6.QtGui import QColor, QPainter, QTextFormat, QFont, QSyntaxHighlighter, QTextCharFormat, QFontDatabase

# Try to import pygments, handle if missing
try:
    from pygments import highlight
    from pygments.lexers import PythonLexer
    from pygments.formatter import Formatter
    from pygments.token import Token, Keyword, Name, Comment, String, Error, Number, Operator, Generic, Literal, Text
    PYGMENTS_AVAILABLE = True
except ImportError:
    PYGMENTS_AVAILABLE = False

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.codeEditor = editor

    def sizeHint(self):
        return QSize(self.codeEditor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.codeEditor.lineNumberAreaPaintEvent(event)

class PygmentsHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Define basic styles for pygments tokens
        self.styles = {
            Token:              QTextCharFormat(),
            
            Keyword:            self.format("#569cd6", "bold"),
            Keyword.Constant:   self.format("#569cd6", "bold"),
            Keyword.Declaration:self.format("#569cd6", "bold"),
            Keyword.Namespace:  self.format("#569cd6", "bold"),
            Keyword.Pseudo:     self.format("#569cd6", "bold"),
            Keyword.Reserved:   self.format("#569cd6", "bold"),
            Keyword.Type:       self.format("#569cd6", "bold"),
            
            Name:               self.format("#d4d4d4"),
            Name.Attribute:     self.format("#9cdcfe"),
            Name.Builtin:       self.format("#4ec9b0"),
            Name.Builtin.Pseudo:self.format("#4ec9b0"),
            Name.Class:         self.format("#4ec9b0"),
            Name.Constant:      self.format("#4fc1ff"),
            Name.Decorator:     self.format("#dcdcaa"),
            Name.Entity:        self.format("#4ec9b0"),
            Name.Exception:     self.format("#4ec9b0"),
            Name.Function:      self.format("#dcdcaa"),
            Name.Label:         self.format("#dcdcaa"),
            Name.Namespace:     self.format("#4ec9b0"),
            Name.Other:         self.format("#d4d4d4"),
            Name.Tag:           self.format("#569cd6"),
            Name.Variable:      self.format("#9cdcfe"),
            Name.Variable.Class:self.format("#9cdcfe"),
            Name.Variable.Global:self.format("#9cdcfe"),
            Name.Variable.Instance:self.format("#9cdcfe"),
            
            String:             self.format("#ce9178"),
            String.Backtick:    self.format("#ce9178"),
            String.Char:        self.format("#ce9178"),
            String.Doc:         self.format("#6a9955"),
            String.Double:      self.format("#ce9178"),
            String.Escape:      self.format("#d7ba7d"),
            String.Heredoc:     self.format("#ce9178"),
            String.Interpol:    self.format("#9cdcfe"),
            String.Other:       self.format("#ce9178"),
            String.Regex:       self.format("#d16969"),
            String.Single:      self.format("#ce9178"),
            String.Symbol:      self.format("#ce9178"),
            
            Number:             self.format("#b5cea8"),
            Number.Float:       self.format("#b5cea8"),
            Number.Hex:         self.format("#b5cea8"),
            Number.Integer:     self.format("#b5cea8"),
            Number.Integer.Long:self.format("#b5cea8"),
            Number.Oct:         self.format("#b5cea8"),
            
            Operator:           self.format("#d4d4d4"),
            Operator.Word:      self.format("#569cd6"),
            
            Comment:            self.format("#6a9955", "italic"),
            Comment.Multiline:  self.format("#6a9955", "italic"),
            Comment.Preproc:    self.format("#6a9955"),
            Comment.Single:     self.format("#6a9955", "italic"),
            Comment.Special:    self.format("#6a9955", "italic"),
            
            Generic.Deleted:    self.format("#d16969"),
            Generic.Emph:       self.format("#d4d4d4", "italic"),
            Generic.Error:      self.format("#f44747"),
            Generic.Heading:    self.format("#d4d4d4", "bold"),
            Generic.Inserted:   self.format("#b5cea8"),
            Generic.Output:     self.format("#d4d4d4"),
            Generic.Prompt:     self.format("#d4d4d4"),
            Generic.Strong:     self.format("#d4d4d4", "bold"),
            Generic.Subheading: self.format("#d4d4d4", "bold"),
            Generic.Traceback:  self.format("#d4d4d4"),
        }
        
    def format(self, color, style=''):
        """Return a QTextCharFormat with the given attributes."""
        _format = QTextCharFormat()
        _format.setForeground(QColor(color))
        if 'bold' in style:
            _format.setFontWeight(QFont.Weight.Bold)
        if 'italic' in style:
            _format.setFontItalic(True)
        return _format

    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text."""
        if not PYGMENTS_AVAILABLE:
            return
            
        lexer = PythonLexer()
        tokens = lexer.get_tokens(text)
        
        # Because pygments returns tokens for the whole text and we only process one block (line) 
        # at a time in Qt, this implementation is simplified. 
        # A proper implementation would need to handle multi-line constructs (like multi-line strings)
        # by managing state. user data, etc. 
        # For this "Mini" version, we'll do a simple per-line lexical analysis 
        # which works for most things except multi-line strings start/end detection across blocks.
        
        index = 0
        for token, content in tokens:
            length = len(content)
            # Find the best match style
            style = self.styles.get(token, self.styles.get(token.parent, None))
            # Just simple fallback loop
            tmp_token = token
            while style is None and tmp_token.parent:
                tmp_token = tmp_token.parent
                style = self.styles.get(tmp_token, None)

            if style:
                self.setFormat(index, length, style)
            
            index += length

class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.lineNumberArea = LineNumberArea(self)
        
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        
        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()
        
        # Setup Font
        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        font.setFamily("Consolas") # Prefer Consolas or Cascadia Code if available
        font.setStyleHint(QFont.StyleHint.Monospace)
        font.setPointSize(11)
        self.setFont(font)
        
        # No line wrap for code usually
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        
        # Syntax Highlighter
        self.highlighter = PygmentsHighlighter(self.document())

    def lineNumberAreaWidth(self):
        digits = 1
        max_val = max(1, self.blockCount())
        while max_val >= 10:
            max_val //= 10
            digits += 1
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def highlightCurrentLine(self):
        extraSelections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor("#2b2b2b") # Slightly lighter than bg
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)

        self.setExtraSelections(extraSelections)

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), QColor("#1e1e1e")) # Match bg or slightly different

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        
        height = self.fontMetrics().height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(QColor("#858585"))
                painter.drawText(0, int(top), self.lineNumberArea.width() - 5, int(height),
                                 Qt.AlignmentFlag.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1
