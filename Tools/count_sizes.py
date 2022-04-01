from glob import glob
import json
import os

data = {x:0 for x in range(0,101)}
format = lambda x : round(x*100)

def main(folder):
	files = glob(os.path.join(folder, '*.txt'))
	
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

	print (json.dumps(data, indent=4))


if __name__ == '__main__':
	import argparse

	parser = argparse.ArgumentParser(description="Prints a list of how much of the image each object occupies.")

	parser.add_argument('--path', type=str, required=True,
	            help='Relative path to the folder containing the labels.')


	args = parser.parse_args()
	main(args.path)