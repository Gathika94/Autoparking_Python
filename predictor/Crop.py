import cv2
import os
import ast



#image cropping
def cropper(coordinates, image, imageURLFilePath, cropFolder):

    coordinatesList=ast.literal_eval(coordinates)
    slots = len(coordinatesList);
    needToWrite = False

    if not (os.path.exists(imageURLFilePath)):
        imageURLFile = open(imageURLFilePath, "w+")
        needToWrite=True

    for i in range(0,slots,1):
        slotMargins = (coordinatesList[i])
        x1 = slotMargins[0]
        x2 = slotMargins[1]
        y1 = slotMargins[2]
        y2 = slotMargins[3]
        croppedImg = image[x1:x2,y1:y2]
        filePath = cropFolder+"/"+"slot"+str(i+1)+"."+"png"
        cv2.imwrite(str(filePath),croppedImg)
        if(needToWrite):
            imageURLFile.write(filePath+"\n")


