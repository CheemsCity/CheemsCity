from PID import PID

pid = PID(0,0,0)
pid.tune(10,0,0)
mossa = pid.compute(50)
print("valore u " + str(mossa))
