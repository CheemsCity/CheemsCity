import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import threading
import datetime
import os
from chessboard import Chessboard
import yaml
import time

class ChessboardApp:
    
    def __init__(self, VideoStream, outPath):
        
        self.vs = VideoStream
        self.outPath = outPath
        self.frame = None
        self.thread = None
        self.endEvent = None
        self.chessboards = []
        self.n = 0
        #self.ctrl serve per attivare il delay dopo un'immagine buona in modo che l'utente capisca che è stata presa
        self.ctrl = False
        
        
        #create the main window of an application
        self.root = tk.Tk() #start
        #panel for image
        self.panel = None
        
        #barra che indica il progresso nel raccoglimento foto
        pbar = ttk.Progressbar(self.root, orient = 'horizontal', length = 300, mode = 'determinate')
        pbar['value'] = self.n * 100/14
        pbar.pack(padx=10, pady = 10)
        
        #testo che indica quante foto raccogliere e quante da raccogliere
        value_label = ttk.Label(self.root, text = f"Current Progress: {self.n}/14")
        value_label.pack(padx=10, pady =10)
        
        if self.n >= 14:
            #se è stato raggiunto il numero giusto di foto il bottone è cliccabile e azionerà la creazione e salvataggio della matrice
            #per creare un bottone:
            btn = tk.Button(self.root, text = "SAVE", command = self.SaveMatrix, bg = "#07e041")
            #pack è uno dei geometry managment mechanism
            btn.pack(side = 'bottom', fill="both", expand = "yes", padx=10, pady =10)
        
        else:
            btn = tk.Button(self.root, text = "SAVE", command = None)
            btn.pack(side = 'bottom', fill="both", expand = "yes", padx=10, pady =10)
        
        #thread che poolla i frame dalla camera
        self.endEvent= threading.Event()
        self.thread = threading.Thread(target=self.videoLoop, args=())
        self.thread.start()
        
        
        
        # set a callback to handle when the window is closed
        self.root.wm_title("Camera Calibration")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)
        
    def videoLoop(self):
        
        try:
            
            while not self.endEvent.is_set():
                ret, self.frame = self.vs.read()
                
                #analize image for chessboard
                if self.n<14:
                    #attiva l'analisi delle foto finchè necessario
                    chessboard = Chessboard(nx = 7, ny = 6,frame = self.frame)
                    if chessboard.ret == True:
                        self.ctrl = True
                        self.chessboards.append(chessboard)
                        self.n += 1
                        cv2.drawChessboardCorners(self.frame, (7,6), chessboard.corners2, chessboard.ret)
                        
                    
                #opencv represents image in BGR, we need to convert i RGB
                image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(image)
                image = ImageTk.PhotoImage(image)
                
                if self.panel is None:
                    #blocco display del video
                    self.panel = tk.Label(image=image)
                    self.panel.image = image
                    self.panel.pack(side="top", padx=10, pady=10)
                    
                else:
                    self.panel.configure(image=image)
                    self.panel.image = image
                
                if self.ctrl:
                    
                    time.sleep(1)
                    self.ctrl = False
                    
        except RuntimeError:
            print("[INFO] caught a Runtimeerror")
    
            
    def SaveMatrix(self):
        
        objpoints = []
        imgpoints = []
        shape = self.chessboards[0].dimensions
        for chessboard in self.chessboards:
            objpoints.append(chessboard.objpoints)
            imgpoints.append(chessboard.imgpoints)
            
        ret, matrix, distortion_coef, rv, tv = cv2.calibrateCamera(objpoints, imgpoints, shape, None, None)
        
        calibration_data = {
            "camera_matrix": matrix, 
            "distortion_coefficient": distortion_coef
        }
        
        with open('calibration_data.yml', 'w') as outfile:
            yaml.dump(data, outfile, default_flow_style=False)
        
        print("[INFO] saved calibration_data.yml")
        
        
    def onClose(self):
        # set the stop event, cleanup the camera, and allow the rest of
        # the quit process to continue
        print("[INFO] closing...")
        self.endEvent.set()
        self.vs.release()
        self.root.quit()
    