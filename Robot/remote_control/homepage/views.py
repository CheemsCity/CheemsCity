from django.shortcuts import render
from django.http.response import StreamingHttpResponse
from controller.models import Camera


def index(request):
	return render(request, 'homepage.html')

def gen(camera):
	while True:
		frame = camera.frame()
		yield (b'--frame\r\n'
				b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def camera_stream(request):
    cam = Camera()
    return StreamingHttpResponse(gen(cam),content_type='multipart/x-mixed-replace; boundary=frame')