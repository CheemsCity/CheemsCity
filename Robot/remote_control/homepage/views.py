from http.client import REQUEST_HEADER_FIELDS_TOO_LARGE
from django.shortcuts import render
from django.http.response import StreamingHttpResponse
from controller.models import Camera
from .forms import CameraFilter

cam = Camera()
bw_status = 0

def index(request):
	global bw_status
	filter = 'clear'
	if request.method == 'GET':
		form = CameraFilter(request.GET)
		if form.is_valid():
			filter = request.GET['filter']
	#TODO mettere gestione avanti,indietro,ecc.
		if 'action' in request.GET:
			action = request.GET['action']
			if action == 'bwready':
				#bw.ready()
				bw_status = 0
			elif action == 'forward':
				#bw.speed = SPEED
				#bw.forward()
				bw_status = 1
			elif action == 'backward':
				#bw.speed = SPEED
				#bw.backward()
				bw_status = -1
			elif action == 'stop':
				#bw.stop()
				bw_status = 0
			print(bw_status)
			# elif action == 'fwready':
			# 	#fw.ready()
			# elif action == 'fwleft':
			# 	#fw.turn_left()
			# elif action == 'fwright':
			# 	#fw.turn_right()
			# elif action == 'fwstraight':
			# 	#fw.turn_straight()

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
