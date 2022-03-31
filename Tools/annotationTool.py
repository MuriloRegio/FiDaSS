import shutil as sh
import pickle
import cv2
import os


points = []
drawing = False
done = False
moving = False


def drag(event, x, y, flags, param):
	image = img.copy()
	def draw(rect):
		if rect:
			cv2.rectangle(image, points[0], points[1], (0, 255, 0), 2)
		else:
			cv2.line(image, (0, y), (disp_size[0], y), (100, 100, 100), 1)
			cv2.line(image, (x, 0), (x, disp_size[1]), (100, 100, 100), 1)

		cv2.imshow("img", image)

	global points, drawing, done, moving

	if event == cv2.EVENT_LBUTTONDOWN:
		points = [(x, y),(x, y)]
		drawing = True
		done = False

	if event == 0 and not done and not drawing: ## show perpendicular lines
		draw(False)

	if event == 0 and drawing: ## dragging the mouse
		points[-1] = (x, y)

	if event == 0 and moving: ## dragging the box
		w, h = [abs(points[0][i]-points[1][i]) for i in range(2)]
		hw = int(w/2)
		hh = int(h/2)

		check = [
			(
				min(img.shape[1], x+hw),
				min(img.shape[0], y+hh)
			),
			(
				max(0, x-hw),
				max(0, y-hh)
			)
		]
		tmp = [(x+hw, y+hh), (x-hw, y-hh)]

		if tmp == check:
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
	dw = 1./size[0]
	dh = 1./size[1]
	x = (box[0] + box[2])/2.0
	y = (box[1] + box[3])/2.0
	w = box[2] - box[0]
	h = box[3] - box[1]
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
	disp_size = (960,480)
	class_id  = 1 

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

	while True:
		img = cv2.imread(os.path.join(inputFolder, frames[idx]))
		# img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
		img = cv2.resize(img, disp_size)
		cv2.imshow('img', img)
		#print(frames[idx], end='\r')
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
			points = []
			print (box)
			boxes.append([str(x) for x in [class_id]+convert(disp_size, box)])
						##c, x, y, w, h
			

			sh.copy(os.path.join(inputFolder,frames[idx]), os.path.join(outputFolder, frames[idx]))

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

	parser = argparse.ArgumentParser(description="Tool for annotating images with the specified labels.")

	parser.add_argument('input_path', type=str,
	            help='Relative path to the folder containing the images.')


	parser.add_argument('output_path', type=str,
	            help='Relative path to the folder where the labels will be written.')


	parser.add_argument('idx', type=str, default='.idx.ckpt',
	            help='File to write the last file analyzed, for continued usage after closing the application.')


	parser.add_argument('checkpoint', type=str, default='.checkpoint.ckpt',
	            help='File to write the checkpoint list, for continued usage after closing the application.')


	args = parser.parse_args()
	main(args.input, args.output, args.checkpoint, args.idx)