import tkinter as tk
from tkinter import *
from tkinter import messagebox
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

configparser = configparser.RawConfigParser()   
os.chdir("/home/agnext/Documents/flc")  # Agnext

configparser.read('flc_utils/screens/touchScreen/gui.cfg')
is_admin = False

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


class MyTkApp(tk.Frame):

    def __init__(self, master):  
        tk.Frame.__init__(self, master)   
        self.userID = ""
        self.token = ""
        self.farmer_id = ""
        self.id_name_dict = {}
        self.OPTIONS = ["Select section ID"] 

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

        self.logout_button = tk.Button(self.window, text="Logout", command=self.logout, fg="white", bg="#539051", width=int(configparser.get('gui-config', 'refresh_width')), font=('times', 12, 'bold'))
        
        self.restart_button = tk.Button(self.window, text="Restart", command=self.restart, fg="white", bg="#DC461D", width=7,font=('times', 12, 'bold'))
        self.shutdown_button = tk.Button(self.window, text="ShutDown", command=self.shutdown, fg="white", bg="#DC461D", width=7, font=('times', 12, 'bold'))
        self.startDemo = tk.Button(self.window, text="Demo Sample", command=self.demo_video, fg="black", bg="#FFE77A", font=('times', 15, 'bold'), width=int(configparser.get('gui-config', 'signin_btn_width')),height=int(configparser.get('gui-config', 'signin_btn_height')))
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
     
        self.farmer_verify = StringVar()
        self.section_verify = StringVar()
        self.section_verify.set("Select section ID")
         
        self.farmer_entry = Entry(self.window, textvariable=self.farmer_verify)
        self.sector_entry = OptionMenu(self.window, self.section_verify, *self.OPTIONS)
        self.sector_entry.configure(width=24, state="disabled")

        self.welcome_text = Label(self.window, text="Welcome, ", font=('times', 15, 'bold'), bg='white')
        self.entered = tk.Button(self.window, text="Start FLC", command=self.details_verify, fg="white", bg="#539051", width=int(configparser.get('gui-config', 'signin_btn_width')),height=int(configparser.get('gui-config', 'signin_btn_height')), font=('times', 15, 'bold'))
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

        self.startDemo.place_forget()
        self.endRecord.place_forget()
        if is_admin:
            self.startCamRecord.place_forget()



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
        self.msg_sent.place_forget()
        self.logout_button.place_forget()
        # self.tuneCamera.place_forget()
        if is_admin:
            self.startCamRecord.place_forget() 
        self.restart_button.place_forget()
        self.shutdown_button.place_forget()
        self.remove_numpad()
        self.start_jetson_fan()
    

    def start_testing(self, command):
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


    def video_stream(self):
        self.start_testing(cmd)


    def demo_video(self):
        farmer = self.farmer_verify.get()
        sector = self.section_verify.get()      
        if farmer not in ["", "Enter farmer Code"] and sector not in ["", "Select section ID"]:
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
            print("Thread started.")
            if self.farmer_verify.get() == "Enter farmer Code":
                self.farmer_entry.delete(0, tk.END)
            try:
                self.startDemo.place_forget()  
                self.endRecord.place_forget()
                self.sector_entry.place_forget()
                self.entered.place_forget()
            except:
                pass
            try:
                self._back.place(x=660, y=350)
                self._zero.place(x=605, y=350)
                self._clear.place(x=550, y=350)
                self._one.place(x=660, y=300)
                self._two.place(x=605, y=300)
                self._three.place(x=550, y=300)
                self._four.place(x=660, y=250)
                self._five.place(x=605, y=250)
                self._six.place(x=550, y=250)
                self._seven.place(x=660, y=200)
                self._eight.place(x=605, y=200)
                self._nine.place(x=550, y=200)
            except:
                pass
            print("Thread ended.")
        t = threading.Thread(target=callback)
        t.start()

    def get_sections(self):
        url = configparser.get('gui-config', 'ip') + "/api/sections"
        headers = {
            'Authorization': "Bearer " + self.token
            }
        resp = requests.request("GET", url, headers=headers)
        data = resp.json()['data']
        section_id_list = [i["sectionId"] for i in data]
        section_name_list = [i["name"] for i in data]

        self.id_name_dict = dict(zip(section_name_list, section_id_list))

        self.OPTIONS = ["Select section ID"] + section_name_list
        self.sector_entry = OptionMenu(self.window, self.section_verify, *self.OPTIONS)
        self.sector_entry.configure(width=24, state="active")

    def get_farmer_id(self):
        try:
            farmer_code = self.farmer_verify.get()
            url = configparser.get('gui-config', 'ip') + "/api/users/code/" + farmer_code
            headers = {
                'Authorization': "Bearer " + self.token
                }
            resp = requests.request("GET", url, headers=headers)
            self.farmer_id = resp.json()['data'][0]['id']
            self.get_sections()
            self.hide_numpad()
        except Exception as e:
            print(e)
            self.enter_correct_details()


    def hide_numpad(self):
        gc.collect()
        self.remove_numpad()
        self.startDemo.place(x=540, y=360)
        self.sector_entry.place(x=540, y=185, height=40)
        self.entered.place(x=540, y=280)


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


    def send_data_api(self):
        if configparser.get('gui-config', 'internet') == 'true':
            
            _1lb, _2lb, _3lb, _1bj, _2bj, _coarse, totalCount, _perc = self.get_class_count()

            head = {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + self.token
            }
            load = {
                "userId": int(self.userID),
                "ccId": 1,
                "sectionId": int(self.id_name_dict[self.section_verify.get()]),
                "assistId": int(self.farmer_id),
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

        _1lb, _2lb, _3lb, _1bj, _2bj, _coarse, totalCount, _perc = self.get_class_count()


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
        farmer = self.farmer_verify.get()
        sector = self.section_verify.get()      
        if farmer not in ["", "Enter farmer Code"] and sector not in ["", "Select section ID"]:
            self.details_entered_success()
            self.video_stream()
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

        self.welcome_text.place(x=int(configparser.get('gui-config', 'welcome_text_x')), y=int(configparser.get('gui-config', 'welcome_text_y')))
        
        self.farmer_entry.bind("<Button-1>", self.show_numpad)
        self.farmer_entry.place(x=540,y=140, height=40, width=190)
        self.farmer_entry.delete(0, tk.END)
        self.farmer_entry.insert(1, "Enter farmer Code")

        self.OPTIONS = ["Select section ID"]
        self.sector_entry.place(x=540, y=185, height=40)
        self.sector_entry.configure(width=24, state="disabled")

        self.entered.place(x=540, y=280)
        self.startDemo.place(x=540, y=360)
        self.logout_button.place(x=int(configparser.get('gui-config', 'logout_x')), y=int(configparser.get('gui-config', 'logout_y')))
        self.restart_button.place(x=int(configparser.get('gui-config', 'restart_x')), y=int(configparser.get('gui-config', 'restart_y')))
        self.shutdown_button.place(x=int(configparser.get('gui-config', 'shutdown_x')), y=int(configparser.get('gui-config', 'shutdown_y')))

     
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


