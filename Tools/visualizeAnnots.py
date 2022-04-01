import shutil as sh
import pickle
import cv2
import os

# last = '.visualizerfinal.txt'
# listfile = '.visualizerfinal.dat'

# old = './Final/selected_images'
# lbl = './Final/selected_labels'

# new = './wrongFinal'

# disp_size = (768, 480)

def mkCheckpointFile(checkpointFile, idxFile, inputFolder):
	frames = os.listdir(inputFolder)

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



def main(inputFolder, annotsFolder, checkpointFile, idxFile):
	disp_size = (960,480)

	if os.path.exists(idxFile) and os.path.exists(checkpointFile):
		foo  = loadCheckpoint
		args = ()
	else:
		foo  = mkCheckpointFile
		args = (inputFolder, )

	idx, frames = foo(checkpointFile, idxFile, *args)

	amt = len(frames)

	try:
		while True:
			img = cv2.imread(os.path.join(inputFolder, frames[idx]))

			annot = os.path.splitext(frames[idx])[0]
			annot = os.path.join(annotsFolder, annot+'.txt')

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

	finally:
		with open(last, 'w') as outfile:
			outfile.write(str(idx))



if __name__ == "__main__":
	import argparse

	parser = argparse.ArgumentParser(description="TODO")

	parser.add_argument('--images', type=str, required=True,
	            help='Relative path to the folder containing the images.')


	parser.add_argument('--labels', type=str, required=True,
	            help='TODO.')


	# parser.add_argument('--idx', type=str,
	#             help='TODO.')


	# parser.add_argument('--checkpoint', type=str,
	#             help='TODO.')

	# parser.add_argument('--input_path', type=str, required=True,
	#             help='Relative path to the folder containing the images.')


	# parser.add_argument('--output_path', type=str, required=True,
	#             help='Relative path to the folder where the labels will be written.')


	parser.add_argument('--idx', type=str, default='.idx.ckpt',
	            help='File to write the last file analyzed, for continued usage after closing the application.')


	parser.add_argument('--checkpoint', type=str, default='.checkpoint.ckpt',
	            help='File to write the checkpoint list, for continued usage after closing the application.')



	args = parser.parse_args()
	main(args.images, args.labels, args.checkpoint, args.idx)