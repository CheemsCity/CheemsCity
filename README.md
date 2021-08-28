# CheemsCity
 
(title of the project)
Tutto il materiale con documentazione del progetto di robotica Cheems City

##explanation


Algoritmo line detection:
1. Creazione della matrice di calibrazione e dei coefficienti di distorsione usando una scacchiera. 
2. Usare le matrici per correggere la distorsione data dalla camera.
3. usare i vari filtri (canny, gaussian blur, color threshold) per eliminare tutte le informazioni in eccesso.
4. applicare la trasfromazione di prospettiva a "birdeye".
5. determinare la ROI e le linee.
6. scegliere la migliore curva che approssima quelle linee.
7. Proiettare le linee di nuovo sull'immagine originale.
8. Sistemare bene la visuale

2) 
##installation guide

(usare docker)
