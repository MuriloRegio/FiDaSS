import cv2
import os

def main(source_folder, new_folder, skip, extensions):
	if not os.path.exists(new_folder):
		os.mkdir(new_folder)

	notVideo = lambda EXT: all([EXT != e for e in extensions])
	step = skip + 1

	for root, _, files in os.walk(source_folder): ## looks for all files in the source folder
		for file in files:
			name, ext = os.path.splitext(file)
			if notVideo(ext[1:]): ## ignores all files that aren't videos
				continue

			cap = cv2.VideoCapture(os.path.join(root,file))
			idx = 0

			while True:
				ret, frame = cap.read()
				for _ in range(skip):
					cap.read() ## skips every few frames

				if not ret:
					break

				mkNew = lambda name, idx : '{0}_{1:06d}.jpg'.format(name, idx)

				new_file = os.path.join(new_folder, mkNew(name,idx))
				while os.path.exists(new_file):
					idx+=step
					new_file = os.path.join(new_folder, mkNew(name, idx))

				cv2.imwrite(new_file, frame)
				idx+= step


if __name__ == '__main__':
	import argparse

	parser = argparse.ArgumentParser(description="Converts a set of videos to frames.\nSearches all sub-folders within the folder specified.")

	parser.add_argument('--videos_folder', type=str, required=True,
	            help='Relative path to the folder containing the videos.')


	parser.add_argument('--frames_path', type=str, required=True,
	            help='Relative path to the folder where the frames will be saved.')


	parser.add_argument('--skip', type=int, default=1,
	            help='Number of frames to skip before saving each time.')

	parser.add_argument('--extensions', type=str, nargs='+', default=['webm', 'mp4'],
	            help='Video extensions to look for within the folder specified.')

	args = parser.parse_args()
	main(args.videos_folder, args.frames_path, args.skip, args.extensions)
	
	os.system(f'notify-send "Frame extraction complete!"')