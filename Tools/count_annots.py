import os
import json
from glob import globs

def main(folder):
	files = glob(os.path.join(folder, '*.txt'))

	data = {}

	for file in files:
		with open(file, 'r') as infile:
			amt = len(infile.readlines())
		
		if amt not in data:
			data[amt] = 0
		data[amt]+= 1

	print (json.dumps(data, indent=4))

if __name__ == '__main__':
	import argparse

	parser = argparse.ArgumentParser(description="Prints a list of numbers of objects per image.")

	parser.add_argument('path', type=str,
	            help='Relative path to the folder containing labels.')

	args = parser.parse_args()
	main(args.path)