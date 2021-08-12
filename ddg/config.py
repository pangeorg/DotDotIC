
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

    DEFAULT_MANUFACTURERS = ["Ablic Inc.", "adesto Technologies", "Advanced Monolithic Systems Inc.", "Advanced Power Electronics Corp.", "ADVICS Manufacturing Ohio, Inc.", "Allegro MicroSystems, LLC",
                            "Alltop Technology", "Allwinner Technology Co., Ltd.", "Alpha & Omega Semiconductor", "ALPINE",
                            "Alps Electric Co.", "Altera Corporation", "Ambarella Inc.", "AMIC Technology Corporation",
                            "Amotech corp.", "Amphenol", "AMS AG", "AMtek SEMICONDUCTORS CO., LTD.", "Anadigics",
                            "Analog Devices, Inc", "ANPEC", "Antenova Limited", "Apple", "Aptina Imaging", "Aptiv", "Arcotronics", "Arisu",
                            "Asahi Kasei Microdevices Corporation", "Ate",
                            "Atmel Corporation", "AU Optronics", "Aupo", "Avago Technologies", "AVX Corporation", "Beijing Jingyuxing Technology Co., Ltd. (Shenzhen)", "Beijing zxsf Polytron Technologies Inc", 
                            "Bennic Components", "BI Technologies", "Bourns, Inc.",
                            "Brightking", "Broadcom Corporation", "C&K Components, LLC.", "Calsonic Kansei", "Capxon Group",
                            "CEC(Shenzhen Zhenhua XinYun Elec)", "ChenYang Technologies GmbH & Co. KG", "Chipsvision Micro", "Chrontel, Inc.", "Cirrus Logic", "Cissoid",
                            "Citizen Electronics Co., Ltd.", "Clarion", "CMI", "CMO", "Coilcraft", "Comchip Technology",
                            "Continental AG", "Cooper Bussmann", "Cooper Industries", "Cornel Dubilier", "CSR plc", "CXW", "Cypress Semiconductor Corporation",
                            "DECO", "Delphi Corporation", "Delta Electronics, Inc.", "Demeter", "Denso Corporation", "Dexerials", "Dialog Semiconductor", "DIGISOUND Electronic GmbH",
                            "Diodes Incorporated", "Diotec Semiconductor", "Dongguan e-Tec Electrics Co.,Ltd", "EastWho Co.Ltd.", "Eaton Corporation", "ECS Inc. International",
                            "Eite Semiconductor Memory Technology Inc. (ESMT)", "Electronic Relays India", "Elmos Semiconductor AG", "Elna Co., Ltd.", "EM Microelectronic-Marin SA", "Eon Silicon Solution Inc.",
                            "Epcos", "eRide / ST", "ERNI", "ESMT", "ESSYS", "ESTec co., ltd", "Ethertronics", "Etron Technology Inc.", "Everlight Electronics Co., Ltd", 
                            "Everspin Technologies", "Explore Microelectronics Inc",
                            "F&T", "Fagor Electronica", "Fairchild Semiconductor", "Faratronic", "FCI", "FDK Corporation", "Fenghua (HK) Electronics Ltd.", "FerroCore", "Fidelix Co,. Ltd.",
                            "Formosa Microsemi Co., Ltd.", "Fortemedia, Inc.", "Fortior Tech", "Foster Electric Company, Limited", "Fox Electronics", "Freescale Semiconductor", "FTCAP GmbH", "Fuji Electric",
                            "Fujitsu", "Fujitsu TEN", "Furuno Electric", "Future Technology Devices International Ltd.", "FUZETEC Technology Co., Ltd.", "G.CARTIER", "GainSpan", 
                            "GCI Technologies", "Gemalto", "Gemcon", "Gentex Corporation", "GEO Semiconductor Inc.",
                            "GigaDevice", "Glovane Co,.Ltd.", "GMCC Electronic Technology Wuxi Ltd", "Good-Ark Semiconductor", "Greenliant Systems, Ltd.", "Gruner", "GS Electronics",
                            "Guangdong Kexin Industrial Co.,Ltd", "Halcyon MicroElectronics, Inc.", "HALO Electronics Inc.", "Hamamatsu", "Hangzhou Silan Microelectronics Co., Ltd",
                            "Hangzhou ZhongKe Microelectronics CO.,Ltd", "Harman International Industries", "Harman International Industries / Analog Devices", "Harmony Electronics Corp.",
                            "Hefei Jingweite Electronics Co., Ltd.", "Hella", "HG Huiguang", "Hi - Tech Resistors Pvt . Ltd", "Himax Technologies, Inc.", "HINODE Electric Co., Ltd.",
                            "Hirose", "Hirschmann", "HiSilicon Technologies Co., Ltd.", "Hitachi, Ltd", "HITECH RESISTORS PVT. LTD.", "Holtek Semiconductor Inc.",
                            "HolyStone International", "Hong kong Crystal", "HONGFA", "Hosiden Corporation", "HTC Korea TAEJIN Technology Co", "Huakai", "Huawei Technologies", "HuaXinAn Electronics",
                            "HuiZhou Shi SongLong LiShang Electronics CO.,LTD", "HVR Advanced Power Components", "HY ELECTRONIC (CAYMAN) LIMITED", "Hyundai Autron Co. Ltd", "Hyundai Mobis",
                            "iC-Haus GmbH", "IC-Logic Microchips", "iiTronic International", "IK Semicon Co., Ltd", "Infineon Technologies AG", "INOVA Semiconductors GmbH", "INPAQ Technology Co., Ltd.", "Integrated Device Technology",
                            "Integrated Silicon Solution Inc.", "Intel Corporation", "International Rectifier", "Intersil Corporation", "iRC-Electronic GmbH", "Isabellenhuette", "Isahaya",
                            "Iskra", "ITE", "IXYS Corporation", "Jackec", "Jackon Capacitor Electronics Co.,Ltd.", "Jamicon", "JAY NAY Co., Ltd.", "Jeju Semiconductor",
                            "Jem-Techno", "Jiangsu Changjiang Electronics Technology Co.,Ltd.", "Jiangsu Jiejie Microelectronics Co., Ltd.", "Jinyoung Electro-Mechanics Co., Ltd", "JMicron",
                            "Johanson Dielectrics, Inc.", "Johnson Controls / JCAE", "JST", "Kaschke Components GmbH",
                            "KDS Daishinku Corporation", "KEC", "Keihin Corporation", "Kemet Corporation", "Kepler", "Kingtronics International Company",
                            "Kionix, Inc.", "Kioxia", "Klixon", "KMG", "Knowles Electronics, LLC.", "KOA Speer Electronics, Inc.", "Kodenshi AUK Group", "KONY",
                            "KORCHIP", "Korea Electronics Technology Co., Ltd", "Koshin", "KRELL", "KSR International Co.", "Kuan Kun Electronic Enterprise Co., Ltd.", "Kyocera International, Inc.", "LAIRD", "Lapis Semiconductor Co., Ltd..",
                            "Lattice Semiconductor Corporation", "Leaguer", "Lelon Electronics Corp", "LEM", "Leshan Radio Company Ltd.", "Lesswire GmbH", "LG Display Co., Ltd.", "LG Group", "LG PHILIPS LCD",
                            "LGInnotek", "LH.NOVA", "Linear Technology", "Lite-On Semiconductor Corp", "Littelfuse", "LK/Kostal", "Logo/Supplier Unknown", "LSHC", "Lucent Technologies", "Macroblock, Inc.",
                            "Macronix International Co., Ltd.", "Maestro Wireless Solutions Limited", "Magellan", "Magneti Marelli", "Mando Corporation", "Marquardt-Gruppe", "Marvell Technology Group", "Master Instrument Corporation (MIC)",
                            "Matsushita Panasonic", "Maxim Integrated Products", "Maxlinear Inc.", "Measurement Specialties, Inc.", "MediaTek ARM", "Megamos", "Melexis",
                            "Memsic, Inc", "Meritek", "MIC Electronic Co., Ltd.", "Micrel Semiconductor", "Micro Commercial Components Corp.", "Micro Crystal", "Microchip Technology", "Micron Technology",
                            "Micronas", "Microsemi", "Minebea Co., Ltd.", "Mitsuba Corporation", "Mitsubishi Electric Corporation", "Mitsumi", "Mobileye",
                            "Mobileye and STMicroelectronics", "Mobis", "Molex", "Monolithic Power Systems", "Mornsun Guangzhou Science & Technology Co.,Ltd", "Mosel Vitelic Corporation", "Motorola Inc.",
                            "MTA S.p.A.", "Murata Manufacturing", "N/A", "NAIS", "Nanya Technology Corp.", "National Semiconductor", "NDK Nihon Dempa Kogyo Co., Ltd.", "NEC Corporation",
                            "NEC TOKIN Corporation", "Neonode", "Nesscap Co., Ltd.", "NetLogic Microsystems", "New Japan Radio Co., Ltd.", "Nexem", "Nexperia",
                            "nFore Technology Co., Ltd.", "Nicera Nippon Ceramic Co., Ltd.", "Nichicon Corporation", "Nidec Elesys Americas Corporation", "Nihon Inter Electronics Corporation",
                            "Nikko Electric Industry Co., Ltd", "Nippon Audiotronix Pvt. Ltd.", "Nippon Chemi-Con", "Novatek Microelectronics Corp.", "NSK Ltd.",
                            "NTN-SNR", "Nuvoton Technology Corporation", "NVIDIA Corporation", "NXP Semiconductors", "O2Micro International Limited.",
                            "OEM logo", "Okaya Electric Industries Co., Ltd.", "Oki Electric Industry", "OmniVision Technologies, Inc.", "Omron",
                            "ON Semiconductor", "OSRAM Opto Semiconductors GmbH", "Otter Controls LTD", "Pacific Engineering Corporation", "Panasonic Corporation",
                            "PANJIT International Inc", "Parrot", "Payton Planar Magnetics Ltd.", "Peiker acustic GmbH & Co.", "Pektron",
                            "Peregrine Semiconductor Corp.", "Pericom Semiconductor Corporation", "Philips Semiconductors", "Pierburg Pump Technology", "Pioneer Corporation", "PMC-Sierra",
                            "PnpNetwork Technologies Inc", "Polytronics Technology Corporation", "Power Integrations", "Premo S.L.", "Princeton Technology Corporation", "Pulse Electronics Power BU", "Pulse Technology Group", "Qorvo",
                            "Qualcomm", "Quectel", "Ramtron International Corporation", "Realtek Semiconductor Corp", "Rectron Semiconductor", "Renesas Electronics Corporation", "RF Micro Devices Inc.", "RF Monolithics",
                            "Rhythm Co., Ltd.", "Richtek Technology Corporation", "Ricoh Company, Ltd.", "Ricoh Electronic Devices Co., Ltd.", "RN2 Technologies", "Robert Bosch GmbH",
                            "Rohm Semiconductor", "Rubycon Corporation", "SAE Power", "SAGAMI ELEC CO., LTD.", "Samsung",
                            "Samwha Capacitor Group", "Samyoung Electronics Co Ltd", "Sancon", "SanDisk Corporation", "Sanken Electric Co., Ltd.", "Sanyanke Technology Co., Ltd.",
                            "Sanyo Semiconductor Co., Ltd.", "Schott", "Seeing Machines", "SEFUSE", "Segma Power Semiconductor Co., Ltd.", "Seiko Epson", "Seiko Instruments Inc.",
                            "SEIKO NPC CORPORATION", "Semtech", "Semtech Corporation", "Sensata Technologies, Inc.", "Sensirion", "Sensirion Semiconductor",
                            "Sensitron Semiconductor", "SG Micro Corp", "SGX Sensortech", "Shanghai Yongming Electronic Co. Ltd", "Shantou Hongzhi enterprise Co., LTD", "Sharp Corporation", "Shenzhen Wangxing Electronics Co., Ltd",
                            "Shindengen Electric Manufacturing", "Shinmei Electric co., ltd.", "Shizuki Electric Co.,Inc.", "Siemens", "Sierra Wireless", "SiGe Semiconductor", "SII Semiconductor Corporation",
                            "Silicon Labs", "Silicon Microstructures, Inc.", "Silicon Motion Technology Corp", "Silicon Sensing", "Silicon Storage Technology, Inc.", "Silicon Works",
                            "Siliconix", "Silvan Chip Electronics Inc", "Sipex", "Sirenza Microdevices", "SiRF Technology, Inc.", "SiTime",
                            "SIWARD Crystal Technology Co., Ltd.", "SJK-Shenzhen Crystal Technology Industrial Co.,Ltd", "SK Hynix Inc.", "Skyworks Solutions, Inc", "SMSC", "SOC Corporation", "Socionext",
                            "Sonceboz", "Song Chuan", "Sony Corporation", "Spansion", "Standard Microsystems Corporation", "Stanley Electric Co., Ltd.", "Starhope (SP Semi)", "STMicroelectronics",
                            "SUMIDA Corporation", "Sumitomo", "SUN Electronic Industries Corporation", "Surge Components Inc.", "Susumu", "Suzuki",
                            "Synaptics Incorporated", "Tai", "Taicon", "TAI-SAW Technology Co., Ltd.", "Taitien Electronics Co.,Ltd", "Taiwan Semiconductor", "Taiyo Yuden Co., Ltd.",
                            "Takamisawa", "Tamagawa seiki Co.,Ltd.", "Tamul", "Tamura Corporation", "TDK Corporation", "TE Connectivity Ltd.", "TEC Electronics",
                            "Tecate Group", "Techwell Inc.", "Telechips Inc.", "Telit Communications PLC", "Temic Semiconductors", "Texas Instruments",
                            "THine Electronics, Inc.", "Thinki Semiconductor Co.,Ltd.", "Timken", "Tocos", "TOHO", "Tokai Rika", "Toko, Inc.",
                            "TOKYO PARTS INDUSTRIAL", "Toneluck Co.,Ltd", "Torex Semiconductor Ltd.", "Toshiba Corporation", "Trimble Navigation", "Tripod",
                            "TriQuint Semiconductor", "TXC Corporation", "TY Taiwan Semiconductor Co., Ltd", "U-blox Holding AG", "UD Info Corp.", "UMW (Youtai Semiconductor Co., Ltd.)",
                            "Unicore Communication Inc.", "Unique Sound Co., Ltd.", "Unisonic Technologies", "United Automotive Electronic Systems Co., Ltd", "United Chemi-Con", "United Monolithic Semiconductors",
                            "Universal Scientific Industrial (Shanghai) Co., Ltd.", "Vacuumschmelze GmbH & Co", "Valens", "Valeo", "VINATech", "Vincotech GmbH",
                            "Vishay", "VOGT electronic AG", "Vogt Elektronik", "VTI technologies", "Weitron Technology Co., Ltd.", "Wima",
                            "Winbond", "WINSOK Semiconductor", "Wolfson Microelectronics", "Won-Top Electronics Co. Ltd", "World Products Inc.", "Würth Elektronik GmbH & Co.", "XFMRS Inc.",
                            "Xiamen Faratronic Co., Ltd.", "Xiamen Hongfa Electroacoustic Co., Ltd.", "Xilinx Automotive solutions", "Xilinx Inc.", "X-Powers Technology Co., Ltd.", "Xradiotech",
                            "Yamaha Corporation", "Yangxing Technology", "Yangzhou Yangjie Electronic Technology Co., Ltd.", "Yantel Corporation", "Yitoa Micro Technology Corporation", "Yixing Honsing Electronics Co., Ltd.",
                            "Zeeman Fuses MFG. (Xiamen) Corp.", "Zentel Electronics Corp.", "Zetex Semiconductors plc", "Zhejiang HKE Co., Ltd.", "Zhuhai Gree Xinyuan Eletronic Co., Ltd.", "Zhuhai Leaguer Capacitor Co. Ltd",
                            "ZMD The Analog Mixed Signal Company"]

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
        def update_from_default(attr, default):
            a = set(attr)
            a = dict.fromkeys(a)
            a.update(dict.fromkeys(default))
            return list(a) # update from default

        config = configparser.ConfigParser()
        config.read(filename)
        for a in AutoCompleteFile._ATTR:
            al = a.lower()
            try:
                value = list(set([c.strip() for _, c in config[a].items() if len(c.strip())]))
                default = getattr(AutoCompleteFile, "DEFAULT_" + a.upper())
                value = update_from_default(value, default)
                setattr(self, al, value)
            except:
                setattr(self, al, getattr(AutoCompleteFile, "DEFAULT_" + a.upper()).copy())

        self.packages.sort(key=lambda x: x.lower())
        self.manufacturers.sort(key=lambda x: x.lower())
        self.metriks.sort(key=lambda x: x.lower())

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


