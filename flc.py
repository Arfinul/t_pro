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
import threading
from flc_utils import helper
import logging

logging.basicConfig(filename='server_logs.log',
                    filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(("FLC"))

configparser = configparser.RawConfigParser()   
os.chdir("/home/agnext/Documents/flc")

configparser.read('flc_utils/screens/touchScreen/gui.cfg')

USE_INTERNET = configparser.get('gui-config', 'internet')

cmd = """
export LD_LIBRARY_PATH=/home/agnext/Documents/flc/
./uselib cfg/jorhat_Dec.names cfg/jorhat_Dec.cfg weights/jorhat_Dec_final.weights web_camera > output.txt
"""

pwd = configparser.get('gui-config', 'sys_password')
jetson_clock_cmd = 'jetson_clocks'


class MyTkApp(tk.Frame):

    def __init__(self, master):  
        tk.Frame.__init__(self, master)   
        self.token = ""
        self.customer_id = ''
        self.garden_id_name_dict = {}
        self.section_id_name_dict = {}
        self.division_id_name_dict = {}
        self.region_id_name_dict = {}
        self.center_id_name_dict = {}
        self.SECTION_OPTIONS = ["Select section ID"]
        self.GARDEN_OPTIONS = ["Select garden ID"]
        self.DIVISION_OPTIONS = ["Select division ID"] 
        self.REGIONS_OPTIONS = ['Select Region']
        self.INSTCENTER_OPTIONS = ['Select Inst Center']
        self.options_displayed = False
        self.new_fields = {}

        self.window = master
        self.x = self.window.winfo_x()
        self.y = self.window.winfo_y()
        self.w = 300
        self.h = 100

        self.window.title("Fine Leaf Count")
        self.window.geometry(configparser.get('gui-config', 'window_geometry'))
        self.window.configure(background='snow')
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.header = tk.Label(self.window, text="   Fine Leaf Count", fg="white", bg="#539051", width=int(configparser.get('gui-config', 'title_width')), height=int(configparser.get('gui-config', 'title_height')), font=('times', 30, 'bold'))
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

        self.endRecord = tk.Button(self.window, text="Save", command=self.end_video, fg="white", bg="#539051", font=('times', 17, 'bold'), width=10, height=2)

        self.msg_sent = Label(self.window, text="", font=('times', 15), fg="green", bg='white')

        self._flc_btn = tk.Button(self.window, text="flc", command=self.do_nothing, fg="white", bg="#12B653", width=int(configparser.get('gui-config', 'result_btn_width')),height=int(configparser.get('gui-config', 'result_btn_height')), font=('times', 20, 'bold'))
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

        self.section_verify = StringVar()
        self.garden_verify = StringVar()
        self.division_verify = StringVar()
        self.section_verify.set("Select section ID")
        self.garden_verify.set("Select garden ID")
        self.division_verify.set("Select division ID")
         
        self.garden_entry = OptionMenu(self.window, self.garden_verify, *self.GARDEN_OPTIONS)
        self.garden_entry.configure(width=24, state="disabled", font=font.Font(family='Helvetica', size=16))
        self.division_entry = OptionMenu(self.window, self.division_verify, *self.DIVISION_OPTIONS)
        self.division_verify.trace("w", self.get_sections)
        self.division_entry.configure(width=24, state="disabled", font=font.Font(family='Helvetica', size=16))
        self.sector_entry = OptionMenu(self.window, self.section_verify, *self.SECTION_OPTIONS)
        self.sector_entry.configure(width=24, state="disabled", font=font.Font(family='Helvetica', size=16))

        self.welcome_text = Label(self.window, text="Welcome, ", font=('times', 15, 'bold'), bg="#f7f0f5")
        self.entered = tk.Button(self.window, text="Start FLC", command=self.details_verify, fg="white", bg="#539051", width=int(configparser.get('gui-config', 'signin_btn_width')),height=int(configparser.get('gui-config', 'signin_btn_height')), font=('times', 16, 'bold'))
        self.formula = Label(self.window, text="FLC = 1LB + 2LB + 1Banjhi", font=("Helvetica", 15), background='white')

        img = ImageTk.PhotoImage(Image.open(configparser.get('gui-config', 'logo')))
        self.panel.configure(image=img)
        self.panel.image = img

        self.header.place(x=int(configparser.get('gui-config', 'title_x')), y=int(configparser.get('gui-config', 'title_y')))
        self.panel.place(x=int(configparser.get('gui-config', 'login_image_x')), y=int(configparser.get('gui-config', 'login_image_y')))
        self.footer.place(x=0, y=420)

        img_bg = ImageTk.PhotoImage(Image.open(configparser.get('gui-config', 'bg_image')))
        self.panel_bg.configure(image=img_bg)
        self.panel_bg.image = img_bg
        self.panel_bg.place(x=int(configparser.get('gui-config', 'panel_bg_x')), y=int(configparser.get('gui-config', 'panel_bg_y')))

        self.username_login_entry.place(x=565, y=130, width=184, height=30)
        self.password_login_entry.place(x=565, y=165, width=184, height=30)
        self.signin.place(x=int(configparser.get('gui-config', 'signin_btn_x')), y=int(configparser.get('gui-config', 'signin_btn_y')))

        self.username_login_entry.bind("<Button-1>", self.action_1)
        self.password_login_entry.bind("<Button-1>", self.action_2)

        self.endRecord.place_forget()

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

        self.weight_label = Label(self.window, text="Weight:", font=('times', label_font_size, 'bold'), bg="#f7f0f5")
        self.weight_entry = Entry(self.window, textvariable=self.weight_verify)
        self.weight_entry.configure(font=font.Font(family='Helvetica', size=entry_font_size))
        self.weight_entry.bind("<Button-1>", self.action_weight)

        self.sample_id_label = Label(self.window, text="Sample ID:", font=('times', label_font_size, 'bold'), bg="#f7f0f5")
        self.sample_id_entry = Entry(self.window, textvariable=self.sample_id_verify)
        self.sample_id_entry.configure(font=font.Font(family='Helvetica', size=entry_font_size))
        self.sample_id_entry.bind("<Button-1>", self.action_sampleid)

        self.lot_id_label = Label(self.window, text="Lot ID:", font=('times', label_font_size, 'bold'), bg="#f7f0f5")
        self.lot_id_entry = Entry(self.window, textvariable=self.lot_id_verify)
        self.lot_id_entry.configure(font=font.Font(family='Helvetica', size=entry_font_size))
        self.lot_id_entry.bind("<Button-1>", self.action_lotid)

        self.device_serial_no_label = Label(self.window, text="Device Serial No.:", font=('times', label_font_size, 'bold'), bg="#f7f0f5")
        self.device_serial_no_entry = Entry(self.window, textvariable=self.device_serial_no_verify)
        self.device_serial_no_entry.configure(font=font.Font(family='Helvetica', size=entry_font_size))
        self.device_serial_no_entry.bind("<Button-1>", self.action_deviceserialno)

        self.batch_id_label = Label(self.window, text="Batch ID:", font=('times', label_font_size, 'bold'), bg="#f7f0f5")
        self.batch_id_entry = Entry(self.window, textvariable=self.batch_id_verify)
        self.batch_id_entry.configure(font=font.Font(family='Helvetica', size=entry_font_size))
        self.batch_id_entry.bind("<Button-1>", self.action_batchid)

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
        try:
            subprocess.Popen("exec " + 'echo {} | sudo -S {}'.format(pwd, jetson_clock_cmd), stdout= subprocess.PIPE, shell=True)
        except Exception as e:
            logger.exception(str('Exception occured in "start_jetson_fan" function\nError message:' + str(e)))

    def details_entered_success(self):
        try:
            self.endRecord.place_forget()
            self.entered.place_forget()
            self.sector_entry.place_forget()
            self.garden_entry.place_forget()
            self.division_entry.place_forget()
            self.msg_sent.place_forget()
        except Exception as e:
            logger.exception(str('Exception occured in "details_entered_success" function\nError message:' + str(e)))
    
    def display_all_options(self):
        try:
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
        except Exception as e:
            logger.exception(str('Exception occured in "display_all_options" function\nError message:' + str(e)))

    def start_testing(self, command):
        try:
            p = subprocess.Popen("exec " + command, stdout= subprocess.PIPE, shell=True)
            p.wait()
            os.rename("flc_utils/trainVideo/testing/result.avi", "flc_utils/trainVideo/testing/" + datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S") + "_" + str(self.customer_id) + ".avi")
            self.show_results_on_display()
            self.endRecord.place(x=int(configparser.get('gui-config', 'endrecord_btn_x')), y=int(configparser.get('gui-config', 'endrecord_btn_y')))
        except Exception as e:
            print(e)
            self.endRecord.place_forget()
            logger.exception(str('Exception occured in "start_testing" function\nError message:' + str(e)))

    def end_video(self):
        try:
            self.formula.place_forget()
            self.endRecord.place_forget()
            self.send_data_api()
            self.msg_sent.place(x=int(configparser.get('gui-config', 'data_saved_notification_x')), y=int(configparser.get('gui-config', 'data_saved_notification_y')))
            self.enter_details()
        except Exception as e:
            logger.exception(str('Exception occured in "end_video" function\nError message:' + str(e)))


    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            gc.collect()
            try:
                subprocess.Popen("exec " + "killall onboard", stdout= subprocess.PIPE, shell=True)
            except:
                pass
            self.window.destroy()
            sys.exit()

    def popup_keyboard(self, event):
        try:
            subprocess.Popen("exec " + "onboard", stdout= subprocess.PIPE, shell=True)
        except Exception as e:
            logger.exception(str('Exception occured in "popup_keyboard" function\nError message:' + str(e)))
    
    def get_locations(self):
        try:
            url = "http://23.98.216.140:8072/api/locations"
            headers = {'Authorization': "Bearer " + self.token}
            response = requests.request("GET", url, headers=headers)
            return response.json()[0]['location_id']
        except Exception as e:
            logger.exception(str('Exception occured in "get_locations" function\nError message:' + str(e)))


    def get_gardens(self):
        try:
            garden_id_list, garden_name_list = [], []
            if USE_INTERNET == "TRUE":
                url = "http://23.98.216.140:8072/api/gardens"
                headers = {'Authorization': "Bearer " + self.token}
                querystring = {"locationId": self.get_locations()}
                response = requests.request("GET", url, headers=headers, params=querystring)
                data = response.json()

                garden_id_list = [i["garden_id"] for i in data]
                garden_name_list = [i["name"] for i in data]
            else:
                garden_name_list, garden_id_list = ["Demo Garden"], ["Demo Garden ID"]

            self.garden_id_name_dict = dict(zip(garden_name_list, garden_id_list))
            if len(garden_name_list) == 1:
                self.GARDEN_OPTIONS = garden_name_list
            else:
                self.GARDEN_OPTIONS = ["Select garden ID"] + garden_name_list
            self.garden_entry.place_forget()
            self.garden_entry = OptionMenu(self.window, self.garden_verify, *self.GARDEN_OPTIONS)
            self.garden_verify.trace("w", self.get_divisions)
            self.garden_entry.configure(width=24, state="active", font=font.Font(family='Helvetica', size=16))
            self.garden_entry.place(x=520, y=155, height=40, width=190)  
            menu = self.nametowidget(self.garden_entry.menuname)
            menu.config(font=font.Font(family='Helvetica', size=15)) 
        except Exception as e:
            logger.exception(str('Exception occured in "get_gardens" function\nError message:' + str(e)))

    def get_divisions(self, *args):
        try:
            division_id_list, division_name_list = [], []
            if USE_INTERNET == "TRUE":
                url = "http://23.98.216.140:8072/api/divisions"
                headers = {'Authorization': "Bearer " + self.token}
                garden_id = self.garden_id_name_dict[self.garden_verify.get()]
                querystring = {"gardenId": garden_id}
                response = requests.request("GET", url, headers=headers, params=querystring)
                data = response.json()

                division_id_list = [i["division_id"] for i in data]
                division_name_list = [i["name"] for i in data]
            else:
                division_id_list, division_name_list = ["Demo Division ID"], ["Demo Division"]

            self.division_id_name_dict = dict(zip(division_name_list, division_id_list))
            self.DIVISION_OPTIONS = division_name_list
            self.division_entry.place_forget()
            self.division_entry = OptionMenu(self.window, self.division_verify, *self.DIVISION_OPTIONS)
            self.division_verify.trace("w", self.get_sections)
            self.division_entry.configure(width=24, state="active", font=font.Font(family='Helvetica', size=16))
            self.division_entry.place(x=520, y=200, height=40, width=190)
            menu = self.nametowidget(self.division_entry.menuname)
            menu.config(font=font.Font(family='Helvetica', size=15))
        except Exception as e:
            logger.exception(str('Exception occured in "get_divisions" function\nError message:' + str(e)))
    
    def get_sections(self, *args):
        try:
            section_id_list, section_name_list = [], []
            if USE_INTERNET == "TRUE":
                url = "http://23.98.216.140:8072/api/sections"
                headers = {'Authorization': "Bearer " + self.token}
                division_id = self.division_id_name_dict[self.division_verify.get()]
                querystring = {"divisionId": division_id}
                response = requests.request("GET", url, headers=headers, params=querystring)
                data = response.json()

                section_id_list = [i["section_id"] for i in data]
                section_name_list = [i["name"] for i in data]
            else:
                section_id_list, section_name_list = ["Demo Section ID"], ["Demo Section"]
            self.section_id_name_dict = dict(zip(section_name_list, section_id_list))
            self.SECTION_OPTIONS = ["Select section ID"] + section_name_list
            self.sector_entry.place_forget()
            self.sector_entry = OptionMenu(self.window, self.section_verify, *self.SECTION_OPTIONS)
            self.sector_entry.configure(width=24, state="active", font=font.Font(family='Helvetica', size=16))
            self.sector_entry.place(x=520, y=245, height=40, width=190)
            menu = self.nametowidget(self.sector_entry.menuname)
            menu.config(font=font.Font(family='Helvetica', size=15))
        except Exception as e:
            logger.exception(str('Exception occured in "get_sections" function\nError message:' + str(e)))

    def get_regions(self):
        try:
            region_names, region_ids = [], []
            if USE_INTERNET == "TRUE":
                if helper.is_internet_available():
                    region_names, region_ids = helper.regions_list_qualix(self.customer_id, self.token)
            else:
                region_names, region_ids = ["Demo Region"], ["Demo Region ID"]
            self.REGIONS_OPTIONS = ["Select Region"] + region_names
            self.region_id_name_dict = dict(zip(region_names, region_ids))
            self.region_entry.place_forget()
            self.region_entry = OptionMenu(self.window, self.region_verify, *self.REGIONS_OPTIONS)
            self.region_verify.trace("w", self.get_instcenter)
            self.region_entry.configure(width=24, state="active", font=font.Font(family='Helvetica', size=16))
            menu = self.nametowidget(self.region_entry.menuname)
            menu.config(font=font.Font(family='Helvetica', size=16))
        except Exception as e:
            logger.exception(str('Exception occured in "get_regions" function\nError message:' + str(e)))

    def get_instcenter(self, *args):
        try:
            center_names, center_ids = [], []
            if USE_INTERNET == "TRUE":
                region_id = self.region_id_name_dict[self.region_verify.get()]
                if helper.is_internet_available():
                    center_names, center_ids = helper.inst_centers_list_qualix(region_id, self.customer_id, self.token)
            else:
                center_names, center_ids = ["Demo Center"], ["Demo Center ID"]
            self.INSTCENTER_OPTIONS = ["Select Region"] + center_names
            self.center_id_name_dict = dict(zip(center_names, center_ids))
            self.inst_center_entry.place_forget()
            self.inst_center_entry = OptionMenu(self.window, self.inst_center_verify, *self.INSTCENTER_OPTIONS)
            self.inst_center_entry.configure(width=24, state="active", font=font.Font(family='Helvetica', size=16))
            self.inst_center_entry.place(x=400, y=290)
            menu = self.nametowidget(self.inst_center_entry.menuname)
            menu.config(font=font.Font(family='Helvetica', size=16))
        except Exception as e:
            logger.exception(str('Exception occured in "get_instcenter" function\nError message:' + str(e)))

    def place_inputs(self):
        try:
            self.garden_entry.place(x=520, y=155, height=40, width=190)
            self.division_entry.place(x=520, y=200, height=40, width=190)
            self.sector_entry.place(x=520, y=245, height=40, width=190)
            self.entered.place(x=520, y=305)
        except Exception as e:
            logger.exception(str('Exception occured in "place_inputs" function\nError message:' + str(e)))

    def load_graph(self):
        try:
            self.graph.place(x=int(configparser.get('gui-config', 'graph_image_x')), y=int(configparser.get('gui-config', 'graph_image_y')))
        except Exception as e:
            logger.exception(str('Exception occured in "load_graph" function\nError message:' + str(e)))

    def forget_graph(self):
        self.graph.place_forget()

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

    def action_weight(self, event):
        if self.weight_verify.get() == "Enter Weight":
            self.weight_entry.delete(0, tk.END)
        self.popup_keyboard(event)

    def action_sampleid(self, event):
        if self.sample_id_verify.get() == "Enter Sample ID":
            self.sample_id_entry.delete(0, tk.END)
        self.popup_keyboard(event)

    def action_lotid(self, event):
        if self.lot_id_verify.get() == "Enter Lot ID":
            self.lot_id_entry.delete(0, tk.END)
        self.popup_keyboard(event)

    def action_deviceserialno(self, event):
        if self.device_serial_no_verify.get() == "Enter Device SerialNo":
            self.device_serial_no_entry.delete(0, tk.END)
        self.popup_keyboard(event)

    def action_batchid(self, event):
        if self.batch_id_verify.get() == "Enter Batch ID":
            self.batch_id_entry.delete(0, tk.END)
        self.popup_keyboard(event)


    def send_data_api(self):
        try:
            _1lb, _2lb, _3lb, _1bj, _2bj, _coarse, totalCount, _perc, payload = helper.get_payload()

            if USE_INTERNET == "TRUE":
                sectionId = int(self.section_id_name_dict[self.section_verify.get()])
                qualix_status = 0
                if helper.is_internet_available():
                    qualix_status = helper.qualix_api(payload, sectionId, self.new_fields)
                if qualix_status == 200:
                    self.msg_sent.configure(text="Data saved", fg="green")
                    if helper.is_internet_available():
                        t = threading.Thread(target=helper.update_spreadsheet, args=(_1lb, _2lb, _3lb, _1bj, _2bj, _coarse, totalCount, _perc,))
                        t.start()
                else:
                    self.msg_sent.configure(text="Couldn't save to servers", fg="red")

            helper.free_space()

            self._flc_btn.place_forget()
            # self._total_btn.place_forget()
            # self._1lb_btn.place_forget()
            # self._2lb_btn.place_forget()
            # self._1bj_btn.place_forget()
            # self._3lb_btn.place_forget()
            self._coarse_btn.place_forget()
            # self._2bj_btn.place_forget()

            helper.update_graph()
        except Exception as e:
            logger.exception(str('Exception occured in "send_data_api" function\nError message:' + str(e)))


    def do_nothing(self):
        pass


    def show_results_on_display(self):
        try:
            self.forget_graph()

            _1lb, _2lb, _3lb, _1bj, _2bj, _coarse, totalCount, _perc = helper.get_class_count()

            if totalCount != 0:
                _1lb_perc = round(_1lb*100/totalCount, 2) + 3
                _1lb_perc = 0 if _1lb_perc < 0 else _1lb_perc
                _2lb_perc = round(_2lb*100/totalCount, 2) - 7
                _2lb_perc = 0 if _2lb_perc < 0 else _2lb_perc
                _3lb_perc = round(_3lb*100/totalCount, 2) + 2
                _3lb_perc = 0 if _3lb_perc < 0 else _3lb_perc
                _1bj_perc = round(_1bj*100/totalCount, 2) - 0.7
                _1bj_perc = 0 if _1bj_perc < 0 else _1bj_perc
                _2bj_perc = round(_2bj*100/totalCount, 2)
                _2bj_perc = 0 if _2bj_perc < 0 else _2bj_perc
                _flc_perc = _1lb_perc + _2lb_perc + _1bj_perc + (0.67 * _3lb_perc)
                _flc_perc = 100 if _flc_perc > 100 else _flc_perc
                _coarse_perc = 100 - _flc_perc
                totalCount = int(totalCount * 1.6)
            else:
                _1lb_perc = 0.0
                _2lb_perc = 0.0
                _3lb_perc = 0.0
                _1bj_perc = 0.0
                _2bj_perc = 0.0
                _coarse_perc = 0.0
                _flc_perc = 0.0

            f = open('flc_utils/records.csv','a')
            dt_ = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            flc_ = str(_flc_perc)
            coarse_ = str(_coarse_perc)
            _1lbp = str(_1lb_perc)
            _2lbp = str(_2lb_perc)
            _3lbp = str(_3lb_perc)
            _1bjp = str(_1bj_perc)
            _2bjp = str(_2bj_perc)
            total_ = str(totalCount)
            f.write(f"{dt_},{flc_},{coarse_},{_1lbp},{_2lbp},{_3lbp},{_1bjp},{_2bjp},{total_}\n")
            f.close()

            self._flc_btn.configure(text="FLC %      " + str(round(_flc_perc, 2)))
            self._total_btn.configure(text="Total Leaves     " + str(totalCount))
            self._1lb_btn.configure(text="1LB %         " + str(round(_1lb_perc, 2)))
            self._2lb_btn.configure(text="2LB %         " + str(round(_2lb_perc, 2)))
            self._1bj_btn.configure(text="1Banjhi %      " + str(round(_1bj_perc, 2)))
            self._3lb_btn.configure(text="3LB %        " + str(round(_3lb_perc, 2)))
            self._coarse_btn.configure(text="Coarse %      " + str(round(_coarse_perc, 2)))
            self._2bj_btn.configure(text="2Banjhi %     " + str(round(_2bj_perc, 2)))

            self._flc_btn.place(x=60,y=150)
            # self._flc_btn.place(x=60,y=130) # before
            # self._total_btn.place(x=300,y=130)
            # self._1lb_btn.place(x=60,y=210)
            # self._2lb_btn.place(x=300,y=210)
            # self._1bj_btn.place(x=60,y=270)
            # self._3lb_btn.place(x=300,y=270)
            self._coarse_btn.place(x=60,y=300)
            # self._coarse_btn.place(x=60,y=330) # before
            # self._2bj_btn.place(x=300,y=330)

            self.formula.place(x=60,y=390)
            gc.collect()
        except Exception as e:
            logger.exception(str('Exception occured in "show_results_on_display" function\nError message:' + str(e)))
             
     
    def login_verify(self):
        try:
            # username = self.username_verify.get()
            # password = self.password_verify.get()
            username = "temprobin331@gmail.com"
            password = "Specx123!"
            if USE_INTERNET == "TRUE":
                if helper.is_internet_available():
                    success, self.token, self.customer_id, name = helper.login_api_qualix(username, password)
                    if success:
                        self.login_success()
                        self.welcome_text.configure(text="Welcome, " + name.title())
                    else:
                        self.show_error_msg("User Not Found")
                else:
                    self.show_error_msg("No Internet!")
            else:
                self.login_success()
                self.welcome_text.configure(text="Welcome, Demo")
            
            gc.collect()

        except Exception as e:
            logger.exception(str('Exception occured in "login_verify" function\nError message:' + str(e)))


    def show_error_msg(self, msg):
        self.error_screen = Toplevel(self.window)
        self.error_screen.geometry("%dx%d+%d+%d" % (self.w, self.h, self.x + 300, self.y + 200))
        self.error_screen.title("Error")
        Label(self.error_screen, text=msg, font=('times', 18, 'bold')).pack()
        Button(self.error_screen, text="OK", command=self.delete_error_screen, width=15, font=('times', 16, 'bold')).pack()

    def delete_error_screen(self):
        self.error_screen.destroy()

    def details_verify(self): 
        try:
            gc.collect() 
            # sector = self.section_verify.get()  
            # garden = self.garden_verify.get()
            # division = self.division_verify.get()    
            # if sector not in ["", "Select section ID"] and garden not in ["", "Select garden ID"] and division not in ["", "Select division ID"]:
            self.details_entered_success()
            self.start_testing(cmd)
            # else:
            #     self.show_error_msg("Please fill all details.")
        except Exception as e:
            logger.exception(str('Exception occured in "details_verify" function\nError message:' + str(e)))
     
    def enter_details(self):
        try:
            gph = ImageTk.PhotoImage(Image.open(configparser.get('gui-config', 'graph')))
            self.graph.configure(image=gph)
            self.graph.image = gph
            self.load_graph()
            try:
                subprocess.Popen("exec " + "killall onboard", stdout= subprocess.PIPE, shell=True)
            except:
                pass

            self.GARDEN_OPTIONS = ["Select garden ID"]
            self.garden_entry.configure(width=24, state="active")
            self.get_gardens()

            self.DIVISION_OPTIONS = ["Select division ID"]
            self.division_entry.configure(width=24, state="disabled")

            self.SECTION_OPTIONS = ["Select section ID"]
            self.sector_entry.configure(width=24, state="disabled")

            self.place_inputs()

            self.poweroff.place(x=750, y=80)
        except Exception as e:
            logger.exception(str('Exception occured in "enter_details" function\nError message:' + str(e)))

    def second_screen_place(self):
        try:
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
            batch_id = self.new_fields['batchId'] if 'batchId' in self.new_fields else "Enter Batch ID"
            self.batch_id_entry.insert(1, batch_id)

            self.get_regions()
            self.region_label.place(x=100, y=y_row3-22)
            self.region_entry.place(x=100, y=y_row3)

            self.inst_center_label.place(x=400, y=y_row3-22)
            self.inst_center_entry.configure(width=24, state="disabled")
            self.inst_center_entry.place(x=400, y=y_row3)

            self.nextBtn.place(x=350,y=330)  
            self.poweroff.place(x=750, y=80)  
        except Exception as e:
            logger.exception(str('Exception occured in "second_screen_place" function\nError message:' + str(e)))    

    def second_screen_forget(self):
        try:
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
        except Exception as e:
            logger.exception(str('Exception occured in "second_screen_forget" function\nError message:' + str(e))) 

    def main_screen(self):
        try:
            self.new_fields['area_covered'] = self.area_covered_verify.get()
            self.new_fields['weight'] = self.weight_verify.get()
            self.new_fields['sample_id'] = self.sample_id_verify.get()
            self.new_fields['lot_id'] = self.lot_id_verify.get()
            self.new_fields['region_id'] = self.region_id_name_dict[self.region_verify.get()] if self.region_verify.get() != 'Select Region' else self.region_verify.get()
            self.new_fields['inst_center_id'] = self.center_id_name_dict[self.inst_center_verify.get()] if self.inst_center_verify.get() != 'Select Inst Center' else self.inst_center_verify.get()
            self.new_fields['device_serial_no'] = self.device_serial_no_verify.get()
            self.new_fields['batchId'] = self.batch_id_verify.get()
            # if (self.new_fields['area_covered'] == 'Enter Area Covered') or \
            #     (self.new_fields['weight'] == "Enter Weight") or \
            #     (self.new_fields['sample_id'] == "Enter Sample ID")  or \
            #     (self.new_fields['lot_id'] == "Enter Lot ID") or \
            #     (self.new_fields['region_id'] == "Select Region") or \
            #     (self.new_fields['inst_center_id'] == "Select Inst Center") or \
            #     (self.new_fields['device_serial_no'] == "Enter Device SerialNo") or \
            #     (self.new_fields['batchId'] == "Enter Batch ID"):
            #     self.show_error_msg("Please fill all details.")
            # else:
            self.second_screen_forget()
            self.enter_details()      
            self.start_jetson_fan()
        except Exception as e:
            logger.exception(str('Exception occured in "main_screen" function\nError message:' + str(e)))  

    def login_success(self):
        try:
            self.username_login_entry.place_forget()
            self.password_login_entry.place_forget()
            self.signin.place_forget()
            self.panel_bg.place_forget()
            self.second_screen_place() 
        except Exception as e:
            logger.exception(str('Exception occured in "login_success" function\nError message:' + str(e)))


def launchApp():
    window = tk.Tk()
    MyTkApp(window)
    tk.mainloop()

if __name__=='__main__':
    launchApp()