
import configparser
import os

HOME = os.path.expanduser("~") + "\\AppData\\Local\\DotDotIC\\"
if not os.path.exists(HOME):
    os.makedirs(HOME)

class RecentlyUsed:
    DEFAULTFILE = HOME + "recently_used.ini" 
    def __init__(self, filename=None):
        if filename is None:
            filename = RecentlyUsed.DEFAULTFILE
        self.filename = filename
        self.files = []
        self.load()

    def add_file(self, filename):
        if filename in self.files:
            index = self.files.index(filename)
            self.files.pop(index)
        self.files.insert(0, filename)
        self.write()


    def load(self):
        import os
        if not os.path.exists(self.filename):
            if not os.path.exists(os.path.dirname(self.filename)):
                os.makedirs(os.path.dirname(self.filename))
            self.write()

        with open(self.filename, "r") as f:
            files = f.readlines()
        files = [f.strip().replace("\n","") for f in files]
        files = list(filter(lambda x: x!="", files))
        if len(files) > 10:
            files = files[:10]
        self.files  = files

    def write(self):
        files = ["\n" + f for f in self.files]
        if len(files) > 10:
            files = files[:10]
        with open(self.filename, "w") as f:
            f.writelines(files)

class DDConfig:
    DEFAULTFILE = HOME + "config.ini" 
    DEFAULT_UI = {'grid': {'size': 200, 'color': [255, 255, 255]}, 'point': {'radius': 25, 'color': [255, 255, 0]}}
    DEFAULT_CATEGORIES = ["Resistor", "Capacitor", "Crystal", "Diode", "Inductor", "Integrated Circuit", "Transistor", "Discrete <= 3 Pins", "Discrete > 3 Pins", "Connectors"]
    DEFAULT_AUTOSAVE_TIMEOUT = 5. # min

    def __init__(self, filename=None):
        if not os.path.exists(DDConfig.DEFAULTFILE):
            if not os.path.exists(os.path.dirname(DDConfig.DEFAULTFILE)):
                os.makedirs(os.path.dirname(DDConfig.DEFAULTFILE))
            DDConfig.write_default()

        if filename is None:
            self.load(DDConfig.DEFAULTFILE)
        else:
            self.load(filename)

    @staticmethod
    def write_default():
        config = configparser.ConfigParser()
        config["Categories"] = {"Category{:02d}".format(i):c for i,c in enumerate(DDConfig.DEFAULT_CATEGORIES)}
        config["grid"] = {}
        config["point"] = {}
        config["general"] = {}
        config["grid"]["size"] = str(DDConfig.DEFAULT_UI["grid"]["size"])
        config["grid"]["color"] = ",".join([str(i) for i in DDConfig.DEFAULT_UI["grid"]["color"]])
        config["point"]["radius"] = str(DDConfig.DEFAULT_UI["point"]["radius"])
        config["point"]["color"] = ",".join([str(i) for i in DDConfig.DEFAULT_UI["point"]["color"]])
        config["general"]["autosave"] = str(DDConfig.DEFAULT_AUTOSAVE_TIMEOUT) + " # minutes"
        with open(DDConfig.DEFAULTFILE, "w") as f:
            config.write(f)

    def write(self, filename):
        config = configparser.ConfigParser()
        config["Categories"] = {"Category{:02d}".format(i):c for i,c in enumerate(self.categories)}
        config["grid"] = {}
        config["point"] = {}
        config["general"] = {}
        config["grid"]["size"] = self.ui["grid"]["size"]
        config["grid"]["color"] = ",".join(self.ui["grid"]["color"])
        config["point"]["radius"] = self.ui["point"]["radius"]
        config["point"]["color"] = ",".join(self.ui["point"]["color"])
        config["general"]["autosave"] = self.autosave_timeout
        with open(filename, "w") as f:
            config.write(f)

    def load(self, filename):
        config = configparser.ConfigParser()
        config.read(filename)
        self.categories = [c.strip() for _, c in config["Categories"].items()]
        self.ui = {}
        self.ui["grid"] = {}
        self.ui["point"] = {}
        self.ui["grid"]["size"] = int(config["grid"]["size"])
        self.ui["grid"]["color"] = [int(i.strip()) for i in config["grid"]["color"].split(",")]
        self.ui["point"]["radius"] = int(config["point"]["radius"])
        self.ui["point"]["color"] = [int(i.strip()) for i in config["point"]["color"].split(",")]
        self.autosave_timeout = float(config["general"]["autosave"].split()[0])

class AutoCompleteFile:
    DEFAULTFILE = HOME + "completion.ini"
    DEFAULT_PACKAGES = ["THT", "SMD", "TO-247", "TO-220", "DO-247", "DO-220", "DPAK", "D²PAK", "H²PAK", "HU3PAK", "DirectFET2 L8", "BGAx", 
                        "BGA-292", "QFP-x", "QFP-100", "LQFP-x", "QFN-x",
                        "DFN-x", "TSSOP-20", "TSSOP-16", "TSSOP-14", "VSSOP-8", "SO-16", "SO-16 wide", 
                        "SO-16 narrow", "SO-14", "SO-8", "SO-5", "SO-4", "SOT-223", "SOT-223-4", "SOT-23", "SOT-23-5", 
                        "SOT-23-6", "SOT-323", "SOT-353",
                        "SOT-363", "SMC", "SMB", "SMA", "SOD-123", "SOD-323", "SOD-523", "SOD-923", "SOD-123FL", "SOD-323FL", "SOD-523FL", "SOD-923FL", 
                        "2520", "1812", "1806", "1210", "1206", "0805", "0603", "0402", "0201",]

    DEFAULT_MANUFACTURERS = ["Altera", "Amphenol", "Analog Devices", "Aptiv", "Avago", "Bourns", "Coilcraft", "Cornel Dubilier", "Diodes Incorporated", "Eaton", 
                            "Elna", "EPCOS", "ERNI", "Faratronic", "Fuji Electric", "Hirose", "Hirschmann", "Infineon", "Isabellenhütte", "JST", "KDS", "Kemet",
                            "Kyocera", "Lelon", "LEM", "Linear Technology", "Littelfuse", "Maxim Integrated", "Melexis", "Microchip", "molex", "Murata", "Nexperia", 
                            "Nichicon", "Nippon Chemi-Con", "NXP", "ON Semiconductor", "Panasonic", "Pulse", "Qualcomm", "Renesas",
                            "Rohm", "Rubycon", "Shindengen", "Shizuki", "Silicon Labs", "STMicroelectronics", "Sumida", "Sumitomo", "Susumu", "Taiwan Semiconductor", 
                            "Taiyo Yuden", "TDK", "TE Connectivity", "Texas Instruments", "United Chemi-Con", "Vishay", "Würth Electronics", "Xilinx"]

    DEFAULT_METRIKS = ["Commodity", "IC", "Passive", "Power", "Mechanical", "Opto", "Display", 
                        "Standard_IC", "Crystal", "Standard_analog", "uC", "Specialty", "Memory", 
                        "EM", "PCB", "Portfolio", "Calculation", ]

    DEFAULT_PLACEMENT = ["SMD small", "SMD large", "THT solder", "THT Pin-in-Paste", "Pressfit", "Part of Final Assy", "not evaluated"]
    _ATTR = ["Packages", "Manufacturers", "Metriks", "Placement"]


    def __init__(self, filename=None):
        if not os.path.exists(AutoCompleteFile.DEFAULTFILE):
            if not os.path.exists(os.path.dirname(AutoCompleteFile.DEFAULTFILE)):
                os.makedirs(os.path.dirname(AutoCompleteFile.DEFAULTFILE))
            AutoCompleteFile.write_default()

        if filename is None:
            self.load(AutoCompleteFile.DEFAULTFILE)
        else:
            self.load(filename)

    def load(self, filename):
        config = configparser.ConfigParser()
        config.read(filename)
        for a in AutoCompleteFile._ATTR:
            al = a.lower()
            try:
                setattr(self, al, list(set([c.strip() for _, c in config[a].items()])))
            except:
                setattr(self, al, getattr(AutoCompleteFile, "DEFAULT_" + a.upper()).copy())
        self.packages.sort()
        self.manufacturers.sort()
        self.metriks.sort()

    def update(self, filename=None, **kwargs):
        if filename is not None:
            config = configparser.ConfigParser()
            config.read(filename)
            for a in AutoCompleteFile._ATTR:
                l = [c.strip() for _, c in config[a].items()]
                ul = kwargs.get(a.lower(), [])
                if len(ul) > 0: l.extend(ul)
                setattr(self, a.lower(), list(set(l)))
            self.write(filename)
        else:
            for a in AutoCompleteFile._ATTR:
                al = a.lower()
                ul = kwargs.get(al, [])
                self_list = getattr(self, al)
                self_list.extend(ul)
                setattr(self, al, list(set(self_list)))
        self.packages.sort()
        self.manufacturers.sort()
        self.metriks.sort()

    def write(self, filename):
        config = configparser.ConfigParser()
        for a in AutoCompleteFile._ATTR:
            config[a] = {a + "{:03d}".format(i):c for i,c in enumerate(getattr(self, a.lower()))}
        with open(filename, "w") as f:
            config.write(f)

    @staticmethod
    def write_default():
        config = configparser.ConfigParser()
        for a in AutoCompleteFile._ATTR:
            config[a] = {a + "{:03d}".format(i):c for i,c in enumerate(getattr(AutoCompleteFile, "DEFAULT_" + a.upper()))}
        with open(AutoCompleteFile.DEFAULTFILE, "w") as f:
            config.write(f)


