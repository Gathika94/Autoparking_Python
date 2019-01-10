
import forward
import Crop
import numpy as np;
from flask import Flask, request
from flask_restful import Resource, Api
import json
from sqlalchemy import create_engine
import subprocess
import os
import cv2


app = Flask(__name__)
api = Api(app)

def methodRunner():
    out = forward.forward_all(
        "/media/gathika/MainDisk/entgra_repos/deep-parking/mAlexNet-on-Combined_CNRParkAB_Ext_train-val-PKLot_val/deploy.prototxt",
        "/media/gathika/MainDisk/entgra_repos/deep-parking/mAlexNet-on-Combined_CNRParkAB_Ext_train-val-PKLot_val/snapshot_iter_6275.caffemodel",
        "images.txt")
    print ("received")
    np.save('predictions.npy', out)
    newArray = np.load("predictions.npy")

    output = [{}]

    for x in range(0, 23, 1):
        availability = (newArray[x, 0])
        if (availability < 1.0 * (10 ** (-25))):
            print ("slot" + str(x + 1) + ": " + str(0))
            output[0]["slot" + str(x + 1)] = 0
        else:
            print ("slot" + str(x + 1) + ": " + str(1))
            output[0]["slot" + str(x + 1)] = 1
    return output


def scriptRunner():
    cmd = 'python forward.py /media/gathika/MainDisk/entgra_repos/deep-parking/mAlexNet-on-Combined_CNRParkAB_Ext_train-val-PKLot_val/deploy.prototxt /media/gathika/MainDisk/entgra_repos/deep-parking/mAlexNet-on-Combined_CNRParkAB_Ext_train-val-PKLot_val/snapshot_iter_6275.caffemodel images.txt predictions.npy'
    #p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    os.system(cmd)
    newArray = np.load("predictions.npy")

    output = {}
    available = 0
    occupied  = 0

    for x in range(0, 23, 1):
        availability = (newArray[x, 0])
        if (availability < 4.0 * (10 ** (-24))):
            print ("slot" + str(x + 1) + ": " + str(0))
            output["slot" + str(x + 1)] = 0
            print ("availability : "+str(availability))
            occupied = occupied+1
        else:
            print ("slot" + str(x + 1) + ": " + str(1))
            output["slot" + str(x + 1)] = 1
            print ("availability : " + str(availability))
            available=available+1

    output["available"] = available
    output["occupied"] = occupied
    jsonOutput = json.dumps(output)
    return jsonOutput
    



class APIOutput(Resource):
    def get(self):
        storage = "/media/gathika/MainDisk/entgra_repos/asas/autoparking/images/"
        #coordinates = [[436, 592, 256, 476], [309, 420, 214, 475], [204, 279, 250, 484]]
        url = request.args.get('camurl')
        print "url :" + str(url)
        coordinates = request.args.get('coord')
        print "coord :"+coord
        imagePath = storage+str(url)+"/"+"park_side4.jpg"
        image = cv2.imread(imagePath,1)
        print "aaa"
        Crop.cropper(coordinates,image)
        print "bbb"


        return {"Hello": "World"}
        #return scriptRunner()


api.add_resource(APIOutput, '/output')



if __name__ == '__main__':
    app.run(port='5002')