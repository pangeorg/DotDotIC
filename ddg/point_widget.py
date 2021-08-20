# -*- coding: utf-8 -*-
#
# DotDotGoose
# Author: Peter Ersts (ersts@amnh.org)
#
# --------------------------------------------------------------------------
#
# This file is part of the DotDotGoose application.
# DotDotGoose was forked from the Neural Network Image Classifier (Nenetic).
#
# DotDotGoose is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# DotDotGoose is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with with this software.  If not, see <http://www.gnu.org/licenses/>.
#
# --------------------------------------------------------------------------
import os
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QDialog, QMenu
from .chip_dialog import ChipDialog
from .ui.point_widget_ui import Ui_PointWidget as WIDGET
from .ui.input_dialog_ui import Ui_InputDialog as DIALOG

def traverse_tree(parent, view, expanded={}, parent_index=None, action="get"):
    if action == "get":
        for i in range(parent.rowCount()):
            item = parent.child(i)
            index = item.index()
            if parent_index:
                is_expanded = view.isExpanded(view.model().index(i, 0, parent_index))
            else:
                is_expanded = view.isExpanded(view.model().index(i, 0))
            expanded[item.data(0)] = is_expanded
            if item.hasChildren():
                traverse_tree(item, view, expanded, index, action)
        return expanded
    elif action == "set":
        for i in range(parent.rowCount()):
            item = parent.child(i)
            index = item.index()
            is_expanded = expanded.get(item.data(0), False)
            view.setExpanded(index, is_expanded)
            if item.hasChildren():
                traverse_tree(item, view, expanded, index, action)

class InputDialog(QDialog, DIALOG):
    def __init__(self, point_widget):
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self)
        self.point_widget = point_widget
        self.pushButtonCancel.clicked.connect(self.close)
        self.pushButtonOk.clicked.connect(self.ok)
        self.categoryBox.addItems(self.point_widget.canvas.categories)

    def setNames(self, index):
        self.index = index
        self.selected = index.data(0)
        if self.selected in self.point_widget.canvas.categories:
            self.classname = None
            self.category = self.selected
        else:
            self.classname = self.selected
            self.category = self.point_widget.canvas.get_category_from_class(self.classname)
        if self.classname is None:
            self.classEdit.setEnabled(False)
            self.classEdit.setText("")
        else:
            self.classEdit.setEnabled(True)
            self.classEdit.setText(self.classname)
        self.categoryBox.lineEdit().setText(self.category)
        return self.exec_()

    def ok(self):
        new_category = self.categoryBox.currentText()
        new_classname = self.classEdit.text()
        self.point_widget.rename(self.index, self.category, self.classname, new_category, new_classname)
        self.close()

class ItemModel(QtGui.QStandardItemModel):
    update_tree = QtCore.pyqtSignal(str, str, int)
    def dropMimeData(self, data, action, row, column, parent):
        column = 0
        row = max(0, row)
        super().dropMimeData(data, action, row, column, parent)
        d = self.itemFromIndex(self.index(row, column, parent))
        p = self.itemFromIndex(self.index(parent.row(), parent.column()))
        self.update_tree.emit(p.data(0), d.data(0), row)
        return True

class PointWidget(QtWidgets.QWidget, WIDGET):
    hide_custom_fields = QtCore.pyqtSignal(bool)
    class_selection_changed = QtCore.pyqtSignal()
    saving = QtCore.pyqtSignal()

    def __init__(self, canvas, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.canvas = canvas

        self.inputDialog = InputDialog(self)

        self.pushButtonAddClass.clicked.connect(lambda: self.add_class(askname=True))
        self.pushButtonAddClass.resize(self.pushButtonAddClass.sizeHint().width(), self.pushButtonAddClass.sizeHint().height())
        self.pushButtonAddCurrent.clicked.connect(lambda: self.add_class(askname=False))
        self.pushButtonAddCategory.clicked.connect(self.add_category)
        self.pushButtonRemoveClass.clicked.connect(self.remove_class)

        self.classModel = ItemModel() # QtGui.QStandardItemModel()
        self.classTree.setDragEnabled(True)
        self.classTree.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        root = self.classModel.invisibleRootItem()
        root.setDropEnabled(False)
        self.classModel.update_tree.connect(self.update_from_drop)
        self.classModel.setHorizontalHeaderLabels(['Name', '#', ""])
        self.classTree.setModel(self.classModel)
        self.classTree.setColumnWidth(0, 270)
        self.classTree.setColumnWidth(1, 10)
        self.classTree.setColumnWidth(2, 10)
        self.classTree.clicked.connect(self.item_clicked)
        self.classTree.doubleClicked.connect(self.inputDialog.setNames)
        self.classTree.selectionModel().selectionChanged.connect(self.selection_changed)
        self.classTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.classTree.customContextMenuRequested.connect(self.openContextMenu)
        self.fill_default_categories()
        self.classTree.resizeColumnToContents(0)
        self.tree_expanded = {} # list of the expanded items in the model

        self.checkBoxDisplayPoints.toggled.connect(self.display_points)
        self.checkBoxDisplayGrid.toggled.connect(self.display_grid)
        self.canvas.image_loaded.connect(self.image_loaded)
        self.canvas.update_point_count.connect(self.update_point_count)
        self.canvas.points_loaded.connect(self.points_loaded)
        self.canvas.points_updated.connect(self.display_classes)
        self.canvas.directory_set.connect(self.set_autosave)

        # model for pictures
        self.model = QtGui.QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Projet Structure', 'Total Count'])
        self.current_model_index = QtCore.QModelIndex()
        self.treeView.setModel(self.model)
        self.treeView.setColumnWidth(0, 270)
        self.treeView.setColumnWidth(1, 10)
        self.reset_model()
        self.treeView.doubleClicked.connect(self.select_model_item)
        self.treeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(self.openEcuContextMenu)

        self.previous_file_name = None  # used for quick save

        self.spinBoxPointRadius.valueChanged.connect(self.canvas.set_point_radius)
        self.spinBoxGrid.valueChanged.connect(self.canvas.set_grid_size)

        icon = QtGui.QPixmap(20, 20)
        icon.fill(QtCore.Qt.yellow)
        self.labelPointColor.setPixmap(icon)
        self.labelPointColor.mousePressEvent = self.change_active_point_color
        icon = QtGui.QPixmap(20, 20)
        icon.fill(QtCore.Qt.white)
        self.labelGridColor.setPixmap(icon)
        self.labelGridColor.mousePressEvent = self.change_grid_color

        self.checkBoxImageFields.clicked.connect(self.hide_custom_fields.emit)

    def fill_default_categories(self):
        root = self.classModel.invisibleRootItem()
        for c in self.canvas.categories:
            key, value, color_item = self._get_default_category(c)
            root.appendRow([key, value, color_item])

    def add_category(self):
        name, ok = QtWidgets.QInputDialog.getText(self, 'New Category', 'Enter Category Name')
        if ok:
            if name in self.canvas.categories:
                dialog = QtWidgets.QMessageBox.question(self, "Choose different name", "Name "+ name + " already taken", QtWidgets.QMessageBox.Ok)
                return
            key, value, color_item = self._get_default_category(name)
            self.canvas.add_category(name)
            self.classModel.invisibleRootItem().appendRow([key, value, color_item])

    def add_class(self, askname=True):
        # get current selection:
        if self.canvas.current_selection is not None:
            name = self.canvas.current_selection.data(0)
            if name not in self.canvas.categories: # current selection is not a category
                category_item = self.canvas.current_selection.parent()
            else: # selection is a category
                category_item = self.canvas.current_selection
            category_name = category_item.data(0)
            category_index = category_item.index()
        else:
            return
        
        default_name = "{:} #{:d}".format(category_name, category_item.rowCount() + 1)
        if askname:
            class_name, ok = QtWidgets.QInputDialog.getText(self, 'New Component', 'Enter Component Name', text=default_name)
        else:
            class_name, ok = default_name, True
        if ok:
            if class_name in self.canvas.classes or class_name in self.canvas.categories:
                dialog = QtWidgets.QMessageBox.question(self, "Choose different name", "Name "+ class_name + " already taken", QtWidgets.QMessageBox.Ok)
                self.add_class()
            else:
                self.canvas.add_class(category_name, class_name)
                key, value, color_item = self._get_default_class(class_name)
                if self.canvas.current_class_name is not None: # toggle previous selection
                    item = self.get_item_from_name(self.canvas.current_class_name)
                    font = item.font()
                    font.setBold(False)
                    key.setFont(font)
                self.classModel.itemFromIndex(category_index).appendRow([key, value, color_item])
                self.classTree.setExpanded(category_index, True)
                self.select_tree_item(key)

    def change_active_point_color(self, event):
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            self.set_active_point_color(color)

    def change_grid_color(self, event):
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            self.set_grid_color(color)

    def display_classes(self):
        for i in range(self.classModel.rowCount()):
            item = self.classModel.item(i)
            self.tree_expanded[item.data(0)] = self.classTree.isExpanded(self.classModel.index(i,0))
        self.reset_class_model()
        root = self.classModel.invisibleRootItem()
        for category in sorted(self.canvas._categories):
            classes = sorted(self.canvas.data[category])
            total_count = 0
            category_item, category_count_item, _ = self._get_default_category(category)
            if len(classes) != 0:
                invisible = []
                for class_name in classes:
                    class_item, class_count_item, class_color_item = self._get_default_class(class_name)
                    if not self.canvas.class_visibility[class_name]:
                        class_item.setCheckState(QtCore.Qt.Unchecked)
                        invisible.append(class_name)
                    count = 0
                    for image in self.canvas.points.keys():
                        if image == self.canvas.current_image_name:
                            count += len(self.canvas.points[image].get(class_name, []))
                    class_count_item.setData(str(count), QtCore.Qt.EditRole)
                    total_count += count
                    if class_name == self.canvas.current_class_name:
                        font = class_item.font()
                        font.setBold(True)
                        class_item.setFont(font)
                    category_item.appendRow([class_item, class_count_item, class_color_item])
                if len(invisible) == len(classes):
                    category_item.setCheckState(QtCore.Qt.Unchecked)
            category_count_item.setData(str(total_count), QtCore.Qt.EditRole)
            root.appendRow([category_item, category_count_item, QtGui.QStandardItem("")])
        for row in range(self.classModel.rowCount()):
            index = self.classModel.index(row, 0)
            item = self.classModel.itemFromIndex(index)
            self.classTree.setExpanded(index, self.tree_expanded.get(item.data(0), False))
        self.classTree.resizeColumnToContents(0)
        if self.canvas.current_class_name:
            self.select_tree_item_from_name(self.canvas.current_class_name)

    def display_count_tree(self):
        expanded = traverse_tree(self.model.invisibleRootItem(), self.treeView, expanded={}, parent_index=None, action="get")
        self.reset_model()
        ecus = self.canvas.ecus 
        for ecu_name, pcbs in ecus.items():
            ecu_item = QtGui.QStandardItem(ecu_name)
            ecu_item.setEditable(False)
            tmp_item = QtGui.QStandardItem("")
            tmp_item.setEditable(False)
            pcb_item = None
            for pcb_name, pcb in pcbs.items():
                pcb_item = QtGui.QStandardItem(pcb_name)
                pcb_item.setEditable(False)
                pos_item = None
                for pos, image in pcb.items():
                    pos_item = QtGui.QStandardItem(pos)
                    pos_item.setEditable(False)
                    count = 0
                    for _, points in self.canvas.points[image].items():
                        count += len(points)
                    count_item = QtGui.QStandardItem(str(count))
                    count_item.setEditable(False)
                    if image == self.canvas.current_image_name:
                        font = pos_item.font()
                        font.setBold(True)
                        pos_item.setFont(font)
                    if pos_item: pcb_item.appendRow([pos_item, count_item])
                if pcb_item: ecu_item.appendRow([pcb_item, tmp_item])
            self.model.appendRow([ecu_item])
        traverse_tree(self.model.invisibleRootItem(), self.treeView, expanded=expanded, parent_index=None, action="set")

    def display_grid(self, display):
        self.canvas.toggle_grid(display=display)

    def display_points(self, display):
        self.canvas.toggle_points(display=display)

    def export_counts(self):
        file_name = QtWidgets.QFileDialog.getSaveFileName(self, 'Export Count Summary', os.path.join(self.canvas.directory, 'counts.csv'), 'Excel Sheet (*.csv)')
        if file_name[0] != '':
            if not open(file_name[0], "r").closed:
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Critical)
                msg.setText("Write - Error")
                msg.setInformativeText('File open in another program. Please close file and retry')
                msg.setWindowTitle("Error")
                msg.exec_()
                return 
            self.canvas.export_counts(file_name[0])

    def export_points(self):
        file_name = QtWidgets.QFileDialog.getSaveFileName(self, 'Export Points', os.path.join(self.canvas.directory, 'points.csv'), 'Text CSV (*.csv)')
        if file_name[0] != '':
            self.canvas.export_points(file_name[0])
    
    def export_details(self):
        self.chip_dialog = ChipDialog(self.canvas.classes, self.canvas.points, self.canvas.directory, self.canvas.survey_id)
        self.chip_dialog.show()
    
    def get_item_from_name(self, name):
        if name in self.canvas.categories:
            return self.classModel.findItems(name)[0]
        elif name in self.canvas.classes:
            category_name = self.canvas.get_category_from_class(name)
            category_item = self.classModel.findItems(category_name)[0]
            for i in range(category_item.rowCount()):
                if name == category_item.child(i, 0).data(0):
                    index = i
            # index = self.canvas.data[category_name].index(name)
            return category_item.child(index, 0)

    def _get_default_category(self, name):
        key = QtGui.QStandardItem(name)
        key.setCheckable(True)
        key.setCheckState(QtCore.Qt.Checked)
        key.setSelectable(True)
        key.setEditable(False)
        key.setTextAlignment(QtCore.Qt.AlignLeft)
        value = QtGui.QStandardItem("0")
        value.setEditable(False)
        value.setDropEnabled(False)
        color_item = QtGui.QStandardItem("")
        color_item.setDropEnabled(False)
        return key, value, color_item

    def _get_default_class(self, class_name):
        key = QtGui.QStandardItem(class_name)
        key.setCheckable(True)
        key.setCheckState(QtCore.Qt.Checked)
        key.setDropEnabled(False)
        value = QtGui.QStandardItem("0")
        value.setEditable(False)
        value.setDropEnabled(False)
        color_item = QtGui.QStandardItem()
        color_item.setDropEnabled(False)
        icon = QtGui.QPixmap(20, 20)
        icon.fill(self.canvas.colors[class_name])
        color_item.setData(icon, QtCore.Qt.DecorationRole)
        color_item.setEditable(False)
        return key, value, color_item

    def item_clicked(self, index):
        if index.column() == 2:
            # set new color
            category_item = index.parent()
            name = category_item.child(index.row(), 0).data(0)
            # prevent color change of categories
            if name is None:
                return
            color = QtWidgets.QColorDialog.getColor()
            if color.isValid():
                self.canvas.colors[name] = color
                icon = QtGui.QPixmap(20, 20)
                icon.fill(color)
                self.classModel.itemFromIndex(index).setData(icon, QtCore.Qt.DecorationRole)
                self.canvas.display_points()
        elif index.column() == 0:
            # edit checkstate
            self.classTree.selectionModel().clear()
            category_item = index.parent()
            name = category_item.child(index.row(), 0).data(0)
            if name is None:
                # clicked is a category
                item = self.classModel.itemFromIndex(index)
                for row in range(item.rowCount()):
                    state = item.checkState()
                    class_item = item.child(row, 0)
                    class_item.setCheckState(state)
                    self.canvas.class_visibility[class_item.data(0)] = state > 1
                self.canvas.set_current_class(name)
                self.select_tree_item(item)
            else:
                category_item = self.classModel.itemFromIndex(index.parent())
                item = category_item.child(index.row(), 0)
                name = item.data(0)
                state = item.checkState()
                self.canvas.class_visibility[name] = state > 1
                self.canvas.set_current_class(name)
                self.select_tree_item_from_name(name)

    def image_loaded(self, directory, file_name):
        self.display_classes()
        self.display_count_tree()

    def load(self):
        if ".pnts" in self.canvas.directory:
            defaultname = os.path.dirname(self.canvas.directory)
        else:
            defaultname = self.canvas.directory
        file_name = QtWidgets.QFileDialog.getOpenFileName(self, 'Select Points File', defaultname, 'Single Point File (*.pnts);;Point File (*.pnt)')
        if file_name[0] != '':
            self.previous_file_name = file_name[0]
            self.canvas.load_points_from_file(file_name[0])

    def points_loaded(self, filename=None):
        self.lineEditSurveyId.setText(self.canvas.survey_id)
        self.display_classes()
        self.display_count_tree()
        self.update_ui_settings()
        self.previous_file_name = filename

    def rename(self, index, category, classname, new_category, new_classname):
        column = index.column()
        row = index.row()
        if new_category == category and new_classname == classname:
            self.inputDialog.close()
            return
        if column == 0 and new_category != "":
            is_expanded = self.classTree.isExpanded(index)
            self.classTree.selectionModel().clear()
            for row in range(self.classModel.rowCount()):
                ind = self.classModel.index(row, 0)
                item = self.classModel.itemFromIndex(ind)
                self.tree_expanded[item.data(0)] = self.classTree.isExpanded(ind)
            if classname is None and new_category != category: # rename category
                if category in self.canvas.categories and new_category not in self.canvas.categories:
                    self.canvas.rename_category(category, new_category)
                    self.tree_expanded[new_category] = self.classTree.isExpanded(index)
                else:
                    classes = self.canvas.data[category].copy()
                    for c in classes:
                        self.canvas.move_class(c, category, new_category)
                    self.canvas.remove_category(category)
            elif new_category != category and new_classname != "": # rename category and class
                if new_category not in self.canvas.categories:
                    self.canvas.add_category(new_category)
                if classname in self.canvas.classes:
                    if new_classname == classname:
                        self.canvas.move_class(classname, category, new_category)
                    elif new_classname != classname and new_classname not in self.canvas.classes:
                        self.canvas.rename_class(classname, new_classname)
                        self.canvas.move_class(new_classname, category, new_category)
                    else:
                        dialog = QtWidgets.QMessageBox.question(self, "Choose different names", "Category/Component "+ new_category + "/" + new_classname +" already taken", QtWidgets.QMessageBox.Ok)
                        self.inputDialog.close()
                        return
            elif new_classname != classname and new_category == category and new_classname != "":
                if new_classname in self.canvas.classes:
                    dialog = QtWidgets.QMessageBox.question(self, "Choose different class name", "Component "+ new_classname +" already taken", QtWidgets.QMessageBox.Ok)
                    self.inputDialog.close()
                    return
                if classname in self.canvas.classes:
                    self.canvas.rename_class(classname, new_classname)
            self.display_classes()

    def reset_class_model(self):
        self.classTree.reset()
        self.classModel.clear()
        self.classModel.setColumnCount(3)
        self.classModel.setHorizontalHeaderLabels(['Name', '#', ""])
        self.classTree.setColumnWidth(0, 270)
        self.classTree.setColumnWidth(1, 10)
        self.classTree.setColumnWidth(2, 10)

    def reset_model(self):
        self.current_model_index = QtCore.QModelIndex()
        self.model.clear()
        self.model.setColumnCount(2)
        self.model.setHeaderData(0, QtCore.Qt.Horizontal, 'Project Structure')
        self.model.setHeaderData(1, QtCore.Qt.Horizontal, 'Count')
        self.treeView.setColumnWidth(0, 270)
        self.treeView.setColumnWidth(1, 10)

    def remove_class(self, indexes=None):
        if not indexes:
            indexes = self.classTree.selectedIndexes()
        if len(indexes) > 0:
            index = indexes[0]
            item = index.model().itemFromIndex(index)
            name = item.data(0)
            msgBox = QtWidgets.QMessageBox()
            msgBox.setWindowTitle('Warning')
            msgBox.setText('You are about to remove [{}] '.format(name))
            msgBox.setInformativeText('Do you want to continue?')
            msgBox.setStandardButtons(QtWidgets.QMessageBox.Cancel | QtWidgets.QMessageBox.Ok)
            msgBox.setDefaultButton(QtWidgets.QMessageBox.Cancel)
            response = msgBox.exec()
            if response == QtWidgets.QMessageBox.Ok:
                if name in self.canvas.categories:
                    if item.rowCount() == 0:
                        self.classModel.removeRow(item.row())
                    else:
                        self.classModel.removeRows(item.row(), item.rowCount())
                    self.canvas.remove_category(name)
                else:
                    category_item = item.parent()
                    category_item.removeRow(item.row())
                    self.canvas.remove_class(name)
                self.tree_expanded = {}
                for row in range(self.classModel.rowCount()):
                    ind = self.classModel.index(row, 0)
                    item = self.classModel.itemFromIndex(ind)
                    self.tree_expanded[item.data(0)] = self.classTree.isExpanded(ind)
                self.display_classes()
                self.display_count_tree()

    
    def autosave(self):
        filename = os.path.dirname(self.canvas.directory, "autosave.pnts")
        self.saving.emit()
        self.save(file_name=filename)

    def set_autosave(self):
        self.timer = QtCore.QTimer()
        self.timer.setInterval(int(1000*60*self.canvas.config.autosave_timeout))
        self.timer.timeout.connect(self.autosave)
        self.timer.start()

    def quick_save(self):
        self.saving.emit()
        self.save(file_name=self.previous_file_name)

    def save(self, override=False, file_name=None):
        import shutil
        is_pnts = False
        if ".pnts" in self.canvas.directory:
            defaultname = os.path.join(os.path.dirname(self.canvas.directory), "untitled")
        else:
            defaultname = os.path.join(self.canvas.directory, 'untitled')
        if file_name is None:
            file_name = QtWidgets.QFileDialog.getSaveFileName(self, 'Save Points', defaultname, 'Single Point File (*.pnts);;Point File (*.pnt)')
        if file_name[0] != '':
            if ".pnts" in file_name[0]: is_pnts = True
            self.previous_file_name = file_name[0]
            # check if files are in different folders
            full_image_names = self.canvas.full_image_names.values()
            dirnames = set([os.path.dirname(f) for f in full_image_names])
            if override is False and len(dirnames) > 1 and (not is_pnts):
                message = """
                            <h1> Save Failed </h1>
                            <p> You are attempting to save a pnt file with image files outside the save directory</p> 
                            <p> Copy files to the folder {:}? This will <b>overwrite</b> files with the same name!</p>""".format(os.path.dirname(file_name[0]))
                msg_box = QtWidgets.QMessageBox()
                msg_box.setTextFormat(QtCore.Qt.RichText)
                msg_box.setWindowTitle('ERROR')
                msg_box.setText(message)
                msg_box.setStandardButtons(QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Cancel)
                msg_box.setDefaultButton(QtWidgets.QMessageBox.Cancel)
                response = msg_box.exec()
                if response == QtWidgets.QMessageBox.Save:
                    dirname = os.path.dirname(file_name[0])
                    for img, f in self.canvas.full_image_names.items():
                        dest = os.path.join(dirname, img)
                        try:
                            shutil.copyfile(f, dest)
                        except shutil.SameFileError:
                            continue
                    self.canvas.full_image_names = {img:os.path.join(dirname, img) for img in self.canvas.points.keys()}
                    self.save(True, file_name=file_name)
            else:
                if self.canvas.save_points(file_name[0]) is False:
                    msg_box = QtWidgets.QMessageBox()
                    msg_box.setWindowTitle('ERROR')
                    msg_box.setText('Save Failed!')
                    msg_box.setInformativeText('It appears you cannot save your pnt file in the working directory, possibly due to permissions.\n\nEither change the permissions on the folder or click the SAVE button and select another location outside of the working directory. Remember to copy of the pnt file back into the current working directory. ')
                    msg_box.setStandardButtons(QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Cancel)
                    msg_box.setDefaultButton(QtWidgets.QMessageBox.Save)
                    response = msg_box.exec()
                    if response == QtWidgets.QMessageBox.Save:
                        self.save(True)

    def select_tree_item(self, item):
        selectionModel = self.classTree.selectionModel()
        flags = QtCore.QItemSelectionModel.Select | QtCore.QItemSelectionModel.Rows
        selected = QtCore.QItemSelection()
        if item.parent() is None:
            index = self.classModel.indexFromItem(item)
        else:
            category_item = item.parent()
            rows = category_item.rowCount()
            category_index = self.classModel.indexFromItem(category_item)
            row = 0
            for i in range(rows):
                child = category_item.child(i, 0)
                if child.data(0) == item.data(0):
                    row = i
                    break
            index = self.classModel.index(row, 0, category_index)
        selectionModel.clearSelection()
        selectionModel.select(index, flags)

    def select_tree_item_from_name(self, name):
        for category_row in range(self.classModel.rowCount()):
            category_index = self.classModel.index(category_row, 0)
            category_item = self.classModel.itemFromIndex(category_index)
            if category_item.data(0) == name:
                self.select_tree_item(category_item)
                return
            category_rows = category_item.rowCount()
            for i in range(category_rows):
                child = category_item.child(i, 0)
                if child.data(0) == name:
                    self.select_tree_item(child)
                    self.classTree.setExpanded(category_index, True)
                    self.tree_expanded[category_item.data(0)] = True
                    return

    def select_model_item(self, model_index):
        item = self.model.itemFromIndex(model_index)
        if item.isSelectable():
            if item.column() != 0:
                index = self.model.index(item.row(), 0)
                item = self.model.itemFromIndex(index)
            text = item.text()
            if text == "Top" or text == "Bottom":
                ecu_name = item.parent().parent().text()
                pcb_name = item.parent().text()
                image = self.canvas.ecus[ecu_name][pcb_name][text]
                path = os.path.join(self.canvas.directory, image)
                self.canvas.load_image(path)

    def selection_changed(self, selected, deselected):
        if len(selected.indexes()) > 0:
            index = selected.indexes()[0]
            item = self.classModel.itemFromIndex(index)
            self.canvas.current_selection = item
            name = item.data(0)
            categories = list(self.canvas.categories)
            if name in categories:
                self.canvas.set_current_category(name)
                self.canvas.set_current_class(None)
            else:
                # also automatically sets corrresponding category
                self.canvas.set_current_class(name)
            font = item.font()
            font.setBold(True)
            item.setFont(font)
            if len(deselected.indexes()) > 0:
                item = self.classModel.itemFromIndex(deselected.indexes()[0])
                font = item.font()
                font.setBold(False)
                item.setFont(font)
        elif len(selected.indexes()) == 0 and len(deselected.indexes()) > 0:
            item = self.classModel.itemFromIndex(deselected.indexes()[0])
            font = item.font()
            font.setBold(False)
            item.setFont(font)
        else:
            self.canvas.set_current_class(None)
        self.class_selection_changed.emit()

    def set_active_point_color(self, color):
        icon = QtGui.QPixmap(20, 20)
        icon.fill(color)
        self.labelPointColor.setPixmap(icon)
        self.canvas.set_point_color(color)

    def set_active_class(self, row):
        if row < self.classTree.rowCount():
            self.classTree.selectRow(row)

    def set_grid_color(self, color):
        icon = QtGui.QPixmap(20, 20)
        icon.fill(color)
        self.labelGridColor.setPixmap(icon)
        self.canvas.set_grid_color(color)

    def openContextMenu(self, position):
        indexes = self.sender().selectedIndexes()
        index = self.classTree.indexAt(position)
        if not index.isValid() or index.column() != 0:
            return
        menu = QMenu()
        action_rename = menu.addAction("Rename")
        action_rename.triggered.connect(lambda: self.inputDialog.setNames(index))
        action_delete = menu.addAction("Delete")
        action_delete.triggered.connect(lambda: self.remove_class(indexes=[index]))
        menu.exec_(self.sender().viewport().mapToGlobal(position))

    def openEcuContextMenu(self, position):
        indexes = self.sender().selectedIndexes()
        index = self.treeView.indexAt(position)
        if not index.isValid() or index.column() != 0:
            return
        nodes = []
        while index.isValid():
            nodes.insert(0, index.data())
            index = index.parent()
        menu = QMenu()
        action_rename = menu.addAction("Remove")
        action_rename.triggered.connect(lambda: self.remove_from_ecus(nodes))
        menu.exec_(self.sender().viewport().mapToGlobal(position))
        self.display_count_tree()
        self.display_classes()

    def remove_from_ecus(self, nodes):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setWindowTitle('Warning')
        msgBox.setText('You are about to remove parts from an ECU')
        msgBox.setInformativeText('Do you want to continue?')
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Cancel | QtWidgets.QMessageBox.Ok)
        msgBox.setDefaultButton(QtWidgets.QMessageBox.Cancel)
        response = msgBox.exec()
        if response == QtWidgets.QMessageBox.Ok:
            self.canvas.remove_from_ecus(nodes)

    def update_point_count(self, image_name, class_name, count):
        if image_name not in self.canvas.points:
            self.display_count_tree()
        else:
            class_item = self.get_item_from_name(class_name)
            category_item = class_item.parent()
            row = class_item.row()
            category_item.child(row, 1).setData(str(count), QtCore.Qt.EditRole)
            total_count = 0
            for i in range(category_item.rowCount()):
                total_count += int(category_item.child(i, 1).data(0))
            self.classModel.itemFromIndex(self.classModel.index(category_item.row(), 1)).setData(str(total_count), QtCore.Qt.EditRole)
            total_count = 0
            for i in range(self.classModel.rowCount()):
                index = self.classModel.index(i, 1)
                item = self.classModel.itemFromIndex(index)
                total_count += int(item.data(0))
            self.display_count_tree()

    def update_ui_settings(self):
        ui = self.canvas.ui
        color = QtGui.QColor(ui['point']['color'][0], ui['point']['color'][1], ui['point']['color'][2])
        self.set_active_point_color(color)
        self.spinBoxPointRadius.setValue(ui['point']['radius'])
        color = QtGui.QColor(ui['grid']['color'][0], ui['grid']['color'][1], ui['grid']['color'][2])
        self.set_grid_color(color)
        self.spinBoxGrid.setValue(ui['grid']['size'])

    def update_from_drop(self, new_category, classname, index):
        category = self.canvas.get_category_from_class(classname)
        self.canvas.move_class(classname, category, new_category, index)
        self.display_classes()
