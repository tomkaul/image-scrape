
import json
import os, re, sys
import requests
import time
from bs4 import BeautifulSoup
from io import StringIO
from PIL import Image

# Provide a User-Agent which is not rejected
UA = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
IMAGE_BASEDIR = 'images/'
# Type of the images you want to download
IMAGE_TYPE = 'svampe'
# Which url to scape?
URL = "http://www.svampeguide.dk/alle-svampe"
# List holding "bad servers" which are not responding
BAD_SERVERS = []

def get_soup(url):
	"""Lookup URL and create a soup"""
	r = requests.get(url, headers={"User-Agent": UA})
	if r.status_code != 200:
		print("Error reading url: " + url)
	soup = BeautifulSoup(r.content, features="html5lib")
	return soup

def pline():
	print('-'*40, flush=True)

def get_image_info(url, images_json):
	"""Get the image descriptions from URL"""
	pline()
	soup = get_soup(url)
	# Get base url
	burl = '/'.join(url.split(sep='/')[:-1])
	imgs = {}
	divs = soup.find_all("div")
	i = 0
	for div in divs:
		img = div.find("img")
		if img:
			href = div.find("a")["href"].strip()
			# Check for empty name
			if len(href) > 1:
				i += 1
				# Get clean name
				txt = div.find("span", {"class": "listtext"}).text
				# Remove thumbnails from the path
				img_path = img['src'].replace('gallery-thumbnails/', '')
				# Extract the latin name from filename, keep in a list
				latin_list = img_path.split(sep='/')[-1].split(sep='_')[-1].split('-')[:-1]
				# Build dict
				print(href, flush=True)
				imgs[href] = {"txt": txt, 
					"img": '/'.join([burl, img_path]), 
					"href": '/'.join([burl, href]),
					"latin": ' '.join(latin_list),
					"search": "https://www.google.dk/search?tbm=isch&q=" + '+'.join(latin_list)}

	# Get images for the different categories
	pline()
	j = 0
	for key, val in imgs.items():
		# Get the google page
		print(key, end=':')
		gs = get_soup(val['search'])
		time.sleep(0.1)
		img_lst = re.findall('http[^"]+\.(?:jpg|JPG)', gs.text)
		# Run through the list and download images
		i = 0
		val['images'] = {}
		for url in img_lst:
			# Give them simple names so the files are sorted in prioritized order
			fname = f"{key}{i}.jpg"
			val['images'][fname] = url 
			i += 1
			j += 1
		print(f'Found {i} images', flush=True)
	# Save the image overview
	with open(images_json, 'w') as outfile:
		json.dump(imgs, outfile, ensure_ascii=False, indent=4)
	pline()
	print(f'Found {j} images in {len(imgs)} entries')
	return imgs


def get_servername(url):
	return '/'.join(url.split('/')[:3])


def download_image(url, file):
	# Check if server is OK, else skip
	if get_servername(url) in BAD_SERVERS:
		print("Skipping server not responding: " + get_servername(url))
		return False
	ok = False

	# Has file already been created?
	if os.path.isfile(file):
		# Skip if file is non-zero
		if os.path.getsize(file) > 1000:
			# print("Already exists, skipping: " + file)
			return False
		else:
			# Delete empty file
			print("========> Removing empty file: " + file)
			os.remove(file)
			time.sleep(0.1)
			# sys.exit()
	print("Downloading: " + url, flush=True)
	try:
		with open(file, 'wb') as f:
			r = requests.get(url, stream=True, timeout=5)
			for block in r.iter_content(1024):
				if not block:
					break
				f.write(block)
		# r = requests.get(url)
		# i = Image.open(StringIO(r.content))
		# i.save(file)
		ok = True
	# except IOError:   #If there is any IOError
	# 	print("=========> IOError on image: " + url)
	# except HTTPError as e:  #If there is any HTTPError
	# 	print("=========> HTTPError: " + url)
	except Exception as e:
		# Clean up
		if os.path.exists(file):
			os.remove(file)
		print("=========> Error downloading: " + url)
		print(str(e))
		# Add server to BAD_SERVERS
		BAD_SERVERS.append(get_servername(url))

	time.sleep(0.1)
	return ok


def download_images(name, images_json, base_dir="images/test"):
	pline()
	print('Opening file: ' + images_json)
	pline()
	with open(images_json, 'r') as fp:
		imgs = json.load(fp)
	
	# create directories
	i = 0
	for key, val in imgs.items():
		print(key, flush=True)
		idir  = '/'.join([base_dir, key])
		if not os.path.exists(idir):	
			try:
				os.makedirs(idir)
			except OSError as e:
				print(str(e))
				raise e
		# Run through the list and download images
		for fname, url in val['images'].items():
			file = '/'.join([idir, fname])
			if download_image(url, file):
				i += 1
	pline()
	print(f'Downloaded {i} images')


def web_scrape(image_type=IMAGE_TYPE, url=URL):
	# Make sure dir has been created
	image_dir = IMAGE_BASEDIR + image_type
	if not os.path.exists(image_dir):
		os.makedirs(image_dir)

	# Get the image info from source URL
	images_json = f"{'/'.join([image_dir, image_type])}.json"
	if not os.path.exists(images_json):
		get_image_info(url, images_json)	
	# Download the files
	download_images(image_type, images_json, base_dir = image_dir)


if __name__ == "__main__":
	############## Main Program ############
	pline()
	t0 = time.time()   #start the timer
	get_image_info(URL, './images/svampe/svampe.json')
	# web_scrape()

	# Calculating time
	pline()
	t1 = time.time()
	total_time = t1 - t0	#Calculating the total time required to crawl
	print(f"Total time taken: {str(total_time)}s")

