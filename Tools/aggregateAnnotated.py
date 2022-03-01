import os
import shutil as sh

img_folders   = ['./Selected From Youtube', './united']
target_folder = './selected'
annots_folder = './boxes'

if not os.path.exists(target_folder):
	os.mkdir(target_folder)

relevat = [os.path.splitext(x)[0] for x in os.listdir(annots_folder)]

for folder in img_folders:
	for file in os.listdir(folder):
		name = os.path.splitext(file)[0]

		if name in relevat:
			sh.move(os.path.join(folder, file), os.path.join(target_folder, file))