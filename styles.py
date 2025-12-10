
# VS Code Dark Theme Colors
COLORS = {
    "background": "#1e1e1e",
    "sidebar": "#252526",
    "sidebar_header": "#383838",
    "editor_bg": "#1e1e1e",
    "text_color": "#d4d4d4",
    "selection": "#264f78",
    "border": "#2b2b2b",  # Slightly darker border
    "hover": "#2a2d2e",
    "active_tab": "#1e1e1e",
    "inactive_tab": "#2d2d2d",
    "scrollbar": "#424242",
    "scrollbar_hover": "#4f4f4f",
    "sidebar_selected": "#37373d",
    "line_number_bg": "#1e1e1e",
    "line_number_color": "#858585"
}

STYLESHEET = f"""
QMainWindow {{
    background-color: {COLORS['background']};
    color: {COLORS['text_color']};
}}

/* Tab Widget */
QTabWidget::pane {{
    border: 1px solid {COLORS['border']};
    background-color: {COLORS['editor_bg']};
}}

QTabBar::tab {{
    background-color: {COLORS['inactive_tab']};
    color: #969696;
    padding: 8px 12px;
    border-right: 1px solid {COLORS['border']};
    border-bottom: 1px solid {COLORS['border']};
}}

QTabBar::tab:selected {{
    background-color: {COLORS['active_tab']};
    color: {COLORS['text_color']};
    border-top: 1px solid #007acc; /* Active tab visual indicator */
    border-bottom: 1px solid {COLORS['active_tab']};
}}

QTabBar::tab:hover {{
    background-color: {COLORS['active_tab']};
}}

/* Tree View (File Explorer) */
QTreeView {{
    background-color: {COLORS['sidebar']};
    color: {COLORS['text_color']};
    border: none;
    outline: 0;
}}

QTreeView::item {{
    padding: 2px;
}}

QTreeView::item:hover {{
    background-color: {COLORS['hover']};
}}

QTreeView::item:selected {{
    background-color: {COLORS['sidebar_selected']};
    border-left: 2px solid #007acc;
}}

QHeaderView::section {{
    background-color: {COLORS['sidebar_header']};
    color: {COLORS['text_color']};
    padding: 4px;
    border: none;
}}

/* Scrollbars */
QScrollBar:vertical {{
    border: none;
    background: {COLORS['background']};
    width: 12px;
    margin: 0px 0px 0px 0px;
}}

QScrollBar::handle:vertical {{
    background: {COLORS['scrollbar']};
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background: {COLORS['scrollbar_hover']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    border: none;
    background: {COLORS['background']};
    height: 12px;
}}

QScrollBar::handle:horizontal {{
    background: {COLORS['scrollbar']};
    min-width: 20px;
}}

QScrollBar::handle:horizontal:hover {{
    background: {COLORS['scrollbar_hover']};
}}

/* Menu Bar */
QMenuBar {{
    background-color: {COLORS['background']};
    color: {COLORS['text_color']};
}}

QMenuBar::item {{
    background-color: transparent;
    padding: 4px 10px;
}}

QMenuBar::item:selected {{
    background-color: {COLORS['sidebar_selected']};
}}

QMenu {{
    background-color: {COLORS['sidebar']};
    color: {COLORS['text_color']};
    border: 1px solid {COLORS['border']};
}}

QMenu::item {{
    padding: 4px 20px;
}}

QMenu::item:selected {{
    background-color: {COLORS['selection']};
}}

/* Splitter */
QSplitter::handle {{
    background-color: {COLORS['background']};
}}
"""
