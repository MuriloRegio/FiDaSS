import os
import shutil as sh

def main(img_folders, annots_folder, target_folder):
	if not os.path.exists(target_folder):
		os.mkdir(target_folder)

	relevat = [os.path.splitext(x)[0] for x in os.listdir(annots_folder)]

	for folder in img_folders:
		for file in os.listdir(folder):
			name = os.path.splitext(file)[0]

			if name in relevat:
				sh.move(os.path.join(folder, file), os.path.join(target_folder, file))


if __name__ == '__main__':
	import argparse

	parser = argparse.ArgumentParser(description="Selects only the annotated frames within a larger collection and moves them to a new folder.")

	parser.add_argument('--img_folders', type=str, nargs="+", required=True,
	            help='Relative path to the folders containing the frames extracted.')

	parser.add_argument('--annots_folder', type=str, required=True,
	            help='Relative path to the folder containing the annotations of the frames of interest.')

	parser.add_argument('--target_folder', type=str, required=True,
	            help='Relative path to the folder where all the annotated frames will be moved to.')

	args = parser.parse_args()
	main(args.img_folders, args.annots_folder, args.target_folder)