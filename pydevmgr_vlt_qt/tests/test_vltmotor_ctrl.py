from pydevmgr_vlt_qt import VltMotorCtrl
from pydevmgr_vlt import VltMotor
from pydevmgr_core import Downloader

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5 import  QtCore


if __name__=="__main__":
    app = QApplication(sys.argv)
    devLinker = VltMotorCtrl(show_ignore_check_box=False)
    devLinker.widget.show()
    downloader = Downloader()
    
    motor = VltMotor('motor1', address="opc.tcp://192.168.1.11:4840", prefix="MAIN.Motor001")#.from_cfgfile("tins/motor1.yml", "motor1", key="motor1")
    
    ctrl = devLinker.connect(downloader, motor)
    
    # To refresh the gui we need a timer and connect the download method 
    timer = QtCore.QTimer()
    timer.timeout.connect(downloader.download)
    # 10Hz GUI is nice
    timer.start(100)
    
    motor.connect()
    try:
        app.exec_()
    finally:
        motor.disconnect()
