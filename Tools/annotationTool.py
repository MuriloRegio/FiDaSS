import shutil as sh
import pickle
import cv2
import os


points = []
drawing = False
done = False
moving = False

disp_size = (960,480)

def draw(rect, x=None, y=None):
	image = img.copy()
	if rect:
		cv2.rectangle(image, points[0], points[1], (0, 255, 0), 2)
	else:
		cv2.line(image, (0, y), (disp_size[0], y), (100, 100, 100), 1)
		cv2.line(image, (x, 0), (x, disp_size[1]), (100, 100, 100), 1)

	cv2.imshow("img", image)

def drag(event, x, y, flags, param):

	global points, drawing, done, moving

	if event == cv2.EVENT_LBUTTONDOWN:
		points = [(x, y),(x, y)]
		drawing = True
		done = False

	if event == 0 and not done and not drawing: ## show perpendicular lines
		draw(False, x, y)

	if event == 0 and drawing: ## dragging the mouse
		points[-1] = (x, y)

	if event == 0 and moving: ## dragging the box
		w, h = [abs(points[0][i]-points[1][i]) for i in range(2)]
		hw = int(w/2)
		hh = int(h/2)

		tmp = [(x+hw, y+hh), (x-hw, y-hh)]

		points = tmp[:]
		draw(True)


	if event == 3: ## middle click (down) -> move the box
		moving = True

	if drawing:
		draw(True)

	if event == 6: ## middle click (up) -> move the box
		moving = False

	if event == cv2.EVENT_LBUTTONUP:
		drawing = False
		done = True



def convert(size, box):
	global points
	check_x = lambda x : max(0, min(size[0], x))
	check_y = lambda y : max(0, min(size[1], y))

	newbox = [
		check_x(box[0]),
		check_y(box[1]),
		check_x(box[2]),
		check_y(box[3]),
	]

	points = [(newbox[0], newbox[1]), (newbox[2], newbox[3])]
	draw(True)

	dw = 1./size[0]
	dh = 1./size[1]
	x = (newbox[0] + newbox[2])/2.0
	y = (newbox[1] + newbox[3])/2.0
	w = newbox[2] - newbox[0]
	h = newbox[3] - newbox[1]
	x = abs(x*dw)
	w = abs(w*dw)
	y = abs(y*dh)
	h = abs(h*dh)

	return [x,y,w,h]



def mkCheckpointFile(checkpointFile, idxFile, inputFolder, outputFolder):
	frames = os.listdir(inputFolder)
	if not os.path.exists(outputFolder):
		os.mkdir(outputFolder)

	def order(x):
		if '_' not in x:
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

		return '_'.join(slots[:last]), key

	frames = sorted(frames, key = order)
	with open(checkpointFile, 'wb') as outfile:
		pickle.dump(frames, outfile)

	with open(idxFile, 'w') as outfile:
		outfile.write('0')

	return 0, frames



def loadCheckpoint(checkpointFile, idxFile):
	with open(idxFile, 'r') as infile:
		idx = int(infile.read())

	with open(checkpointFile, 'rb') as infile:
		frames = pickle.load(infile)

	return idx, frames



def main(inputFolder, outputFolder, checkpointFile, idxFile):
	class_id  = 0

	global img, done, points

	if os.path.exists(idxFile) and os.path.exists(checkpointFile):
		foo  = loadCheckpoint
		args = ()
	else:
		foo  = mkCheckpointFile
		args = (inputFolder, outputFolder)

	idx, frames = foo(checkpointFile, idxFile, *args)

	cv2.namedWindow("img")
	cv2.setMouseCallback("img", drag)

	amt = len(frames)

	last_key = None
	momentum = 0

	boxes = []
	key   = None

	while True:
		img = cv2.imread(os.path.join(inputFolder, frames[idx]))
		img = cv2.resize(img, disp_size)

		if key != ord('s'):
			cv2.imshow('img', img)

		print('{1:06d}/{0:06d}\t\t{2}'.format(amt, idx+1, frames[idx]), end='\r')

		key = cv2.waitKey(0) & 0xff

		if key == ord('w'):
			if len(boxes):
				name = os.path.splitext(frames[idx])[0]
				with open(os.path.join(outputFolder, name)+'.txt', 'w') as outfile:
					outfile.write(
						'\n'.join(
							map(
								lambda x:
								' '.join(x),
								boxes
							)
						)
					)
				boxes = []
				
				# sh.copy(os.path.join(inputFolder,frames[idx]), os.path.join(outputFolder, frames[idx]))

		if key == ord('a'):
			boxes = []
			points = []
			done = False
			idx = max(0, idx-1)
			mod = -1
		if key == ord('d') or key == ord('w'):
			boxes = []
			points = []
			done = False
			idx = min(amt-1, idx+1)
			mod = 1
		if key == ord('q'):
			break

		if key == ord('r'):
			img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
			cv2.imwrite(os.path.join(inputFolder, frames[idx]), img)

		if key == ord('s') and done:
			done = False
			box = list(points[0])+list(points[1])
			print (box)
			boxes.append([str(x) for x in [class_id]+convert(disp_size, box)])
						##c, x, y, w, h
			points = []
			

		if key == last_key:
			momentum = min(momentum+1,100)
			if   momentum >= 100: idx+=19*mod
			elif momentum >=  50: idx+=9*mod
			elif momentum >=  25: idx+=4*mod
		else:
			momentum = 0
		last_key = key

	print()
	with open(idxFile, 'w') as outfile:
		outfile.write(str(idx))


if __name__ == "__main__":
	import argparse

	parser = argparse.ArgumentParser(description="Tool for annotating images with the specified labels."
		"\n\nUsage:"
		"\n\tLeft click + Drag -> Select area of interest"
		"\n\tMiddle click + Drag -> Move the bounding box"
		"\n\t's' key -> Save current bounding box"
		"\n\t'w' key -> Write all saved bounding boxes for current image"
		"\n\t'r' key -> Inverts RGB to BGR color space"
		"\n\t'a' and 'd' keys -> Move to previous/next image"
		"\n\t'q' key -> leave application"
		"\nMoving to a new image erases all saved bounding boxes",
		formatter_class=argparse.RawTextHelpFormatter
	)

	parser.add_argument('--input_path', type=str,
	            help='Relative path to the folder containing the images.')


	parser.add_argument('--output_path', type=str,
	            help='Relative path to the folder where the labels will be written.')


	parser.add_argument('--idx', type=str, default='.idx.ckpt',
	            help='File to write the last file analyzed, for continued usage after closing the application.')


	parser.add_argument('--checkpoint', type=str, default='.checkpoint.ckpt',
	            help='File to write the checkpoint list, for continued usage after closing the application.')


	args = parser.parse_args()
	main(args.input_path, args.output_path, args.checkpoint, args.idx)