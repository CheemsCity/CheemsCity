from http.client import REQUEST_HEADER_FIELDS_TOO_LARGE
from django.shortcuts import render
from django.http.response import StreamingHttpResponse
from controller.models import Camera
from hardware.Motor import Motor
from pkg_resources import resource_string
import yaml
import numpy as np

cam = Camera() #oggetto per la camera (stream + filtri)
'''---------------------------------------------------------------------
	                variabili controllo motori
					--------------------------
'''
mot = Motor(left_trim=-3) #oggetto per comunicazione seriale con i motori
mot_status = 0 #NON ANCORA IN USO mi dà un'indicazione del verso di movimento della camera
speed = 50 #velocità standard
'''---------------------------------------------------------------------
	                variabili camera calibration
					--------------------------
'''
thresh = 40
numphoto = 0
h, w = None, None
file = resource_string('camera.CameraCalibration','camera_calibration_settings.yaml')
settings = yaml.full_load(file)
chessboards = []

def index(request):
	global mot_status, speed
	#print("il messaggio è:")
	#print(mot.ticksValue())
	filter = 'clear' #parto dal senza filtri
	if request.method == 'GET':
		if 'filter' in request.GET:
			filter = request.GET['filter'] #setto il filtro richiesto
		if 'action' in request.GET: #se torno con una richiesta di action (le frecce)
			action = request.GET['action']
			print("velocità richiesta: ")
			print(speed)
			print(type(speed))
			if action == 'ready':
				mot.Stop() #ferma i motori
				mot_status = 0
			elif action == 'stop':
				mot.Stop() #ferma i motori
				mot_status = 0
			elif action == 'frleft':
				mot.NO(speed) #va a Nord Ovest
				mot_status = 1
			elif action == 'forward':
				mot.Avanti(speed) #va a Nord
				mot_status = 1
			elif action == 'frright':
				mot.NE(speed) #va a Nord Est
				mot_status = 1
			elif action == 'bwleft':
				mot.SO(speed) #va a Sud Ovest
				mot_status = -1
			elif action == 'backward':
				mot.Indietro(speed) #va a Sud
				mot_status = -1
			elif action == 'bwright':
				mot.SE(speed) #va a Sud Est
				mot_status = -1
		elif 'speed' in request.GET: #in caso di modifica della velocità
			speed = int(request.GET['speed']) #setta la nuova velocità di gestione dei motori
	return render(request, 'homepage.html', {'filter': filter})

def stream(camera, filter):
	while True: #qui vengono chiamate diverse pipeline per i frame a seconda del filro richiesto
		if filter == 'clear':
			frame = camera.frameClear()
		elif filter == 'line_detector':
			frame = camera.frameLineDetector()
		elif filter == 'aruco':
			frame = camera.frameArucoDetector()
		yield (b'--frame\r\n'
				b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n') #si fa uno yield perché devo creare uno streming che verrà visto una volta sola

def camera_cal_stream(camera):
	global numphoto, chessboards, h, w
	while True:
		frame, chessboard, h, w = camera.frameCameraCalibration()
		if chessboard is not None:
			chessboards.append(chessboard)
			numphoto += 1
		print(np.size(frame))
		yield (b'--frame\r\n'
				b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n') #si fa uno yield perché devo creare uno streming che verrà visto una volta sola

def camera_stream(request):
	filter = 'clear'
	if request.method == 'GET':
		filter = request.GET['filter']
	return StreamingHttpResponse(stream(cam,filter),content_type='multipart/x-mixed-replace; boundary=frame') #streaming del frame generato con stream()

def camera_calibration(request): #vista della calibrazione della camera
	return StreamingHttpResponse(camera_cal_stream(cam),content_type='multipart/x-mixed-replace; boundary=frame') #streaming del frame generato con camera_cal_stream()

def CameraCalibration(request):
	global numphoto, chessboards, h, w
	if request.method == 'GET':
		if 'save' in request.GET:
			print("[INFO] starting the calculation for the matrix, wait 30s...")
			objpoints = []
			imgpoints = []
			for chessboard in self.chessboards:
				objpoints.append(chessboard.objpoints)
				imgpoints.append(chessboard.imgpoints)
				
			ret, matrix, distortion_coef, rv, tv = cv2.calibrateCamera(objpoints, imgpoints, (w,h), None, None)
			print("[INFO] starting the file's creation")
			calibration_data = {
				"camera_matrix": matrix, 
				"distortion_coefficient": distortion_coef
			}
			
			with open('./packages/camera/CameraCalibration.yaml', 'w') as outfile:
				yaml.dump(calibration_data, outfile, default_flow_style=False)
			
			print("[INFO] saved FinalCalibration.yml")
			chessboards = []
			numphoto = 0
			#disabilitare poi il bottone
	return render(request, 'cameraCal.html')
