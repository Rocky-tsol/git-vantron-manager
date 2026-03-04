import sys
from PySide6.QtWidgets import QTreeWidgetItem, QMainWindow, QApplication, QHeaderView, QMessageBox, QFileDialog, QDialog, QFormLayout, QLineEdit, QDialogButtonBox
from ui_form import Ui_MainWindow
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor
import os
import json, requests
print(sys.executable)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PINNED_APPS = { "thermatouch service", "touchsteam"}      #add an app name in lowercase to make it pinned at the top of json file
class AddAppDialog(QDialog):
    #dialog box that has the fields to add app
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add App")

        self.fields = {}

        layout = QFormLayout(self)
        field_names = ["app_name", "package_name", "current_version", "updated", "min_core_req", "min_service_version", "apk_icon_url"]
        for name in field_names:
            edit = QLineEdit()
            self.fields[name] = edit
            layout.addRow(name.replace("_", " ").title(), edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    def get_data(self):
        return {k: v.text() for k, v in self.fields.items()}

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.current_file_path = None
        self.ui.openJsonButton.clicked.connect(self.open_json_file)
        self.ui.saveButton.clicked.connect(self.save_to_file)
        self.ui.treeWidget.itemChanged.connect(self.on_item_changed)
        self.ui.addAppButton.clicked.connect(self.open_add_app_dialog)
        self.ui.deleteAppButton.clicked.connect(self.delete_selected_app)
        self.ui.fetchButton.clicked.connect(self.fetch_json_from_server)
        header = self.ui.treeWidget.header()                                  #gets rid of text elide
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header = self.ui.treeWidget.header()
        header.setStretchLastSection(True)
        header.setTextElideMode(Qt.ElideNone)

        self.current_source = None     #tracks where json file came from
        self.current_file_path = None
        self.current_url = None


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
        self.ui.openJsonButton.setStyleSheet("""
        QPushButton {
            background-color: #680000;
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
        self.ui.addAppButton.setStyleSheet("""
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
        self.ui.deleteAppButton.setStyleSheet("""
        QPushButton {
            background-color: #680000;
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
        self.ui.fetchButton.setStyleSheet("""
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


    def fetch_json_from_server(self):
        #fetches json from server and populates the list
        url = "https://thermatouch.tsolup.com/vantron.json"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            apps = data.get("app_details", [])

            self.ui.treeWidget.clear()

            for app in apps:
                self.insert_app_alphabetically(app)
            self.current_source = "server"
            self.current_url = url

            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.current_file_path = os.path.join(base_dir, "vantron.json")
        except Exception as e:
            QMessageBox.critical(self, "Download Error", str(e))

    def open_json_file(self):
        # Open a JSON file and load its contents into the tree widget to be edited

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
            return
        self.current_source = "local"
        self.current_file_path = file_path

        self.load_apps(data)
    def load_apps(self, apps):
        #clears tree then populates it with data

        self.ui.treeWidget.clear()
        for app in apps:
            self.add_app(app)

    def validate_apps(self):
        """
        Validates all editable values in the tree.
        returns a list of error messages if any issues are found.
        """
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
        #Validate data and saves it back to the JSON file.

        # if not self.current_file_path:
            # QMessageBox.warning(self, "No File Open", "Please open a JSON file first.")
            # return

        errors = self.validate_apps()
        if errors:
            QMessageBox.critical(
                self,
                "Validation Error",
                "\n".join(errors)
            )
            return
        data = self.export_to_json()

        if self.current_file_path:
            with open(self.current_file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=True)
        if self.current_source == "server":

            QMessageBox.information(self, "Saved", "Saved to local file.")

        folder = os.getcwd()  #gets current directory
        filename = "vantron.json"
        file_path = os.path.join(folder, filename)



        print("Saved to:", file_path)

    def add_app(self, app_data):
        #add a single app and its fields to the tree widget

        parent = QTreeWidgetItem(self.ui.treeWidget)
        parent.setText(0, str(app_data["app_name"]))
        parent.setExpanded(False)
        for key, value in app_data.items():
            child = QTreeWidgetItem(parent)
            child.setText(0, key)
            child.setText(1, str(value))

            # Make value editable
            child.setFlags(child.flags() | Qt.ItemIsEditable)

    def open_add_app_dialog(self):
        #enables pop up to add a new app validates app name and removes empty fields
        dialog = AddAppDialog(self)

        if dialog.exec() != QDialog.Accepted:
            return
        app_data = dialog.get_data()

        if app_data["app_name"].strip() == "":
            QMessageBox.critical(self, "Error", "App name is required.")
            return
        app_data = {
            k: v for k, v in app_data.items()
            if v.strip() != ""
        }
        self.insert_app_alphabetically(app_data)



    def insert_app_alphabetically(self, app_data):
        #puts the new app in alphabetical order
        #keeps pinned apps at the top
        new_name = app_data.get("app_name", "").strip()
        new_name = new_name.lower()
        pinned_count = 0
        for i in range(self.ui.treeWidget.topLevelItemCount()):
        # counts the pinned apps already in tree
            name = self.ui.treeWidget.topLevelItem(i).text(0).lower()
            if name in PINNED_APPS:
                pinned_count += 1
            else:
                break
        if new_name in PINNED_APPS:
            index = pinned_count
        else:
            index = pinned_count
        for i in range(pinned_count, self.ui.treeWidget.topLevelItemCount()):
            existing = self.ui.treeWidget.topLevelItem(i)
            if existing.text(0).lower() > new_name:
                break
            index += 1

        parent = QTreeWidgetItem()
        parent.setText(0, str(app_data["app_name"]))
        parent.setFirstColumnSpanned(True)

        for key, value in app_data.items():
            child = QTreeWidgetItem(parent)
            child.setText(0, key)
            child.setText(1, str(value))
            child.setFlags(child.flags() | Qt.ItemIsEditable)
        self.ui.treeWidget.insertTopLevelItem(index, parent)

    def delete_selected_app(self):
        # deletes highlighted app and asks for confirmation
        item = self.ui.treeWidget.currentItem()

        if not item:
            QMessageBox.warning(
                self, "No Selection", "Please select an app to delete."
            )
            return
        # If a child is selected, delete its parent app
        if item.parent():
            item = item.parent()
        app_name = item.text(0)
        reply = QMessageBox.question(self, "Confirm Delete", f"Are you sure you want to delete '{app_name}'?", QMessageBox.Ok | QMessageBox.Cancel)
        if reply != QMessageBox.Ok:
            return
        index = self.ui.treeWidget.indexOfTopLevelItem(item)
        self.ui.treeWidget.takeTopLevelItem(index)
    def on_item_changed(self, item, column):
        #Respond to edits made in the tree widget
        if item.parent() is None:
            return
        field = item.text(0)
        new_value = item.text(1)
        app_name = item.parent().text(0)

        print(f"{app_name} -> {field} updated to {new_value}")

    def export_to_json(self):
        #Converts tree widget contents back into JSON compatible data
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
