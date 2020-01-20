import tkinter as tk
from tkinter import *
import cv2
import csv
import os
import numpy as np
from PIL import Image,ImageTk
import datetime
import time
import sys
import subprocess   
from time import sleep
import requests
import json
import signal
import configparser
import math

configparser = configparser.RawConfigParser()   
os.chdir("/home/agnext/Documents/flc")  # Agnext

configparser.read('flc_utils/screens/touchScreen/gui.cfg')
is_login = False
details_filled = False
is_admin = False
userName = ""

cmd = """
export LD_LIBRARY_PATH=/home/agnext/Documents/flc/
./uselib cfg/jorhat_Dec.names cfg/jorhat_Dec.cfg weights/jorhat_Dec_final.weights web_camera
"""

pwd = "qwerty"
cmd_camera_setting = "/usr/local/ecam_tk1/bin/ecam_tk1_guvcview"
jetson_clock_cmd = 'jetson_clocks'
record_cam_cmd = "python3 flc_utils/guiHelpers/record_cam_gui.py"


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
    subprocess.Popen("exec " + "onboard", stdout= subprocess.PIPE, shell=True)

    # function for video streaming
    def video_stream():
        msg_sent.place_forget()
        startRecord.place_forget()  
        endRecord.place_forget()
        tuneCamera.place_forget()
        refresh_button.place_forget()
        logout_button.place_forget()
        if is_admin:
            startCamRecord.place_forget() 
        try:
            global p
            p = subprocess.Popen("exec " + cmd, stdout= subprocess.PIPE, shell=True)
            not_file_found = True
            while(not_file_found):
                if os.path.exists("result.txt"):
                    not_file_found = False
            show_results_on_display()
            endRecord.place(x=int(configparser.get('gui-config', 'endrecord_btn_x')), y=int(configparser.get('gui-config', 'endrecord_btn_y')))
        except:
            p.kill()
            endRecord.place_forget()
            startRecord.configure(bg="#539051", state="active")
            refresh()

    def end_video():
        p.terminate()
        p.kill()
        endRecord.place_forget()
        send_data_api()       #send data to api
        sleep(2)
        if os.path.exists("result.txt"):
            os.remove("result.txt")
        place_all_buttons()


    def start_record_video():
        startCamRecord.configure(bg='silver', state="disabled")
        cam_record = subprocess.Popen("exec " + record_cam_cmd, stdout= subprocess.PIPE, shell=True)


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
            if os.path.exists("result.txt"):
                os.remove("result.txt")
            window.destroy()

    def clear_search_1(event):
        username_login_entry.delete(0, tk.END)

    def clear_search_2(event):
        password_login_entry.delete(0, tk.END)
            

    def popup_keyboard(event):
        global pop
        pop = subprocess.Popen("exec " + "onboard", stdout= subprocess.PIPE, shell=True)

    def clear_farmer(event):
        farmer_entry.delete(0, tk.END)
        popup_keyboard(event)

    def action_1(event):
        clear_search_1(event)
        popup_keyboard(event)

    def action_2(event):
        clear_search_2(event)
        popup_keyboard(event)

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
            
            if response.json()['success'] == True:
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
            _1lb = round(float(li[1].split(": ")[1]), 2)
            _2lb = round(float(li[2].split(": ")[1]), 2)
            _3lb = round(float(li[3].split(": ")[1]), 2)
            _1bj = round(float(li[4].split(": ")[1]), 2)
            _2bj = round(float(li[5].split(": ")[1]), 2)
            _coarse = round(float(li[6].split(": ")[1]), 2)
            _perc = round(float(li[7].split(": ")[1]), 2)
            _perc = _perc if math.isnan(float('nan')) == False else 0
            totalCount = _1lb + _2lb + _3lb + _1bj + _2bj + _coarse

            head = {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            }
            load = {
                "userId": int(userID),
                "ccId": int(section_verify.get()),
                "assistId": int(farmer_verify.get()),
                "oneLeafBud": _1lb,
                "twoLeafBud": _2lb,
                "threeLeafBud": _3lb,
                "oneLeafBanjhi": _1bj,
                "twoLeafBanjhi": _2bj,
                "oneBudCount": "0",
                "oneBanjhiCount": 0,
                "oneLeafCount": "0",
                "twoLeafCount": "0",
                "threeLeafCount": "0",
                "qualityScore": _perc,
                "totalCount": totalCount,
            }
            resp = requests.request("POST", configparser.get('gui-config', 'ip') + "/api/user/scans", data=json.dumps(load), headers=head)
            print(load)
            print(resp.json())
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
        _1lb_btn.place_forget()
        _2lb_btn.place_forget()
        _1bj_btn.place_forget()
        _3lb_btn.place_forget()
        _coarse_btn.place_forget()
        _2bj_btn.place_forget()
        _flc_btn.place_forget()
        _total_btn.place_forget()


    def do_nothing():
        pass

    def show_results_on_display():
        txt_file = open("result.txt", "r").read()
        li = txt_file.split("\n")
        _1lb = round(float(li[1].split(": ")[1]), 2)
        _2lb = round(float(li[2].split(": ")[1]), 2)
        _3lb = round(float(li[3].split(": ")[1]), 2)
        _1bj = round(float(li[4].split(": ")[1]), 2)
        _2bj = round(float(li[5].split(": ")[1]), 2)
        _coarse = round(float(li[6].split(": ")[1]), 2)
        _perc = round(float(li[7].split(": ")[1]), 2)
        _perc = _perc if math.isnan(float('nan')) == False else 0
        totalCount = _1lb + _2lb + _3lb + _1bj + _2bj + _coarse

        _flc_btn.configure(text="FLC % " + str(_perc))
        _total_btn.configure(text="Total " + str(totalCount))
        try:
            _1lb_btn.configure(text="1LB % " + str(math.ceil(_1lb*100/totalCount)))
        except:
            _1lb_btn.configure(text="1LB % 0.0")
        try:
            _2lb_btn.configure(text="2LB % " + str(math.ceil(_2lb*100/totalCount)))
        except:
            _2lb_btn.configure(text="2LB % 0.0")
        try:
            _1bj_btn.configure(text="1Banjhi % " + str(math.ceil(_1bj*100/totalCount)))
        except:
            _1bj_btn.configure(text="1Banjhi % 0.0")
        try:
            _3lb_btn.configure(text="3LB % " + str(math.ceil(_3lb*50/totalCount)))
        except:
            _3lb_btn.configure(text="3LB % 0.0")
        try:
            _coarse_btn.configure(text="Coarse % " + str(math.ceil(_1lb*100/totalCount)))
        except:
            _coarse_btn.configure(text="Coarse % 0.0")
        try:
            _2bj_btn.configure(text="2Banjhi % " + str(math.ceil(_2bj*100/totalCount)))
        except:
            _2bj_btn.configure(text="2Banjhi % 0.0")

        _flc_btn.place(x=150,y=140)
        _total_btn.place(x=300,y=140)
        _1lb_btn.place(x=150,y=195)
        _2lb_btn.place(x=300,y=195)
        _1bj_btn.place(x=150,y=250)
        _3lb_btn.place(x=300,y=250)
        _coarse_btn.place(x=150,y=305)
        _2bj_btn.place(x=300,y=305)


    def place_all_buttons():
        refresh_button.place(x=int(configparser.get('gui-config', 'refresh_x')), y=int(configparser.get('gui-config', 'refresh_y')))
        logout_button.place(x=int(configparser.get('gui-config', 'logout_x')), y=int(configparser.get('gui-config', 'logout_y')))


        startRecord.place(x=int(configparser.get('gui-config', 'startrecord_btn_x')), y=int(configparser.get('gui-config', 'startrecord_btn_y')))
        tuneCamera.place(x=int(configparser.get('gui-config', 'tunecamera_btn_x')), y=int(configparser.get('gui-config', 'tunecamera_btn_y')))

        if is_admin:
            startCamRecord.place(x=int(configparser.get('gui-config', 'cam_record_start_x')), y=int(configparser.get('gui-config', 'cam_record_start_y')))


    def place_on_screen():
        try:
            subprocess.Popen("exec " + "killall onboard", stdout= subprocess.PIPE, shell=True)
        except:
            pass
        try:
            farmer_entry.place_forget()
            sector_entry.place_forget()
            entered.place_forget()
            welcome_text.place_forget()
        except:
            pass
        place_all_buttons()
             
     
    # Implementing event on login button 
     
    def login_verify():
        username1 = username_verify.get()
        password1 = password_verify.get()
        if configparser.get('gui-config', 'internet') == 'true':
            status = login_api(username1, password1)
            if status == True:
                login_sucess()
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
                else:
                    password_not_recognised()

            else:
                user_not_found()

    def show_error_msg():
        x = window.winfo_x()
        y = window.winfo_y()
        w = 150
        h = 60

        global details_not_filled_screen
        details_not_filled_screen = Toplevel(window)
        details_not_filled_screen.geometry("%dx%d+%d+%d" % (w, h, x + 300, y + 200))
        details_not_filled_screen.title("Error")
        Label(details_not_filled_screen, text="Please fill all details.").pack()
        Button(details_not_filled_screen, text="OK", command=delete_details_not_found_screen).pack()

    def delete_details_not_found_screen():
        details_not_filled_screen.destroy()

    def enter_correct_details():
        x = window.winfo_x()
        y = window.winfo_y()
        w = 150
        h = 60

        global enter_correct_details_screen
        enter_correct_details_screen = Toplevel(window)
        enter_correct_details_screen.geometry("%dx%d+%d+%d" % (w, h, x + 300, y + 200))
        enter_correct_details_screen.title("Error")
        Label(enter_correct_details_screen, text="Please enter correct details.").pack()
        Button(enter_correct_details_screen, text="OK", command=enter_correct_details_destroy).pack()

    def enter_correct_details_destroy():
        enter_correct_details_screen.destroy()

    def details_verify():
        farmer = farmer_verify.get()
        sector = section_verify.get()
        
        if farmer not in ["154"] and sector not in ["", "Enter section ID"]:
            enter_correct_details()
        elif farmer not in ["", "Enter farmer ID"] and sector not in ["", "Enter section ID"]:
            global details_filled
            details_filled = True
            jetson_clock = subprocess.Popen("exec " + 'echo {} | sudo -S {}'.format(pwd, jetson_clock_cmd), stdout= subprocess.PIPE, shell=True)
            place_on_screen()
        else:
            show_error_msg()

     
    def enter_details():

        txt = "Welcome, " + userName.title()
        global welcome_text
        welcome_text = Label(window, text=txt, font=('times', 15, 'bold'), bg='white')
        welcome_text.place(x=int(configparser.get('gui-config', 'welcome_text_x')), y=int(configparser.get('gui-config', 'welcome_text_y')))

        global farmer_verify
        global section_verify
        OPTIONS = ["1","2","3", "4"] 
         
        farmer_verify = StringVar()
        section_verify = StringVar(window)
        section_verify.set("Enter section ID")
         
        global farmer_entry
        global sector_entry
       
        farmer_entry = Entry(window, textvariable=farmer_verify)
        farmer_entry.insert(1, "Enter farmer ID")
        farmer_entry.bind("<Button-1>", clear_farmer)
        farmer_entry.place(x=150,y=135, height=30)
        
        sector_entry = OptionMenu(window, section_verify, *OPTIONS)
        sector_entry.place(x=300, y=135, height=30)
        
        global entered
        entered = tk.Button(window, text="Submit", command=details_verify, fg="white", bg="#539051", width=int(configparser.get('gui-config', 'signin_btn_width')),height=1, activebackground = "Grey" , font=('times', 15, 'bold'))
        entered.place(x=450, y=135)

        logout_button.place(x=int(configparser.get('gui-config', 'logout_x')), y=int(configparser.get('gui-config', 'logout_y')))

    # Designing popup for login success
     
    def login_sucess():
        global is_login
        is_login = True
        username_login_entry.place_forget()
        password_login_entry.place_forget()
        signin.place_forget()
        panel_bg.place_forget()
        enter_details()

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
    
    tuneCamera = tk.Button(window, text="Camera Setting", command=set_camera, fg="white", bg="#539051", width=int(configparser.get('gui-config', 'buttons_width')),height=int(configparser.get('gui-config', 'buttons_height')), font=('times', 15, 'bold'))

    refresh_button = tk.Button(window, text="Refresh", command=refresh, fg="white", bg="#539051", width=int(configparser.get('gui-config', 'refresh_width')),height=1, font=('times', 10, 'bold'))
    logout_button = tk.Button(window, text="Logout", command=logout, fg="white", bg="#539051", width=int(configparser.get('gui-config', 'refresh_width')),height=1, font=('times', 10, 'bold'))

    startRecord = tk.Button(window, text="Start", command=video_stream, fg="white", bg="#539051", width=int(configparser.get('gui-config', 'buttons_width')),height=int(configparser.get('gui-config', 'buttons_height')), font=('times', 15, 'bold'))
    endRecord = tk.Button(window, text="Submit", command=end_video, fg="white", bg="#539051", width=int(configparser.get('gui-config', 'buttons_width')),height=int(configparser.get('gui-config', 'buttons_height')), font=('times', 15, 'bold'))

    if is_admin:
        startCamRecord = tk.Button(window, text="Record training video", command=start_record_video, fg="white", bg="#539051", width=int(configparser.get('gui-config', 'buttons_width')),height=int(configparser.get('gui-config', 'buttons_height')), activebackground = "Grey" , font=('times', 15, 'bold'))

    msg_sent = Label(window, text="Data sent status", font=('times', 15), fg="green", bg='white')

    _flc_btn = tk.Button(window, text="flc", command=do_nothing, fg="white", bg="#318FCC", width=int(configparser.get('gui-config', 'result_btn_width')),height=int(configparser.get('gui-config', 'result_btn_height')), font=('times', 15, 'bold'))
    _total_btn = tk.Button(window, text="total", command=do_nothing, fg="white", bg="#318FCC", width=int(configparser.get('gui-config', 'result_btn_width')),height=int(configparser.get('gui-config', 'result_btn_height')), font=('times', 15, 'bold'))
    _1lb_btn = tk.Button(window, text="1lb", command=do_nothing, fg="white", bg="#12B653", width=int(configparser.get('gui-config', 'result_btn_width')),height=int(configparser.get('gui-config', 'result_btn_height')), font=('times', 15, 'bold'))
    _2lb_btn = tk.Button(window, text="2lb", command=do_nothing, fg="white", bg="#12B653", width=int(configparser.get('gui-config', 'result_btn_width')),height=int(configparser.get('gui-config', 'result_btn_height')), font=('times', 15, 'bold'))
    _1bj_btn = tk.Button(window, text="1bj", command=do_nothing, fg="white", bg="#12B653", width=int(configparser.get('gui-config', 'result_btn_width')),height=int(configparser.get('gui-config', 'result_btn_height')), font=('times', 15, 'bold'))
    _3lb_btn = tk.Button(window, text="3lb", command=do_nothing, fg="black", bg="#F3EF62", width=int(configparser.get('gui-config', 'result_btn_width')),height=int(configparser.get('gui-config', 'result_btn_height')), font=('times', 15, 'bold'))
    _coarse_btn = tk.Button(window, text="coarse", command=do_nothing, fg="white", bg="#F37C62", width=int(configparser.get('gui-config', 'result_btn_width')),height=int(configparser.get('gui-config', 'result_btn_height')), font=('times', 15, 'bold'))
    _2bj_btn = tk.Button(window, text="2bj", command=do_nothing, fg="white", bg="#F37C62", width=int(configparser.get('gui-config', 'result_btn_width')),height=int(configparser.get('gui-config', 'result_btn_height')), font=('times', 15, 'bold'))


    def detail_fxn():
        pass

    def qr_scan_fxn():
        pass
     
    global username_verify
    global password_verify
     
    username_verify = StringVar()
    password_verify = StringVar()
     
    global username_login_entry
    global password_login_entry
   
    username_login_entry = Entry(window, textvariable=username_verify)
    username_login_entry.insert(1, "Enter username")
    username_login_entry.bind("<Button-1>", action_1)
    
    password_login_entry = Entry(window, textvariable=password_verify, show= '*')
    password_login_entry.insert(1, "Enter password")
    password_login_entry.bind("<Button-1>", action_2)
    
    
    signin = tk.Button(window, text="Login", command=login_verify, fg="white", bg="#539051", width=int(configparser.get('gui-config', 'signin_btn_width')),height=int(configparser.get('gui-config', 'signin_btn_height')), activebackground = "Grey" , font=('times', 15, 'bold'))
    
    if is_login == True and details_filled == True:

        signin.place_forget()
        username_login_entry.place_forget()
        password_login_entry.place_forget()
        place_on_screen()

    else:
        username_login_entry.place(x=570, y=140)
        password_login_entry.place(x=570, y=170)

        global panel_bg
        img_bg = ImageTk.PhotoImage(Image.open(configparser.get('gui-config', 'bg_image')))
        panel_bg = Label(window, image = img_bg, bg='white')
        panel_bg.place(x=int(configparser.get('gui-config', 'panel_bg_x')), y=int(configparser.get('gui-config', 'panel_bg_y')))

        signin.place(x=int(configparser.get('gui-config', 'signin_btn_x')), y=int(configparser.get('gui-config', 'signin_btn_y')))

        startRecord.place_forget()
        endRecord.place_forget()
        if is_admin:
            startCamRecord.place_forget()

    window.mainloop()

if __name__ == '__main__':
    def refresh():
        window.destroy()
        vp_start_gui()

    def logout():
        global is_login
        is_login = False
        refresh()

    vp_start_gui()



