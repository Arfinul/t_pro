import numpy as np
import cv2
import tkinter as tk
from PIL import Image, ImageTk
import os
import configparser
import datetime

configparser = configparser.RawConfigParser()   
configparser.read('gui.cfg')


def testVal(inStr,acttyp):
    if acttyp == '1': #insert
        if not inStr.isdigit():
            return False
    return True

def detail_fxn():
    pass

def qr_scan_fxn():
    pass

window = tk.Tk()  #Makes main window
window.wm_title("Enter details")
window.config(background="#FFFFFF")

def remove_farmer():
    FARMER_ENTRY.delete(first=0, last=22)

def remove_sector():
    SECTOR_ENTRY.delete(first=0, last=22)

top = tk.Frame(window)
middle = tk.Frame(window)
bottom = tk.Frame(window)
top.pack(side='top')
middle.pack(side='top')
bottom.pack(side="bottom", fill="both", expand=True)


farmer = tk.Label(window, text="Farmer ID", width=int(configparser.get('gui-config', 'id_label_width')), height=int(configparser.get('gui-config', 'id_label_height')), fg="white", bg="#008CBA", font=('times', int(configparser.get('gui-config', 'font')), ' bold '))
sector = tk.Label(window, text="Sector ID", width=int(configparser.get('gui-config', 'id_label_width')), height=int(configparser.get('gui-config', 'id_label_height')), fg="white", bg="#008CBA", font=('times', int(configparser.get('gui-config', 'font')), ' bold '))

FARMER_ENTRY = tk.Entry(window, width=int(configparser.get('gui-config', 'entry_width')),validate='key', bg="silver", fg="black", font=('times', 23, 'bold'))
FARMER_ENTRY['validatecommand'] = (FARMER_ENTRY.register(testVal), '%P', '%d')
SECTOR_ENTRY = tk.Entry(window, width=int(configparser.get('gui-config', 'entry_width')), bg="silver", fg="black", font=('times', 23, ' bold '))


clear_farmer = tk.Button(window, text="Clear", command=remove_farmer, fg="black", bg="#e7e7e7", width=int(configparser.get('gui-config', 'clear_btn_width')), height=1, activebackground="gray", font=('times', int(configparser.get('gui-config', 'font')), ' bold '))
clear_sector = tk.Button(window, text="Clear", command=remove_sector, fg="black", bg="#e7e7e7", width=int(configparser.get('gui-config', 'clear_btn_width')), height=1, activebackground="gray", font=('times', int(configparser.get('gui-config', 'font')), ' bold '))

save_details = tk.Button(window, text="Save", width=10, height=1, fg="black", bg="silver", font=('times', int(configparser.get('gui-config', 'font')), 'bold'), command=detail_fxn)
qr_code = tk.Button(window, text="Scan QR", width=10, height=1, fg="black", bg="silver", font=('times', int(configparser.get('gui-config', 'font')), 'bold'), command=qr_scan_fxn)



farmer.pack(in_= top, side="left", fill="both", expand=False)
sector.pack(in_= middle, side="left", fill="both", expand=True)

FARMER_ENTRY.pack(in_= top, side="left", fill="both", expand=True)
SECTOR_ENTRY.pack(in_= middle, side="left", fill="both", expand=True)

clear_farmer.pack(in_= top, side="right", fill="both", expand=True)
clear_sector.pack(in_= middle, side="right", fill="both", expand=True)

save_details.pack(in_= bottom, side="left", fill="both", expand=True)
qr_code.pack(in_= bottom, side="right", fill="both", expand=True)

window.mainloop()  #Starts GUI