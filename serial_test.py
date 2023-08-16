import serial
import time
import threading 
#install libraries like this
#py -m pip install pyserial


def read_blackbox_serial(serial, num_bytes):
    while IS_RUNNING:
        data = serial.read(num_bytes)
        print("from thread")
        print(data.decode('utf-8'))
        time.sleep(1)

    print("leaving thread...")




#BUTTON_ON = "01"
#LED_ON = "02"
#ALL_ON = "03"
port = "COM4" # or "COM1" on Windows
usart = serial.Serial(port, 115200, timeout=0.1)
IS_RUNNING = True
num_bytes = 10
t = threading.Thread(target = read_blackbox_serial, args = (usart, num_bytes))
t.start()

message_bytes = bytes("RR", "utf-8")
usart.write(message_bytes)
time.sleep(1)

message_bytes = bytes("##","utf-8")
usart.write(message_bytes)
time.sleep(0.5)

data = usart.read(2)
print(data)

message_bytes = bytes("01","utf-8")
usart.write(message_bytes)
time.sleep(5)

message_bytes = bytes("02","utf-8")
usart.write(message_bytes)
time.sleep(5)

message_bytes = bytes("03","utf-8")
usart.write(message_bytes)
time.sleep(5)

usart.write(bytes("00", "utf-8"))



IS_RUNNING = False


#message_bytes = bytes.fromhex("RR")
time.sleep(5)
usart.close()


