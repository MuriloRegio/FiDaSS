import shutil as sh
import cv2
import os

SHAPE = (960,480)
SHAPE = (1600,900)

last = '.last.txt'
listfile = '.last.dat'

old = 'Extracted/frames'
new = 'selected_frames/'

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

last_key = None
momentum = 0

while True:
	img = cv2.imread(os.path.join(old, frames[idx]))
	# img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
	cv2.imshow('img', cv2.resize(img, SHAPE))
	#print(frames[idx], end='\r')
	print('{1:06d}/{0:06d}'.format(amt, idx), end='\r')

	key = cv2.waitKey(0) & 0xff


	if key == ord('a'):
		idx = max(0, idx-1)
		mod = -1
	if key == ord('d'):
		idx = min(amt-1, idx+1)
		mod = 1
	if key == ord('q'):
		break

	if key == ord('s'):
		sh.copy(os.path.join(old,frames[idx]), os.path.join(new, frames[idx]))

	if key == last_key:
		momentum = min(momentum+1,100)
		if momentum >= 100: idx+=19*mod
		elif momentum >= 50: idx+=9*mod
		elif momentum >= 25: idx+=4*mod
	else:
		momentum = 0
	last_key = key


with open(last, 'w') as outfile:
	outfile.write(str(idx))
