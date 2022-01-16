from http.client import REQUEST_HEADER_FIELDS_TOO_LARGE
from django.shortcuts import render
from django.http.response import StreamingHttpResponse
from controller.models import Camera
from .forms import CameraFilter

def index(request):
	filter = 'clear'
	if request.method == 'GET':
		form = CameraFilter(request.GET)
		if form.is_valid():
			filter = request.GET['filter']
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
	cam = Camera()
	filter = 'clear'
	if request.method == 'GET':
		filter = request.GET['filter']
	return StreamingHttpResponse(stream(cam,filter),content_type='multipart/x-mixed-replace; boundary=frame')
