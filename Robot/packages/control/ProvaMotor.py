from hardware.Motor import Motor
import time

motori = Motor()
motori.Test()
motori.Power('r', 0)
time.sleep(1)
motori.Power('l', 0)
