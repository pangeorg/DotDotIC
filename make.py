#!/env python
import os
from glob import glob
import sys
import shutil

USE_SPEC = True
ONLY_UI = False

NAME = "DotDotIC"
INSTALLER = "pyinstaller"
PROG = "main.py"
SPEC = "DotDotIC.spec"
ARGS = ["clean", "windowed"]
EXCLUDES = ["pandas", "scipy", "matplotlib", "xlwings", "beautifulsoup4", "sklearn", "tornado", 
            "hook", "setuptools", "site", "tensorflow", "flask", "cx_freeze", "flake8", "hdf5", 
            "h5py", "ipython", "ipython", "jupyter", "selenium", "requests", "pyinstaller", "tkinter", 'pyqtdeploy']
DATAS = ["./ddg/ui/*.ui"]

ONEFILE = True
NOUPX = True

for f in glob(".\\ddg\\ui\\*.ui"):
    os.system("pyuic5 {} -o {}".format(f, f.replace(".ui", "_ui.py")))

args = sys.argv[1:]    

if not ONLY_UI:
    if not USE_SPEC:

        argstr = " " + " ".join(["--{} ".format(a) for a in ARGS])
        argstr += " ".join(["--exclude-module " + m for m in EXCLUDES]) + " "
        # argstr += " ".join(["--add-data '{:}:.'".format(d) for d in DATAS])
        argstr += " --name=" + NAME

        call = INSTALLER + " " + PROG + argstr
        if ONEFILE:
            call += " --onefile"
        else:
            call += " --onedir"
        if NOUPX:
            call += " --noupx"
            
    else:
        call = "pyinstaller " + SPEC + " --onefile --noupx"
    os.system(call)

if "dev" in args:
    shutil.move("dist/DotDotIC.exe", "dist/DotDotIC_dev.exe")
elif "release" in args:
    shutil.move("dist/DotDotIC.exe", "dist/DotDotIC_release.exe")