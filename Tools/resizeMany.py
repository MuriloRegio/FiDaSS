import cv2
import os

def main(source, dims):
	net_shape = tuple(dims)
	net_shape = (net_shape[0],net_shape[0]) if len(net_shape) == 1 else net_shape[:2]

	for file in os.listdir(source):
		fpath = os.path.join(source, file)

		img = cv2.imread(fpath)
		img = cv2.resize(img, net_shape)

		cv2.imwrite(fpath, img)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Resizes a set of images to a standardized size.")

    parser.add_argument('--path', type=str, required=True,
                help='Relative path to the folder containing the images to be resized.')

    parser.add_argument('--img_size', type=int, nargs='+', default=[768,480],
                help='Image dimensions for them to be resized to.')


    args = parser.parse_args()
    main(args.path, args.img_size)