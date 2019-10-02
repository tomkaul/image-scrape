
import json
import os
import requests
from bs4 import BeautifulSoup

# Provide a User-Agent which is not rejected
UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/69.0.3497.105 Mobile/15E148 Safari/605.1"
IMAGES_JSON = 'images.json'

def get_soup(url):
	"""Lookup URL and create a soup"""
	r = requests.get(url, headers={"User-Agent": UA})
	if r.status_code != 200:
		print("Error reading url: " + url)
	soup = BeautifulSoup(r.content, features="html5lib")
	return soup


def get_image_info(url):
	"""Get the image descriptions from URL"""
	soup = get_soup(url)
	# Get base url
	burl = '/'.join(url.split(sep='/')[:-1])
	imgs = {}
	divs = soup.find_all("div")
	for div in divs:
		img = div.find("img")
		if img:
			href = div.find("a")["href"].strip()
			# Check for empty name
			if len(href) > 1:
				# Get clean name
				txt = div.find("span", {"class": "listtext"}).text
				# Remove thumbnails from the path
				img_path = img['src'].replace('gallery-thumbnails/', '')
				# Extract the latin name from filename, keep in a list
				latin_list = img_path.split(sep='/')[-1].split(sep='_')[-1].split('-')[:-1]
				# Build dict
				imgs[href] = {"txt": txt, 
					"img": '/'.join([burl, img_path]), 
					"href": '/'.join([burl, href]),
					"latin": ' '.join(latin_list),
					"search": "https://www.google.dk/search?tbm=isch&q=" + '+'.join(latin_list)}
	with open(IMAGES_JSON, 'w') as outfile:
		json.dump(imgs, outfile, ensure_ascii=False, indent=4)

	return imgs


def download_images(name):
	with open(IMAGES_JSON, 'r') as fp:
		imgs = json.load(fp)
	
	for key, val in imgs.items():
		# create 

if __name__ == "__main__":
    url = "http://www.svampeguide.dk/alle-svampe"
    # get_image_info(url)	
    download_images("svampe")
