#gui libraries
import sys
import numpy as np

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QCheckBox, QStackedLayout
from PyQt5.QtGui import QDoubleValidator, QPainter, QColor
from PyQt5.QtCore import QTimer, pyqtSignal, QObject, QThread

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class ConfigWidget(QWidget):
    def __init__(self, width = 100, height = 100):
        super(ConfigWidget, self).__init__()
        self.screen_w = width
        self.screen_h = height
        self.setGeometry(100, 100, self.screen_w + 300, self.screen_h + 200)
        
        self.config = {"led_on"     : True,
                       "button_on"  : False,
                       "turn_both"  : False,
                       "resp_delay": 0,
                       "resp_duration" : 1,
                       "lock_resp" : False,}
        
        
        self.init_ui()

    def init_ui(self):
        self.setObjectName("Black Box Toolkit Config")
        self.layout = QVBoxLayout()

        self.setLayout(self.layout)
        double_validator = QDoubleValidator()
        self.check_activate_lock = QCheckBox("Disable Response")
        self.check_activate_led = QCheckBox("Activate Led")
        self.check_activate_button = QCheckBox("Activate Button")
        
        self.check_activate_led.setChecked(True)
        self.check_activate_lock.stateChanged.connect(self.on_checkbox_lock_resp)


        label_resp_delay = QLabel("Response Delay (s)")
        self.textbox_resp_delay = QLineEdit()
        self.textbox_resp_delay.setValidator(double_validator)
        self.textbox_resp_delay.setText(str(self.config["resp_delay"]))
        self.textbox_resp_delay.setEnabled(not self.config["lock_resp"])

        label_resp_duration = QLabel("Response Duration (s)")
        self.textbox_resp_duration = QLineEdit()
        self.textbox_resp_duration.setValidator(double_validator)
        self.textbox_resp_duration.setText(str(self.config["resp_duration"]))
        self.textbox_resp_duration.setEnabled(not self.config["lock_resp"])

        self.apply_button  = QPushButton("Apply", self)
        self.apply_button.clicked.connect(self.on_applied_changes)

        #self.layout.addWidget(textbox1)
        self.layout.addWidget(self.check_activate_lock)
        self.layout.addWidget(self.check_activate_led)
        self.layout.addWidget(self.check_activate_button)
        self.layout.addWidget(label_resp_delay)
        self.layout.addWidget(self.textbox_resp_delay)
        self.layout.addWidget(label_resp_duration)
        self.layout.addWidget(self.textbox_resp_duration)
        self.layout.addWidget(self.apply_button)
        self.layout.setAlignment(self.apply_button, Qt.AlignRight | Qt.AlignBottom )

        #self.show()

    def on_checkbox_lock_resp(self):

        if self.check_activate_lock.isChecked():
            "lock the textboxes"
            self.textbox_resp_duration.setEnabled(False)
            self.textbox_resp_duration.setText("0")
            self.textbox_resp_delay.setEnabled(False)
            self.textbox_resp_delay.setText("0")
            self.check_activate_led.setCheckState(False)
            self.check_activate_led.setCheckable(False)
            self.check_activate_button.setChecked(False)
            self.check_activate_button.setCheckable(False)
            self.config["lock_resp"] = True

             
        else:
            self.textbox_resp_duration.setEnabled(True)
            self.textbox_resp_delay.setEnabled(True)
            self.check_activate_led.setCheckable(True)
            self.check_activate_led.setChecked(True)
            self.check_activate_button.setCheckable(True)

            self.config["lock_resp"] = False

    def on_applied_changes(self):
        print("changes applied")
        self.config = {"led_on"        : self.check_activate_led.isChecked(),
                       "button_on"     : self.check_activate_button.isChecked(),
                       "turn_both"     : (self.check_activate_led.isChecked() and self.check_activate_button.isChecked()), 
                       "resp_delay"    : float(self.textbox_resp_delay.text()),
                       "resp_duration" : float(self.textbox_resp_duration.text()),
                       "lock_resp"     : self.check_activate_lock.isChecked()} 
        print(self.config)
        self.close()


class MainWidget(QWidget):
    def __init__(self, width = 300, height = 300):
        super(MainWidget, self).__init__()
        self.screen_w = width
        self.screen_h = height
        self.setGeometry(100, 100, self.screen_w + 300, self.screen_h + 200)
        self.ConfigWidget = ConfigWidget()
        self.config_button = QPushButton("Config", self)
        self.run_button = QPushButton("Run", self)
        self.stop_button = QPushButton("Stop", self)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.config_button)
        self.layout.addWidget(self.run_button)
        self.layout.addWidget(self.stop_button)
        self.layout.setAlignment(self.config_button, Qt.AlignRight | Qt.AlignTop )
        self.layout.setAlignment(self.run_button, Qt.AlignRight | Qt.AlignBottom )
        self.layout.setAlignment(self.stop_button, Qt.AlignRight | Qt.AlignBottom )
        self.config_button.clicked.connect(self.on_config_button)
        self.show()

    def get_config(self):
        return self.ConfigWidget.config

    def on_config_button(self):
        self.ConfigWidget.show()


class CircularButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setChecked(False)
        self.turn_off()
        self.setText("Press")
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        size = min(self.width(), self.height())
        radius = size / 2
        painter.setBrush(self.color)
        painter.drawEllipse(0, 0, size, size)

    def setColor(self, color):
        self.color = color
        self.update()
 
    def turn_on(self):
        self.setColor(QColor("blue"))
        self.setText("Pressed")

    def turn_off(self):
        self.setColor(QColor("grey"))
        self.setText("Press")

    def minimumSizeHint(self):
        return QSize(100, 100)


class CircularShape(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(20, 20)
        self._color = QColor("red")

    def setColor(self, color):
        self._color = color
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        size = min(self.width(), self.height())
        painter.setBrush(self._color)
        painter.drawEllipse(0, 0, size, size)

class VirtualBlackboxWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Virtual BlackBoxKit")
        self.circular_shape = CircularShape()
        self.button = CircularButton("OFF")
        self.button.clicked.connect(self.toggle_button)
        self.setGeometry(0,0,250, 200)
        layout = QVBoxLayout()
        layout.addWidget(self.circular_shape, alignment=Qt.AlignCenter)
        layout.addWidget(self.button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def toggle_button(self):
        if self.button.isChecked():
            self.button.setText("ON")
        else:
            self.button.setText("OFF")

        # Reset the button's checkable state
        #self.button.setChecked(False)        

    def turn_on_led(self):
        self.circular_shape.setColor(QColor("green"))
        
    def turn_off_led(self):
        self.circular_shape.setColor(QColor("red"))






class VirtualStimulatorWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Virtual Stimulator")

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        self.ax = self.figure.add_subplot(111)
        self.line, = self.ax.plot([], [], lw=2)

        self.data = []

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(100)  # Update every 100 milliseconds
    
    def load_data(self, data):
        self.data.append(data)

    def update_plot(self):
        #self.data.append(np.random.random())  # Replace with your actual data source
        
        self.line.set_data(range(len(self.data)), self.data)
        # Set fixed limits for the x and y axes
        self.ax.set_xlim(0, len(self.data))  # Change the limits as needed
        self.ax.set_ylim(-0.5, 1.5)  # Change the limits as needed
        self.canvas.draw()

    def shutdown(self):
        self.timer.stop()
        self.close()
