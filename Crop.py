import cv2

img = cv2.imread("park_side.jpg",1)
print (img.shape)
cropped1 = img[309:420,214:475]
cropped2 = img[436:592,256:476]
cv2.imwrite("park_cropped1.png", cropped1)
cv2.imwrite("park_cropped2.png", cropped2)
