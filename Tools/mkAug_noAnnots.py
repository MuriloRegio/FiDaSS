from traceback import print_exc
import numpy as np
import os
import cv2

import random
random.seed(0)


from data_aug.data_aug import *
from data_aug.bbox_util import *


DIRS = ['./Final/negatives']
IMG_PATH   = './Final/AUG_NEG'



N_TRANSFORMS = {
	'0' : 3
}

with open('new_neg_train.txt', 'r') as infile:
	TRAIN_FILES = [os.path.basename(file) for file in infile.read().split('\n')]


if not os.path.exists(IMG_PATH):
	os.mkdir(IMG_PATH)



def rotateImage(image, angle):
	image_center = tuple(np.array(image.shape[1::-1]) / 2)
	rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
	result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
	return result


def voc2box(size, box):
	dw = size[1]
	dh = size[0]

	x, y, w, h = box

	x = x*dw
	w = w*dw
	y = y*dh
	h = h*dh

	box = []
	box.append(x - w/2)
	box.append(y - h/2)
	box.append(x + w/2)
	box.append(y + h/2)

	return np.asarray(box)


def box2voc(size, box):
	dw = 1./size[1]
	dh = 1./size[0]
	x = (box[0] + box[2])/2.0
	y = (box[1] + box[3])/2.0
	w = box[2] - box[0]
	h = box[3] - box[1]
	x = x*dw
	w = w*dw
	y = y*dh
	h = h*dh
	return [x,y,w,h]


def noiser(image):
	row,col,ch= image.shape
	mean = 0
	var = 5
	sigma = var**2
	gauss = np.random.normal(mean,sigma,(row,col,ch))
	noisy = cv2.add(image, gauss, dtype=cv2.CV_8U)
	return noisy


def transform(im, bboxes):
	img = noiser(im)

	seq = Sequence(
		[
			RandomHSV(50, 50, 50),
			RandomHorizontalFlip(), 
			RandomScale(), 
			RandomTranslate(), 
			RandomRotate(10), 
			RandomShear()
		]
	)
	img_, bboxes_ = seq(img.copy(), bboxes.copy())

	return img_, bboxes_


def load(path, size):
	if not os.path.exists(path):
		return np.asarray([]), []

	with open(path, 'r') as infile:
		astxt = infile.read()

	bbxes = [
		voc2box(size, [
			eval(x) 
			for x in line.split(' ')[1:]
		])
		for line in astxt.splitlines()
	]

	classes = [line.split(' ')[0] for line in astxt.splitlines()]

	return np.asarray(bbxes), classes


def write(name, img, bbs, classes):
	cv2.imwrite(os.path.join(IMG_PATH, name)+'.png', img)

	voc = [
		' '.join([classes[i]]+[str(x) for x in box2voc(img.shape, bbs[i])])
		for i in range(len(bbs))
	]
	return

COUNT = [0]
def process(directory):
	img_dir   = directory
	annot_dir = 'Final/selected_labels'
	template  = "{}_{}" 

	imgs = os.listdir(img_dir)
	annots = os.listdir(annot_dir)

	for im in imgs:
		if im not in TRAIN_FILES:
			continue

		name = os.path.splitext(im)[0]
		label = name + '.txt'
		#if not os.path.exists(os.path.join(annot_dir, label)):continue

		img = cv2.imread(os.path.join(img_dir, im))
		img = cv2.resize(img,(768, 480))
		bboxes, classes = load(os.path.join(annot_dir, annots[0]), img.shape[:2])

		cs  = classes
		bbs = bboxes
		# print(cs)

		data = [(bbs[i], cs[i]) for i in range(len(bbs)) if cs[i] in N_TRANSFORMS and N_TRANSFORMS[cs[i]] > 0]

		if not len(data) and len(bbs):
			continue

		bbs_, cs_ = [], []
		total = []
		for bb, c in data:
			n = N_TRANSFORMS[c]

			total.append(n)
			bbs_.append(bb)
			cs_.append(c)

		bbs_ = np.asarray(bbs_)
		# total = int(round(total/len(bbs_)))
		#total = max(total)

		if not len(total):
			total = N_TRANSFORMS[None]
		else:
			total = max(total)

		# print (img.shape, total)
		j = 0

		for i in range(total):
			try:
				img_, nbbs = transform(img, bbs_)

			except Exception as e:
				try:
					img_, nbbs = transform(img, bbs_)
				except:
					print_exc()
					COUNT[0] += 1
					continue

			if len(nbbs) == len(bbs_) and not any([x is None for x in cs_]):
				j+=1
				write(template.format(name, i), img_, nbbs, cs_)

		print (name, j, '(', total, ')')



dirs = [d.replace('images', '').replace('labels', '') for d in DIRS]
[process(d) for d in dirs]
print (COUNT[0])

