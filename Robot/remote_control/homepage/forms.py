from django import forms

CHOICES = [
    ('clear', 'Senza Filtri'),
    ('line_detector', 'Line Detector'),
    ('aruco', 'Aruco Markers Detector')
]

class CameraFilter(forms.Form): #lista dei vari pacchetti sviluppati sulla camera
    filter = forms.ChoiceField(choices = CHOICES)
