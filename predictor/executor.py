import base64

import forward
import crop
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
deployFileLocation = "/media/gathika/MainDisk/entgra_repos/deep-parking/mAlexNet-on-Combined_CNRParkAB_Ext_train-val-PKLot_val/deploy.prototxt"
modelLocation = "/media/gathika/MainDisk/entgra_repos/deep-parking/mAlexNet-on-Combined_CNRParkAB_Ext_train-val-PKLot_val/snapshot_iter_6275.caffemodel"


# run machine learning model as a method
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


# run machine learning model as a script
def scriptRunner(imagesFileLocation, predictionFileLocation, numberOfSlots, image_as_text):
    cmd = 'python forward.py' + ' ' + deployFileLocation + ' ' + modelLocation + ' ' + imagesFileLocation + ' ' + \
          predictionFileLocation
    os.system(cmd)
    newArray = np.load(predictionFileLocation)
    output = {}
    available = 0
    occupied = 0

    for x in range(0, numberOfSlots, 1):
        availability = (newArray[x, 0])
        if (availability < 4.0 * (10 ** (-24))):
            print ("slot" + str(x + 1) + ": " + str(0))
            output["slot" + str(x + 1)] = 0
            print ("availability : " + str(availability))
            occupied = occupied + 1
        else:
            print ("slot" + str(x + 1) + ": " + str(1))
            output["slot" + str(x + 1)] = 1
            print ("availability : " + str(availability))
            available = available + 1

    output["available"] = available
    output["occupied"] = occupied
    output["image"] = image_as_text
    jsonOutput = json.dumps(output)
    return str(jsonOutput)


@app.route('/occupancy',methods=['GET'])
def index():
    # extract data from api parameters
    url = request.args.get('camurl')
    coordinates = request.args.get('grid')
    coordinatesList = ast.literal_eval(coordinates)
    numberOfSlots = len(coordinatesList);

    # directory and file paths
    imageURLFile = storage + str(url) + "/" + "images.txt"
    predictionFile = storage + str(url) + "/" + "predictions.npy"
    cropFolder = storage + str(url) + "/" + "slots"

    # sorting images of a particular camera based on access time
    startingDir = os.getcwd()
    searchDir = storage + str(url) + "/images/"
    os.chdir(searchDir)
    files = filter(os.path.isfile, os.listdir(searchDir))
    files = [os.path.join(searchDir, f) for f in files]  # add path to each file
    files.sort(key=os.path.getatime)
    imagePath = files[-1]
    os.chdir(startingDir)

    # crop image
    image = cv2.imread(imagePath, 1);
    crop.cropper(coordinates, image, imageURLFile, cropFolder);
    resizedImage = cv2.resize(image, (400, 300))
    cv2.imwrite("resized.jpg", resizedImage)
    retval, buffer = cv2.imencode('.jpg', resizedImage)
    print buffer
    image_as_text = base64.b64encode(buffer)

    # return occupance status
    return scriptRunner(imageURLFile, predictionFile, numberOfSlots, image_as_text)

@app.route('/image/<camid>',methods=['GET'])
def getImage(camid):
    image = request.args.get('image')
    output ={}
    output["camid"]=camid
    output["image"]=image
    jsonOutput = json.dumps(output)
    return jsonOutput

@app.route('/location/<locationid>',methods=['GET'])
def getLocationDetails(locationid):
    # extract data from api parameters
    url = locationid
    coordinates = request.args.get('grid')
    coordinatesList = ast.literal_eval(coordinates)
    numberOfSlots = len(coordinatesList);

    # directory and file paths
    imageURLFile = storage + str(url) + "/" + "images.txt"
    predictionFile = storage + str(url) + "/" + "predictions.npy"
    cropFolder = storage + str(url) + "/" + "slots"

    # sorting images of a particular camera based on access time
    startingDir = os.getcwd()
    searchDir = storage + str(url) + "/images/"
    os.chdir(searchDir)
    files = filter(os.path.isfile, os.listdir(searchDir))
    files = [os.path.join(searchDir, f) for f in files]  # add path to each file
    files.sort(key=os.path.getatime)
    imagePath = files[-1]
    os.chdir(startingDir)

    # crop image
    image = cv2.imread(imagePath, 1);
    crop.cropper(coordinates, image, imageURLFile, cropFolder);
  

    # return occupance status
    return scriptRunner(imageURLFile, predictionFile, numberOfSlots, imagePath)




if __name__ == '__main__':
    app.run(port='5002')
