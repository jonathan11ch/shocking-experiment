import typing
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QCheckBox
from PyQt5.QtGui import QDoubleValidator
from blackboxkit import BlackBoxKit
from datahandler import DataHandler
from utils import StoppableTimer
from daq import StimulusGenerator
import sys
import time
import threading
from PyQt5.QtCore import QTimer, pyqtSignal, QObject, QThread

app = QApplication(sys.argv)

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


class ProtocolSession(object):
    def __init__(self):
        self.MainWidget = MainWidget()
        self.BlackBoxToolkit = BlackBoxKit(ser_port= 'COM4', ser_timeout=0.1)
        self.BlackBoxToolkit.set_read_bytes(2)
        self.BlackBoxToolkit.sample_time = 0.1
        self.sample_time = 0.5
        self.IS_ON = False
        self.set_events()
        self.StateMachine = StateMachine()
        self.StimulusGenerator = StimulusGenerator()

    def set_events(self):
        self.MainWidget.run_button.clicked.connect(self.on_start_experiment)
        self.MainWidget.stop_button.clicked.connect(self.shutdown)



    def on_start_experiment(self):
        self.config = self.MainWidget.get_config()
        self.delay_timer = StoppableTimer(self.config['resp_delay'], self.on_delay_timeup)
        self.delay_timer.name = 'delay timer'
        self.light_on_timer = StoppableTimer(self.config['resp_duration'], self.on_light_on_timeup)
        self.light_on_timer.name = 'light_on timer'
        self.IS_ON = True
        self.StateMachine.handle_event('start')
        
        
        if self.BlackBoxToolkit.check_status():
            self.initial_time = time.time()
            self.t1 = threading.Thread(target= self.state_machine).start()
        else:
            print("Black Box Kit not connected")
            
    
    def state_machine(self):
        while self.IS_ON:
            if self.StateMachine.current_state == "running":
                print("Session thread running state")
                self.button_data = self.BlackBoxToolkit.read_blackbox_serial()
                if self.button_data == b'01':
                    'clicked button'
                    self.StateMachine.handle_event('clicked')
                    
                    'start running the delay timer'
                    self.delay_timer.start()
            else:
                self.BlackBoxToolkit.flush_serial()
                print("not in running")
            time.sleep(self.sample_time)
            #time.sleep(self.sample_time)
        
        self.final_time = time.time()
        self.BlackBoxToolkit.shutdown()
        self.MainWidget.close()
        print("Session Ended")

    def on_delay_timeup(self):
        print("enter on_delay_timeup()")
        self.StateMachine.handle_event('delay_timeup')
        #self.delay_timer.stop()
        if self.config['lock_resp']:
            self.BlackBoxToolkit.turn_off()
        else:
            self.StimulusGenerator.launch_pulse(time = self.config['resp_duration'])
            if self.config['turn_both']:
                self.BlackBoxToolkit.turn_on_all()
            elif self.config['led_on']:
                self.BlackBoxToolkit.turn_on_led()
            elif self.config['button_on']:
                self.BlackBoxToolkit.turn_on_button()

        self.light_on_timer.start()

    def on_light_on_timeup(self):
        self.StateMachine.handle_event('light_on_timeup')
        self.BlackBoxToolkit.turn_off()
        #self.light_on_timer.stop()


    def shutdown(self):
        self.StateMachine.handle_event('on_stop')
        self.StimulusGenerator.shutdown()
        time.sleep(1)
        self.IS_ON = False
        

        

class StateMachine(object):
    def __init__(self):
        self.states = {
            'idle'  : self.idle_state,
            'running' : self.running_state,
            'delay' : self.delay_state,
            'light_on': self.light_on_state,
            'stop'  : self.stop_state
        }
        self.current_state = 'idle'
        self.DataHandler = DataHandler()

    def handle_event(self, event):
        if event == 'on_stop':
            print("stoppppppppppppppppppppppppp")
            self.DataHandler.register_event(name='on_stop', val= -1)
            self.DataHandler.shutdown()
            self.current_state = 'stop'
            stop_action = self.states['stop']
            stop_action()
        elif self.current_state in self.states:
            action_method = self.states[self.current_state]
            next_state = action_method(event)
            if next_state  is not None:
                self.current_state = next_state
            else:
                print("Invalid event")
        else:
            print("Invalid State")


    def idle_state(self, event):
        if event == 'start':
            self.DataHandler.launch()
            print("event: running")
            return 'running'
        else:
            return self.current_state

    def running_state(self, event):
        if event == 'clicked':
            self.DataHandler.register_event(name='clicked', val=1)
            print("event: clicked")
            return 'delay'
        else:
            return self.current_state

    def delay_state(self, event):
        if event == 'delay_timeup':
            self.DataHandler.register_event(name='delay_timeup',val=2)
            print("event: delay")
            return 'light_on'
        else:
            return self.current_state

    def light_on_state(self, event):
        if event == 'light_on_timeup':
            self.DataHandler.register_event(name='light_on_timeup', val=3)
            print("event: light on")
            return 'running'
        else:
            return self.current_state

    def stop_state(self):
            return self.current_state

session = ProtocolSession()
sys.exit(app.exec())



