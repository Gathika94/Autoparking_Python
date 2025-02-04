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
import datetime
import pathlib2
import grid
import drawGrid
import logging

app = Flask(__name__)
api = Api(app)

storage = "/media/gathika/MainDisk/entgra_repos/asas/autoparking/images/"
deployFileLocation = "/media/gathika/MainDisk/entgra_repos/deep-parking/mAlexNet-on-Combined_CNRParkAB_Ext_train-val-PKLot_val/deploy.prototxt"
modelLocation = "/media/gathika/MainDisk/entgra_repos/deep-parking/mAlexNet-on-Combined_CNRParkAB_Ext_train-val-PKLot_val/snapshot_iter_6275.caffemodel"


logging.basicConfig(level=logging.DEBUG, filename="file.log", format='%(asctime)s - %(message)s')

def checkOccupancy(url, coordinates, gridThreshold):
    coordinatesList = ast.literal_eval(coordinates)
    numberOfSlots = len(coordinatesList)

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
    image = cv2.imread(imagePath, 1)
    crop.cropper(coordinates, image, imageURLFile, cropFolder)

    # metaData
    createdTime = getImageCreatedTime(imagePath);  # need to fix - last access time for

    # return occupance status
    print "number of slots :" + str(numberOfSlots)
    output = scriptRunnerWithThreshold(imageURLFile, predictionFile, numberOfSlots, imagePath, gridThreshold)
    occupied = output["occupied"]
    return occupied


def chooseBestGrid(url, horizontalStart, horizontalEnd, horizontalGap, verticalStart, verticalSize, verticalInclination,
                   horizontalIncrement, horizontalIncrementSteps, verticalIncrement, verticalIncrementSteps,
                   gridThreshold):
    selectedGrids = findSuitableGrid(horizontalStart, horizontalEnd, horizontalGap, verticalStart, verticalSize,
                                     verticalInclination, horizontalIncrement, horizontalIncrementSteps,
                                     verticalIncrement, verticalIncrementSteps)
    numberOfGrids = len(selectedGrids)
    maxOccupied = -1
    currentlySelectedGrid = ""
    for i in range(0, numberOfGrids, 1):
        internalGrid = str(selectedGrids[i])
        occupied = checkOccupancy(url, internalGrid, gridThreshold)
        print "occupied : " + str(occupied)
        print "grid : " + internalGrid
        if (occupied > maxOccupied):
            maxOccupied = occupied
            currentlySelectedGrid = internalGrid
    return str(currentlySelectedGrid)


def findSuitableGrid(horizontalStart, horizontalEnd, horizontalGap, verticalStart, verticalSize, verticalInclination,
                     horizontalIncrement, horizontalIncrementSteps, verticalIncrement, verticalIncrementSteps):
    horizontalWidth = horizontalEnd - horizontalStart
    horizontalIncrement = horizontalIncrement
    horizontalIncrementSteps = horizontalIncrementSteps
    verticalIncrement = verticalIncrement
    verticalIncrementSteps = verticalIncrementSteps
    grids = []
    for i in range(0, horizontalIncrementSteps, 1):
        newHorizontalStart = horizontalStart + i * horizontalIncrement
        newHorizontalEnd = horizontalStart + horizontalWidth
        for j in range(0, verticalIncrementSteps, 1):
            newVerticalStart = verticalStart + j * verticalIncrement
            singleGrid = grid.horizontalGridLine(newHorizontalStart, newHorizontalEnd, horizontalGap, newVerticalStart,
                                                 verticalSize, verticalInclination)
            grids.append(singleGrid)
    return grids


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
        if (availability < 1.0 * (10 ** (-15))):
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
    slots = {}
    available = 0
    occupied = 0

    for x in range(0, numberOfSlots, 1):
        availability = (newArray[x, 0])
        if (availability < 1.0 * (10 ** (-15))):
            print ("slot" + str(x + 1) + ": " + str(0))
            # output["slot" + str(x + 1)] = 0
            slots["slot" + str(x + 1)] = 0
            print ("availability : " + str(availability))
            occupied = occupied + 1

        else:
            print ("slot" + str(x + 1) + ": " + str(1))
            # output["slot" + str(x + 1)] = 1
            slots["slot" + str(x + 1)] = 1
            print ("availability : " + str(availability))
            available = available + 1

    output["available"] = available
    output["occupied"] = occupied
    output["slots"] = slots
    output["image"] = image_as_text
    return output


def scriptRunnerWithThreshold(imagesFileLocation, predictionFileLocation, numberOfSlots, image_as_text, threshold):
    cmd = 'python forward.py' + ' ' + deployFileLocation + ' ' + modelLocation + ' ' + imagesFileLocation + ' ' + \
          predictionFileLocation
    os.system(cmd)
    newArray = np.load(predictionFileLocation)
    output = {}
    slots = {}
    available = 0
    occupied = 0
    availabilityList = []

    for x in range(0, numberOfSlots, 1):
        availability = (newArray[x, 0])
        if (availability < threshold):
            print ("slot" + str(x + 1) + ": " + str(0))
            # output["slot" + str(x + 1)] = 0
            slots["slot" + str(x + 1)] = 0
            print ("availability : " + str(availability))
            occupied = occupied + 1
            availabilityList.append(0)
        else:
            print ("slot" + str(x + 1) + ": " + str(1))
            # output["slot" + str(x + 1)] = 1
            slots["slot" + str(x + 1)] = 1
            print ("availability : " + str(availability))
            available = available + 1
            availabilityList.append(1)

    output["available"] = available
    output["occupied"] = occupied
    output["slots"] = slots
    output["image"] = image_as_text
    output["availabilityList"] = availabilityList
    return output


def getImageCreatedTime(imagePath):
    image = pathlib2.Path(imagePath);
    imageAccessTime = datetime.datetime.fromtimestamp(image.stat().st_atime).replace(
        microsecond=0);  # need to fix - last access time for now
    # year = imageAccessTime.year
    # month = imageAccessTime.month
    # day = imageAccessTime.day
    # hour = imageAccessTime.hour
    # minute = imageAccessTime.minute
    # createdTime={}
    # createdTime["year"] = year
    # createdTime["month"] = month
    # createdTime["day"] = day
    # createdTime["hour"] = hour
    # createdTime["minute"] = minute
    return str(imageAccessTime)


@app.route('/occupancy', methods=['GET'])
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

    # get created time using metaData
    createdTime = getImageCreatedTime(imagePath)

    # crop image
    image = cv2.imread(imagePath, 1)
    crop.cropper(coordinates, image, imageURLFile, cropFolder)
    resizedImage = cv2.resize(image, (400, 300))
    cv2.imwrite("resized.jpg", resizedImage)
    retval, buffer = cv2.imencode('.jpg', resizedImage)
    print buffer
    image_as_text = base64.b64encode(buffer)

    # return occupance status
    output = scriptRunner(imageURLFile, predictionFile, numberOfSlots, image_as_text)
    output["imagePath"] = imagePath
    output["accessedTime"] = createdTime
    jsonOutput = json.dumps(output)
    return str(jsonOutput)


@app.route('/image', methods=['GET'])
def getImage():
    imagePath = request.args.get('path')
    print "imagePath :" + imagePath
    image = cv2.imread(imagePath, 1);
    resizedImage = cv2.resize(image, (400, 300))
    cv2.imwrite("resized.jpg", resizedImage)
    retval, buffer = cv2.imencode('.jpg', resizedImage)
    image_as_text = base64.b64encode(buffer)
    output = {}
    output["image"] = image_as_text
    jsonOutput = json.dumps(output)
    return jsonOutput


@app.route('/location/<locationid>', methods=['GET'])
def getLocationDetails(locationid):
    # extract data from api parameters
    url = locationid
    coordinates = request.args.get('grid')
    coordinatesList = ast.literal_eval(coordinates)
    numberOfSlots = len(coordinatesList)

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
    image = cv2.imread(imagePath, 1)
    crop.cropper(coordinates, image, imageURLFile, cropFolder)

    # metaData
    createdTime = getImageCreatedTime(imagePath);  # need to fix - last access time for

    # return occupance status
    output = scriptRunner(imageURLFile, predictionFile, numberOfSlots, imagePath)
    # output["imagePath"] = imagePath #have to remove this
    output["accessedTime"] = createdTime
    jsonOutput = json.dumps(output)
    return jsonOutput


@app.route('/drawGrid/<locationid>', methods=['GET'])
def returnGrid(locationid):
    url = locationid
    horizontalStart = int(request.args.get('HS'))
    horizontalEnd = int(request.args.get('HE'))
    horizontalGap = int(request.args.get('HG'))
    verticalStart = int(request.args.get('VS'))
    verticalSize = int(request.args.get('VZ'))
    verticalInclination = int(request.args.get('VI'))
    horizontalIncrement = int(request.args.get('HGI'))
    horizontalIncrementSteps = int(request.args.get('HGIS'))
    verticalIncrement = int(request.args.get('VGI'))
    verticalIncrementSteps = int(request.args.get('VGIS'))
    gridThresholdValue = float(request.args.get("GTV"))
    gridThresholdPower = int(request.args.get("GTP"))
    gridThreshold = gridThresholdValue * (10 ** gridThresholdPower)
    bestGrid = chooseBestGrid(url, horizontalStart, horizontalEnd, horizontalGap, verticalStart, verticalSize,
                              verticalInclination,
                              horizontalIncrement, horizontalIncrementSteps, verticalIncrement, verticalIncrementSteps,
                              gridThreshold)
    print "selectedGrid" + bestGrid
    output = {}
    output["grid"] = bestGrid
    jsonOutput = json.dumps(output)
    return jsonOutput


@app.route('/grid/<gridid>', methods=['GET'])
def getGridDetails(gridid):
    logging.debug("grid details requested 2");
    # extract data from api parameters
    url = gridid
    coordinates = request.args.get('grid')
    print "coordinates" + coordinates
    gridThresholdValue = float(request.args.get("GTV"))
    gridThresholdPower = int(request.args.get("GTP"))
    coordinatesList = ast.literal_eval(coordinates)
    numberOfSlots = len(coordinatesList)
    gridThreshold = gridThresholdValue * (10 ** gridThresholdPower)

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
    image = cv2.imread(imagePath, 1)
    crop.cropper(coordinates, image, imageURLFile, cropFolder)

    # metaData
    createdTime = getImageCreatedTime(imagePath);  # need to fix - last access time for

    # return occupance status
    output = scriptRunnerWithThreshold(imageURLFile, predictionFile, numberOfSlots, imagePath, gridThreshold)
    # output["imagePath"] = imagePath #have to remove this
    output["accessedTime"] = createdTime
    jsonOutput = json.dumps(output)

    return jsonOutput


@app.route('/gridImage', methods=['POST'])
def getImageWithGrid():
    # extract data from api parameters
    grid = request.form['grid']
    imageFolder=request.form.get('imagePath', 'default value')
    availabilityList= request.form.get('availability', 'default value')
    sourceDirectory=storage + str(imageFolder) + "/images/"
    imagePath=sourceDirectory+"snap.jpg"
    print grid
    print imagePath
    #output={}
    #output["image"]=imagePath
    #jsonOutput = json.dumps(output)
    #return jsonOutput
    return drawGrid.drawGridLine(imagePath,grid,availabilityList,sourceDirectory)

@app.route('/createImage', methods=['POST'])
def createNewImage():
    # extract data from api parameters
    camId = request.form['camId']
    startingDir = os.getcwd()
    sourceDirectory=storage + str(camId) + "/images/"
    os.chdir(sourceDirectory)
    print "Hello World"
    print sourceDirectory
    os.chdir(startingDir)
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


if __name__ == '__main__':
    app.run(port='5002')
