
import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QSplitter, QTabWidget, QFileDialog, 
                             QMessageBox, QLabel)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QIcon

from styles import STYLESHEET
from file_manager import FileExplorer
from editor import CodeEditor

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Mini Code Editor")
        self.resize(1200, 800)
        
        # Apply global stylesheet
        self.setStyleSheet(STYLESHEET)
        
        # Main Layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Splitter to resize sidebar
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(self.splitter)
        
        # Sidebar (File Explorer)
        self.file_explorer = FileExplorer()
        self.file_explorer.doubleClicked.connect(self.on_file_double_clicked)
        self.splitter.addWidget(self.file_explorer)
        
        # Editor Area (Tabs)
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.splitter.addWidget(self.tabs)
        
        # Set initial splitter sizes (Sidebar: 250px, Editor: rest)
        self.splitter.setSizes([250, 950])
        self.splitter.setCollapsible(0, False) # Don't collapse sidebar completely
        
        # Setup Menu Bar
        self.create_menu_bar()
        
        # Status Bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")
        self.status_bar.setStyleSheet("background-color: #007acc; color: white;")
        
    def create_menu_bar(self):
        menu_bar = self.menuBar()
        
        # File Menu
        file_menu = menu_bar.addMenu("File")
        
        open_action = QAction("Open Folder...", self)
        open_action.triggered.connect(self.open_folder)
        file_menu.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_current_file)
        file_menu.addAction(save_action)
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View Menu
        view_menu = menu_bar.addMenu("View")
        toggle_sidebar = QAction("Toggle Sidebar", self)
        toggle_sidebar.setShortcut("Ctrl+B")
        toggle_sidebar.triggered.connect(self.toggle_sidebar)
        view_menu.addAction(toggle_sidebar)

    def open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Open Folder")
        if folder:
            self.file_explorer.setRootIndex(self.file_explorer.model.index(folder))
            self.status_bar.showMessage(f"Opened: {folder}")

    def on_file_double_clicked(self, index):
        path = self.file_explorer.model.filePath(index)
        if os.path.isfile(path):
            self.open_file(path)

    def open_file(self, path):
        # Check if file is already open
        for i in range(self.tabs.count()):
            if self.tabs.tabToolTip(i) == path:
                self.tabs.setCurrentIndex(i)
                return
        
        # Open file
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file: {e}")
            return
            
        editor = CodeEditor()
        editor.setPlainText(content)
        
        # Add tab
        filename = os.path.basename(path)
        index = self.tabs.addTab(editor, filename)
        self.tabs.setTabToolTip(index, path)
        self.tabs.setCurrentIndex(index)
        self.status_bar.showMessage(f"Opened file: {filename}")

    def save_current_file(self):
        current_index = self.tabs.currentIndex()
        if current_index == -1:
            return
            
        editor = self.tabs.widget(current_index)
        path = self.tabs.tabToolTip(current_index)
        
        if not path:
            # Save As (not implemented for simplicity for now, or just fallback)
            return
            
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(editor.toPlainText())
            self.status_bar.showMessage(f"Saved: {os.path.basename(path)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file: {e}")

    def close_tab(self, index):
        self.tabs.removeTab(index)

    def toggle_sidebar(self):
        if self.file_explorer.isVisible():
            self.file_explorer.hide()
        else:
            self.file_explorer.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set app style hints if needed
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())
