# Imports
from src.crawler import crawl_and_download, merge_images, process_images
from src.utils import load_yaml_data

# Load config
config = load_yaml_data('crawl.yaml')

# Crawl images
if config['task'] == 'crawl':
    crawl_and_download(config=config)

# Process images
elif config['task'] == 'process':
    process_images(config=config)
    

# Merge a directory of existing images into selected
elif config['task'] == 'merge':
    merge_images(config=config)
