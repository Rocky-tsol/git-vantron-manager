import sys
from PySide6.QtWidgets import QTreeWidgetItem, QMainWindow, QApplication, QHeaderView, QMessageBox, QFileDialog
from ui_form import Ui_MainWindow
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor
import os
import json
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = r"C:\Users\rocky\Documents\app_manager\vantron.json"


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.current_file_path = None
        self.ui.openjsonbutton.clicked.connect(self.open_json_file)
        self.ui.saveButton.clicked.connect(self.save_to_file)
        self.ui.treeWidget.setTextElideMode(Qt.ElideNone)
        self.ui.treeWidget.itemChanged.connect(self.on_item_changed)

        header = self.ui.treeWidget.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header = self.ui.treeWidget.header()
        header.setStretchLastSection(True)
        header.setTextElideMode(Qt.ElideNone)



        self.ui.saveButton.setStyleSheet("""
        QPushButton {
            background-color: #000068;
            color: #ffffff;
            border-radius: 6px;
            padding: 6px 12px;
        }

        QPushButton:hover {
            background-color: #1e6fd9;
        }

        QPushButton:pressed {
            background-color: #155fa0;
        }
        """)

    def open_json_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open JSON File",
            "",
            "JSON Files (*.json)"
        )
        if not file_path:
            return
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return
        if not isinstance(data, list):
            QMessageBox.critical(self, "Invalid JSON", "JSON file must contain a list of apps")
        self.current_file_path = file_path
        self.load_apps(data)
    def load_apps(self, apps):
        self.ui.treeWidget.clear()
        for app in apps:
            self.add_app(app)

    def validate_apps(self):
        errors = []

        for i in range(self.ui.treeWidget.topLevelItemCount()):
            parent = self.ui.treeWidget.topLevelItem(i)
            app_name = parent.text(0)



            for j in range(parent.childCount()):
                child = parent.child(j)
                key = child.text(0)
                value = child.text(1)
                if value.strip() == "":
                    errors.append(f"{app_name}: '{key}' cannot be blank.")
                    child.setBackground(1, QBrush(QColor("#ccffcc")))
                if value != value.strip():
                    errors.append(f"{app_name}: '{key}' contains spaces at the start or end.")
                    child.setBackground(1, QBrush(QColor("#ccffcc")))

        return errors

    def save_to_file(self):
        if not self.current_file_path:
            QMessageBox.warning(self, "No File Open", "Please open a JSON file first.")
            return

        errors = self.validate_apps()
        if errors:
            QMessageBox.critical(
                self,
                "Validation Error",
                "\n".join(errors)
            )
            return
        data = self.export_to_json()

        with open(self.current_file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=True)
        QMessageBox.information(self, "Saved", "JSON file saved successfully.")

        with open(FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        print("Saved to:", FILE_PATH)

    def add_app(self, app_data):
        parent = QTreeWidgetItem(self.ui.treeWidget)
        parent.setText(0, app_data["app_name"])
        parent.setExpanded(False)
        for key, value in app_data.items():
            child = QTreeWidgetItem(parent)
            child.setText(0, key)
            child.setText(1, str(value))

            # Make value editable
            child.setFlags(child.flags() | Qt.ItemIsEditable)

    def on_item_changed(self, item, column):
        if item.parent() is None:
            return
        field = item.text(0)
        new_value = item.text(1)
        app_name = item.parent().text(0)

        print(f"{app_name} -> {field} updated to {new_value}")

    def export_to_json(self):
        data = []
        for i in range(self.ui.treeWidget.topLevelItemCount()):
            parent = self.ui.treeWidget.topLevelItem(i)
            app = {}

            for j in range(parent.childCount()):
                child = parent.child(j)
                app[child.text(0)] = child.text(1)
            data.append(app)
        return data

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())
