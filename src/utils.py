import shutil , os , stat ,platform , subprocess


from PyQt5.QtWidgets import QWidget, QTreeView, QInputDialog, QMenu , QAction ,QAbstractItemView , QApplication , QMessageBox , QFileIconProvider , QLineEdit , QVBoxLayout
from PyQt5.QtCore import Qt, QPoint, QSize , pyqtSignal , QModelIndex
from PyQt5.QtGui import QCursor,QIcon
from PyQt5.QtWidgets import QFileSystemModel
from SettingWindow import load_setting



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
    pathChanged = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        setting = load_setting()

        # Set initial path
        self.path = setting.get('last_path', os.getcwd())
        self.project_root = self.path
        self._clip = None
        try : 
            os.chdir(self.project_root)
        except OSError : 
            print('[Project Path Folder Not Found ]')


        # Configure model
        self.fs_model = QFileSystemModel()
        self.fs_model.setRootPath(self.path)
        self.fs_model.setIconProvider(CustomIconProvider())

        # Apply model
        self.setModel(self.fs_model)
        self.setRootIndex(self.fs_model.index(self.path))
        self.setIconSize(QSize(32, 32))
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

    def _on_selection_changed(self, selected, deselected):
        if selected.indexes():
            index = selected.indexes()[0]
            self.on_item_selected(index)

    def on_item_selected(self, index):
        path = os.path.abspath(self.fs_model.filePath(index))
        project_root = os.path.abspath(self.project_root)


        if path != project_root:
            self.path = path
            self.pathChanged.emit(path)

    def keyPressEvent(self, event):
        index = self.currentIndex()
        if not index.isValid():
            return

        path = self.fs_model.filePath(index)
        editing = self.state() == QAbstractItemView.EditingState

        if editing:
            super().keyPressEvent(event)
            return

        if event.key() == Qt.Key_Delete:
            self.delete_item()
        elif event.key() == Qt.Key_C and event.modifiers() == Qt.ControlModifier:
            self.copy_item()
        elif event.key() == Qt.Key_X and event.modifiers() == Qt.ControlModifier:
            self.cut_item()
        elif event.key() == Qt.Key_V and event.modifiers() == Qt.ControlModifier:
            self.paste_item(path)
        elif event.key() == Qt.Key_F2:
            self.rename_item()
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if os.path.exists(path) and os.path.isdir(path):
                if self.isExpanded(index):
                    self.collapse(index)
                else:
                    self.expand(index)
        else:
            super().keyPressEvent(event)

    def show_context_menu(self, position: QPoint):
        index = self.indexAt(position)
        has_selection = index.isValid()
        path = self.fs_model.filePath(index) if has_selection else self.path

        is_nav = has_selection and self.fs_model.fileName(index) in (".", "..")
        can_edit = has_selection and not is_nav

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #ffffff;
                border: 1px solid #c8c8c8;
                border-radius: 6px;
                padding: 6px 4px;
            }
            QMenu::item {
                padding: 7px 28px 7px 14px;
                margin: 1px 4px;
                border-radius: 4px;
                color: #222222;
            }
            QMenu::item:selected { background-color: #dbeafe; color: #000000; }
            QMenu::item:disabled { color: #a0a0a0; }
            QMenu::separator { height: 1px; background: #e2e2e2; margin: 6px 10px; }
        """)

        def add(text, slot, enabled=True, shortcut=None):
            act = QAction(text, menu)
            if shortcut:
                act.setShortcut(shortcut)
                act.setShortcutVisibleInContextMenu(True)
            act.setEnabled(enabled)
            act.triggered.connect(slot)
            menu.addAction(act)
            return act

        # --- باز کردن ---
        add("Open", self.open_item, has_selection)
        add("Show in File Explorer", lambda: self.show_in_explorer(path), has_selection)

        menu.addSeparator()

        # --- ساخت ---
        add("Add File", self.create_file)
        add("New Folder", self.create_folder)

        menu.addSeparator()

        # --- ویرایش ---
        add("Cut", self.cut_item, can_edit, "Ctrl+X")
        add("Copy", self.copy_item, can_edit, "Ctrl+C")
        paste_ok = bool(self._clip) or os.path.exists(QApplication.clipboard().text() or "")
        add("Paste", lambda: self.paste_item(path), paste_ok, "Ctrl+V")

        menu.addSeparator()

        # --- تغییر نام و حذف ---
        add("Rename", self.rename_item, can_edit, "F2")
        add("Delete", self.delete_item, can_edit, "Del")

        menu.addSeparator()

        # --- مسیر ---
        add("Copy Path", lambda: QApplication.clipboard().setText(path), has_selection)

        menu.exec_(QCursor.pos())

    def create_file(self):
        index = self.currentIndex()
        if index.isValid():
            path = self.fs_model.filePath(index)
        else:
            path = self.path  


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
            editor = self.findChild(QLineEdit)
            if editor:
                full_text = editor.text()                
                last_dot_index = full_text.rfind('.')                
                if last_dot_index != -1:
                    editor.setSelection(0, last_dot_index)
                else:
                    editor.selectAll()

    def create_py_file(self):
        index = self.currentIndex()
        if index.isValid():
            path = self.fs_model.filePath(index)
        else:
            path = self.path  


        target_dir = path if os.path.isdir(path) else os.path.dirname(path)
        if not os.path.exists(target_dir):
            QMessageBox.warning(self, "Warning", "Please select a valid folder first.")
            return

        base_name = "untitled.py"
        new_file_path = os.path.join(target_dir, base_name)
        counter = 1
        while os.path.exists(new_file_path):
            new_file_path = os.path.join(target_dir, f"untitled_{counter}.py")
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
            editor = self.findChild(QLineEdit)
            if editor:
                full_text = editor.text()                
                last_dot_index = full_text.rfind('.')                
                if last_dot_index != -1:
                    editor.setSelection(0, last_dot_index)
                else:
                    editor.selectAll()

    def open_item(self, path):
        index = self.currentIndex()
        if index.isValid():
            path = self.fs_model.filePath(index)
        else:
            path = self.path 

        try:
            system = platform.system()
            if system == "Windows":
                os.startfile(path)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", path], check=True)
            else:  # Linux and others
                subprocess.run(["xdg-open", path], check=True)

            if os.path.isdir(path):
                os.chdir(path)

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open:\n{e}")

    def delete_item(self):
        index = self.currentIndex()
        if index.isValid():
            path = self.fs_model.filePath(index)
        else:
            path = self.path  


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
        if index.isValid():
            path = self.fs_model.filePath(index)
        else:
            path = self.path  

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
        if index.isValid():
            path = self.fs_model.filePath(index)
        else:
            path = self.path  



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

    def mousePressEvent(self, event):
        index = self.indexAt(event.pos())
        if not index.isValid():
            self.clearSelection()
            self.setCurrentIndex(QModelIndex())
            self.path = self.project_root
            self.pathChanged.emit(self.project_root)
        super().mousePressEvent(event)

    def show_in_explorer(self, path=None):
        if path is None:
            index = self.currentIndex()
            if index.isValid():
                path = self.fs_model.filePath(index)
            else:
                path = self.path

        if not path or not os.path.exists(path):
            QMessageBox.warning(self, "Error", f"Path does not exist:\n{path}")
            return

        try:
            system = platform.system()

            if system == "Windows":
                if os.path.isdir(path):
                    subprocess.run(["explorer", path], check=False)
                else:
                    subprocess.run(["explorer", "/select,", path], check=False)

            elif system == "Darwin":  # macOS
                subprocess.run(["open", "-R", path], check=False)

            else:  # Linux and others
                self._show_in_linux_explorer(path)

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open file manager:\n{e}")

    def _show_in_linux_explorer(self, path):
        if os.path.isdir(path):
            subprocess.Popen(["xdg-open", path])
            return

        parent_dir = os.path.dirname(path)

        candidates = [
            (["nautilus", "--select", path], "nautilus"),      # GNOME
            (["dolphin", "--select", path], "dolphin"),        # KDE
            (["nemo", path], "nemo"),                          # Cinnamon
            (["thunar", path], "thunar"),                      # XFCE
            (["pcmanfm", path], "pcmanfm"),                    # LXDE
        ]

        for cmd, exe in candidates:
            if shutil.which(exe):
                try:
                    subprocess.Popen(cmd)
                    return
                except Exception:
                    continue

        try:
            subprocess.Popen(["xdg-open", parent_dir])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open folder:\n{e}")

    def _selected_path(self):
        index = self.currentIndex()
        if not index.isValid():
            return None
        if self.fs_model.fileName(index) in (".", ".."):
            return None
        return self.fs_model.filePath(index)

    def copy_item(self):
        path = self._selected_path()
        if not path:
            return
        self._clip = ("copy", path)
        QApplication.clipboard().setText(path)

    def cut_item(self):
        path = self._selected_path()
        if not path:
            return
        self._clip = ("cut", path)
        QApplication.clipboard().setText(path)

    @staticmethod

    def _unique_dest(dest_path):
        if not os.path.exists(dest_path):
            return dest_path
        base, ext = os.path.splitext(dest_path)
        counter = 1
        while True:
            suffix = "_copy" if counter == 1 else f"_copy{counter}"
            candidate = f"{base}{suffix}{ext}"
            if not os.path.exists(candidate):
                return candidate
            counter += 1

    def paste_item(self, target_path):
        if self._clip:
            mode, source = self._clip
        else:
            mode, source = "copy", QApplication.clipboard().text()

        if not source or not os.path.exists(source):
            QMessageBox.warning(self, "Error", "Nothing valid to paste (source no longer exists).")
            self._clip = None
            return

        if not target_path:
            target_path = self.project_root
        target_dir = target_path if os.path.isdir(target_path) else os.path.dirname(target_path)

        base_name = os.path.basename(source.rstrip("/\\"))
        dest_path = os.path.join(target_dir, base_name)

        src_abs = os.path.abspath(source)
        dst_abs = os.path.abspath(dest_path)
        if os.path.isdir(src_abs) and (dst_abs == src_abs or dst_abs.startswith(src_abs + os.sep)):
            QMessageBox.warning(self, "Error", "Cannot paste a folder into itself.")
            return

        try:
            if mode == "cut":
                if os.path.abspath(os.path.dirname(src_abs)) == os.path.abspath(target_dir):
                    self._clip = None
                    return
                dest_path = self._unique_dest(dest_path)
                shutil.move(source, dest_path)
                self._clip = None
            else:
                dest_path = self._unique_dest(dest_path)
                if os.path.isdir(source):
                    shutil.copytree(source, dest_path)
                else:
                    shutil.copy2(source, dest_path)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not paste:\n{e}")

    def delete_item(self):
        path = self._selected_path()
        if not path:
            return

        if os.path.abspath(path) == os.path.abspath(self.project_root):
            QMessageBox.warning(self, "Delete", "The project root folder cannot be deleted from here.")
            return

        reply = QMessageBox.question(
            self, "Delete", f"Are you sure you want to delete?\n{path}",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return

        try:
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                def on_rm_error(func, p, exc_info):
                    os.chmod(p, stat.S_IWRITE)
                    func(p)
                shutil.rmtree(path, onerror=on_rm_error)
            self.clearSelection()
            self.setCurrentIndex(QModelIndex())
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not delete:\n{e}")

    def rename_item(self):
        path = self._selected_path()
        if not path:
            return

        base_dir = os.path.dirname(path)
        old_name = os.path.basename(path)
        new_name, ok = QInputDialog.getText(self, "Rename", "Enter new name:", text=old_name)
        if ok and new_name and new_name != old_name:
            new_path = os.path.join(base_dir, new_name)
            if os.path.exists(new_path):
                QMessageBox.warning(self, "Error", "An item with that name already exists.")
                return
            try:
                os.rename(path, new_path)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not rename:\n{e}")