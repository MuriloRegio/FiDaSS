import os
from glob import glob
import random
random.seed(42)

folder = 'Final/selected_labels'
folder = 'Final/negatives'
isNeg = True



def mksplits(folder, isNeg):
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

	
	split_size = int(.15*total)
	sets = {"test":[], "val":[], "train":[]}


	test_left = split_size
	val_left = split_size
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


mksplits(folder, isNeg)