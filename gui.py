import tkinter as tk
from tkinter import *
import cv2
import csv
import os
import numpy as np
from PIL import Image,ImageTk
import pandas as pd
import datetime
import time
import sys
import subprocess
from time import sleep
import requests
import json
os.chdir("/home/agnext/Music/darknet")	# Agnext (Desktop icon path issue fix)

is_login = False
userName = ""
cmd = './uselib cfg/1_black_conveyor.names cfg/5_yolov3_optimised.cfg 5_yolov3_optimised.weights web_camera > output.txt'
cmd_camera_setting = 'ecam_tk1_guvcview'

def vp_start_gui():
    global window
    window = tk.Tk()
    # window.attributes("-fullscreen", True)
    window.title("Fine Leaf Count")

    window.geometry('1920x1080')
    window.configure(background='snow')

    # function for video streaming
    def video_stream():
        msg_sent.place_forget()
        tuneCamera.configure(state='disabled', fg="black", bg="silver")
        try:
            global p
            p = subprocess.Popen("exec " + cmd, stdout= subprocess.PIPE, shell=True)
            endRecord.configure(bg="#539051", state="active")
            startRecord.configure(bg='silver', state="disabled")
        except:
            p.kill()
            endRecord.configure(bg='silver', state="disabled")
            startRecord.configure(bg="#539051", state="active")
            refresh()

    def end_video():
        p.kill()
        tuneCamera.configure(fg="white", bg="#539051", state='active')
        endRecord.configure(bg='silver', state="disabled")
        startRecord.configure(bg="#539051", state="active")
        send_data_api()       #send data to api
        # refresh()

    def set_camera():
        try:
            global csetting
            csetting = subprocess.Popen("exec " + cmd_camera_setting, stdout= subprocess.PIPE, shell=True)
            #startRecord.configure(state="disabled", bg='silver')
        except:
            csetting.kill()
            refresh()

    def set_camera_exit():
        csetting.kill()
        refresh()

    def on_closing():
        from tkinter import messagebox
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            window.destroy()

    # APIs
    def login_api(usr, pwd):
        payload = {
            "username": usr,
            "password": pwd,
            "entity": "mobile",
            "deviceToken": "1"
        }
        headers = {
        	"Content-Type": "application/json"
        }
        response = requests.request("POST", "http://18.218.214.164:9955/api/auth/login", data=json.dumps(payload), headers=headers)
        status = False
        try:
            global userID
            global token
            if response.json()['success'] == "true":
                userID = response.json()["user"]["id"]
                token = response.json()['token']
                global userName
                userName = response.json()["user"]["name"]
                status = True
        except Exception as e:
            print("Exception during login: ", e)
        return status


    def send_data_api():
        txt_file = open("result.txt", "r").read()
        li = txt_file.split("\n")
        _1lb = li[1].split(" : ")[1]
        _2lb = li[2].split(" : ")[1]
        _3lb = li[3].split(" : ")[1]
        head = {
        	"Content-Type": "application/json",
        	"Authorization": "Bearer " + token
        }
        load = {
            "flcData": "",
            "sectionId": 1,
            "oneLeafBud": _1lb,
            "twoLeafBud": _2lb,
            "oneLeafBanjhi": "0",
            "twoLeafBanjhi": "0",
            "moderateShoot": "0",
            "fineShoot": "0",
            "scannedBy": userID,
            "weighment": "0",
            "oneBanjhiCount": "0",
            "oneBudCount": "0",
            "oneLeafCount": "0",
            "twoLeafCount": "0",
            "threeLeafCount": "0",
            "userId": userID,
            "dateDone": "12/11/2019"
        }
        resp = requests.request("POST", "http://18.218.214.164:9955/api/own-flc", data=json.dumps(load), headers=head)
        if resp.json()['success'] == "true":
            msg_sent.configure(text="Data saved", fg="green")
            msg_sent.place(x=90, y=650)
        else:
            msg_sent.configure(text="Couldn't save to servers", fg="red")
            msg_sent.place(x=90, y=650, fg="red")
     
    # Designing window for login 
     
    def login():
        x = window.winfo_x()
        y = window.winfo_y()
        global login_screen
        login_screen = Toplevel(window)
        login_screen.title("Login")
        login_screen.geometry("+%d+%d" % (x + 830, y + 230))
        Label(login_screen, text="Please enter details below to login", font=("times", 14, 'bold'), width=30).pack()
        Label(login_screen, text="").pack()
     
        global username_verify
        global password_verify
     
        username_verify = StringVar()
        password_verify = StringVar()
     
        global username_login_entry
        global password_login_entry
     
        Label(login_screen, text="Username * ", font=("times", 13)).pack()
        username_login_entry = Entry(login_screen, textvariable=username_verify)
        username_login_entry.pack()
        Label(login_screen, text="").pack()
        Label(login_screen, text="Password * ", font=("times", 13)).pack()
        password_login_entry = Entry(login_screen, textvariable=password_verify, show= '*')
        password_login_entry.pack()
        Label(login_screen, text="").pack()
        Button(login_screen, text="Login", width=10, height=1, command = login_verify, font=("times", 13, 'bold')).pack()
     
     
    # Implementing event on login button 
     
    def login_verify():
        username1 = username_verify.get()
        password1 = password_verify.get()

        status = login_api(username1, password1)
        if status == True:
            login_sucess()
        else:
        	user_not_found()
     
    # Designing popup for login success
     
    def login_sucess():
        global is_login
        is_login = True
        login_screen.destroy()
        startRecord.place(x=90, y=450)
        tuneCamera.place(x=90, y=200)
        #tuneCamera_exit.place(x=90, y=750)
        endRecord.configure(state="disabled", bg="silver", fg="black")
        endRecord.place(x=90, y=550)
        # register.place_forget()
        signin.place_forget()
        # section_gui()
        panel_bg.place_forget()
        # section.place(x=90, y=150)
        global userName
        txt = "Welcome, " + userName.title()
        Label(window, text=txt, font=('times', 15, 'bold'), bg='white').place(x=1550, y=130)

    # Designing popup for login invalid password
     
    def password_not_recognised():
        global password_not_recog_screen
        password_not_recog_screen = Toplevel(login_screen)
        password_not_recog_screen.title("Success")
        password_not_recog_screen.geometry("150x100")
        Label(password_not_recog_screen, text="Invalid Password ").pack()
        Button(password_not_recog_screen, text="OK", command=delete_password_not_recognised).pack()
     
    # Designing popup for user not found
     
    def user_not_found():
        global user_not_found_screen
        user_not_found_screen = Toplevel(login_screen)
        user_not_found_screen.title("Success")
        user_not_found_screen.geometry("150x100")
        Label(user_not_found_screen, text="User Not Found").pack()
        Button(user_not_found_screen, text="OK", command=delete_user_not_found_screen).pack()
     
    # Deleting popups
     
    def delete_login_success():
        login_success_screen.destroy()
     
     
    def delete_password_not_recognised():
        password_not_recog_screen.destroy()
     
     
    def delete_user_not_found_screen():
        user_not_found_screen.destroy()

    # def section_gui():
    #     # section.configure(state="disabled")
    #     global section_name
    #     global section_entry
    #     global old_button
    #     section_name = StringVar()
    #     # name_label = Label(window, text="Please enter section name", font=("times", 14, 'bold'), width=30).place(x=100, y=150)
    #     section_lable = Label(window, text="Section name * ", font=("times", 13, "bold"))
    #     section_lable.place(x=180, y=160)
    #     section_entry = Entry(window, textvariable=section_name)
    #     section_entry.place(x=140, y=215)
    #     tk.Button(window, text="Add Section", width=10, height=1, bg="#539051", fg="white", command = add_section, font=("times", 13, 'bold')).place(x=110, y=240)
    #     tk.Button(window, text="Add Another", width=10, height=1, bg="silver", fg="black", command = refresh, font=("times", 13, 'bold')).place(x=250, y=240)
       
    # def add_section():
    #     global section_success
    #     section_info = section_name.get()
    #     if section_info == "":
    #         section_success = Label(window, text="Can't be empty!", fg="orange", font=("calibri", 11)).place(x=150, y=280)
    #     else:
    #         file = open(userName, "a")
    #         file.write(str(datetime.datetime.now()) + ", ")
    #         file.write(section_info + "\n")
    #         file.close()
         
    #         section_success = Label(window, text=" Section added!", fg="green", font=("calibri", 11)).place(x=150, y=280)

    window.protocol("WM_DELETE_WINDOW", on_closing)

    message = tk.Label(window, text="Fine Leaf Count System", fg="black", bg="#539051", width=85, height=2, font=('times', 30, 'bold'))
    message.place(x=80, y=10)

    img = ImageTk.PhotoImage(Image.open("logo.png"))
    panel = Label(window, image = img, bg='#539051')
    panel.place(x=1350, y=10)
    
    tuneCamera = tk.Button(window, text="Camera Setting", command=set_camera, fg="white", bg="#539051", width=20,height=3, activebackground = "Grey" , font=('times', 15, 'bold'))
    # tuneCamera_exit = tk.Button(window, text="Save Camera Setting", command=set_camera_exit, fg="white", bg="#539051", width=20,height=3, activebackground = "Grey" , font=('times', 15, 'bold'))
    startRecord = tk.Button(window, text="Start", command=video_stream, fg="white", bg="#539051", width=20,height=3, activebackground = "Grey" , font=('times', 15, 'bold'))
    endRecord = tk.Button(window, text="Save & restart", command=end_video, fg="white", bg="#539051", width=20,height=3, activebackground = "Grey" , font=('times', 15, 'bold'))

    msg_sent = Label(window, text="Data sent status", font=('times', 15), fg="green", bg='white')

    if is_login == True:

        # section_gui()
        # section = tk.Button(window, text="Add Section", command=section_gui, fg="black", bg="deep sky blue", width=20,height=2, activebackground = "Grey" , font=('times', 15, 'bold'))
        # section.place(x=90, y=150) 

        signin = tk.Button(window, text="Login", command=login, fg="black", bg="#539051", width=20,height=2, activebackground = "Grey" , font=('times', 15, 'bold'))
        signin.place_forget()

        txt = "Welcome, " + userName.title()
        Label(window, text=txt, font=('times', 15, 'bold'), bg='white').place(x=1550, y=130)

        startRecord.place(x=90, y=450)

        endRecord.place(x=90, y=550)
        endRecord.configure(state="disabled", bg="silver")

    else:
        global panel_bg
        img_bg = ImageTk.PhotoImage(Image.open("bg.png"))
        panel_bg = Label(window, image = img_bg, bg='white')
        panel_bg.place(x=80, y=250)

        # section = tk.Button(window, text="Add Section", command=section_gui, fg="black", bg="deep sky blue", width=20,height=2, activebackground = "Grey" , font=('times', 15, 'bold'))
        # section.place_forget()

        signin = tk.Button(window, text="Login", command=login, fg="black", bg="#539051", width=25,height=2, activebackground = "Grey" , font=('times', 20, 'bold'))
        signin.place(x=1300, y=500)

        startRecord.place_forget()

        endRecord.place_forget()

    window.mainloop()

if __name__ == '__main__':
    def refresh():
        window.destroy()
        vp_start_gui()

    vp_start_gui()
