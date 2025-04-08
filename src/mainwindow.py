


import os
import json
from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QAction, QFileDialog, 
                            QDockWidget, QListWidget, QListWidgetItem, QMenu,
                            QMessageBox, QVBoxLayout, QWidget)
from PyQt5.QtCore import Qt, QMimeData, QPoint
from PyQt5.QtGui import QIcon, QDrag, QPixmap, QPainter
from nodes import NodeEditor, InputNode, OutputNode, WriteOutputNode, AndNode, OrNode, NotNode, NandNode, NorNode, XorNode, XnorNode

class DraggableNodeListWidget(QListWidget):
    """Custom QListWidget that handles starting node drags properly"""
    def startDrag(self, supportedActions):
        item = self.currentItem()
        if item:
            node_class_name = item.data(Qt.UserRole)
            
            mime_data = QMimeData()
            
            mime_data.setText(node_class_name) 
            
            drag = QDrag(self)
            drag.setMimeData(mime_data)
            
            
            pixmap = QPixmap(100, 30)
            pixmap.fill(Qt.gray) 
            painter = QPainter(pixmap)
            painter.setPen(Qt.white)
            painter.drawText(pixmap.rect(), Qt.AlignCenter, item.text())
            painter.end()
            drag.setPixmap(pixmap)
            
            drag.setHotSpot(QPoint(pixmap.width() // 2, pixmap.height() // 2)) 
            
            
            drag.exec_(Qt.CopyAction)

class MainWindow(QMainWindow):
    """Main window for the Logic Gate Simulator application"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Logic Gate Simulator")
        self.setGeometry(100, 100, 1200, 800)
        
        
        self.initUI()
        
    def initUI(self):
        """Initialize the user interface"""
        
        
        self.tabWidget = QTabWidget()
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.tabCloseRequested.connect(self.closeTab)
        self.setCentralWidget(self.tabWidget)
        
        
        self.createNodeList()
        
        
        self.createMenuBar()
        
        self.changeTheme("dark")
        
        
        self.newTab()
    
    def createMenuBar(self):
        """Create the application menu bar"""
        
        
        fileMenu = self.menuBar().addMenu("File")
        
        newAction = QAction("New", self)
        newAction.setShortcut("Ctrl+N")
        newAction.triggered.connect(self.newTab)
        fileMenu.addAction(newAction)
        
        openAction = QAction("Open", self)
        openAction.setShortcut("Ctrl+O")
        openAction.triggered.connect(self.openFile)
        fileMenu.addAction(openAction)
        
        saveAction = QAction("Save", self)
        saveAction.setShortcut("Ctrl+S")
        saveAction.triggered.connect(self.saveFile)
        fileMenu.addAction(saveAction)
        
        fileMenu.addSeparator()
        
        exitAction = QAction("Exit", self)
        exitAction.setShortcut("Ctrl+Q")
        exitAction.triggered.connect(self.close)
        fileMenu.addAction(exitAction)
        
        
        editMenu = self.menuBar().addMenu("Edit")
        
        undoAction = QAction("Undo", self)
        undoAction.setShortcut("Ctrl+Z")
        undoAction.triggered.connect(self.undo)
        editMenu.addAction(undoAction)
        
        redoAction = QAction("Redo", self)
        redoAction.setShortcut("Ctrl+Y")
        redoAction.triggered.connect(self.redo)
        editMenu.addAction(redoAction)
        
        editMenu.addSeparator()
        
        cutAction = QAction("Cut", self)
        cutAction.setShortcut("Ctrl+X")
        cutAction.triggered.connect(self.cut)
        editMenu.addAction(cutAction)
        
        copyAction = QAction("Copy", self)
        copyAction.setShortcut("Ctrl+C")
        copyAction.triggered.connect(self.copy)
        editMenu.addAction(copyAction)
        
        pasteAction = QAction("Paste", self)
        pasteAction.setShortcut("Ctrl+V")
        pasteAction.triggered.connect(self.paste)
        editMenu.addAction(pasteAction)
        
        deleteAction = QAction("Delete", self)
        deleteAction.setShortcut("Del")
        deleteAction.triggered.connect(self.delete)
        editMenu.addAction(deleteAction)
        
        
        windowMenu = self.menuBar().addMenu("Window")
        
        lightThemeAction = QAction("Light Theme", self)
        lightThemeAction.triggered.connect(lambda: self.changeTheme("light"))
        windowMenu.addAction(lightThemeAction)
        
        darkThemeAction = QAction("Dark Theme", self)
        darkThemeAction.triggered.connect(lambda: self.changeTheme("dark"))
        windowMenu.addAction(darkThemeAction)
    
    def createNodeList(self):
        """Create the side panel with the list of available nodes"""
        
        
        self.nodeDock = QDockWidget("Nodes", self)
        self.nodeDock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        
        nodeListContainer = QWidget()
        layout = QVBoxLayout(nodeListContainer)
        
        
        self.nodeList = DraggableNodeListWidget() 
        self.nodeList.setDragEnabled(True)
        
        
        node_types = [
            {"name": "Input", "class": InputNode},
            {"name": "Output", "class": OutputNode},
            {"name": "Write Output", "class": WriteOutputNode},
            {"name": "AND", "class": AndNode},
            {"name": "OR", "class": OrNode},
            {"name": "NOT", "class": NotNode},
            {"name": "NAND", "class": NandNode},
            {"name": "NOR", "class": NorNode},
            {"name": "XOR", "class": XorNode},
            {"name": "XNOR", "class": XnorNode}
        ]
        
        for node_type in node_types:
            item = QListWidgetItem(node_type["name"])
            item.setData(Qt.UserRole, node_type["class"].__name__)
            self.nodeList.addItem(item)
        
        
        
        
        
        
        
        layout.addWidget(self.nodeList)
        nodeListContainer.setLayout(layout)
        
        self.nodeDock.setWidget(nodeListContainer)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.nodeDock)
    
    
    def newTab(self):
        """Create a new tab with a node editor"""
        
        editor = NodeEditor()
        index = self.tabWidget.addTab(editor, f"Untitled {self.tabWidget.count() + 1}")
        self.tabWidget.setCurrentIndex(index)
    
    def closeTab(self, index):
        """Close the tab at the given index"""
        
        
        editor = self.tabWidget.widget(index)
        if editor.hasUnsavedChanges():
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "This tab has unsaved changes. Do you want to save them?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Save:
                if not self.saveFile():
                    return
            elif reply == QMessageBox.Cancel:
                return
        
        self.tabWidget.removeTab(index)
        
        
        
        
    
    def getCurrentEditor(self):
        """Get the currently active node editor"""
        if self.tabWidget.count() > 0:
             return self.tabWidget.currentWidget()
        return None
    
    def openFile(self):
        """Open a circuit file"""
        
        filePath, _ = QFileDialog.getOpenFileName(
            self, "Open Circuit", "", "Circuit Files (*.circuit);;All Files (*)"
        )
        
        if filePath:
            try:
                with open(filePath, 'r') as f:
                    data = json.load(f)
                
                editor = NodeEditor()
                editor.loadFromJson(data)
                
                
                filename = os.path.basename(filePath)
                index = self.tabWidget.addTab(editor, filename)
                self.tabWidget.setCurrentIndex(index)
                
                editor.setFilePath(filePath)
                editor.setUnsavedChanges(False) 
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file: {str(e)}")
    
    def saveFile(self):
        """Save the current circuit to a file"""
        
        editor = self.getCurrentEditor()
        if editor is None:
            return False
        
        filePath = editor.getFilePath()
        
        if not filePath:
            filePath, _ = QFileDialog.getSaveFileName(
                self, "Save Circuit", "", "Circuit Files (*.circuit);;All Files (*)"
            )
            
            if not filePath:
                return False
        
        try:
            data = editor.saveToJson()
            
            with open(filePath, 'w') as f:
                json.dump(data, f, indent=4)
            
            
            filename = os.path.basename(filePath)
            self.tabWidget.setTabText(self.tabWidget.currentIndex(), filename)
            
            editor.setFilePath(filePath)
            editor.setUnsavedChanges(False)
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")
            return False
    
    def undo(self):
        """Undo the last action in the current editor"""
        
        editor = self.getCurrentEditor()
        if editor:
            editor.undo()
    
    def redo(self):
        """Redo the last undone action in the current editor"""
        
        editor = self.getCurrentEditor()
        if editor:
            editor.redo()
    
    def cut(self):
        """Cut the selected nodes in the current editor"""
        
        editor = self.getCurrentEditor()
        if editor:
            editor.cut()
    
    def copy(self):
        """Copy the selected nodes in the current editor"""
        
        editor = self.getCurrentEditor()
        if editor:
            editor.copy()
    
    def paste(self):
        """Paste the copied nodes in the current editor"""
        
        editor = self.getCurrentEditor()
        if editor:
            editor.paste()
    
    def delete(self):
        """Delete the selected nodes in the current editor"""
        
        editor = self.getCurrentEditor()
        if editor:
            editor.delete()
    
    def changeTheme(self, theme):
        """Change the application theme"""
        
        try:
            
            current_dir = os.path.dirname(os.path.abspath(__file__))
            resources_dir = os.path.join(os.path.dirname(current_dir), "resources")
            
            if theme == "dark":
                style_path = os.path.join(resources_dir, "dark_theme.qss")
            else:
                style_path = os.path.join(resources_dir, "light_theme.qss")
                
            with open(style_path, "r") as f:
                style = f.read()
                
            self.setStyleSheet(style)
        except FileNotFoundError as e:
            QMessageBox.warning(self, "Warning", f"{theme.capitalize()} theme file not found. Error: {str(e)}")
            
    def closeEvent(self, event):
        """Handle application close event to check for unsaved changes"""
        
        
        for i in range(self.tabWidget.count()):
            editor = self.tabWidget.widget(i)
            if editor.hasUnsavedChanges():
                
                self.tabWidget.setCurrentIndex(i)
                
                reply = QMessageBox.question(
                    self, "Unsaved Changes",
                    f"Tab '{self.tabWidget.tabText(i)}' has unsaved changes. Do you want to save them?",
                    QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
                )
                
                if reply == QMessageBox.Save:
                    if not self.saveFile():
                        
                        event.ignore()
                        return
                elif reply == QMessageBox.Cancel:
                    
                    event.ignore()
                    return
        
        
        event.accept()
