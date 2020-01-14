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
import signal
import configparser

configparser = configparser.RawConfigParser()   
configparser.read('flc_utils/screens/touchScreen/gui.cfg')

# os.chdir("/home/agnext/Music/darknet")  # Agnext (Desktop icon path issue fix)

is_login = False
userName = ""
cmd = './uselib cfg/jorhat_Dec.names cfg/jorhat_Dec.cfg weights/jorhat_Dec_final.weights web_camera'
cmd_camera_setting = 'ecam_tk1_guvcview'
jetson_clock_cmd = 'jetson_clocks'
record_cam_cmd = "python3 flc_utils/guiHelpers/record_cam_gui.py"
edit_details_cmd = "python3 flc_utils/guiHelpers/farmer_section.py"

def testVal(inStr,acttyp):
    if acttyp == '1': #insert
        if not inStr.isdigit():
            return False
    return True

def vp_start_gui():
    global window
    window = tk.Tk()
    # window.attributes("-fullscreen", True)
    window.title("Fine Leaf Count")

    window.geometry(configparser.get('gui-config', 'window_geometry'))
    window.configure(background='snow')

    # function for video streaming
    def video_stream():
        msg_sent.place_forget()
        tuneCamera.configure(state='disabled', fg="black", bg="silver")
        startCamRecord.configure(state='disabled', fg="black", bg="silver")
        editDetails.configure(state='disabled', fg="black", bg="silver")
        try:
            global p
            p = subprocess.Popen("exec " + cmd, stdout= subprocess.PIPE, shell=True)
            endRecord.configure(bg="#539051", state="active")
            startRecord.place_forget()            
            endRecord.place(x=int(configparser.get('gui-config', 'endrecord_btn_x')), y=int(configparser.get('gui-config', 'endrecord_btn_y')))
        except:
            p.kill()
            endRecord.place_forget()
            startRecord.configure(bg="#539051", state="active")
            refresh()

    def end_video():
        p.terminate()
        p.kill()
        tuneCamera.configure(fg="white", bg="#539051", state='active')
        startCamRecord.configure(fg="white", bg="#539051", state='active')
        editDetails.configure(fg="white", bg="#539051", state='active')
        endRecord.place_forget()
        startRecord.place(x=int(configparser.get('gui-config', 'startrecord_btn_x')), y=int(configparser.get('gui-config', 'startrecord_btn_y')))
        send_data_api()       #send data to api
        sleep(2)
        # refresh()


    def start_record_video():
        startCamRecord.configure(bg='silver', state="disabled")
        cam_record = subprocess.Popen("exec " + record_cam_cmd, stdout= subprocess.PIPE, shell=True)


    def edit_details():
        editDetails.configure(bg='silver', state="disabled")
        details_process = subprocess.Popen("exec " + edit_details_cmd, stdout= subprocess.PIPE, shell=True)

    def set_camera():
        try:
            global csetting
            csetting = subprocess.Popen("exec " + cmd_camera_setting, stdout= subprocess.PIPE, shell=True)
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
        response = requests.request("POST", configparser.get('gui-config', 'ip') + "/api/auth/login", data=json.dumps(payload), headers=headers)
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
        if configparser.get('gui-config', 'internet') == 'true':
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
            resp = requests.request("POST", configparser.get('gui-config', 'ip') + "/api/own-flc", data=json.dumps(load), headers=head)
            saved = resp.json()['success']
        else:
            txt_file = open("result.txt", "r").read()
            li = txt_file.split("\n")

            with open("flc_utils/noInternetFiles/realTimeTesting.logs", "a") as out_file:
                out_file.write("Datetime " + str(datetime.datetime.now())[:-7] + "\n")
                out_file.write(txt_file)
                out_file.write("\n")
            saved = "true"

        if saved == "true":
            msg_sent.configure(text="Data saved", fg="green")
            msg_sent.place(x=int(configparser.get('gui-config', 'data_saved_notification_x')), y=int(configparser.get('gui-config', 'data_saved_notification_y')))
        else:
            msg_sent.configure(text="Couldn't save to servers", fg="red")
            msg_sent.place(x=int(configparser.get('gui-config', 'data_saved_notification_x')), y=int(configparser.get('gui-config', 'data_saved_notification_y')))



    def place_on_screen():

        txt = "Welcome, " + userName.title()
        Label(window, text=txt, font=('times', 15, 'bold'), bg='white').place(x=int(configparser.get('gui-config', 'welcome_text_x')), y=int(configparser.get('gui-config', 'welcome_text_y')))

        refresh_button.place(x=int(configparser.get('gui-config', 'refresh_x')), y=int(configparser.get('gui-config', 'refresh_y')))

        startRecord.place(x=int(configparser.get('gui-config', 'startrecord_btn_x')), y=int(configparser.get('gui-config', 'startrecord_btn_y')))
        tuneCamera.place(x=int(configparser.get('gui-config', 'tunecamera_btn_x')), y=int(configparser.get('gui-config', 'tunecamera_btn_y')))

        startCamRecord.place(x=int(configparser.get('gui-config', 'cam_record_start_x')), y=int(configparser.get('gui-config', 'cam_record_start_y')))
        editDetails.place(x=int(configparser.get('gui-config', 'edit_details_x')), y=int(configparser.get('gui-config', 'edit_details_y')))

    # Designing window for login 
     
    def login():
        x = window.winfo_x()
        y = window.winfo_y()
        global login_screen
        login_screen = Toplevel(window)
        login_screen.title("Login")
        login_screen.geometry("+%d+%d" % (x + int(configparser.get('gui-config', 'login_screen_x')), y + int(configparser.get('gui-config', 'login_screen_y'))))
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
        global jetson_clock
        if configparser.get('gui-config', 'internet') == 'true':
            status = login_api(username1, password1)
            if status == True:
                login_sucess()
                jetson_clock = subprocess.Popen("exec " + jetson_clock_cmd, stdout= subprocess.PIPE, shell=True)
            else:
                user_not_found()
        else:
            list_of_files = os.listdir("flc_utils/noInternetFiles/")
            if username1 in list_of_files:
                file1 = open("flc_utils/noInternetFiles/"+username1, "r")
                verify = file1.read().splitlines()
                if password1 in verify:
                    global userName
                    userName = username1
                    login_sucess()
                    jetson_clock = subprocess.Popen("exec " + jetson_clock_cmd, stdout= subprocess.PIPE, shell=True)
                else:
                    password_not_recognised()

            else:
                user_not_found()

        
     
    # Designing popup for login success
     
    def login_sucess():
        global is_login
        is_login = True
        username_login_entry.place_forget()
        password_login_entry.place_forget()
        signin.place_forget()
        panel_bg.place_forget()
        place_on_screen()

    # Designing popup for login invalid password
     
    def password_not_recognised():
        x = window.winfo_x()
        y = window.winfo_y()
        w = 150
        h = 60  
          
        global password_not_recog_screen
        password_not_recog_screen = Toplevel(window)
        password_not_recog_screen.geometry("%dx%d+%d+%d" % (w, h, x + 300, y + 200))
        password_not_recog_screen.title("Error")
        Label(password_not_recog_screen, text="Invalid Password ").pack()
        Button(password_not_recog_screen, text="OK", command=delete_password_not_recognised).pack()
     
    # Designing popup for user not found
     
    def user_not_found():
        x = window.winfo_x()
        y = window.winfo_y()
        w = 150
        h = 60

        global user_not_found_screen
        user_not_found_screen = Toplevel(window)
        user_not_found_screen.geometry("%dx%d+%d+%d" % (w, h, x + 300, y + 200))
        user_not_found_screen.title("Error")
        Label(user_not_found_screen, text="User Not Found").pack()
        Button(user_not_found_screen, text="OK", command=delete_user_not_found_screen).pack()
     
    # Deleting popups
     
    def delete_login_success():
        login_success_screen.destroy()
     
     
    def delete_password_not_recognised():
        password_not_recog_screen.destroy()
     
     
    def delete_user_not_found_screen():
        user_not_found_screen.destroy()

    window.protocol("WM_DELETE_WINDOW", on_closing)

    message = tk.Label(window, text="Fine Leaf Count System                          ", fg="white", bg="#539051", width=int(configparser.get('gui-config', 'title_width')), height=int(configparser.get('gui-config', 'title_height')), font=('times', 30, 'bold'))
    message.place(x=int(configparser.get('gui-config', 'title_x')), y=int(configparser.get('gui-config', 'title_y')))

    img = ImageTk.PhotoImage(Image.open(configparser.get('gui-config', 'logo')))
    panel = Label(window, image = img, bg='#539051')
    panel.place(x=int(configparser.get('gui-config', 'login_image_x')), y=int(configparser.get('gui-config', 'login_image_y')))
    
    tuneCamera = tk.Button(window, text="Camera Setting", command=set_camera, fg="white", bg="#539051", width=int(configparser.get('gui-config', 'buttons_width')),height=int(configparser.get('gui-config', 'buttons_height')), activebackground = "Grey" , font=('times', 15, 'bold'))

    refresh_button = tk.Button(window, text="Refresh", command=refresh, fg="white", bg="#539051", width=int(configparser.get('gui-config', 'refresh_width')),height=1, activebackground = "Grey" , font=('times', 10, 'bold'))

    startRecord = tk.Button(window, text="Start Testing", command=video_stream, fg="white", bg="#539051", width=int(configparser.get('gui-config', 'buttons_width')),height=int(configparser.get('gui-config', 'buttons_height')), activebackground = "Grey" , font=('times', 15, 'bold'))
    endRecord = tk.Button(window, text="Save & restart", command=end_video, fg="white", bg="#539051", width=int(configparser.get('gui-config', 'buttons_width')),height=int(configparser.get('gui-config', 'buttons_height')), activebackground = "Grey" , font=('times', 15, 'bold'))

    startCamRecord = tk.Button(window, text="Record training video", command=start_record_video, fg="white", bg="#539051", width=int(configparser.get('gui-config', 'buttons_width')),height=int(configparser.get('gui-config', 'buttons_height')), activebackground = "Grey" , font=('times', 15, 'bold'))
    editDetails = tk.Button(window, text="Edit details", command=edit_details, fg="white", bg="#539051", width=int(configparser.get('gui-config', 'buttons_width')),height=int(configparser.get('gui-config', 'buttons_height')), activebackground = "Grey" , font=('times', 15, 'bold'))

    msg_sent = Label(window, text="Data sent status", font=('times', 15), fg="green", bg='white')

    def detail_fxn():
        pass

    def qr_scan_fxn():
        pass

    def clear_search_1(event):
        username_login_entry.delete(0, tk.END)

    def clear_search_2(event):
        password_login_entry.delete(0, tk.END)
     
    global username_verify
    global password_verify
     
    username_verify = StringVar()
    password_verify = StringVar()
     
    global username_login_entry
    global password_login_entry
   
    username_login_entry = Entry(window, textvariable=username_verify)
    username_login_entry.insert(1, "Enter username")
    username_login_entry.bind("<Button-1>", clear_search_1)
    
    password_login_entry = Entry(window, textvariable=password_verify, show= '*')
    password_login_entry.insert(1, "Enter password")
    password_login_entry.bind("<Button-1>", clear_search_2)
    
    
    signin = tk.Button(window, text="Login", command=login_verify, fg="white", bg="#539051", width=int(configparser.get('gui-config', 'signin_btn_width')),height=int(configparser.get('gui-config', 'signin_btn_height')), activebackground = "Grey" , font=('times', 15, 'bold'))

    if is_login == True:

        signin.place_forget()
        username_login_entry.place_forget()
        password_login_entry.place_forget()
        place_on_screen()

    else:
        username_login_entry.place(x=570, y=200)
        password_login_entry.place(x=570, y=230)

        global panel_bg
        img_bg = ImageTk.PhotoImage(Image.open(configparser.get('gui-config', 'bg_image')))
        panel_bg = Label(window, image = img_bg, bg='white')
        panel_bg.place(x=int(configparser.get('gui-config', 'panel_bg_x')), y=int(configparser.get('gui-config', 'panel_bg_y')))

        signin.place(x=int(configparser.get('gui-config', 'signin_btn_x')), y=int(configparser.get('gui-config', 'signin_btn_y')))

        startRecord.place_forget()
        endRecord.place_forget()

        startCamRecord.place_forget()
        editDetails.place_forget()

    window.mainloop()

if __name__ == '__main__':
    def refresh():
        window.destroy()
        vp_start_gui()

    vp_start_gui()
