import cv2


#img = cv2.imread("/media/gathika/MainDisk/entgra_repos/asas/autoparking/images/camera1/park_side4.jpg",1)
#coordinates = [[436,592,256,476], [309,420,214,475], [204,279,250,484]]
#folderPath = "/media/gathika/MainDisk/entgra_repos/asas/autoparking/images/camera1_slots/";
#print (img.shape)


def cropper(coordinates, image):

    slots = len(coordinates);
    count = 1;
    for i in range(0,slots,1):
        x1 = coordinates[i][0]
        x2 = coordinates[i][1]
        y1 = coordinates[i][2]
        y2 = coordinates[i][3]
        croppedImg = image[x1:x2,y1:y2]
        #cropped2 = img[309:420,214:475]
        #cropped3 = img[204:279,250:484]
        folderPath = "/media/gathika/MainDisk/entgra_repos/asas/autoparking/images/camera1_slots/"
        filePath = folderPath+"slot"+str(i+1)+"."+"png"
        print filePath
       # filePath = "/media/gathika/MainDisk/entgra_repos/AutoParking/images/cropped/park_cropped2.png"
        cv2.imwrite(str(filePath),croppedImg)
        #cv2.imwrite("/media/gathika/MainDisk/entgra_repos/AutoParking/images/cropped/park_cropped2.png",croppedImg)
        #cv2.imwrite("/media/gathika/MainDisk/entgra_repos/AutoParking/images/cropped/park_cropped3.png",cropped3)

#cropper(coordinates,img)