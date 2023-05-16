kindle_clippings_processor
==========================

Takes as input the "My Clippings.txt" that stores the annotations and markings from the Kindle. and outputs one markdown file per Ebook with all annotations from that book. This file can then be imported in Obsidian or any markdown editor. 

Current python version: 3.10

## Usage

Copy your MyClippings.txt file into this directory. 

Preferably setup a virtual environment, then run: 

`pip install -r requirements`

`python3 kindle.py`

## Limitations

Unfortunately, the clippings file that my older Kindle (Touch) creates is highly irregular. I don't know
how the clippings of newer Kindle versions would look like. I can only test with my device. 

The clippings are also localized. This script was developed for my Kindle and clippings and therefore can only parse clippings that were created in English oder German.

If you need another language, please open an issue and copy-paste a sample clipping. 