import os
from PIL import Image


def clean_images(directory, min_size=10):
	i = 0
	print(f'Deleting images which cannot be loaded as images')
	print('-'*40)
	for r, dirs, files in os.walk(directory):
		for fp in files:
			f = os.path.join(r,fp)
			if f.split('.')[-1].lower() == 'jpg':
				try:
					im = Image.open(f)
					im.verify() #I perform also verify, don't know if he sees other types o defects
					width, height = im.size
					im.close() #reload is necessary in my case
					# Delete if too small
					if width < min_size or height < min_size:
						print(f, flush=True)
						os.remove(f)
						i += 1
				except IOError:
					# filename not an image fileimport os
					print(f, flush=True)
					os.remove(f)
					i += 1
	print('-'*40)
	print(f'Deleted {i} images')
	print('-'*40)


if __name__ == "__main__":
	clean_images('data')
