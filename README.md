# BatteryDisassemblyDataset

[![Python version](https://img.shields.io/badge/python-3.9-green.svg)](https://www.python.org/downloads/)
[![Roboflow](https://img.shields.io/badge/Roboflow-blue)](https://roboflow.com/)


With this repository you can build your own image dataset. It offers the possibility to pass search terms to Google Images and automatically download a certain number of images. These images are suggested to the user and he can decide which ones should be included in the dataset and which not. In addition to search terms, already accepted images from the dataset can also serve as examples for further images. As with the search terms, the search results are automatically saved and suggested to the user. In addition, duplicates are automatically detected and removed.

---

## Installation

Before you can start:

- Make sure you have installed a compatible **Python** version (we recommend python 3.9)
- **Install the Chrome browser** on your computer


Now you can get your code ready:

0. Clone this repository

```
git clone https://github.com/WBK-Robotics/wbkcrawler.git
```

1. Navigate into crawler directory

```
cd wbkcrawler
```

2. Create and activate a virtual environment.

Create virtual environment:

```
# Run in terminal
python3 -m venv /path/to/new/virtual/environment
```

Activate the environment:

```
# On Unix or MacOS, using the bash shell:
source /path/to/venv/bin/activate
```

```
# On windows the cmd line:
venvironment\Scripts\activate
```


3. Install all packages

```
pip install -r requirements.txt
```

4. **Optionally** test your setup with default settings and download some pictures of the Karlsruhe Institute of Technology.

```
python main.py
```

---

## Usage | Settings

Set your parameters in the config.yaml:


![A picture of the config.yaml](src/readme/config.png)


1. Choose your **task** (cf. line 4 in config.yaml). Note that you only can 'process' image candidates, if you already crawled some candidates. So the first task for a new dataset is always 'crawl'! 'process' will show you all candidates and you can decide which one you want to keep. Press 'a' to accept and 'd' to delete a proposed image. Duplicates or images under a specific resolution will automatically deleted and not shown to you.

2. Set the **path_dataset** to your dataset or just leave the default value (cf. line 8 in config.yaml). Default will create the dataset in your repository.
 Note that you can build multiple datasets. To switch between them just change the path to the specific directory or pass a new path to create a new one. Note that you can not overwrite a existing dataset. You first need to delete it manually.

2. Choose your **search_by** paramter (cf. line 9 in config.yaml). If search_by is 'keyword' the crawler will search by your keywords you wrote into the keywords list. If search_by is 'image', the crawler will take all not already used images in your dataset as search example. If no images are left, then you should process some candidates by changing the task to 'process'.

3. Set **keywords** (cf. line 10 in config.yaml). You can add multiple keywords to your keywords list. Every entry is one search, and can consist of multiple words. For example ['images for my dataset', 'some more', 'images'] will trigger three runs.

4. Set your **limit** (cf. line 11 in config.yaml). This is a parameter to limit your search results for one search. Otherwise it could run endless, or crash your storage. If the crawler stucks at some point or reaches a time out. The number of results may be less than your limit.

5. Set your **delay** (cf. line 12 in config.yaml). The delay is the amount of seconds the crawler has time to load content. It depends on your internet speed and hardware. If it's too low, the images may not have the full resolution. If it's too high, your crawler speed is slow. So choose wisely, I recommend 1-2 seconds to be sure.

6. Choose the **min_res** parameter for your images (cf. line 13 in config.yaml). If the image is under your given resolution it will automatically removed from your dataset.

---


## Usage | Run your crawler

To run the crawler there a two options:

### 1) Run from terminal:

1. Activate your virtual environment.

```
# On Unix or MacOS, using the bash shell:
source /path/to/venv/bin/activate
```

```
# On windows the cmd line:
venvironment\Scripts\activate
```
2. Run the main.py

```
# This will run the program
python main.py
```

### 2) Run with your IDE:

Open the project in your IDE, activate your virtual environment and just press the run button for the main.py.

---


## Add Labels to your Data

In order to apply supervised learning you need labels for your data. We recommend cvat.ai. 

---#wbkcrawler