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
import io
import json
import glob
import numpy as np
from enum import Enum
import dataclasses
from zipfile import ZipFile
from dataclasses import dataclass
from ddg.config import AutoCompleteFile, DDConfig, RecentlyUsed
from .ui.ecu_input_dialog_ui import Ui_ECUInputDialog as ECU_DIALOG

from PIL import Image
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QDialog

completion = AutoCompleteFile()
recentlyUsed = RecentlyUsed()
Image.MAX_IMAGE_PIXELS = 1000000000

class EditStyle(Enum):
    POINTS = 1
    RECTS = 2

def pixmap_from_image_array(array, channels):
    arr = np.array(array[1:-1, 1:-1, ...]) # necessary bugfix for some images. Qt cannot add the pixmap if this line is removed
    if channels == 1:
        qt_image = QtGui.QImage(arr.data, arr.shape[1], arr.shape[0], QtGui.QImage.Format_Grayscale8)
    else:
        # Apply basic min max stretch to the image
        for chan in range(channels):
            arr[:, :, chan] = np.interp(arr[:, :, chan], (arr[:, :, chan].min(), arr[:, :, chan].max()), (0, 255))
        bpl = int(arr.nbytes / arr.shape[0])
        if arr.shape[2] == 4:
            qt_image = QtGui.QImage(arr.data, arr.shape[1], arr.shape[0], QtGui.QImage.Format_RGBA8888)
        else:
            qt_image = QtGui.QImage(arr.data, arr.shape[1], arr.shape[0], bpl, QtGui.QImage.Format_RGB888)
    return QtGui.QPixmap.fromImage(qt_image)

def generate_file_list(files):
    result = {}
    for f in files:
        _, ext = os.path.splitext(f)
        hashname = str(hash(f)) + ext
        result[f] = hashname
    return result

@dataclass
class Scale:
    scale: float = 1
    unit: str = "px"
    top: int = 0
    left: int = 0

    @staticmethod
    def from_dict(dictionary):
        scale = Scale()
        fields = dataclasses.fields(Scale)
        for field in fields:
            setattr(scale, field.name, dictionary.get(field.name, field.default))
        return scale

def attributes_from_dict(attrs):
    return {k:Attributes.from_dict(v) for k, v in attrs.items()}

class Attributes(dict):
    DEFAULT_KEYS = ["Name", "Partnumber", "Description", "Short Description", "Placement",
                    "Manufacturer", "Marking", "Datasheet", "Diameter", "Length", "Width", 
                    "Height", "Weight", "Package", "IO/Pin Count", "Metrik"]
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        for k in Attributes.DEFAULT_KEYS:
            self[k] = ""

    def __delitem__(self, k):
        if not k in Attributes.DEFAULT_KEYS:
            if self.has_key(k):
                dict.__delitem__(self, k)
    @staticmethod
    def from_dict(d):
        a = Attributes()
        a.update(d)
        return a

class ECUInputDialog(QDialog, ECU_DIALOG):
    def __init__(self, canvas):
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self)
        self.canvas = canvas
        self.pushButtonCancel.clicked.connect(self.cancel)
        self.pushButtonOk.clicked.connect(self.ok)
        self.ecu_comboBox.currentTextChanged.connect(self.set_pcb_names)
        self.ecu_comboBox.currentTextChanged.connect(self.check_ok)
        self.pcb_comboBox.currentTextChanged.connect(self.check_ok)
        self.pos_comboBox.currentTextChanged.connect(self.check_ok)
        self.last_exit = 0
        self.w = 500
        self.h = 167

    def check_ok(self):
        ecu_name, pcb_name, pos = self.ecu_comboBox.currentText(), self.pcb_comboBox.currentText(), self.pos_comboBox.currentText()
        if ecu_name == "" or pcb_name == "":
            self.pushButtonOk.setEnabled(False)
            return
        try:
            _ = self.canvas.ecus[ecu_name][pcb_name][pos]
        except KeyError:
            self.pushButtonOk.setEnabled(True)
            return
        self.pushButtonOk.setEnabled(False)

    def set_pcb_names(self, ecu_name):
        self.pcb_comboBox.model().clear()
        if ecu_name in self.canvas.ecus.keys():
            for pcb_name in self.canvas.ecus[ecu_name].keys():
                self.pcb_comboBox.addItem(pcb_name)
        else:
            self.pcb_comboBox.addItem("PCB 1")
        self.pcb_comboBox.setCurrentIndex(0)
        self.pcb_comboBox.setEditable(True)

    def run(self, image):
        self.image = os.path.basename(image)
        self.setWindowTitle(self.image)
        ecu_names = list(self.canvas.ecus.keys())
        self.ecu_comboBox.model().clear()
        if len(ecu_names) == 0:
            self.ecu_comboBox.addItem("ECU 1")
        else:
            for ecu_name in ecu_names:
                self.ecu_comboBox.addItem(ecu_name)
        self.ecu_comboBox.setCurrentIndex(0)
        self.ecu_comboBox.setEditable(True)
        self.check_ok()
        pixmap = QtGui.QPixmap(image)
        rect = self.geometry()
        w, h = rect.width(), rect.height()
        self.imageLabel.setPixmap(pixmap.scaled(w, h, QtCore.Qt.KeepAspectRatio))
        self.imageLabel.show()
        desktop_rect = QtWidgets.QApplication.desktop().availableGeometry(self)
        center = desktop_rect.center()
        self.setGeometry(center.x()-self.w//2, center.y()-self.h//2, self.w, self.h)
        self.exec_()

    def cancel(self):
        self.last_exit = 0
        self.close()
        return 1

    def ok(self):
        ecu_name = self.ecu_comboBox.currentText()
        pcb_name = self.pcb_comboBox.currentText()
        position = self.pos_comboBox.currentText()
        if ecu_name != "" and pcb_name != "":
            self.canvas.set_ecu_info(ecu_name, pcb_name, position, self.image)
            self.last_exit = 1
            self.close()
            return 1
        return 0

class PointSaver(QtCore.QThread):
    def __init__(self, filename, packaged_points, pixmaps):
        QtCore.QThread.__init__(self)
        self.filename = filename
        self.packaged_points = packaged_points
        self.pixmaps = pixmaps

    def run(self):
        _, ext = os.path.splitext(self.filename)
        if ext == ".pnt":
            with open(self.filename, 'w') as f:
                json.dump(self.packaged_points, f)
        elif ext == ".pnts":
            basename = os.path.basename(self.filename)
            pntname = basename.replace(".pnts", ".pnt")
            dirname = os.path.dirname(self.filename)
            with ZipFile(self.filename, "w") as z:
                z.writestr(pntname, json.dumps(self.packaged_points))
                for img, px in self.pixmaps.values():
                    _, ext = os.path.splitext(img)
                    savename = os.path.join(dirname, str(hash(img)) + ext)
                    image = Image.fromqpixmap(px)
                    image.save(savename)
                    z.write(savename, img)
                    os.remove(savename)

class Canvas(QtWidgets.QGraphicsScene):
    image_loaded = QtCore.pyqtSignal(str, str)
    points_loaded = QtCore.pyqtSignal(str)
    points_saved = QtCore.pyqtSignal(str)
    directory_set = QtCore.pyqtSignal(str)
    fields_updated = QtCore.pyqtSignal()
    points_updated = QtCore.pyqtSignal()
    update_point_count = QtCore.pyqtSignal(str, str, int)
    DEFAULT_COLORS = {"Resistor":QtGui.QColor(QtCore.Qt.black), "Capacitor":QtGui.QColor(QtCore.Qt.gray), "Crystal":QtGui.QColor(QtCore.Qt.green), 
                      "Diode": QtGui.QColor(QtCore.Qt.blue), "Inductor":QtGui.QColor(QtCore.Qt.cyan), "Integrated Circuit":QtGui.QColor(QtCore.Qt.yellow).darker(200), 
                      "Transistor":QtGui.QColor(QtCore.Qt.darkYellow), "Discrete < 3 Pins":QtGui.QColor(QtCore.Qt.magenta), 
                      "Discrete > 3 Pins":QtGui.QColor(QtCore.Qt.darkMagenta), "Connectors":QtGui.QColor(QtCore.Qt.cyan)}

    def __init__(self):
        QtWidgets.QGraphicsScene.__init__(self)
        self.reset()

    @property
    def classes(self):
        classes = []
        for _, v in self.data.items():
            classes.extend(v)
        return classes

    def add_class(self, category, class_name):
        if class_name not in self.classes:
            self.set_changed(True)
            a = Attributes()
            a["Name"] = class_name
            self.data[category].append(class_name)
            self.colors[class_name] = Canvas.DEFAULT_COLORS.get(category, QtGui.QColor(QtCore.Qt.black))
            self.class_attributes[class_name] = a
            self.class_visibility[class_name] = True

    def add_category(self, name):
        if name not in self._categories:
            self.set_changed(True)
            self.data[name] = []
            self._categories.append(name)

    def add_point(self, point):
        self.set_changed(True)
        if self.edit_style != EditStyle.POINTS:
            return

        if self.current_image_name is None or self.current_class_name is None:
            return

        if not self.class_visibility[self.current_class_name]:
            return

        for image in self.points.keys():
            if self.current_class_name not in self.points[image]:
                self.points[image][self.current_class_name] = []
        display_radius = self.ui['point']['radius']
        active_color = QtGui.QColor(self.ui['point']['color'][0], self.ui['point']['color'][1], self.ui['point']['color'][2])
        active_brush = QtGui.QBrush(active_color, QtCore.Qt.SolidPattern)
        active_pen = QtGui.QPen(active_brush, 2)
        self.points[self.current_image_name][self.current_class_name].append(point)
        # count = 0
        # for image in self.points.keys():
        #     count += len(self.points[image][self.current_class_name])
        count = len(self.points[self.current_image_name][self.current_class_name])
        self.addEllipse(QtCore.QRectF(point.x() - ((display_radius - 1) / 2), point.y() - ((display_radius - 1) / 2), display_radius, display_radius), active_pen, active_brush)
        self.update_point_count.emit(self.current_image_name, self.current_class_name, count)

    @property
    def categories(self):
        i1 = list(sorted(self.data.keys()))
        i2 = list(sorted(self._categories))
        assert i1 == i2
        return self._categories

    def clear_grid(self):
        for graphic in self.items():
            if type(graphic) == QtWidgets.QGraphicsLineItem:
                self.removeItem(graphic)

    def clear_points(self):
        for graphic in self.items():
            if type(graphic) == QtWidgets.QGraphicsEllipseItem:
                self.removeItem(graphic)
            
    def clear_measures(self):
        for graphic in self.items():
            if type(graphic) == QtWidgets.QGraphicsPathItem:
                self.removeItem(graphic)
            elif type(graphic) == QtWidgets.QGraphicsTextItem:
                self.removeItem(graphic)

    def clear_pixmap(self):
        for graphic in self.items():
            self.removeItem(graphic)

    def clear_selection(self):
        self.selection = []
        if self.edit_style == EditStyle.RECTS:
            self.clear_measures()
            self.display_measures()
        elif self.edit_style == EditStyle.POINTS:
            self.clear_points()
            self.display_points()

    def delete_selected_points(self):
        self.set_changed(True)
        if self.current_image_name is not None:
            if self.edit_style == EditStyle.POINTS:
                points = self.points[self.current_image_name]
                for class_name, point in self.selection:
                    points[class_name].remove(point)
                    count = 0
                    for image in self.points.keys():
                        count += len(self.points[image].get(class_name, []))
                    self.update_point_count.emit(self.current_image_name, class_name, count)
                self.selection = []
                self.display_points()
            elif self.edit_style == EditStyle.RECTS:
                mrects = self.measure_rects[self.current_image_name]
                for selected in self.selection:
                    for i, mrect in enumerate(mrects):
                        if selected == mrect:
                            self.measure_rects[self.current_image_name].pop(i)
                            self.measure_rects_data[self.current_image_name].pop(i)
                            break
                self.selection = []
                self.display_measures()


    def display_grid(self):
        self.clear_grid()
        if self.current_image_name and self.show_grid:
            grid_color = QtGui.QColor(self.ui['grid']['color'][0], self.ui['grid']['color'][1], self.ui['grid']['color'][2])
            grid_size = self.ui['grid']['size']
            rect = self.itemsBoundingRect()
            brush = QtGui.QBrush(grid_color, QtCore.Qt.SolidPattern)
            pen = QtGui.QPen(brush, 1)
            for x in range(grid_size, int(rect.width()), grid_size):
                line = QtCore.QLineF(x, 0.0, x, rect.height())
                self.addLine(line, pen)
            for y in range(grid_size, int(rect.height()), grid_size):
                line = QtCore.QLineF(0.0, y, rect.width(), y)
                self.addLine(line, pen)

    def display_points(self):
        if self.edit_style != EditStyle.POINTS:
            return
        self.clear_points()
        if self.current_image_name in self.points:
            display_radius = self.ui['point']['radius']
            active_color = QtGui.QColor(self.ui['point']['color'][0], self.ui['point']['color'][1], self.ui['point']['color'][2])
            active_brush = QtGui.QBrush(active_color, QtCore.Qt.SolidPattern)
            active_pen = QtGui.QPen(active_brush, 2)
            for class_name in self.points[self.current_image_name]:
                if not self.class_visibility[class_name]:
                    continue
                points = self.points[self.current_image_name][class_name]
                brush = QtGui.QBrush(self.colors[class_name], QtCore.Qt.SolidPattern)
                pen = QtGui.QPen(brush, 2)
                for point in points:
                    if class_name == self.current_class_name:
                        self.addEllipse(QtCore.QRectF(point.x() - ((display_radius - 1) / 2), point.y() - ((display_radius - 1) / 2), display_radius, display_radius), active_pen, active_brush)
                    else:
                        self.addEllipse(QtCore.QRectF(point.x() - ((display_radius - 1) / 2), point.y() - ((display_radius - 1) / 2), display_radius, display_radius), pen, brush)

    def display_measures(self):
        if self.current_image_name is None or self.edit_style != EditStyle.RECTS:
            return
        self.clear_measures()

        white = QtGui.QColor(255, 255, 255)
        color = QtGui.QColor(self.ui['point']['color'][0], self.ui['point']['color'][1], self.ui['point']['color'][2])
        brush = QtGui.QBrush(color, QtCore.Qt.SolidPattern)
        pen = QtGui.QPen(brush, 2)

        image_scale = self.image_scale.get(self.current_image_name, Scale())
        scale = image_scale.scale
        unit = image_scale.unit

        # mrects = self.measure_rects[self.current_image_name].copy()
        mrects_data = self.measure_rects_data[self.current_image_name].copy()
        self.measure_rects[self.current_image_name] = []
        self.measure_rects_data[self.current_image_name] = []
        for mrect in mrects_data:
            x = mrect["x"]
            y = mrect["y"]
            width = mrect["width"]
            height = mrect["height"]
            ppath = QtGui.QPainterPath()
            ppath.setFillRule(QtCore.Qt.WindingFill)
            ppath.addRect(x, y, width, height)
            path = self.addPath(ppath, pen)

            topItem = self.addText("{:.1f} {}".format(width*scale, unit))
            topItem.setDefaultTextColor(white)
            font = topItem.font()
            font.setBold(True)
            topItem.setFont(font)
            topItem.setPos(x, y)

            leftItem = self.addText("{:.1f} {}".format(height*scale, unit))
            leftItem.setDefaultTextColor(white)
            leftItem.setPos(x, y + leftItem.boundingRect().width() + topItem.boundingRect().height()*1.05)
            leftItem.setRotation(-90)
            font = leftItem.font()
            font.setBold(True)
            leftItem.setFont(font)
            self.measure_rects[self.current_image_name].append(path)
            self.measure_rects_data[self.current_image_name].append(mrect)

    def prepare_export_counts(self):
        rows = []
        header = ["ECU", "PCB", "Short Description", "Component Description", "Top", "Bottom", "Manufacturer", "Partnumber", 
                "Marking", "Relevant Marking", "Package", "Placement", "Unit", "IO/Pin Count", 
                "Diameter", "Length", "Width", "Height", "Metrik"]
        rows.append(header)
        for ecu_name, pcbs in self.ecus.items():
            for pcb_name, positions in pcbs.items():
                top = positions.get("Top", "")
                bottom = positions.get("Bottom", "")
                for category in self.categories:
                    for class_name in self.data[category]:
                        count_top = len(self.points.get(top, {}).get(class_name, []))
                        count_bot = len(self.points.get(bottom, {}).get(class_name, []))
                        # count_tot = count_bot + count_top
                        attr = self.class_attributes[class_name]
                        row = [ecu_name, pcb_name, category, attr["Description"], count_top, count_bot, attr['Manufacturer'], 
                            attr["Partnumber"], attr["Marking"], "", attr["Package"], attr["Placement"], "", attr["IO/Pin Count"], attr["Diameter"], 
                            attr["Length"], attr["Width"], attr["Height"], attr["Metrik"]]
                        rows.append(row)
        return rows

    def export_counts(self, file_name):
        import csv
        rows = self.prepare_export_counts()
        with open(file_name, "w", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(rows[0])
            for row in rows[1:]:
                writer.writerow(row)

    def get_category_from_class(self, class_name):
        category = None
        for c, v in self.data.items():
            if class_name in v:
                category = c
                break
        return category

    def load(self, drop_list):
        peek = drop_list[0]
        if not isinstance(peek, str):
            peek = peek.toLocalFile()
        self.reset_undo_stack()
        image_format = [".jpg", ".jpeg", ".png", ".tif"]
        f = (lambda x: os.path.splitext(x)[1].lower() in image_format)
        if os.path.isdir(peek): # direcotry
            # strip off trailing sep from path
            osx_hack = os.path.join(peek, 'OSX')
            directory = os.path.split(osx_hack)[0]
            files = glob.glob(os.path.join(peek, '*'))
            image_list = sorted(list(filter(f, files)))
            ignore_message = False
            for img in image_list:
                basename = os.path.basename(img)
                if basename in self.points.keys(): 
                    if not ignore_message:
                        message = """
                                    <h1> Import Failed </h1>
                                    <p> You already imported a file {} </p> 
                                    <p> Ignore File? </p>""".format(basename)
                        msg_box = QtWidgets.QMessageBox(self.parent())
                        msg_box.setTextFormat(QtCore.Qt.RichText)
                        msg_box.setWindowTitle('ERROR')
                        msg_box.setText(message)
                        msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.YesToAll )
                        msg_box.setDefaultButton(QtWidgets.QMessageBox.Yes)
                        response = msg_box.exec()
                        if response == QtWidgets.QMessageBox.Yes:
                            continue
                        else:
                            ignore_message = True
                    image_list.pop(image_list.index(img))
            self.directory = directory
            self.directory_set.emit(self.directory)
            self.load_images(image_list)
        elif ".pnt" in os.path.splitext(peek)[1]: # point file
            if os.path.exists(peek):
                self.reset()
                self.load_points_from_file(peek)
                recentlyUsed.add_file(peek)
            else:
                message = peek + " not found"
                QtWidgets.QMessageBox.warning(self.parent(), 'Warning', message, QtWidgets.QMessageBox.Ok)
                return
        else: # images
            base_path = os.path.split(peek)[0]
            image_list = []
            for drop in drop_list:
                if type(drop) == QtCore.QUrl:
                    nf = drop.toLocalFile()
                else:
                    nf = drop
                image_list.append(nf)
            image_list = sorted(list(filter(f, image_list)))
            self.directory = base_path
            self.directory_set.emit(self.directory)
            self.load_images(image_list)

    def load_image(self, image):
        self.selection = []
        self.clear()
        self.current_image_name = image
        self.addPixmap(self.pixmaps[image])
        self.image_loaded.emit(self.directory, self.current_image_name)
        if self.edit_style == EditStyle.POINTS:
            self.display_points()
        elif self.edit_style == EditStyle.RECTS:
            self.display_measures()
        self.display_grid()

    def load_image_from_file(self, in_file_name):
        self.reset_undo_stack()
        file_name = in_file_name
        if type(file_name) == QtCore.QUrl:
            file_name = in_file_name.toLocalFile()
        
        image = os.path.basename(file_name)
        ecu_name, _, _ = self.get_ecu_info(image)
        self.ecu_dialog = ECUInputDialog(self)
        if not ecu_name: 
            self.ecu_dialog.run(file_name)
            if not self.ecu_dialog.last_exit: # cancel
                return
        self.ecu_dialog.close()

        if self.directory == '':
            self.directory = os.path.split(file_name)[0]
            self.directory_set.emit(self.directory)

        # check if the image is already in the zipfle
        img_in_pnts_file = False
        if ".pnts" in self.directory:
            with ZipFile(self.directory, 'r') as z:
                if image in z.namelist(): img_in_pnts_file = True

        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.selection = []
        self.clear()
        self.current_image_name = image
        if self.current_image_name not in self.points.keys():
            self.points[self.current_image_name] = {}
        if self.current_image_name not in self.pcb_info.keys():
            self.pcb_info[self.current_image_name] = {"x":"", "y":""}
        self.full_image_names[image] = in_file_name
        if img_in_pnts_file:
            # file is in zp file under the image name
            with ZipFile(self.directory, 'r') as z:
                img = Image.open(io.BytesIO(z.read(image)))
                channels = len(img.getbands())
                array = np.array(img)
                img.close()
        else:
            img = Image.open(file_name)
            channels = len(img.getbands())
            array = np.array(img)
            img.close()
        pixmap = pixmap_from_image_array(array, channels)
        self.addPixmap(pixmap)
        self.pixmaps[image] = pixmap
        self.image_loaded.emit(self.directory, self.current_image_name)
        if self.edit_style == EditStyle.POINTS:
            self.display_points()
        elif self.edit_style == EditStyle.RECTS:
            self.display_measures()
        self.display_grid()
        QtWidgets.QApplication.restoreOverrideCursor()

    def load_images(self, images):
        self.set_changed(True)
        for f in images:
            file_name = f
            if type(f) == QtCore.QUrl:
                file_name = f.toLocalFile()
            image_name = os.path.split(file_name)[1]
            if image_name not in self.points:
                self.points[image_name] = {}
        if len(images) > 0:
            for img in images:
                self.load_image_from_file(img)

    def apply_points(self, data):
        self.survey_id = data['metadata']['survey_id']
        self.class_attributes = attributes_from_dict(data["attributes"])
        for class_name, attributes in self.class_attributes.items():
            if attributes["Package"] not in completion.packages:
                completion.update(packages=[attributes["Package"]])
            if attributes["Manufacturer"] not in completion.manufacturers:
                completion.update(manufacturers=[attributes["Manufacturer"]])

        pcb_info = data["pcb_data"].copy()
        for k, v in pcb_info.items():
            self.pcb_info[k].update(v)
        self.colors = data['colors'].copy()
        self.data = data['data'].copy()
        self.ecus = data["ecus"].copy()
        self._categories = list(self.data.keys())
        self.current_image_name = data.get('current_image_name', None)
        self.current_category_name = data.get('current_category_name', None)
        self.current_class_name = data.get('current_class_name', None)

        self.points = {}
        if 'points' in data:
            self.points = data['points']

        self.class_visibility = data['visibility']
        image_scale = data['image_scale']
        for k, scale in image_scale.items():
            self.image_scale[k] = Scale.from_dict(scale)

        for image in self.points:
            for class_name in self.points[image]:
                for p in range(len(self.points[image][class_name])):
                    point = self.points[image][class_name][p]
                    if isinstance(point, dict):
                        self.points[image][class_name][p] = QtCore.QPointF(point['x'], point['y'])
                    else:
                        self.points[image][class_name][p] = QtCore.QPointF(point.x(), point.y())

        for class_name in data['colors']:
            self.colors[class_name] = QtGui.QColor(self.colors[class_name][0], self.colors[class_name][1], self.colors[class_name][2])

        for image in data["measures"]:
            self.measure_rects[image].clear()
            self.measure_rects_data[image].clear()
            for rect in data["measures"][image]:
                x = rect['x']
                y = rect['y']
                w = rect['w']
                h = rect['h']
                qrect = QtCore.QRectF(x, y, w, h)
                ppath = QtGui.QPainterPath()
                ppath.setFillRule(QtCore.Qt.WindingFill)
                ppath.addRect(qrect)
                path = QtWidgets.QGraphicsPathItem(ppath)
                self.measure_rects[image].append(path)
                self.measure_rects_data[image].append({"x":x, "y":y, "width":w, "height":h})

    def load_points_from_file(self, file_name):
        import os
        self.reset()
        _, suffix = os.path.splitext(file_name)
        is_pnt = suffix == ".pnt"
        is_pnts = suffix == ".pnts"
        if is_pnt:
            with open(file_name, 'r') as f:
                data = json.load(f)
            directory = os.path.split(file_name)[0]
            self.directory = directory
            self.full_image_names = {img:os.path.join(self.directory, img) for img in data["points"]}
        elif is_pnts:
            self.directory = file_name
            with ZipFile(file_name, "r") as z:
                basename = os.path.basename(file_name).replace(".pnts", ".pnt")
                data = json.loads(z.read(basename))
            self.full_image_names = {img:img for img in data["points"]}
        self.directory_set.emit(self.directory)
        self.apply_points(data)
        self.points_loaded.emit(file_name)
        self.fields_updated.emit()
        dirname = os.path.split(file_name)[0]
        for img in self.points.keys():
            if is_pnt:
                path = os.path.join(dirname, img)
            else:
                path = img
            self.load_image_from_file(path)
        recentlyUsed.add_file(file_name)
        self.reset_undo_stack()

    def reset_undo_stack(self):
        self.set_changed(False)
        self._undo_stack = []
        self._undo_pointer = -1
        self._redone = False

    def set_changed(self, changed):
        self._state_changed = changed
        if changed:
            self.update_undo_stack()

    def update_undo_stack(self):
        if self._redone or self._undone:
            self._undo_stack = self._undo_stack[self._undo_pointer:]
            self._undo_pointer = 0
            self._redone = False
            self._undone = False

        if self._undo_pointer < 0:
            self._undo_pointer = 0

        output = self.package_points()
        self._undo_stack.insert(0, json.dumps(output.copy()))
        self._undo_stack = list(dict.fromkeys(self._undo_stack)) # remove duplicates
        if len(self._undo_stack) == self._max_undo:
            self._undo_stack.pop(-1)

    def undo(self):
        if self._undo_pointer > 0:
            if self._undo_pointer >= len(self._undo_stack):
                return
        elif self._undo_pointer < 0:
            return
        last_edit = json.loads(self._undo_stack[self._undo_pointer])
        if not self._undone:
            self._undo_stack.insert(0, json.dumps(self.package_points()))
            self._undo_pointer += 1
        self._undo_pointer += 1
        self.apply_points(last_edit)
        # print("undo", len(self._undo_stack), self._undo_pointer, self._undone)
        self._undone = True

    def redo(self):
        up = self._undo_pointer
        nstack = len(self._undo_stack)
        if up < 1 or nstack == 0: 
            return
        if not self._redone:
            self._undo_pointer -= 1
        self._undo_pointer -= 1
        last_edit = json.loads(self._undo_stack[self._undo_pointer])
        self._redone = True
        self.apply_points(last_edit)
        # print("redo", len(self._undo_stack), self._undo_pointer)

    def get_changed(self):
        return self._state_changed

    def measure_area(self, rect):
        if self.current_image_name is None or self.edit_style != EditStyle.RECTS:
            return
        self.set_changed(True)

        image_scale = self.image_scale.get(self.current_image_name, Scale)

        topLeft = rect.topLeft()
        bottomRight = rect.bottomRight()
        width = bottomRight.x() - topLeft.x()
        height = bottomRight.y() - topLeft.y()
        scale = image_scale.scale
        unit = image_scale.unit

        active_color = QtGui.QColor(self.ui['point']['color'][0], self.ui['point']['color'][1], self.ui['point']['color'][2])
        active_brush = QtGui.QBrush(active_color, QtCore.Qt.SolidPattern)
        active_pen = QtGui.QPen(active_brush, 2)

        ppath = QtGui.QPainterPath()
        ppath.setFillRule(QtCore.Qt.WindingFill)
        ppath.addRect(rect)
        path = self.addPath(ppath, active_pen)

        topItem = self.addText("{:.1f} {}".format(width*scale, unit))
        topItem.setDefaultTextColor(QtGui.QColor(255, 255, 255))
        font = topItem.font()
        font.setBold(True)
        topItem.setFont(font)
        topItem.setPos(topLeft.x(), topLeft.y())

        leftItem = self.addText("{:.1f} {}".format(height*scale, unit))
        leftItem.setDefaultTextColor(QtGui.QColor(255, 255, 255))
        leftItem.setPos(topLeft.x(), topLeft.y() + leftItem.boundingRect().width() + topItem.boundingRect().height()*1.05)
        leftItem.setRotation(-90)
        font = leftItem.font()
        font.setBold(True)
        leftItem.setFont(font)
        self.measure_rects[self.current_image_name].append(path)
        self.measure_rects_data[self.current_image_name].append({"x":topLeft.x(), "y":topLeft.y(), "width":width, "height":height})

    def package_points(self):
        from io import StringIO
        import json
        self.set_changed(False)
        # count = 0
        image_scale = {}
        for k, scale in self.image_scale.items():
            image_scale[k] = dataclasses.asdict(scale)

        for class_name, attributes in self.class_attributes.items():
            if attributes["Package"] not in completion.packages:
                completion.update(packages=[attributes["Package"]])
            if attributes["Manufacturer"] not in completion.manufacturers:
                completion.update(manufacturers=[attributes["Manufacturer"]])

        package = {'data': {}, 'points': {}, 'colors': {}, 'pcb_data': self.pcb_info, "ecus": self.ecus,
                   'metadata': {'survey_id': self.survey_id}, 'attributes': self.class_attributes, 'ui': self.ui, 
                   'visibility': self.class_visibility, 'image_scale': image_scale, 'measures': {}, 
                   'current_image_name': self.current_image_name, 'current_class_name': self.current_class_name, 
                   'current_category_name': self.current_category_name}
        package['data'] = self.data.copy()
        for class_name in self.colors:
            r = self.colors[class_name].red()
            g = self.colors[class_name].green()
            b = self.colors[class_name].blue()
            package['colors'][class_name] = [r, g, b]
        for image in self.points:
            package['points'][image] = {}
            for class_name in self.points[image]:
                package['points'][image][class_name] = []
                src = self.points[image][class_name]
                dst = package['points'][image][class_name]
                for point in src:
                    p = {'x': point.x(), 'y': point.y()}
                    dst.append(p)
                    # count += 1
        for image in self.measure_rects_data:
            package['measures'][image] = []
            for mrect in self.measure_rects_data[image]:
                measure_data = {}
                measure_data['x'] = mrect["x"]
                measure_data['y'] = mrect["y"]
                measure_data['w'] = mrect["width"]
                measure_data['h'] = mrect["height"]
                package['measures'][image].append(measure_data)
        return package

    def relabel_selected_points(self):
        if self.current_class_name is not None:
            self.set_changed(True)
            # for class_name, point in self.selection:
            for _, point in self.selection:
                self.add_point(point)
            self.delete_selected_points()
            self.points_updated.emit()

    def rename_category(self, old_category, new_category):
        self.set_changed(True)
        if new_category in self.categories:
            raise ValueError("New name already exists {}".format(new_category))
        self.data[new_category] = self.data.pop(old_category)
        index = self._categories.index(old_category)
        self._categories.pop(index)
        self._categories.insert(index, new_category)
        self.current_category_name = new_category

    def rename_ecu(self, new_name, ecu_name, pcb_name, pos):
        self.set_changed(True)
        if ecu_name and pcb_name and pos: # switch top / bottom
            image = self.ecus[ecu_name][pcb_name][pos]
            if new_name in self.ecus[ecu_name][pcb_name].keys():
                self.ecus[ecu_name][pcb_name][pos] = self.ecus[ecu_name][pcb_name][new_name] 
            else:
                del self.ecus[ecu_name][pcb_name][pos]
            self.ecus[ecu_name][pcb_name][new_name] = image
        elif ecu_name and not pcb_name and not pos: # rename only ecu
            if new_name in self.ecus:
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Critical)
                msg.setText("Error")
                msg.setInformativeText('ECU Name Already Taken')
                msg.setWindowTitle("Error")
                msg.exec_()
                return 0
            self.ecus = {new_name if k == ecu_name else k:v for k, v in self.ecus.items()}
        elif ecu_name and pcb_name and not pos: # rename pcb
            pcbs = self.ecus[ecu_name]
            if new_name in pcbs:
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Critical)
                msg.setText("Error")
                msg.setInformativeText('PCB Name Already Taken')
                msg.setWindowTitle("Error")
                msg.exec_()
                return 0
            pcbs = {new_name if k == pcb_name else k:v for k, v in pcbs.items()}
            self.ecus[ecu_name] = pcbs
        return 1
        
    def move_class(self, classname, old_category, new_category, index=None):
        self.set_changed(True)
        if new_category not in self.categories or old_category not in self.categories:
            raise ValueError("Category not found {}".format(new_category))
        if classname not in self.classes:
            raise ValueError("New name not found {}".format(classname))

        classes = self.data[old_category]
        index  = classes.index(classname)
        to_move = classes.pop(index)
        self.data[old_category] = classes
        if index is None:
            self.data[new_category].append(to_move)
        else:
            self.data[new_category].insert(index, to_move)
        self.display_points()

    def rename_class(self, old_class, new_class):
        self.set_changed(True)
        if new_class in self.classes:
            raise ValueError("New name already exists {}".format(new_class))

        for k, v in self.data.items():
            if old_class in v:
                category = k
                break

        classes = self.data[category]
        index  = classes.index(old_class)
        classes.pop(index)
        if not new_class in self.classes:
            classes.insert(index, new_class)
        self.data[category] = classes
        self.colors[new_class] = self.colors.pop(old_class)
        self.class_visibility[new_class] = self.class_visibility[old_class]
        self.class_attributes[new_class] = self.class_attributes[old_class]
        del self.class_attributes[old_class]
        del self.class_visibility[old_class]
        
        for image in self.points:
            if old_class in self.points[image] and new_class in self.points[image]:
                self.points[image][new_class] += self.points[image].pop(old_class)
            elif old_class in self.points[image]:
                self.points[image][new_class] = self.points[image].pop(old_class)
        self.current_class_name = new_class
        self.display_points()

    def get_images_in_ecu(self, ecuname):
        names = []
        pcbs = self.ecus[ecuname]
        for pcb_names, positions in pcbs.items():
            for pos, image in positions.items():
                names.append(image)
        return names

    def remove_from_ecus(self, nodes):
        self.set_changed(True)
        n = len(nodes)
        if not n:
            return
        elif n == 1: # remove whole ecu:
            images = self.get_images_in_ecu(nodes[0])
            del self.ecus[nodes[0]]
            for image in images:
                del self.points[image]
                del self.pcb_info[image]
                del self.pixmaps[image]
        elif n == 2:
            images = list(self.ecus[nodes[0]][nodes[1]].values())
            for image in images:
                del self.points[image]
                del self.pcb_info[image]
                del self.pixmaps[image]
            del self.ecus[nodes[0]][nodes[1]]
        else:
            image = self.ecus[nodes[0]][nodes[1]][nodes[2]]
            del self.points[image]
            del self.pcb_info[image]
            del self.pixmaps[image]
            del self.ecus[nodes[0]][nodes[1]][nodes[2]]
        if self.current_image_name not in self.points:
            self.current_image_name = None
            self.clear()
        self.display_points()
        
    def remove_class(self, name):
        self.set_changed(True)
        category = self.get_category_from_class(name)
        for image in self.points:
            if name in self.points[image]:
                del self.points[image][name]
        classes = self.data[category]
        classes.pop(classes.index(name))
        self.data[category] = classes
        del self.class_attributes[name]
        self.current_class_name = None
        del self.class_visibility[name]
        self.display_points()

    def remove_category(self, name):
        self.set_changed(True)
        classes = self.data[name]
        for image in self.points:
            for class_name in classes:
                del self.class_attributes[class_name]
                del self.class_visibility[class_name]
                if class_name in self.points[image]:
                    del self.points[image][class_name]
        self.current_category_name = None
        self.current_class_name = None
        del self.data[name]
        self._categories.pop(self._categories.index(name))
        self.display_points()

    def reset(self):
        from collections import defaultdict
        from ddg.config import DDConfig

        self.config = DDConfig(DDConfig.DEFAULTFILE)
        self.points = {}
        self.class_visibility = {} # to be implemented
        self.colors = {}
        self.pcb_info = defaultdict(lambda:{"x":"", "y":""})
        self.survey_id = ""

        self._categories = sorted(self.config.categories.copy())
        self.class_attributes = {}
        self.data = {}
        for c in self._categories:
            self.data[c] = [] # classes
        self.previous_class_name = None
        self.next_class_name = None

        self.selection = []
        self.edit_style = EditStyle.POINTS
        self.ui = self.config.ui.copy()

        self.directory = ''
        self.current_image_name = None
        self.full_image_names = {}
        self.pixmaps = {}
        self.ecus = {}
        self.aliases = {}
        self.current_class_name = None
        self.current_category_name = None
        self.current_selection = None

        self.show_grid = True

        self.selected_pen = QtGui.QPen(QtGui.QBrush(QtCore.Qt.red, QtCore.Qt.SolidPattern), 1)

        self.image_scale = defaultdict(dict)
        self.measure_rects = defaultdict(list) # here we sore the QGraphicsPathItems
        self.measure_rects_data = defaultdict(list) # here we store the x, y, w, h of the measured rects. PathItems are destroyed when updating the view therefore we need to store that info seperately
        self.timer = None
        self.set_changed(False)
        self._undo_stack = []
        self._max_undo = 50
        self._undo_pointer = -1
        self._redone = False
        self._undone = False

    def save_pcb_info(self, x, y):
        self.set_changed(True)
        if self.current_image_name is not None:
            self.pcb_info[self.current_image_name].update({"x":x, "y":y})

    def save_points(self, file_name):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        if isinstance(file_name, (tuple, list)):
            file_name = file_name[0]
        _, ext = os.path.splitext(file_name)
        output = self.package_points()
        if ext == ".pnt":
            with open(file_name, 'w') as f:
                json.dump(output, f)
        elif ext == ".pnts":
            basename = os.path.basename(file_name)
            pntname = basename.replace(".pnts", ".pnt")
            dirname = os.path.dirname(file_name)
            with ZipFile(file_name, "w") as z:
                z.writestr(pntname, json.dumps(output))
                for img, px in self.pixmaps.items():
                    _, ext = os.path.splitext(img)
                    savename = os.path.join(dirname, str(hash(img)) + ext)
                    image = Image.fromqpixmap(px)
                    image.save(savename)
                    z.write(savename, img)
                    os.remove(savename)
            self.directory = file_name
            self.directory_set.emit(self.directory)
        completion.write(AutoCompleteFile.DEFAULTFILE)
        self.points_saved.emit(file_name)
        self.set_changed(False)
        QtWidgets.QApplication.restoreOverrideCursor()
        return True

    def select_points(self, rect):
        self.selection = []
        if self.edit_style == EditStyle.POINTS:
            self.display_points()
            current = self.points[self.current_image_name]
            display_radius = self.ui['point']['radius']
            for class_name in current:
                for point in current[class_name]:
                    if rect.contains(point):
                        offset = ((display_radius + 6) // 2)
                        self.addEllipse(QtCore.QRectF(point.x() - offset, point.y() - offset, display_radius + 6, display_radius + 6), self.selected_pen)
                        self.selection.append((class_name, point))
        elif self.edit_style == EditStyle.RECTS:
            color = QtGui.QColor(223, 23, 23)
            brush = QtGui.QBrush(color, QtCore.Qt.SolidPattern)
            pen = QtGui.QPen(brush, 4)
            for mrect in self.measure_rects[self.current_image_name]:
                if mrect.path().intersects(rect):
                    self.removeItem(mrect)
                    path = QtGui.QPainterPath()
                    path.setFillRule(QtCore.Qt.WindingFill)
                    path.addRect(mrect.boundingRect())
                    self.addPath(path, pen)
                    self.selection.append(mrect)

    def set_current_class(self, class_name):
        if class_name in self.classes:
            self.current_class_name = class_name
            category = self.get_category_from_class(class_name)
            if category: self.set_current_category(category)
        else:
            self.current_class_name = None
        self.display_points()

    def set_current_category(self, category):
        self.current_category_name = category

    def set_edit_style(self, edit_style):
        self.edit_style = edit_style
        if self.edit_style == EditStyle.POINTS:
            self.clear_measures()
            self.display_points()
        elif self.edit_style == EditStyle.RECTS:
            self.clear_points()
            self.display_measures()

    def set_grid_color(self, color):
        self.set_changed(True)
        self.ui['grid']['color'] = [color.red(), color.green(), color.blue()]
        self.display_grid()

    def set_grid_size(self, size):
        self.set_changed(True)
        self.ui['grid']['size'] = max(size, 10)
        self.display_grid()

    def set_point_color(self, color):
        self.set_changed(True)
        self.ui['point']['color'] = [color.red(), color.green(), color.blue()]
        self.display_points()

    def set_point_radius(self, radius):
        self.set_changed(True)
        self.ui['point']['radius'] = radius
        self.display_points()

    def set_scale(self, mm, rect):
        self.set_changed(True)
        if self.current_image_name is None:
            return
        scale = int(mm)/int(rect.width())
        topLeft = rect.topLeft()
        if self.current_image_name not in self.image_scale.keys():
            self.image_scale[self.current_image_name] = Scale()
        self.image_scale[self.current_image_name].scale = scale
        self.image_scale[self.current_image_name].unit = "mm"
        self.image_scale[self.current_image_name].top = topLeft.y()*scale
        self.image_scale[self.current_image_name].left = topLeft.x()*scale
        self.display_measures()

    def toggle_grid(self, display):
        if display:
            self.show_grid = True
            self.display_grid()
        else:
            self.show_grid = False
            self.clear_grid()

    def toggle_points(self, display):
        if display:
            self.display_points()
            self.selection = []
        else:
            self.clear_points()
            
    def set_component_attribute(self, attribute, value):
        self.set_changed(True)
        if self.current_class_name is not None:
            self.class_attributes[self.current_class_name][attribute] = value

    def set_ecu_info(self, ecu_name, pcb_name, position, image):
        self.set_changed(True)
        if not ecu_name in self.ecus:
            self.ecus[ecu_name] = {}
        if not pcb_name in self.ecus[ecu_name]:
            self.ecus[ecu_name][pcb_name] = {}
        self.ecus[ecu_name][pcb_name][position] = image

    def get_ecu_info(self, image_name):
        for ecu_name, pcbs in self.ecus.items():
            for pcb_name, positions in pcbs.items():
                for pos, image in positions.items():
                    if image_name == image:
                        return ecu_name, pcb_name, pos
        return None, None, None
