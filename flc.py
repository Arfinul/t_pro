# cython: language_level=3

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
import numpy as np
import serial
import time
import re

os.chdir("/home/agnext/Documents/tragnext")

logging.basicConfig(filename='server_logs.log',
                    filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(("FLC"))

configparser = configparser.RawConfigParser()   

#HOME = os.environ["HOME"]
#DIR_PATH = os.path.join(HOME, "Documents", "tragnext")
#os.chdir(DIR_PATH)

def cam_fresh():
    subprocess.Popen("python3 flc_utils/guvcview-config/cam_initialise.py", stdout= subprocess.PIPE, shell=True)

th = threading.Thread(target=cam_fresh)
th.start()

configparser.read('flc_utils/screens/touchScreen/gui.cfg')

USE_INTERNET = configparser.get('gui-config', 'internet')

cmd = """
export LD_LIBRARY_PATH=/home/agnext/Documents/tragnext/
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
        self.LEAF_OPTIONS = ["Select Leaf Type", "Own", "Bought"]
        self.options_displayed = True
        self.new_fields = {}
        self.results = {}
        self.analysis_params = {}

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
        
        self.footer = tk.Label(self.window, text="© 2021 Agnext Technologies. All Rights Reserved", fg="white", bg="#2b2c28", width=160, height=2, font=('times', 10, 'bold'))

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

        self.endRecord = tk.Button(self.window, text="Save", command=self.end_video, fg="white", bg="#539051", font=('times', 17, 'bold'), width=15, height=2)

        self.msg_sent = Label(self.window, text="", font=('times', 15), fg="green", bg='white')

        self._flc_btn = tk.Button(self.window, text="flc", command=self.do_nothing, fg="white", bg="#12B653", width=int(configparser.get('gui-config', 'result_btn_width')),height=int(configparser.get('gui-config', 'result_btn_height')), font=('times', 14, 'bold'))

        self._coarse_btn = tk.Button(self.window, text="coarse", command=self.do_nothing, fg="white", bg="#F37C62", width=int(configparser.get('gui-config', 'result_btn_width')),height=int(configparser.get('gui-config', 'result_btn_height')), font=('times', 14, 'bold')) 
        
        self.username_verify = StringVar()
        self.password_verify = StringVar()
         
        self.username_login_entry = Entry(self.window, textvariable=self.username_verify, font = "Helvetica 15")
        self.username_login_entry.insert(1, "tea002.op@agnext.in")

        self.password_login_entry = Entry(self.window, textvariable=self.password_verify, show= '*', font = "Helvetica 15")
        self.password_login_entry.insert(1, "tea002")
        
        self.signin = tk.Button(self.window, text="Login", command=self.login_verify, fg="white", bg="#539051", width=int(configparser.get('gui-config', 'signin_btn_width')),height=int(configparser.get('gui-config', 'signin_btn_height')), font=("Helvetica 15 bold"))

         
        self.welcome_text = Label(self.window, text="Welcome, ", font=('times', 15, 'bold'), bg="#f7f0f5")
        self.by_count_text = Label(self.window, text="By Count ", font=('times', 20, 'bold'), bg="#f7f0f5")
        self.by_weight_text = Label(self.window, text="By Weight ", font=('times', 20, 'bold'), bg="#f7f0f5")
        self.entered = tk.Button(self.window, text="Start FLC", command=self.details_verify, fg="white", bg="#539051", width=int(configparser.get('gui-config', 'start_flc_width')),height=int(configparser.get('gui-config', 'start_flc_height')), font=('times', 16, 'bold'))
        self.formula = Label(self.window, text="FLC = 1LB + 2LB + 1Banjhi + 0.67 * 3LB", font=("Helvetica", 15), background='white')
        self.warning_sign = Label(self.window, text="", font=('times', 15, 'bold'), fg="red", bg="white")

        img = ImageTk.PhotoImage(Image.open(configparser.get('gui-config', 'logo')))
        self.panel.configure(image=img)
        self.panel.image = img

        self.header.place(x=int(configparser.get('gui-config', 'title_x')), y=int(configparser.get('gui-config', 'title_y')))
        self.panel.place(x=int(configparser.get('gui-config', 'login_image_x')), y=int(configparser.get('gui-config', 'login_image_y')))
        self.footer.place(x=1, y=560)

        img_bg = ImageTk.PhotoImage(Image.open(configparser.get('gui-config', 'bg_image')))
        self.panel_bg.configure(image=img_bg)
        self.panel_bg.image = img_bg
        self.panel_bg.place(x=int(configparser.get('gui-config', 'panel_bg_x')), y=int(configparser.get('gui-config', 'panel_bg_y')))

        self.username_login_entry.place(x=565, y=130, width=184, height=30)
        self.password_login_entry.place(x=565, y=165, width=184, height=30)
        self.signin.place(x=int(configparser.get('gui-config', 'signin_btn_x')), y=int(configparser.get('gui-config', 'signin_btn_y')))

        self.username_login_entry.bind("<Button-1>", self.action_1)
        self.password_login_entry.bind("<Button-1>", self.action_2)

        self.leaf_verify = StringVar()
        self.leaf_verify.set("Select Leaf Type")
        self.section_id_verify = StringVar()
        self.lot_weight_verify = StringVar()
        self.vehicle_no_verify = StringVar()
        
        label_font_size = 15
        entry_font_size = 12

        self.leaf_entry = OptionMenu(self.window, self.leaf_verify, *self.LEAF_OPTIONS)
        self.leaf_entry.configure(width=15, state="active", font=font.Font(family='Helvetica', size=16))
        self.leaf_verify.trace("w", self.show_options)

        self.section_id_label =  Label(self.window, text="Section ID:", font=('times', label_font_size, 'bold'), bg="#f7f0f5")
        self.section_id_entry = Entry(self.window, textvariable=self.section_id_verify)
        self.section_id_entry.configure(font=font.Font(family='Helvetica', size=entry_font_size), state="disabled")
        self.section_id_entry.bind("<Button-1>", self.action_section_id)

        self.lot_weight_label = Label(self.window, text="Lot Weight:", font=('times', label_font_size, 'bold'), bg="#f7f0f5")
        self.lot_weight_entry = Entry(self.window, textvariable=self.lot_weight_verify)
        self.lot_weight_entry.configure(font=font.Font(family='Helvetica', size=entry_font_size), state="disabled")
        self.lot_weight_entry.bind("<Button-1>", self.action_lot_weight)

        self.vehicle_no_label = Label(self.window, text="Vehicle No.:", font=('times', label_font_size, 'bold'), bg="#f7f0f5")
        self.vehicle_no_entry = Entry(self.window, textvariable=self.vehicle_no_verify)
        self.vehicle_no_entry.configure(font=font.Font(family='Helvetica', size=entry_font_size), state="disabled")
        self.vehicle_no_entry.bind("<Button-1>", self.action_vehicle_no)

        self.nextBtn = tk.Button(self.window, text="Next", command=self.main_screen, fg="white", bg="#F37C62", width=12,height=2, font=('times', 16, 'bold'))
        
        # Weight Integration labels
        self.initial_weight = 0
        self.final_weight = 0
        self.mlc_value = 0

        self.wait_till_mlc = tk.IntVar()
        
        self.measure_weight = tk.Button(self.window, text="Measure Initial Weight", command=self.get_initial_weight, fg="white", bg="#539051", font=('times', 16, 'bold'))
        self.measure_final_weight = tk.Button(self.window, text="Measure Final Weight", command=lambda:[self.get_final_weight(), self.wait_till_mlc.set(1)], fg="white", bg="#539051", font=('times', 16, 'bold'))

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
            self.measure_weight.place_forget()
            self.endRecord.place_forget()
            self.entered.place_forget()
            self.msg_sent.place_forget()
        except Exception as e:
            logger.exception(str('Exception occured in "details_entered_success" function\nError message:' + str(e)))
    
    def display_all_options(self):
        try:
            if self.options_displayed == True:
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
            self.moisture_loss_count()
            self.show_results_on_display()
            self.endRecord.place(x=int(configparser.get('gui-config', 'endrecord_btn_x')), y=int(configparser.get('gui-config', 'endrecord_btn_y')))
        except Exception as e:
            print(e)
            self.endRecord.place_forget()
            logger.exception(str('Exception occured in "start_testing" function\nError message:' + str(e)))

    def end_video(self):
        try:
            print("END RECORD")
            self.by_count_text.place_forget()
            self._flc_btn.place_forget()
            self._coarse_btn.place_forget()
            self.leaf_type_label.place_forget()
            self.dynamic_label.place_forget()
            self._initial_weight_label.place_forget()
            self._final_weight_label.place_forget()
            self._lot_weight_label.place_forget()
            self.mlc_label.place_forget()
            self.mlc_formula_label.place_forget()
            self.formula.place_forget()
            self.warning_sign.place(x=10, y=390)
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
    
    def show_options(self, *args):
        leaf_type = self.leaf_verify.get()
        if leaf_type == "Own":
            self.vehicle_no_entry.configure(state="disabled")
            self.section_id_entry.configure(state="normal")
            self.lot_weight_entry.configure(state="normal")
        elif leaf_type == "Bought":
            self.section_id_entry.configure(state="disabled")
            self.vehicle_no_entry.configure(state="normal")
            self.lot_weight_entry.configure(state="normal")

    def place_inputs(self):
        try:
            self.entered.place(x=540, y=305)
            self.measure_weight.place(x=500, y=110, height=30, width=230)
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

    def action_section_id(self, event):
        if self.section_id_verify.get() == 0:
            self.section_id_entry.delete(0, tk.END)
        self.popup_keyboard(event)

    def action_lot_weight(self, event):
        if self.lot_weight_verify.get() == 0:
            self.lot_weight_entry.delete(0, tk.END)
        self.popup_keyboard(event)
    
    def action_vehicle_no(self, event):
        if self.vehicle_no_verify.get() == 0:
            self.vehicle_no_entry.delete(0, tk.END)
        self.popup_keyboard(event)


    def send_data_api(self):
        try:
            if USE_INTERNET == "TRUE":
                qualix_status = 0
                if helper.is_internet_available():
                    lt = self.leaf_verify.get()
                    qualix_status = helper.qualix_api(self.token, self.analysis_params, self.new_fields, lt)
                    if qualix_status != 200:
                        logger.exception(f"payload {self.results}, data {self.new_fields}")
                else:
                    logger.exception(str("Internet unavailable. Data won't get saved."))
                if qualix_status == 200:
                    self.msg_sent.configure(text="Data saved", fg="green")
                    if helper.is_internet_available():
                        t = threading.Thread(target=helper.update_spreadsheet, 
                            args=(self.results["one_leaf_bud"], self.results["two_leaf_bud"], 
                                self.results["three_leaf_bud"], self.results["one_leaf_banjhi"], 
                                self.results["two_leaf_banjhi"], 100 - self.results["quality_score"], self.results["total_count"], self.results["quality_score"],))
                        t.start()
                else:
                    self.msg_sent.configure(text="Couldn't save to servers", fg="red")

            helper.free_space()
            self.by_count_text.place_forget()
            self._flc_btn.place_forget()
            self._coarse_btn.place_forget()
            #self._flc_btn_by_weight.place_forget()
            #self._coarse_btn_by_weight.place_forget()
            self.by_count_text.place_forget()
            self.mlc_label.place_forget()
            self.final_weight_label.place_forget()
            self.mlc_formula_label.place_forget()
            self.initial_weight_label.place_forget()
            helper.update_graph()
        except Exception as e:
            logger.exception(str('Exception occured in "send_data_api" function\nError message:' + str(e)))


    def do_nothing(self):
        pass


    def show_results_on_display(self):
        try:
           # self.measure_final_weight.place_forget()          
            self.forget_graph()
            _1lb, _2lb, _3lb, _1bj, _2bj, _coarse, totalCount, _perc = helper.get_class_count()
            leaf = self.leaf_verify.get()
            
            if totalCount != 0:
                if leaf == "Own":
                    _1lb_perc = round(_1lb*100/totalCount, 2) - 5
                    _2lb_perc = round(_2lb*100/totalCount, 2) + 2
                    _3lb_perc = round(_3lb*100/totalCount, 2)
                    _1bj_perc = round(_1bj*100/totalCount, 2) - 12
                    _2bj_perc = round(_2bj*100/totalCount, 2)
                    totalCount = int(totalCount * 0.80)
                elif leaf == "Bought":
                    _1lb_perc = round(_1lb*100/totalCount, 2) - 8
                    _2lb_perc = round(_2lb*100/totalCount, 2) - 5
                    _3lb_perc = round(_3lb*100/totalCount, 2) - 4
                    _1bj_perc = round(_1bj*100/totalCount, 2) - 13
                    _2bj_perc = round(_2bj*100/totalCount, 2)
                    totalCount = int(totalCount * 0.80)

                _1lb_perc = 0 if _1lb_perc < 0 else _1lb_perc
                _2lb_perc = 0 if _2lb_perc < 0 else _2lb_perc
                _3lb_perc = 0 if _3lb_perc < 0 else _3lb_perc
                _1bj_perc = 0 if _1bj_perc < 0 else _1bj_perc
                _2bj_perc = 0 if _2bj_perc < 0 else _2bj_perc
                _flc_perc = _1lb_perc + _2lb_perc + _1bj_perc + (0.67 * _3lb_perc)
                _flc_perc = 100 if _flc_perc > 100 else _flc_perc
                _flc_perc_by_weight = 24.53 + (0.45 * _flc_perc)
                _flc_perc_by_weight = 100 if _flc_perc_by_weight > 100 else _flc_perc_by_weight
                _coarse_perc = 100 - _flc_perc
                _coarse_perc_by_weight = 100 - _flc_perc_by_weight
            else:
                _1lb_perc = 0.0
                _2lb_perc = 0.0
                _3lb_perc = 0.0
                _1bj_perc = 0.0
                _2bj_perc = 0.0
                _coarse_perc = 0.0
                _flc_perc = 0.0
                _coarse_perc_by_weight = 0.0
                _flc_perc_by_weight = 0.0
            
            _mlc_val_csv = self.mlc_value
            _ini_wt_csv = self.initial_weight
            _fin_wt_csv = self.final_weight

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
            f.write(f"{dt_},{flc_},{coarse_},{_1lbp},{_2lbp},{_3lbp},{_1bjp},{_2bjp},{total_},{leaf},{_flc_perc_by_weight},{_coarse_perc_by_weight},{_mlc_val_csv},{_ini_wt_csv},{_fin_wt_csv}\n")
            f.close()
            
            r = open('/home/agnext/Desktop/results.csv','a')
            r.write(f"{dt_},{flc_},{coarse_},{leaf},{_flc_perc_by_weight},{_coarse_perc_by_weight},{_mlc_val_csv},{_ini_wt_csv},{_fin_wt_csv}\n")
            r.close()

            self.results['one_leaf_bud'] = int(np.ceil(_1lb_perc * totalCount/100))
            self.results['two_leaf_bud'] = int(np.ceil(_2lb_perc * totalCount/100))
            self.results['three_leaf_bud'] = int(np.ceil(_3lb_perc * totalCount/100))
            self.results['one_leaf_banjhi'] = int(np.ceil(_1bj_perc * totalCount/100))
            self.results['two_leaf_banjhi'] = int(np.ceil(_2bj_perc * totalCount/100))
            self.results['one_bud_count'] = 0
            self.results['one_leaf_count'] = 0
            self.results['two_leaf_count'] = 0
            self.results['three_leaf_count'] = 0
            self.results['one_banjhi_count'] = 0
            self.results['total_count'] = totalCount
            self.results['quality_score'] = "{:.2f}".format(_flc_perc)
            self.results['quality_score_by_weight'] = "{:.2f}".format(_flc_perc_by_weight)
            
            
            if _ini_wt_csv == 0 or _fin_wt_csv == 0 or _ini_wt_csv < _fin_wt_csv:
                self.results['initial_weight'] = 'n/a'
                self.results['final_weight'] = 'n/a'

            else:
                self.results['initial_weight'] = _ini_wt_csv
                self.results['final_weight'] = _fin_wt_csv

            self.analysis_params['FLC'] = float(_flc_perc)
            self.analysis_params['Coarse'] = float(100 - _flc_perc)
           
            if _ini_wt_csv == 0 or _fin_wt_csv == 0 or _ini_wt_csv < _fin_wt_csv:
                self.analysis_params['InitialWeight'] = 'n/a'
                self.analysis_params['FinalWeight'] = 'n/a'
                self.analysis_params['Moisture'] = 'n/a'
            else:
                self.analysis_params['InitialWeight'] = _ini_wt_csv
                self.analysis_params['FinalWeight'] = _fin_wt_csv
                if self.mlc_value == 0:
                    mlc_perc = 'n/a'
                else:
                    mlc_perc = "{:.2f}".format(self.mlc_value)
                    self.analysis_params['Moisture'] = float(mlc_perc)

            self._flc_btn.configure(text="FLC %      " + str(round(_flc_perc, 2)))
            self._coarse_btn.configure(text="Coarse %      " + str(round(_coarse_perc, 2)))
            
            self._flc_btn.place(x=60,y=180)
            self._coarse_btn.place(x=60,y=230)
            self.by_count_text.place(x=100,y=130)

            self.warning_sign.place_forget()
            self.formula.place(x=60,y=500)
            gc.collect()
        except Exception as e:
            logger.exception(str('Exception occured in "show_results_on_display" function\nError message:' + str(e)))
      
        leaf_type = self.leaf_verify.get()
        
        self.leaf_type_label = tk.Button(self.window, text="Leaf Type: "+ leaf_type, command=self.do_nothing, fg="white", bg="#12B653", width=int(configparser.get('gui-config', 'result_btn_width')),height=int(configparser.get('gui-config', 'result_btn_height')), font=('times', 14, 'bold'))
        
        if leaf_type == "Own":
            self.dynamic_label = tk.Button(self.window, text="Section ID: "+ self.section_id_verify.get(), command=self.do_nothing, fg="white", bg="#12B653", width=int(configparser.get('gui-config', 'result_btn_width')),height=int(configparser.get('gui-config', 'result_btn_height')), font=('times', 14, 'bold'))
        elif leaf_type == "Bought":
            self.dynamic_label = tk.Button(self.window, text="Vehicle No: "+ self.vehicle_no_verify.get(), command=self.do_nothing, fg="white", bg="#12B653", width=int(configparser.get('gui-config', 'result_btn_width')),height=int(configparser.get('gui-config', 'result_btn_height')), font=('times', 14, 'bold'))

        self.mlc_label = tk.Button(self.window, text="MLC %  " + '{:.2f}'.format(self.mlc_value), command=self.do_nothing, fg="white", bg="#12B653", width=int(configparser.get('gui-config', 'result_btn_width')),height=int(configparser.get('gui-config', 'result_btn_height')), font=('times', 14, 'bold'))

        self._initial_weight_label = tk.Button(self.window, text="Initial Weight (Kg):" + '{:.2f}'.format(self.initial_weight), command=self.do_nothing, fg="white", bg="#12B653", width=int(configparser.get('gui-config', 'result_btn_width')),height=int(configparser.get('gui-config', 'result_btn_height')), font=('times', 14, 'bold'))
        
        self._final_weight_label = tk.Button(self.window, text="Final Weight (Kg):" + '{:.2f}'.format(self.final_weight), command=self.do_nothing, fg="white", bg="#12B653", width=int(configparser.get('gui-config', 'result_btn_width')),height=int(configparser.get('gui-config', 'result_btn_height')), font=('times', 14, 'bold'))
        
        self._lot_weight_label = tk.Button(self.window, text="Lot Weight (Kg): " + self.lot_weight_verify.get(), command=self.do_nothing, fg="white", bg="#12B653", width=int(configparser.get('gui-config', 'result_btn_width')),height=int(configparser.get('gui-config', 'result_btn_height')), font=('times', 14, 'bold'))

        self.mlc_formula_label = tk.Label(self.window, text="M.L. = ((Ini Weight - Fin Weight)/Ini Weight)*100", font=('times', 10), bg="#f7f0f5")
        
        self.mlc_label.place(x=280, y=180)
        self._initial_weight_label.place(x=280, y=230)
        self._final_weight_label.place(x=280, y=280)
        self.leaf_type_label.place(x=510, y=180)
        self.dynamic_label.place(x=510, y=230)
        self._lot_weight_label.place(x=510, y=280)
        self.mlc_formula_label.pack()
        self.mlc_formula_label.place(x=900, y=600) 
     
    def login_verify(self):
        try:
            username = self.username_verify.get()
            password = self.password_verify.get()
            if USE_INTERNET == "TRUE":
                if helper.is_internet_available():
                    success, self.token, self.customer_id, name = helper.login_api_qualix(username, password)
                    if success:
                        registered, valid, days = 1 , 1, 230#helper.check_expiry(self.token)
                        if registered:
                            if valid:
                                if 0 < days < 3:
                                    self.warning_sign.configure(text=f"License - {days} days left", fg="red")
                                    self.warning_sign.place(x=1, y=520)
                                else:
                                    self.warning_sign.configure(text=f"License - {days} days left", fg="green")
                                    self.warning_sign.place(x=1, y=520)
                                self.login_success()
                              
                                self.welcome_text.configure(text="Welcome, " + name.title())
                            else:
                                self.show_error_msg("License expired.")
                        else:
                            self.show_error_msg("Device not registered.")
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
            lot_weight = self.lot_weight_verify.get()  
            section_id = self.section_id_verify.get()
            vehicle_no = self.vehicle_no_verify.get()
            print("DEBUG: WT-> ", lot_weight)
            if (lot_weight != '') or \
                (section_id != '') or \
                (vehicle_no != ''):    
                self.details_entered_success()
                self.start_testing(cmd)
            else:
                self.show_error_msg("Please fill all details.")
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

            self.leaf_entry.configure(width=15, state="active")
            menu = self.nametowidget(self.leaf_entry.menuname)
            menu.config(font=font.Font(family='Helvetica', size=16))

            self.place_inputs()
            self.display_all_options()

            self.poweroff.place(x=960, y=80)
        except Exception as e:
            logger.exception(str('Exception occured in "enter_details" function\nError message:' + str(e)))

    def second_screen_place(self):
        try:
            #self.leaf_entry.place_forget()
            #self.by_count_text.place_forget()
            #self._flc_btn.place_forget()
            #self._coarse_btn.place_forget()
            #self.leaf_type_label.place_forget()
            #self.dynamic_label.place_forget()
            #self._initial_weight_label.place_forget()
            #self._final_weight_label.place_forget()
            #self._lot_weight_label.place_forget()
            #self.mlc_label.place_forget()
            #self.mlc_formula_label.place_forget()
            #self.formula.place_forget()
            #self.vehicle_no_label.place_forget()
            #self.vehicle_no_entry.place_forget()
            #self.lot_weight_entry.place_forget()
            #self.lot_weight_label.place_forget()
            #self.section_id_label.place_forget()
            #self.section_id_entry.place_forget()
            #self._total_btn.place_forget()
            #self.measure_final_weight.place_forget()
            self.forget_graph()
            self.details_entered_success()
            try:
                subprocess.Popen("exec " + "killall onboard", stdout= subprocess.PIPE, shell=True)
            except:
                pass
            self.welcome_text.place(x=int(configparser.get('gui-config', 'welcome_text_x')), y=int(configparser.get('gui-config', 'welcome_text_y')))

            x_col1, x_col2, x_col3, x_col4 = 70, 300, 520, 650
            y_row1, y_row2, y_row3, y_row4 = 150, 210, 290, 330

            self.leaf_entry.place(x=x_col1-10, y=y_row1-10)
            menu = self.nametowidget(self.leaf_entry.menuname)
            menu.config(font=font.Font(family='Helvetica', size=16))

            self.section_id_label.place(x=x_col2, y=y_row1-22)
            self.section_id_entry.place(x=x_col2, y=y_row1)
            self.section_id_entry.delete(0, tk.END)
            section_id = self.new_fields['section_id'] if 'section_id' in self.new_fields else "Enter Section ID"
            self.section_id_entry.insert(1, section_id)

            self.lot_weight_label.place(x=x_col3, y=y_row1-22)
            self.lot_weight_entry.place(x=x_col3, y=y_row1)
            self.lot_weight_entry.delete(0, tk.END)
            lot_weight = self.new_fields['lot_weight'] if 'lot_weight' in self.new_fields else "Enter Lot Weight"
            self.lot_weight_entry.insert(1, lot_weight)

            self.vehicle_no_label.place(x=x_col2, y=y_row1+40)
            self.vehicle_no_entry.place(x=x_col2, y=y_row1+62)
            self.vehicle_no_entry.delete(0, tk.END)
            vehicle_no = self.new_fields['vehicle_no'] if 'vehicle_no' in self.new_fields else "Enter Vehicle No"
            self.vehicle_no_entry.insert(1, vehicle_no)

            self.nextBtn.place(x=350,y=330)  
            self.poweroff.place(x=960, y=80)  
        except Exception as e:
            logger.exception(str('Exception occured in "second_screen_place" function\nError message:' + str(e)))    

    def second_screen_forget(self):
        try:
            self.leaf_entry.place_forget()
            self.vehicle_no_label.place_forget()
            self.vehicle_no_entry.place_forget()
            self.lot_weight_entry.place_forget()
            self.lot_weight_label.place_forget()
            self.section_id_label.place_forget()
            self.section_id_entry.place_forget()
            self.nextBtn.place_forget()
        except Exception as e:
            logger.exception(str('Exception occured in "second_screen_forget" function\nError message:' + str(e))) 

    def main_screen(self):
        try:
            leaf_type =  self.leaf_verify.get()
            if leaf_type == "Own":
                self.new_fields['lot_weight'] = str(self.lot_weight_verify.get()) if self.lot_weight_verify.get() != "Enter Lot Weight" else '0'
                self.new_fields['section_id'] = str(self.section_id_verify.get()) if self.section_id_verify.get() != "Enter Section ID" else '0'
                if (len(self.section_id_entry.get()) == 0) or \
                    (len(self.lot_weight_entry.get()) == 0):
                    self.show_error_msg("Please fill all details.")
                else:
                    self.second_screen_forget()
                    self.enter_details()      
                    self.start_jetson_fan()
                    
            elif leaf_type == "Bought":
                self.new_fields['lot_weight'] = str(self.lot_weight_verify.get()) if self.lot_weight_verify.get() != "Enter Lot Weight" else '0'
                self.new_fields['supplier_veh_no'] = str(self.vehicle_no_verify.get()) if self.vehicle_no_verify.get() != "Enter Vehicle No." else '0'
                
                if (len(self.lot_weight_entry.get()) == 0) or \
                    (len(self.vehicle_no_entry.get()) == 0):
                    self.show_error_msg("Please fill all details.")
                else:
                    self.second_screen_forget()
                    self.enter_details()      
                    self.start_jetson_fan()
            else:
                self.show_error_msg("Please select leaf type")
        except Exception as e:
            logger.exception(str('Exception occured in "main_screen" function\nError message:' + str(e)))  

    def login_success(self):
        try:
            self.username_login_entry.place_forget()
            self.password_login_entry.place_forget()
            self.signin.place_forget()
            self.panel_bg.place_forget()
            self.second_screen_place()
            #th = threading.Thread(target=helper.send_email)
            #th.start() 
        except Exception as e:
            logger.exception(str('Exception occured in "login_success" function\nError message:' + str(e)))
    def get_weight_from_scale(self, timeoutVar_seconds):
        buffer = ""
        port = serial.Serial("/dev/ttyUSB0", baudrate=9600)
        weight_list = []
        # Get values for 30 x 0.2 = 6 seconds
        try:
            timeout = timeoutVar_seconds * 5
            max_data = 0
            while timeout:
                ser_bytes = str(port.readline(7))
                decoded_bytes = float(ser_bytes[3:8])
                final = decoded_bytes / 1000
                if final > max_data:
                    max_data = final
                timeout = timeout - 1
                time.sleep(.01)
            print("HEHE"+str(max_data))
            messagebox.showinfo("Weight:", max_data)
            return max_data
        except:
            self.show_error_msg("Connect Weighing Scale")
            print("Weighing scale Serial ERROR")

    # Initial Weight wrapepr
    def get_initial_weight(self):
        self.initial_weight = self.get_weight_from_scale(5)

    # Final Weight wrapper
    def get_final_weight(self):
        self.final_weight = self.get_weight_from_scale(5)

    # Moisture Loss Formula
    def moisture_loss_count(self):
        self.measure_final_weight.place(x=500, y=110, height=30, width=230)
        self.measure_final_weight.wait_variable(self.wait_till_mlc)
        if self.initial_weight is not 0 and self.final_weight is not 0 and self.final_weight < self.initial_weight:
            self.mlc_value = ((self.initial_weight - self.final_weight)/self.initial_weight)*100
        else:
            # TODO: POP-UP ERROR FOR RE-MEASURING
            print("Measured Initial weight cannot be Zero or greater than the final weight measured")
        self.measure_final_weight.place_forget()

def launchApp():
    window = tk.Tk()
    #window.attributes('-fullscreen',True)
    MyTkApp(window)
    tk.mainloop()

if __name__=='__main__':
    launchApp()
