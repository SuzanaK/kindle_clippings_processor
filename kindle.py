#!/usr/bin/env python
# -*- coding: utf-8 -*- 

# buch auswählen, buch löschen oder anzeigen, alle zitate in der richtigen reihenfolge, präsentieren, löschen oder behalten. 
# ergebnis speichern in db und exportieren als markdown 

# Visualisierung mit notebook
# und pandas
# wie viele notizen 
# wie viele verschiedene autoren
# wie viele versch titel
# clipping pro titel
# notizen pro autor
# notizen pro jahr
# histogramm über ganzen zeitraum
# hist über jahr, woche, tag 
# kalender histogramm?
# wörter pro notiz
# max pro buch, autor, tag,, in notizen u wörtern
# topics finden

import json, sys, os, codecs, re, time
from pathlib import Path
import dateparser
from collections import defaultdict
from typing import Tuple, List, Dict

filename = 'My Clippings.txt'
#filename = 'My Clippings-2022-04-03.txt'
#filename = 'clippings-utf8.txt'

# date = datetime.datetime.strptime(date, "%d %m %Y - %H:%M:%S")


regex_title = re.compile(r'(.*)\((.*)\)')

def split_title_and_author(line: str) -> Tuple[str, str]:
    m = regex_title.match(line)
    if not m:
        print('No Match for author and title split!')
        print(line)
        return (None, None)

    groups = m.groups()
    if len(groups) != 2:
        print(groups)
    else:
        title, author = groups
        return title.strip(), author.strip()

def extract_meta_data_from_second_line(line: str) -> Tuple:

    meta = line.split('|')
    position = None
    page = None
    timestamp = None
    if len(meta) == 3:
        page = meta[0].replace('- Ihre Markierung auf Seite ', '')
        position = meta[1]
        timestamp = meta[2]
    elif len(meta) == 2:
        if 'Position' in meta[0] or 'Location' in meta[0]:
            page = None
            position = meta[0].replace('- Ihre Markierung Position ', '').replace('- Your Highlight Location', '').strip()
        elif 'Seite' in meta[0]:
            page = meta[0].replace('- Ihre Markierung auf Seite ', '')
            position = None
        timestamp = meta[1]
    else:
        print('cannot parse this meta information')
        print(meta)
        return None
    if position:
        position = position.replace('Position', '').strip()
        position = position.split('-')
    else:
        position_start = None
        position_end = None
    if position and len(position) == 2:
        position_start, position_end = position
    elif position and len(position) == 1:
        position_start = position[0]
        position_end = None
    else:
        print('cannot parse this meta')
        print(meta)
    timestamp = timestamp.replace('Hinzugefügt am ', '').replace('Added on', '')
    timestamp = dateparser.parse(timestamp)
    if not timestamp:
        print(meta)
        print(timestamp)

    return (page, position_start, position_end, timestamp)



def process_clipping(clipping) -> Dict:

    # every clipping has a title, content and a date
    clipping_dict = {}
    clipping = clipping.strip()
    if not clipping:
        return None
    clipping_lines = clipping.split('\r\n')
    #print(f'clipping hat {len(clipping_lines)} Zeilen')
    if len(clipping_lines) == 2:
        #print('skipping bookmark without notes')
        return None
    if not clipping_lines or len(clipping_lines) < 4:
        print('unregelmäßiges clipping:' + clipping)
        return None
    title, author = split_title_and_author(clipping_lines[0])
    if not title or not author:
        print(clipping)
        return None
    page_number, position_start, position_end, timestamp = extract_meta_data_from_second_line(clipping_lines[1])
    # TODO date option, nicht nach datum sortieren
    content = " ".join(clipping_lines[3:])

    # example for a clipping:

    #Jane Eyre (Brontë, Charlotte)
    #- Ihre Markierung auf Seite 262 | Position 7077-7078 | Hinzugefügt am Sonntag, 27. Mai 2012 um 01:31:13 Uhr
    #Reserved people often really need the frank discussion of their sentiments and griefs more than the expansive. 
    #==========

    clipping_dict = {
        'author': author,
        'title': title,
        'page': page_number,
        'position_start': position_start,
        'position_end': position_end,
        'timestamp': timestamp,
        'content': content,
    }
    #print(clipping_dict)
    return clipping_dict
    
    
def process_file():


    output_path = Path('clippings')
    yearly_directories = [output_path.joinpath(str(year)) for year in range(2012, 2023)]
    for directory in [output_path, output_path.joinpath('unkown_year')] + yearly_directories:
        if not directory.is_dir():
            directory.mkdir()

	# vorher als utf8 gespeichert, sonst utf-8-sig
    fh = codecs.open(filename, 'r', 'utf-8')
    text = fh.read()
    #text = text.encode('utf-8')
    clippings = text.split('\r\n==========\r\n')

    print(f'found {len(clippings)} highlights and notes')
    
    ebooks = defaultdict(list)
    
    # zum testen
    #for c in clippings[0:1000]:
    clippings.reverse()

    for i, c in enumerate(clippings):
        if i % 100 == 0:
            print(i)
        clipping_dict = process_clipping(c)
        if clipping_dict:
            ebooks[clipping_dict['title']].append(clipping_dict)

    for ebook, clipping_list in ebooks.items():
        clipping_list = sorted(clipping_list, key=lambda d: d['position_start'])             
        ebook = ebook.replace('/', '')
        ebook = ebook.replace('\\', '')
        first_clipping = clipping_list[0]
        if not (first_clipping and first_clipping.get('timestamp')):
            print('no timestamp')
            print(first_clipping)
            continue
        timestamp = first_clipping['timestamp']
        if not timestamp or not timestamp.year:  
            print(first_clipping)
            year = 'unkown_year'
        else:
            year = timestamp.year
        markdown_file = output_path.joinpath(str(year)).joinpath(ebook + '.md')
        fh = codecs.open(markdown_file, 'w', 'utf-8')
        print(str(markdown_file))
        fh.write('# ' + first_clipping['title'] + '\n\n')
        fh.write('## ' + first_clipping['author'] + '\n\n')

        for clipping_dict in clipping_list:
          fh.write(clipping_dict['content'] + '\n\n')
        fh.close()


    fh = codecs.open('clippings_all.json', 'w', 'utf-8')
    fh.write(json.dumps(list(ebooks.items()), indent=4, sort_keys=True, ensure_ascii=False, default=str))
    fh.close()

    


if __name__ == '__main__':

    process_file()

    # TODO parse date
    # create data structure 
    # export to markdown and create one epub per year
    # convert to mobi/epub
    # add possibility to create html (with index to the left) or markdown 
