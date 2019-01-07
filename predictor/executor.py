
import forward
import numpy as np;

out =forward.forward_all("/media/gathika/MainDisk/entgra_repos/deep-parking/mAlexNet-on-Combined_CNRParkAB_Ext_train-val-PKLot_val/deploy.prototxt", "/media/gathika/MainDisk/entgra_repos/deep-parking/mAlexNet-on-Combined_CNRParkAB_Ext_train-val-PKLot_val/snapshot_iter_6275.caffemodel",
                    "images.txt");
np.save('predictions.npy', out)
newArray = np.load("predictions.npy")


for x in range(0,23,1):
    availability = (newArray[x,0])
    if(availability<1.0*(10**(-25))):
        print ("slot"+str(x+1)+": "+str(0))
    else:
        print ("slot" +str(x+1) + ": " + str(1))

