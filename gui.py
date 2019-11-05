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

is_login = False
userName = ""
cmd = 'time ./uselib cfg/1_black_conveyor.names cfg/5_yolov3_optimised.cfg 5_yolov3_optimised.weights web_camera > output.txt'

def vp_start_gui():
    global window
    window = tk.Tk()
    # window.attributes("-fullscreen", True)
    window.title("Fine Leaf Count")

    window.geometry('1920x1080')
    window.configure(background='snow')

    # function for video streaming
    def video_stream():
        try:
            global p
            p = subprocess.Popen("exec " + cmd, stdout= subprocess.PIPE, shell=True)
            endRecord.configure(state="active", bg="#539051")
            startRecord.configure(state="disabled", bg='silver')
        except:
            p.kill()
            endRecord.configure(state="disabled", bg='silver')
            startRecord.configure(state="active", bg="#539051")
            refresh()

    def end_video():
        p.kill()
        endRecord.configure(state="disabled", bg='silver')
        startRecord.configure(state="active", bg="#539051")
        # send_data_api()       //send data to api
        refresh()

    def on_closing():
        from tkinter import messagebox
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            window.destroy()

    # APIs
    def login_api(usr, pwd):
        url = ""
        data = {
            "username": usr,
            "password": pwd,
            "entity": "mobile",
            "deviceToken": "1"
        }
        response = requests.request("POST", url, params=json.dumps(data))
        print(response.json())
        status = False
        try:
            global userID
            global token
            userID = response.json()["id"]
            token = response.json()['token']
            status = True
        except Exception as e:
            print("Exception during login: ", e)
        return status


    def send_data_api():
        txt_file = open("example.txt", "r").read()
        li = txt_file.split("\n")
        _1lb = li[1].split(" : ")[1]
        _2lb = li[2].split(" : ")[1]
        _3lb = li[3].split(" : ")[1]
        url = ""
        headers = {
        	"application": ""
        }
        data = {
            "flcData": "",
            "sectionId": 1,
            "oneLeafBud": _1lb,
            "twoLeafBud": _2lb,
            "oneLeafBanjhi": "",
            "twoLeafBanjhi": "",
            "moderateShoot": "",
            "fineShoot": "",
            "scannedBy": userID,
            "weighment": "",
            "oneBanjhiCount": "",
            "oneBudCount": "",
            "oneLeafCount": "",
            "twoLeafCount": "",
            "threeLeafCount": "",
            "userId": 1,
            "dateDone": datetime.datetime.today().date()
        }
        response = requests.request("POST", url, params=json.dumps(data), headers=headers)
        print(response.json())



    # Designing window for registration
     
    def register():
        global register_screen
        register_screen = Toplevel(window)
        register_screen.title("Register")
        register_screen.geometry("400x300")
     
        global username
        global password
        global username_entry
        global password_entry
        username = StringVar()
        password = StringVar()
        Label(register_screen, text="").pack()
        Label(register_screen, text="Please enter details below", font=("times", 14, 'bold'), width=30).pack()
        Label(register_screen, text="").pack()
        username_lable = Label(register_screen, text="Username * ", font=("times", 13))
        username_lable.pack()
        username_entry = Entry(register_screen, textvariable=username)
        username_entry.pack()
        password_lable = Label(register_screen, text="Password * ", font=("times", 13))
        password_lable.pack()
        password_entry = Entry(register_screen, textvariable=password, show='*')
        password_entry.pack()
        Label(register_screen, text="").pack()
        Button(register_screen, text="Register", width=10, height=1, bg="salmon", command = register_user, font=("times", 13, 'bold')).pack()
     
     
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
     
    # Implementing event on register button
     
    def register_user():
     
        username_info = username.get()
        password_info = password.get()
     
        file = open(username_info, "w")
        file.write(username_info + "\n")
        file.write(password_info + "\n")
        file.close()
     
        username_entry.delete(0, END)
        password_entry.delete(0, END)
     
        Label(register_screen, text="Registration Success", fg="#539051", font=("calibri", 11)).pack()
     
    # Implementing event on login button 
     
    def login_verify():
        username1 = username_verify.get()
        password1 = password_verify.get()

        # status = login_api(username1, password1)

        username_login_entry.delete(0, END)
        password_login_entry.delete(0, END)
     
        list_of_files = os.listdir()
        if username1 in list_of_files:
            file1 = open(username1, "r")
            verify = file1.read().splitlines()
            if password1 in verify:
                global userName
                userName = username1
                login_sucess()
            else:
                password_not_recognised()
     
        else:
            user_not_found()
     
    # Designing popup for login success
     
    def login_sucess():
        global is_login
        is_login = True
        login_screen.destroy()
        startRecord.place(x=90, y=450)
        endRecord.configure(state="disabled", bg="silver", fg="black")
        endRecord.place(x=90, y=550)
        # register.place_forget()
        signin.place_forget()
        section_gui()
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

    def section_gui():
        # section.configure(state="disabled")
        global section_name
        global section_entry
        global old_button
        section_name = StringVar()
        # name_label = Label(window, text="Please enter section name", font=("times", 14, 'bold'), width=30).place(x=100, y=150)
        section_lable = Label(window, text="Section name * ", font=("times", 13, "bold"))
        section_lable.place(x=180, y=160)
        section_entry = Entry(window, textvariable=section_name)
        section_entry.place(x=140, y=215)
        tk.Button(window, text="Add Section", width=10, height=1, bg="#539051", fg="white", command = add_section, font=("times", 13, 'bold')).place(x=110, y=240)
        tk.Button(window, text="Add Another", width=10, height=1, bg="silver", fg="black", command = refresh, font=("times", 13, 'bold')).place(x=250, y=240)
       
    def add_section():
        global section_success
        section_info = section_name.get()
        if section_info == "":
            section_success = Label(window, text="Can't be empty!", fg="orange", font=("calibri", 11)).place(x=150, y=280)
        else:
            file = open(userName, "a")
            file.write(str(datetime.datetime.now()) + ", ")
            file.write(section_info + "\n")
            file.close()
         
            section_success = Label(window, text=" Section added!", fg="green", font=("calibri", 11)).place(x=150, y=280)

    window.protocol("WM_DELETE_WINDOW", on_closing)

    message = tk.Label(window, text="Fine Leaf Count System", fg="black", bg="#539051", width=85, height=2, font=('times', 30, 'bold'))
    message.place(x=80, y=10)

    img = ImageTk.PhotoImage(Image.open("logo.png"))
    panel = Label(window, image = img, bg='#539051')
    panel.place(x=1350, y=10)
    

    startRecord = tk.Button(window, text="Start", command=video_stream, fg="white", bg="#539051", width=20,height=3, activebackground = "Grey" , font=('times', 15, 'bold'))
    endRecord = tk.Button(window, text="Save & exit", command=end_video, fg="white", bg="#539051", width=20,height=3, activebackground = "Grey" , font=('times', 15, 'bold'))


    if is_login == True:

        section_gui()
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
