import os
import json
from zipfile import ZipFile
from PIL import Image
from PyQt5 import QtCore, QtGui, QtWidgets
import glob

__all__ = ["FileManager"]

def pixmap_from_image_array(array, channels):
    import numpy as np
    arr = np.arr(arr[1:-1, 1:-1, ...]) # necessary bugfix for some images. Qt cannot add the pixmap if this line is removed
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

class FileManager:
    FILTYPE_PNT = 1
    FILTYPE_PNTS = 2
    _FILETYPE_SUFFIX = {"pnt":FileManager.FILTYPE_PNT, "pnts":FileManager.FILTYPE_PNTS}
    directory_set = QtCore.pyqtSignal(str)
    image_loaded = QtCore.pyqtSignal(str, str)
    points_loaded = QtCore.pyqtSignal(str)
    points_saved = QtCore.pyqtSignal(str)

    def __init__(self, filename=None):
        self._filename = filename
        self._filetype = None
        self._directory = None

    @property
    def filetype(self):
        return self._filetype
    
    @filetype.setter
    def filetype(self, filetype):
        if filetype not in FileManager._FILETYPE_SUFFIX.values():
            raise ValueError("Filetype not understood " + filetype)
        self._filetype = filetype

    @property
    def directory(self):
        return self._directory
    
    @directory.setter
    def directory(self, directory):
        self._directory = directory
        self.directory_set.emit(self._directory)

    def load_file(self, filename):
        suffix = filename.split(".")[-1]
        filetype = FileManager._FILETYPE_SUFFIX.get(suffix, None)
        if not filetype:
            return False
        self._filename = filename
        if filetype == FileManager.FILTYPE_PNT:
            self._file = FilePNT(filename)
            self._directory = os.path.dirname(self._filename)
            return self._file.load_file()
        elif filetype == FileManager.FILTYPE_PNT:
            self._file = FilePNTS(filename)
            self._directory = self._filename
            return self._file.load_file()
        else:
            return False

    def load(self, droplist):
        peek = droplist[0]
        if not isinstance(peek, str):
            peek = peek.toLocalFile()
        if os.path.isdir(peek):
            if self.directory is None:
                self._directory = peek
                files = glob.glob(os.path.join(self.directory, '*'))
                image_format = [".jpg", ".jpeg", ".png", ".tif"]
                f = (lambda x: os.path.splitext(x)[1].lower() in image_format)
                image_list = list(filter(f, files))
                image_list = sorted(image_list)
                self.load_images(image_list)

    def load_image(self, filename):
        pixmap = self._file.load_image(filename)
        if pixmap:
            self.directory = self._file.directory
            self.image_loaded.emit(self.directory, filename)
        QtWidgets.QApplication.restoreOverrideCursor()
        return pixmap

    def load_images(self, images):
        pass

    @property
    def directory(self):
        return self._file.directory

    @property
    def filename(self):
        return self._file.filename

class FilePNT:
    def __init__(self, filename=None):
        self.filename = filename
        self.directory = None

    def load_file(self, filename=None):
        if not filename:
            filename = self.filename
        if not filename:
            return None

        with open(filename, 'r') as f
            data = json.load(f)
        points = data['points']
        self.directory = os.path.split(filename)[0]
        img = None
        if points.keys():
            path = os.path.join(self.directory, list(points.keys())[0])
            img = self.load_image(path)
        return data, img

    def _load_image_data(self, filename=None):
        Image.MAX_IMAGE_PIXELS = 1000000000
        img = Image.open(file_name)
        channels = len(img.getbands())
        img.close()
        return pixmap_from_image_array(array, channels)

    def load_image(self, filename=None):
        if self.directory == '':
            self.directory = os.path.split(filename)[0]
        if self.directory == os.path.split(filename)[0]:
            return self._load_image_data(filename)


class FilePNTS:
    def __init__(self, filename=None):
        self.filename = filename
        self.directory = None

    def load_file(self, filename=None):
        data, img = None, None
        if not filename:
            filename = self.filename
        else:
            self.filename = filename
        if not filename:
            return data, img
        with ZipFile(self.filename, 'r') as z:
            basename = os.path.basename(self.filename).replace(".pnts", ".pnt")
            data = json.loads(z.read(basename))
        points = data['points']
        self.directory = filename
        img = None
        if points.keys():
            path = list(points.keys())[0]
            img = self.load_image(path)
        return data, img

    def _load_image_data(self, imagename=None):
        from io import BytesIO
        import numpy as np
        with ZipFile(self.filename, 'r') as z:
            img = Image.open(BytesIO(z.read(imagename)))
            channels = len(img.getbands())
            array = np.array(img)
            img.close()
        return pixmap_from_image_array(array, channels)

    def load_image(self, filename):
        Image.MAX_IMAGE_PIXELS = 1000000000
        if self.directory == '':
            self.directory = self.filename
        return self._load_image_data(filename)