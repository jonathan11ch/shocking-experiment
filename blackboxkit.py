import numpy
import threading
import time
from gui import VirtualBlackboxWidget

def custom_library(isVirtual = False):
    if not isVirtual:
        import serial


class BlackBoxKit(object):
    def __init__(self,ser_port = "COM4", ser_timeout = 0.1, sample_time = 0.5):
        self.baudrate = 115200
        self.ser_timeout = ser_timeout
        self.ser_port = ser_port 
        self.bytes2read = 10
        self.sample_time  = sample_time
        self.serial = serial.Serial(self.ser_port, self.baudrate, timeout=self.ser_timeout)
        self.t = threading.Thread(target = self.read_blackbox_serial)
        self.action_dict = {'turn_led'   : self.turn_on_led,
                            'turn_button': self.turn_on_button,
                            'turn_both'  : self.turn_on_all}
        self.IS_RUNNING = True
    
    def check_status(self):
        message_bytes = bytes("##", "utf-8")
        self.serial.write(message_bytes)
        time.sleep(0.5)
        data = self.serial.read(2)
        if data.decode('utf-8') == "XX":
            return True 
        
        return False
    
    def set_read_bytes(self,bytes):
        self.bytes2read = bytes

    def turn_on_led(self):
        message_bytes = bytes("01","utf-8")
        self.serial.write(message_bytes)

    def turn_on_button(self):
        message_bytes = bytes("02","utf-8")
        self.serial.write(message_bytes)
    
    def turn_on_all(self):
        message_bytes = bytes("03","utf-8")
        self.serial.write(message_bytes)
    
    def turn_off(self):
        message_bytes = bytes("00","utf-8")
        self.serial.write(message_bytes)

    def launch(self):
        if self.check_status():
            self.t.start()
            print("blackbox toolkit launched")
        else:
            print("Serial not connected properly")


    def read_blackbox_serial(self):
        self.data = self.serial.read(self.bytes2read)
        self.serial.flushInput()
        return self.data
    
    def flush_serial(self):
        self.serial.flushInput()

    def read_blackbox_serial_loop(self):
        while self.IS_RUNNING:
            self.data = self.serial.read(self.bytes2read)
            print("from thread")
            print(self.data.decode('utf-8'))
            self.serial.flushInput()
            time.sleep(self.sample_time)

        print("leaving thread...")

    def shutdown(self):
        self.IS_RUNNING =False
        self.serial.close()
        

class VirtualBlackBoxKit(object):
    def __init__(self,ser_port = "COM4", ser_timeout = 0.1, sample_time = 0.5):
        self.baudrate = 115200
        self.ser_timeout = ser_timeout
        self.ser_port = ser_port 
        self.bytes2read = 10
        self.sample_time  = sample_time
        self.VirtualBlackboxWidget = VirtualBlackboxWidget()
        self.VirtualBlackboxWidget.show()

    def set_read_bytes(self,bytes):
        self.bytes2read = bytes

    def check_status(self):
        return True

    def launch(self):
        #launch gui with botton and two lights
        pass

    def turn_on_led(self):
        self.VirtualBlackboxWidget.turn_on_led()

    def turn_on_button(self):
        self.VirtualBlackboxWidget.button.turn_on()

    def turn_on_all(self):
        self.turn_on_led()
        self.turn_on_button()

    def turn_off(self):
        self.VirtualBlackboxWidget.turn_off_led()
        self.VirtualBlackboxWidget.button.turn_off()

    def flush_serial(self):
        pass

    def read_blackbox_serial(self):
        if self.VirtualBlackboxWidget.button.isChecked():
            self.data = b'01'
        else:
            self.data = b'00'
        
        return self.data

    def shutdown(self):
        self.VirtualBlackboxWidget.close()
        pass    

if __name__ == "__main__":

    kit = BlackBoxKit(ser_port= 'COM4', ser_timeout=0.1)
    kit.set_read_bytes(2)

    if kit.check_status():
        kit.launch()

    kit.turn_on_led()
    time.sleep(5)
    kit.turn_off()
    time.sleep(2)

    kit.turn_on_button()
    time.sleep(5)
    kit.turn_off()
    time.sleep(2)

    kit.turn_on_all()
    time.sleep(5)
    kit.turn_off()
    time.sleep(2)
    time.sleep(10)
    kit.shutdown()