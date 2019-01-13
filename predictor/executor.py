
import forward
import Crop
import numpy as np
from flask import Flask, request
from flask_restful import Resource, Api
import json
import os
import cv2
import ast


app = Flask(__name__)
api = Api(app)

storage = "/media/gathika/MainDisk/entgra_repos/asas/autoparking/images/"
deployFileLocation ="/media/gathika/MainDisk/entgra_repos/deep-parking/mAlexNet-on-Combined_CNRParkAB_Ext_train-val-PKLot_val/deploy.prototxt"
modelLocation ="/media/gathika/MainDisk/entgra_repos/deep-parking/mAlexNet-on-Combined_CNRParkAB_Ext_train-val-PKLot_val/snapshot_iter_6275.caffemodel"


#run machine learning model as a method
def methodRunner(imagesFileLocation):
    out = forward.forward_all(
        deployFileLocation,
        modelLocation,
        imagesFileLocation)
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

#run machine learning model as a script
def scriptRunner(imagesFileLocation, predictionFileLocation,numberOfSlots):

    cmd = 'python forward.py'+' '+deployFileLocation+' '+ modelLocation+' '+ imagesFileLocation+' '+ predictionFileLocation
    os.system(cmd)
    newArray = np.load(predictionFileLocation)
    output = {}
    available = 0
    occupied  = 0

    for x in range(0, numberOfSlots, 1):
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
    


#API
class APIOutput(Resource):
    def get(self):
        url = request.args.get('camurl')
        coordinates = request.args.get('grid')
        coordinatesList = ast.literal_eval(coordinates)
        numberOfSlots = len(coordinatesList);
        imagePath = storage+str(url)+"/images/"+"park_side.jpg"

        search_dir = storage+str(url)+"/images/"
        os.chdir(search_dir)
        files = filter(os.path.isfile, os.listdir(search_dir))
        files = [os.path.join(search_dir, f) for f in files]  # add path to each file
        files.sort(key=os.path.getatime)
        print files
        imagePath = files[-1]
        print imagePath

        imageURLFile = storage+str(url)+"/"+"images.txt"
        predictionFile = storage+str(url)+"/"+"predictions.npy"
        cropFolder = storage+str(url)+"/"+"slots"
        image = cv2.imread(imagePath,1)
        Crop.cropper(coordinates,image,imageURLFile,cropFolder)
        #return scriptRunner(imageURLFile,predictionFile,numberOfSlots)
        return {"a":"b"}


api.add_resource(APIOutput, '/occupancy')



if __name__ == '__main__':
    app.run(port='5002')