import shutil as sh
import cv2
import os

last = '.visualizerfinal.txt'
listfile = '.visualizerfinal.dat'

old = './Final/selected_images'
lbl = './Final/selected_labels'

new = './wrongFinal'

disp_size = (768, 480)
#disp_size = (320, 160)

idx = 0
if os.path.exists(last):
	with open(last, 'r') as infile:
		idx = int(infile.read())

if not os.path.exists(new):
	os.mkdir(new)

import pickle
if os.path.exists(listfile):
	with open(listfile, 'rb') as infile:
		frames = pickle.load(infile)
else:
	frames = os.listdir(old)
	def order(x):
		if '(' in x:
			name, idx = x.split(' (')
			idx = int(idx.split(')')[0])
			return name, idx

		slots = x.split('_')
		slots[-1] = slots[-1].split('.')[0]
		if slots[-2].isdigit():
			key = int("{0:03d}{1:06d}".format((int(slots[-2])+1),(int(slots[-1])+1)))
			last = -2
		else:
			key = int(slots[-1])
			last = -1
		#key = key.split('.')[0]
		return '_'.join(slots[:last]), key

	frames = sorted(frames, key = order)
	with open(listfile, 'wb') as outfile:
		pickle.dump(frames, outfile)

amt = len(frames)




try:
	while True:
		img = cv2.imread(os.path.join(old, frames[idx]))

		annot = os.path.splitext(frames[idx])[0]
		annot = os.path.join(lbl, annot+'.txt')

		if not os.path.exists(annot):
			del frames[idx]
			continue

		img = cv2.resize(img, disp_size)
		with open(annot, 'r') as infile:
			annots = []
			for line in infile.read().split('\n'):
				if len(line) != 0:
					objClass, x, y, w, h = [float(i) for i in line.split(' ')]
					x = int(x * disp_size[0])
					y = int(y * disp_size[1])
					w = int(w * disp_size[0] / 2)
					h = int(h * disp_size[1] / 2)

					x1 = x-w
					x2 = x+w
					y1 = y-h
					y2 = y+h

					print(x1, y1, x2, y2, end=' ')

					cv2.rectangle(img, (x1, y1), (x2, y2), (0,255,0), 1)
					cv2.putText(img, str(int(objClass)), (x1, y1 +30), 0, 5e-3 * 150, (0,255,0),2)
					annots.append([x,y1-30])

			for x,y in annots:
				cv2.putText(img, str(len(annots)), (x,y), 0, 5, (0,255,0),10)
			cv2.putText(img, str(len(annots)), (int(disp_size[1]/2), 200), 0, 5, (0,255,0),2)



		print('{1:05d}/{0:05d}'.format(amt, idx), end='\r')
		cv2.imshow('img', img)

		key = cv2.waitKey(0) & 0xff


		if key == ord('a'):
			idx = max(0, idx-1)
		if key == ord('d'):
			idx = min(amt-1, idx+1)
		if key == ord('q'):
			break

		if key == ord('s'):
			sh.copy(os.path.join(old,frames[idx]), os.path.join(new, frames[idx]))
			idx = min(amt-1, idx+1)

finally:
	with open(last, 'w') as outfile:
		outfile.write(str(idx))
