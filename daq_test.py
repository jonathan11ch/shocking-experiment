
'''
import PyDAQmx
import numpy
import time
from ctypes import byref
from ctypes import c_int

num_samples = 100
read = c_int(0)
timeout = PyDAQmx.DAQmx_Val_WaitInfinitely
task = PyDAQmx.Task()
task.CreateDIChan("Dev1/port0", "", PyDAQmx.DAQmx_Val_ChanForAllLines)
data = numpy.zeros((num_samples,), dtype=numpy.uint32)
task.ReadDigitalLines(num_samples, timeout, PyDAQmx.DAQmx_Val_GroupByChannel, data, num_samples, byref(read), None)

time.sleep(5)
task.StopTask()
task.ClearTask()
print(data)
print(read)
print("end...")
'''

from PyDAQmx import Task, int32, byref, DAQmx_Val_GroupByChannel
import numpy
import time
task = Task()

# Configure the task for digital input with a range of lines
task.CreateDIChan("Dev1/port0/line0:7", "", DAQmx_Val_GroupByChannel)

# Read digital data
num_samples = 10
timeout = 10.0  # Timeout in seconds
data = numpy.zeros(num_samples, dtype=numpy.uint8)  # Use uint8 data type
read = int32()

buffer_size = num_samples * 8  # Multiply by 8 to account for 8 bits per sample
task.ReadDigitalLines(num_samples, timeout, DAQmx_Val_GroupByChannel, data, buffer_size, byref(read), None, None)
print("sssss")
# Process the acquired data
print("Read", read.value, "samples")
print("Digital data:", data)

time.sleep(2)
# Clean up
task.StopTask()
task.ClearTask()


