import numpy as np
import cv2
import tkinter as tk
from PIL import Image, ImageTk
import os
import configparser
import datetime

configparser = configparser.RawConfigParser()   
configparser.read('gui.cfg')

if not os.path.exists("recorded/"):
	os.mkdir("recorded")

last_video = ""
writer = cv2.VideoWriter(__file__.replace("record_cam_gui.py", "recorded/cam_record.mp4"), cv2.VideoWriter_fourcc(*'MP4V'), int(configparser.get('gui-config', 'fps')), (int(configparser.get('gui-config', 'recording_resolution_width')), int(configparser.get('gui-config', 'recording_resolution_height'))), True)

window = tk.Tk()  #Makes main window
window.wm_title("Recording...")
window.config(background="#FFFFFF")

def clear_search(event): 
    vid_name.delete(0, tk.END) 

def do_nothing():
	pass

def save_and_close():
	name = vid_name.get()
	writer.release()
	if name in ["Enter video name..", "Please enter video name", ""]:
		vid_name.delete(0, tk.END) 
		vid_name.insert(1, 'Please enter video name')
	else:
		last_video = name
		os.rename("recorded/cam_record.mp4", "recorded/" + "_".join(str(datetime.datetime.now())[:-7].split()) + "_" + name + ".mp4")
		window.destroy()

def discard_video():
	if last_video == "":
		cmd = "rm -rf recorded/cam_record.mp4"
	else:
		cmd = "rm -rf recorded/" + last_video + ".mp4"
	os.system(cmd)
	window.destroy()

window.protocol("WM_DELETE_WINDOW", do_nothing)

#Graphics window
imageFrame = tk.Frame(window, width=600, height=600)
imageFrame.pack(side="top", fill="x")

vid_name = tk.Entry(window, width=20,validate='key', bg="white", fg="black", font=('times', 23, 'bold'))
vid_name.insert(1, 'Enter video name..')
vid_name.pack(side='top', fill="both", expand=True)
vid_name.bind("<Button-1>", clear_search) 

save = tk.Button(window, text="Save video", command=save_and_close, fg="white", bg="green", width=10,height=2, activebackground = "Grey" , font=('times', 15, 'bold'))
save.pack(side="left", fill="both", expand=True)

discard = tk.Button(window, text="Discard video", command=discard_video, fg="white", bg="#e33b3b", width=10,height=2, activebackground = "Grey" , font=('times', 15, 'bold'))
discard.pack(side="right", fill="both", expand=True)

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
