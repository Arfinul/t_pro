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
from flc_utils import helper

PATH = 'reports/*'

create_folders = ['reports', 'reports/1lb', 'reports/2lb', 'reports/3lb', 'reports/1bj', 'reports/2bj', 'reports/coarse', 'reports/cluster']
for folder in create_folders:
    if not os.path.exists(folder):
        os.mkdir(folder)

configparser = configparser.RawConfigParser()   
# os.chdir("/home/agnext/Documents/flc")  # Agnext

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


class MyTkApp(tk.Frame):

    def __init__(self, master):  
        tk.Frame.__init__(self, master)   
        self.userID = ""
        self.token = ""
        self.farmer_id = ""
        self.customer_id = ''
        self.factory_id_name_dict = {}
        self.section_id_name_dict = {}
        self.division_id_name_dict = {}
        self.region_id_name_dict = {}
        self.center_id_name_dict = {}
        self.SECTION_OPTIONS = ["Select section ID"]
        self.FACTORY_OPTIONS = ["Select factory"]
        self.DIVISION_OPTIONS = ["Select division ID"] 
        self.REGIONS_OPTIONS = ['Select Region']
        self.INSTCENTER_OPTIONS = ['Select Inst Center']
        self.options_displayed = False
        self.data = {}
        self.new_fields = {}

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

        back_icon = PhotoImage(file = "flc_utils/screens/touchScreen/back.png")
        self.back_button = tk.Button(self.window, command=self.second_screen_place, image = back_icon, bg="#f7f0f5")
        self.back_button.image = back_icon

        shutdown_icon = PhotoImage(file = "flc_utils/screens/touchScreen/shutdown.png")
        self.shutdown_button = tk.Button(self.window, command=self.shutdown, image = shutdown_icon, bg="#f7f0f5")
        self.shutdown_button.image = shutdown_icon

        logout_icon = PhotoImage(file = "flc_utils/screens/touchScreen/logout.png")
        self.logout_button = tk.Button(self.window, command=self.logout, image = logout_icon, bg="#f7f0f5")
        self.logout_button.image = logout_icon

        restart_icon = PhotoImage(file = "flc_utils/screens/touchScreen/restart.png")
        self.restart_button = tk.Button(self.window, command=self.restart, image = restart_icon, bg="#f7f0f5")
        self.restart_button.image = restart_icon

        self.startDemo = tk.Button(self.window, text="Demo Sample", command=self.demo_video, fg="black", bg="#FFE77A", font=('times', 16, 'bold'), width=int(configparser.get('gui-config', 'signin_btn_width')),height=int(configparser.get('gui-config', 'signin_btn_height')))
        self.endRecord = tk.Button(self.window, text="Save", command=self.end_video, fg="white", bg="#539051", font=('times', 17, 'bold'), width=10, height=2)
        if is_admin:
            self.startCamRecord = tk.Button(self.window, text="Record training video", command=self.start_record_video, fg="white", bg="#539051", font=('times', 15, 'bold'))

        self.msg_sent = Label(self.window, text="Data sent status", font=('times', 15), fg="green", bg='white')

        self._flc_btn = tk.Button(self.window, text="flc", command=self.do_nothing, fg="white", bg="#318FCC", width=int(configparser.get('gui-config', 'result_btn_width')),height=int(configparser.get('gui-config', 'result_btn_height')), font=('times', 20, 'bold'))
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

        self.rainy_season = IntVar()
        self.rainy_season_checkbox = Checkbutton(self.window, text = "Rainy Season", variable = self.rainy_season, onvalue = 1, offvalue = 0, height=3, width = 25)
        
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
        self.entered = tk.Button(self.window, text="Start FLC", command=self.details_verify, fg="white", bg="#539051", width=int(configparser.get('gui-config', 'signin_btn_width')),height=int(configparser.get('gui-config', 'signin_btn_height')), font=('times', 16, 'bold'))
        self.formula = Label(self.window, text="FLC = 1LB + 2LB + 1Banjhi + (0.5 * 3LB)", font=("Helvetica", 15), background='white')

        img = ImageTk.PhotoImage(Image.open(configparser.get('gui-config', 'logo')))
        self.panel.configure(image=img)
        self.panel.image = img

        self.header.place(x=int(configparser.get('gui-config', 'title_x')), y=int(configparser.get('gui-config', 'title_y')))
        self.panel.place(x=int(configparser.get('gui-config', 'login_image_x')), y=int(configparser.get('gui-config', 'login_image_y')))
        self.footer.place(x=0, y=450)

        img_bg = ImageTk.PhotoImage(Image.open(configparser.get('gui-config', 'bg_image')))
        self.panel_bg.configure(image=img_bg)
        self.panel_bg.image = img_bg
        self.panel_bg.place(x=int(configparser.get('gui-config', 'panel_bg_x')), y=int(configparser.get('gui-config', 'panel_bg_y')))

        self.username_login_entry.place(x=565, y=130, width=184, height=30)
        self.password_login_entry.place(x=565, y=165, width=184, height=30)
        self.signin.place(x=int(configparser.get('gui-config', 'signin_btn_x')), y=int(configparser.get('gui-config', 'signin_btn_y')))

        self.username_login_entry.bind("<Button-1>", self.action_1)
        self.password_login_entry.bind("<Button-1>", self.action_2)

        self.startDemo.place_forget()
        self.endRecord.place_forget()
        if is_admin:
            self.startCamRecord.place_forget()

        self.area_covered_verify = StringVar()
        self.weight_verify = StringVar()
        self.sample_id_verify = StringVar()
        self.lot_id_verify = StringVar()
        self.device_serial_no_verify = StringVar()
        self.batch_id_verify = StringVar()
        self.region_verify = StringVar()
        self.inst_center_verify = StringVar()
        self.region_verify.set("Select Region")
        self.inst_center_verify.set("Select Inst Center")

        label_font_size = 15
        entry_font_size = 12
        self.area_covered_label = Label(self.window, text="Area covered:", font=('times', label_font_size, 'bold'), bg="#f7f0f5")
        self.area_covered_entry = Entry(self.window, textvariable=self.area_covered_verify)
        self.area_covered_entry.configure(font=font.Font(family='Helvetica', size=entry_font_size))
        self.area_covered_entry.bind("<Button-1>", self.action_area)
        self.area_covered_entry.bind("<FocusOut>", self.lost_focus_area_covered)

        self.weight_label = Label(self.window, text="Weight:", font=('times', label_font_size, 'bold'), bg="#f7f0f5")
        self.weight_entry = Entry(self.window, textvariable=self.weight_verify)
        self.weight_entry.configure(font=font.Font(family='Helvetica', size=entry_font_size))
        self.weight_entry.bind("<Button-1>", self.action_weight)
        self.weight_entry.bind("<FocusOut>", self.lost_focus_weight)

        self.sample_id_label = Label(self.window, text="Sample ID:", font=('times', label_font_size, 'bold'), bg="#f7f0f5")
        self.sample_id_entry = Entry(self.window, textvariable=self.sample_id_verify)
        self.sample_id_entry.configure(font=font.Font(family='Helvetica', size=entry_font_size))
        self.sample_id_entry.bind("<Button-1>", self.action_sampleid)
        self.sample_id_entry.bind("<FocusOut>", self.lost_focus_sample_id)

        self.lot_id_label = Label(self.window, text="Lot ID:", font=('times', label_font_size, 'bold'), bg="#f7f0f5")
        self.lot_id_entry = Entry(self.window, textvariable=self.lot_id_verify)
        self.lot_id_entry.configure(font=font.Font(family='Helvetica', size=entry_font_size))
        self.lot_id_entry.bind("<Button-1>", self.action_lotid)
        self.lot_id_entry.bind("<FocusOut>", self.lost_focus_lot_id)

        self.device_serial_no_label = Label(self.window, text="Device Serial No.:", font=('times', label_font_size, 'bold'), bg="#f7f0f5")
        self.device_serial_no_entry = Entry(self.window, textvariable=self.device_serial_no_verify)
        self.device_serial_no_entry.configure(font=font.Font(family='Helvetica', size=entry_font_size))
        self.device_serial_no_entry.bind("<Button-1>", self.action_deviceserialno)
        self.device_serial_no_entry.bind("<FocusOut>", self.lost_focus_device_serial_no)

        self.batch_id_label = Label(self.window, text="Batch ID:", font=('times', label_font_size, 'bold'), bg="#f7f0f5")
        self.batch_id_entry = Entry(self.window, textvariable=self.batch_id_verify)
        self.batch_id_entry.configure(font=font.Font(family='Helvetica', size=entry_font_size))
        self.batch_id_entry.bind("<Button-1>", self.action_batchid)
        self.batch_id_entry.bind("<FocusOut>", self.lost_focus_batch_id)

        self.region_label = Label(self.window, text="Region:", font=('times', label_font_size, 'bold'), bg="#f7f0f5")
        self.region_entry = OptionMenu(self.window, self.region_verify, *self.REGIONS_OPTIONS)
        self.region_entry.configure(width=24, state="active", font=font.Font(family='times', size=16))

        self.inst_center_label = Label(self.window, text="Installation Center:", font=('times', label_font_size, 'bold'), bg="#f7f0f5")
        self.inst_center_entry = OptionMenu(self.window, self.inst_center_verify, *self.INSTCENTER_OPTIONS)
        self.inst_center_entry.configure(width=24, state="active", font=font.Font(family='times', size=16))

        self.nextBtn = tk.Button(self.window, text="Next", command=self.main_screen, fg="white", bg="#F37C62", width=12,height=2, font=('times', 16, 'bold'))



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
        self.startDemo.place_forget()  
        self.endRecord.place_forget()
        self.entered.place_forget()
        self.farmer_entry.place_forget()
        self.sector_entry.place_forget()
        self.factory_entry.place_forget()
        self.division_entry.place_forget()
        self.msg_sent.place_forget()
        # self.poweroff.place_forget()
        # self.back_button.place_forget()
        # self.logout_button.place_forget()
        # self.restart_button.place_forget()
        # self.shutdown_button.place_forget()
        # self.rainy_season_checkbox.place_forget()
        self.remove_numpad()
    
    def display_all_options(self):
        if self.options_displayed == False:
            self.back_button.place(x=int(configparser.get('gui-config', 'back_x')), y=int(configparser.get('gui-config', 'back_y')))
            self.logout_button.place(x=int(configparser.get('gui-config', 'logout_x')), y=int(configparser.get('gui-config', 'logout_y')))
            self.restart_button.place(x=int(configparser.get('gui-config', 'restart_x')), y=int(configparser.get('gui-config', 'restart_y')))
            self.shutdown_button.place(x=int(configparser.get('gui-config', 'shutdown_x')), y=int(configparser.get('gui-config', 'shutdown_y')))
            self.options_displayed = True
        else:
            self.back_button.place_forget()
            self.logout_button.place_forget()
            self.restart_button.place_forget()
            self.shutdown_button.place_forget()
            self.options_displayed = False


    def start_testing(self, command):
        for i in glob.glob(PATH):
            files = glob.glob(i + '/*')
            for file in files:
                os.remove(file)
        try:
            p = subprocess.Popen("exec " + command, stdout= subprocess.PIPE, shell=True)
            p.wait()
            os.rename("flc_utils/trainVideo/testing/result.avi", "flc_utils/trainVideo/testing/" + str(self.userID) + "_" + datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ".avi")
            self.show_results_on_display()
            self.endRecord.place(x=int(configparser.get('gui-config', 'endrecord_btn_x')), y=int(configparser.get('gui-config', 'endrecord_btn_y')))
        except Exception as e:
            print(e)
            self.endRecord.place_forget()
            self.startDemo.configure(bg="#539051", state="active")


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
        self.formula.place_forget()
        self.endRecord.place_forget()
        self.send_data_api()
        if os.path.exists("result.txt"):
            os.remove("result.txt")
        self.msg_sent.place(x=int(configparser.get('gui-config', 'data_saved_notification_x')), y=int(configparser.get('gui-config', 'data_saved_notification_y')))
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
            sys.exit()

    def popup_keyboard(self, event):
        subprocess.Popen("exec " + "onboard", stdout= subprocess.PIPE, shell=True)
    

    def show_numpad(self, event):
        gc.collect()
        def callback():
            if self.farmer_verify.get() == "Enter farmer Code":
                self.farmer_entry.delete(0, tk.END)
            try:
                self.startDemo.place_forget()  
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


    def get_regions(self):
        # helper.token_api_qualix()
        # success, token, self.customer_id = helper.login_api_qualix()
        customer_id, token = 91, "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2VtYWlsIjoiZGVtb29wZXJhdG9yQGdtYWlsLmNvbSIsInVzZXJfZm5hbWUiOiJPcGVyYXRvciIsInVzZXJfbmFtZSI6ImRlbW9vcGVyYXRvckBnbWFpbC5jb20iLCJjdXN0b21lcl91dWlkIjoiOGE1YTU2YTAtNGY0MS00YTFjLWFiMTQtNmQ1MWFlNjIyZDBiIiwicm9sZXMiOlsib3BlcmF0b3IiXSwiaXNzIjoiUXVhbGl4IiwidXNlcl9sbmFtZSI6Ik9wZXJhdG9yIiwiY2xpZW50X2lkIjoiY2xpZW50LW1vYmlsZSIsInVzZXJfdXVpZCI6Ijc3Nzk3NTkwLTlmMzYtNDM5Ni1iMTA2LTcwNThiZjFkMTc3ZiIsInVzZXJfdHlwZSI6IkNVU1RPTUVSIiwidXNlcl9pZCI6MTg4LCJ1c2VyX21vYmlsZSI6Ijk2NTY1ODU2OTUiLCJzY29wZSI6WyJhbGwiXSwidXNlcl9oaWVyYXJjaHkiOm51bGwsImN1c3RvbWVyX25hbWUiOiJEZW1vIGN1c3RvbWVyIiwiZXhwIjoxNjAxMDAxMDA2LCJjdXN0b21lcl9pZCI6OTEsImp0aSI6IjQ4YTZmZGI5LTcxZTgtNDEwMi04ZTQ5LTRjOGU2ZDVlY2YzYyJ9.PVmAvB5fqQD2qSiT3pHzqNfuShQ2P5Ly9heBrY02Ldpn9X4Q3ciPwx7LV7md1t871wuRylTAjS-_VHEDlGjKDo3Q1ZkhR8fDWT7jWPKLPbX0SX2pCZtCzHKFbTk4giGP1W1QACvVi-VKBUZw5fHglk8V7uqDyqJ80N-8ouSofLfwdoaZhFzrAaLT3jVuevRqQGDE5D2Asysx2lUH1-bQNWF3AzaTipqE6fWF9uF0RA0evDve5vQXLpTDEyc4C8DpIWj5ol0-X723cI549ZDYIjrKGIoF2rYSWXGCwTA2gEJ_t8dv4V1xDCPSJ1kQ_VSPpVkUSdpjbEB25OWm7OIr5w"
        region_names, region_ids = helper.regions_list_qualix(customer_id, token)
        self.REGIONS_OPTIONS = ["Select Region"] + region_names

        self.region_id_name_dict = dict(zip(region_names, region_ids))
        self.region_entry.place_forget()
        self.region_entry = OptionMenu(self.window, self.region_verify, *self.REGIONS_OPTIONS)
        self.region_verify.trace("w", self.get_instcenter)
        self.region_entry.configure(width=24, state="active", font=font.Font(family='Helvetica', size=16))
        menu = self.nametowidget(self.region_entry.menuname)
        menu.config(font=font.Font(family='Helvetica', size=16))


    def get_instcenter(self, *args):
        customer_id, token = 91, "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2VtYWlsIjoiZGVtb29wZXJhdG9yQGdtYWlsLmNvbSIsInVzZXJfZm5hbWUiOiJPcGVyYXRvciIsInVzZXJfbmFtZSI6ImRlbW9vcGVyYXRvckBnbWFpbC5jb20iLCJjdXN0b21lcl91dWlkIjoiOGE1YTU2YTAtNGY0MS00YTFjLWFiMTQtNmQ1MWFlNjIyZDBiIiwicm9sZXMiOlsib3BlcmF0b3IiXSwiaXNzIjoiUXVhbGl4IiwidXNlcl9sbmFtZSI6Ik9wZXJhdG9yIiwiY2xpZW50X2lkIjoiY2xpZW50LW1vYmlsZSIsInVzZXJfdXVpZCI6Ijc3Nzk3NTkwLTlmMzYtNDM5Ni1iMTA2LTcwNThiZjFkMTc3ZiIsInVzZXJfdHlwZSI6IkNVU1RPTUVSIiwidXNlcl9pZCI6MTg4LCJ1c2VyX21vYmlsZSI6Ijk2NTY1ODU2OTUiLCJzY29wZSI6WyJhbGwiXSwidXNlcl9oaWVyYXJjaHkiOm51bGwsImN1c3RvbWVyX25hbWUiOiJEZW1vIGN1c3RvbWVyIiwiZXhwIjoxNjAxMDAxMDA2LCJjdXN0b21lcl9pZCI6OTEsImp0aSI6IjQ4YTZmZGI5LTcxZTgtNDEwMi04ZTQ5LTRjOGU2ZDVlY2YzYyJ9.PVmAvB5fqQD2qSiT3pHzqNfuShQ2P5Ly9heBrY02Ldpn9X4Q3ciPwx7LV7md1t871wuRylTAjS-_VHEDlGjKDo3Q1ZkhR8fDWT7jWPKLPbX0SX2pCZtCzHKFbTk4giGP1W1QACvVi-VKBUZw5fHglk8V7uqDyqJ80N-8ouSofLfwdoaZhFzrAaLT3jVuevRqQGDE5D2Asysx2lUH1-bQNWF3AzaTipqE6fWF9uF0RA0evDve5vQXLpTDEyc4C8DpIWj5ol0-X723cI549ZDYIjrKGIoF2rYSWXGCwTA2gEJ_t8dv4V1xDCPSJ1kQ_VSPpVkUSdpjbEB25OWm7OIr5w"
        region_id = self.region_id_name_dict[self.region_verify.get()]
        center_names, center_ids = helper.inst_centers_list_qualix(region_id, customer_id, token)
        self.INSTCENTER_OPTIONS = ["Select Region"] + center_names

        self.center_id_name_dict = dict(zip(center_names, center_ids))
        self.inst_center_entry.place_forget()
        self.inst_center_entry = OptionMenu(self.window, self.inst_center_verify, *self.INSTCENTER_OPTIONS)
        self.inst_center_entry.configure(width=24, state="active", font=font.Font(family='Helvetica', size=16))
        self.inst_center_entry.place(x=400, y=290)
        menu = self.nametowidget(self.inst_center_entry.menuname)
        menu.config(font=font.Font(family='Helvetica', size=16))

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
        self.startDemo.place(x=520, y=360)
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
        if self.username_verify.get() == "Enter username":
            self.username_login_entry.delete(0, tk.END)
        self.popup_keyboard(event)

    def action_2(self, event):
        if self.password_verify.get() == "Enter password":
            self.password_login_entry.delete(0, tk.END)
        self.popup_keyboard(event)

    def kill_keyboard(self, event):
        try:
            subprocess.Popen("exec " + "killall onboard", stdout= subprocess.PIPE, shell=True)
        except:
            pass

    def action_area(self, event):
        if self.area_covered_verify.get() == "Enter Area Covered":
            self.area_covered_entry.delete(0, tk.END)
        self.popup_keyboard(event)

    def lost_focus_area_covered(self, event):
        if self.area_covered_verify.get() == "":
            self.area_covered_entry.insert(1, "Enter Area Covered")
        self.kill_keyboard(event)

    def action_weight(self, event):
        if self.weight_verify.get() == "Enter Weight":
            self.weight_entry.delete(0, tk.END)
        self.popup_keyboard(event)

    def lost_focus_weight(self, event):
        if self.weight_verify.get() == "":
            self.weight_entry.insert(1, "Enter Weight")
        self.kill_keyboard(event)

    def action_sampleid(self, event):
        if self.sample_id_verify.get() == "Enter Sample ID":
            self.sample_id_entry.delete(0, tk.END)
        self.popup_keyboard(event)

    def lost_focus_sample_id(self, event):
        if self.sample_id_verify.get() == "":
            self.sample_id_entry.insert(1, "Enter Sample ID")
        self.kill_keyboard(event)

    def action_lotid(self, event):
        if self.lot_id_verify.get() == "Enter Lot ID":
            self.lot_id_entry.delete(0, tk.END)
        self.popup_keyboard(event)

    def lost_focus_lot_id(self, event):
        if self.lot_id_verify.get() == "":
            self.lot_id_entry.insert(1, "Enter Lot ID")
        self.kill_keyboard(event)

    def action_deviceserialno(self, event):
        if self.device_serial_no_verify.get() == "Enter Device SerialNo":
            self.device_serial_no_entry.delete(0, tk.END)
        self.popup_keyboard(event)

    def lost_focus_device_serial_no(self, event):
        if self.device_serial_no_verify.get() == "":
            self.device_serial_no_entry.insert(1, "Enter Device SerialNo")
        self.kill_keyboard(event)

    def action_batchid(self, event):
        if self.batch_id_verify.get() == "Enter Batch ID":
            self.batch_id_entry.delete(0, tk.END)
        self.popup_keyboard(event)

    def lost_focus_batch_id(self, event):
        if self.batch_id_verify.get() == "":
            self.batch_id_entry.insert(1, "Enter Batch ID")
        self.kill_keyboard(event)


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


    def send_data_api(self):
        ccId = int(self.factory_id_name_dict[self.factory_verify.get()]),
        sectionId = int(self.section_id_name_dict[self.section_verify.get()])
        farmer_code = self.farmer_verify.get()

        saved, payload = helper.get_saved_status(self.token, self.userID, ccId, sectionId, self.farmer_id)
        qualix = helper.qualix_api(payload, sectionId, farmer_code, self.new_fields)

        if saved == "true" and qualix == 200:
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


    def show_results_on_display(self):
        self.forget_graph()

        _1lb, _2lb, _3lb, _1bj, _2bj, _coarse, totalCount, _perc = helper.get_class_count()


        self._flc_btn.configure(text="FLC %      " + str(_perc))
        self._total_btn.configure(text="Total Leaves     " + str(totalCount))
        try:
            self._1lb_btn.configure(text="1LB %         " + str(round(_1lb*100/totalCount, 2)))
        except Exception as e:
            print(e)
            self._1lb_btn.configure(text="1LB %          0")
        try:
            self._2lb_btn.configure(text="2LB %         " + str(round(_2lb*100/totalCount, 2)))
        except Exception as e:
            print(e)
            self._2lb_btn.configure(text="2LB %        0")
        try:
            self._1bj_btn.configure(text="1Banjhi %      " + str(round(_1bj*100/totalCount, 2)))
        except Exception as e:
            print(e)
            self._1bj_btn.configure(text="1Banjhi %     0")
        try:
            self._3lb_btn.configure(text="3LB %        " + str(round(_3lb*50/totalCount, 2)))
        except Exception as e:
            print(e)
            self._3lb_btn.configure(text="3LB %       0")
        try:
            self._coarse_btn.configure(text="Coarse %      " + str(round(_coarse*100/totalCount, 2)))
        except Exception as e:
            print(e)
            self._coarse_btn.configure(text="Coarse %      0")
        try:
            self._2bj_btn.configure(text="2Banjhi %     " + str(round(_2bj*100/totalCount, 2)))
        except Exception as e:
            print(e)
            self._2bj_btn.configure(text="2Banjhi %     0")

        self._flc_btn.place(x=60,y=130)
        self._total_btn.place(x=300,y=130)
        self._1lb_btn.place(x=60,y=210)
        self._2lb_btn.place(x=300,y=210)
        self._1bj_btn.place(x=60,y=270)
        self._3lb_btn.place(x=300,y=270)
        self._coarse_btn.place(x=60,y=330)
        self._2bj_btn.place(x=300,y=330)

        self.formula.place(x=60,y=415)
        gc.collect()
             
     
    def login_verify(self):
        username1 = self.username_verify.get()
        password1 = self.password_verify.get()
        if configparser.get('gui-config', 'internet') == 'true':
            status = self.login_api(username1, password1)
            if status == True:
                self.login_success()
            else:
                self.user_not_found()
        else:
            list_of_files = os.listdir("flc_utils/noInternetFiles/")
            if username1 in list_of_files:
                file1 = open("flc_utils/noInternetFiles/"+username1, "r")
                verify = file1.read().splitlines()
                if password1 in verify:
                    self.welcome_text.configure(text="Welcome, " + username1.title())
                    self.login_success()
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

    def empty_field_error_msg(self):
        self.empty_field_screen = Toplevel(self.window)
        self.empty_field_screen.geometry("%dx%d+%d+%d" % (self.w, self.h, self.x + 300, self.y + 200))
        self.empty_field_screen.title("Error")
        Label(self.empty_field_screen, text="Please fill all details.").pack()
        Button(self.empty_field_screen, text="OK", command=self.delete_empty_field_error_msg_screen).pack()


    def delete_empty_field_error_msg_screen(self):
        self.empty_field_screen.destroy()


    def details_verify(self): 
        gc.collect() 
        farmer = self.farmer_verify.get()
        sector = self.section_verify.get()  
        factory = self.factory_verify.get()
        division = self.division_verify.get()    
        if farmer not in ["", "Enter farmer Code"] and sector not in ["", "Select section ID"] and factory not in ["", "Select factory"] and division not in ["", "Select division ID"]:
            self.details_entered_success()
            self.start_testing(cmd)
        else:
            self.show_error_msg()

     
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

    def second_screen_place(self):
        self.forget_graph()
        self.details_entered_success()
        try:
            subprocess.Popen("exec " + "killall onboard", stdout= subprocess.PIPE, shell=True)
        except:
            pass
        self.welcome_text.place(x=int(configparser.get('gui-config', 'welcome_text_x')), y=int(configparser.get('gui-config', 'welcome_text_y')))

        x_col1, x_col2, x_col3, x_col4 = 70, 300, 520, 650
        y_row1, y_row2, y_row3, y_row4 = 150, 210, 290, 330

        self.area_covered_label.place(x=x_col1, y=y_row1-22)
        self.area_covered_entry.place(x=x_col1, y=y_row1)
        self.area_covered_entry.delete(0, tk.END)
        area_covered = self.new_fields['area_covered'] if 'area_covered' in self.new_fields else "Enter Area Covered"
        self.area_covered_entry.insert(1, area_covered)

        self.weight_label.place(x=x_col2, y=y_row1-22)
        self.weight_entry.place(x=x_col2, y=y_row1)
        self.weight_entry.delete(0, tk.END)
        weight = self.new_fields['weight'] if 'weight' in self.new_fields else "Enter Weight"
        self.weight_entry.insert(1, weight)

        self.sample_id_label.place(x=x_col3, y=y_row1-22)
        self.sample_id_entry.place(x=x_col3, y=y_row1)
        self.sample_id_entry.delete(0, tk.END)
        sample_id = self.new_fields['sample_id'] if 'sample_id' in self.new_fields else "Enter Sample ID"
        self.sample_id_entry.insert(1, sample_id)

        self.lot_id_label.place(x=x_col1, y=y_row2-22)
        self.lot_id_entry.place(x=x_col1, y=y_row2)
        self.lot_id_entry.delete(0, tk.END)
        lot_id = self.new_fields['lot_id'] if 'lot_id' in self.new_fields else "Enter Lot ID"
        self.lot_id_entry.insert(1, lot_id)

        self.device_serial_no_label.place(x=x_col2, y=y_row2-22)
        self.device_serial_no_entry.place(x=x_col2, y=y_row2)
        self.device_serial_no_entry.delete(0, tk.END)
        device_serial_no = self.new_fields['device_serial_no'] if 'device_serial_no' in self.new_fields else "Enter Device SerialNo"
        self.device_serial_no_entry.insert(1, device_serial_no)

        self.batch_id_label.place(x=x_col3, y=y_row2-22)
        self.batch_id_entry.place(x=x_col3, y=y_row2)
        self.batch_id_entry.delete(0, tk.END)
        batch_id = self.new_fields['batch_id'] if 'batch_id' in self.new_fields else "Enter Batch ID"
        self.batch_id_entry.insert(1, batch_id)

        self.get_regions()
        self.region_label.place(x=100, y=y_row3-22)
        self.region_entry.place(x=100, y=y_row3)

        self.inst_center_label.place(x=400, y=y_row3-22)
        self.inst_center_entry.configure(width=24, state="disabled")
        self.inst_center_entry.place(x=400, y=y_row3)

        self.nextBtn.place(x=350,y=330)  
        self.poweroff.place(x=750, y=80)      

    def second_screen_forget(self):
        self.area_covered_label.place_forget()
        self.area_covered_entry.place_forget()
        self.weight_label.place_forget()
        self.weight_entry.place_forget()
        self.sample_id_label.place_forget()
        self.sample_id_entry.place_forget()
        self.lot_id_label.place_forget()
        self.lot_id_entry.place_forget()
        self.region_label.place_forget()
        self.region_entry.place_forget()
        self.inst_center_label.place_forget()
        self.inst_center_entry.place_forget()
        self.device_serial_no_label.place_forget()
        self.device_serial_no_entry.place_forget()
        self.batch_id_label.place_forget()
        self.batch_id_entry.place_forget()

        self.nextBtn.place_forget()

    def main_screen(self):
        self.new_fields['area_covered'] = self.area_covered_verify.get()
        self.new_fields['weight'] = self.weight_verify.get()
        self.new_fields['sample_id'] = self.sample_id_verify.get()
        self.new_fields['lot_id'] = self.lot_id_verify.get()
        self.new_fields['region_id'] = self.region_id_name_dict[self.region_verify.get()] if self.region_verify.get() != 'Select Region' else self.region_verify.get()
        self.new_fields['inst_center_id'] = self.center_id_name_dict[self.inst_center_verify.get()] if self.inst_center_verify.get() != 'Select Inst Center' else self.inst_center_verify.get()
        self.new_fields['device_serial_no'] = self.device_serial_no_verify.get()
        self.new_fields['batch_id'] = self.batch_id_verify.get()
        if (self.new_fields['area_covered'] == 'Enter Area Covered') or \
            (self.new_fields['weight'] == "Enter Weight") or \
            (self.new_fields['sample_id'] == "Enter Sample ID")  or \
            (self.new_fields['lot_id'] == "Enter Lot ID") or \
            (self.new_fields['region_id'] == "Select Region") or \
            (self.new_fields['inst_center_id'] == "Select Inst Center") or \
            (self.new_fields['device_serial_no'] == "Enter Device SerialNo") or \
            (self.new_fields['batch_id'] == "Enter Batch ID"):
            self.empty_field_error_msg()
        else:
            self.second_screen_forget()
            self.enter_details()      
            self.start_jetson_fan()

    def login_success(self):
        self.username_login_entry.place_forget()
        self.password_login_entry.place_forget()
        self.signin.place_forget()
        self.panel_bg.place_forget()
        self.second_screen_place() 


def launchApp():
    window = tk.Tk()
    MyTkApp(window)
    tk.mainloop()

if __name__=='__main__':
    launchApp()



