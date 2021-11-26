'''
Created on Oct 04, 2021
@author: Young Min Kim
revision on Nov 17, 2021
'''
#======================
# imports
#======================
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import Menu
from tkinter import messagebox as msg
from ToolTip import ToolTip

import resources

import pandas as pd

import datetime
import os

from queue import Queue

from tkinter import filedialog as fd
from os import path

from data_analysis import plot_Timeseries, plot_Unit

# Module level GLOBALS
GLOBAL_CONST = 42
fDir   = path.dirname(__file__)
netDir = fDir


#=====================================================
class OOP():
    def __init__(self):         # Initializer method
        if int(datetime.datetime.now().year) <= 2021:

            # Create instance
            self.win = tk.Tk()   
            
            # Add a title       
            self.win.title(" Graph Viewer for Mass log")  
            
            # Create a Queue
            self.gui_queue = Queue() 
                
            self.create_widgets()

        else:
            os._exit()

        # # Create instance
        # self.win = tk.Tk()   
        
        # # Add a title       
        # self.win.title(" Graph Viewer for Mass log")  
        
        # # Create a Queue
        # self.gui_queue = Queue() 
            
        # self.create_widgets()

    # update progressbar in callback loop
    def run_progressbar_0(self):

        self.Timeseries_scrol.insert(tk.INSERT, "Please wait to process... Human !!" + '\n')
        self.Timeseries_scrol.see("end")  

        try:
        # plot_Timeseries(main_list, sub_list, main_file, sub_file, Y1_Axis, Y2_Axis, Y1_log_OX, Y2_log_OX, main_path, sub_path, progress)
            plot_Timeseries(self.a, 
            self.Timeseries_main_fileEntry.get(), self.Timeseries_sub_fileEntry.get(), 
            self.number_1_chosen.get(), self.number_2_chosen.get(), 
            self.chVar_0.get(), self.chVar_1.get(), 
            self.progress_bar_0)

            self.progress_bar_0["value"] = 0       # reset/clear progressbar  

            self.Timeseries_scrol.insert(tk.INSERT, "Process is END. Human !!" + '\n')
            self.Timeseries_scrol.see("end")

        except:
            self.Timeseries_scrol.insert(tk.INSERT, "Setting miss, Retry Human !!" + '\n')
            self.Timeseries_scrol.see("end")  



    def run_progressbar_1(self):

        self.Unit_scrol.insert(tk.INSERT, "Please wait to process... Human !!" + '\n')
        self.Unit_scrol.see("end")  
        
        try:
            # plot_Unit(main_list, op_file, main_file, step_start, step_end, X_Axis, Y1_Axis, Y2_Axis, Y1_log_OX, Y2_log_OX, sum_CSV, save_path, progress)
            plot_Unit(self.a,
            self.Unit_op_fileEntry.get(), self.Unit_main_fileEntry.get(), self.Unit_sub_fileEntry.get(), 
            self.step_start_chosen.get(), self.step_end_chosen.get(),
            self.number_3_chosen.get(), self.number_4_chosen.get(), self.number_5_chosen.get(), 
            self.chVar_3.get(), self.chVar_4.get(), self.chVar_5.get(), 
            self.Unit_save_file.get(), self.progress_bar_1)

            self.progress_bar_1["value"] = 0       # reset/clear progressbar  

            self.Unit_scrol.insert(tk.INSERT, "Process is END. Human !!" + '\n')
            self.Unit_scrol.see("end")  

        except:
            self.Unit_scrol.insert(tk.INSERT, "Setting miss, Retry Human !!" + '\n')
            self.Unit_scrol.see("end")  


    def usingGlobal(self):
        global GLOBAL_CONST
        GLOBAL_CONST = 777
        
                            
    # Exit GUI cleanly
    def _quit(self):
        self.win.quit()
        self.win.destroy()
        exit() 
                  
    #####################################################################################       
    def create_widgets(self):    
        tabControl = ttk.Notebook(self.win)     # Create Tab Control
        
        tab1 = ttk.Frame(tabControl)            # Create a tab 
        tabControl.add(tab1, text=' Time series graph ')      # Add the tab

        tab2 = ttk.Frame(tabControl)            # Add a second tab
        tabControl.add(tab2, text=' Unit step graph ')      # Make second tab visible
        
        tabControl.pack(expand=1, fill="both")  # Pack to make visible
        
        
        #=====================================================================================
        # Create Manage Files Frame ------------------------------------------------
        mngFilesFrame = ttk.LabelFrame(tab1, text=' Manage Files ')
        mngFilesFrame.grid(column=0, row=0, sticky='WE', padx=10, pady=5)

        # Button Callback
        def Timeseries_main_getFileName():
            fDir  = path.dirname(__file__)
            fName = fd.askopenfilename(parent=self.win, initialdir=fDir)
            # self.Timeseries_main_fileEntry.config(state='enabled')
            self.Timeseries_main_fileEntry.delete(0, tk.END)
            self.Timeseries_main_fileEntry.insert(0, fName)
            # print(self.Timeseries_main_fileEntry.get())
            self.Timeseries_scrol.insert(tk.INSERT, "Main: " + str(fName[int(len(fDir)+1):]) + '\n') 
            self.Timeseries_scrol.see("end")
        
    
        def Timeseries_sub_getFileName():
            fDir  = path.dirname(__file__)
            fName = fd.askopenfilename(parent=self.win, initialdir=fDir)
            # self.Timeseries_sub_fileEntry.config(state='enabled')
            self.Timeseries_sub_fileEntry.delete(0, tk.END)
            self.Timeseries_sub_fileEntry.insert(0, fName)
            # print(self.Timeseries_sub_fileEntry.get())
            self.Timeseries_scrol.insert(tk.INSERT, "Sub : " + str(fName[int(len(fDir)+1):]) + '\n') 
            self.Timeseries_scrol.see("end")

                        
        # Add Widgets to Manage Files Frame
        lb = ttk.Button(mngFilesFrame, text=" Main LOG..", command=Timeseries_main_getFileName)     
        lb.grid(column=0, row=0, sticky='WE') 
        
        #-----------------------------------------------------        
        self.Timeseries_main_file = tk.StringVar()
        self.entryLen = 35
        self.Timeseries_main_fileEntry = tk.Entry(mngFilesFrame, width=self.entryLen, textvariable=self.Timeseries_main_file)
        self.Timeseries_main_fileEntry.grid(column=1, row=0, sticky='WE')
        
        #-----------------------------------------------------
        self.Timeseries_sub_file = tk.StringVar()
        self.Timeseries_sub_fileEntry = tk.Entry(mngFilesFrame, width=self.entryLen, textvariable=self.Timeseries_sub_file)
        self.Timeseries_sub_fileEntry.grid(column=1, row=1, sticky='WE')  
        
        cb = ttk.Button(mngFilesFrame, text=" Sub LOG...", command=Timeseries_sub_getFileName)    
        cb.grid(column=0, row=1, sticky='WE') 
                
        # Add some space around each label
        for child in mngFilesFrame.winfo_children(): 
            child.grid_configure(padx=5, pady=5)


        # We are creating a container frame to hold all other widgets
        selScaleType = ttk.LabelFrame(tab1, text=' Select scale type ')
        selScaleType.grid(column=0, row=1, padx=10, pady=5, sticky='WE')

        def isChecked_0():
            if self.chVar_0.get() == 1:
                self.Timeseries_scrol.insert(tk.INSERT, "Y1 Log scaled" + '\n')
                self.Timeseries_scrol.see("end")
            else:
                self.Timeseries_scrol.insert(tk.INSERT, "Y1 Normal scaled" + '\n')
                self.Timeseries_scrol.see("end")


        def isChecked_1():
            if self.chVar_1.get() == 1:
                self.Timeseries_scrol.insert(tk.INSERT, "Y2 Log scaled" + '\n')
                self.Timeseries_scrol.see("end")
            else:
                self.Timeseries_scrol.insert(tk.INSERT, "Y2 Normal scaled" + '\n')
                self.Timeseries_scrol.see("end")


        # Creating three checkbuttons
        self.chVar_0 = tk.IntVar()
        check0 = tk.Checkbutton(selScaleType, text=" Y1 Log scale ", onvalue=1, offvalue=0, variable=self.chVar_0, command=isChecked_0)
        check0.deselect()
        check0.grid(column=0, row=1, sticky='WE') 


        self.chVar_1 = tk.IntVar()
        check1 = tk.Checkbutton(selScaleType, text=" Y2 Log scale ", onvalue=1, offvalue=0, variable=self.chVar_1, command=isChecked_1)
        check1.deselect()
        check1.grid(column=1, row=1, sticky='WE') 


        # Add some space around each label
        for child in selScaleType.winfo_children(): 
            child.grid_configure(padx=42, pady=5)


        # We are creating a container frame to hold all other widgets
        setAxisData = ttk.LabelFrame(tab1, text=' Select Axis data  ')
        setAxisData.grid(column=0, row=2, padx=10, pady=5, sticky='WE')


        # Combobox callback 
        def comboCallback_0():
            self.a = 0
            self.b = 0
            if int(path.isfile(self.Timeseries_main_file.get())) + int(path.isfile(self.Timeseries_sub_file.get())) == 0:
                self.Timeseries_scrol.insert(tk.INSERT, "Plz select your file." + '\n')
                self.Timeseries_scrol.see("end")
            elif int(path.isfile(self.Timeseries_main_file.get())) + int(path.isfile(self.Timeseries_sub_file.get())) == 2:
                self.a = list(pd.read_csv(self.Timeseries_main_file.get(), header=None, nrows=1).iloc[0][1:])
                self.b = list(pd.read_csv(self.Timeseries_sub_file.get(), header=None, nrows=1).iloc[0][1:])
                if len(self.a) == 0 & len(self.b) == 0:
                    self.Timeseries_scrol.insert(tk.INSERT, "These are wrong file" + '\n')
                    self.Timeseries_scrol.see("end")
                else:
                    [self.number_1_chosen['values'], self.number_2_chosen['values']] = [self.a + self.b, self.a + self.b]
                    self.Timeseries_scrol.insert(tk.INSERT, "You are selected MAIN & SUB" + '\n')
                    self.Timeseries_scrol.see("end")    
            elif int(path.isfile(self.Timeseries_main_file.get())) == 0:
                self.b = list(pd.read_csv(self.Timeseries_sub_file.get(), header=None, nrows=1).iloc[0][1:])
                if len(self.b) == 1:
                    self.Timeseries_scrol.insert(tk.INSERT, "SUB is wrong file" + '\n')
                    self.Timeseries_scrol.see("end")
                else:
                    [self.number_1_chosen['values'], self.number_2_chosen['values']] = [self.b, self.b]
                    self.Timeseries_scrol.insert(tk.INSERT, "You are only selected SUB" + '\n')
                    self.Timeseries_scrol.see("end")
            else:
                self.a = list(pd.read_csv(self.Timeseries_main_file.get(), header=None, nrows=1).iloc[0][1:])
                if len(self.a) == 1:
                    self.Timeseries_scrol.insert(tk.INSERT, "MAIN is wrong file" + '\n')
                    self.Timeseries_scrol.see("end")
                else:
                    [self.number_1_chosen['values'], self.number_2_chosen['values']] = [self.a, self.a]
                    self.Timeseries_scrol.insert(tk.INSERT, "You are only selected MAIN" + '\n')
                    self.Timeseries_scrol.see("end")



        # XY Axis setting
        # def callbackFunc_0(event):
        #     self.scrol.insert(tk.INSERT, ' X Axis is ' + self.number_0_chosen.get() + '\n')

        def callbackFunc_1(event):
            self.Timeseries_scrol.insert(tk.INSERT, 'Y1 Axis is ' + self.number_1_chosen.get() + '\n')
            self.Timeseries_scrol.see("end")

        def callbackFunc_2(event):
            self.Timeseries_scrol.insert(tk.INSERT, 'Y2 Axis is ' + self.number_2_chosen.get() + '\n')
            self.Timeseries_scrol.see("end")


        # ttk.Label(setAxisData, text="  X Axis : ").grid(column=0, row=5, sticky='WE')
        # number_0 = tk.StringVar()
        # number_0_chosen = ttk.Combobox(setAxisData, width=35, textvariable=number_0, state='readonly', postcommand=comboCallback_0)
        # number_0_chosen.grid(column=1, row=5)
        # number_0_chosen.bind("<<ComboboxSelected>>", callbackFunc_0)

        ttk.Label(setAxisData, text=" Y1 Axis : ").grid(column=0, row=6, sticky='WE')
        self.number_1 = tk.StringVar()
        self.number_1_chosen = ttk.Combobox(setAxisData, width=35, textvariable=self.number_1, state='readonly', postcommand=comboCallback_0)
        self.number_1_chosen.grid(column=1, row=6)
        self.number_1_chosen.bind("<<ComboboxSelected>>", callbackFunc_1)

        ttk.Label(setAxisData, text=" Y2 Axis : ").grid(column=0, row=7, sticky='WE')
        self.number_2 = tk.StringVar()
        self.number_2_chosen = ttk.Combobox(setAxisData, width=35, textvariable=self.number_2, state='readonly', postcommand=comboCallback_0)
        self.number_2_chosen.grid(column=1, row=7)
        self.number_2_chosen.bind("<<ComboboxSelected>>", callbackFunc_2)


        # Add some space around each label
        for child in setAxisData.winfo_children(): 
            child.grid_configure(padx=10, pady=5)


        # Add a Progressbar to Tab 1
        Timeseries_progbar = ttk.LabelFrame(tab1, text=' Progress bar ')
        Timeseries_progbar.grid(column=0, row=3, padx=5, pady=5)
        
        # Add Buttons for Progressbar commands
        ttk.Button(Timeseries_progbar, text=" RUN ", command=self.run_progressbar_0).grid(column=0, row=0, sticky='WE')   

        self.progress_bar_0 = ttk.Progressbar(Timeseries_progbar, orient='horizontal', length=290, mode='determinate')
        self.progress_bar_0.grid(column=1, row=0, pady=2, sticky='WE')

        # Add some space around each label
        for child in Timeseries_progbar.winfo_children(): 
            child.grid_configure(padx=5, pady=5)



        # We are creating a container frame to hold all other widgets
        scrolTEXTbox = ttk.LabelFrame(tab1, text=' Message box ')
        scrolTEXTbox.grid(column=0, row=5, padx=10, pady=5, sticky='WE')

        # Using a scrolled Text control    
        scrol_w = 52; scrol_h = 15                 # increase sizes
        self.Timeseries_scrol = scrolledtext.ScrolledText(scrolTEXTbox, width=scrol_w, height=scrol_h, wrap=tk.WORD)
        self.Timeseries_scrol.grid(column=0, row=0, sticky='WE', columnspan=3)  


        for child in scrolTEXTbox.winfo_children():  
            child.grid_configure(padx=5, pady=5) 

        
        # Add a reset
        Reset_bt = ttk.LabelFrame(tab1, text=' Reset setting ')
        Reset_bt.grid(column=0, row=4, padx=10, pady=5, sticky='WE')
        
        def reset_all():
            self.step_start_chosen.set('')
            self.step_end_chosen.set('')
            self.number_3_chosen.set('')
            self.number_4_chosen.set('')
            self.number_5_chosen.set('')
            self.chVar_3.set(0)
            self.chVar_4.set(0)
            self.chVar_5.set(0)
            self.Unit_save_file.set('')
            self.Unit_main_file.set('')
            self.Unit_op_file.set('')
            self.number_1_chosen.set('')
            self.number_2_chosen.set('')
            self.chVar_0.set(0)
            self.chVar_1.set(0)
            self.Timeseries_main_file.set('')
            self.Timeseries_sub_file.set('')

        def reset_axis():
            self.number_3_chosen.set('')
            self.number_4_chosen.set('')
            self.number_5_chosen.set('')
            self.chVar_3.set(0)
            self.chVar_4.set(0)
            self.chVar_5.set(0)
            self.number_1_chosen.set('')
            self.number_2_chosen.set('')
            self.chVar_0.set(0)
            self.chVar_1.set(0)



        # Add Buttons for Progressbar commands
        ttk.Button(Reset_bt, text=" Reset all", command=reset_all).grid(column=0, row=0, sticky='WE')

        ttk.Button(Reset_bt, text=" Reset axis", command=reset_axis).grid(column=1, row=0, sticky='WE')

        # Add some space around each label
        for child in Reset_bt.winfo_children(): 
            child.grid_configure(padx=5, pady=5)



        #=====================================================================================
        # tab2             
        # Create Manage Files Frame ------------------------------------------------
        mngFilesFrame = ttk.LabelFrame(tab2, text=' Manage Files ')
        mngFilesFrame.grid(column=0, row=0, sticky='WE', padx=10, pady=5)

        # Button Callback
        def Unit_op_getFileName():
            fDir  = path.dirname(__file__)
            fName = fd.askopenfilename(parent=self.win, initialdir=fDir)
            # self.Timeseries_main_fileEntry.config(state='enabled')
            self.Unit_op_fileEntry.delete(0, tk.END)
            self.Unit_op_fileEntry.insert(0, fName)
            self.Unit_scrol.insert(tk.INSERT, "Operation: " + str(fName[int(len(fDir)+1):]) + '\n') 
            self.Unit_scrol.see("end")
        
    
        def Unit_main_getFileName():
            fDir  = path.dirname(__file__)
            fName = fd.askopenfilename(parent=self.win, initialdir=fDir)
            # self.Timeseries_sub_fileEntry.config(state='enabled')
            self.Unit_main_fileEntry.delete(0, tk.END)
            self.Unit_main_fileEntry.insert(0, fName)
            self.Unit_scrol.insert(tk.INSERT, "Main : " + str(fName[int(len(fDir)+1):]) + '\n') 
            self.Unit_scrol.see("end")
        
        
        def Unit_sub_getFileName():
            fDir  = path.dirname(__file__)
            fName = fd.askopenfilename(parent=self.win, initialdir=fDir)
            # self.Timeseries_sub_fileEntry.config(state='enabled')
            self.Unit_sub_fileEntry.delete(0, tk.END)
            self.Unit_sub_fileEntry.insert(0, fName)
            self.Unit_scrol.insert(tk.INSERT, "Sub : " + str(fName[int(len(fDir)+1):]) + '\n') 
            self.Unit_scrol.see("end")        


        def getFolderName2():
            fDir2 = fd.askdirectory()
            # self.Unit_save_fileEntry.config(state='enabled')
            self.Unit_save_fileEntry.delete(0, tk.END)
            self.Unit_save_fileEntry.insert(0, fDir2)
            
            if len(fDir2) > self.entryLen:
                self.Unit_save_fileEntry.config(width=len(fDir2) + 3)

            self.Unit_scrol.insert(tk.INSERT, "Save path : " + str(fDir2) + '\n') 
            self.Unit_scrol.see("end")

                        
        # Add Widgets to Manage Files Frame
        lb = ttk.Button(mngFilesFrame, text=" Operarion ", command=Unit_op_getFileName)     
        lb.grid(column=0, row=0, sticky='WE') 
        
        #-----------------------------------------------------        
        self.Unit_op_file = tk.StringVar()
        self.entryLen = 35
        self.Unit_op_fileEntry = tk.Entry(mngFilesFrame, width=self.entryLen, textvariable=self.Unit_op_file)
        self.Unit_op_fileEntry.grid(column=1, row=0, sticky='WE')
        
        #-----------------------------------------------------
        self.Unit_main_file = tk.StringVar()
        self.Unit_main_fileEntry = tk.Entry(mngFilesFrame, width=self.entryLen, textvariable=self.Unit_main_file)
        self.Unit_main_fileEntry.grid(column=1, row=1, sticky='WE')  

        self.Unit_sub_file = tk.StringVar()
        self.Unit_sub_fileEntry = tk.Entry(mngFilesFrame, width=self.entryLen, textvariable=self.Unit_sub_file)
        self.Unit_sub_fileEntry.grid(column=1, row=2, sticky='WE')          
        
        self.Unit_save_file = tk.StringVar()
        self.Unit_save_fileEntry = tk.Entry(mngFilesFrame, width=self.entryLen, textvariable=self.Unit_save_file)
        self.Unit_save_fileEntry.grid(column=1, row=3, sticky='WE')  

        cb = ttk.Button(mngFilesFrame, text=" Main LOG..", command=Unit_main_getFileName)    
        cb.grid(column=0, row=1, sticky='WE')

        db = ttk.Button(mngFilesFrame, text=" Sub LOG..", command=Unit_sub_getFileName)    
        db.grid(column=0, row=2, sticky='WE') 

        sb = ttk.Button(mngFilesFrame, text="Save path..", command=getFolderName2)     
        sb.grid(column=0, row=3, sticky=tk.W) 

        # Add some space around each label
        for child in mngFilesFrame.winfo_children(): 
            child.grid_configure(padx=5, pady=5)



        # We are creating a container frame to hold all other widgets
        selScaleType = ttk.LabelFrame(tab2, text=' Select scale type ')
        selScaleType.grid(column=0, row=1, padx=10, pady=5, sticky='WE')

        def isChecked_3():
            if self.chVar_3.get() == 1:
                self.Unit_scrol.insert(tk.INSERT, "Y1 Log scaled" + '\n')
                self.Unit_scrol.see("end")
            else:
                self.Unit_scrol.insert(tk.INSERT, "Y1 Normal scaled" + '\n')
                self.Unit_scrol.see("end")


        def isChecked_4():
            if self.chVar_4.get() == 1:
                self.Unit_scrol.insert(tk.INSERT, "Y2 Log scaled" + '\n')
                self.Unit_scrol.see("end")
            else:
                self.Unit_scrol.insert(tk.INSERT, "Y2 Normal scaled" + '\n')
                self.Unit_scrol.see("end")


        def isChecked_5():
            if self.chVar_5.get() == 1:
                self.Unit_scrol.insert(tk.INSERT, "Making Summary CSV" + '\n')
                self.Unit_scrol.see("end")
            else:
                self.Unit_scrol.insert(tk.INSERT, "Cancel Summary CSV" + '\n')
                self.Unit_scrol.see("end")

        # Creating three checkbuttons
        self.chVar_3 = tk.IntVar()
        check3 = tk.Checkbutton(selScaleType, text=" Y1 Log scale ", onvalue=1, offvalue=0, variable=self.chVar_3, command=isChecked_3)
        check3.deselect()
        check3.grid(column=0, row=1, sticky='WE') 

        self.chVar_4 = tk.IntVar()
        check4 = tk.Checkbutton(selScaleType, text=" Y2 Log scale ", onvalue=1, offvalue=0, variable=self.chVar_4, command=isChecked_4)
        check4.deselect()
        check4.grid(column=1, row=1, sticky='WE') 

        self.chVar_5 = tk.IntVar()
        check5 = tk.Checkbutton(selScaleType, text=" Summary CVS ", onvalue=1, offvalue=0, variable=self.chVar_5, command=isChecked_5)
        check5.deselect()
        check5.grid(column=2, row=1, sticky='WE') 


        # Add some space around each label
        for child in selScaleType.winfo_children(): 
            child.grid_configure(padx=5, pady=5)


                        
        # We are creating a container frame to hold all other widgets
        selSTEPorder = ttk.LabelFrame(tab2, text=' Step start to end  ')
        selSTEPorder.grid(column=0, row=2, padx=10, pady=5, sticky='WE')

        def callbackFunc_3(event):
            self.Unit_scrol.insert(tk.INSERT, self.step_start_chosen.get() + '\n')
            self.Unit_scrol.see("end")

        def callbackFunc_4(event):
            self.Unit_scrol.insert(tk.INSERT, self.step_end_chosen.get() + '\n')
            self.Unit_scrol.see("end")


        # Changing our Label
        ttk.Label(selSTEPorder, text="  START : ").grid(column=0, row=2, sticky='WE')
        self.step_start = tk.StringVar()
        self.step_start_chosen = ttk.Combobox(selSTEPorder, width=35, textvariable=self.step_start, state='readonly')
        self.step_start_chosen['values'] = ("Auto Step:Step_Face Up_Start", "Auto Step:Step_Dechuck_Start", "Auto Step:Step_PinUP_Start",
        "Auto Step:Step_GL Unload_Start", "Auto Step:Step_GL Load_Start", "Auto Step:Step_Pin Down_Start", "Auto Step:Step_Chuck_Start", 
        "Auto Step:Step_Face Down_Start", "Auto Step:Step_Face Down_End", "Auto Step:Step_Move Align_Start", "Auto Step:Step_Align_Start", 
        "Auto Step:Step_Move Process_Start", "Auto Step:Step_Process_Start", "Auto Step:Step_Move Home_Start", "PreOffSet_X1")
        self.step_start_chosen.grid(column=1, row=2)
        self.step_start_chosen.current(0)
        self.step_start_chosen.bind("<<ComboboxSelected>>", callbackFunc_3)


        ttk.Label(selSTEPorder, text="  END   : ").grid(column=0, row=3, sticky='WE')
        self.step_end = tk.StringVar()
        self.step_end_chosen = ttk.Combobox(selSTEPorder, width=35, textvariable=self.step_end, state='readonly')
        self.step_end_chosen['values'] = ("Auto Step:Step_Face Up_End", "Auto Step:Step_Dechuck_End", "Auto Step:Step_PinUp_End", "Auto Step:Step_GL Unload_End", 
        "Auto Step:Step_GL Load_End", "Auto Step:Step_PinDown_End", "Auto Step:Step_Chuck_End", "Auto Step:Step_Face Down_End", "Auto Step:Step_Move Align_End", 
        "Auto Step:Step_Align_End", "Auto Step:Step_Move Process_End", "Auto Step:Step_Process_End", "Auto Step:Step_Move Home_End", "PreOffSet_Y2")
        self.step_end_chosen.grid(column=1, row=3)
        self.step_end_chosen.current(0)
        self.step_end_chosen.bind("<<ComboboxSelected>>", callbackFunc_4)

        # Add some space around each label
        for child in selSTEPorder.winfo_children(): 
            child.grid_configure(padx=5, pady=5)

 
 
        # We are creating a container frame to hold all other widgets
        setAxisData = ttk.LabelFrame(tab2, text=' Select Axis data  ')
        setAxisData.grid(column=0, row=3, padx=10, pady=5, sticky='WE')


        # Combobox callback 
        # def comboCallback_1():
        #     if int(path.isfile(self.Unit_op_file.get())) + int(path.isfile(self.Unit_main_file.get())) == 0:
        #         self.Unit_scrol.insert(tk.INSERT, "Plz select your file." + '\n')
        #         self.Unit_scrol.see("end")
        #     elif int(path.isfile(self.Unit_op_file.get())) + int(path.isfile(self.Unit_main_file.get())) == 1:
        #         self.Unit_scrol.insert(tk.INSERT, "Plz select MAIN file." + '\n')
        #         self.Unit_scrol.see("end")
        #     else:
        #         self.b = list(pd.read_csv(self.Unit_main_file.get(), header=None, nrows=1).iloc[0][0:])
        #         if len(self.b) == 0:
        #             self.Unit_scrol.insert(tk.INSERT, "These are wrong file" + '\n')
        #             self.Unit_scrol.see("end")
        #         else:
        #             [self.number_3_chosen['values'], self.number_4_chosen['values'], self.number_5_chosen['values']] = [self.b, self.b, self.b]
        #             self.Unit_scrol.insert(tk.INSERT, "You are selected OP & MAIN" + '\n')
        #             self.Unit_scrol.see("end")    


        def comboCallback_1():
            self.a = 0
            self.b = 0
            if int(path.isfile(self.Unit_main_file.get())) + int(path.isfile(self.Unit_sub_file.get())) == 0:
                self.Unit_scrol.insert(tk.INSERT, "Plz select your file." + '\n')
                self.Unit_scrol.see("end")
            elif int(path.isfile(self.Unit_main_file.get())) + int(path.isfile(self.Unit_sub_file.get())) == 2:
                self.a = list(pd.read_csv(self.Unit_main_file.get(), header=None, nrows=1).iloc[0][0:])
                self.b = list(pd.read_csv(self.Unit_sub_file.get(), header=None, nrows=1).iloc[0][1:])
                if len(self.a) == 0 & len(self.b) == 0:
                    self.Unit_scrol.insert(tk.INSERT, "These are wrong file" + '\n')
                    self.Unit_scrol.see("end")
                else:
                    [self.number_3_chosen['values'], self.number_4_chosen['values'], self.number_5_chosen['values']] = [self.a + self.b, self.a + self.b, self.a + self.b]
                    self.Unit_scrol.insert(tk.INSERT, "You are selected MAIN & SUB" + '\n')
                    self.Unit_scrol.see("end")    
            elif int(path.isfile(self.Unit_main_file.get())) == 0:
                self.b = list(pd.read_csv(self.Unit_sub_file.get(), header=None, nrows=1).iloc[0][1:])
                if len(self.b) == 1:
                    self.Unit_scrol.insert(tk.INSERT, "SUB is wrong file" + '\n')
                    self.Unit_scrol.see("end")
                else:
                    [self.number_3_chosen['values'], self.number_4_chosen['values'], self.number_5_chosen['values']] = [self.b, self.b, self.b]
                    self.Unit_scrol.insert(tk.INSERT, "You are only selected SUB" + '\n')
                    self.Unit_scrol.see("end")
            else:
                self.a = list(pd.read_csv(self.Unit_main_file.get(), header=None, nrows=1).iloc[0][0:])
                if len(self.a) == 1:
                    self.Unit_scrol.insert(tk.INSERT, "MAIN is wrong file" + '\n')
                    self.Unit_scrol.see("end")
                else:
                    [self.number_3_chosen['values'], self.number_4_chosen['values'], self.number_5_chosen['values']] = [self.a, self.a, self.a]
                    self.Unit_scrol.insert(tk.INSERT, "You are only selected MAIN" + '\n')
                    self.Unit_scrol.see("end")

        
        # XY Axis setting
        def callbackFunc_5(event):
            self.Unit_scrol.insert(tk.INSERT, ' X Axis is ' + self.number_3_chosen.get() + '\n')
            self.Unit_scrol.see("end")

        def callbackFunc_6(event):
            self.Unit_scrol.insert(tk.INSERT, 'Y1 Axis is ' + self.number_4_chosen.get() + '\n')
            self.Unit_scrol.see("end")
        
        def callbackFunc_7(event):
            self.Unit_scrol.insert(tk.INSERT, 'Y2 Axis is ' + self.number_5_chosen.get() + '\n')
            self.Unit_scrol.see("end")


        ttk.Label(setAxisData, text="  X Axis : ").grid(column=0, row=5, sticky='WE')
        self.number_3 = tk.StringVar()
        self.number_3_chosen = ttk.Combobox(setAxisData, width=35, textvariable=self.number_3, state='readonly', postcommand=comboCallback_1)
        self.number_3_chosen.grid(column=1, row=5)
        self.number_3_chosen.bind("<<ComboboxSelected>>", callbackFunc_5)

        ttk.Label(setAxisData, text=" Y1 Axis : ").grid(column=0, row=6, sticky='WE')
        self.number_4 = tk.StringVar()
        self.number_4_chosen = ttk.Combobox(setAxisData, width=35, textvariable=self.number_4, state='readonly', postcommand=comboCallback_1)
        self.number_4_chosen.grid(column=1, row=6)
        self.number_4_chosen.bind("<<ComboboxSelected>>", callbackFunc_6)

        ttk.Label(setAxisData, text=" Y2 Axis : ").grid(column=0, row=7, sticky='WE')
        self.number_5 = tk.StringVar()
        self.number_5_chosen = ttk.Combobox(setAxisData, width=35, textvariable=self.number_5, state='readonly', postcommand=comboCallback_1)
        self.number_5_chosen.grid(column=1, row=7)
        self.number_5_chosen.bind("<<ComboboxSelected>>", callbackFunc_7)


        # Add some space around each label
        for child in setAxisData.winfo_children(): 
            child.grid_configure(padx=10, pady=5)



        # Add a Progressbar to Tab 2
        Unit_progbar = ttk.LabelFrame(tab2, text=' Progress bar ')
        Unit_progbar.grid(column=0, row=4, padx=5, pady=5)
        
        # Add Buttons for Progressbar commands
        ttk.Button(Unit_progbar, text=" RUN ", command=self.run_progressbar_1).grid(column=0, row=0, sticky='WE')   

        self.progress_bar_1 = ttk.Progressbar(Unit_progbar, orient='horizontal', length=290, mode='determinate')
        self.progress_bar_1.grid(column=1, row=0, pady=2, sticky='WE')


        # Add some space around each label
        for child in Unit_progbar.winfo_children(): 
            child.grid_configure(padx=5, pady=5)



        # We are creating a container frame to hold all other widgets
        scrolTEXTbox = ttk.LabelFrame(tab2, text=' Message box ')
        scrolTEXTbox.grid(column=0, row=5, padx=10, pady=5, sticky='WE')

        # Using a scrolled Text control    
        scrol_w = 52; scrol_h = 5                 # increase sizes
        self.Unit_scrol = scrolledtext.ScrolledText(scrolTEXTbox, width=scrol_w, height=scrol_h, wrap=tk.WORD)
        self.Unit_scrol.grid(column=0, row=0, sticky='WE', columnspan=3)  


        for child in scrolTEXTbox.winfo_children():  
            child.grid_configure(padx=5, pady=5) 




        # Creating a Menu Bar ==========================================================            
        menu_bar = Menu(self.win)
        self.win.config(menu=menu_bar)
        
        # Add menu items
        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Blank")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        # Display a Message Box
        def _msgBox():
            msg.showinfo('GVM Info Box', 'Revision r02 \n\nOptimize Logic and Remove Usless if statement.\n\nCopyright by KIM\n\nLicensed until 2021.\nPast 2021, You should be deleted it.\n\nFor my Galaxy and CG children')  
            
        # Add another Menu to the Menu Bar and an item
        help_menu = Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=_msgBox)   # display messagebox when clicked
        menu_bar.add_cascade(label="Help", menu=help_menu)
        
        # Change the tab1 windows icon
        self.win.iconbitmap(resources.icon)
        
        # call function
        self.usingGlobal()
        
        
        # Add Tooltips -----------------------------------------------------
        # Add a Tooltip to the Spinbox
        ToolTip(self.Timeseries_scrol, 'This is a Message box')
        ToolTip(self.Unit_scrol, 'This is a Message box')

                 
#======================
# Start GUI
#======================
oop = OOP()
oop.win.mainloop()