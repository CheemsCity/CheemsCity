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
from picamera import PiCamera
from camera.CameraStream import CameraStream
from threading import Thread
from camera.FPS import FPS
import numpy as np

class ChessboardApp:
    
    def __init__(self, VideoStream, outPath):
        with open(r'camera_calibration_settings.yaml') as file:
            self.settings = yaml.full_load(file)
        self.vs = VideoStream
        self.outPath = outPath
        self.frame = None
        self.thread = None
        self.endEvent = None
        self.chessboards = []
        self.n = 0
        self.cod = False
        #self.ctrl serve per attivare il delay dopo un'immagine buona in modo che l'utente capisca che è stata presa
        self.ctrl = False
        self.nThresh = 5 #min number of cheesboard's data to create the matrix
        
        
        #create the main window of an application
        self.root = tk.Tk() #start
        self.root.geometry(self.settings['camera_calibration_canvasResolution'])
        #panel for image
        self.panel = None
        
        #barra che indica il progresso nel raccoglimento foto
        self.pbar = ttk.Progressbar(self.root, orient = 'horizontal', length = 300, mode = 'determinate')
        self.pbar.pack(padx=10, pady = 10)
        
        #testo che indica quante foto raccogliere e quante da raccogliere
        value_label = ttk.Label(self.root, text =self.update_label())
        value_label.pack(padx=10, pady =10)
        
       # if self.n >= 14:
            #se è stato raggiunto il numero giusto di foto il bottone è cliccabile e azionerà la creazione e salvataggio della matrice
            #per creare un bottone:
            #self.btn = tk.Button(self.root, text = "SAVE", command = self.SaveMatrix, bg = "#07e041")
            #pack è uno dei geometry managment mechanism
            #self.btn.pack(side = 'bottom', fill="both", expand = "yes", padx=10, pady =10)
        
       # else:
        self.btn = tk.Button(self.root, text = "SAVE", command = self.SaveMatrix,  state = 'disabled')
        self.btn.pack(side = 'bottom', fill="both", expand = "yes", padx=10, pady =10)

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
                self.frame = self.vs.read()
                
                #analize image for chessboard
                if self.n < self.nThresh:
                    #attiva l'analisi delle foto finchè necessario
                    chessboard = Chessboard(nx = self.settings['camera_calibration_chessboardX'], ny = self.settings['camera_calibration_chessboardY'],frame = self.frame, square_size = self.settings['camera_calibration_squareSize']) #metri
                    if chessboard.ret == True:
                        self.ctrl = True
                        self.chessboards.append(chessboard)
                        self.n += 1
                        self.pbar['value']=(self.n * 100)/self.nThresh
                        cv2.drawChessboardCorners(self.frame, (8, 8), chessboard.imgpoints, chessboard.ret)
                        print(self.n)

                if (self.n==self.nThresh and  self.cod ==False):
                    #self.btn.configure(command = self.SaveMatrix, bg = "#07e041")
                    self.btn['bg'] = "#07e041"
                    self.btn['state'] = 'normal'
                    self.cod = True
                    
                #opencv represents image in BGR, we need to convert i RGB
                image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(image)
                image = image.resize(self.settings['camera_calibration_resizeImage'], Image.ANTIALIAS)
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

        print("[INFO] starting the calculation for the matrix, wait 30s...")
        objpoints = []
        imgpoints = []
        h, w = self.frame.shape[:2]
        for chessboard in self.chessboards:
            objpoints.append(chessboard.objpoints)
            imgpoints.append(chessboard.imgpoints)
            
        ret, matrix, distortion_coef, rv, tv = cv2.calibrateCamera(objpoints, imgpoints, (w,h), None, None)
        print("[INFO] starting the file's creation")
        calibration_data = {
            "camera_matrix": matrix, 
            "distortion_coefficient": distortion_coef
        }
        
        with open('../prova.yml', 'w') as outfile:
            yaml.dump(calibration_data, outfile, default_flow_style=False)
        
        print("[INFO] saved FinalCalibration.yml")
        
        
    def onClose(self):
        # set the stop event, cleanup the camera, and allow the rest of
        # the quit process to continue
        print("[INFO] closing...")
        self.endEvent.set()
        print("[DEBUG] endEvent")
        self.vs.stop()
        print("[DEBUG] end vs")
        self.root.quit()
        print("[DEBUG] end root")

    def update_label(self):
        return f"Foto acquisite: {self.n}"
