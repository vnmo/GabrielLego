#!/usr/bin/env python
from __future__ import absolute_import, division, print_function

import logging
import sys  # We need sys so that we can pass argv to QApplication
import threading
import time

import fire
import logzero
from PyQt4 import QtGui
from PyQt4.QtCore import QString, QThread, pyqtSignal, Qt
from PyQt4.QtGui import QImage, QPixmap

import client
import design  # This file holds our MainWindow and all design related things


class UI(QtGui.QMainWindow, design.Ui_MainWindow):
    start_signal = pyqtSignal()

    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)  # This is defined in design.py file automatically
        self.started = False
        self.set_guidance_text('Press Enter to begin.')

    def keyPressEvent(self, event):
        super(self.__class__, self).keyPressEvent(event)
        if not self.started and (
                event.key() == Qt.Key_Enter or
                event.key() == Qt.Key_Return
        ):
            self.started = True
            self.start_signal.emit()

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

    def __init__(self, ip, countdown_from=10):
        super(self.__class__, self).__init__()
        self._stop = threading.Event()
        self.ip = ip
        self.countdown_from = countdown_from

    def run(self):
        # countdown before starting the experiment
        for i in range(self.countdown_from, 0, -1):
            ti = time.time()
            self.sig_instruction_available.emit('{}'.format(i))
            time.sleep(max(1.0 - (time.time() - ti), 0))

        self.sig_instruction_available.emit('')
        client.run(sig_feed_available=self.sig_feed_available,
                   sig_instruction_available=self.sig_instruction_available,
                   sig_guidance_available=self.sig_guidance_available,
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
    clientThread.sig_guidance_available.connect(ui.set_guidance_image)
    clientThread.sig_instruction_available.connect(ui.set_guidance_text)
    clientThread.finished.connect(app.exit)

    ui.start_signal.connect(clientThread.start)

    # clientThread.start()
    sys.exit(app.exec_())  # and execute the app


if __name__ == '__main__':  # if we're running file directly and not
    # importing it
    logzero.loglevel(logging.INFO)
    fire.Fire(main)
