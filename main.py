isVirtual = True
import typing
import sys
import time
import threading
from PyQt5.QtWidgets import QApplication

#custom libraries
from gui import MainWidget
from datahandler import DataHandler
from utils import StoppableTimer

if isVirtual:
    from blackboxkit import VirtualBlackBoxKit as BlackBoxKit
    from daq import VirtualStimulusGenerator as StimulusGenerator
else:
    from blackboxkit import BlackBoxKit
    from daq import StimulusGenerator

from blackboxkit import custom_library as blackboxlibrary
blackboxlibrary(isVirtual = isVirtual)

from daq import custom_library as daqlibrary
daqlibrary(isVirtual = isVirtual)


app = QApplication(sys.argv)



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
                print("data from virtual thing")
                print(self.button_data)
                if self.button_data == b'01':
                    print('clicked button')
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



