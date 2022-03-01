import os
from glob import glob

folder= 'Final/selected_labels'
folder= 'Final/AUG_ANNOT'

files = glob(os.path.join(folder, '*.txt'))

data = {}

for file in files:
	with open(file, 'r') as infile:
		amt = len(infile.readlines())
	
	if amt not in data:
		data[amt] = 0
	data[amt]+= 1

print (data)
