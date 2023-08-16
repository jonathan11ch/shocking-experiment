import time
class DataHandler(object):
    def __init__(self):
        self.file_name = "default.csv"
        self.t0 = 0
        self.header = "time;event;value\n"
        self.set_file_header()

    def set_file_name(self, name = ""):
        self.file_name = name + ".csv"

    def set_file_header(self):
        self.f = open(self.file_name, 'w+')
        self.f.write(self.header)
        self.f.close()

    def launch(self):
        self.f = open(self.file_name, 'a')
        self.register_initial_time()

    def register_initial_time(self):
        self.t0 = time.time()
        string = "0.0;initial_time;"+str(self.t0) + "\n"
        self.f.write(string)



    def register_event(self, name='name', val= 0):
        string = str(time.time()-self.t0) + ";" + name + ";" +str(val) +"\n"
        self.f.write(string)

    def shutdown(self):
        self.f.close()
        pass





if __name__ == "__main__":
    h= DataHandler()
    time.sleep(5)
    h.launch()
    time.sleep(2)
    h.register_event(name="on_connect",val=0)
    time.sleep(1)
    h.register_event(name="on_test")
    h.register_event()


    