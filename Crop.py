import cv2
import os
import ast
#img = cv2.imread("/media/gathika/MainDisk/entgra_repos/asas/autoparking/images/camera1/park_side4.jpg",1)
#coordinates = [[436,592,256,476], [309,420,214,475], [204,279,250,484]]
#folderPath = "/media/gathika/MainDisk/entgra_repos/asas/autoparking/images/camera1_slots/";
#print (img.shape)


def cropper(coordinates, image, imageURLFilePath):


    coordinatesList=ast.literal_eval(coordinates)

    print coordinatesList[0]
    slots = len(coordinatesList);
    print "slots :"+str(slots)
    count = 1;
    needToWrite = False

    if not (os.path.exists(imageURLFilePath)):
        imageURLFile = open(imageURLFilePath, "w+")
        needToWrite=True

    for i in range(0,slots,1):
        slotMargins = (coordinatesList[i])
        print slotMargins[0]
        x1 = slotMargins[0]
        x2 = slotMargins[1]
        y1 = slotMargins[2]
        y2 = slotMargins[3]
        croppedImg = image[x1:x2,y1:y2]
        #cropped2 = img[309:420,214:475]
        #cropped3 = img[204:279,250:484]
        folderPath = "/media/gathika/MainDisk/entgra_repos/asas/autoparking/images/camera1_slots/"
        filePath = folderPath+"slot"+str(i+1)+"."+"png"
        print filePath
       # filePath = "/media/gathika/MainDisk/entgra_repos/AutoParking/images/cropped/park_cropped2.png"
        cv2.imwrite(str(filePath),croppedImg)
        if(needToWrite):
            imageURLFile.write(filePath+"\n")
        #cv2.imwrite("/media/gathika/MainDisk/entgra_repos/AutoParking/images/cropped/park_cropped2.png",croppedImg)
        #cv2.imwrite("/media/gathika/MainDisk/entgra_repos/AutoParking/images/cropped/park_cropped3.png",cropped3)

#cropper(coordinates,img)