from hardware.Motor import Motor
import pygame
import time

pygame.init()
motori =Motor()
screen = pygame.display.set_mode([240, 160])

while True:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                motori.Right(90)
                print("Destra")
            elif event.key == pygame.K_LEFT:
                motori.Left(100)
                print("Sinistra")
            elif event.key == pygame.K_UP:
                motori.Avanti(100)
                print("Avanti")
            elif event.key == pygame.K_DOWN:
                motori.Indietro(100)
                print("indietro")
            elif event.key == pygame.K_q:
                pygame.quit()
        elif event.type == pygame.KEYUP:
            print("Tasto non premuto")
            motori.Power('r', 0)
            motori.Power('l', 0)
