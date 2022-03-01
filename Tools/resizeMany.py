import cv2
import os

source = 'Final/selected'
net_shape = (768, 480)

for file in os.listdir(source):
	fpath = os.path.join(source, file)

	img = cv2.imread(fpath)
	img = cv2.resize(img, net_shape)

	cv2.imwrite(fpath, img)
