import numpy as np
import cv2
import tkinter as tk
from PIL import Image, ImageTk
import os
import configparser

configparser = configparser.RawConfigParser()   
configparser.read('gui.cfg')

writer = cv2.VideoWriter(__file__.replace("record_cam_gui.py", "cam_record.mp4"), cv2.VideoWriter_fourcc(*'MP4V'), int(configparser.get('gui-config', 'fps')), (int(configparser.get('gui-config', 'recording_resolution_width')), int(configparser.get('gui-config', 'recording_resolution_height'))), True)

#Set up GUI
window = tk.Tk()  #Makes main window
window.wm_title("Recording...")
window.config(background="#FFFFFF")
# window.geometry(configparser.get('gui-config', 'record_window_geometry'))

#Graphics window
imageFrame = tk.Frame(window, width=600, height=500)
imageFrame.grid(row=0, column=0)

#Capture video frames
lmain = tk.Label(imageFrame)
lmain.grid(row=0, column=0)
cap = cv2.VideoCapture(0)

def show_frame():
    _, frame = cap.read()
    # frame = cv2.flip(frame, 1)
    writer.write(frame)
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)
    lmain.after(10, show_frame) 


show_frame()  #Display 2
window.mainloop()  #Starts GUI
