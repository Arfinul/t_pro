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
import gc
import pandas as pd
import matplotlib.pyplot as plt
import pyautogui
import sys
import seaborn as sns
import threading

configparser = configparser.RawConfigParser()   
os.chdir("/home/agnext/Documents/flc")  # Agnext

configparser.read('flc_utils/screens/touchScreen/gui.cfg')
is_login = False
details_filled = False
is_admin = False
userName = ""

cmd = """
export LD_LIBRARY_PATH=/home/agnext/Documents/flc/
./uselib cfg/jorhat_Dec.names cfg/jorhat_Dec.cfg weights/jorhat_Dec_final.weights web_camera > output.txt
"""

cmd_demo = """
export LD_LIBRARY_PATH=/home/agnext/Documents/flc/
./uselib cfg/jorhat_Dec.names cfg/jorhat_Dec.cfg weights/jorhat_Dec_final.weights z_testData/57_11Dec_Mix.mp4 > output.txt
"""

pwd = configparser.get('gui-config', 'sys_password')
cmd_camera_setting = "/usr/local/ecam_tk1/bin/ecam_tk1_guvcview"
reset_camera_setting = "/usr/local/ecam_tk1/bin/ecam_tk1_guvcview --profile=flc_utils/guvcview-config/default.gpfl"
jetson_clock_cmd = 'jetson_clocks'
record_cam_cmd = "python3 flc_utils/guiHelpers/record_cam_gui.py"
gc.collect()

def code(value):
    if farmer_verify.get() == "Enter farmer ID":
        farmer_entry.delete(0, tk.END)
    farmer_entry.insert('end', value)
    

def vp_start_gui():
    global window
    window = tk.Tk()
    # window.attributes("-fullscreen", True)
    window.title("Fine Leaf Count")
    window.geometry(configparser.get('gui-config', 'window_geometry'))
    window.configure(background='snow')
    subprocess.Popen("exec " + "onboard", stdout= subprocess.PIPE, shell=True)

    def remove_numpad():
        _one.place_forget()
        _two.place_forget()
        _three.place_forget()
        _four.place_forget()
        _five.place_forget()
        _six.place_forget()
        _seven.place_forget()
        _eight.place_forget()
        _nine.place_forget()
        _clear.place_forget()
        _zero.place_forget()
        _back.place_forget()

    # function for video streaming
    def video_stream():
        msg_sent.place_forget()
        startDemo.place_forget()  
        endRecord.place_forget()
        # tuneCamera.place_forget()
        logout_button.place_forget()
        # restart_button.place_forget()
        # shutdown_button.place_forget()

        remove_numpad()

        if is_admin:
            startCamRecord.place_forget() 
        try:
            global p
            p = subprocess.Popen("exec " + cmd, stdout= subprocess.PIPE, shell=True)
            p.wait()
            show_results_on_display()
            endRecord.place(x=int(configparser.get('gui-config', 'endrecord_btn_x')), y=int(configparser.get('gui-config', 'endrecord_btn_y')))
        except:
            p.kill()
            endRecord.place_forget()
            startDemo.configure(bg="#539051", state="active")
            refresh()

    # function for video streaming
    def demo_video():
        farmer = farmer_verify.get()
        sector = section_verify.get()      
        if farmer not in ["154"] and sector not in ["", "Select section ID"]:
            enter_correct_details()
        elif farmer not in ["", "Enter farmer ID"] and sector not in ["", "Select section ID"]:
            global details_filled
            details_filled = True
            jetson_clock = subprocess.Popen("exec " + 'echo {} | sudo -S {}'.format(pwd, jetson_clock_cmd), stdout= subprocess.PIPE, shell=True)
            msg_sent.place_forget()
            logout_button.place_forget()
            # restart_button.place_forget()
            # shutdown_button.place_forget()

            remove_numpad()
            startDemo.place_forget()  
            endRecord.place_forget()
            entered.place_forget()
            farmer_entry.place_forget()
            sector_entry.place_forget()

            if is_admin:
                startCamRecord.place_forget() 
            try:
                global q
                q = subprocess.Popen("exec " + cmd_demo, stdout= subprocess.PIPE, shell=True)
                q.wait()
                show_results_on_display()
                endRecord.place(x=int(configparser.get('gui-config', 'endrecord_btn_x')), y=int(configparser.get('gui-config', 'endrecord_btn_y')))
            except:
                q.kill()
                endRecord.place_forget()
                startDemo.configure(bg="#539051", state="active")
                refresh()
        else:
            show_error_msg()
        

    def end_video():
        formula.place_forget()
        endRecord.place_forget()
        send_data_api()       #send data to api
        if os.path.exists("result.txt"):
            os.remove("result.txt")
        msg_sent.place(x=int(configparser.get('gui-config', 'data_saved_notification_x')), y=int(configparser.get('gui-config', 'data_saved_notification_y')))
        enter_details()

    def start_record_video():
        startCamRecord.configure(bg='silver', state="disabled")
        cam_record = subprocess.Popen("exec " + record_cam_cmd, stdout= subprocess.PIPE, shell=True)


    def set_camera(type_cam):
        global csetting
        if type_cam == "manual":
            csetting = subprocess.Popen("exec " + cmd_camera_setting, stdout= subprocess.PIPE, shell=True)
        else:
            csetting = subprocess.Popen("exec " + reset_camera_setting, stdout= subprocess.PIPE, shell=True)
            # csetting.kill()

    def set_camera_exit():
        csetting.kill()
        refresh()

    def on_closing():
        from tkinter import messagebox
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            if os.path.exists("result.txt"):
                os.remove("result.txt")
            gc.collect()
            window.destroy()
            sys.exit()

    def clear_search_1(event):
        if username_verify.get() == "Enter username":
            username_login_entry.delete(0, tk.END)

    def clear_search_2(event):
        if password_verify.get() == "Enter password":
            password_login_entry.delete(0, tk.END)
            

    def popup_keyboard(event):
        global pop
        pop = subprocess.Popen("exec " + "onboard", stdout= subprocess.PIPE, shell=True)

    def force_clear_farmer():
        farmer_entry.delete(0, tk.END)

    def show_numpad():
        pyautogui.press('ctrl')
        gc.collect()
        startDemo.place_forget()  
        endRecord.place_forget()
        sector_entry.place_forget()
        entered.place_forget()
        _back.place(x=640, y=350)
        _zero.place(x=585, y=350)
        _clear.place(x=530, y=350)
        _one.place(x=640, y=300)
        _two.place(x=585, y=300)
        _three.place(x=530, y=300)
        _four.place(x=640, y=250)
        _five.place(x=585, y=250)
        _six.place(x=530, y=250)
        _seven.place(x=640, y=200)
        _eight.place(x=585, y=200)
        _nine.place(x=530, y=200)

        if farmer_verify.get() == "Enter farmer ID":
            farmer_entry.delete(0, tk.END)
        pyautogui.press('ctrl')

    def threading_function(event):
        global submit_thread
        submit_thread = threading.Thread(target=show_numpad)
        submit_thread.daemon = True
        submit_thread.start()


    def hide_numpad():
        pyautogui.press('ctrl')
        gc.collect()
        remove_numpad()

        startDemo.place(x=520, y=360)
        sector_entry.place(x=520, y=185, height=40)
        entered.place(x=520, y=280)
        pyautogui.press('ctrl')


    def load_graph():
        graph.place(x=int(configparser.get('gui-config', 'graph_image_x')), y=int(configparser.get('gui-config', 'graph_image_y')))

    def forget_graph():
        graph.place_forget()

    def back_farmer():
        original =  farmer_verify.get()
        farmer_entry.delete(0, tk.END)
        farmer_entry.insert('end', original[:-1])

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

    def get_class_count():
        txt_file = open("result.txt", "r").read()
        li = txt_file.split("\n")
        frame_count = li[0].split(": ")[1]
        _1lb = int(li[1].split(": ")[1])
        _2lb = int(li[2].split(": ")[1])
        _3lb = int(li[3].split(": ")[1]) 
        _1bj = int(li[4].split(": ")[1])
        _2bj = int(li[5].split(": ")[1])
        _cluster = int(li[6].split(": ")[1])
        _coarse = int(li[7].split(": ")[1])
        time_taken = li[9].split(": ")[1]
        # _perc = round(float(li[8].split(": ")[1]), 2)
        # _perc = _perc if math.isnan(float(_perc)) == False else 0

        totalCount = int(_1lb + _2lb + _3lb + _1bj + _2bj + _coarse)

        _1lb = int(round(_1lb * 1.1346, 0))
        _2lb = int(round(_2lb * 1.2006, 0))
        _1bj = int(round(_1bj * 1.3288, 0))
        _3lb = int(round(_3lb * 1.4213, 0))
        _2bj = int(round(_2bj * 0.85, 0))

        _coarse = int(round(_coarse - totalCount * 0.012, 0))
        _coarse = _coarse if _coarse > 0 else 0

        totalCount = _1lb + _2lb + _3lb + _1bj + _2bj + _coarse
        try:
            _perc = round(((_1lb + _2lb + (_3lb/2) + _1bj) / totalCount)*100, 2)
        except:
            _perc = 0

        with open("factor.txt", "w") as factor:
            factor.write("Frame: "+ frame_count + "\n")
            factor.write("1LB: " + str(_1lb) + "\n")
            factor.write("2LB: " + str(_2lb) + "\n")
            factor.write("3LB: " + str(_3lb) + "\n")
            factor.write("1Bj: " + str(_1bj) + "\n")
            factor.write("2Bj: " + str(_2bj) + "\n")
            factor.write("Coarse: " + str(_cluster) + "\n")
            factor.write("Cluster: " + str(_coarse) + "\n")
            factor.write("Total: " + str(totalCount) + "\n")
            factor.write("FLC % " + str(_perc) + "\n")
            factor.write("Time: " + time_taken + "\n")
        gc.collect()
        
        return _1lb, _2lb, _3lb, _1bj, _2bj, _coarse, totalCount, _perc


    def send_data_api():
        if configparser.get('gui-config', 'internet') == 'true':
            
            _1lb, _2lb, _3lb, _1bj, _2bj, _coarse, totalCount, _perc = get_class_count()

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
        else:
            msg_sent.configure(text="Couldn't save to servers", fg="red")
        _1lb_btn.place_forget()
        _2lb_btn.place_forget()
        _1bj_btn.place_forget()
        _3lb_btn.place_forget()
        _coarse_btn.place_forget()
        _2bj_btn.place_forget()
        _flc_btn.place_forget()
        _total_btn.place_forget()

        f = open('flc_utils/records.csv','a')
        f.write(section_verify.get() + ',' + str(_perc)+ ',' + datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S") + '\n')
        f.close()

        df = pd.read_csv("flc_utils/records.csv")
        rows = df.shape[0]
        if rows > 9:
            rows = 10
            df = df.iloc[-10:, :]
        fig = plt.figure(figsize=(7,5))
        plot = sns.barplot(df.index, df.FLC)
        fig.savefig('flc_utils/result.png')
        cv2_img = cv2.imread("flc_utils/result.png")
        new_img = cv2.resize(cv2_img, (400, 270))
        gc.collect()
        cv2.imwrite("flc_utils/result.png", new_img)
        pyautogui.press('ctrl')
        pyautogui.press('ctrl')


    def do_nothing():
        pass

    def show_results_on_display():
        forget_graph()

        _1lb, _2lb, _3lb, _1bj, _2bj, _coarse, totalCount, _perc = get_class_count()


        _flc_btn.configure(text="FLC %      " + str(_perc))
        _total_btn.configure(text="Total Leaves     " + str(totalCount))
        try:
            _1lb_btn.configure(text="1LB %         " + str(round(_1lb*100/totalCount, 2)))
        except Exception as e:
            print(e)
            _1lb_btn.configure(text="1LB %          0")
        try:
            _2lb_btn.configure(text="2LB %         " + str(round(_2lb*100/totalCount, 2)))
        except Exception as e:
            print(e)
            _2lb_btn.configure(text="2LB %        0")
        try:
            _1bj_btn.configure(text="1Banjhi %      " + str(round(_1bj*100/totalCount, 2)))
        except Exception as e:
            print(e)
            _1bj_btn.configure(text="1Banjhi %     0")
        try:
            _3lb_btn.configure(text="3LB %        " + str(round(_3lb*50/totalCount, 2)))
        except Exception as e:
            print(e)
            _3lb_btn.configure(text="3LB %       0")
        try:
            _coarse_btn.configure(text="Coarse %      " + str(round(_coarse*100/totalCount, 2)))
        except Exception as e:
            print(e)
            _coarse_btn.configure(text="Coarse %      0")
        try:
            _2bj_btn.configure(text="2Banjhi %     " + str(round(_2bj*100/totalCount, 2)))
        except Exception as e:
            print(e)
            _2bj_btn.configure(text="2Banjhi %     0")

        _flc_btn.place(x=60,y=130)
        _total_btn.place(x=300,y=130)
        _1lb_btn.place(x=60,y=210)
        _2lb_btn.place(x=300,y=210)
        _1bj_btn.place(x=60,y=270)
        _3lb_btn.place(x=300,y=270)
        _coarse_btn.place(x=60,y=330)
        _2bj_btn.place(x=300,y=330)

        global formula
        formula = Label(window, text="FLC = 1LB + 2LB + 1Banjhi + (0.5 * 3LB)", font=("Helvetica", 15), background='white')
        formula.place(x=60,y=415)
        pyautogui.press('ctrl')
        gc.collect()



    def place_all_buttons():
        logout_button.place(x=int(configparser.get('gui-config', 'logout_x')), y=int(configparser.get('gui-config', 'logout_y')), height=30, width=70)
        # restart_button.place(x=int(configparser.get('gui-config', 'logout_x')), y=int(configparser.get('gui-config', 'restart_y')))
        # shutdown_button.place(x=int(configparser.get('gui-config', 'logout_x')), y=int(configparser.get('gui-config', 'shutdown_y')))

        startDemo.place(x=int(configparser.get('gui-config', 'tunecamera_btn_x')), y=int(configparser.get('gui-config', 'tunecamera_btn_y')), height=35, width=140)
        # tuneCamera.place(x=int(configparser.get('gui-config', 'tunecamera_btn_x')), y=int(configparser.get('gui-config', 'tunecamera_btn_y')), height=35, width=140)

        if is_admin:
            startCamRecord.place(x=int(configparser.get('gui-config', 'cam_record_start_x')), y=int(configparser.get('gui-config', 'cam_record_start_y')), height=35, width=140)

        
    def place_on_screen():
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
        gc.collect()

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
        gc.collect() 
        farmer = farmer_verify.get()
        sector = section_verify.get()      
        if farmer not in ["154"] and sector not in ["", "Select section ID"]:
            enter_correct_details()
        elif farmer not in ["", "Enter farmer ID"] and sector not in ["", "Select section ID"]:
            startDemo.place_forget()  
            endRecord.place_forget()
            entered.place_forget()
            farmer_entry.place_forget()
            sector_entry.place_forget()

            global details_filled
            details_filled = True
            jetson_clock = subprocess.Popen("exec " + 'echo {} | sudo -S {}'.format(pwd, jetson_clock_cmd), stdout= subprocess.PIPE, shell=True)
            video_stream()
        else:
            show_error_msg()

     
    def enter_details():
        load_graph()
        gc.collect()
        try:
            subprocess.Popen("exec " + "killall onboard", stdout= subprocess.PIPE, shell=True)
        except:
            pass

        txt = "Welcome, " + userName.title()
        global welcome_text
        welcome_text = Label(window, text=txt, font=('times', 15, 'bold'), bg='white')
        welcome_text.place(x=int(configparser.get('gui-config', 'welcome_text_x')), y=int(configparser.get('gui-config', 'welcome_text_y')))

        global farmer_verify
        global section_verify
        OPTIONS = ["Select section ID", "1","2","3", "4"] 
         
        farmer_verify = StringVar()
        section_verify = StringVar(window)
        section_verify.set("Select section ID")
         
        global farmer_entry
        global sector_entry
       
        farmer_entry = Entry(window, textvariable=farmer_verify)
        farmer_entry.insert(1, "Enter farmer ID")
        farmer_entry.bind("<Button-1>", threading_function)
        farmer_entry.place(x=520,y=140, height=40, width=190)
        
        sector_entry = OptionMenu(window, section_verify, *OPTIONS)
        sector_entry.configure(width=24)
        sector_entry.place(x=520, y=185, height=40)
        
        global entered
        entered = tk.Button(window, text="Start FLC", command=details_verify, fg="white", bg="#539051", width=int(configparser.get('gui-config', 'signin_btn_width')),height=int(configparser.get('gui-config', 'signin_btn_height')), font=('times', 15, 'bold'))
        entered.place(x=520, y=280)

        startDemo.place(x=520, y=360)

        global _one
        global _two
        global _three
        global _four
        global _five
        global _six
        global _seven
        global _eight
        global _nine
        global _clear
        global _zero
        global _back

        _one = tk.Button(window, text="1", height=3, width=5, command=lambda val=1:code(val))
        _two = tk.Button(window, text="2", height=3, width=5, command=lambda val=2:code(val))
        _three = tk.Button(window, text="3", height=3, width=5, command=lambda val=3:code(val))
        _four = tk.Button(window, text="4", height=3, width=5, command=lambda val=4:code(val))
        _five = tk.Button(window, text="5", height=3, width=5, command=lambda val=5:code(val))
        _six = tk.Button(window, text="6", height=3, width=5, command=lambda val=6:code(val))
        _seven = tk.Button(window, text="7", height=3, width=5, command=lambda val=7:code(val))
        _eight = tk.Button(window, text="8", height=3, width=5, command=lambda val=8:code(val))
        _nine = tk.Button(window, text="9", height=3, width=5, command=lambda val=9:code(val))
        _clear = tk.Button(window, text="OK", height=3, width=5, command=hide_numpad)
        _zero = tk.Button(window, text="0", height=3, width=5, command=lambda val=0:code(val))
        _back = tk.Button(window, text="<--", height=3, width=5, command=back_farmer)

        logout_button.place(x=int(configparser.get('gui-config', 'logout_x')), y=int(configparser.get('gui-config', 'logout_y')))
        # restart_button.place(x=int(configparser.get('gui-config', 'logout_x')), y=int(configparser.get('gui-config', 'restart_y')))
        # shutdown_button.place(x=int(configparser.get('gui-config', 'logout_x')), y=int(configparser.get('gui-config', 'shutdown_y')))
        pyautogui.press('ctrl')
        gc.collect()


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

    def check_cam_selected_option(x):
        if x == "Manual":
            set_camera("manual")
        elif x == "Default":
            set_camera("reset")
        else:
            pass

    def restart():
        subprocess.Popen("exec " + "reboot", stdout= subprocess.PIPE, shell=True)

    def shutdown():
        subprocess.Popen("exec " + "poweroff", stdout= subprocess.PIPE, shell=True)

    window.protocol("WM_DELETE_WINDOW", on_closing)

    message = tk.Label(window, text="                                         Fine Leaf Count System", fg="white", bg="#539051", width=int(configparser.get('gui-config', 'title_width')), height=int(configparser.get('gui-config', 'title_height')), font=('times', 30, 'bold'))
    message.place(x=int(configparser.get('gui-config', 'title_x')), y=int(configparser.get('gui-config', 'title_y')))

    footer = tk.Label(window, text="                                                  © 2020 Agnext Technologies. All Rights Reserved                                                          ", fg="white", bg="#2b2c28", width=160, height=2, font=('times', 10, 'bold'))
    footer.place(x=0, y=437) # 435

    img = ImageTk.PhotoImage(Image.open(configparser.get('gui-config', 'logo')))
    panel = Label(window, image = img, bg='#539051')
    panel.place(x=int(configparser.get('gui-config', 'login_image_x')), y=int(configparser.get('gui-config', 'login_image_y')))

    gc.collect()
    gph = ImageTk.PhotoImage(Image.open(configparser.get('gui-config', 'graph')))

    global graph
    graph = Label(window, image = gph)
    
    # global camera_verify
    # OPTION = ["Camera Settings", "Default", "Manual"] 
     
    # camera_verify = StringVar(window)
    # camera_verify.set("Camera Settings")
    # tuneCamera = OptionMenu(window, camera_verify, *OPTION, command=check_cam_selected_option)
    # tuneCamera.configure(width=15)

    logout_button = tk.Button(window, text="Logout", command=logout, fg="white", bg="#539051", width=int(configparser.get('gui-config', 'refresh_width')), font=('times', 12, 'bold'))

    # restart_button = tk.Button(window, text="Restart", command=restart, fg="white", bg="#DC461D", width=7,font=('times', 12, 'bold'))
    # shutdown_button = tk.Button(window, text="ShutDown", command=shutdown, fg="white", bg="#DC461D", width=7, font=('times', 12, 'bold'))

    startDemo = tk.Button(window, text="Demo Sample", command=demo_video, fg="black", bg="#FFE77A", font=('times', 15, 'bold'), width=int(configparser.get('gui-config', 'signin_btn_width')),height=int(configparser.get('gui-config', 'signin_btn_height')))
    endRecord = tk.Button(window, text="Save", command=end_video, fg="white", bg="#539051", font=('times', 17, 'bold'), width=10, height=2)

    if is_admin:
        startCamRecord = tk.Button(window, text="Record training video", command=start_record_video, fg="white", bg="#539051", font=('times', 15, 'bold'))

    msg_sent = Label(window, text="Data sent status", font=('times', 15), fg="green", bg='white')

    _flc_btn = tk.Button(window, text="flc", command=do_nothing, fg="white", bg="#318FCC", width=int(configparser.get('gui-config', 'result_btn_width')),height=int(configparser.get('gui-config', 'result_btn_height')), font=('times', 20, 'bold'))
    _total_btn = tk.Button(window, text="total", command=do_nothing, fg="white", bg="#318FCC", width=int(configparser.get('gui-config', 'result_btn_width')),height=int(configparser.get('gui-config', 'result_btn_height')), font=('times', 20, 'bold'))
    _1lb_btn = tk.Button(window, text="1lb", command=do_nothing, fg="white", bg="#12B653", width=int(configparser.get('gui-config', 'result_btn_width')),height=int(configparser.get('gui-config', 'result_btn_height')), font=('times', 20, 'bold'))
    _2lb_btn = tk.Button(window, text="2lb", command=do_nothing, fg="white", bg="#12B653", width=int(configparser.get('gui-config', 'result_btn_width')),height=int(configparser.get('gui-config', 'result_btn_height')), font=('times', 20, 'bold'))
    _1bj_btn = tk.Button(window, text="1bj", command=do_nothing, fg="white", bg="#12B653", width=int(configparser.get('gui-config', 'result_btn_width')),height=int(configparser.get('gui-config', 'result_btn_height')), font=('times', 20, 'bold'))
    _3lb_btn = tk.Button(window, text="3lb", command=do_nothing, fg="black", bg="#F3EF62", width=int(configparser.get('gui-config', 'result_btn_width')),height=int(configparser.get('gui-config', 'result_btn_height')), font=('times', 20, 'bold'))
    _coarse_btn = tk.Button(window, text="coarse", command=do_nothing, fg="white", bg="#F37C62", width=int(configparser.get('gui-config', 'result_btn_width')),height=int(configparser.get('gui-config', 'result_btn_height')), font=('times', 20, 'bold'))
    _2bj_btn = tk.Button(window, text="2bj", command=do_nothing, fg="white", bg="#F37C62", width=int(configparser.get('gui-config', 'result_btn_width')),height=int(configparser.get('gui-config', 'result_btn_height')), font=('times', 20, 'bold'))


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
   
    username_login_entry = Entry(window, textvariable=username_verify, font = "Helvetica 15")
    username_login_entry.insert(1, "Enter username")
    username_login_entry.bind("<Button-1>", action_1)
    
    password_login_entry = Entry(window, textvariable=password_verify, show= '*', font = "Helvetica 15")
    password_login_entry.insert(1, "Enter password")
    password_login_entry.bind("<Button-1>", action_2)
    
    
    signin = tk.Button(window, text="Login", command=login_verify, fg="white", bg="#539051", width=int(configparser.get('gui-config', 'signin_btn_width')),height=int(configparser.get('gui-config', 'signin_btn_height')), font=("Helvetica 15 bold"))
    
    if is_login == True and details_filled == True:

        signin.place_forget()
        username_login_entry.place_forget()
        password_login_entry.place_forget()
        enter_details()
        # restart_button.place(x=int(configparser.get('gui-config', 'logout_x')), y=int(configparser.get('gui-config', 'restart_y')))
        # shutdown_button.place(x=int(configparser.get('gui-config', 'logout_x')), y=int(configparser.get('gui-config', 'shutdown_y')))

    else:
        username_login_entry.place(x=545, y=130, width=180, height=30)
        password_login_entry.place(x=545, y=165, width=180, height=30)

        global panel_bg
        img_bg = ImageTk.PhotoImage(Image.open(configparser.get('gui-config', 'bg_image')))
        panel_bg = Label(window, image = img_bg, bg='white')
        panel_bg.place(x=int(configparser.get('gui-config', 'panel_bg_x')), y=int(configparser.get('gui-config', 'panel_bg_y')))

        signin.place(x=int(configparser.get('gui-config', 'signin_btn_x')), y=int(configparser.get('gui-config', 'signin_btn_y')))

        startDemo.place_forget()
        endRecord.place_forget()
        if is_admin:
            startCamRecord.place_forget()

    window.mainloop()

if __name__ == '__main__':
    def refresh():
        window.destroy()
        vp_start_gui()
        pyautogui.press('ctrl')

    def logout():
        global is_login
        is_login = False
        refresh()

    vp_start_gui()
    pyautogui.press('ctrl')


