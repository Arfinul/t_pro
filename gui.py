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

is_login = False
userName = ""
cmd = 'time ./uselib cfg/1_black_conveyor.names cfg/5_yolov3_optimised.cfg 5_yolov3_optimised.weights web_camera'

def vp_start_gui():
    #####Window is our Main frame of system
    global window
    window = tk.Tk()
    # window.attributes("-fullscreen", True)
    window.title("Fine Leaf Count")

    window.geometry('1920x1080')
    window.configure(background='snow')

    # # Create a label in the frame
    # lmain = Label(window)
    # lmain.place(x=400, y=160)

    # cap = cv2.VideoCapture(0)

    # function for video streaming
    def video_stream():
        try:
            global p
            p = subprocess.Popen("exec " + cmd, stdout= subprocess.PIPE, shell=True)
            # _, frame = cap.read()
            # frame = cv2.resize(frame, (800,500))
            # cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            # img = Image.fromarray(cv2image)
            # imgtk = ImageTk.PhotoImage(image=img)
            # lmain.imgtk = imgtk
            # lmain.configure(image=imgtk)
            # lmain.after(1, video_stream)
            endRecord.configure(state="active")
            startRecord.configure(state="disabled")
        except:
            p.kill()
            # cap.release()
            # cv2.destroyAllWindows()
            endRecord.configure(state="disabled")
            startRecord.configure(state="active")
            refresh()

    def end_video():
        p.kill()
        # cap.release()
        # cv2.destroyAllWindows()
        endRecord.configure(state="disabled")
        startRecord.configure(state="active")
        refresh()

    def on_closing():
        from tkinter import messagebox
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            window.destroy()

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
        global login_screen
        login_screen = Toplevel(window)
        login_screen.title("Login")
        login_screen.geometry("300x250")
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
     
        Label(register_screen, text="Registration Success", fg="green", font=("calibri", 11)).pack()
     
    # Implementing event on login button 
     
    def login_verify():
        username1 = username_verify.get()
        password1 = password_verify.get()
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
        # global login_success_screen
        # login_success_screen = Toplevel(login_screen)
        # login_success_screen.title("Success")
        # login_success_screen.geometry("150x100")
        # Label(login_success_screen, text="Login Success").pack()
        # Button(login_success_screen, text="OK", command=delete_login_success).pack()
        global is_login
        is_login = True
        login_screen.destroy()
        startRecord.place(x=90, y=450)
        endRecord.place(x=90, y=550)
        register.place_forget()
        signin.place_forget()
        section.place(x=90, y=150)
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
        global section_screen
        section_screen = Toplevel(window)
        section_screen.title("Register")
        section_screen.geometry("400x300")
     
        global section_name
        global section_entry
        section_name = StringVar()
        Label(section_screen, text="").pack()
        Label(section_screen, text="Please enter section name", font=("times", 14, 'bold'), width=30).pack()
        Label(section_screen, text="").pack()
        section_lable = Label(section_screen, text="Section name * ", font=("times", 13))
        section_lable.pack()
        username_entry = Entry(section_screen, textvariable=section_name)
        username_entry.pack()
        Label(section_screen, text="").pack()
        Button(section_screen, text="Add Section", width=10, height=1, bg="salmon", command = add_section, font=("times", 13, 'bold')).pack()

    def add_section():
        section_info = section_name.get()
     
        file = open(userName, "a")
        file.write(str(datetime.datetime.now()) + ", ")
        file.write(section_info + "\n")
        file.close()
     
        Label(section_screen, text="Section added!", fg="green", font=("calibri", 11)).pack()

    window.protocol("WM_DELETE_WINDOW", on_closing)

    message = tk.Label(window, text="Fine Leaf Count System", fg="black", width=85  ,
                       height=2, font=('times', 30))
    message.place(x=80, y=20)

    if is_login == True:

        section = tk.Button(window, text="Add Section", command=section_gui, fg="black", bg="deep sky blue", width=20,height=2, activebackground = "Grey" , font=('times', 15, 'bold'))
        section.place(x=90, y=150) 

        register = tk.Button(window, text="Register", command=register, fg="black", bg="salmon", width=20,height=2, activebackground = "Grey" , font=('times', 15, 'bold'))
        register.place_forget()

        signin = tk.Button(window, text="Login", command=login, fg="black", bg="deep sky blue", width=20,height=2, activebackground = "Grey" , font=('times', 15, 'bold'))
        signin.place_forget()

        txt = "Welcome, " + userName.title()
        Label(window, text=txt, font=('times', 15, 'bold'), bg='white').place(x=1550, y=130)

        startRecord = tk.Button(window, text="Start", command=video_stream, fg="black", bg="Silver", width=20,height=3, activebackground = "Grey" , font=('times', 15, 'bold'))
        startRecord.place(x=90, y=450)

        endRecord = tk.Button(window, text="Finished", command=end_video, fg="black", bg="Silver", width=20,height=3, activebackground = "Grey" , font=('times', 15, 'bold'))
        endRecord.place(x=90, y=550)
        endRecord.configure(state="disabled")

    else:

        section = tk.Button(window, text="Add Section", command=section_gui, fg="black", bg="deep sky blue", width=20,height=2, activebackground = "Grey" , font=('times', 15, 'bold'))
        section.place_forget()

        register = tk.Button(window, text="Register", command=register, fg="black", bg="salmon", width=20,height=2, activebackground = "Grey" , font=('times', 15, 'bold'))
        register.place(x=700, y=300)

        signin = tk.Button(window, text="Login", command=login, fg="black", bg="deep sky blue", width=20,height=2, activebackground = "Grey" , font=('times', 15, 'bold'))
        signin.place(x=1000, y=300)

        startRecord = tk.Button(window, text="Start", command=video_stream, fg="black", bg="Silver", width=20,height=3, activebackground = "Grey" , font=('times', 15, 'bold'))
        startRecord.place_forget()

        endRecord = tk.Button(window, text="Finished", command=end_video, fg="black", bg="Silver", width=20,height=3, activebackground = "Grey" , font=('times', 15, 'bold'))
        endRecord.place_forget()
        endRecord.configure(state="disabled")

    window.mainloop()

if __name__ == '__main__':
    def refresh():
        window.destroy()
        vp_start_gui()

    vp_start_gui()


# datetime, username, userID, sectionID, FLC %age