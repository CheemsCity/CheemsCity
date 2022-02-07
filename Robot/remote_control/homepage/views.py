from http.client import REQUEST_HEADER_FIELDS_TOO_LARGE
from django.shortcuts import render
from django.http.response import StreamingHttpResponse
from controller.models import Camera
from .forms import CameraFilter
from hardware.Motor import Motor

cam = Camera()
mot = Motor()
mot_status = 0
speed = 50

def index(request):
	global mot_status, speed
	filter = 'clear'
	if request.method == 'GET':
		form = CameraFilter(request.GET)
		if form.is_valid():
			filter = request.GET['filter']
	#TODO mettere gestione avanti,indietro,ecc.
		if 'action' in request.GET:
			action = request.GET['action']
			if action == 'ready':
				mot.ready()
				mot_status = 0
			elif action == 'stop':
				mot.Stop()
				mot_status = 0
			elif action == 'frleft':
				mot.NO(speed)
				mot_status = 1
			elif action == 'forward':
				mot.Avanti(speed)
				mot_status = 1
			elif action == 'frright':
				mot.NE(speed)
				mot_status = 1
			elif action == 'bwleft':
				mot.SO(speed)
				mot_status = -1
			elif action == 'backward':
				mot.Indietro(speed)
				mot_status = -1
			elif action == 'bwright':
				mot.SE(speed)
				mot_status = -1
		elif 'speed' in request.GET:
			speed = request.GET['speed']
	else:
		form = CameraFilter()
	return render(request, 'homepage.html', {'form': form, 'filter': filter})

def stream(camera, filter):
	while True:
		if filter == 'clear':
			frame = camera.frameClear()
		elif filter == 'line_detector':
			frame = camera.frameLineDetector()
		elif filter == 'aruco':
			frame = camera.frameArucoDetector()
		yield (b'--frame\r\n'
				b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def camera_stream(request):
	filter = 'clear'
	if request.method == 'GET':
		filter = request.GET['filter']
	return StreamingHttpResponse(stream(cam,filter),content_type='multipart/x-mixed-replace; boundary=frame')
