from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import QTimer
import sys
import time
import csv
import os
import winsound
from libs import Track, Car
from SimRacingTools import getShiftRPM
from SimRacingTools.FuelSavingOptimiser import fuelSavingOptimiser, rollOut
from libs.IDDU import IDDUThread, IDDUItem
from functionalities.libs import importExport, importIBT, maths
from functionalities.RTDB import RTDB
import numpy as np


def decorator(fn):
    def wrapper(*args, **kwargs):
        fn_results = fn(*args, **kwargs)
        return fn_results

    return wrapper


class iDDUGUIThread(IDDUThread):

    def __init__(self, rate):
        IDDUThread.__init__(self, rate)

    def run(self):
        Gui()


class Stream(QtCore.QObject):
    newText = QtCore.pyqtSignal(str)

    def write(self, text):
        self.newText.emit(str(text))


class Gui(IDDUItem):

    @decorator
    def closeEvent(self, event):
        reply = QMessageBox.question(self.iDDU, 'Close iDDU?', "Are you sure to quit iDDU?", QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            print("Closing iDDU...")
            event.accept()
            sys.exit(self.exec_())
        else:
            event.ignore()

    def __init__(self):
        IDDUItem.__init__(self)
        import sys
        app = QtWidgets.QApplication(sys.argv)
        iDDU = QtWidgets.QWidget()
        iDDU.closeEvent = self.closeEvent
        if os.environ['COMPUTERNAME'] == 'MARC-SURFACE':
            iDDU.move(self.db.config['rGUI'][0], self.db.config['rGUI'][1])
        else:
            iDDU.move(0, 1080)
            # change console output to iDDU print window
            sys.stdout = Stream(newText=self.onUpdateText)
            sys.stderr = Stream(newText=self.onUpdateText)

        self.setupUi(iDDU)
        iDDU.show()

        # make QTimer
        iDDU.qTimer = QTimer()
        # set interval to 1 s
        iDDU.qTimer.setInterval(1000)  # 1000 ms = 1 s
        # connect timeout signal to signal handler
        iDDU.qTimer.timeout.connect(self.refreshGUI)
        # start timer
        iDDU.qTimer.start()

        self.getJoystickList()

        sys.exit(app.exec_())

    def setupUi(self, iDDU):
        self.iDDU = iDDU
        self.iDDU.setObjectName("iDDU")
        # self.iDDU.resize(798, 448)
        self.iDDU.setFixedSize(798, 448)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(self.db.dir + "/files/gui/iRacing_Icon.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        iDDU.setWindowIcon(icon)

        self.tabWidget = QtWidgets.QTabWidget(iDDU)
        self.tabWidget.setGeometry(QtCore.QRect(10, 10, 781, 431))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setMaximumSize(QtCore.QSize(781, 16777215))
        self.tabWidget.setObjectName("tabWidget")
        self.tabGeneral = QtWidgets.QWidget()
        self.tabGeneral.setObjectName("tabGeneral")
        self.groupBox_2 = QtWidgets.QGroupBox(self.tabGeneral)
        self.groupBox_2.setGeometry(QtCore.QRect(20, 350, 281, 51))
        self.groupBox_2.setObjectName("groupBox_2")
        self.pushButton_StartDDU = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_StartDDU.setGeometry(QtCore.QRect(40, 20, 75, 23))
        self.pushButton_StartDDU.setToolTip("")
        self.pushButton_StartDDU.setObjectName("pushButton_StartDDU")
        self.pushButton_StopDDU = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_StopDDU.setGeometry(QtCore.QRect(160, 20, 75, 23))
        self.pushButton_StopDDU.setObjectName("pushButton_StopDDU")
        self.groupBox_3 = QtWidgets.QGroupBox(self.tabGeneral)
        self.groupBox_3.setGeometry(QtCore.QRect(10, 10, 291, 191))
        self.groupBox_3.setObjectName("groupBox_3")
        self.spinBoxRaceLaps = QtWidgets.QSpinBox(self.groupBox_3)
        self.spinBoxRaceLaps.setGeometry(QtCore.QRect(140, 20, 101, 22))
        self.spinBoxRaceLaps.setMaximum(10000)
        self.spinBoxRaceLaps.setSingleStep(1)
        self.spinBoxRaceLaps.setObjectName("spinBoxRaceLaps")
        self.label_8 = QtWidgets.QLabel(self.groupBox_3)
        self.label_8.setGeometry(QtCore.QRect(20, 20, 81, 16))
        self.label_8.setObjectName("label_8")
        self.label_14 = QtWidgets.QLabel(self.groupBox_3)
        self.label_14.setGeometry(QtCore.QRect(20, 80, 101, 16))
        self.label_14.setObjectName("label_14")
        self.doubleSpinBox_P2PActivations = QtWidgets.QDoubleSpinBox(self.groupBox_3)
        self.doubleSpinBox_P2PActivations.setGeometry(QtCore.QRect(140, 110, 101, 22))
        self.doubleSpinBox_P2PActivations.setPrefix("")
        self.doubleSpinBox_P2PActivations.setSuffix("")
        self.doubleSpinBox_P2PActivations.setDecimals(0)
        self.doubleSpinBox_P2PActivations.setMaximum(1000.0)
        self.doubleSpinBox_P2PActivations.setSingleStep(1.0)
        self.doubleSpinBox_P2PActivations.setProperty("value", self.db.config['P2PActivationsGUI'])
        self.doubleSpinBox_P2PActivations.setObjectName("doubleSpinBox_P2PActivations")
        self.doubleSpinBox_DRSActivations = QtWidgets.QDoubleSpinBox(self.groupBox_3)
        self.doubleSpinBox_DRSActivations.setGeometry(QtCore.QRect(140, 80, 101, 22))
        self.doubleSpinBox_DRSActivations.setPrefix("")
        self.doubleSpinBox_DRSActivations.setSuffix("")
        self.doubleSpinBox_DRSActivations.setDecimals(0)
        self.doubleSpinBox_DRSActivations.setMaximum(1000.0)
        self.doubleSpinBox_DRSActivations.setSingleStep(1.0)
        self.doubleSpinBox_DRSActivations.setProperty("value", self.db.config['DRSActivationsGUI'])
        self.doubleSpinBox_DRSActivations.setObjectName("doubleSpinBox_DRSActivations")
        self.checkBox_MapHighlight = QtWidgets.QCheckBox(self.groupBox_3)
        self.checkBox_MapHighlight.setEnabled(True)
        self.checkBox_MapHighlight.setGeometry(QtCore.QRect(20, 150, 251, 17))
        self.checkBox_MapHighlight.setChecked(self.db.config['MapHighlight'])
        self.checkBox_MapHighlight.setObjectName("checkBox_MapHighlight")
        self.label_15 = QtWidgets.QLabel(self.groupBox_3)
        self.label_15.setGeometry(QtCore.QRect(20, 110, 101, 16))
        self.label_15.setObjectName("label_15")
        self.label_NStintLaps = QtWidgets.QLabel(self.groupBox_3)
        self.label_NStintLaps.setGeometry(QtCore.QRect(20, 50, 81, 16))
        self.label_NStintLaps.setObjectName("label_NStintLaps")
        self.spinBoxStintLaps = QtWidgets.QSpinBox(self.groupBox_3)
        self.spinBoxStintLaps.setGeometry(QtCore.QRect(140, 50, 101, 22))
        self.spinBoxStintLaps.setMaximum(10000)
        self.spinBoxStintLaps.setSingleStep(1)
        self.spinBoxStintLaps.setObjectName("spinBoxStintLaps")
        self.groupBox_5 = QtWidgets.QGroupBox(self.tabGeneral)
        self.groupBox_5.setGeometry(QtCore.QRect(310, 10, 261, 91))
        self.groupBox_5.setObjectName("groupBox_5")
        self.label_13 = QtWidgets.QLabel(self.groupBox_5)
        self.label_13.setGeometry(QtCore.QRect(20, 60, 101, 16))
        self.label_13.setObjectName("label_13")
        self.label_12 = QtWidgets.QLabel(self.groupBox_5)
        self.label_12.setGeometry(QtCore.QRect(20, 20, 101, 16))
        self.label_12.setObjectName("label_12")
        self.doubleSpinBox_JokerLapDelta = QtWidgets.QDoubleSpinBox(self.groupBox_5)
        self.doubleSpinBox_JokerLapDelta.setGeometry(QtCore.QRect(140, 20, 101, 22))
        self.doubleSpinBox_JokerLapDelta.setPrefix("")
        self.doubleSpinBox_JokerLapDelta.setSuffix("")
        self.doubleSpinBox_JokerLapDelta.setDecimals(0)
        self.doubleSpinBox_JokerLapDelta.setMaximum(1000.0)
        self.doubleSpinBox_JokerLapDelta.setSingleStep(0.1)
        self.doubleSpinBox_JokerLapDelta.setProperty("value", self.db.config['JokerLapDelta'])
        self.doubleSpinBox_JokerLapDelta.setObjectName("doubleSpinBox_JokerLapDelta")
        self.doubleSpinBox_JokerLapsRequired = QtWidgets.QDoubleSpinBox(self.groupBox_5)
        self.doubleSpinBox_JokerLapsRequired.setGeometry(QtCore.QRect(140, 60, 101, 22))
        self.doubleSpinBox_JokerLapsRequired.setPrefix("")
        self.doubleSpinBox_JokerLapsRequired.setSuffix("")
        self.doubleSpinBox_JokerLapsRequired.setDecimals(0)
        self.doubleSpinBox_JokerLapsRequired.setMaximum(1000.0)
        self.doubleSpinBox_JokerLapsRequired.setSingleStep(1.0)
        self.doubleSpinBox_JokerLapsRequired.setProperty("value", self.db.config['JokerLapsRequired'])
        self.doubleSpinBox_JokerLapsRequired.setObjectName("doubleSpinBox_JokerLapsRequired")
        self.groupBox_7 = QtWidgets.QGroupBox(self.tabGeneral)
        self.groupBox_7.setGeometry(QtCore.QRect(10, 210, 291, 131))
        self.groupBox_7.setObjectName("groupBox_7")
        self.pushButtonTrackRotateLeft = QtWidgets.QPushButton(self.groupBox_7)
        self.pushButtonTrackRotateLeft.setGeometry(QtCore.QRect(40, 20, 75, 21))
        self.pushButtonTrackRotateLeft.setObjectName("pushButtonTrackRotateLeft")
        self.pushButtonTrackRotateRight = QtWidgets.QPushButton(self.groupBox_7)
        self.pushButtonTrackRotateRight.setGeometry(QtCore.QRect(160, 20, 75, 23))
        self.pushButtonTrackRotateRight.setObjectName("pushButtonTrackRotateRight")
        self.pushButtonLoadTrack = QtWidgets.QPushButton(self.groupBox_7)
        self.pushButtonLoadTrack.setGeometry(QtCore.QRect(40, 60, 75, 21))
        self.pushButtonLoadTrack.setObjectName("pushButtonLoadTrack")
        self.pushButtonSaveTrack = QtWidgets.QPushButton(self.groupBox_7)
        self.pushButtonSaveTrack.setGeometry(QtCore.QRect(160, 60, 75, 23))
        self.pushButtonSaveTrack.setObjectName("pushButtonSaveTrack")
        self.pushButtonLoadReferenceLap = QtWidgets.QPushButton(self.groupBox_7)
        self.pushButtonLoadReferenceLap.setGeometry(QtCore.QRect(40, 100, 191, 21))
        self.pushButtonLoadReferenceLap.setObjectName("pushButtonLoadReferenceLap")
        self.groupBox_8 = QtWidgets.QGroupBox(self.tabGeneral)
        self.groupBox_8.setGeometry(QtCore.QRect(310, 120, 261, 80))
        self.groupBox_8.setObjectName("groupBox_8")
        self.checkBox_BEnableLogger = QtWidgets.QCheckBox(self.groupBox_8)
        self.checkBox_BEnableLogger.setGeometry(QtCore.QRect(10, 20, 161, 17))
        self.checkBox_BEnableLogger.setObjectName("checkBox_BEnableLogger")
        self.checkBox_BEnableLapLogging = QtWidgets.QCheckBox(self.groupBox_8)
        self.checkBox_BEnableLapLogging.setGeometry(QtCore.QRect(10, 50, 161, 17))
        self.checkBox_BEnableLapLogging.setObjectName("checkBox_BEnableLapLogging")
        self.checkBox_BEnableLapLogging.setChecked(self.db.config['BEnableLapLogging'])
        self.groupBox_11 = QtWidgets.QGroupBox(self.tabGeneral)
        self.groupBox_11.setGeometry(QtCore.QRect(310, 210, 261, 141))
        self.groupBox_11.setObjectName("groupBox_11")
        self.pushButton_MSMapDecrease = QtWidgets.QPushButton(self.groupBox_11)
        self.pushButton_MSMapDecrease.setGeometry(QtCore.QRect(20, 60, 91, 23))
        self.pushButton_MSMapDecrease.setObjectName("pushButton_MSMapDecrease")
        self.pushButton_MSMapIncrease = QtWidgets.QPushButton(self.groupBox_11)
        self.pushButton_MSMapIncrease.setGeometry(QtCore.QRect(134, 60, 101, 23))
        self.pushButton_MSMapIncrease.setObjectName("pushButton_MSMapIncrease")
        self.comboBox_MultiSwitch = QtWidgets.QComboBox(self.groupBox_11)
        self.comboBox_MultiSwitch.setGeometry(QtCore.QRect(20, 20, 211, 22))
        self.comboBox_MultiSwitch.setObjectName("comboBox_MultiSwitch")
        tempDcList = list(dict(self.dcConfig))
        for i in range(0, len(tempDcList)):
            self.comboBox_MultiSwitch.addItem(tempDcList[i])
        self.comboBox_MultiSwitch.setMaxVisibleItems(len(tempDcList))
        self.comboBox_MultiSwitch.setCurrentIndex(0)
        self.pushButton_MSDriverMarker = QtWidgets.QPushButton(self.groupBox_11)
        self.pushButton_MSDriverMarker.setGeometry(QtCore.QRect(20, 100, 211, 23))
        self.pushButton_MSDriverMarker.setObjectName("pushButton_MSDriverMarker")
        self.tabWidget.addTab(self.tabGeneral, "")
        self.tabPitStops = QtWidgets.QWidget()
        self.tabPitStops.setObjectName("tabPitStops")
        self.label_10 = QtWidgets.QLabel(self.tabPitStops)
        self.label_10.setGeometry(QtCore.QRect(20, 50, 81, 16))
        self.label_10.setObjectName("label_10")
        self.doubleSpinBox_PitStopsRequired = QtWidgets.QDoubleSpinBox(self.tabPitStops)
        self.doubleSpinBox_PitStopsRequired.setGeometry(QtCore.QRect(140, 90, 101, 22))
        self.doubleSpinBox_PitStopsRequired.setPrefix("")
        self.doubleSpinBox_PitStopsRequired.setSuffix("")
        self.doubleSpinBox_PitStopsRequired.setDecimals(0)
        self.doubleSpinBox_PitStopsRequired.setMaximum(1000.0)
        self.doubleSpinBox_PitStopsRequired.setSingleStep(1.0)
        self.doubleSpinBox_PitStopsRequired.setProperty("value", 1.0)
        self.doubleSpinBox_PitStopsRequired.setObjectName("doubleSpinBox_PitStopsRequired")
        self.spinBox_FuelSetting = QtWidgets.QSpinBox(self.tabPitStops)
        self.spinBox_FuelSetting.setGeometry(QtCore.QRect(140, 200, 101, 22))
        self.spinBox_FuelSetting.setMaximum(200)
        self.spinBox_FuelSetting.setObjectName("spinBox_FuelSetting")
        self.spinBox_FuelSetting.setValue(self.db.config['VUserFuelSet'])
        self.checkBox_ChangeTyres = QtWidgets.QCheckBox(self.tabPitStops)
        self.checkBox_ChangeTyres.setEnabled(True)
        self.checkBox_ChangeTyres.setGeometry(QtCore.QRect(20, 130, 121, 17))
        self.checkBox_ChangeTyres.setAcceptDrops(False)
        self.checkBox_ChangeTyres.setObjectName("checkBox_ChangeTyres")
        self.checkBox_ChangeTyres.setChecked(self.db.config['BChangeTyres'])
        self.label_17 = QtWidgets.QLabel(self.tabPitStops)
        self.label_17.setGeometry(QtCore.QRect(20, 200, 101, 21))
        self.label_17.setObjectName("label_17")
        self.doubleSpinBox_PitStopDelta = QtWidgets.QDoubleSpinBox(self.tabPitStops)
        self.doubleSpinBox_PitStopDelta.setGeometry(QtCore.QRect(140, 50, 101, 22))
        self.doubleSpinBox_PitStopDelta.setPrefix("")
        self.doubleSpinBox_PitStopDelta.setSuffix("")
        self.doubleSpinBox_PitStopDelta.setDecimals(1)
        self.doubleSpinBox_PitStopDelta.setMaximum(1000.0)
        self.doubleSpinBox_PitStopDelta.setSingleStep(0.1)
        self.doubleSpinBox_PitStopDelta.setProperty("value", 60.0)
        self.doubleSpinBox_PitStopDelta.setObjectName("doubleSpinBox_PitStopDelta")
        self.label_16 = QtWidgets.QLabel(self.tabPitStops)
        self.label_16.setGeometry(QtCore.QRect(20, 160, 101, 21))
        self.label_16.setObjectName("label_16")
        self.checkBox_FuelUp = QtWidgets.QCheckBox(self.tabPitStops)
        self.checkBox_FuelUp.setGeometry(QtCore.QRect(150, 130, 81, 17))
        self.checkBox_FuelUp.setObjectName("checkBox_FuelUp")
        self.checkBox_FuelUp.setChecked(self.db.config['BBeginFueling'])
        self.label_11 = QtWidgets.QLabel(self.tabPitStops)
        self.label_11.setGeometry(QtCore.QRect(20, 90, 101, 16))
        self.label_11.setObjectName("label_11")
        self.comboBox_FuelMethod = QtWidgets.QComboBox(self.tabPitStops)
        self.comboBox_FuelMethod.setGeometry(QtCore.QRect(140, 160, 101, 22))
        self.comboBox_FuelMethod.setObjectName("comboBox_FuelMethod")
        self.comboBox_FuelMethod.addItem("")
        self.comboBox_FuelMethod.addItem("")
        self.checkBox_PitCommandControl = QtWidgets.QCheckBox(self.tabPitStops)
        self.checkBox_PitCommandControl.setEnabled(True)
        self.checkBox_PitCommandControl.setGeometry(QtCore.QRect(20, 20, 221, 17))
        self.checkBox_PitCommandControl.setAcceptDrops(False)
        self.checkBox_PitCommandControl.setObjectName("checkBox_PitCommandControl")
        self.checkBox_PitCommandControl.setChecked(self.db.config['BPitCommandControl'])
        self.tabWidget.addTab(self.tabPitStops, "")
        self.tabUpshiftTone = QtWidgets.QWidget()
        self.tabUpshiftTone.setObjectName("tabUpshiftTone")
        self.groupBox = QtWidgets.QGroupBox(self.tabUpshiftTone)
        self.groupBox.setGeometry(QtCore.QRect(10, 10, 301, 391))
        self.groupBox.setObjectName("groupBox")
        self.groupBox_Gear1 = QtWidgets.QGroupBox(self.groupBox)
        self.groupBox_Gear1.setGeometry(QtCore.QRect(10, 20, 271, 51))
        self.groupBox_Gear1.setObjectName("groupBox_Gear1")
        self.spinBox_Gear1 = QtWidgets.QSpinBox(self.groupBox_Gear1)
        self.spinBox_Gear1.setGeometry(QtCore.QRect(20, 20, 71, 22))
        self.spinBox_Gear1.setMinimum(4000)
        self.spinBox_Gear1.setMaximum(20000)
        self.spinBox_Gear1.setSingleStep(10)
        self.spinBox_Gear1.setObjectName("spinBox_Gear1")
        self.label = QtWidgets.QLabel(self.groupBox_Gear1)
        self.label.setGeometry(QtCore.QRect(110, 20, 46, 22))
        self.label.setObjectName("label")
        self.checkBox_Gear1 = QtWidgets.QCheckBox(self.groupBox_Gear1)
        self.checkBox_Gear1.setEnabled(True)
        self.checkBox_Gear1.setGeometry(QtCore.QRect(170, 20, 51, 22))
        self.checkBox_Gear1.setAcceptDrops(False)
        self.checkBox_Gear1.setChecked(True)
        self.checkBox_Gear1.setObjectName("checkBox_Gear1")
        self.groupBox_Gear2 = QtWidgets.QGroupBox(self.groupBox)
        self.groupBox_Gear2.setGeometry(QtCore.QRect(10, 70, 271, 51))
        self.groupBox_Gear2.setObjectName("groupBox_Gear2")
        self.spinBox_Gear2 = QtWidgets.QSpinBox(self.groupBox_Gear2)
        self.spinBox_Gear2.setGeometry(QtCore.QRect(20, 20, 71, 22))
        self.spinBox_Gear2.setMinimum(4000)
        self.spinBox_Gear2.setMaximum(20000)
        self.spinBox_Gear2.setSingleStep(10)
        self.spinBox_Gear2.setObjectName("spinBox_Gear2")
        self.label_2 = QtWidgets.QLabel(self.groupBox_Gear2)
        self.label_2.setGeometry(QtCore.QRect(110, 20, 46, 22))
        self.label_2.setObjectName("label_2")
        self.checkBox_Gear2 = QtWidgets.QCheckBox(self.groupBox_Gear2)
        self.checkBox_Gear2.setGeometry(QtCore.QRect(170, 20, 51, 22))
        self.checkBox_Gear2.setChecked(True)
        self.checkBox_Gear2.setObjectName("checkBox_Gear2")
        self.groupBox_Gear3 = QtWidgets.QGroupBox(self.groupBox)
        self.groupBox_Gear3.setGeometry(QtCore.QRect(10, 120, 271, 51))
        self.groupBox_Gear3.setObjectName("groupBox_Gear3")
        self.spinBox_Gear3 = QtWidgets.QSpinBox(self.groupBox_Gear3)
        self.spinBox_Gear3.setGeometry(QtCore.QRect(20, 20, 71, 22))
        self.spinBox_Gear3.setMinimum(4000)
        self.spinBox_Gear3.setMaximum(20000)
        self.spinBox_Gear3.setSingleStep(10)
        self.spinBox_Gear3.setObjectName("spinBox_Gear3")
        self.label_3 = QtWidgets.QLabel(self.groupBox_Gear3)
        self.label_3.setGeometry(QtCore.QRect(110, 20, 46, 22))
        self.label_3.setObjectName("label_3")
        self.checkBox_Gear3 = QtWidgets.QCheckBox(self.groupBox_Gear3)
        self.checkBox_Gear3.setGeometry(QtCore.QRect(170, 20, 51, 22))
        self.checkBox_Gear3.setChecked(True)
        self.checkBox_Gear3.setObjectName("checkBox_Gear3")
        self.groupBox_Gear4 = QtWidgets.QGroupBox(self.groupBox)
        self.groupBox_Gear4.setGeometry(QtCore.QRect(10, 170, 271, 51))
        self.groupBox_Gear4.setObjectName("groupBox_Gear4")
        self.spinBox_Gear4 = QtWidgets.QSpinBox(self.groupBox_Gear4)
        self.spinBox_Gear4.setGeometry(QtCore.QRect(20, 20, 71, 22))
        self.spinBox_Gear4.setMinimum(4000)
        self.spinBox_Gear4.setMaximum(20000)
        self.spinBox_Gear4.setSingleStep(10)
        self.spinBox_Gear4.setObjectName("spinBox_Gear4")
        self.label_4 = QtWidgets.QLabel(self.groupBox_Gear4)
        self.label_4.setGeometry(QtCore.QRect(110, 20, 46, 22))
        self.label_4.setObjectName("label_4")
        self.checkBox_Gear4 = QtWidgets.QCheckBox(self.groupBox_Gear4)
        self.checkBox_Gear4.setGeometry(QtCore.QRect(170, 20, 51, 22))
        self.checkBox_Gear4.setChecked(True)
        self.checkBox_Gear4.setObjectName("checkBox_Gear4")
        self.groupBox_Gear2_4 = QtWidgets.QGroupBox(self.groupBox)
        self.groupBox_Gear2_4.setGeometry(QtCore.QRect(10, 220, 271, 51))
        self.groupBox_Gear2_4.setObjectName("groupBox_Gear2_4")
        self.spinBox_Gear5 = QtWidgets.QSpinBox(self.groupBox_Gear2_4)
        self.spinBox_Gear5.setGeometry(QtCore.QRect(20, 20, 71, 22))
        self.spinBox_Gear5.setMinimum(4000)
        self.spinBox_Gear5.setMaximum(20000)
        self.spinBox_Gear5.setSingleStep(10)
        self.spinBox_Gear5.setObjectName("spinBox_Gear5")
        self.label_5 = QtWidgets.QLabel(self.groupBox_Gear2_4)
        self.label_5.setGeometry(QtCore.QRect(110, 20, 46, 22))
        self.label_5.setObjectName("label_5")
        self.checkBox_Gear5 = QtWidgets.QCheckBox(self.groupBox_Gear2_4)
        self.checkBox_Gear5.setGeometry(QtCore.QRect(170, 20, 51, 22))
        self.checkBox_Gear5.setChecked(True)
        self.checkBox_Gear5.setObjectName("checkBox_Gear5")
        self.groupBox_Gear6 = QtWidgets.QGroupBox(self.groupBox)
        self.groupBox_Gear6.setGeometry(QtCore.QRect(10, 270, 271, 51))
        self.groupBox_Gear6.setObjectName("groupBox_Gear6")
        self.spinBox_Gear6 = QtWidgets.QSpinBox(self.groupBox_Gear6)
        self.spinBox_Gear6.setGeometry(QtCore.QRect(20, 20, 71, 22))
        self.spinBox_Gear6.setMinimum(4000)
        self.spinBox_Gear6.setMaximum(20000)
        self.spinBox_Gear6.setSingleStep(10)
        self.spinBox_Gear6.setObjectName("spinBox_Gear6")
        self.label_6 = QtWidgets.QLabel(self.groupBox_Gear6)
        self.label_6.setGeometry(QtCore.QRect(110, 20, 46, 22))
        self.label_6.setObjectName("label_6")
        self.checkBox_Gear6 = QtWidgets.QCheckBox(self.groupBox_Gear6)
        self.checkBox_Gear6.setGeometry(QtCore.QRect(170, 20, 51, 22))
        self.checkBox_Gear6.setObjectName("checkBox_Gear6")
        self.groupBox_Gear7 = QtWidgets.QGroupBox(self.groupBox)
        self.groupBox_Gear7.setGeometry(QtCore.QRect(10, 330, 271, 51))
        self.groupBox_Gear7.setObjectName("groupBox_Gear7")
        self.spinBox_Gear7 = QtWidgets.QSpinBox(self.groupBox_Gear7)
        self.spinBox_Gear7.setGeometry(QtCore.QRect(20, 20, 71, 22))
        self.spinBox_Gear7.setMinimum(4000)
        self.spinBox_Gear7.setMaximum(20000)
        self.spinBox_Gear7.setSingleStep(10)
        self.spinBox_Gear7.setObjectName("spinBox_Gear7")
        self.label_7 = QtWidgets.QLabel(self.groupBox_Gear7)
        self.label_7.setGeometry(QtCore.QRect(110, 20, 46, 22))
        self.label_7.setObjectName("label_7")
        self.checkBox_Gear7 = QtWidgets.QCheckBox(self.groupBox_Gear7)
        self.checkBox_Gear7.setGeometry(QtCore.QRect(170, 20, 51, 22))
        self.checkBox_Gear7.setObjectName("checkBox_Gear7")
        self.groupBox_6 = QtWidgets.QGroupBox(self.tabUpshiftTone)
        self.groupBox_6.setGeometry(QtCore.QRect(340, 10, 401, 141))
        self.groupBox_6.setObjectName("groupBox_6")
        self.saveButton = QtWidgets.QPushButton(self.groupBox_6)
        self.saveButton.setGeometry(QtCore.QRect(100, 100, 41, 23))
        self.saveButton.setObjectName("saveButton")
        self.label_9 = QtWidgets.QLabel(self.groupBox_6)
        self.label_9.setGeometry(QtCore.QRect(20, 60, 101, 22))
        self.label_9.setObjectName("label_9")
        self.checkBox_UpshiftTone = QtWidgets.QCheckBox(self.groupBox_6)
        self.checkBox_UpshiftTone.setGeometry(QtCore.QRect(20, 30, 251, 17))
        self.checkBox_UpshiftTone.setChecked(self.db.config['ShiftToneEnabled'])
        self.checkBox_UpshiftTone.setObjectName("checkBox_UpshiftTone")
        self.openButton = QtWidgets.QPushButton(self.groupBox_6)
        self.openButton.setGeometry(QtCore.QRect(20, 100, 41, 23))
        self.openButton.setObjectName("openButton")
        self.comboBox = QtWidgets.QComboBox(self.groupBox_6)
        self.comboBox.setGeometry(QtCore.QRect(150, 60, 131, 22))
        self.comboBox.setMaxVisibleItems(5)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("iRacing First RPM")
        self.comboBox.addItem("iRacing Shift RPM")
        self.comboBox.addItem("iRacing Last RPM")
        self.comboBox.addItem("iRacing Blink RPM")
        self.comboBox.addItem("User defined")
        self.comboBox.addItem("from Car properties")
        self.comboBox.setMaxVisibleItems(6)
        self.comboBox.setCurrentIndex(self.db.config['UpshiftStrategy'])
        self.comboBox_FuelMethod.setCurrentIndex(self.db.config['NFuelSetMethod'])
        self.pushButton_calcUpshiftRPM = QtWidgets.QPushButton(self.groupBox_6)
        self.pushButton_calcUpshiftRPM.setGeometry(QtCore.QRect(180, 100, 201, 23))
        self.pushButton_calcUpshiftRPM.setObjectName("pushButton_calcUpshiftRPM")
        self.groupBox_10 = QtWidgets.QGroupBox(self.tabUpshiftTone)
        self.groupBox_10.setGeometry(QtCore.QRect(340, 160, 401, 91))
        self.groupBox_10.setObjectName("groupBox_10")
        self.pushButton_testShiftTone = QtWidgets.QPushButton(self.groupBox_10)
        self.pushButton_testShiftTone.setGeometry(QtCore.QRect(260, 40, 91, 23))
        self.pushButton_testShiftTone.setObjectName("pushButton_testShiftTone")
        self.label_20 = QtWidgets.QLabel(self.groupBox_10)
        self.label_20.setGeometry(QtCore.QRect(10, 20, 101, 22))
        self.label_20.setObjectName("label_20")
        self.spinBox_ShiftToneFrequency = QtWidgets.QSpinBox(self.groupBox_10)
        self.spinBox_ShiftToneFrequency.setGeometry(QtCore.QRect(130, 20, 71, 22))
        self.spinBox_ShiftToneFrequency.setMinimum(0)
        self.spinBox_ShiftToneFrequency.setMaximum(2000)
        self.spinBox_ShiftToneFrequency.setSingleStep(10)
        self.spinBox_ShiftToneFrequency.setProperty("value", self.db.config['fShiftBeep'])
        self.spinBox_ShiftToneFrequency.setObjectName("spinBox_ShiftToneFrequency")
        self.spinBox_ShiftToneDuration = QtWidgets.QSpinBox(self.groupBox_10)
        self.spinBox_ShiftToneDuration.setGeometry(QtCore.QRect(130, 60, 71, 22))
        self.spinBox_ShiftToneDuration.setMinimum(0)
        self.spinBox_ShiftToneDuration.setMaximum(1000)
        self.spinBox_ShiftToneDuration.setSingleStep(10)
        self.spinBox_ShiftToneDuration.setProperty("value", self.db.config['tShiftBeep'])
        self.spinBox_ShiftToneDuration.setObjectName("spinBox_ShiftToneDuration")
        self.label_21 = QtWidgets.QLabel(self.groupBox_10)
        self.label_21.setGeometry(QtCore.QRect(10, 60, 101, 22))
        self.label_21.setObjectName("label_21")
        self.tabWidget.addTab(self.tabUpshiftTone, "")
        self.tabFuelManagement = QtWidgets.QWidget()
        self.tabFuelManagement.setObjectName("tabFuelManagement")
        self.groupBox_9 = QtWidgets.QGroupBox(self.tabFuelManagement)
        self.groupBox_9.setGeometry(QtCore.QRect(10, 10, 231, 321))
        self.groupBox_9.setObjectName("groupBox_9")
        self.openButton_2 = QtWidgets.QPushButton(self.groupBox_9)
        self.openButton_2.setGeometry(QtCore.QRect(20, 60, 191, 23))
        self.openButton_2.setObjectName("openButton_2")
        self.calcFuelSavingButton = QtWidgets.QPushButton(self.groupBox_9)
        self.calcFuelSavingButton.setGeometry(QtCore.QRect(20, 160, 191, 23))
        self.calcFuelSavingButton.setObjectName("calcFuelSavingButton")
        self.calcRollOutButton = QtWidgets.QPushButton(self.groupBox_9)
        self.calcRollOutButton.setGeometry(QtCore.QRect(20, 110, 191, 23))
        self.calcRollOutButton.setObjectName("calcRollOutButton")
        self.label_VFuelTGT = QtWidgets.QLabel(self.groupBox_9)
        self.label_VFuelTGT.setGeometry(QtCore.QRect(20, 210, 101, 22))
        self.label_VFuelTGT.setObjectName("label_VFuelTGT")
        self.doubleSpinBox_VFuelTGT = QtWidgets.QDoubleSpinBox(self.groupBox_9)
        self.doubleSpinBox_VFuelTGT.setGeometry(QtCore.QRect(140, 210, 71, 22))
        self.doubleSpinBox_VFuelTGT.setPrefix("")
        self.doubleSpinBox_VFuelTGT.setSuffix("")
        self.doubleSpinBox_VFuelTGT.setDecimals(2)
        self.doubleSpinBox_VFuelTGT.setMinimum(0.0)
        self.doubleSpinBox_VFuelTGT.setMaximum(20.0)
        self.doubleSpinBox_VFuelTGT.setSingleStep(0.01)
        self.doubleSpinBox_VFuelTGT.setProperty("value", self.db.config['VFuelTgt'])
        self.doubleSpinBox_VFuelTGT.setObjectName("doubleSpinBox_VFuelTGT")
        self.comboBox_NFuelConsumptionMethod = QtWidgets.QComboBox(self.groupBox_9)
        self.comboBox_NFuelConsumptionMethod.setGeometry(QtCore.QRect(20, 280, 191, 22))
        self.comboBox_NFuelConsumptionMethod.setMaxVisibleItems(3)
        self.comboBox_NFuelConsumptionMethod.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToMinimumContentsLengthWithIcon)
        self.comboBox_NFuelConsumptionMethod.setObjectName("comboBox_NFuelConsumptionMethod")
        self.comboBox_NFuelConsumptionMethod.addItem("Average all laps")
        self.comboBox_NFuelConsumptionMethod.addItem("Average last 3 laps")
        self.comboBox_NFuelConsumptionMethod.addItem("Reference lap")
        self.label_NFuelConsumptionMethod = QtWidgets.QLabel(self.groupBox_9)
        self.label_NFuelConsumptionMethod.setGeometry(QtCore.QRect(20, 250, 191, 22))
        self.label_NFuelConsumptionMethod.setObjectName("label_NFuelConsumptionMethod")
        self.comboBox_NFuelManagement = QtWidgets.QComboBox(self.groupBox_9)
        self.comboBox_NFuelManagement.setGeometry(QtCore.QRect(20, 20, 191, 22))
        self.comboBox_NFuelManagement.setMaxVisibleItems(4)
        self.comboBox_NFuelManagement.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToMinimumContentsLengthWithIcon)
        self.comboBox_NFuelManagement.setObjectName("comboBox_NFuelManagement")
        self.comboBox_NFuelManagement.addItem("Off")
        self.comboBox_NFuelManagement.addItem("Static Target")
        self.comboBox_NFuelManagement.addItem("End of Race")
        self.comboBox_NFuelManagement.addItem("End of Stint")
        self.groupBox_4 = QtWidgets.QGroupBox(self.tabFuelManagement)
        self.groupBox_4.setGeometry(QtCore.QRect(250, 10, 511, 141))
        self.groupBox_4.setObjectName("groupBox_4")
        self.pushButton_testFuelTone = QtWidgets.QPushButton(self.groupBox_4)
        self.pushButton_testFuelTone.setGeometry(QtCore.QRect(310, 70, 141, 41))
        self.pushButton_testFuelTone.setObjectName("pushButton_testFuelTone")
        self.label_FuelToneFrequency = QtWidgets.QLabel(self.groupBox_4)
        self.label_FuelToneFrequency.setGeometry(QtCore.QRect(10, 20, 101, 22))
        self.label_FuelToneFrequency.setObjectName("label_FuelToneFrequency")
        self.spinBox_FuelToneFrequency = QtWidgets.QSpinBox(self.groupBox_4)
        self.spinBox_FuelToneFrequency.setGeometry(QtCore.QRect(150, 20, 71, 22))
        self.spinBox_FuelToneFrequency.setMinimum(0)
        self.spinBox_FuelToneFrequency.setMaximum(2000)
        self.spinBox_FuelToneFrequency.setSingleStep(10)
        self.spinBox_FuelToneFrequency.setProperty("value", self.db.config['fFuelBeep'])
        self.spinBox_FuelToneFrequency.setObjectName("spinBox_FuelToneFrequency")
        self.spinBox_FuelToneDuration = QtWidgets.QSpinBox(self.groupBox_4)
        self.spinBox_FuelToneDuration.setGeometry(QtCore.QRect(150, 60, 71, 22))
        self.spinBox_FuelToneDuration.setMinimum(0)
        self.spinBox_FuelToneDuration.setMaximum(1000)
        self.spinBox_FuelToneDuration.setSingleStep(10)
        self.spinBox_FuelToneDuration.setProperty("value", self.db.config['tFuelBeep'])
        self.spinBox_FuelToneDuration.setObjectName("spinBox_FuelToneDuration")
        self.label_FuelToneDuration = QtWidgets.QLabel(self.groupBox_4)
        self.label_FuelToneDuration.setGeometry(QtCore.QRect(10, 60, 101, 22))
        self.label_FuelToneDuration.setObjectName("label_FuelToneDuration")
        self.label_tLiftReaction = QtWidgets.QLabel(self.groupBox_4)
        self.label_tLiftReaction.setGeometry(QtCore.QRect(280, 20, 101, 22))
        self.label_tLiftReaction.setObjectName("label_tLiftReaction")
        self.doubleSpinBox_tLiftReaction = QtWidgets.QDoubleSpinBox(self.groupBox_4)
        self.doubleSpinBox_tLiftReaction.setGeometry(QtCore.QRect(390, 20, 101, 22))
        self.doubleSpinBox_tLiftReaction.setPrefix("")
        self.doubleSpinBox_tLiftReaction.setSuffix("")
        self.doubleSpinBox_tLiftReaction.setDecimals(2)
        self.doubleSpinBox_tLiftReaction.setMinimum(-2.0)
        self.doubleSpinBox_tLiftReaction.setMaximum(2.0)
        self.doubleSpinBox_tLiftReaction.setSingleStep(0.01)
        self.doubleSpinBox_tLiftReaction.setProperty("value", self.db.config['tReactionLift'])
        self.doubleSpinBox_tLiftReaction.setObjectName("doubleSpinBox_tLiftReaction")
        self.label_tLiftGap = QtWidgets.QLabel(self.groupBox_4)
        self.label_tLiftGap.setGeometry(QtCore.QRect(10, 100, 121, 22))
        self.label_tLiftGap.setObjectName("label_tLiftGap")
        self.doubleSpinBox_tLiftGap = QtWidgets.QDoubleSpinBox(self.groupBox_4)
        self.doubleSpinBox_tLiftGap.setGeometry(QtCore.QRect(150, 100, 71, 22))
        self.doubleSpinBox_tLiftGap.setPrefix("")
        self.doubleSpinBox_tLiftGap.setSuffix("")
        self.doubleSpinBox_tLiftGap.setDecimals(2)
        self.doubleSpinBox_tLiftGap.setMinimum(-3.0)
        self.doubleSpinBox_tLiftGap.setMaximum(3.0)
        self.doubleSpinBox_tLiftGap.setSingleStep(0.01)
        self.doubleSpinBox_tLiftGap.setProperty("value", self.db.config['tLiftGap'])
        self.doubleSpinBox_tLiftGap.setObjectName("doubleSpinBox_tLiftGap")
        self.tabWidget.addTab(self.tabFuelManagement, "")
        self.tabDebug = QtWidgets.QWidget()
        self.tabDebug.setObjectName("tabDebug")
        self.textEdit = QtWidgets.QTextEdit(self.tabDebug)
        self.textEdit.setGeometry(QtCore.QRect(10, 40, 756, 331))
        self.textEdit.setObjectName("textEdit")
        self.pushButtonInvoke = QtWidgets.QPushButton(self.tabDebug)
        self.pushButtonInvoke.setGeometry(QtCore.QRect(670, 380, 101, 23))
        self.pushButtonInvoke.setObjectName("pushButtonInvoke")
        self.lineEditInvoke = QtWidgets.QLineEdit(self.tabDebug)
        self.lineEditInvoke.setGeometry(QtCore.QRect(10, 380, 651, 20))
        self.lineEditInvoke.setObjectName("lineEditInvoke")
        self.pushButtonSaveSnapshot = QtWidgets.QPushButton(self.tabDebug)
        self.pushButtonSaveSnapshot.setGeometry(QtCore.QRect(10, 10, 101, 23))
        self.pushButtonSaveSnapshot.setObjectName("pushButtonSaveSnapshot")
        self.pushButtonLoadSnapshot = QtWidgets.QPushButton(self.tabDebug)
        self.pushButtonLoadSnapshot.setGeometry(QtCore.QRect(120, 10, 101, 23))
        self.pushButtonLoadSnapshot.setObjectName("pushButtonLoadSnapshot")
        self.tabWidget.addTab(self.tabDebug, "")
        self.tabSettings = QtWidgets.QWidget()
        self.tabSettings.setObjectName("tabSettings")
        self.pushButtonSaveConfig = QtWidgets.QPushButton(self.tabSettings)
        self.pushButtonSaveConfig.setGeometry(QtCore.QRect(10, 10, 75, 23))
        self.pushButtonSaveConfig.setObjectName("pushButtonSaveConfig")
        self.pushButtonLoadConfig = QtWidgets.QPushButton(self.tabSettings)
        self.pushButtonLoadConfig.setGeometry(QtCore.QRect(100, 10, 75, 23))
        self.pushButtonLoadConfig.setObjectName("pushButtonLoadConfig")
        self.label_22 = QtWidgets.QLabel(self.tabSettings)
        self.label_22.setGeometry(QtCore.QRect(20, 50, 91, 16))
        self.label_22.setObjectName("label_22")
        self.label_23 = QtWidgets.QLabel(self.tabSettings)
        self.label_23.setGeometry(QtCore.QRect(20, 90, 91, 16))
        self.label_23.setObjectName("label_23")
        self.lineEditiRPath = QtWidgets.QLineEdit(self.tabSettings)
        self.lineEditiRPath.setEnabled(True)
        self.lineEditiRPath.setGeometry(QtCore.QRect(110, 50, 521, 20))
        self.lineEditiRPath.setObjectName("lineEditiRPath")
        self.lineEditTelemPath = QtWidgets.QLineEdit(self.tabSettings)
        self.lineEditTelemPath.setGeometry(QtCore.QRect(110, 90, 521, 20))
        self.lineEditTelemPath.setObjectName("lineEditTelemPath")
        self.pushButtonSetiRPath = QtWidgets.QPushButton(self.tabSettings)
        self.pushButtonSetiRPath.setGeometry(QtCore.QRect(640, 50, 101, 23))
        self.pushButtonSetiRPath.setObjectName("pushButtonSetiRPath")
        self.pushButtonSetTelemPath = QtWidgets.QPushButton(self.tabSettings)
        self.pushButtonSetTelemPath.setGeometry(QtCore.QRect(640, 90, 101, 23))
        self.pushButtonSetTelemPath.setObjectName("pushButtonSetTelemPath")
        self.groupBox_12 = QtWidgets.QGroupBox(self.tabSettings)
        self.groupBox_12.setEnabled(True)
        self.groupBox_12.setGeometry(QtCore.QRect(10, 120, 751, 211))
        font = QtGui.QFont()
        font.setKerning(False)
        self.groupBox_12.setFont(font)
        self.groupBox_12.setObjectName("groupBox_12")
        self.pushButtonSaveDDUPage = QtWidgets.QPushButton(self.groupBox_12)
        self.pushButtonSaveDDUPage.setGeometry(QtCore.QRect(10, 60, 161, 21))
        self.pushButtonSaveDDUPage.setObjectName("pushButtonSaveDDUPage")
        self.lineEditDDUPage = QtWidgets.QLineEdit(self.groupBox_12)
        self.lineEditDDUPage.setGeometry(QtCore.QRect(190, 60, 541, 20))
        self.lineEditDDUPage.setObjectName("lineEditDDUPage")
        self.pushButtonPreviousMulti = QtWidgets.QPushButton(self.groupBox_12)
        self.pushButtonPreviousMulti.setGeometry(QtCore.QRect(10, 90, 161, 21))
        self.pushButtonPreviousMulti.setObjectName("pushButtonPreviousMulti")
        self.lineEditPreviousMulti = QtWidgets.QLineEdit(self.groupBox_12)
        self.lineEditPreviousMulti.setGeometry(QtCore.QRect(190, 90, 541, 20))
        self.lineEditPreviousMulti.setObjectName("lineEditPreviousMulti")
        self.pushButtonNextMulti = QtWidgets.QPushButton(self.groupBox_12)
        self.pushButtonNextMulti.setGeometry(QtCore.QRect(10, 120, 161, 21))
        self.pushButtonNextMulti.setObjectName("pushButtonNextMulti")
        self.lineEditNextMulti = QtWidgets.QLineEdit(self.groupBox_12)
        self.lineEditNextMulti.setGeometry(QtCore.QRect(190, 120, 541, 20))
        self.lineEditNextMulti.setObjectName("lineEditNextMulti")
        self.pushButtonMultiDecrease = QtWidgets.QPushButton(self.groupBox_12)
        self.pushButtonMultiDecrease.setGeometry(QtCore.QRect(10, 150, 161, 21))
        self.pushButtonMultiDecrease.setObjectName("pushButtonMultiDecrease")
        self.lineEditMultiDecrease = QtWidgets.QLineEdit(self.groupBox_12)
        self.lineEditMultiDecrease.setGeometry(QtCore.QRect(190, 150, 541, 20))
        self.lineEditMultiDecrease.setObjectName("lineEditMultiDecrease")
        self.pushButtonMultiIncrease = QtWidgets.QPushButton(self.groupBox_12)
        self.pushButtonMultiIncrease.setGeometry(QtCore.QRect(10, 180, 161, 21))
        self.pushButtonMultiIncrease.setObjectName("pushButtonMultiIncrease")
        self.lineEditMultiIncrease = QtWidgets.QLineEdit(self.groupBox_12)
        self.lineEditMultiIncrease.setGeometry(QtCore.QRect(190, 180, 541, 20))
        self.lineEditMultiIncrease.setObjectName("lineEditMultiIncrease")
        self.label_24 = QtWidgets.QLabel(self.groupBox_12)
        self.label_24.setGeometry(QtCore.QRect(20, 20, 101, 21))
        self.label_24.setObjectName("label_24")
        self.comboBox_JoystickSelection = QtWidgets.QComboBox(self.groupBox_12)
        self.comboBox_JoystickSelection.setGeometry(QtCore.QRect(190, 20, 541, 22))
        self.comboBox_JoystickSelection.setObjectName("comboBox_JoystickSelection")
        self.comboBox_JoystickSelection.addItem("")
        self.comboBox_JoystickSelection.addItem("")
        self.comboBox_JoystickSelection.addItem("")
        self.comboBox_JoystickSelection.addItem("")
        self.comboBox_JoystickSelection.addItem("")
        self.comboBox_JoystickSelection.addItem("")
        self.comboBox_JoystickSelection.addItem("")
        self.comboBox_JoystickSelection.addItem("")
        self.comboBox_JoystickSelection.addItem("")
        self.tabWidget.addTab(self.tabSettings, "")


        self.checkBox_BEnableLogger.setChecked(self.db.config['BLoggerActive'])

        self.spinBoxRaceLaps.setValue(self.db.config['UserRaceLaps'])
        self.doubleSpinBox_PitStopDelta.setValue(self.db.config['PitStopDelta'])
        self.doubleSpinBox_PitStopsRequired.setValue(self.db.config['PitStopsRequired'])

        self.spinBoxRaceLaps.valueChanged.connect(self.assignRaceLaps)
        self.doubleSpinBox_PitStopDelta.valueChanged.connect(self.assignPitStopDelta)
        self.doubleSpinBox_PitStopsRequired.valueChanged.connect(self.assignPitStopsRequired)

        self.checkBox_UpshiftTone.stateChanged.connect(self.EnableShiftTone)
        self.comboBox.currentIndexChanged.connect(self.UpshiftStrategy)
        self.spinBox_Gear1.valueChanged.connect(self.UpshiftStrategy)
        self.checkBox_Gear1.stateChanged.connect(self.UpshiftStrategy)
        self.spinBox_Gear2.valueChanged.connect(self.UpshiftStrategy)
        self.checkBox_Gear2.stateChanged.connect(self.UpshiftStrategy)
        self.spinBox_Gear3.valueChanged.connect(self.UpshiftStrategy)
        self.checkBox_Gear3.stateChanged.connect(self.UpshiftStrategy)
        self.spinBox_Gear4.valueChanged.connect(self.UpshiftStrategy)
        self.checkBox_Gear4.stateChanged.connect(self.UpshiftStrategy)
        self.spinBox_Gear5.valueChanged.connect(self.UpshiftStrategy)
        self.checkBox_Gear5.stateChanged.connect(self.UpshiftStrategy)
        self.spinBox_Gear6.valueChanged.connect(self.UpshiftStrategy)
        self.checkBox_Gear6.stateChanged.connect(self.UpshiftStrategy)
        self.spinBox_Gear7.valueChanged.connect(self.UpshiftStrategy)
        self.checkBox_Gear7.stateChanged.connect(self.UpshiftStrategy)
        self.pushButtonInvoke.clicked.connect(self.InvokeUserCommand)
        self.lineEditInvoke.returnPressed.connect(self.InvokeUserCommand)
        self.pushButton_StartDDU.clicked.connect(self.StartDDU)
        self.pushButton_StopDDU.clicked.connect(self.StopDDU)
        self.saveButton.clicked.connect(self.saveShiftToneSettings)
        self.openButton.clicked.connect(self.loadShiftToneSettings)
        self.pushButtonLoadSnapshot.clicked.connect(self.loadRTDBSnapshot)
        self.pushButtonSaveSnapshot.clicked.connect(self.saveRTDBSnapshot)
        self.pushButtonTrackRotateLeft.clicked.connect(self.rotateTrackLeft)
        self.pushButtonTrackRotateRight.clicked.connect(self.rotateTrackRight)
        self.pushButtonLoadTrack.clicked.connect(self.loadTrack)
        self.pushButtonSaveTrack.clicked.connect(self.saveTrack)
        self.pushButtonLoadReferenceLap.clicked.connect(self.loadReferenceLap)

        self.doubleSpinBox_DRSActivations.valueChanged.connect(self.assignDRS)
        self.doubleSpinBox_JokerLapDelta.valueChanged.connect(self.assignJokerDelta)
        self.doubleSpinBox_JokerLapsRequired.valueChanged.connect(self.assignJokerLaps)
        self.doubleSpinBox_P2PActivations.valueChanged.connect(self.assignP2P)
        self.checkBox_MapHighlight.stateChanged.connect(self.MapHighlight)
        self.checkBox_BEnableLogger.stateChanged.connect(self.enableLogger)
        self.checkBox_BEnableLapLogging.stateChanged.connect(self.enableLapLogging)

        self.checkBox_FuelUp.stateChanged.connect(self.enableFuelUp)
        self.checkBox_ChangeTyres.stateChanged.connect(self.enableTyreChange)
        self.spinBox_FuelSetting.valueChanged.connect(self.setUserFuelPreset)
        self.comboBox_FuelMethod.currentIndexChanged.connect(self.setFuelSetMethod)

        self.checkBox_PitCommandControl.stateChanged.connect(self.setPitCommandControl)

        self.spinBox_FuelToneFrequency.valueChanged.connect(self.FuelBeep)
        self.spinBox_FuelToneDuration.valueChanged.connect(self.FuelBeep)
        self.pushButton_testFuelTone.clicked.connect(self.testFuelTone)
        # self.checkBox_EnableFuelManagement.stateChanged.connect(self.enableFuelManagement)
        self.openButton_2.clicked.connect(self.loadFuelManagementSettings)
        self.pushButton_testShiftTone.clicked.connect(self.testShiftTone)
        self.spinBox_ShiftToneFrequency.valueChanged.connect(self.ShiftBeep)
        self.spinBox_ShiftToneDuration.valueChanged.connect(self.ShiftBeep)
        self.calcFuelSavingButton.clicked.connect(self.calcFuelSaving)
        self.pushButton_calcUpshiftRPM.clicked.connect(self.calcUpshiftRPM)
        self.calcRollOutButton.clicked.connect(self.calcRollOut)

        self.pushButton_MSMapDecrease.clicked.connect(self.MSMapDecrease)
        self.pushButton_MSMapIncrease.clicked.connect(self.MSMapIncrease)
        # self.comboBox_MultiSwitch.clicked.connect(self.retranslateUi)
        # self.comboBox_MultiSwitch.activated.connect(self.retranslateUi)
        
        self.pushButtonLoadConfig.clicked.connect(self.LoadConfig)
        self.pushButtonSaveConfig.clicked.connect(self.SaveConfig)
        self.pushButtonSetiRPath.clicked.connect(self.SetiRPath)
        self.pushButtonSetTelemPath.clicked.connect(self.SetTelemPath)

        self.pushButton_MSDriverMarker.clicked.connect(self.assignDriverMarker)
        self.pushButtonPreviousMulti.clicked.connect(self.assignButtonPreviousMulti)
        self.pushButtonNextMulti.clicked.connect(self.assignButtonNextMulti)
        self.pushButtonMultiDecrease.clicked.connect(self.assignButtonMultiDecrease)
        self.pushButtonMultiIncrease.clicked.connect(self.assignButtonMultiIncrease)
        self.pushButtonSaveDDUPage.clicked.connect(self.assignButtonDDUPage)
        
        self.doubleSpinBox_tLiftReaction.valueChanged.connect(self.setTLiftReaction)
        self.doubleSpinBox_tLiftGap.valueChanged.connect(self.setTLift)
        self.doubleSpinBox_VFuelTGT.valueChanged.connect(self.setVFuelTgt)
        self.comboBox_NFuelConsumptionMethod.currentIndexChanged.connect(self.NFuelConsumptionMethod)
        self.comboBox_NFuelManagement.currentIndexChanged.connect(self.NFuelTargetMethod)

        # finish = self.iDDU.closeEvent()
        # QtCore.QMetaObject.connectSlotsByName(iDDU)
        # app.aboutToQuit.connect(self.closeEvent)
        #
        # finish = QtWidgets.QAction("Quit", self.iDDU)
        # finish.triggered.connect(self.closeEvent)

        self.retranslateUi(iDDU)
        self.tabWidget.setCurrentIndex(0)
        self.comboBox.setCurrentIndex(0)
        self.comboBox_NFuelConsumptionMethod.setCurrentIndex(0)
        self.comboBox_NFuelManagement.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(iDDU)
        self.UpshiftStrategy()

    def retranslateUi(self, iDDU):
        _translate = QtCore.QCoreApplication.translate
        iDDU.setWindowTitle(_translate("iDDU", "iDDU"))
        self.groupBox_2.setTitle(_translate("iDDU", "DDU"))
        self.pushButton_StartDDU.setText(_translate("iDDU", "Start DDU"))
        self.pushButton_StopDDU.setText(_translate("iDDU", "Stop DDU"))
        self.groupBox_3.setTitle(_translate("iDDU", "General"))
        self.label_8.setText(_translate("iDDU", "Race Laps"))
        self.label_14.setText(_translate("iDDU", "DRS Activations"))
        self.checkBox_MapHighlight.setText(_translate("iDDU", "activate Delta on Map"))
        self.label_15.setText(_translate("iDDU", "P2P Activations"))
        self.label_NStintLaps.setText(_translate("iDDU", "Stint Laps"))
        self.groupBox_5.setTitle(_translate("iDDU", "RallyX"))
        self.label_13.setText(_translate("iDDU", "Required Joker Laps"))
        self.label_12.setText(_translate("iDDU", "Joker Lap Delta"))
        self.groupBox_7.setTitle(_translate("iDDU", "Track"))
        self.pushButtonTrackRotateLeft.setText(_translate("iDDU", "Rotate Left"))
        self.pushButtonTrackRotateRight.setText(_translate("iDDU", "Rotate Right"))
        self.pushButtonLoadTrack.setText(_translate("iDDU", "Load"))
        self.pushButtonSaveTrack.setText(_translate("iDDU", "Save"))
        self.pushButtonLoadReferenceLap.setText(_translate("iDDU", "Load Reference Lap"))
        self.groupBox_8.setTitle(_translate("iDDU", "Logging"))
        self.checkBox_BEnableLogger.setText(_translate("iDDU", "enable Logger"))
        self.checkBox_BEnableLapLogging.setText(_translate("iDDU", "enable  end of lap logging"))
        self.groupBox_11.setTitle(_translate("iDDU", "Multi Switch"))
        self.pushButton_MSMapDecrease.setText(_translate("iDDU", "Map Decrease"))
        self.pushButton_MSMapIncrease.setText(_translate("iDDU", "Map Increase"))
        self.pushButton_MSDriverMarker.setText(_translate("iDDU", "assign Driver Marker"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabGeneral), _translate("iDDU", "General"))
        self.label_10.setText(_translate("iDDU", "Pit Stop Delta"))
        self.checkBox_ChangeTyres.setText(_translate("iDDU", "Change Tyres"))
        self.label_17.setText(_translate("iDDU", "User fuel pre set"))
        self.label_16.setText(_translate("iDDU", "Pit stop fuel setting"))
        self.checkBox_FuelUp.setText(_translate("iDDU", "Fuel up"))
        self.label_11.setText(_translate("iDDU", "Required Pit Stops"))
        self.comboBox_FuelMethod.setItemText(0, _translate("iDDU", "User pre set"))
        self.comboBox_FuelMethod.setItemText(1, _translate("iDDU", "calculated"))
        self.checkBox_PitCommandControl.setText(_translate("iDDU", "iDDU has control over pit commands"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabPitStops), _translate("iDDU", "Pit Stops"))
        self.groupBox.setTitle(_translate("iDDU", "Upshift RPM"))
        self.groupBox_Gear1.setTitle(_translate("iDDU", "Gear 1"))
        self.label.setText(_translate("iDDU", "RPM"))
        self.checkBox_Gear1.setText(_translate("iDDU", "active"))
        self.groupBox_Gear2.setTitle(_translate("iDDU", "Gear 2"))
        self.label_2.setText(_translate("iDDU", "RPM"))
        self.checkBox_Gear2.setText(_translate("iDDU", "active"))
        self.groupBox_Gear3.setTitle(_translate("iDDU", "Gear 3"))
        self.label_3.setText(_translate("iDDU", "RPM"))
        self.checkBox_Gear3.setText(_translate("iDDU", "active"))
        self.groupBox_Gear4.setTitle(_translate("iDDU", "Gear 4"))
        self.label_4.setText(_translate("iDDU", "RPM"))
        self.checkBox_Gear4.setText(_translate("iDDU", "active"))
        self.groupBox_Gear2_4.setTitle(_translate("iDDU", "Gear 5"))
        self.label_5.setText(_translate("iDDU", "RPM"))
        self.checkBox_Gear5.setText(_translate("iDDU", "active"))
        self.groupBox_Gear6.setTitle(_translate("iDDU", "Gear 6"))
        self.label_6.setText(_translate("iDDU", "RPM"))
        self.checkBox_Gear6.setText(_translate("iDDU", "active"))
        self.groupBox_Gear7.setTitle(_translate("iDDU", "Gear 7"))
        self.label_7.setText(_translate("iDDU", "RPM"))
        self.checkBox_Gear7.setText(_translate("iDDU", "active"))
        self.groupBox_6.setTitle(_translate("iDDU", "Strategy"))
        self.saveButton.setText(_translate("iDDU", "Save"))
        self.label_9.setText(_translate("iDDU", "Upshift RPM Source"))
        self.checkBox_UpshiftTone.setText(_translate("iDDU", "activate Upshift Tone"))
        self.openButton.setText(_translate("iDDU", "Load"))
        self.comboBox.setItemText(0, _translate("iDDU", "iRacing First RPM"))
        self.comboBox.setItemText(1, _translate("iDDU", "iRacing Shift RPM"))
        self.comboBox.setItemText(2, _translate("iDDU", "iRacing Last RPM"))
        self.comboBox.setItemText(3, _translate("iDDU", "iRacing Blink RPM"))
        self.comboBox.setItemText(4, _translate("iDDU", "User defined"))
        self.comboBox.setItemText(5, _translate("iDDU", "from Car properties"))
        self.comboBox_MultiSwitch.setMaxVisibleItems(6)
        self.comboBox.setCurrentIndex(self.db.config['UpshiftStrategy'])
        self.pushButton_calcUpshiftRPM.setText(_translate("iDDU", "Calculate Upshift RPM from data"))
        self.groupBox_10.setTitle(_translate("iDDU", "Audio Settings"))
        self.pushButton_testShiftTone.setText(_translate("iDDU", "Play Test Tone"))
        self.label_20.setText(_translate("iDDU", "Tone Frequency"))
        self.label_21.setText(_translate("iDDU", "Tone Duration"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabUpshiftTone), _translate("iDDU", "Upshift Tone"))
        self.groupBox_9.setTitle(_translate("iDDU", "Configuration"))
        self.openButton_2.setText(_translate("iDDU", "Load Configuration"))
        self.calcFuelSavingButton.setText(_translate("iDDU", "Calculate fuel saving from data"))
        self.calcRollOutButton.setText(_translate("iDDU", "Calculate roll-out curves"))
        self.label_VFuelTGT.setText(_translate("iDDU", "Consumption Target"))
        self.comboBox_NFuelConsumptionMethod.setItemText(0, _translate("iDDU", "Average Laps"))
        self.comboBox_NFuelConsumptionMethod.setItemText(1, _translate("iDDU", "Last 3 Laps"))
        self.comboBox_NFuelConsumptionMethod.setItemText(2, _translate("iDDU", "Reference Lap"))
        self.label_NFuelConsumptionMethod.setText(_translate("iDDU", "Fuel Consumption Calculation Method"))
        self.comboBox_NFuelManagement.setItemText(0, _translate("iDDU", "Off"))
        self.comboBox_NFuelManagement.setItemText(1, _translate("iDDU", "Static Target"))
        self.comboBox_NFuelManagement.setItemText(2, _translate("iDDU", "End of Race"))
        self.comboBox_NFuelManagement.setItemText(3, _translate("iDDU", "End of Stint"))
        self.groupBox_4.setTitle(_translate("iDDU", "Audio Settings"))
        self.pushButton_testFuelTone.setText(_translate("iDDU", "Play Test Tone"))
        self.label_FuelToneFrequency.setText(_translate("iDDU", "Tone Frequency"))
        self.label_FuelToneDuration.setText(_translate("iDDU", "Tone Duration"))
        self.label_tLiftReaction.setText(_translate("iDDU", "Lift Reaction Time"))
        self.label_tLiftGap.setText(_translate("iDDU", "Gap between Lift Tones"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabFuelManagement), _translate("iDDU", "Fuel Management"))
        self.pushButtonInvoke.setText(_translate("iDDU", "Invoke Command"))
        self.pushButtonSaveSnapshot.setText(_translate("iDDU", "RTDB Snapshot"))
        self.pushButtonLoadSnapshot.setText(_translate("iDDU", "Load Snapshot"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabDebug), _translate("iDDU", "Debug"))
        self.checkBox_MapHighlight.setChecked(self.db.config['MapHighlight'])
        self.pushButtonSaveConfig.setText(_translate("iDDU", "Save Settings"))
        self.pushButtonLoadConfig.setText(_translate("iDDU", "Load Settings"))
        self.label_22.setText(_translate("iDDU", "iRacing Path:"))
        self.label_23.setText(_translate("iDDU", "Telemetry Path:"))
        self.lineEditiRPath.setText(_translate("iDDU", self.db.config['iRPath']))
        self.lineEditTelemPath.setText(_translate("iDDU", self.db.config['TelemPath']))
        self.pushButtonSetiRPath.setText(_translate("iDDU", "Set iRacing Path"))
        self.pushButtonSetTelemPath.setText(_translate("iDDU", "Set Telemetry Path"))
        self.groupBox_12.setTitle(_translate("iDDU", "Button assignments"))
        self.pushButtonSaveDDUPage.setText(_translate("iDDU", "Change DDU Page"))
        self.pushButtonPreviousMulti.setText(_translate("iDDU", "Previous Multi Position"))
        self.pushButtonNextMulti.setText(_translate("iDDU", "Next Multi Position"))
        self.pushButtonMultiDecrease.setText(_translate("iDDU", "Decrease Multi Value"))
        self.pushButtonMultiIncrease.setText(_translate("iDDU", "Increase Multi Value"))
        self.label_24.setText(_translate("iDDU", "Select Joystick"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabSettings), _translate("iDDU", "Settings"))

        self.spinBoxRaceLaps.setValue(self.db.config['UserRaceLaps'])
        self.checkBox_BEnableLogger.setChecked(self.db.config['BLoggerActive'])
        self.checkBox_BEnableLapLogging.setChecked(self.db.config['BEnableLapLogging'])
        self.checkBox_FuelUp.setChecked(self.db.config['BBeginFueling'])
        self.checkBox_ChangeTyres.setChecked(self.db.config['BChangeTyres'])
        self.checkBox_PitCommandControl.setChecked(self.db.config['BPitCommandControl'])
        self.comboBox_FuelMethod.setCurrentIndex(self.db.config['NFuelSetMethod'])
        self.checkBox_UpshiftTone.setChecked(self.db.config['ShiftToneEnabled'])
        self.comboBox_NFuelConsumptionMethod.setCurrentIndex(self.db.config['NFuelConsumptionMethod'])
        self.comboBox_NFuelManagement.setCurrentIndex(self.db.config['NFuelTargetMethod'])

        self.lineEditDDUPage.setText('Device: {} | Button: {}'.format(self.db.config['ButtonAssignments']['DDUPage']['Joystick'], self.db.config['ButtonAssignments']['DDUPage']['Button']))
        self.lineEditNextMulti.setText('Device: {} | Button: {}'.format(self.db.config['ButtonAssignments']['NextMulti']['Joystick'], self.db.config['ButtonAssignments']['NextMulti']['Button']))
        self.lineEditPreviousMulti.setText('Device: {} | Button: {}'.format(self.db.config['ButtonAssignments']['PreviousMulti']['Joystick'], self.db.config['ButtonAssignments']['PreviousMulti']['Button']))
        self.lineEditMultiDecrease.setText('Device: {} | Button: {}'.format(self.db.config['ButtonAssignments']['MultiDecrease']['Joystick'], self.db.config['ButtonAssignments']['MultiDecrease']['Button']))
        self.lineEditMultiIncrease.setText('Device: {} | Button: {}'.format(self.db.config['ButtonAssignments']['MultiIncrease']['Joystick'], self.db.config['ButtonAssignments']['MultiIncrease']['Button']))

        dcList = list(self.db.car.dcList.keys())
        k = 0

        for i in range(0, len(dcList)):
            if self.db.car.dcList[dcList[i]][1]:                
                # self.comboBox_MultiSwitch.addItem(dcList[i])
                self.comboBox_MultiSwitch.setItemText(k, _translate("iDDU", dcList[i]))
                k += 1

        self.comboBox_MultiSwitch.setMaxVisibleItems(len(list(dict(self.dcConfig))))
        # self.comboBox_MultiSwitch.setCurrentIndex(0)

        for i in range(0, len(self.joystickList)):
            self.comboBox_JoystickSelection.setItemText(i, _translate("iDDU", self.joystickList[i]))

        self.comboBox_JoystickSelection.setMaxVisibleItems(len(self.joystickList)+5)

    def assignRaceLaps(self):
        # self.db.LapsToGo = self.spinBoxRaceLaps.value()
        self.db.config['UserRaceLaps'] = self.spinBoxRaceLaps.value()
        # self.db.config['RaceLaps'] = self.spinBoxRaceLaps.value()
        self.retranslateUi(self.iDDU)

    def assignDRS(self):
        if self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionType'] == 'Race':
            self.db.config['DRSActivations'] = self.doubleSpinBox_DRSActivations.value()
        self.db.config['DRSActivationsGUI'] = self.doubleSpinBox_DRSActivations.value()
        self.retranslateUi(self.iDDU)

    def assignJokerDelta(self):
        self.db.config['JokerLapDelta'] = self.doubleSpinBox_JokerLapDelta.value()
        self.retranslateUi(self.iDDU)

    def MapHighlight(self):
        self.db.config['MapHighlight'] = self.checkBox_MapHighlight.isChecked()
        self.retranslateUi(self.iDDU)

    def assignJokerLaps(self):
        self.db.config['JokerLapsRequired'] = self.doubleSpinBox_JokerLapsRequired.value()
        self.retranslateUi(self.iDDU)

    def assignP2P(self):
        if self.db.SessionInfo['Sessions'][self.db.SessionNum]['SessionType'] == 'Race':
            self.db.config['P2PActivations'] = self.doubleSpinBox_P2PActivations.value()
        self.db.config['P2PActivationsGUI'] = self.doubleSpinBox_P2PActivations.value()
        self.retranslateUi(self.iDDU)

    def assignPitStopDelta(self):
        self.db.config['PitStopDelta'] = self.doubleSpinBox_PitStopDelta.value()
        self.retranslateUi(self.iDDU)

    def assignPitStopsRequired(self):
        self.db.config['PitStopsRequired'] = self.doubleSpinBox_PitStopsRequired.value()
        self.retranslateUi(self.iDDU)

    def UpshiftStrategy(self):
        self.db.config['UpshiftStrategy'] = self.comboBox.currentIndex()
        self.db.config['UserShiftRPM'] = [self.spinBox_Gear1.value(), self.spinBox_Gear2.value(), self.spinBox_Gear3.value(), self.spinBox_Gear4.value(), self.spinBox_Gear5.value(), self.spinBox_Gear6.value(),
                                self.spinBox_Gear7.value()]
        self.db.config['UserShiftFlag'] = [self.checkBox_Gear1.isChecked(), self.checkBox_Gear2.isChecked(), self.checkBox_Gear3.isChecked(), self.checkBox_Gear4.isChecked(), self.checkBox_Gear5.isChecked(),
                                 self.checkBox_Gear6.isChecked(), self.checkBox_Gear7.isChecked()]
        self.retranslateUi(self.iDDU)

    def EnableShiftTone(self):
        self.db.config['ShiftToneEnabled'] = self.checkBox_UpshiftTone.isChecked()
        self.retranslateUi(self.iDDU)

    def InvokeUserCommand(self):
        try:
            cmd = self.lineEditInvoke.text()
            print(self.db.timeStr + ": >> " + cmd)
            if "=" in cmd:
                exec(cmd)
                outstr = cmd.split('=')
                print(self.db.timeStr + ': ' + str(eval(outstr[0])))
            else:
                print(self.db.timeStr + ': ' + str(eval(cmd)))
        except:
            print(self.db.timeStr + ': User command not working!')

        self.retranslateUi(self.iDDU)

    def onUpdateText(self, text):
        cursor = self.textEdit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.textEdit.setTextCursor(cursor)
        self.textEdit.ensureCursorVisible()

    def StartDDU(self):
        self.db.StartDDU = True

    def StopDDU(self):
        self.db.StopDDU = True

    def saveShiftToneSettings(self):

        SaveFileName = QFileDialog.getSaveFileName(self.iDDU, 'Save Shift Tone File', './data/shiftTone', 'CSV(*.csv)')

        if SaveFileName == ('', ''):
            print(time.strftime("%H:%M:%S", time.localtime()) + ':\tNo valid path to CSV file provided...aborting!')
            return

        with open(SaveFileName[0], 'w', newline='') as f:
            thewriter = csv.writer(f)
            for l in range(0, 7):
                thewriter.writerow([self.db.config['UserShiftRPM'][l], self.db.config['UserShiftFlag'][l], self.db.config['UpshiftStrategy']])

        print(self.db.timeStr + ': Saved Shift Tone settings to: ' + SaveFileName[0])

    def loadShiftToneSettings(self):
        OpenFileName = QFileDialog.getOpenFileName(self.iDDU, 'Load Shift Tone File', './data/shiftTone', 'CSV(*.csv)')

        if OpenFileName == ('', ''):
            print(time.strftime("%H:%M:%S", time.localtime()) + ':\tNo valid path to CSV file provided...aborting!')
            return

        i = 0
        UserShiftRPM = [0, 0, 0, 0, 0, 0, 0]
        UserShiftFlag = [0, 0, 0, 0, 0, 0, 0]

        with open(OpenFileName[0]) as csv_file:
            csv_reader = csv.reader(csv_file)
            for line in csv_reader:
                UserShiftRPM[i] = float(line[0])
                UserShiftFlag[i] = eval(line[1])
                UpshiftStrategy = int(line[2])
                i = i + 1

        csv_file.close()

        self.checkBox_Gear1.setChecked(UserShiftFlag[0])
        self.checkBox_Gear2.setChecked(UserShiftFlag[1])
        self.checkBox_Gear3.setChecked(UserShiftFlag[2])
        self.checkBox_Gear4.setChecked(UserShiftFlag[3])
        self.checkBox_Gear5.setChecked(UserShiftFlag[4])
        self.checkBox_Gear6.setChecked(UserShiftFlag[5])
        self.checkBox_Gear7.setChecked(UserShiftFlag[6])

        self.spinBox_Gear1.setValue(UserShiftRPM[0])
        self.spinBox_Gear2.setValue(UserShiftRPM[1])
        self.spinBox_Gear3.setValue(UserShiftRPM[2])
        self.spinBox_Gear4.setValue(UserShiftRPM[3])
        self.spinBox_Gear5.setValue(UserShiftRPM[4])
        self.spinBox_Gear6.setValue(UserShiftRPM[5])
        self.spinBox_Gear7.setValue(UserShiftRPM[6])

        self.comboBox.setCurrentIndex(UpshiftStrategy)

        self.db.config['UserShiftFlag'] = UserShiftFlag
        self.db.config['UserShiftRPM'] = UserShiftRPM
        self.db.config['UpshiftStrategy'] = UpshiftStrategy

        print(self.db.timeStr + ': Loaded Shift Tone settings from: ' + OpenFileName[0])

        self.retranslateUi(self.iDDU)

    def loadRTDBSnapshot(self):
        OpenFileName = QFileDialog.getOpenFileName(self.iDDU, 'Load Track JSON file', './data/snapshots', 'JSON(*.json)')

        if OpenFileName == ('', ''):
            print(time.strftime("%H:%M:%S", time.localtime()) + ':\tNo valid path to RTDB snapshot file provided...aborting!')
            return

        OpenFileName = OpenFileName[0].split('/')
        OpenFileName = OpenFileName[-1]
        OpenFileName = OpenFileName.split('.')
        self.db.loadSnapshot(OpenFileName[0])

    def saveRTDBSnapshot(self):
        self.db.snapshot()

    def rotateTrackLeft(self):
        self.db.track.rotate(-5/180*3.142)

    def rotateTrackRight(self):
        self.db.track.rotate(5/180*3.142)

    def saveTrack(self):
        self.db.track.save(self.db.dir)

    def enableLogger(self):
        self.db.config['BLoggerActive'] = self.checkBox_BEnableLogger.isChecked()
        self.retranslateUi(self.iDDU)

    def enableLapLogging(self):
        self.db.config['BEnableLapLogging'] = self.checkBox_BEnableLapLogging.isChecked()
        self.retranslateUi(self.iDDU)

    def loadTrack(self):
        OpenFileName = QFileDialog.getOpenFileName(self.iDDU, 'Load Track JSON file', './data/track', 'JSON(*.json)')

        if OpenFileName == ('', ''):
            print(time.strftime("%H:%M:%S", time.localtime()) + ':\tNo valid path to track file provided...aborting!')
            return

        NDDUPageTemp = self.db.NDDUPage
        BResetScreen = False
        if self.db.NDDUPage == 2:
            BResetScreen = True
            self.db.NDDUPage = 1
            time.sleep(0.2)

        self.db.track = Track.Track('default')
        self.db.track.load(OpenFileName[0])

        if BResetScreen:
            self.db.NDDUPage = NDDUPageTemp

    def loadReferenceLap(self):
        print(time.strftime("%H:%M:%S", time.localtime()) + ':\tImporting reference lap')

        ibtPath = QFileDialog.getOpenFileName(self.iDDU, 'Load IBT file', self.db.config['TelemPath'], 'IBT(*.ibt)')

        if ibtPath == ('', ''):
            print(time.strftime("%H:%M:%S", time.localtime()) + ':\t\tNo valid path to ibt file provided...aborting!')
            return

        d, _ = importIBT.importIBT(ibtPath[0],
                                   lap='f',
                                   channels=['zTrack', 'LapDistPct', 'rThrottle', 'rBrake', 'QFuel', 'SessionTime', 'VelocityX', 'VelocityY', 'Yaw', 'Gear', 'YawNorth'],
                                   channelMapPath=self.db.dir + '/functionalities/libs/iRacingChannelMap.csv')

        if not d:
            print(time.strftime("%H:%M:%S", time.localtime()) + ':\t\tNo valid lap found...aborting!')
            return

        d['x'], d['y'] = maths.createTrack(d)

        tempDB = RTDB.RTDB()
        tempDB.initialise(d, False, False)

        # check if car available
        carList = importExport.getFiles(self.db.dir + '/data/car', 'json')
        carName = d['DriverInfo']['Drivers'][tempDB.DriverInfo['DriverCarIdx']]['CarScreenNameShort']
        carPath = d['DriverInfo']['Drivers'][tempDB.DriverInfo['DriverCarIdx']]['CarPath']

        # load or create car
        if carName + '.json' in carList:
            self.db.car.load("data/car/" + carName + '.json')
        else:
            self.db.car = Car.Car(Driver=d['DriverInfo']['Drivers'][tempDB.DriverInfo['DriverCarIdx']])
            self.db.car.createCar(tempDB)
            self.db.car.save(self.db.dir)
            print(time.strftime("%H:%M:%S", time.localtime()) + ':\tCar has been successfully created')

        # create track
        TrackName = d['WeekendInfo']['TrackName']
        track = Track.Track(TrackName)
        aNorth = d['YawNorth'][0]
        track.createTrack(d['x'], d['y'], d['LapDistPct']*100, aNorth, float(d['WeekendInfo']['TrackLength'].split(' ')[0])*1000)
        track.save(self.db.dir)

        print(time.strftime("%H:%M:%S", time.localtime()) + ':\t\tTrack {} has been successfully created.'.format(TrackName))

        self.db.track.load(self.db.dir + '/data/track/' + TrackName + '.json')

        print(time.strftime("%H:%M:%S", time.localtime()) + ':\t\tAdding reference lap time to car {}'.format(self.db.car.name))

        # add lap time to car
        if maths.strictly_increasing(d['tLap']) and maths.strictly_increasing(d['LapDistPct']):
            self.db.car.addLapTime(TrackName, d['tLap'], d['LapDistPct']*100, track.LapDistPct, d['VFuelLap'])
            self.db.car.save(self.db.dir)
            print(time.strftime("%H:%M:%S", time.localtime()) + ':\t\tReference lap time set successfully!')
        else:
            print(time.strftime("%H:%M:%S", time.localtime()) + ':\t\tRecorded Laptime is not monotonically increasing. Aborted track creation!')

    def setUserFuelPreset(self):
        self.db.config['VUserFuelSet'] = self.spinBox_FuelSetting.value()
        self.db.BPitCommandUpdate = True
        self.retranslateUi(self.iDDU)

    def enableFuelUp(self):
        self.db.config['BBeginFueling'] = self.checkBox_FuelUp.isChecked()
        self.db.BPitCommandUpdate = True
        self.retranslateUi(self.iDDU)

    def setPitCommandControl(self):
        self.db.config['BPitCommandControl'] = self.checkBox_PitCommandControl.isChecked()
        self.db.BPitCommandUpdate = True
        self.retranslateUi(self.iDDU)

    def enableTyreChange(self):
        self.db.config['BChangeTyres'] = self.checkBox_ChangeTyres.isChecked()
        self.db.BPitCommandUpdate = True
        self.retranslateUi(self.iDDU)

    def setFuelSetMethod(self):
        self.db.config['NFuelSetMethod'] = self.comboBox_FuelMethod.currentIndex()
        self.db.BPitCommandUpdate = True
        self.retranslateUi(self.iDDU)

    def FuelBeep(self):
        self.db.config['tFuelBeep'] = self.spinBox_FuelToneDuration.value()
        self.db.config['fFuelBeep'] = self.spinBox_FuelToneFrequency.value()
        self.retranslateUi(self.iDDU)

    def ShiftBeep(self):
        self.db.config['tShiftBeep'] = self.spinBox_ShiftToneDuration.value()
        self.db.config['fShiftBeep'] = self.spinBox_ShiftToneFrequency.value()
        self.retranslateUi(self.iDDU)

    def testFuelTone(self):
        winsound.Beep(self.db.config['fFuelBeep'], self.db.config['tFuelBeep'])
        time.sleep(self.db.config['tLiftGap'] - self.db.config['tFuelBeep'] / 1000)
        winsound.Beep(self.db.config['fFuelBeep'], self.db.config['tFuelBeep'])
        time.sleep(self.db.config['tLiftGap'] - self.db.config['tFuelBeep'] / 1000)
        winsound.Beep(self.db.config['fFuelBeep'], self.db.config['tFuelBeep'])

    def testShiftTone(self):
        winsound.Beep(self.db.config['fShiftBeep'], self.db.config['tShiftBeep'])

    def loadFuelManagementSettings(self):
        OpenFileName = QFileDialog.getOpenFileName(self.iDDU, 'Load Fuel Management Configuration', './data/fuelSaving', 'JSON(*.json)')

        if OpenFileName == ('', ''):
            print(time.strftime("%H:%M:%S", time.localtime()) + ':\tNo valid path to fuel saving file provided...aborting!')
            return

        self.db.loadFuelTgt(OpenFileName[0])

        self.doubleSpinBox_VFuelTGT.setMinimum(np.min(self.db.FuelTGTLiftPoints['VFuelTGT']))
        self.doubleSpinBox_VFuelTGT.setMaximum(np.max(self.db.FuelTGTLiftPoints['VFuelTGT']))
        self.doubleSpinBox_VFuelTGT.setProperty("value", self.db.config['VFuelTgt'])
        
        self.retranslateUi(self.iDDU)
    
    def setVFuelTgt(self):
        self.db.config['VFuelTgt'] = self.doubleSpinBox_VFuelTGT.value()
        self.retranslateUi(self.iDDU)

    def calcUpshiftRPM(self):
        getShiftRPM.getShiftRPM(self.db.dir, self.db.config['TelemPath'])
        self.retranslateUi(self.iDDU)

    def calcFuelSaving(self):
        fuelSavingOptimiser.optimise(self.db.dir, self.db.config['TelemPath'])
        self.retranslateUi(self.iDDU)

    def calcRollOut(self):
        rollOut.getRollOutCurve(self.db.dir, self.db.config['TelemPath'])
        self.retranslateUi(self.iDDU)

    def MSMapDecrease(self):
        mapName = self.comboBox_MultiSwitch.currentText()
        self.pressButton(self.dcConfig[mapName][0]+1, 0.2)
        self.retranslateUi(self.iDDU)

    def MSMapIncrease(self):
        mapName = self.comboBox_MultiSwitch.currentText()
        self.pressButton(self.dcConfig[mapName][1]+1, 0.2)
        self.retranslateUi(self.iDDU)

    def assignDriverMarker(self):
        self.pressButton(64, 0.2)

    def getJoystickControl(self):
        WaitingForEvent = True
        t = time.time()
        self.initJoystick(self.joystickList[self.comboBox_JoystickSelection.currentIndex()])

        self.pygame.display.get_init()

        while WaitingForEvent and (time.time()-t) < 10:
            events = self.pygame.event.get()
            for event in events:
                if event.type == self.pygame.JOYBUTTONDOWN:
                    WaitingForEvent = False
                    print('Joystick: ' + str(event.joy))
                    print('Button: ' + str(event.button))

        if WaitingForEvent:
            print(time.strftime("%H:%M:%S", time.localtime()) + ':\tNo valid Joystick input found....aborting!')
        else:
            print(time.strftime("%H:%M:%S", time.localtime()) + ':\tAssigned button {} of Joystick {}!'.format(event.button, event.joy))

        return self.pygame.joystick.Joystick(event.joy).get_name(), event.button

    def assignButtonPreviousMulti(self):
        self.assignButton('PreviousMulti')

    def assignButtonNextMulti(self):
        self.assignButton('NextMulti')

    def assignButtonMultiIncrease(self):
        self.assignButton('MultiIncrease')

    def assignButtonMultiDecrease(self):
        self.assignButton('MultiDecrease')

    def assignButtonDDUPage(self):
        self.assignButton('DDUPage')

    def assignButton(self, name):
        joyID, joyButton = self.getJoystickControl()
        self.db.config['ButtonAssignments'][name]['Joystick'] = joyID
        self.db.config['ButtonAssignments'][name]['Button'] = joyButton
        self.SaveConfig()

    def LoadConfig(self):
        config = importExport.loadJson(self.db.dir + '/data/configs/config.json')
        self.db.initialise({'config': config}, False, False)
        self.retranslateUi(self.iDDU)

    def SaveConfig(self):
        importExport.saveJson(self.db.config, self.db.dir + '/data/configs/config.json')
        self.retranslateUi(self.iDDU)

    def refreshGUI(self):
        self.retranslateUi(self.iDDU)

        if self.db.IsOnTrack:
            self.iDDU.qTimer.setInterval(30000)
        else:
            self.iDDU.qTimer.setInterval(500)

    def SetiRPath(self):
        dirPath = QFileDialog.getExistingDirectory(self.iDDU, 'Select iRacing Directory', './')

        if dirPath == '':
            return

        self.db.config['iRPath'] = dirPath
        self.SaveConfig()

    def SetTelemPath(self):
        dirPath = QFileDialog.getExistingDirectory(self.iDDU, 'Select Telemetry Data Directory', './')

        if dirPath == '':
            return

        self.db.config['TelemPath'] = dirPath
        self.SaveConfig()

    def setTLift(self):
        tLiftGap = self.doubleSpinBox_tLiftGap.value()
        self.db.config['tLiftGap'] = tLiftGap
        self.db.tLiftTones = [2*tLiftGap, tLiftGap, 0]
        self.retranslateUi(self.iDDU)

    def setTLiftReaction(self):
        self.db.config['tReactionLift'] = self.doubleSpinBox_tLiftReaction.value()
        self.retranslateUi(self.iDDU)

    def NFuelConsumptionMethod(self):
        self.db.config['NFuelConsumptionMethod'] = self.comboBox_NFuelConsumptionMethod.currentIndex()
        self.retranslateUi(self.iDDU)

    def NFuelTargetMethod(self):
        self.db.config['NFuelTargetMethod'] = self.comboBox_NFuelManagement.currentIndex()
        self.retranslateUi(self.iDDU)

    def __del__(self):
        sys.stdout = sys.__stdout__
