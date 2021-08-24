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
from itertools import cycle
from PyQt5 import QtCore, QtWidgets, QtGui

from ddg import Canvas, SearchDialog
from ddg.canvas import EditStyle, Scale, completion
from ddg import PointWidget
from .ui.central_widget_ui import Ui_CentralWidget as CLASS_DIALOG

def getText(widget):
    if isinstance(widget, (LineEdit, QtWidgets.QLineEdit)):
        return widget.text()
    elif isinstance(widget, QtWidgets.QComboBox):
        return widget.currentText()
    return None

def setText(widget, text):
    if isinstance(widget, (LineEdit, QtWidgets.QLineEdit)):
        return widget.setText(text)
    elif isinstance(widget, QtWidgets.QComboBox):
        return widget.setCurrentText(text)
    return None

class LineEdit(QtWidgets.QLineEdit):
    copy_all_signal = QtCore.pyqtSignal()
    paste_all_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None, available_actions=["Copy", "Copy All Details", "Paste", "Paste All Details", "Convert To Uppercase"]):
        super().__init__(parent)
        self.setFrame(False)
        self.available_actions = available_actions
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.createMenu)

    def createMenu(self, position):

        self.menu = QtWidgets.QMenu()
        copy_one = self.menu.addAction("Copy (CTRL+C)")
        paste_one = self.menu.addAction("Paste (CTRL+V)")
        cut_one = self.menu.addAction("Cut (CTRL+X)")
        self.menu.addSeparator()
        copy_all = self.menu.addAction("Copy All Details")
        paste_all = self.menu.addAction("Paste All Details")
        self.menu.addSeparator()
        convert_to_uppercase = self.menu.addAction("Convert to Uppercase")
        convert_to_lowercase = self.menu.addAction("Convert to Lowercase")
        if "Copy All Details" not in self.available_actions:
            copy_all.setEnabled(False)
        if "Paste All Details" not in self.available_actions:
            paste_all.setEnabled(False)
        if "Convert To Uppercase" not in self.available_actions:
            convert_to_uppercase.setEnabled(False)
            convert_to_lowercase.setEnabled(False)

        self.menu.addSeparator()
        search_actions = []
        for name in ["Google", "Digi-Key", "Findchips"]:
            search_actions.append(self.menu.addAction("Search {}".format(name)))

        action = self.menu.exec_(self.mapToGlobal(position))
        if action is None:
            return
        if action == copy_one:
            self.copy_one()
        elif action == paste_one:
            self.paste_one()
        elif action == cut_one:
            self.cut_one()
        elif action == copy_all:
            self.copy_all_signal.emit()
        elif action == paste_all:
            self.paste_all_signal.emit()
        elif action == convert_to_uppercase:
            self.convert_to_uppercase()
        elif action == convert_to_lowercase:
            self.convert_to_lowercase()
        elif action in search_actions:
            self.websearch(action.text())

    def websearch(self, where):
        if self.hasSelectedText():
            text = self.selectedText()
        else:
            text = self.text()
        addr = r"https:\\www."
        if "Google" in where:
            addr = addr + "google.com/search?q=" + text.replace(" ", "+")
        elif "Digi-Key" in where:
            addr = addr + "digikey.com/product-search/en?keywords=" + text
        elif "Findchips" in where:
            addr = addr + "findchips.com/search/" + text
        import webbrowser as wb
        wb.get("windows-default").open(addr)

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        key = a0.key()
        if key == QtCore.Qt.Key_Escape:
            self.clearFocus()
        else:
            return super().keyPressEvent(a0)

    def copy_one(self):
        clipboard = QtWidgets.QApplication.clipboard()
        if len(self.selectedText()) > 0:
            text = self.selectedText()
        else:
            text = self.text()
        clipboard.setText(text)

    def convert_to_uppercase(self):
        text = self.text().upper()
        self.setText(text)
        self.textEdited.emit(text)

    def convert_to_lowercase(self):
        text = self.text().lower()
        self.setText(text)
        self.textEdited.emit(text)

    def cut_one(self):
        clipboard = QtWidgets.QApplication.clipboard()
        if len(self.selectedText()) > 0:
            text = self.selectedText()
        else:
            text = self.text()
        clipboard.setText(text)
        text = self.text().replace(text, "")
        self.setText(text)
        self.textEdited.emit(text)

    def focusInEvent(self, a0):
        self.setFrame(True)
        return super().focusInEvent(a0)

    def focusOutEvent(self, a0):
        self.setFrame(False)
        return super().focusOutEvent(a0)

    def paste_one(self):
        clipboard = QtWidgets.QApplication.clipboard()
        text = self.text()
        n = len(text)
        ctext = clipboard.text()
        if len(self.selectedText()) > 0:
            text = text.replace(self.selectedText(), ctext).strip()
        else:
            pos = min(self.cursorPosition(), n)
            text = text[:pos] + ctext + text[pos:]
        self.setText(text)
        self.textEdited.emit(text)


class CentralWidget(QtWidgets.QDialog, CLASS_DIALOG):

    load_custom_data = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None):
        from functools import partial
        _translate = QtCore.QCoreApplication.translate
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self)
        self.canvas = Canvas()

        self.point_widget = PointWidget(self.canvas, self)
        self.findChild(QtWidgets.QFrame, 'framePointWidget').layout().addWidget(self.point_widget)
        self.point_widget.hide_custom_fields.connect(self.hide_custom_fields)
        self.point_widget.saving.connect(self.display_quick_save)
        self.point_widget.class_selection_changed.connect(self.display_attributes)
        self.point_widget.lineEditSurveyId.textEdited.connect(self.set_survey_id)

        self.save_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("Ctrl+S")), self)  # quick save using Ctrl+S
        self.save_shortcut.setContext(QtCore.Qt.WidgetWithChildrenShortcut)
        self.save_shortcut.activated.connect(self.point_widget.quick_save)

        self.graphicsView.setScene(self.canvas)
        self.graphicsView.drop_complete.connect(self.canvas.load)
        self.graphicsView.region_selected.connect(self.canvas.select_points)
        self.graphicsView.delete_selection.connect(self.canvas.delete_selected_points)
        self.graphicsView.clear_selection.connect(self.canvas.clear_selection)
        self.graphicsView.relabel_selection.connect(self.canvas.relabel_selected_points)
        self.graphicsView.measure_area.connect(self.canvas.measure_area)
        self.graphicsView.toggle_points.connect(self.point_widget.checkBoxDisplayPoints.toggle)
        self.graphicsView.toggle_grid.connect(self.point_widget.checkBoxDisplayGrid.toggle)
        self.graphicsView.scale_selected.connect(self.set_scale)
        self.graphicsView.select_class.connect(self.point_widget.select_tree_item_from_name)
        self.graphicsView.add_class.connect(lambda: self.point_widget.add_class(askname=False))
        self.graphicsView.search.connect(self.search)

        self.graphicsView.add_point.connect(self.canvas.add_point)
        self.graphicsView.display_pointer_coordinates.connect(self.display_pointer_coordinates)
        self.graphicsView.find_point.connect(self.find_point)
        self.canvas.image_loaded.connect(self.graphicsView.image_loaded)
        self.canvas.directory_set.connect(self.display_working_directory)

        # Image data fields
        self.canvas.image_loaded.connect(self.display_coordinates)
        self.canvas.image_loaded.connect(self.display_attributes)
        self.canvas.fields_updated.connect(self.display_attributes)

        self.dataLineEditsNames = ["lineEdit_ecu", "lineEdit_pcb", "comboBox_pos", "lineEditX", "lineEditY"]
        pcbAttr = ["ECU Name", "PCB Name", "Side", "Length", "Width"]

        self.attribute_widget_names = ["lineEdit_description", "lineEdit_marking", 
                     "lineEdit_partnumber", "comboBox_manufacturer", "comboBox_package", "comboBox_placement", 
                     "lineEdit_diameter", "lineEdit_length", "lineEdit_width", "lineEdit_height", 
                     "lineEdit_pincount", "comboBox_metrik"]

        self.attribute_names = ["Description", "Marking", "Partnumber", "Manufacturer", "Package", "Placement", "Diameter",
                             "Length", "Width", "Height", "IO/Pin Count", "Metrik"]

        for i, k in enumerate(self.dataLineEditsNames):
            box = self.groupBoxImageData
            layout = self.gridLayout_2
            if "line" in k:
                widget = LineEdit(box, available_actions=["Copy", "Paste"])
                widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
                widget.setAcceptDrops(False)
                widget.setObjectName(k)
                widget.setDisabled(True)
                widget.returnPressed.connect(self.cycle_edits)
                if "X" in k or "Y" in k:
                    widget.textEdited.connect(self.update_pcb_info)
                else:
                    widget.returnPressed.connect(self.update_ecu_name)
            else:
                widget = QtWidgets.QComboBox()
                widget.addItems(["Top", "Bottom"])
                widget.setDisabled(True)
                widget.setCurrentIndex(0)
                widget.activated.connect(self.update_ecu_name)
            layout.addWidget(widget, i, 1, 1, 1)

            label = QtWidgets.QLabel(box)
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(label.sizePolicy().hasHeightForWidth())
            label.setSizePolicy(sizePolicy)
            label.setText(_translate("CentralWidget", pcbAttr[i]))
            layout.addWidget(label, i, 0, 1, 1)
            setattr(self, k, widget)

        self.attribute_widgets = {}
        for i, k in enumerate(self.attribute_widget_names):
            box = self.groupBoxCustomFields
            layout = self.gridLayout
            if "line" in k:
                widget = LineEdit(box)
                widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
                widget.setAcceptDrops(False)
                widget.setObjectName(k)
                widget.setDisabled(True)
                widget.textEdited.connect(partial(self.update_attributes, name=k))
                widget.returnPressed.connect(self.cycle_edits)
                widget.copy_all_signal.connect(self.copy_all_attributes)
                widget.paste_all_signal.connect(self.paste_all_attributes)
            else:
                widget = QtWidgets.QComboBox(box)
                widget.setDisabled(True)
                widget.setObjectName(k)
                widget.setLineEdit(LineEdit())
                widget.currentTextChanged.connect(partial(self.update_attributes, name=k))
                widget.currentIndexChanged.connect(partial(self.update_attributes, name=k))
                widget.lineEdit().textEdited.connect(partial(self.update_attributes, name=k))
                widget.lineEdit().returnPressed.connect(self.cycle_edits)
                widget.lineEdit().copy_all_signal.connect(self.copy_all_attributes)
                widget.lineEdit().paste_all_signal.connect(self.paste_all_attributes)

            layout.addWidget(widget, i, 1, 1, 1)
            widget.setFrame(False)

            label = QtWidgets.QLabel(box)
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(label.sizePolicy().hasHeightForWidth())
            label.setSizePolicy(sizePolicy)
            label.setText(_translate("CentralWidget", self.attribute_names[i]))
            layout.addWidget(label, i, 0, 1, 1)

            self.attribute_widgets[self.attribute_names[i]] = widget
            setattr(self, k, widget)
            setattr(self, k.replace("lineEdit", "label").replace("comboBox", "label"), label)

        self.info_widgets = self.dataLineEditsNames.copy()
        self.info_widgets.extend(self.attribute_widget_names)
        self.set_tool_tips()

        package_completer = QtWidgets.QCompleter(completion.packages)
        package_completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.comboBox_package.lineEdit().setCompleter(package_completer)
        self.comboBox_package.addItems(completion.packages)
        self.comboBox_package.setCurrentText("")
        package_completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)

        manufacturer_completer = QtWidgets.QCompleter(completion.manufacturers)
        manufacturer_completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.comboBox_manufacturer.lineEdit().setCompleter(manufacturer_completer)
        self.comboBox_manufacturer.addItems(completion.manufacturers)
        self.comboBox_manufacturer.setCurrentText("")
        manufacturer_completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)

        metrik_completer = QtWidgets.QCompleter(completion.metriks)
        metrik_completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.comboBox_metrik.lineEdit().setCompleter(metrik_completer)
        self.comboBox_metrik.addItems(completion.metriks)
        self.comboBox_metrik.setCurrentText("")
        metrik_completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)

        placement_list = list(sorted(completion.placement))
        placement_completer = QtWidgets.QCompleter(sorted(placement_list))
        placement_completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.comboBox_placement.lineEdit().setCompleter(placement_completer)
        self.comboBox_placement.addItems(placement_list)
        self.comboBox_placement.setCurrentText("")
        placement_completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)

        # self.pushButtonFolder.clicked.connect(self.select_folder)
        self.pushButtonZoomOut.clicked.connect(self.graphicsView.zoom_out)
        self.pushButtonZoomIn.clicked.connect(self.graphicsView.zoom_in)

        self.quick_save_frame = QtWidgets.QFrame(self.graphicsView)
        self.quick_save_frame.setStyleSheet("QFrame { background: #4caf50;color: #FFF;font-weight: bold}")
        self.quick_save_frame.setLayout(QtWidgets.QHBoxLayout())
        self.quick_save_frame.layout().addWidget(QtWidgets.QLabel('Saving...'))
        self.quick_save_frame.setGeometry(3, 3, 100, 35)
        self.quick_save_frame.hide()
        
        self.toolBar = QtWidgets.QToolBar()
        self.toolLayout.addWidget(self.toolBar)
        self.pointsToolButton = QtWidgets.QToolButton()
        self.pointsToolButton.setText("Count")
        self.pointsToolButton.setCheckable(True)
        self.pointsToolButton.setChecked(True)
        self.pointsToolButton.setAutoExclusive(True)
        self.toolBar.addWidget(self.pointsToolButton)
        self.rectsToolButton = QtWidgets.QToolButton()
        self.rectsToolButton.setText("Measure")
        self.rectsToolButton.setCheckable(True)
        self.rectsToolButton.setChecked(False)
        self.rectsToolButton.setAutoExclusive(True)
        self.toolBar.addWidget(self.rectsToolButton)

    def reset_toolbar(self):
        self.pointsToolButton.setChecked(True)
        self.rectsToolButton.setChecked(False)
        self.canvas.set_edit_style(EditStyle.POINTS)

    def copy_all_attributes(self):
        from os import linesep
        clipboard = QtWidgets.QApplication.clipboard()
        text = ""
        for _, widget in self.attribute_widgets.items():
            text = text + getText(widget) + linesep
        clipboard.setText(text.strip(linesep))

    def paste_all_attributes(self):
        from os import linesep
        clipboard = QtWidgets.QApplication.clipboard()
        text = clipboard.text()
        if linesep in text:
            text = text.split(linesep)
        elif "\n" in text:
            text = text.split("\n")
        if text[-1] == "\n" or text[-1] == linesep:
            text = text[:-1]
        attributes = list(self.attribute_widgets.keys())
        for i, t in enumerate(text):
            if i == len(attributes):
                break
            setText(self.attribute_widgets[attributes[i]], text[i])

    def cycle_edits(self):
        cycled = cycle(self.info_widgets)
        for k in cycled:
            w = getattr(self, k)
            if w.hasFocus():
                w.clearFocus()
                nextW = getattr(self, next(cycled))
                nextW.setFocus()
                break

    def display_pointer_coordinates(self, point):
        img = self.canvas.current_image_name
        image_scale = self.canvas.image_scale.get(img, Scale())
        scale = image_scale.scale
        left = image_scale.left
        top = image_scale.top
        unit = image_scale.unit
        text = "{:.1f}, {:.1f} {}".format(int(point.x())*scale - left, int(point.y())*scale - top, unit)
        self.posLabel.setText(text)

    def display_coordinates(self, directory, image):
        if self.canvas.current_image_name is None:
            for i, k in enumerate(self.dataLineEditsNames):
                getattr(self, k).setDisabled(True)
        else:
            for i, k in enumerate(self.dataLineEditsNames):
                getattr(self, k).setDisabled(False)
        ecu_name, pcb_name, position = self.canvas.get_ecu_info(image)
        self.lineEditX.setText(self.canvas.pcb_info[image]['x'])
        self.lineEditY.setText(self.canvas.pcb_info[image]['y'])
        self.lineEdit_ecu.setText(ecu_name)
        self.comboBox_pos.setCurrentText(position)
        self.lineEdit_pcb.setText(pcb_name)

    def display_attributes(self):
        if self.canvas.current_class_name is None or self.canvas.current_image_name is None:
            for _, w in self.attribute_widgets.items():
                setText(w, "")
                w.setDisabled(True)
        else:
            for k, widget in self.attribute_widgets.items():
                widget.setDisabled(False)
                value = self.canvas.class_attributes[self.canvas.current_class_name].get(k, "")
                setText(widget, value)

    def display_ecu_name(self):
        if self.canvas.current_image_name is not None:
            ecu_name, pcb_name, position = self.canvas.get_ecu_info(self.canvas.current_image_name)
            self.lineEdit_ecu.setText(ecu_name)
            self.lineEdit_pcb.setText(pcb_name)
            self.comboBox_pos.setCurrentText(position)
                
    def display_working_directory(self, directory):
        self.labelWorkingDirectory.setText(directory)

    def display_quick_save(self):
        self.quick_save_frame.show()
        QtCore.QTimer.singleShot(500, self.quick_save_frame.hide)

    def find_point(self, point):
        self.graphicsView.hovered_name = None
        if self.canvas.current_image_name is None:
            return
        item = self.canvas.itemAt(point, QtGui.QTransform())
        if item is None or not isinstance(item, QtWidgets.QGraphicsEllipseItem):
            return
        classes = self.canvas.points[self.canvas.current_image_name]
        if len(classes) == 0:
            return
        for c, points in classes.items():
            for p in points:
                if item.contains(p):
                    self.graphicsView.hovered_name = c
                    break

    def hide_custom_fields(self, hide):
        if hide is True:
            self.frameCustomField.hide()
        else:
            self.frameCustomField.show()

    def resizeEvent(self, theEvent):
        self.graphicsView.resize_image()

    def set_scale(self, rect):
        mm, ok = QtWidgets.QInputDialog.getInt(self, 'Set scale', 'Enter Length (x-axis) in mm')
        if ok:
            self.canvas.set_scale(mm, rect)

    def select_folder(self):
        name = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select image folder', self.canvas.directory)
        if name != '':
            self.canvas.load([QtCore.QUrl('file:{}'.format(name))])

    def set_tool_tips(self):
        self.lineEdit_ecu.setToolTip("ECU name of active PCB. To change name hit 'Enter'")
        self.lineEdit_pcb.setToolTip("Name of active PCB. To change name hit 'Enter'")
        self.lineEditX.setToolTip("Width of active PCB. Saved when edited")
        self.lineEditY.setToolTip("Width of active PCB. Saved when edited")
        for attr, edit in zip(self.attribute_names, self.attribute_widget_names):
            widget = getattr(self, edit)
            widget.setToolTip("{:} of active component. Saved when text changed.".format(attr))


    def update_pcb_info(self, info):
        x = self.lineEditX.text()
        y = self.lineEditY.text()
        self.canvas.save_pcb_info(x, y)

    def update_ecu_name(self):
        new_name = None
        ecu_name, pcb_name, position = self.canvas.get_ecu_info(self.canvas.current_image_name)
        new_ecu = self.lineEdit_ecu.text()
        if len(ecu_name) == 1:
            self.lineEdit_ecu.setText(ecu_name)
            new_ecu = ecu_name
        new_pcb = self.lineEdit_pcb.text()
        if len(pcb_name) == 1:
            self.lineEdit_pcb.setText(pcb_name)
            new_ecu = pcb_name
        new_pos = self.comboBox_pos.currentText()
        if new_ecu != ecu_name:
            new_name = new_ecu
            pcb_name = None
            position = None
        elif new_pcb != pcb_name:
            new_name = new_pcb
            position = None
        elif new_pos != position:
            new_name = new_pos
        
        if new_name:
            done = self.canvas.rename_ecu(new_name, ecu_name, pcb_name, position)
            if not done:
                self.lineEdit_ecu.setText(ecu_name)
                self.lineEdit_pcb.setText(pcb_name)
                self.comboBox_pos.setCurrentText(position)
            else:
                self.point_widget.display_count_tree()
        
    def update_attributes(self, text, name):
        if "combo" in name.lower():
            text = getattr(self, name).currentText()
        i = self.attribute_widget_names.index(name)
        attr = self.attribute_names[i]
        self.canvas.set_component_attribute(attr, text)

    def set_survey_id(self):
        self.canvas.survey_id = self.point_widget.lineEditSurveyId.text()

    def search(self):
        dialog = SearchDialog(self)
        dialog.exec_()