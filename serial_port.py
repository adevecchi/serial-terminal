#!/usr/bin/env python
#
# (C)2021 Andre Devecchi <andre.devecchi@gmail.com>

import serial
import threading

class SerialPortThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.receive_callback = None
        self.receive_message = None
        self.serialport = serial.Serial()
    
    def register_callback(self, callback):
        self.receive_callback = callback
    
    def run(self):
        while True:
            try:
                if self.serialport.is_open:
                    self.receive_message = self.serialport.readline()
                    if self.receive_message != '':
                        self.receive_callback(self.receive_message)
            except:
                #print('Error reading port')
                pass
    
    def open(self, port, baudrate):
        try:
            if not self.serialport.is_open:
                self.serialport.port = port
                self.serialport.baudrate = baudrate
                #self.serialport.timeout = 1
                self.serialport.open()
        except serial.serialutil.SerialException:
            raise Exception('Port name not found.')
    
    def close(self):
        try:
            if self.serialport.is_open:
                self.serialport.close()
        except serial.serialutil.SerialException:
            raise Exception('Error closing port.')
    
    def isOpen(self):
        return self.serialport.is_open
    
    def send(self, message):
        try:
            if self.serialport.is_open:
                send_message = message.strip()
                send_message += '\n'
                self.serialport.write(send_message.encode('utf-8'))
                return True
            return False
        except serial.serialutil.SerialException:
            raise Exception('Error sending message')
