###################
#Cherif Ahmad Seye#
#     Pure Air    #
###################

import serial
import serial.tools.list_ports as ports
from time import sleep
from sys import platform

class SerialPort:
    def __init__(self, ser=serial.Serial()):
       
        self.ser= ser
        
    def get_portlist(self):
        self.ports_list = []
        if platform == 'darwin':
            self.ports_list = [str(port).split(' ')[0] for port in ports.comports() if "usb" in str(port)]
            
        elif platform == 'win32':
            self.ports_list = [str(port).split(' ')[0] for port in ports.comports()]
        
        elif platform == 'linux' or platform == 'linux2':
            self.ports_list = [str(port).split(' ')[0] for port in ports.comports()]
        
        return self.ports_list
        
    def port_isOpen(self):
        return self.ser.is_open
    
    def open_port(self):
        if self.ser.is_open:
            pass
        else:
            self.ser.open()
        
    def close_port(self):
        if self.ser.is_open == False:
            pass
        else:
            self.ser.close()
    
    
    def get_data(self):
        values = self.ser.readline().decode().split(',')
        return [float(value) for value in values]
    
    def check_arduino(self):
        for port in ports.comports():
            print(str(port.hwid))
    

