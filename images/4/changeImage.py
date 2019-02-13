from shutil import copyfile
from shutil import copy2
import ntpath
import os

storage = "/media/gathika/MainDisk/entgra_repos/asas/autoparking/images/"
deployFileLocation = "/media/gathika/MainDisk/entgra_repos/deep-parking/mAlexNet-on-Combined_CNRParkAB_Ext_train-val-PKLot_val/deploy.prototxt"
modelLocation = "/media/gathika/MainDisk/entgra_repos/deep-parking/mAlexNet-on-Combined_CNRParkAB_Ext_train-val-PKLot_val/snapshot_iter_6275.caffemodel"
searchDir = storage + str(4) + "/images/"

showImageDir = storage+str(4)+"/showImages"
os.chdir(showImageDir)
files = filter(os.path.isfile, os.listdir(showImageDir))
files = [os.path.join(showImageDir, f) for f in files]  # add path to each file
files.sort(key=os.path.getatime)
imagePath = files[0]
oldImagePath = files[-1]
oldImageBaseName = ntpath.basename(oldImagePath)
imageBaseName = ntpath.basename(imagePath);
oldName = "oldImage.jpg"
newName = "newImage.jpg"

os.rename(oldImageBaseName, oldName)
os.rename(imageBaseName, newName)


newImagePath = showImageDir + "/" + newName
copy2(newImagePath, searchDir)
print "newImagePath" + newImagePath
