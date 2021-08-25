
from .ui.search_ui import Ui_Search as DIALOG
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QHeaderView
from PyQt5 import QtCore

class SearchDialog(QDialog, DIALOG):
    def __init__(self, central_widget):
        QDialog.__init__(self)
        self.setupUi(self)
        self.central_widget = central_widget
        self.attribute_names = self.central_widget.attribute_names.copy()
        self.attribute_names.insert(0, "all")
        self.comboBox.addItems(self.attribute_names)
        self.comboBox.setCurrentText("all")
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(["Component Name", "Attribute", "Search Result"])
        self.searchButton.clicked.connect(self.search)
        self.cancelButton.clicked.connect(self.close)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.setWindowTitle("Search")

    def search_data(self, term):
        canvas = self.central_widget.canvas
        classes = canvas.classes
        where = self.comboBox.currentText()
        lower_term = term.lower()
        result = {}
        if where == "all":
            to_search = self.attribute_names[1:] # skip "all"
        else:
            to_search = [where]
        for c in classes:
            for attr in to_search:
                if lower_term in canvas.class_attributes[c][attr].lower():
                    result[c] = [attr, canvas.class_attributes[c][attr]]
        if len(result.keys()) == 0:
            result["NA"] = ["NA", "NA"]
        return result

    def fill_table(self, result):
        nrows = len(result.keys())
        self.tableWidget.setRowCount(nrows)
        keys = list(result.keys())
        flags = QtCore.Qt.ItemFlags()
        flags != QtCore.Qt.ItemIsEditable
        for ir, k in enumerate(keys):
            info = result[k]
            newitem = QTableWidgetItem(str(k))
            newitem.setFlags(flags)
            self.tableWidget.setItem(ir, 0, newitem)
            for ic in range(1, 3):
                newitem = QTableWidgetItem(info[ic-1])
                newitem.setFlags(flags)
                self.tableWidget.setItem(ir, ic, newitem)
        self.tableWidget.setHorizontalHeaderLabels(["Component Name", "Attribute", "Search Result"])

    def search(self):
        if len(self.searchEdit.text()):
            res = self.search_data(self.searchEdit.text())
            self.fill_table(res)
            self.tableWidget.resizeColumnsToContents()
            self.tableWidget.resizeRowsToContents()
            self.tableWidget.horizontalHeader().setStretchLastSection(True)
