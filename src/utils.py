import yaml
import os
import errno
import hashlib
import os
import cv2


def is_path_file(string):
    if os.path.isfile(string):
        return string
    else:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), string)

def load_yaml_data(path):
    if is_path_file(path):
        with open(path) as f_tmp:
            return yaml.load(f_tmp, Loader=yaml.FullLoader)


def compute_hash(path, min_res = (250, 250)):

    # Open the image file and calculate its perceptual hash
    image = cv2.imread(path)
    
    # Get resolution
    height, width, _ = image.shape
    
    # Check image resolution
    fits = not height < min_res[0] or width < min_res[1]

    image = cv2.resize(image, (8,8))
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.bitwise_not(image)

    # Compute hash
    image_hash = str(image.flatten())

    return image_hash, fits
