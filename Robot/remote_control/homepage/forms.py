from django import forms

#questa è la lista dei filtri possibili da usare per analizzare le immagini
#la lista verrà allungata ogni qualvolta verranno aggiunti dei filtri nel pacchetto "camera"
CHOICES = [
    ('clear', 'Senza Filtri'),
    ('line_detector', 'Line Detector'),
    ('aruco', 'Aruco Markers Detector')
]

class CameraFilter(forms.Form): #lista dei vari pacchetti sviluppati sulla camera
    filter = forms.ChoiceField(choices = CHOICES)

