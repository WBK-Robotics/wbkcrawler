import hashlib
import json
import os
import shutil
import time

import cv2
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from src.utils import compute_hash
from webdriver_manager.chrome import ChromeDriverManager


# This loads a image by its path and offers the possibility to choose coordinates with mous clicks 
def user_interface(path_to_image, fits):

    # Read image
    img = cv2.imread(path_to_image, 1)
    
    try:
        # Check if image resolution is smaller than min_res
        if not fits:
            # Delete image
            action = 'del'
        # If resolution is okay
        else:
            # Show image in window
            cv2.imshow('image', img)   
            # Wait for a key to be pressed to exit
            k= cv2.waitKey(0)

            if k == ord('d'):
                print('Image removed from dataset.')
                action = 'del'
            elif k == ord('a'):
                print('Image added to dataset.')
                action = 'add'   
            else:
                action = 'save'
            
            # close the window
            cv2.destroyAllWindows()
    except:
        action = 'del'
    # Return action for image
    return action


def process_images(config):
    
    # Create UrlHandler
    uh = UrlHandler(config)

    # Get all candidates
    candidates = os.listdir(uh.path_candidates)

    # Process all candidate images
    for candidate in candidates:
        
        # Calculate hash of the file
        try:
            file_hash, fits = compute_hash(os.path.join(uh.path_candidates, candidate), min_res=uh.min_res)
        except:
            print('Could not calculate hash for {}!'.format(candidate))
            file_hash = 1
            fits = None
        
        # If file is not already processed and in hash list of json)
        if not file_hash in uh.url_data['hash_list'] and fits:
            
            # Get action from user for image
            action = user_interface(os.path.join(uh.path_candidates, candidate), fits=fits)

            # If action is 'add' add image
            if action == 'add':
                # Move candidate to selected
                uh.select_candidate(candidate)
                os.rename(os.path.join(uh.path_candidates, candidate), os.path.join(uh.path_selected, candidate))
            # If action
            elif action == 'del':
                uh.delete_candidate(candidate)
                os.remove(os.path.join(uh.path_candidates, candidate))
            else:
                uh.save()
                print('Interface stopped, you will start from this image again.')
                break
            
            # Only add to hash list, if user saw a picture with correct resolution
            uh.url_data['hash_list'].append(file_hash)
        # If in hash list, it's a duplicate
        else:
            # Delete image
            uh.delete_candidate(candidate)
            # Remove from json
            os.remove(os.path.join(uh.path_candidates, candidate))
            # Save json
            uh.save()
            # Print status
            print('Removed duplicate.')
    else:
        # Save json
        uh.save()
        print('Saved. No candidates left! You need to search by keyword/image first.')

# load/write/save url data
class UrlHandler:
    def __init__(self, config):
        
        # Store main hyperparameters
        self.path_url_handler_json = os.path.join(config['crawler']['path_dataset'], 'url_data.json')
        self.path_dataset = config['crawler']['path_dataset']
        self.path_candidates = os.path.join(self.path_dataset, 'candidates')
        self.path_selected = os.path.join(self.path_dataset, 'selected')
        self.min_res = config['crawler']['min_res']

        # If we want to create a new dataset
        if not os.path.exists(self.path_url_handler_json):
            if not os.path.exists(self.path_dataset):
                # Create dataset directory
                os.makedirs(self.path_dataset)
                # Create "candidates" and "selected" directory
                os.makedirs(os.path.join(self.path_dataset, 'candidates'))
                os.makedirs(os.path.join(self.path_dataset, 'selected'))

            # Initialize dictionary
            self.url_data = {'id':  0,
                             'keywords': [],
                             'num_selected': 0,
                             'num_candidates': 0,   
                             'candidates':  {},
                             'example_candidates':  {},
                             'selected': {},
                             'search_examples': [],
                             'hash_list':   []}

        # Reload existing dataset
        else:
            # Read json file with url data
            with open(self.path_url_handler_json, 'r') as json_file:
                # Reading from json file
                self.url_data = json.load(json_file)

    # Save actual url_data
    def save(self):
        self.url_data['num_candidates'] = len(self.url_data['candidates'])
        self.url_data['num_selected'] = len(self.url_data['selected'])

        with open(self.path_url_handler_json, "w") as outfile:
            outfile.write(json.dumps(self.url_data, indent=4))
    
    # Add candidate image
    def add_candidate(self, key, url, ex_url):
        self.url_data['id'] += 1
        self.url_data['candidates'][key] = url
        self.url_data['example_candidates'][key] = ex_url
        
    # Merge an image from another directory
    def merge_image(self, key, hash):
        self.url_data['selected'][key] = 'merged'
        self.url_data['hash_list'].append(hash)
        self.url_data['id'] += 1

    # Select candidate
    def select_candidate(self, key):
        self.url_data['selected'][key] = self.url_data['candidates'].pop(key)
        self.url_data['search_examples'].append(self.url_data['example_candidates'].pop(key))

    # Delete candidate
    def delete_candidate(self, key):
        self.url_data['candidates'].pop(key)
        self.url_data['example_candidates'].pop(key)

    # Get actual key for actual id
    def get_key(self):
        return 'image_{}.jpg'.format(str(self.url_data['id']).zfill(6))

    def add_keyword(self, keyword):
        self.url_data['keywords'].append(keyword)


def get_images_from_google(delay, limit, keyword, url):
    def scroll_down(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(delay)

    wd = webdriver.Chrome(ChromeDriverManager().install())
    # wd = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    
    if url is None:
    #if True:    
        search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"

        # load the page
        wd.get(search_url.format(q=keyword))

    else:

        search_url = url
        wd.get(search_url)


    # Skip cookies
    time.sleep(delay)
    # wd.find_element(By.CLASS_NAME, "Nc7WLe").click()
    wd.find_element(By.CLASS_NAME,
                    "VfPpkd-LgbsSe.VfPpkd-LgbsSe-OWXEXe-k8QpJ.VfPpkd-LgbsSe-OWXEXe-dgl2Hf.nCP5yc.AjY5Oe.DuMIQc.LQeN7.XWZjwc").click()

    time.sleep(delay)

    image_urls = set()
    image_urls = []
    search_examples_urls = []
    skips = 0
    breaker = 0
    while len(image_urls) + skips < limit:
        scroll_down(wd)
        thumbnails = wd.find_elements(By.CLASS_NAME, "rg_i.Q4LuWd") # 2zEKz   Q4LuWd
        number_of_images_before = len(image_urls)
        for img in thumbnails[len(image_urls) + skips:limit]:
            try:
                img.click()
                time.sleep(delay)
            except:
                continue

            images = wd.find_elements(By.CLASS_NAME, "sFlh5c.pT0Scc.iPVvYb") #n3VNCb
            print(len(images))
            for image in images:
                if image.get_attribute('src') in image_urls:
                    limit += 1
                    skips += 1
                    break

                if image.get_attribute('src') and 'http' in image.get_attribute('src'):
                    #image_urls.add(image.get_attribute('src'))
                    #search_examples_urls.append(wd.find_element(By.CLASS_NAME, "MkRxHd.MIdC8d.jwwPNd").get_attribute('href'))
                    ##print(f"Found {len(image_urls)}")
                    try:
                        search_examples_urls.append(wd.find_element(By.CLASS_NAME, "T38yZ.MIdC8d.jwwPNd").get_attribute('href')) #MkRxHd.MIdC8d.jwwPNd
                        # search_examples_urls.append(image.get_attribute('src'))
                        image_urls.append(image.get_attribute('src'))
                    except:
                        continue
        number_of_images_after = len(image_urls)
        if number_of_images_before == number_of_images_after:
            breaker +=1
            if breaker > 4:
                print(f"Found {len(image_urls)} images. Since we got no new results, stop with this search example.")
                break
    return image_urls, search_examples_urls


def persist_image(url:str, uh, ex_url):
    try:
        image_content = requests.get(url, timeout=20).content

    except Exception as e:
        print(f"ERROR - Could not download {url} - {e}")

    try:
        f = open(os.path.join(uh.path_candidates, uh.get_key()), 'wb')
        f.write(image_content)
        f.close()
        uh.add_candidate(url=url, key=uh.get_key(), ex_url=ex_url)
        #print(f"SUCCESS - saved {url} - as {folder_path}")
    except Exception as e:
        print(f"ERROR - Could not save {url} - {e}")

    return uh


def crawl_and_download(config):

    # Create UrHandler
    uh = UrlHandler(config)

    # Search by keyword
    if config['crawler']['search_by'] == 'keyword':

        for word in config['crawler']['keywords']:
            if not word in uh.url_data['keywords']:
                print('Search by keyword \"{}\".'.format(word))
                urls, example_urls = get_images_from_google(delay = config['crawler']['delay'], limit=config['crawler']['limit'], keyword=word, url=None)
                for i, url in enumerate(urls):
                    uh = persist_image(uh=uh, url=url, ex_url=example_urls[i])
                    uh.save()
                uh.add_keyword(word)
            else:
                print('Keyword already in search history -> skip  keyword \"{}\".'.format(word))
        
        uh.save()
    
    # Search by image
    elif config['crawler']['search_by'] == 'image' and len(uh.url_data['search_examples'])>0:
        
        for index, image_url in enumerate(uh.url_data['search_examples']):
            print('Search by image \"{}\".'.format(image_url))
            urls, example_urls = get_images_from_google(delay = config['crawler']['delay'], limit=config['crawler']['limit'], keyword=None, url=image_url)
            for i, url in enumerate(urls):
                uh = persist_image(uh=uh, url=url, ex_url=example_urls[i])
                uh.save()
            uh.url_data['search_examples'].pop(index)
            uh.save()

        uh.save()

    elif config['crawler']['search_by'] == 'image' and len(uh.url_data['search_examples']) == 0:
        print('No selected images to search by left! You have to process candidates first.')


def create_hash_dict_for_dir(path_to_dir, uh):
    images = os.listdir(path_to_dir)
    # Create a dictionary of image hash
    dict_images = {}
    for image in images:
        file_hash, fits = compute_hash(os.path.join(path_to_dir, image), min_res=uh.min_res)
        if fits:
            dict_images[image] = file_hash
            
    return dict_images


def merge_images(config):
    # Create UrHandler
    uh = UrlHandler(config)
    # Path to files to merge
    path_to_images_to_merge = config['crawler']['path_images_to_merge']
    path_to_selected = uh.path_selected
    # Get dictionaries
    dict_merge = create_hash_dict_for_dir(path_to_images_to_merge, uh)
    dict_selected = create_hash_dict_for_dir(path_to_selected, uh)
    dict_selected_rev = {v: k for k, v in dict_selected.items()}
    
    for m_key, m_value in dict_merge.items():
        # If hash already exists, overwrite image by new image
        if m_value in dict_selected.values():
            # copy the file to the destination directory and overwrite if necessary
            shutil.copy2(os.path.join(path_to_images_to_merge, m_key), os.path.join(uh.path_selected, dict_selected_rev[m_value]))
        # Else add image to dataset
        else:
            # Get a new image name for file to merge
            key = uh.get_key()
            # Copy the image into selected
            shutil.copy2(os.path.join(path_to_images_to_merge, m_key), os.path.join(uh.path_selected, key))
            # Add metadata and update json
            uh.merge_image(key=key, hash=m_value)
            # Save json
            uh.save()

    
            
            
            

    
    