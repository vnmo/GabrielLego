#!/usr/bin/env python
from __future__ import absolute_import, division, print_function

import os  # For listing directory methods
import pdb
import re
import sys  # We need sys so that we can pass argv to QApplication
import threading

import numpy as np
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import SIGNAL, QThread, pyqtSignal, QString
from PyQt4.QtGui import QImage, QMessageBox, QPixmap, QVBoxLayout

import client
import design  # This file holds our MainWindow and all design related things
import fire


class UI(QtGui.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)  # This is defined in design.py file automatically

    @staticmethod
    def set_label_image(frame, label):
        img = QImage(
            frame, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888)
        pix = QPixmap.fromImage(img)
        label.setPixmap(pix)

    def set_feed_image(self, frame):
        UI.set_label_image(frame, self.feed_label)

    def set_guidance_image(self, frame):
        UI.set_label_image(frame, self.guidance_label)

    def set_guidance_text(self, instruction):
        self.instruction_label.setText(QString(instruction))


class ClientThread(QThread):
    sig_feed_available = pyqtSignal(object)
    sig_instruction_available = pyqtSignal(str)
    sig_guidance_available = pyqtSignal(object)

    def __init__(self, ip):
        super(self.__class__, self).__init__()
        self._stop = threading.Event()
        self.ip = ip

    def run(self):
        client.run(sig_feed_available=self.sig_feed_available,
                   sig_instruction_available=self.sig_instruction_available,
                   sig_guidance_available=self.sig_guidance_available,
                   ui=True,
                   ip=self.ip)

    def stop(self):
        client.alive = False
        self._stop.set()


def main(ip, *args, **kwargs):
    app = QtGui.QApplication(sys.argv)
    ui = UI()
    ui.show()
    clientThread = ClientThread(ip)
    clientThread.sig_feed_available.connect(ui.set_feed_image)
    clientThread.sig_instruction_available.connect(ui.set_guidance_text)
    clientThread.finished.connect(app.exit)
    clientThread.start()

    sys.exit(app.exec_())  # and execute the app


if __name__ == '__main__':  # if we're running file directly and not
    # importing it
    fire.Fire(main)
