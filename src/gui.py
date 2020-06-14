#! /usr/bin/env python
#  -*- coding: utf-8 -*-
#
# GUI module generated by PAGE version 5.2
#  in conjunction with Tcl version 8.6
#    Apr 28, 2020 06:38:01 PM CEST  platform: Windows NT

import sys
from iota import Iota, Tag, ProposedTransaction, Address, TryteString
from tkinter import messagebox
import json
from tkintertable import TableCanvas, TableModel, Tables
import time
import datetime
import requests
from pandas.tseries.offsets import Hour
from _sqlite3 import Row

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

try:
    import ttk
    py3 = False
except ImportError:
    import tkinter.ttk as ttk
    py3 = True

import gui_support

def vp_start_gui():
    '''Starting point when module is the main routine.'''
    global val, w, root
    root = tk.Tk()
    top = Toplevel1 (root)
    gui_support.init(root, top)
    now = datetime.datetime.now()
    Toplevel1.initialTime = now.strftime("%H:%M:%S")
    
    root.mainloop()

w = None
def create_Toplevel1(rt, *args, **kwargs):
    '''Starting point when module is imported by another module.
       Correct form of call: 'create_Toplevel1(root, *args, **kwargs)' .'''
    global w, w_win, root
    #rt = root
    root = rt
    w = tk.Toplevel (root)
    top = Toplevel1 (w)
    gui_support.init(w, top, *args, **kwargs)
    return (w, top)

def destroy_Toplevel1():
    global w
    w.destroy()
    w = None

class Toplevel1:
    
    #Ab hier fängt die eigentliche GUI Logik an!
    
    nodeURL = 'https://wasp.servebeer.com:14267'#'https://nodes.thetangle.org:443'
    targetAddress =''
    fleetAddress =''
    entered = False
    enteredEnemy = False
    targetRow = ''
    targetCol = ''
    shipCount = 5
    initialTime =''
    incomingTime = []
    session = 1
    hitResponse = ''
    hitRow = ''
    hitCol = ''

    #Enter und Exit checken, ob die Maus im Enemy Fleet Frame ist. Ansonsten wird auch der Mouseclick im OurFleet Frame übernommen.
    
    def timer(self):
        now = datetime.datetime.now()
        dt_string = now.strftime("%d-%m-%Y,%H:%M:%S")
        return dt_string
    
    
    def enterOwn(self,event):
        self.entered=True
        
        
    def exitOwn(self,event):
        self.entered=False
    
    
    def enterEnemy(self,event):
        self.enteredEnemy=True
        
        
    def exitEnemy(self,event):
        self.enteredEnemy=False
        
    def updateLog(self,logEntry):
        self.Log.configure(state='normal')
        self.Log.insert(tk.INSERT, logEntry)
        self.Log.configure(state='disabled')
        self.Log.see("end")
        
        
    def checkStatus(self):
        today = datetime.datetime.now()
        todayCheck = today.strftime("%d-%m-%Y")
        initialTime = self.initialTime
        logEntry='Checking for incoming missiles...\n'
        self.updateLog(logEntry)
        txCommand = {
          "command": "findTransactions",
          "addresses": [self.fleetAddress]
        }
        findTx = json.dumps(txCommand)
        headers = {
            'content-type': 'application/json',
            'X-IOTA-API-Version': '1'
        }
        try:
            requestFindTx = requests.post(url=self.nodeURL,data=findTx,headers=headers)
            jsonDataTx = json.loads(requestFindTx.text)
            tryteCommand = {
              "command": "getTrytes",
              "hashes": jsonDataTx['hashes']
            }
        except:
            messagebox.showinfo("Error", "The address is invalid!")
        findTrytes = json.dumps(tryteCommand)
        requestTrytes = requests.post(url=self.nodeURL,data=findTrytes,headers=headers)
        jsonDataTrytes = json.loads(requestTrytes.content)
        for item in jsonDataTrytes['trytes']:
            tryteString = TryteString(item).decode(errors='ignore', strip_padding=False)
            head = tryteString.split(';')
            content = head[0].split(',')
            for data in content:
                if data == todayCheck:
                    if datetime.datetime.strptime(content[3],'%H:%M:%S') >= datetime.datetime.strptime(initialTime,'%H:%M:%S'):
                        self.incomingTime.append(content[3])
                        if len(self.incomingTime) > 1:
                            if len(set(self.incomingTime)) == self.session:
                                if datetime.datetime.strptime(content[3],'%H:%M:%S') == datetime.datetime.strptime(max(set(self.incomingTime)),'%H:%M:%S'):
                                    self.session+=1
                                    self.displayIncoming(content[0], content[1])
                                    self.displayHitResponse(content[4], content[5], content[6])
                                    break
                        else:
                            self.session+=1
                            self.displayIncoming(content[0], content[1])

                        
    def displayIncoming(self, row, col):
        if self.fleetDict[row][col] == 'S':
            mark = 'X'
            logEntry = 'An enemy projectile has struck your ship at '+row+col+'!\n'
            self.updateLog(logEntry)
            self.setOwnFleetDict(row,col,mark)
            self.setHitDict(row, col, mark)
        else:
            mark = 'o'
            logEntry = 'An enemy projectile has dropped into the ocean at '+row+col+'.\n'
            self.updateLog(logEntry)
            self.setOwnFleetDict(row,col,mark)
            self.setHitDict(row, col, mark)
            
            
    def displayHitResponse(self, row, col, mark):
        print(row+col+mark)
        if mark == 'X':
            logEntry = 'Your projectile fired at '+row+col+' has hit an enemy ship! \n'
            self.updateLog(logEntry)
            self.setEnemyFleetDict(row,col,mark)
        elif mark == 'o':
            logEntry = 'Your projectile has dropped into the ocean at '+row+col+'.\n'
            self.updateLog(logEntry)
            self.setEnemyFleetDict(row,col,mark)
        else:
            return
        
        
    def saveConnectionSettings(self):
        if len(self.targetAddressEntry.get())>0:
            self.targetAddress= self.targetAddressEntry.get()
        if len(self.addressEntry.get())>0:
            self.fleetAddress = self.addressEntry.get()
        if len(self.nodeURLEntry.get())>0:
            self.nodeURL = self.nodeURLEntry.get()

        
    def click(self,event):
        try:
            row = str(int(self.table.get_row_clicked(event)+1))
            colNum = int(self.table.get_col_clicked(event))
            col ='';
            if colNum == 0:
                col='A'
            elif colNum ==1:
                col='B'
            elif colNum ==2:
                col='C'
            elif colNum ==3:
                col='D'
            elif colNum ==4:
                col='E'
            if self.entered:
                self.fleetClick(row,col)
            elif self.enteredEnemy:
                self.lockTarget(row, col)
        except:
            print("Click not in main window")
        
        
    def fleetClick(self,row,col):
        while self.shipCount > 0:
            self.shipCount -=1
            mark = 'S'
            logEntry='You have placed a ship at '+row+col+'. '+str(self.shipCount)+' ships remain.\n'
            self.updateLog(logEntry)
            self.setOwnFleetDict(row,col,mark)
            return
        else:
            logEntry='You have no ships left to place.\n'
            self.updateLog(logEntry)
            return
        
        
    def setOwnFleetDict(self,row,col,mark):
        self.fleetDict[row][col]=mark
        self.iniFleet()
        
        
    def setEnemyFleetDict(self,row,col,mark):
        self.enemyFleetDict[row][col]=mark
        self.iniEnemyFleet()
        
        
    def setHitDict(self,row,col,mark):
        self.hitDict[row][col]='O'
        self.hitRow = row
        self.hitCol = col
        self.hitResponse = mark
                
    def lockTarget(self,row,col):
        self.ACoordinates.configure(state='normal')
        self.ACoordinates.delete("0", "end")
        self.ACoordinates.insert(tk.INSERT, row)
        self.NCoordinates.configure(state='normal')
        self.NCoordinates.delete("0", "end")
        self.NCoordinates.insert(tk.INSERT, col)
        self.targetRow = row
        self.targetCol = col
        
        
    def fire(self):
        row = self.targetRow
        col = str(self.targetCol)
        self.prepareShot(row,col)
    

    def prepareShot(self,row,col):
        try:
            #seed =  self.seed
            targetAddress = self.targetAddress
            api = Iota(self.nodeURL)
            closing = ';'
            fireTime = self.timer()
            hitRow = self.hitRow
            hitCol = self.hitCol
            hitResponse = self.hitResponse
            content = str(row+","+col+","+fireTime+","+hitRow+","+hitCol+","+hitResponse+closing)
            print(content)
            self.sendTransaction(targetAddress,content,api,row,col)
        except  Exception as e:
            print("Error preparing TX")
            logEntry=str(e)+' Transaction could not be created.\n'
            self.updateLog(logEntry)
        
        
    def sendTransaction(self,targetAddress,content,api,row,col):
        try:
            transaction = ProposedTransaction(
            address = Address(targetAddress),
            message = TryteString.from_unicode(content),
            tag = Tag(b'NODE9TEST'),
            value = 0,)
            api.send_transfer([transaction])
            self.shotFired(row,col)
        except Exception as e:
            print("Error sending TX")
            print(e)
            logEntry=str(e)+' Transaction could not be created.\n'
            self.updateLog(logEntry)

            
    def shotFired(self, row, col):
        mark = 'O'
        logEntry='You fired at '+row+col+'!\n'
        self.updateLog(logEntry)
        self.setEnemyFleetDict(row, col, mark)
    
    
    tkFont = ["Arial", 18]
    fleetDict={'1':{'A':'','B':'','C':'','D':'','E':'',},
                  '2':{'A':'','B':'','C':'','D':'','E':'',},
                  '3':{'A':'','B':'','C':'','D':'','E':'',},
                  '4':{'A':'','B':'','C':'','D':'','E':'',},
                  '5':{'A':'','B':'','C':'','D':'','E':'',}}
    
    enemyFleetDict={'1':{'A':'','B':'','C':'','D':'','E':'',},
                  '2':{'A':'','B':'','C':'','D':'','E':'',},
                  '3':{'A':'','B':'','C':'','D':'','E':'',},
                  '4':{'A':'','B':'','C':'','D':'','E':'',},
                  '5':{'A':'','B':'','C':'','D':'','E':'',}}
    
    hitDict={'1':{'A':'','B':'','C':'','D':'','E':'',},
                  '2':{'A':'','B':'','C':'','D':'','E':'',},
                  '3':{'A':'','B':'','C':'','D':'','E':'',},
                  '4':{'A':'','B':'','C':'','D':'','E':'',},
                  '5':{'A':'','B':'','C':'','D':'','E':'',}}
    
    def iniFleet(self):
        self.model = TableModel()
        self.table = TableCanvas(self.Fleet, model=self.model,
               cellwidth=105, cellbackgr='white',
               thefont=self.tkFont,rowheight=105,editable=True,
               rowselectedcolor="white",reverseorder=1,align='center')
        self.model.importDict(self.fleetDict)
        self.table.createTableFrame()
        self.table.autoResizeColumns()
        self.table.redrawTable
    
    
    def iniEnemyFleet(self):
        self.model = TableModel()
        self.table = TableCanvas(self.EnemyFleet, model=self.model,
               cellwidth=106, cellbackgr='white',
               thefont=self.tkFont,rowheight=106,editable=True,
               rowselectedcolor="white",reverseorder=1,align='center')
        self.model.importDict(self.enemyFleetDict)
        self.table.createTableFrame()
        self.table.autoResizeColumns()
        self.table.redrawTable
        
        
    def drawFleetTable(self):
        self.model = TableModel()
        self.table = TableCanvas(self.Fleet, model=self.model,
               cellwidth=50, cellbackgr='white',
               thefont=self.tkFont,rowheight=16,editable=True,
              rowselectedcolor='white',reverseorder=1)
        self.table.createTableFrame()
        self.table.model.columnNames = ['A','B','C','D','E']
        self.table.redrawTable
        self.iniFleet()
        
        
    def drawEnemyFleetTable(self):
        self.model = TableModel()
        self.table = TableCanvas(self.EnemyFleet, model=self.model,
               cellwidth=50, cellbackgr='white',
               thefont=self.tkFont,rowheight=16,editable=True,
              rowselectedcolor='white',reverseorder=1)
        self.table.createTableFrame()
        self.table.model.columnNames = ['A','B','C','D','E']
        self.table.redrawTable
        self.iniEnemyFleet()
    
    
    def __init__(self, top=None):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9' # X11 color: 'gray85'
        _ana1color = '#d9d9d9' # X11 color: 'gray85'
        _ana2color = '#ececec' # Closest X11 color: 'gray92'
        self.style = ttk.Style()
        if sys.platform == "win32":
            self.style.theme_use('winnative')
        self.style.configure('.',background=_bgcolor)
        self.style.configure('.',foreground=_fgcolor)
        self.style.configure('.',font="TkDefaultFont")
        self.style.map('.',background=
            [('selected', _compcolor), ('active',_ana2color)])
        

        top.geometry("1342x872+287+110")
        top.minsize(120, 1)
        top.maxsize(5764, 1061)
        top.resizable(1, 1)
        top.title("BattleShip v0.9")
        top.configure(background="#d9d9d9")
        top.configure(highlightbackground="#404040")
        top.configure(highlightcolor="black")
        top.bind('<ButtonRelease-1>', self.click)
        

        self.style.configure('TNotebook.Tab', background=_bgcolor)
        self.style.configure('TNotebook.Tab', foreground=_fgcolor)
        self.style.map('TNotebook.Tab', background=
            [('selected', _compcolor), ('active',_ana2color)])
        self.TNotebook1 = ttk.Notebook(top)
        self.TNotebook1.place(relx=-0.001, rely=0.0, relheight=0.982
                , relwidth=0.995)
        self.TNotebook1.configure(takefocus="")
        self.TNotebook1_t1 = tk.Frame(self.TNotebook1)
        self.TNotebook1.add(self.TNotebook1_t1, padding=3)
        self.TNotebook1.tab(0, text="Bridge",compound="left",underline="-1",)
        self.TNotebook1_t1.configure(background="#d9d9d9")
        self.TNotebook1_t1.configure(highlightbackground="#150f4a")
        self.TNotebook1_t1.configure(highlightcolor="black")
        self.TNotebook1_t2 = tk.Frame(self.TNotebook1)
        self.TNotebook1.add(self.TNotebook1_t2, padding=3)
        self.TNotebook1.tab(1, text="Options",compound="left",underline="-1",)
        self.TNotebook1_t2.configure(background="#d9d9d9")
        self.TNotebook1_t2.configure(highlightbackground="#d9d9d9")
        self.TNotebook1_t2.configure(highlightcolor="black")

        self.Fleet = tk.LabelFrame(self.TNotebook1_t1)
        self.Fleet.place(relx=0.038, rely=0.012, relheight=0.723, relwidth=0.451)
        self.Fleet.configure(relief='groove')
        self.Fleet.configure(foreground="black")
        self.Fleet.configure(text='''Our Fleet''')
        self.Fleet.configure(background="#d9d9d9")
        self.Fleet.configure(highlightbackground="#d9d9d9")
        self.Fleet.configure(highlightcolor="black")
        self.Fleet.bind('<Enter>', self.enterOwn)
        self.Fleet.bind('<Leave>', self.exitOwn)
        self.drawFleetTable()

        self.EnemyFleet = tk.LabelFrame(self.TNotebook1_t1)
        self.EnemyFleet.place(relx=0.518, rely=0.012, relheight=0.723
                , relwidth=0.452)
        self.EnemyFleet.configure(relief='groove')
        self.EnemyFleet.configure(foreground="black")
        self.EnemyFleet.configure(text='''Enemy Fleet''')
        self.EnemyFleet.configure(background="#d9d9d9")
        self.EnemyFleet.configure(highlightbackground="#d9d9d9")
        self.EnemyFleet.configure(highlightcolor="black")
        self.EnemyFleet.bind('<Enter>', self.enterEnemy)
        self.EnemyFleet.bind('<Leave>', self.exitEnemy)
        self.drawEnemyFleetTable()
        

        self.Labelframe3 = tk.LabelFrame(self.TNotebook1_t1)
        self.Labelframe3.place(relx=0.038, rely=0.747, relheight=0.235
                , relwidth=0.451)
        self.Labelframe3.configure(relief='groove')
        self.Labelframe3.configure(foreground="black")
        self.Labelframe3.configure(text='''Log''')
        self.Labelframe3.configure(background="#d9d9d9")
        self.Labelframe3.configure(highlightbackground="#d9d9d9")
        self.Labelframe3.configure(highlightcolor="black")

        self.Log = ScrolledText(self.Labelframe3)
        self.Log.place(relx=0.017, rely=0.103, relheight=0.846, relwidth=0.975
                , bordermode='ignore')
        self.Log.configure(background="white")
        self.Log.configure(state="disabled")
        self.Log.configure(font="TkTextFont")
        self.Log.configure(foreground="black")
        self.Log.configure(highlightbackground="#d9d9d9")
        self.Log.configure(highlightcolor="black")
        self.Log.configure(insertbackground="black")
        self.Log.configure(insertborderwidth="3")
        self.Log.configure(selectbackground="#c4c4c4")
        self.Log.configure(selectforeground="black")
        self.Log.configure(wrap="none")

        self.Labelframe4 = tk.LabelFrame(self.TNotebook1_t1)
        self.Labelframe4.place(relx=0.518, rely=0.747, relheight=0.235
                , relwidth=0.452)
        self.Labelframe4.configure(relief='groove')
        self.Labelframe4.configure(foreground="black")
        self.Labelframe4.configure(text='''Command''')
        self.Labelframe4.configure(background="#d9d9d9")
        self.Labelframe4.configure(highlightbackground="#d9d9d9")
        self.Labelframe4.configure(highlightcolor="black")

        self.ACoordinates = tk.Entry(self.Labelframe4)
        self.ACoordinates.place(relx=0.116, rely=0.41, height=50, relwidth=0.09
                , bordermode='ignore')
        self.ACoordinates.configure(background="white")
        self.ACoordinates.configure(disabledforeground="#a3a3a3")
        self.ACoordinates.configure(font="-family {Arial} -size 16")
        self.ACoordinates.configure(foreground="#000000")
        self.ACoordinates.configure(highlightbackground="#d9d9d9")
        self.ACoordinates.configure(highlightcolor="black")
        self.ACoordinates.configure(insertbackground="black")
        self.ACoordinates.configure(justify='center')
        self.ACoordinates.configure(selectbackground="#c4c4c4")
        self.ACoordinates.configure(selectforeground="black")

        self.NCoordinates = tk.Entry(self.Labelframe4)
        self.NCoordinates.place(relx=0.266, rely=0.41, height=50, relwidth=0.09
                , bordermode='ignore')
        self.NCoordinates.configure(background="white")
        self.NCoordinates.configure(disabledforeground="#a3a3a3")
        self.NCoordinates.configure(font="-family {Arial} -size 16")
        self.NCoordinates.configure(foreground="#000000")
        self.NCoordinates.configure(highlightbackground="#d9d9d9")
        self.NCoordinates.configure(highlightcolor="black")
        self.NCoordinates.configure(insertbackground="black")
        self.NCoordinates.configure(justify='center')
        self.NCoordinates.configure(selectbackground="#c4c4c4")
        self.NCoordinates.configure(selectforeground="black")

        self.Fire = tk.Button(self.Labelframe4,command=self.fire)
        self.Fire.place(relx=0.698, rely=0.256, height=94, width=157
                , bordermode='ignore')
        self.Fire.configure(activebackground="#ececec")
        self.Fire.configure(activeforeground="#000000")
        self.Fire.configure(background="#d9d9d9")
        self.Fire.configure(disabledforeground="#a3a3a3")
        self.Fire.configure(font="-family {Arial} -size 21")
        self.Fire.configure(foreground="#000000")
        self.Fire.configure(highlightbackground="#d9d9d9")
        self.Fire.configure(highlightcolor="black")
        self.Fire.configure(pady="0")
        self.Fire.configure(text='''Fire!''')

        self.Coordinates = tk.Label(self.Labelframe4)
        self.Coordinates.place(relx=0.116, rely=0.256, height=21, width=143
                , bordermode='ignore')
        self.Coordinates.configure(activebackground="#f9f9f9")
        self.Coordinates.configure(activeforeground="black")
        self.Coordinates.configure(background="#d9d9d9")
        self.Coordinates.configure(disabledforeground="#a3a3a3")
        self.Coordinates.configure(foreground="#000000")
        self.Coordinates.configure(highlightbackground="#d9d9d9")
        self.Coordinates.configure(highlightcolor="black")
        self.Coordinates.configure(text='''Target Coordinates''')

        self.Check = tk.Button(self.Labelframe4,command=self.checkStatus)
        self.Check.place(relx=0.432, rely=0.256, height=94, width=147
                , bordermode='ignore')
        self.Check.configure(activebackground="#ececec")
        self.Check.configure(activeforeground="#000000")
        self.Check.configure(background="#d9d9d9")
        self.Check.configure(disabledforeground="#a3a3a3")
        self.Check.configure(foreground="#000000")
        self.Check.configure(highlightbackground="#d9d9d9")
        self.Check.configure(highlightcolor="black")
        self.Check.configure(pady="0")
        self.Check.configure(text='''Check''')

        self.seedEntry = tk.Entry(self.TNotebook1_t2)
        self.seedEntry.place(relx=0.09, rely=0.145,height=30, relwidth=0.424)
        self.seedEntry.configure(background="white")
        self.seedEntry.configure(disabledforeground="#a3a3a3")
        self.seedEntry.configure(font="TkFixedFont")
        self.seedEntry.configure(foreground="#000000")
        self.seedEntry.configure(highlightbackground="#d9d9d9")
        self.seedEntry.configure(highlightcolor="black")
        self.seedEntry.configure(insertbackground="black")
        self.seedEntry.configure(selectbackground="#c4c4c4")
        self.seedEntry.configure(selectforeground="black")

        self.Seed = tk.Label(self.TNotebook1_t2)
        self.Seed.place(relx=0.09, rely=0.108, height=20, width=31)
        self.Seed.configure(activebackground="#f9f9f9")
        self.Seed.configure(activeforeground="black")
        self.Seed.configure(background="#d9d9d9")
        self.Seed.configure(disabledforeground="#a3a3a3")
        self.Seed.configure(foreground="#000000")
        self.Seed.configure(highlightbackground="#d9d9d9")
        self.Seed.configure(highlightcolor="black")
        self.Seed.configure(text='''Seed''')

        self.targetAddressEntry = tk.Entry(self.TNotebook1_t2)
        self.targetAddressEntry.place(relx=0.09, rely=0.253, height=30
                , relwidth=0.424)
        self.targetAddressEntry.configure(background="white")
        self.targetAddressEntry.configure(disabledforeground="#a3a3a3")
        self.targetAddressEntry.configure(font="TkFixedFont")
        self.targetAddressEntry.configure(foreground="#000000")
        self.targetAddressEntry.configure(highlightbackground="#d9d9d9")
        self.targetAddressEntry.configure(highlightcolor="black")
        self.targetAddressEntry.configure(insertbackground="black")
        self.targetAddressEntry.configure(selectbackground="#c4c4c4")
        self.targetAddressEntry.configure(selectforeground="black")

        self.TargetAddress = tk.Label(self.TNotebook1_t2)
        self.TargetAddress.place(relx=0.09, rely=0.217, height=21, width=88)
        self.TargetAddress.configure(activebackground="#f9f9f9")
        self.TargetAddress.configure(activeforeground="black")
        self.TargetAddress.configure(background="#d9d9d9")
        self.TargetAddress.configure(disabledforeground="#a3a3a3")
        self.TargetAddress.configure(foreground="#000000")
        self.TargetAddress.configure(highlightbackground="#d9d9d9")
        self.TargetAddress.configure(highlightcolor="black")
        self.TargetAddress.configure(text='''Target Address''')

        self.nodeURLEntry = tk.Entry(self.TNotebook1_t2)
        self.nodeURLEntry.place(relx=0.09, rely=0.47,height=30, relwidth=0.183)
        self.nodeURLEntry.configure(background="white")
        self.nodeURLEntry.configure(disabledforeground="#a3a3a3")
        self.nodeURLEntry.configure(font="TkFixedFont")
        self.nodeURLEntry.configure(foreground="#000000")
        self.nodeURLEntry.configure(highlightbackground="#d9d9d9")
        self.nodeURLEntry.configure(highlightcolor="black")
        self.nodeURLEntry.configure(insertbackground="black")
        self.nodeURLEntry.configure(selectbackground="#c4c4c4")
        self.nodeURLEntry.configure(selectforeground="black")

        self.NodeURL = tk.Label(self.TNotebook1_t2)
        self.NodeURL.place(relx=0.09, rely=0.434, height=20, width=58)
        self.NodeURL.configure(activebackground="#f9f9f9")
        self.NodeURL.configure(activeforeground="black")
        self.NodeURL.configure(background="#d9d9d9")
        self.NodeURL.configure(disabledforeground="#a3a3a3")
        self.NodeURL.configure(foreground="#000000")
        self.NodeURL.configure(highlightbackground="#d9d9d9")
        self.NodeURL.configure(highlightcolor="black")
        self.NodeURL.configure(text='''Node URL''')

        self.Connect = tk.Button(self.TNotebook1_t2)
        self.Connect.place(relx=0.293, rely=0.47, height=34, width=87)
        self.Connect.configure(activebackground="#ececec")
        self.Connect.configure(activeforeground="#000000")
        self.Connect.configure(background="#d9d9d9")
        self.Connect.configure(cursor="fleur")
        self.Connect.configure(disabledforeground="#a3a3a3")
        self.Connect.configure(foreground="#000000")
        self.Connect.configure(highlightbackground="#d9d9d9")
        self.Connect.configure(highlightcolor="black")
        self.Connect.configure(pady="0")
        self.Connect.configure(text='''Connect''')

        self.netEntry = tk.Entry(self.TNotebook1_t2)
        self.netEntry.place(relx=0.09, rely=0.554,height=70, relwidth=0.266)
        self.netEntry.configure(background="white")
        self.netEntry.configure(disabledforeground="#a3a3a3")
        self.netEntry.configure(font="TkFixedFont")
        self.netEntry.configure(foreground="#000000")
        self.netEntry.configure(highlightbackground="#d9d9d9")
        self.netEntry.configure(highlightcolor="black")
        self.netEntry.configure(insertbackground="black")
        self.netEntry.configure(selectbackground="#c4c4c4")
        self.netEntry.configure(selectforeground="black")

        self.NetStatus = tk.Label(self.TNotebook1_t2)
        self.NetStatus.place(relx=0.09, rely=0.518, height=21, width=86)
        self.NetStatus.configure(activebackground="#f9f9f9")
        self.NetStatus.configure(activeforeground="black")
        self.NetStatus.configure(background="#d9d9d9")
        self.NetStatus.configure(disabledforeground="#a3a3a3")
        self.NetStatus.configure(foreground="#000000")
        self.NetStatus.configure(highlightbackground="#d9d9d9")
        self.NetStatus.configure(highlightcolor="black")
        self.NetStatus.configure(text='''Network Status''')

        self.addressEntry = tk.Entry(self.TNotebook1_t2)
        self.addressEntry.place(relx=0.09, rely=0.361,height=30, relwidth=0.424)
        self.addressEntry.configure(background="white")
        self.addressEntry.configure(disabledforeground="#a3a3a3")
        self.addressEntry.configure(font="TkFixedFont")
        self.addressEntry.configure(foreground="#000000")
        self.addressEntry.configure(insertbackground="black")

        self.Address = tk.Label(self.TNotebook1_t2)
        self.Address.place(relx=0.09, rely=0.325, height=20, width=54)
        self.Address.configure(background="#d9d9d9")
        self.Address.configure(disabledforeground="#a3a3a3")
        self.Address.configure(foreground="#000000")
        self.Address.configure(text='''Address''')

        self.Save = tk.Button(self.TNotebook1_t2, command=self.saveConnectionSettings)
        self.Save.place(relx=0.563, rely=0.241, height=54, width=117)
        self.Save.configure(activebackground="#ececec")
        self.Save.configure(activeforeground="#000000")
        self.Save.configure(background="#d9d9d9")
        self.Save.configure(disabledforeground="#a3a3a3")
        self.Save.configure(foreground="#000000")
        self.Save.configure(highlightbackground="#d9d9d9")
        self.Save.configure(highlightcolor="black")
        self.Save.configure(pady="0")
        self.Save.configure(text='''Save''')


class AutoScroll(object):
    '''Configure the scrollbars for a widget.'''
    def __init__(self, master):
        #  Rozen. Added the try-except clauses so that this class
        #  could be used for scrolled entry widget for which vertical
        #  scrolling is not supported. 5/7/14.
        try:
            vsb = ttk.Scrollbar(master, orient='vertical', command=self.yview)
        except:
            pass
        hsb = ttk.Scrollbar(master, orient='horizontal', command=self.xview)
        try:
            self.configure(yscrollcommand=self._autoscroll(vsb))
        except:
            pass
        self.configure(xscrollcommand=self._autoscroll(hsb))
        self.grid(column=0, row=0, sticky='nsew')
        try:
            vsb.grid(column=1, row=0, sticky='ns')
        except:
            pass
        hsb.grid(column=0, row=1, sticky='ew')
        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(0, weight=1)
        # Copy geometry methods of master  (taken from ScrolledText.py)
        if py3:
            methods = tk.Pack.__dict__.keys() | tk.Grid.__dict__.keys() \
                  | tk.Place.__dict__.keys()
        else:
            methods = tk.Pack.__dict__.keys() + tk.Grid.__dict__.keys() \
                  + tk.Place.__dict__.keys()
        for meth in methods:
            if meth[0] != '_' and meth not in ('config', 'configure'):
                setattr(self, meth, getattr(master, meth))

    @staticmethod
    def _autoscroll(sbar):
        '''Hide and show scrollbar as needed.'''
        def wrapped(first, last):
            first, last = float(first), float(last)
            if first <= 0 and last >= 1:
                sbar.grid_remove()
            else:
                sbar.grid()
            sbar.set(first, last)
        return wrapped

    def __str__(self):
        return str(self.master)

def _create_container(func):
    '''Creates a ttk Frame with a given master, and use this new frame to
    place the scrollbars and the widget.'''
    def wrapped(cls, master, **kw):
        container = ttk.Frame(master)
        container.bind('<Enter>', lambda e: _bound_to_mousewheel(e, container))
        container.bind('<Leave>', lambda e: _unbound_to_mousewheel(e, container))
        return func(cls, container, **kw)
    return wrapped

class ScrolledText(AutoScroll, tk.Text):
    '''A standard Tkinter Text widget with scrollbars that will
    automatically show/hide as needed.'''
    @_create_container
    def __init__(self, master, **kw):
        tk.Text.__init__(self, master, **kw)
        AutoScroll.__init__(self, master)

import platform
def _bound_to_mousewheel(event, widget):
    child = widget.winfo_children()[0]
    if platform.system() == 'Windows' or platform.system() == 'Darwin':
        child.bind_all('<MouseWheel>', lambda e: _on_mousewheel(e, child))
        child.bind_all('<Shift-MouseWheel>', lambda e: _on_shiftmouse(e, child))
    else:
        child.bind_all('<Button-4>', lambda e: _on_mousewheel(e, child))
        child.bind_all('<Button-5>', lambda e: _on_mousewheel(e, child))
        child.bind_all('<Shift-Button-4>', lambda e: _on_shiftmouse(e, child))
        child.bind_all('<Shift-Button-5>', lambda e: _on_shiftmouse(e, child))

def _unbound_to_mousewheel(event, widget):
    if platform.system() == 'Windows' or platform.system() == 'Darwin':
        widget.unbind_all('<MouseWheel>')
        widget.unbind_all('<Shift-MouseWheel>')
    else:
        widget.unbind_all('<Button-4>')
        widget.unbind_all('<Button-5>')
        widget.unbind_all('<Shift-Button-4>')
        widget.unbind_all('<Shift-Button-5>')

def _on_mousewheel(event, widget):
    if platform.system() == 'Windows':
        widget.yview_scroll(-1*int(event.delta/120),'units')
    elif platform.system() == 'Darwin':
        widget.yview_scroll(-1*int(event.delta),'units')
    else:
        if event.num == 4:
            widget.yview_scroll(-1, 'units')
        elif event.num == 5:
            widget.yview_scroll(1, 'units')

def _on_shiftmouse(event, widget):
    if platform.system() == 'Windows':
        widget.xview_scroll(-1*int(event.delta/120), 'units')
    elif platform.system() == 'Darwin':
        widget.xview_scroll(-1*int(event.delta), 'units')
    else:
        if event.num == 4:
            widget.xview_scroll(-1, 'units')
        elif event.num == 5:
            widget.xview_scroll(1, 'units')

if __name__ == '__main__':
    vp_start_gui()
    



