import cv2
import os

source_folder = './Originals/Negatives'
new_folder = './Extracted/Negatives'



if not os.path.exists(new_folder):
	os.mkdir(new_folder)


for root, _, files in os.walk(source_folder): ## looks for all files in the source folder
	for file in files:
		name, ext = os.path.splitext(file)
		if ext != '.mp4' and ext != '.webm':  ## ignores all files that aren't mp4 videos
			continue

		cap = cv2.VideoCapture(os.path.join(root,file))
		idx = 0

		while True:
			ret, frame = cap.read()
			cap.read() ## skips every second frame

			if not ret:
				break

			mkNew = lambda name, idx : '{0}_{1:06d}.jpg'.format(name, idx)

			new_file = os.path.join(new_folder, mkNew(name,idx))
			while os.path.exists(new_file):
				idx+=2
				new_file = os.path.join(new_folder, mkNew(name, idx))

			cv2.imwrite(new_file, frame)
			idx+= 2


os.system(f'notify-send "Frame extraction complete!"')
