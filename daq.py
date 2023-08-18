import numpy as np
import time
import threading
from utils import StoppableTimer
from gui import VirtualStimulatorWidget

def custom_library(isVirtual = False):
    if not isVirtual:
        import PyDAQmx as daq
        


def analog_write():
    task = daq.Task()

    # Create an analog output voltage channel
    task.CreateAOVoltageChan("Dev1/ao1", "", -10.0, 10.0, daq.DAQmx_Val_Volts, None)

    # Generate a waveform
    t = np.linspace(0, 1, 1000)
    #waveform = 5 * np.sin(2 * np.pi * 10 * t)
    waveform = 4*np.ones(1000)
    # Write the waveform to the analog output
    task.WriteAnalogF64(len(waveform), True, -1, daq.DAQmx_Val_GroupByChannel, waveform, None, None)

    # Start the task
    task.StartTask()

    # Wait for the task to complete
    task.WaitUntilTaskDone(-1)

    # Stop and clear the task
    task.StopTask()
    task.ClearTask()
    print("end.....")

def pwm_signal():
    task = daq.Task()
    task.CreateAOVoltageChan("/Dev1/ao1", "", -10.0, 10.0, daq.DAQmx_Val_Volts, None)
    task.StartTask()
    data = np.zeros((1000,), dtype=np.float64)
    data[0:500] = 10
    for i in range(100):
        task.WriteAnalogF64(1000, False, 10.0, daq.DAQmx_Val_GroupByChannel, data, None, None)

    task.StopTask()
    task.ClearTask()


def generate_pulse():
    # Create a task object
    task = daq.Task()

    # Create a digital output channel
    task.CreateDOChan("/Dev1/port0/line0", "", daq.DAQmx_Val_ChanForAllLines)

    # Generate a pulse
    data = np.zeros((1,), dtype=np.uint8)
    data[0] = 1
    for i in range(1000):
        task.WriteDigitalLines(1, 1, 10.0, daq.DAQmx_Val_GroupByChannel, data, None, None)
        if data[0] == 1:
            data[0] = 0
        else:
            data[0] = 1

        time.sleep(0.1)


    # Clear the task object
    task.ClearTask()




class StimulusGenerator(object):
    def __init__(self):
        self.stim_duration = 1
        self.sample_time = 0.1
        # Create a task object
        self.task = daq.Task()
        # Create a digital output channel
        self.task.CreateDOChan("/Dev1/port0/line0", "", daq.DAQmx_Val_ChanForAllLines)
        # Generate a pulse
        self.data = np.zeros((1,), dtype=np.uint8)
        self.data[0] = 1
        self.IS_ON = False
        
    def launch_pulse(self, time):
        self.IS_ON = True
        self.t = threading.Thread(target = self.generate_pulse).start()
        self.pulse_timer = StoppableTimer(time, self.stop_pulse)
        self.pulse_timer.start()

    def stop_pulse(self):
        self.IS_ON =False

    def generate_pulse(self):
        #pulse_time = round(self.stim_duration/self.sample_time)
        t1 = time.time()
        while self.IS_ON:
            self.task.WriteDigitalLines(1, 1, 10.0, daq.DAQmx_Val_GroupByChannel, self.data, None, None)
            if self.data[0] == 1:
                self.data[0] = 0
            else:
                self.data[0] = 1
            time.sleep(self.sample_time)

        t2 = time.time()
        print(t2 - t1)


    def shutdown(self):
        self.task.ClearTask()


class VirtualStimulusGenerator(object):
    def __init__(self):
        self.stim_duration = 1
        self.sample_time = 0.1
        # Create a task object
        self.data = np.zeros((1,), dtype=np.uint8)
        self.data[0] = 1
        self.IS_ON = False
        #launch virtual interface (gui?)
        self.VirtualStimulatorWidget = VirtualStimulatorWidget()
        self.VirtualStimulatorWidget.show()

    def launch_pulse(self, time):
        self.IS_ON = True
        self.t = threading.Thread(target = self.generate_pulse).start()
        self.pulse_timer = StoppableTimer(time, self.stop_pulse)
        self.pulse_timer.start()

    def stop_pulse(self):
        self.IS_ON =False

    def generate_pulse(self):
        #pulse_time = round(self.stim_duration/self.sample_time)
        t1 = time.time()
        while self.IS_ON:
            #substitute for digial version
            #self.task.WriteDigitalLines(1, 1, 10.0, daq.DAQmx_Val_GroupByChannel, self.data, None, None)
            if self.data[0] == 1:
                self.data[0] = 0
            else:
                self.data[0] = 1
            self.VirtualStimulatorWidget.load_data(self.data[0])
            time.sleep(self.sample_time)

        t2 = time.time()
        print(t2 - t1)


    def shutdown(self):
        self.VirtualStimulatorWidget.shutdown()
        pass


if __name__ == "__main__":
    #pwm_signal()
    s = StimulusGenerator()
    #t1 = time.time()
    s.launch_pulse(time = 5)
    #t2 = time.time()
    #print(t2-t1)

    time.sleep(10)
    s.shutdown()