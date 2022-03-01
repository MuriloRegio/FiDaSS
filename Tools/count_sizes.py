import os
from glob import glob

folder= 'Final/selected_labels'
#folder= 'Final/AUG_ANNOT'

files = glob(os.path.join(folder, '*.txt'))

#data = {x:0 for x in range(0,101,5)}
data = {x:0 for x in range(0,101)}
#format = lambda x : round(round(x*2,1)/2*100)
format = lambda x : round(x*100)

for file in files:
	with open(file, 'r') as infile:
		lines = infile.read().split('\n')
	
	for line in lines:
		if not len(line):
			continue
		_, _, _, w, h = line.split(' ')

		pctg = format(float(w)*float(h))
		#data[pctg]+= 1
		if not pctg:
			print(float(w)*float(h), file)

		if pctg not in data:
			print(float(w)*float(h), file)
			data[100] += 1
		else:
			data[pctg]+= 1

print (sum(data.values()))
print (data)
