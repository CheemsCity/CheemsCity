import numpy as np
import math
from camera.ColorFinder.finder import ColorFinder


class StreetLight:

    def __init__(self, image=None):
        self.image = image
        if self.image is not None:
            self.width = math.trunc(self.image.shape[0])
            self.height = math.trunc(self.image.shape[1])
            self.SO = (0, self.height)
            self.NE = (self.width, 0)

    def changeImage(self, imageNew=None):
        self.image = imageNew
        if self.image is not None:
            self.width = math.trunc(self.image.shape[0])
            self.height = math.trunc(self.image.shape[1])
            self.SO = (0, self.height)
            self.NE = (self.width, 0)

    def inBorder(self, SO,
                 NE):  #controllo solo le x perché le y non le modifico
        if SO[0] < 0:
            SO[0] = 0
        if NE[0] > self.width:
            NE[0] = self.width
        return (SO[0], SO[1]), (NE[0], NE[1])

    def roi(self, sign):
        coordinates = np.array(
            sign[0]
        ).T  #trasposta perché voglio una riga di coordinate x ed una di coordinate y
        xs = coordinates[0].astype(int)  #coordinate x arrotondate all'intero
        ys = coordinates[1].astype(int)  #coordinate y arrotondate all'intero
        len = max(xs) - min(
            xs)  #larghezza cartello (rispetto a piano della camera)
        #devo ora prendere la roi che è il rettangolo di uguali dimensioni a sx di quello in input
        xMin = min(
            xs) - len  #il nuovo minimo è il vecchio minimo meno la larghezza
        xMax = min(xs)  #il nuovo massimo è il vecchio minimo
        self.SO, self.NE = self.inBorder(
            [xMin, max(ys)],
            [xMax, min(ys)
             ])  #correggo in caso con i conti sono finito "fuori dai bordi"
        return self.SO, self.NE  #torno le coordinate del SO e NE del futuro rettangolo di roi

    def color(
        self
    ):  #ERA GIUSTO CONTROLLARE SEMPRE CON CHE FORMATO DI COLORE è CARICATA L'IMMAGINE
        #prima provo a cercare il rosso RGB(255,0,0) con raggio 50 => da RGB(205,0,0) a RGB(255,0,0)
        #come immagine prendo la roi calcolata sopra, RICORDARE: y viene prima della x
        finder = ColorFinder(image=self.image[self.NE[1]:self.SO[1],
                                              self.SO[0]:self.NE[0]],
                             color=(255, 0, 0),
                             radius=50)
        self.redMask = finder.distInRange()
        #cerco per il giallo RGB(255,255,0) metto raggio 60 perché il led gialli perdono tanta luminosità con piccoli sbalzi di corrente
        finder.changeValues(colorNew=(255, 255, 0), radiusNew=60)
        self.yellowMask = finder.distInRange()
        #cerco per il verde RGB(0,255,0) metto raggio 50 => da RGB(0,205,0) a RGB(0,255,0)
        finder.changeValues(colorNew=(0, 255, 0), radiusNew=50)
        self.greenMask = finder.distInRange()
        return self.redMask, self.yellowMask, self.greenMask

    def lightColor(self):
        #calcolo quanti pixel occupa un ogni colore così da trovare il colore predominante che ritengo essere il colore del semaforo
        #nota che l'algoritmo viene chiamato solo qundo c'è il cartello del semaforo
        self.r_num = np.count_nonzero(self.redMask)
        self.y_num = np.count_nonzero(self.yellowMask)
        self.g_num = np.count_nonzero(self.greenMask)
        max_num = max([self.r_num, self.y_num, self.g_num])
        if max_num == self.r_num:
            return 'r'
        elif max_num == self.y_num:
            return 'y'
        else:  #non metto un'altra conferma perché un massimo esiste per forza
            return 'g'
