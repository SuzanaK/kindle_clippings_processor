#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import sys, os, codecs
from collections import defaultdict

filename = 'My Clippings.txt'



def process_clipping(clipping):

    # every clipping has a title, content and a date
    clipping_lines = clipping.split('\r\n')
    if not len(clipping_lines) >= 4:
        return ('', '')
    title = clipping_lines[0].split('(')[0]
    # TODO date option
    content = "\r\n".join(clipping_lines[3:])
    print title
    return title, content
    
    
def process_file():

    fh = codecs.open(filename, 'r', 'utf-8')
    text = fh.read()
    clippings = text.split('\r\n==========\r\n')

    ebooks = defaultdict(list)
    for c in clippings:
        title, content = process_clipping(c)
        if title and content:
            ebooks[title].append(content)

    if not os.path.isdir('clippings'):
        os.mkdir('clippings')

    for ebook in ebooks.keys():

        ebook = ebook.replace('/', '')
        ebook = ebook.replace('\\', '')
        fh = codecs.open('clippings/' + ebook + '.txt', 'w', 'utf-8')
        for content in ebooks[ebook]:
            fh.write(content + '\n\n')
        fh.close()

    


if __name__ == '__main__':

    process_file()

    # TODO option parsing, input file, output file directory, with or without name
    # add possibility to create html (with overview to the left) or latex 
