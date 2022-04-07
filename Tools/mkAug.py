from traceback import print_exc
import os
import numpy as np
import cv2

import random
random.seed(42)


from data_aug.data_aug import *
from data_aug.bbox_util import *


GET_NAME = lambda x: os.path.basename(os.path.splitext(x)[0])

def explorePath(path):
	annots = {}

	for (dirpath, _, files) in os.walk(path):
		for file in files:
			if file.endswith('.txt'):
				annots[GET_NAME(file)] = os.path.join(dirpath, file)

	return annots

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


def write(name, img, bbs, classes, img_path, annot_path):
	cv2.imwrite(os.path.join(img_path, name)+'.png', img)

	voc = [
		' '.join([classes[i]]+[str(x) for x in box2voc(img.shape, bbs[i])])
		for i in range(len(bbs))
	]

	with open(os.path.join(annot_path, name)+'.txt', 'w') as outfile:
		outfile.write('\n'.join(voc))


def process(img_paths, labels_path, img_size, img_save_path, label_save_path, TRAIN_FILES, N_TRANSFORMS):
	template  = "{}_{}"

	imgs = [os.path.join(path,file) for path in img_paths for file in os.listdir(path)]
	annots_path = explorePath(labels_path)

	for im in imgs:
		name = GET_NAME(im)

		if TRAIN_FILES is not None and name not in TRAIN_FILES:
			continue
			
		img = cv2.imread(im)
		img = cv2.resize(img, img_size)

		label = annots_path[name]
		bbs, cs = load(label, img_size)

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

		if not len(total):
			total = N_TRANSFORMS[None]
		else:
			total = max(total)

		j = 0
		for i in range(total):
			try:
				img_, nbbs = transform(img, bbs_)

			except Exception as e:
				try:
					img_, nbbs = transform(img, bbs_)
				except:
					print_exc()
					continue

			if len(nbbs) == len(bbs_) and not any([x is None for x in cs_]):
				j+=1
				write(template.format(name, i), img_, nbbs, cs_, img_save_path, label_save_path)

		print (name, j, '(', total, ')')


def main(img_paths, labels_path, img_size, img_save_path, label_save_path, train_list, transforms):
	N_TRANSFORMS = {str(idx):amt for idx, amt in enumerate(transforms)}

	img_size = tuple(img_size)
	img_size = (img_size[0],img_size[0]) if len(img_size) == 1 else img_size[:2]

	TRAIN_FILES = None
	if train_list is not None:
		with open(train_list, 'r') as infile:
			TRAIN_FILES = [GET_NAME(file) for file in infile.read().split('\n')]


	for dir in [img_save_path, label_save_path]:
		if not os.path.exists(dir):
			os.mkdir(dir)

	process(img_paths, labels_path, img_size, img_save_path, label_save_path, TRAIN_FILES, N_TRANSFORMS)



if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Tool for creating an augmented train dataset.")

    parser.add_argument('--images_path', type=str, nargs='+', required=True,
                help='Relative path to the folder containing the train images.')

    parser.add_argument('--labels_path', type=str, required=True,
                help='Relative path to the directory containing annotations (may be a path to subfolders containing the annotations).')

    parser.add_argument('--img_size', type=int, nargs='+', default=[512,512],
                help='Image dimensions of the network input.')

    parser.add_argument('--img_save_path', type=str, required=True,
                help='Relative path to the folder where the images will be written.')

    parser.add_argument('--label_save_path', type=str, required=True,
                help='Relative path to the folder where the labels will be written.')

    parser.add_argument('--train_list', type=str,
                help='Txt file containing image path of the train images.')

    parser.add_argument('--transforms', type=int, nargs='+', default=[3],
                help='Amount of transformations applied for each class. Should be informed by ascending order of the class IDs.')


    args = parser.parse_args()
    main(args.images_path, args.labels_path, args.img_size, args.img_save_path, args.label_save_path, args.train_list, args.transforms)