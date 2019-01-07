import cv2


img = cv2.imread("/media/gathika/MainDisk/entgra_repos/AutoParking/images/original/park_side4.jpg",1)
print (img.shape)

cropped1 = img[436:592,256:476]
cropped2 = img[309:420,214:475]
cropped3 = img[204:279,250:484]
cv2.imwrite("/media/gathika/MainDisk/entgra_repos/AutoParking/images/cropped/park_cropped1.png",cropped1)
cv2.imwrite("/media/gathika/MainDisk/entgra_repos/AutoParking/images/cropped/park_cropped2.png",cropped2)
cv2.imwrite("/media/gathika/MainDisk/entgra_repos/AutoParking/images/cropped/park_cropped3.png",cropped3)
