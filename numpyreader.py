import numpy as np

newArray = np.load("predictions.npy")


for x in range(0,7,1):
    availability = (newArray[x,0])
    if(availability<1.0*(10**(-25))):
        print ("slot"+str(x+1)+": "+str(0))
    else:
        print ("slot" +str(x+1) + ": " + str(1))
