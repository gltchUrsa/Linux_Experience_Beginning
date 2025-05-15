import sys
import subprocess
import time
import os
import glob
from PyQt5.QtWidgets import QApplication, QPushButton
from PyQt5.QtCore import Qt, QTimer, QRectF
from PyQt5.QtGui import QFont, QPainter, QBrush, QColor, QPen

class FloatingButton(QPushButton):
    def __init__(self, screen_geometry):
        super().__init__()
        self.screen_geometry = screen_geometry
        self.setFixedSize(60, 60)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.75)  # 75% opacity

        font = QFont("Arial", 28, QFont.Bold)
        self.setFont(font)
        self.setText("↻")

        self.move_to_bottom_right()
        self.clicked.connect(self.restart_firefox)

        self.timer = QTimer()
        self.timer.timeout.connect(self.move_to_bottom_right)
        self.timer.start(1000)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = QRectF(1, 1, self.width() - 2, self.height() - 2)
        radius = self.width() / 2

        brush = QBrush(QColor(255, 255, 255))
        pen = QPen(QColor(0, 0, 0), 3)

        painter.setBrush(brush)
        painter.setPen(pen)
        painter.drawRoundedRect(rect, radius, radius)

        painter.setPen(QColor(0, 0, 0))
        painter.setFont(self.font())
        painter.drawText(rect, Qt.AlignCenter, self.text())

    def move_to_bottom_right(self):
        geom = self.screen_geometry
        x = geom.x() + geom.width() - self.width() - 10
        y = geom.y() + geom.height() - self.height() - 10
        self.move(x, y)

    def restart_firefox(self):
        subprocess.call(['pkill', '-9', 'firefox'])
        time.sleep(0.5)

        home = os.path.expanduser("~")
        profiles_path = os.path.join(home, ".mozilla/firefox")
        for lock_file in glob.glob(os.path.join(profiles_path, "*.default-release", "lock")) + \
                         glob.glob(os.path.join(profiles_path, "*.default-release", ".parentlock")):
            try:
                os.remove(lock_file)
            except FileNotFoundError:
                pass

        subprocess.Popen(['firefox', '--kiosk', '--private-window', 'https://www.google.com'])

if __name__ == "__main__":
    app = QApplication(sys.argv)

    buttons = []
    for screen in app.screens():
        button = FloatingButton(screen.geometry())
        button.show()
        buttons.append(button)

    sys.exit(app.exec_())
