import base64
import json
import cv2
import ast


#imagePath = "snap22.jpg"
#gridCoordinates = "[[256, 286, 390, 450], [259, 289, 450, 510], [262, 292, 510, 570], [265, 295, 570, 630], " \
#                  "[268, 298, 630, 690], [271, 301, 690, 750], [274, 304, 750, 810], [277, 307, 810, 870], " \
#                  "[280, 310, 870, 930]]"

sourceDirectory = "/media/gathika/MainDisk/entgra_repos/asas/autoparking/testing_images/";
def drawGridLine(imagePath,gridCoordinates):
    img = cv2.imread(imagePath, 1)
    gridLineList = ast.literal_eval(gridCoordinates)
    numberOfGrids=len(gridLineList)
    print gridLineList
    for j in range(0,numberOfGrids,1):
        print gridLineList[j]
        coordinatesList= gridLineList[j]
        numberOfSlots = len(coordinatesList)
        needToWrite = False
        output={}
        for i in range(0, numberOfSlots, 1):
            slotMargins = (coordinatesList[i])
            y1 = slotMargins[0]
            y2 = slotMargins[1]
            x1 = slotMargins[2]
            x2 = slotMargins[3]
            cv2.line(img, (x1, y1), (x2, y1), (255, 0, 0), 2, 1)
            cv2.line(img, (x1, y2), (x2, y2), (255, 0, 0), 2, 1)
            cv2.line(img, (x1, y1), (x1, y2), (255, 0, 0), 2, 1)
            cv2.line(img, (x2, y1), (x2, y2), (255, 0, 0), 2, 1)
    newImagePath = sourceDirectory+"newSnap.jpg"
    cv2.imwrite(newImagePath, img)
    newImage=cv2.imread(newImagePath,1)
    resizedImage = cv2.resize(newImage, (1000, 600))
    cv2.imwrite("resized.jpg", resizedImage)
    retval, buffer = cv2.imencode('.jpg', resizedImage)
    print buffer
    image_as_text = base64.b64encode(buffer)
    output["image"] = image_as_text
    jsonOutput = json.dumps(output)
    return jsonOutput
