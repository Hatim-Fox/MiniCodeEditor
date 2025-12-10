
import os
from PyQt6.QtWidgets import QTreeView, QHeaderView
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtCore import Qt, QDir

class FileExplorer(QTreeView):
    def __init__(self, start_path=None):
        super().__init__()
        
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.rootPath())
        # Filter to show only files and directories, no hidden files unless needed
        self.model.setFilter(QDir.Filter.NoDotAndDotDot | QDir.Filter.AllDirs | QDir.Filter.Files)
        
        self.setModel(self.model)
        
        if start_path and os.path.exists(start_path):
            self.setRootIndex(self.model.index(start_path))
        else:
            self.setRootIndex(self.model.index(QDir.currentPath()))
            
        # Hide unnecessary columns (Size, Type, Date Modified) for a cleaner side-bar look
        self.hideColumn(1)
        self.hideColumn(2)
        self.hideColumn(3)
        
        # Header setup
        self.setHeaderHidden(True)
        
        # Visual tweaks
        self.setAnimated(True)
        self.setIndentation(20)
        self.setSortingEnabled(True)
