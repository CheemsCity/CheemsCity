from http.client import REQUEST_HEADER_FIELDS_TOO_LARGE
from django.shortcuts import render
from django.http.response import StreamingHttpResponse
from controller.models import Camera
from .forms import CameraFilter
from hardware.Motor import Motor

cam = Camera() #oggetto per la camera (stream + filtri)
mot = Motor() #oggetto per comunicazione seriale con i motori
mot_status = 0 #NON ANCORA IN USO mi dà un'indicazione del verso di movimento della camera
speed = 50 #velocità standard

def index(request):
	global mot_status, speed
	filter = 'clear' #parto dal senza filtri
	if request.method == 'GET':
		form = CameraFilter(request.GET) #analizzo la richiesta di filtro
		if form.is_valid():
			filter = request.GET['filter'] #setto il filtro richiesto
		if 'action' in request.GET: #se torno con una richiesta di action (le frecce)
			action = request.GET['action']
			if action == 'ready':
				mot.ready() #se i motori funzionano
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
			speed = request.GET['speed'] #setta la nuova velocità di gestione dei motori
	else:
		form = CameraFilter()
	return render(request, 'homepage.html', {'form': form, 'filter': filter})

def stream(camera, filter):
	while True: #qui vengono chiamate diverse pipeline per i frame a seconda del filro richiesto
		if filter == 'clear':
			frame = camera.frameClear()
		elif filter == 'line_detector':
			frame = camera.frameLineDetector()
		elif filter == 'aruco':
			frame = camera.frameArucoDetector()
		yield (b'--frame\r\n'
				b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n') #si fa uno yield perché devo creare uno streming che verrà vito una volta sola

def camera_stream(request):
	filter = 'clear'
	if request.method == 'GET':
		filter = request.GET['filter']
	return StreamingHttpResponse(stream(cam,filter),content_type='multipart/x-mixed-replace; boundary=frame') #streaming del frame generato con stream()
