#!/usr/bin/env python
#
# (C)2021 Andre Devecchi <andre.devecchi@gmail.com>

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import scrolledtext

from serial_port import SerialPortThread

class Window(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Serial Terminal')

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = screen_width / 2
        window_height = screen_width / 2
        window_position_x = screen_width / 2 - window_width / 2
        window_position_y = screen_height / 2 - window_height / 2

        self.geometry('%dx%d+%d+%d' % (window_width, window_height, window_position_x, window_position_y))

        self.protocol('WM_DELETE_WINDOW', self.on_closing)

        self.init_components()

        self.serialport = SerialPortThread()
        self.serialport.register_callback(self.on_receive_data)
        self.serialport.daemon = True
        self.serialport.start()

    def init_components(self):
        frame_rx = ttk.Frame(self)
        frame_rx.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.btn_cleardata = ttk.Button(master=frame_rx, text='Clear Data', width=10, command=self.cmd_clear_data, state=tk.DISABLED)
        self.btn_cleardata.pack(side=tk.TOP, anchor=tk.NW, expand=0, padx=4, pady=(4,0))

        self.text_rx = scrolledtext.ScrolledText(master=frame_rx, wrap=tk.WORD, state=tk.DISABLED)
        self.text_rx.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1, padx=4, pady=4)
        self.text_rx.tag_config('open_port', foreground='green')
        self.text_rx.tag_config('close_port', foreground='red')

        frame_tx = ttk.Frame(self)
        frame_tx.pack(side=tk.TOP, fill=tk.BOTH, expand=0)

        self.text_tx = ttk.Entry(master=frame_tx, state=tk.DISABLED)
        self.text_tx.pack(side=tk.LEFT, anchor=tk.NW, fill=tk.BOTH, expand=1, padx=4, pady=(4,8))

        self.btn_senddata = ttk.Button(master=frame_tx, text='Send Message', command=self.cdm_send_data, state=tk.DISABLED)
        self.btn_senddata.pack(side=tk.LEFT, anchor=tk.NE, expand=0, padx=4, pady=(4,8))

        frame = ttk.Frame(self)
        frame.pack(side=tk.TOP, fill=tk.BOTH, expand=0)

        label_port = ttk.Label(master=frame, text='Port:')
        label_port.pack(side=tk.LEFT, expand=0, padx=4, pady=8)

        self.text_port = ttk.Entry(master=frame, width=12)
        self.text_port.pack(side=tk.LEFT, expand=0, padx=4, pady=8, ipady=3)

        self.btn_openclose = ttk.Button(master=frame, text='Open Port', command=self.cmd_open_close)
        self.btn_openclose.pack(side=tk.LEFT, expand=0, padx=4, pady=8)

        label_baud = ttk.Label(master=frame, text='Baud Rate:')
        label_baud.pack(side=tk.LEFT, expand=0, padx=(70,4), pady=8)

        self.combo_baud = ttk.Combobox(master=frame, values=('1200', '2400', '4800', '9600', '19200'))
        self.combo_baud.pack(side=tk.LEFT, expand=0, padx=4, pady=8, ipady=3)
        self.combo_baud.current(3)
        
    def cmd_open_close(self):
        if self.btn_openclose.cget('text') == 'Open Port':
            port = self.text_port.get()
            baudrate = self.combo_baud.get()
            try:
                self.serialport.open(port, baudrate)
                self.btn_cleardata['state'] = tk.NORMAL
                self.text_rx['state'] = tk.NORMAL
                self.text_tx['state'] = tk.NORMAL
                self.btn_senddata['state'] = tk.NORMAL
                self.btn_openclose.config(text='Close Port')
                self.text_rx.insert(tk.END, 'Port Opened\n', 'open_port')
                self.text_rx.see(tk.END)
            except Exception as err:
                messagebox.showerror('Serial Terminal', str(err))
        elif self.btn_openclose.cget('text') == 'Close Port':
            try:
                self.serialport.close()
                self.btn_openclose.config(text='Open Port')
                self.text_rx.insert(tk.END, 'Port Closed\n', 'close_port')
                self.text_rx.see(tk.END)
                self.btn_cleardata['state'] = tk.DISABLED
                self.text_rx['state'] = tk.DISABLED
                self.text_tx['state'] = tk.DISABLED
                self.btn_senddata['state'] = tk.DISABLED
            except Exception as err:
                messagebox.showerror('Serial Terminal', str(err))
    
    def cmd_clear_data(self):
        self.text_rx.delete('1.0', tk.END)
    
    def cdm_send_data(self):
        if self.serialport.isOpen():
            message = self.text_tx.get()
            try:
                self.serialport.send(message)
            except Exception as err:
                messagebox.showerror('Serial Terminal', str(err))
        else:
            messagebox.showwarning('Serial Terminal', 'Not Send - Port is closed.')

    def on_receive_data(self, message):
        message = message.decode('utf-8').replace('\r', '')
        self.text_rx.insert(tk.END, message)
        self.text_rx.yview_pickplace(tk.END)
    
    def on_closing(self):
        if messagebox.askokcancel('Serial Terminal', 'Do you want to quit?'):
            if self.serialport.isOpen():
                try:
                    self.serialport.close()
                except Exception as err:
                    messagebox.showerror('Serial Terminal', str(err))
            self.destroy()
