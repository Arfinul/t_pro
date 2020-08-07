import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import font
import cv2
import os
from PIL import Image,ImageTk
import datetime
import sys
import subprocess   
import requests
import json
import configparser
import math
import gc
import pandas as pd
import matplotlib.pyplot as plt
import sys
import seaborn as sns
import threading
import shutil
import glob
from flask_server import server

PATH = 'reports/*'

create_folders = ['reports', 'reports/1lb', 'reports/2lb', 'reports/3lb', 'reports/1bj', 'reports/2bj', 'reports/coarse', 'reports/cluster']
for folder in create_folders:
    if not os.path.exists(folder):
        os.mkdir(folder)

configparser = configparser.RawConfigParser()   
#os.chdir("/home/agnext/Documents/flc")  # Agnext

configparser.read('flc_utils/screens/touchScreen/gui.cfg')
is_admin = False

cmd = """
export LD_LIBRARY_PATH=/home/agnext/Documents/flc/
./uselib cfg/jorhat_Dec.names cfg/jorhat_Dec.cfg weights/jorhat_Dec_final.weights web_camera > output.txt
"""

cmd_demo = """
export LD_LIBRARY_PATH=/home/agnext/Documents/flc/
./uselib cfg/jorhat_Dec.names cfg/jorhat_Dec.cfg weights/jorhat_Dec_final.weights z_testData/{0} > output.txt
""".format(configparser.get('gui-config', 'demo_video'))

pwd = configparser.get('gui-config', 'sys_password')
cmd_camera_setting = "/usr/local/ecam_tk1/bin/ecam_tk1_guvcview"
reset_camera_setting = "/usr/local/ecam_tk1/bin/ecam_tk1_guvcview --profile=flc_utils/guvcview-config/default.gpfl"
jetson_clock_cmd = 'jetson_clocks'
record_cam_cmd = "python3 flc_utils/guiHelpers/record_cam_gui.py"

def start_server():
    global SERVER
    SERVER = subprocess.Popen("exec " + "python3 flc_server.py", stdout= subprocess.PIPE, shell=True)

class MyTkApp(tk.Frame):

    def __init__(self, master):  
        tk.Frame.__init__(self, master)   
        self.userID = ""
        self.token = ""
        self.farmer_id = ""
        self.factory_id_name_dict = {}
        self.section_id_name_dict = {}
        self.division_id_name_dict = {}
        self.SECTION_OPTIONS = ["Select section ID"]
        self.FACTORY_OPTIONS = ["Select factory"]
        self.DIVISION_OPTIONS = ["Select division ID"] 
        self.options_displayed = False
        self.data = {}

        self.window = master
        self.x = self.window.winfo_x()
        self.y = self.window.winfo_y()
        self.w = 150
        self.h = 60

        self.window.title("Fine Leaf Count")
        self.window.geometry(configparser.get('gui-config', 'window_geometry'))
        self.window.configure(background='snow')
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.header = tk.Label(self.window, text="                                 Fine Leaf Count System", fg="white", bg="#539051", width=int(configparser.get('gui-config', 'title_width')), height=int(configparser.get('gui-config', 'title_height')), font=('times', 30, 'bold'))
        self.footer = tk.Label(self.window, text="                                                    © 2020 Agnext Technologies. All Rights Reserved                                                          ", fg="white", bg="#2b2c28", width=160, height=2, font=('times', 10, 'bold'))

        self.panel = Label(self.window, bg='#539051')
        self.graph = Label(self.window)
        self.panel_bg = Label(self.window, bg='white')

        options_icon = PhotoImage(file = "flc_utils/screens/touchScreen/options.png")
        self.poweroff = tk.Button(self.window, text="Click me!", command=self.display_all_options, image = options_icon, bg="#f7f0f5")
        self.poweroff.image = options_icon

        shutdown_icon = PhotoImage(file = "flc_utils/screens/touchScreen/shutdown.png")
        self.shutdown_button = tk.Button(self.window, command=self.shutdown, image = shutdown_icon, bg="#f7f0f5")
        self.shutdown_button.image = shutdown_icon

        logout_icon = PhotoImage(file = "flc_utils/screens/touchScreen/logout.png")
        self.logout_button = tk.Button(self.window, command=self.logout, image = logout_icon, bg="#f7f0f5")
        self.logout_button.image = logout_icon

        restart_icon = PhotoImage(file = "flc_utils/screens/touchScreen/restart.png")
        self.restart_button = tk.Button(self.window, command=self.restart, image = restart_icon, bg="#f7f0f5")
        self.restart_button.image = restart_icon

        # self.startDemo = tk.Button(self.window, text="Demo Sample", command=self.demo_video, fg="black", bg="#FFE77A", font=('times', 16, 'bold'), width=int(configparser.get('gui-config', 'signin_btn_width')),height=int(configparser.get('gui-config', 'signin_btn_height')))
        self.endRecord = tk.Button(self.window, text="Save", command=self.end_video, fg="white", bg="#539051", font=('times', 17, 'bold'), width=10, height=2)
        if is_admin:
            self.startCamRecord = tk.Button(self.window, text="Record training video", command=self.start_record_video, fg="white", bg="#539051", font=('times', 15, 'bold'))

        self.msg_sent = Label(self.window, text="Data sent status", font=('times', 15), fg="green", bg='white')

        self._flc_btn = tk.Button(self.window, text="flc", command=self.do_nothing, fg="white", bg="#318FCC", width=40,height=10, font=('times', 10, 'bold'))
        self._total_btn = tk.Button(self.window, text="total", command=self.do_nothing, fg="white", bg="#318FCC", width=int(configparser.get('gui-config', 'result_btn_width')),height=int(configparser.get('gui-config', 'result_btn_height')), font=('times', 20, 'bold'))
        self._1lb_btn = tk.Button(self.window, text="1lb", command=self.do_nothing, fg="white", bg="#12B653", width=int(configparser.get('gui-config', 'result_btn_width')),height=int(configparser.get('gui-config', 'result_btn_height')), font=('times', 20, 'bold'))
        self._2lb_btn = tk.Button(self.window, text="2lb", command=self.do_nothing, fg="white", bg="#12B653", width=int(configparser.get('gui-config', 'result_btn_width')),height=int(configparser.get('gui-config', 'result_btn_height')), font=('times', 20, 'bold'))
        self._1bj_btn = tk.Button(self.window, text="1bj", command=self.do_nothing, fg="white", bg="#12B653", width=int(configparser.get('gui-config', 'result_btn_width')),height=int(configparser.get('gui-config', 'result_btn_height')), font=('times', 20, 'bold'))
        self._3lb_btn = tk.Button(self.window, text="3lb", command=self.do_nothing, fg="black", bg="#F3EF62", width=int(configparser.get('gui-config', 'result_btn_width')),height=int(configparser.get('gui-config', 'result_btn_height')), font=('times', 20, 'bold'))
        self._coarse_btn = tk.Button(self.window, text="coarse", command=self.do_nothing, fg="white", bg="#F37C62", width=int(configparser.get('gui-config', 'result_btn_width')),height=int(configparser.get('gui-config', 'result_btn_height')), font=('times', 20, 'bold'))
        self._2bj_btn = tk.Button(self.window, text="2bj", command=self.do_nothing, fg="white", bg="#F37C62", width=int(configparser.get('gui-config', 'result_btn_width')),height=int(configparser.get('gui-config', 'result_btn_height')), font=('times', 20, 'bold'))

        self.username_verify = StringVar()
        self.password_verify = StringVar()
         
        self.username_login_entry = Entry(self.window, textvariable=self.username_verify, font = "Helvetica 15")
        self.username_login_entry.insert(1, "Enter username")

        self.password_login_entry = Entry(self.window, textvariable=self.password_verify, show= '*', font = "Helvetica 15")
        self.password_login_entry.insert(1, "Enter password")
        
        self.signin = tk.Button(self.window, text="Login", command=self.login_verify, fg="white", bg="#539051", width=int(configparser.get('gui-config', 'signin_btn_width')),height=int(configparser.get('gui-config', 'signin_btn_height')), font=("Helvetica 15 bold"))
        
        self._one = tk.Button(self.window, text="1", height=3, width=5, command=lambda val=1:self.code(val))
        self._two = tk.Button(self.window, text="2", height=3, width=5, command=lambda val=2:self.code(val))
        self._three = tk.Button(self.window, text="3", height=3, width=5, command=lambda val=3:self.code(val))
        self._four = tk.Button(self.window, text="4", height=3, width=5, command=lambda val=4:self.code(val))
        self._five = tk.Button(self.window, text="5", height=3, width=5, command=lambda val=5:self.code(val))
        self._six = tk.Button(self.window, text="6", height=3, width=5, command=lambda val=6:self.code(val))
        self._seven = tk.Button(self.window, text="7", height=3, width=5, command=lambda val=7:self.code(val))
        self._eight = tk.Button(self.window, text="8", height=3, width=5, command=lambda val=8:self.code(val))
        self._nine = tk.Button(self.window, text="9", height=3, width=5, command=lambda val=9:self.code(val))
        self._clear = tk.Button(self.window, text="OK", height=3, width=5, command=self.get_farmer_id, fg="white", bg="#539051", font=("Helvetica 10 bold"))
        self._zero = tk.Button(self.window, text="0", height=3, width=5, command=lambda val=0:self.code(val))
        self._back = tk.Button(self.window, text="<--", height=3, width=5, command=self.back_farmer)

        # self.rainy_season = IntVar()
        # self.rainy_season_checkbox = Checkbutton(self.window, text = "Rainy Season", variable = self.rainy_season, onvalue = 1, offvalue = 0, height=3, width = 25)
        
        self.farmer_verify = StringVar()
        self.section_verify = StringVar()
        self.factory_verify = StringVar()
        self.division_verify = StringVar()
        self.section_verify.set("Select section ID")
        self.factory_verify.set("Select factory")
        self.division_verify.set("Select division ID")
         
        self.farmer_entry = Entry(self.window, textvariable=self.farmer_verify)
        self.farmer_entry.configure(font=font.Font(family='Helvetica', size=16))
        self.factory_entry = OptionMenu(self.window, self.factory_verify, *self.FACTORY_OPTIONS)
        self.factory_entry.configure(width=24, state="disabled", font=font.Font(family='Helvetica', size=16))
        self.division_entry = OptionMenu(self.window, self.division_verify, *self.DIVISION_OPTIONS)
        self.division_verify.trace("w", self.get_sections)
        self.division_entry.configure(width=24, state="disabled", font=font.Font(family='Helvetica', size=16))
        self.sector_entry = OptionMenu(self.window, self.section_verify, *self.SECTION_OPTIONS)
        self.sector_entry.configure(width=24, state="disabled", font=font.Font(family='Helvetica', size=16))
        

        self.welcome_text = Label(self.window, text="Welcome, ", font=('times', 15, 'bold'), bg="#f7f0f5")
        self.entered = tk.Button(self.window, text="Test Image", command=self.details_verify, fg="white", bg="#539051", width=int(configparser.get('gui-config', 'signin_btn_width')),height=int(configparser.get('gui-config', 'signin_btn_height')), font=('times', 16, 'bold'))
        self.formula = Label(self.window, text="FLC = 1LB + 2LB + 1Banjhi + (0.5 * 3LB)", font=("Helvetica", 15), background='white')

        img = ImageTk.PhotoImage(Image.open(configparser.get('gui-config', 'logo')))
        self.panel.configure(image=img)
        self.panel.image = img

        self.header.place(x=int(configparser.get('gui-config', 'title_x')), y=int(configparser.get('gui-config', 'title_y')))
        self.panel.place(x=int(configparser.get('gui-config', 'login_image_x')), y=int(configparser.get('gui-config', 'login_image_y')))
        self.footer.place(x=0, y=437)

        img_bg = ImageTk.PhotoImage(Image.open(configparser.get('gui-config', 'bg_image')))
        self.panel_bg.configure(image=img_bg)
        self.panel_bg.image = img_bg
        self.panel_bg.place(x=int(configparser.get('gui-config', 'panel_bg_x')), y=int(configparser.get('gui-config', 'panel_bg_y')))

        self.username_login_entry.place(x=565, y=130, width=184, height=30)
        self.password_login_entry.place(x=565, y=165, width=184, height=30)
        self.signin.place(x=int(configparser.get('gui-config', 'signin_btn_x')), y=int(configparser.get('gui-config', 'signin_btn_y')))

        self.username_login_entry.bind("<Button-1>", self.action_1)
        self.password_login_entry.bind("<Button-1>", self.action_2)

        # self.startDemo.place_forget()
        self.endRecord.place_forget()
        if is_admin:
            self.startCamRecord.place_forget()
        ser = threading.Thread(target=start_server)
        ser.start()


    def restart(self):
        if messagebox.askokcancel("Quit", "Do you really want to restart the system?"):
            self.window.destroy()
            sys.exit()
            subprocess.Popen("exec reboot", stdout= subprocess.PIPE, shell=True)


    def shutdown(self):
        if messagebox.askokcancel("Quit", "Do you really want to shutdown the system?"):
            self.window.destroy()
            sys.exit()
            subprocess.Popen("exec poweroff", stdout= subprocess.PIPE, shell=True)


    def logout(self):
        self.window.destroy()
        launchApp()

    def start_jetson_fan(self):
        subprocess.Popen("exec " + 'echo {} | sudo -S {}'.format(pwd, jetson_clock_cmd), stdout= subprocess.PIPE, shell=True)


    def code(self, value):
        if self.farmer_verify.get() == "Enter farmer Code":
            self.farmer_entry.delete(0, tk.END)
        self.farmer_entry.insert('end', value)


    def remove_numpad(self):
        self._one.place_forget()
        self._two.place_forget()
        self._three.place_forget()
        self._four.place_forget()
        self._five.place_forget()
        self._six.place_forget()
        self._seven.place_forget()
        self._eight.place_forget()
        self._nine.place_forget()
        self._clear.place_forget()
        self._zero.place_forget()
        self._back.place_forget()


    def details_entered_success(self):
        # self.startDemo.place_forget()  
        self.endRecord.place_forget()
        self.entered.place_forget()
        self.farmer_entry.place_forget()
        self.sector_entry.place_forget()
        self.factory_entry.place_forget()
        self.division_entry.place_forget()
        self.msg_sent.place_forget()
        self.poweroff.place_forget()
        self.logout_button.place_forget()
        # self.tuneCamera.place_forget()
        if is_admin:
            self.startCamRecord.place_forget() 
        self.restart_button.place_forget()
        self.shutdown_button.place_forget()
        # self.rainy_season_checkbox.place_forget()
        self.remove_numpad()
        self.start_jetson_fan()
    
    def display_all_options(self):
        if self.options_displayed == False:
            self.logout_button.place(x=int(configparser.get('gui-config', 'logout_x')), y=int(configparser.get('gui-config', 'logout_y')))
            self.restart_button.place(x=int(configparser.get('gui-config', 'restart_x')), y=int(configparser.get('gui-config', 'restart_y')))
            self.shutdown_button.place(x=int(configparser.get('gui-config', 'shutdown_x')), y=int(configparser.get('gui-config', 'shutdown_y')))
            self.options_displayed = True
        else:
            self.logout_button.place_forget()
            self.restart_button.place_forget()
            self.shutdown_button.place_forget()
            self.options_displayed = False


    def start_testing(self, command):
        try:
            import cv2
            os.makedirs('capture', exist_ok=True)
            img_counter = len(os.listdir('capture'))
            cam = cv2.VideoCapture(0)
            ret, frame = cam.read()
            img_name = "capture/{}.png".format(img_counter)
            cv2.imwrite(img_name, frame)
            result = server(img_name)
            print(result)

            self.show_results_on_display(result)
            self.endRecord.place(x=int(configparser.get('gui-config', 'endrecord_btn_x')), y=int(configparser.get('gui-config', 'endrecord_btn_y')))
        except Exception as e:
            print(e)
            # self.endRecord.place_forget()
            # self.startDemo.configure(bg="#539051", state="active")


    def demo_video(self):
        farmer = self.farmer_verify.get()
        sector = self.section_verify.get()  
        factory = self.factory_verify.get()
        division = self.division_verify.get()    
        if farmer not in ["", "Enter farmer Code"] and sector not in ["", "Select section ID"] and factory not in ["", "Select factory"] and division not in ["", "Select division ID"]:
            self.details_entered_success()
            self.start_testing(cmd_demo)
        else:
            self.show_error_msg()
        

    def end_video(self):
        # self.formula.place_forget()
        self.endRecord.place_forget()
        self._flc_btn.place_forget()
        # self.send_data_api()
        # self.msg_sent.place(x=int(configparser.get('gui-config', 'data_saved_notification_x')), y=int(configparser.get('gui-config', 'data_saved_notification_y')))
        self.enter_details()


    def start_record_video(self):
        self.startCamRecord.configure(bg='silver', state="disabled")
        subprocess.Popen("exec " + record_cam_cmd, stdout= subprocess.PIPE, shell=True)


    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            if os.path.exists("result.txt"):
                os.remove("result.txt")
            gc.collect()
            self.window.destroy()
            SERVER.kill()
            sys.exit()


    def clear_search_1(self, event):
        if self.username_verify.get() == "Enter username":
            self.username_login_entry.delete(0, tk.END)


    def clear_search_2(self, event):
        if self.password_verify.get() == "Enter password":
            self.password_login_entry.delete(0, tk.END)


    def popup_keyboard(self, event):
        subprocess.Popen("exec " + "onboard", stdout= subprocess.PIPE, shell=True)
    

    def show_numpad(self, event):
        gc.collect()
        def callback():
            if self.farmer_verify.get() == "Enter farmer Code":
                self.farmer_entry.delete(0, tk.END)
            try:
                # self.startDemo.place_forget()  
                self.endRecord.place_forget()
                self.sector_entry.place_forget()
                self.factory_entry.place_forget()
                self.division_entry.place_forget()
                self.entered.place_forget()
                # self.rainy_season_checkbox.place_forget()
            except:
                pass
            try:
                self._back.place(x=640, y=330)
                self._zero.place(x=585, y=330)
                self._clear.place(x=530, y=330)
                self._one.place(x=640, y=280)
                self._two.place(x=585, y=280)
                self._three.place(x=530, y=280)
                self._four.place(x=640, y=230)
                self._five.place(x=585, y=230)
                self._six.place(x=530, y=230)
                self._seven.place(x=640, y=180)
                self._eight.place(x=585, y=180)
                self._nine.place(x=530, y=180)
            except:
                pass
        t = threading.Thread(target=callback)
        t.start()

    def get_factories(self):
        url = configparser.get('gui-config', 'ip') + "/api/collections?p=0&l=10"
        headers = {
            'Authorization': "Bearer " + self.token
            }
        resp = requests.request("GET", url, headers=headers)
        data = resp.json()['data']
        factory_id_list = [i["id"] for i in data]
        factory_name_list = [i["name"] for i in data]

        self.factory_id_name_dict = dict(zip(factory_name_list, factory_id_list))
        if len(factory_name_list) == 1:
            self.FACTORY_OPTIONS = factory_name_list
        else:
            self.FACTORY_OPTIONS = ["Select factory"] + factory_name_list
        self.factory_entry.place_forget()
        self.factory_entry = OptionMenu(self.window, self.factory_verify, *self.FACTORY_OPTIONS)
        self.factory_entry.configure(width=24, state="active", font=font.Font(family='Helvetica', size=16))
        self.factory_entry.place(x=520, y=155, height=40, width=190)  
        menu = self.nametowidget(self.factory_entry.menuname)
        menu.config(font=font.Font(family='Helvetica', size=15)) 


    def get_sections(self, *args):
        for i in self.data['divisionList']:
            if i['divisionName'] == self.division_verify.get():
                sec_data = i['sectionVO']
        section_id_list = [i["sectionId"] for i in sec_data]
        section_name_list = [i["name"] for i in sec_data]

        self.section_id_name_dict = dict(zip(section_name_list, section_id_list))
        self.SECTION_OPTIONS = ["Select section ID"] + section_name_list
        self.sector_entry.place_forget()
        self.sector_entry = OptionMenu(self.window, self.section_verify, *self.SECTION_OPTIONS)
        self.sector_entry.configure(width=24, state="active", font=font.Font(family='Helvetica', size=16))
        self.sector_entry.place(x=520, y=245, height=40, width=190)
        menu = self.nametowidget(self.sector_entry.menuname)
        menu.config(font=font.Font(family='Helvetica', size=15))


    def get_divisions(self):
        div_data = self.data['divisionList']
        division_id_list = [i["divisionId"] for i in div_data]
        division_name_list = [i["divisionName"] for i in div_data]

        self.division_id_name_dict = dict(zip(division_name_list, division_id_list))
        self.DIVISION_OPTIONS = division_name_list
        self.division_entry = OptionMenu(self.window, self.division_verify, *self.DIVISION_OPTIONS)
        self.division_verify.trace("w", self.get_sections)
        self.division_entry.configure(width=24, state="active", font=font.Font(family='Helvetica', size=16))
        menu = self.nametowidget(self.division_entry.menuname)
        menu.config(font=font.Font(family='Helvetica', size=15))


    def get_farmer_id(self):
        try:
            farmer_code = self.farmer_verify.get()
            url = configparser.get('gui-config', 'ip') + "/api/users/code/" + farmer_code
            headers = {
                'Authorization': "Bearer " + self.token
                }
            resp = requests.request("GET", url, headers=headers)
            self.data = resp.json()['data'][0]
            self.farmer_id = self.data['id']
            self.get_factories()
            self.get_divisions()
            self.hide_numpad()
        except Exception as e:
            print(e)
            self.enter_correct_details()

    def place_inputs(self):
        self.farmer_entry.place(x=520,y=110, height=40, width=190)
        self.factory_entry.place(x=520, y=155, height=40, width=190)
        self.division_entry.place(x=520, y=200, height=40, width=190)
        self.sector_entry.place(x=520, y=245, height=40, width=190)
        self.entered.place(x=520, y=305)
        # self.startDemo.place(x=520, y=360)
        # self.rainy_season_checkbox.place(x=520, y=80)


    def hide_numpad(self):
        gc.collect()
        self.remove_numpad()
        self.place_inputs()


    def load_graph(self):
        self.graph.place(x=int(configparser.get('gui-config', 'graph_image_x')), y=int(configparser.get('gui-config', 'graph_image_y')))


    def forget_graph(self):
        self.graph.place_forget()


    def back_farmer(self):
        val = self.farmer_verify.get()[:-1]
        self.farmer_entry.delete(0, tk.END)
        self.farmer_entry.insert('end', val)

    def action_1(self, event):
        self.clear_search_1(event)
        self.popup_keyboard(event)


    def action_2(self, event):
        self.clear_search_2(event)
        self.popup_keyboard(event)


    def login_api(self, usr, pwd):
        payload = {
            "username": usr,
            "password": pwd,
            "entity": "mobile",
            "deviceToken": "",
        }
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.request("POST", configparser.get('gui-config', 'ip') + "/api/auth/login", data=json.dumps(payload), headers=headers)
        status = False
        try:
            if response.json()['success'] == True:
                self.userID = response.json()["user"]["id"]
                self.token = response.json()['token']
                userName = response.json()["user"]["name"]
                self.welcome_text.configure(text="Welcome, " + userName.title())
                status = True
        except Exception as e:
            print("Exception during login: ", e)
        return status


    def get_class_count(self):
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
        # rainy = int(self.rainy_season.get())

        # try:
        #     if rainy == 0:
        #         print("Non - Rainy season")
        #         _perc = round(((_1lb + _2lb + (_3lb/2) + _1bj) / totalCount)*100, 2)
        #     else:
        #         print("Rainy season")
        #         _perc = round(((_1lb + _2lb + (_3lb*3/4) + _1bj) / totalCount)*100, 2)
        # except Exception as e:
        #     print(e)
        #     _perc = 0

        try:
            _perc = round(((_1lb + _2lb + (_3lb/2) + _1bj) / totalCount)*100, 2)
        except Exception as e:
            print(e)
            _perc = 0

        with open("factor.txt", "w") as factor:
            factor.write("Frame: "+ frame_count + "\n")
            factor.write("1LB: " + str(_1lb) + "\n")
            factor.write("2LB: " + str(_2lb) + "\n")
            factor.write("3LB: " + str(_3lb) + "\n")
            factor.write("1Bj: " + str(_1bj) + "\n")
            factor.write("2Bj: " + str(_2bj) + "\n")
            factor.write("Coarse: " + str(_coarse) + "\n")
            factor.write("Cluster: " + str(_cluster) + "\n")
            factor.write("Total: " + str(totalCount) + "\n")
            factor.write("FLC % " + str(_perc) + "\n")
            factor.write("Time: " + time_taken + "\n")
        gc.collect()
        
        return _1lb, _2lb, _3lb, _1bj, _2bj, _coarse, totalCount, _perc


    def send_data_api(self):
        if configparser.get('gui-config', 'internet') == 'true':
            
            _1lb, _2lb, _3lb, _1bj, _2bj, _coarse, totalCount, _perc = self.get_class_count()

            head = {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + self.token
            }
            load = {
                "userId": int(self.userID),
                "ccId": int(self.factory_id_name_dict[self.factory_verify.get()]),
                "sectionId": int(self.section_id_name_dict[self.section_verify.get()]),
                "assistId": int(self.farmer_id),
                "oneLeafBud": _1lb,
                "twoLeafBud": _2lb,
                "threeLeafBud": _3lb,
                "oneLeafBanjhi": _1bj,
                "twoLeafBanjhi": _2bj,
                "oneBudCount": "0",
                "oneBanjhiCount": "0",
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
            self.msg_sent.configure(text="Data saved", fg="green")
        else:
            self.msg_sent.configure(text="Couldn't save to servers", fg="red")
        self._1lb_btn.place_forget()
        self._2lb_btn.place_forget()
        self._1bj_btn.place_forget()
        self._3lb_btn.place_forget()
        self._coarse_btn.place_forget()
        self._2bj_btn.place_forget()
        self._flc_btn.place_forget()
        self._total_btn.place_forget()

        f = open('flc_utils/records.csv','a')
        f.write(self.section_verify.get() + ',' + str(_perc)+ ',' + datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S") + '\n')
        f.close()

        df = pd.read_csv("flc_utils/records.csv")
        rows = df.shape[0]
        if rows > 9:
            rows = 10
            df = df.iloc[-10:, :]
        fig = plt.figure(figsize=(7,5))
        plot = sns.barplot(df.index, df.FLC)
        plot.set(ylabel='FLC %')
        plt.title("Last " + str(rows) + " FLC results", fontsize=15)
        fig.savefig('flc_utils/result.png')
        cv2_img = cv2.imread("flc_utils/result.png")
        new_img = cv2.resize(cv2_img, (400, 270))
        gc.collect()
        cv2.imwrite("flc_utils/result.png", new_img)


    def do_nothing(self):
        pass


    def show_results_on_display(self, result):
        self.forget_graph()
        text_result = ''
        for i in result:
            text_result += i + ': ' + str(result[i]) + '\n'
        self._flc_btn.configure(text="Result    " + text_result)
        self._flc_btn.place(x=60,y=130)
        gc.collect()
             
     
    def login_verify(self):
        username1 = self.username_verify.get()
        password1 = self.password_verify.get()
        if configparser.get('gui-config', 'internet') == 'true':
            status = self.login_api(username1, password1)
            if status == True:
                self.login_sucess()
            else:
                self.user_not_found()
        else:
            list_of_files = os.listdir("flc_utils/noInternetFiles/")
            if username1 in list_of_files:
                file1 = open("flc_utils/noInternetFiles/"+username1, "r")
                verify = file1.read().splitlines()
                if password1 in verify:
                    self.welcome_text.configure(text="Welcome, " + username1.title())
                    self.login_sucess()
                else:
                    self.password_not_recognised()

            else:
                self.user_not_found()
        gc.collect()


    def show_error_msg(self):
        self.details_not_filled_screen = Toplevel(self.window)
        self.details_not_filled_screen.geometry("%dx%d+%d+%d" % (self.w, self.h, self.x + 300, self.y + 200))
        self.details_not_filled_screen.title("Error")
        Label(self.details_not_filled_screen, text="Please fill all details.").pack()
        Button(self.details_not_filled_screen, text="OK", command=self.delete_details_not_filled_screen).pack()


    def delete_details_not_filled_screen(self):
        self.details_not_filled_screen.destroy()


    def enter_correct_details(self):
        self.enter_correct_details_screen = Toplevel(self.window)
        self.enter_correct_details_screen.geometry("%dx%d+%d+%d" % (self.w, self.h, self.x + 300, self.y + 200))
        self.enter_correct_details_screen.title("Error")
        Label(self.enter_correct_details_screen, text="Please enter correct code.").pack()
        Button(self.enter_correct_details_screen, text="OK", command=self.enter_correct_details_destroy).pack()


    def enter_correct_details_destroy(self):
        self.enter_correct_details_screen.destroy()

    def password_not_recognised(self):
        self.password_not_recog_screen = Toplevel(self.window)
        self.password_not_recog_screen.geometry("%dx%d+%d+%d" % (self.w, self.h, self.x + 300, self.y + 200))
        self.password_not_recog_screen.title("Error")
        Label(self.password_not_recog_screen, text="Invalid Password ").pack()
        Button(self.password_not_recog_screen, text="OK", command=self.delete_password_not_recognised).pack()

     
    def delete_password_not_recognised(self):
        self.password_not_recog_screen.destroy()

    def user_not_found(self):
        self.user_not_found_screen = Toplevel(self.window)
        self.user_not_found_screen.geometry("%dx%d+%d+%d" % (self.w, self.h, self.x + 300, self.y + 200))
        self.user_not_found_screen.title("Error")
        Label(self.user_not_found_screen, text="User Not Found").pack()
        Button(self.user_not_found_screen, text="OK", command=self.delete_user_not_found_screen).pack()
  
     
    def delete_user_not_found_screen(self):
        self.user_not_found_screen.destroy()


    def details_verify(self): 
        gc.collect() 
        # farmer = self.farmer_verify.get()
        # sector = self.section_verify.get()  
        # factory = self.factory_verify.get()
        # division = self.division_verify.get()    
        # if farmer not in ["", "Enter farmer Code"] and sector not in ["", "Select section ID"] and factory not in ["", "Select factory"] and division not in ["", "Select division ID"]:
        self.details_entered_success()
        self.start_testing(cmd)
        # else:
        #     self.show_error_msg()

     
    def enter_details(self):
        gph = ImageTk.PhotoImage(Image.open(configparser.get('gui-config', 'graph')))
        self.graph.configure(image=gph)
        self.graph.image = gph
        self.load_graph()
        try:
            subprocess.Popen("exec " + "killall onboard", stdout= subprocess.PIPE, shell=True)
        except:
            pass

        # self.rainy_season_checkbox.place(x=520, y=80)

        self.welcome_text.place(x=int(configparser.get('gui-config', 'welcome_text_x')), y=int(configparser.get('gui-config', 'welcome_text_y')))
        
        self.farmer_entry.bind("<Button-1>", self.show_numpad)
        self.farmer_entry.delete(0, tk.END)
        self.farmer_entry.insert(1, "Enter farmer Code")

        self.SECTION_OPTIONS = ["Select section ID"]
        self.sector_entry.configure(width=24, state="disabled")

        self.FACTORY_OPTIONS = ["Select factory"]
        self.factory_entry.configure(width=24, state="disabled")

        self.DIVISION_OPTIONS = ["Select division"]
        self.division_entry.configure(width=24, state="disabled")

        self.place_inputs()

        self.poweroff.place(x=750, y=80)

     
    def login_sucess(self):
        self.username_login_entry.place_forget()
        self.password_login_entry.place_forget()
        self.signin.place_forget()
        self.panel_bg.place_forget()
        self.enter_details()       


def launchApp():
    window = tk.Tk()
    MyTkApp(window)
    tk.mainloop()

if __name__=='__main__':
    launchApp()



