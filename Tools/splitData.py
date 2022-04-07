import os
from glob import glob
import random
random.seed(42)

# folder = 'Final/selected_labels'
# folder = 'Final/negatives'
# isNeg = True



def main(folder, isNeg, test_pct, val_pct):
	assert test_pct+val_pct <= 100

	test_pct  = test_pct/100
	val_pct   = val_pct/100

	if isNeg:
		files = glob(os.path.join(folder, '*'))
		key = '_neg'
	else:
		files = glob(os.path.join(folder, '*.txt'))
		key = ''

	random.shuffle(files)

	to_ID = lambda x : (' '.join(x.split(' ')[:-1]) if '_' not in x else '_'.join(x.split('_')[:-1]))
	vIDs = {to_ID(os.path.basename(x)) for x in files}


	data  = {v:0 for v in vIDs}
	names  = {v:[] for v in vIDs}
	total = 0

	for file in files:
		if isNeg:
			amt = 1
		else:
			with open(file, 'r') as infile:
				amt = len(infile.readlines())
		
		fname = os.path.basename(file)
		ID = to_ID(fname)

		data[ID] += amt
		names[ID].append(fname)
		total += amt

	
	sets = {"test":[], "val":[], "train":[]}


	test_left = int(total*test_pct)
	val_left  = int(total*val_pct)
	train_size = 0


	order = sorted(data.items(), key = lambda x : x[1])

	for k,v in order:
		if test_left > 0:
			split = 'test'
			test_left -= v

		elif val_left > 0:
			split = 'val'
			val_left -= v

		else:
			split = 'train'
			train_size += v

		sets[split].append(k)

	for split in ["train", "test", "val"]:
		filelist = []

		for ID in sets[split]:
			filelist += names[ID]

		random.shuffle(filelist)
		with open(f'new{key}_{split}.txt', 'w') as outfile:
			outfile.write(
				'\n'.join(
					map(
						lambda x : 
							os.path.join('data', 'obj', x.replace('.txt','.jpg'))
						, 
						filelist
					)
				)
			)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Divides a collection of frames into Train/Test/Validation sets. The tool guarantees that frames of the same video are on the same subset.")

    parser.add_argument('--input_folder', type=str, required=True,
                help='Relative path to the folder with the annotations of the dataset, or the images in case of images with no annotations.')


    parser.add_argument('--isNeg', action='store_true',
                help='In case the path informed does not contain annotations.')


    parser.add_argument('--test_pct', type=float, default=15,
                help='Percentage of the dataset that should be dedicated for testing.')

    parser.add_argument('--val_pct', type=float, default=15,
                help='Percentage of the dataset that should be dedicated for validation.')


    args = parser.parse_args()
    main(args.input_folder, args.isNeg, test_pct, val_pct)