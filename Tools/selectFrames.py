import shutil as sh
import cv2
import os


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

	if os.path.exists(idxFile) and os.path.exists(checkpointFile):
		foo  = loadCheckpoint
		args = ()
	else:
		foo  = mkCheckpointFile
		args = (inputFolder, outputFolder)

	idx, frames = foo(checkpointFile, idxFile, *args)

	amt = len(frames)

	last_key = None
	momentum = 0

	while True:
		img = cv2.imread(os.path.join(inputFolder, frames[idx]))
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
			sh.copy(os.path.join(inputFolder, frames[idx]), os.path.join(outputFolder, frames[idx]))

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

	parser = argparse.ArgumentParser(description="TODO")

	parser.add_argument('input', type=str, required=True,
	            help='TODO.')


	parser.add_argument('output', type=str, required=True,
	            help='TODO.')


	parser.add_argument('idx', type=str,
	            help='TODO.')


	parser.add_argument('checkpoint', type=str,
	            help='TODO.')


	args = parser.parse_args()
	main(args.input, args.output, args.checkpoint, args.idx)