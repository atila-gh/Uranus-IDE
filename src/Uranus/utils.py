from PyQt5.QtWidgets import QWidget, QTreeView, QInputDialog, QMenu , QAction , QApplication , QMessageBox , QFileIconProvider , QLineEdit , QVBoxLayout
from PyQt5.QtCore import Qt, QPoint, QSize , pyqtSignal , QModelIndex
from PyQt5.QtGui import QCursor,QIcon
from PyQt5.QtWidgets import QFileSystemModel
import shutil , os , stat


from Uranus.SettingWindow import load_setting
# Override Tree View Standard Class

class CustomIconProvider(QFileIconProvider):


    def icon(self, file_info):
        if file_info.isDir():
            icon_path = os.path.join(os.path.dirname(__file__), "image", "folder.png")
            return QIcon(icon_path)  

        ext = file_info.suffix().lower()

        if ext == "py":
            icon_path = os.path.join(os.path.dirname(__file__), "image", "python_icon.png")
            return QIcon(icon_path)

        elif ext == "ipynb":
            icon_path = os.path.join(os.path.dirname(__file__), "image", "ipynb_icon.png")
            return QIcon(icon_path)
        
        elif ext == "txt":
            icon_path = os.path.join(os.path.dirname(__file__), "image", "txt.png")
            return QIcon(icon_path)
        
        elif ext == "json":
            icon_path = os.path.join(os.path.dirname(__file__), "image", "json.png")
            return QIcon(icon_path)
        
        elif ext == "csv":
            icon_path = os.path.join(os.path.dirname(__file__), "image", "csv.png")
            return QIcon(icon_path)
        
        elif ext == "db":
            icon_path = os.path.join(os.path.dirname(__file__), "image", "db.png")
            return QIcon(icon_path)
        
        elif ext == "png" or ext == 'jpg':
            icon_path = os.path.join(os.path.dirname(__file__), "image", "image.png")
            return QIcon(icon_path)
        
        else:
            return QIcon(os.path.join(os.path.dirname(__file__), "image", "file_unknown.png"))




class FileTreePanel(QWidget):
    """
    Composite widget for Uranus IDE's file explorer panel.

    Displays the current working directory above the file tree,
    allowing users to see and navigate their project structure clearly.

    Components:
    - QLineEdit (read-only): Shows current path.
    - FileTreeView: Interactive tree view of filesystem.

    Automatically updates path display when root changes.
    """
    pathChanged = pyqtSignal(str)


    def __init__(self):
        super().__init__()

        self.tree = FileTreeView()
        self.path_display = QLineEdit()
        self.path_display.setReadOnly(True)
        self.path_display.setText(self.tree.path)
        self.path_display.setStyleSheet("""
            QLineEdit {
                background-color: #f0f0f0;
                font-weight: bold;
                padding: 4px;
                border: none;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.addWidget(self.path_display)
        layout.addWidget(self.tree)
        self.setLayout(layout)

        # Connect signal to update path display if root changes
        self.tree.pathChanged.connect(self.path_display.setText)

   


class FileTreeView(QTreeView):
   


    """
        A customized file explorer widget for Uranus IDE, extending QTreeView.

        This class provides an interactive tree-based view of the filesystem with enhanced features
    for file and folder management. It supports inline editing, custom icons, keyboard shortcuts,
    and context menus for common operations.

        Features:
        - Displays filesystem using QFileSystemModel with custom icons for .py and .ipynb files.
        - Supports renaming, deleting, copying, pasting, and creating folders via keyboard or context menu.
        - Automatically loads the last accessed path from settings.
        - Hides extra columns for a cleaner UI (size, type, date modified).
        - Integrates with clipboard for path copy/paste operations.
        - Handles folder expansion/collapse via Enter key.

        Keyboard Shortcuts:
        - Delete: Remove selected file/folder.
        - Ctrl+C: Copy path to clipboard.
        - Ctrl+V: Paste copied item into selected directory.
        - F2: Rename selected item.
        - Enter: Expand/collapse folder.

        Context Menu Actions:
        - Open: Launch file/folder using system default.
        - Delete: Remove item with confirmation.
        - Rename: Inline rename with validation.
        - New Folder: Create and rename a new folder.
        - Copy Path: Copy full path to clipboard.
        - Paste: Paste file/folder from clipboard.

        Usage:
        Used as the left-side dock widget in MainWindow to navigate and manage project files.
        Automatically reflects changes in the filesystem and supports direct interaction.
        """
    
    pathChanged = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        setting = load_setting()

        # Set initial path
        self.path = setting.get('last_path', os.getcwd())
        self.project_root = self.path

        # Configure model
        self.fs_model = QFileSystemModel()
        self.fs_model.setRootPath(self.path)
        self.fs_model.setIconProvider(CustomIconProvider())

        # Apply model
        self.setModel(self.fs_model)
        self.setRootIndex(self.fs_model.index(self.path))
        self.setIconSize(QSize(24, 24))
        self.fs_model.setReadOnly(False)
        self.setEditTriggers(QTreeView.EditKeyPressed | QTreeView.SelectedClicked)

        # Clean UI
        self.setHeaderHidden(True)
        self.setColumnHidden(1, True)
        self.setColumnHidden(2, True)
        self.setColumnHidden(3, True)

        # Context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        # ✅ Fix: update path immediately on any selection change
        self.selectionModel().selectionChanged.connect(self._on_selection_changed)

    # ------------------------------------------------------------
    # Selection Handling
    # ------------------------------------------------------------
    def _on_selection_changed(self, selected, deselected):
        """Triggered whenever a new file/folder is selected."""
        if selected.indexes():
            index = selected.indexes()[0]
            self.on_item_selected(index)

    def on_item_selected(self, index):
        """Update path when a tree item is selected."""
        path = self.fs_model.filePath(index)
        if not os.path.commonpath([path, self.project_root]) == self.project_root:
            return
        self.path = path
        self.pathChanged.emit(path)

    # ------------------------------------------------------------
    # Keyboard Events
    # ------------------------------------------------------------
    def keyPressEvent(self, event):
        index = self.currentIndex()
        if not index.isValid():
            return

        path = self.fs_model.filePath(index)

        if event.key() == Qt.Key_Delete:
            self.delete_item()
        elif event.key() == Qt.Key_C and event.modifiers() == Qt.ControlModifier:
            QApplication.clipboard().setText(path)
        elif event.key() == Qt.Key_V and event.modifiers() == Qt.ControlModifier:
            self.paste_item(path)
        elif event.key() == Qt.Key_F2:
            self.rename_item()
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if os.path.isdir(path):
                if self.isExpanded(index):
                    self.collapse(index)
                else:
                    self.expand(index)
            else:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)

    # ------------------------------------------------------------
    # Context Menu
    # ------------------------------------------------------------
    def show_context_menu(self, position: QPoint):
        index = self.indexAt(position)
        if not index.isValid():
            return

        path = self.fs_model.filePath(index)
        menu = QMenu()

        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_item)
        menu.addAction(open_action)

      
        add_file_action = QAction("Add File", self)
        add_file_action.triggered.connect(self.create_file)
        menu.addAction(add_file_action)

        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(self.delete_item)
        menu.addAction(delete_action)

        rename_action = QAction("Rename", self)
        rename_action.triggered.connect(self.rename_item)
        menu.addAction(rename_action)

        new_folder_action = QAction("New Folder", self)
        new_folder_action.triggered.connect(self.create_folder)
        menu.addAction(new_folder_action)

        copy_action = QAction("Copy Path", self)
        copy_action.triggered.connect(lambda: QApplication.clipboard().setText(path))
        menu.addAction(copy_action)

        paste_action = QAction("Paste", self)
        paste_action.triggered.connect(lambda: self.paste_item(path))
        menu.addAction(paste_action)

        menu.exec_(QCursor.pos())

    # ------------------------------------------------------------
    # File Operations
    # ------------------------------------------------------------
    def create_file(self):
        """Create a new untitled .ipynb file in the selected folder."""

        index = self.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Warning", "No item selected.")
            return

        path = self.fs_model.filePath(index)

        target_dir = path if os.path.isdir(path) else os.path.dirname(path)
        if not os.path.exists(target_dir):
            QMessageBox.warning(self, "Warning", "Please select a valid folder first.")
            return

        base_name = "untitled.ipynb"
        new_file_path = os.path.join(target_dir, base_name)
        counter = 1
        while os.path.exists(new_file_path):
            new_file_path = os.path.join(target_dir, f"untitled_{counter}.ipynb")
            counter += 1

        try:
            with open(new_file_path, "w", encoding="utf-8") as f:
                f.write("")  # create empty file
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not create file:\n{e}")
            return

        index = self.fs_model.index(new_file_path)
        if index.isValid():
            self.setCurrentIndex(index)
            self.edit(index)

    def open_item(self, path):
        index = self.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Warning", "No item selected.")
            return

        path = self.fs_model.filePath(index)
        try:
            os.startfile(path)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open:\n{e}")

    def delete_item(self):
        index = self.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Warning", "No item selected.")
            return

        path = self.fs_model.filePath(index)


        reply = QMessageBox.question(self, "Delete", f"Are you sure you want to delete?\n{path}")
        if reply == QMessageBox.Yes:
            try:
                if os.path.isfile(path):
                    os.remove(path)
                elif os.path.isdir(path):
                    # handle read-only files and folders
                    def on_rm_error(func, path, exc_info):
                        os.chmod(path, stat.S_IWRITE)
                        func(path)
                    shutil.rmtree(path, onerror=on_rm_error)

                self.clearSelection()
                self.setCurrentIndex(QModelIndex())
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not delete:\n{e}")

    def rename_item(self):
        index = self.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Warning", "No item selected.")
            return

        path = self.fs_model.filePath(index)
        base_dir = os.path.dirname(path)
        old_name = os.path.basename(path)
        new_name, ok = QInputDialog.getText(self, "Rename", "Enter new name:", text=old_name)
        if ok and new_name:
            new_path = os.path.join(base_dir, new_name)
            try:
                os.rename(path, new_path)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not rename:\n{e}")

    def create_folder(self):
        index = self.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Warning", "No item selected.")
            return

        path = self.fs_model.filePath(index)
        target_dir = path if os.path.isdir(path) else os.path.dirname(path)
        if target_dir and os.path.exists(target_dir):
            current_dir = target_dir
        else:
            current_dir = os.getcwd()

        temp_folder_name = "NewFolder"
        temp_folder_path = os.path.join(current_dir, temp_folder_name)
        counter = 1
        while os.path.exists(temp_folder_path):
            temp_folder_path = os.path.join(current_dir, f"NewFolder_{counter}")
            counter += 1

        try:
            os.mkdir(temp_folder_path)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not create folder:\n{e}")
            return

        index = self.fs_model.index(temp_folder_path)
        if index.isValid():
            self.setCurrentIndex(index)
            self.edit(index)

    def paste_item(self, target_path):
        index = self.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Warning", "No item selected.")
            return

       
        source = QApplication.clipboard().text()
        if not os.path.exists(source):
            QMessageBox.warning(self, "Error", "Clipboard does not contain a valid path.")
            return

        try:
            base_name = os.path.basename(source)
            target_dir = target_path if os.path.isdir(target_path) else os.path.dirname(target_path)
            dest_path = os.path.join(target_dir, base_name)

            if os.path.isfile(source):
                shutil.copy2(source, dest_path)
            elif os.path.isdir(source):
                shutil.copytree(source, dest_path)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not paste:\n{e}")

    # ------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------
    def set_root_path(self, new_path):
        self.path = new_path
        self.project_root = new_path
        self.fs_model.setRootPath(new_path)
        self.setRootIndex(self.fs_model.index(new_path))
        self.pathChanged.emit(new_path)
   

    # def create_file_selected(self):
    #     index = self.currentIndex()
    #     if not index.isValid():
    #         return
    #     path = self.fs_model.filePath(index)
    #     self.create_file(path)