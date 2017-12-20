#! /usr/bin/env python
#  -*- coding: utf-8 -*-
import shutil
import subprocess
import logging
import pickle
from copy import deepcopy

import igraph
import os

import math
from wand.image import Image


CACHE_ENABLE = True
TILE_SIZE = 256
MINIMAL_NODE_SIZE = 1
MAX_NODE_SIZE = 100

# todo zoom grade
# todo config
# fixme filepath

TILES_FOLDER = 'data/tiles'
GRAPH_FILE = 'graph.gml'
MAP_TEMPLATE_FILE = 'main.template.js'
MAP_FILE = 'data/main.js'
LAYOUT_FILE = 'data/graph.layout'
PREVIEW_FILE = 'data/preview.png'
FULL_FILE_PS = 'data/full_map.ps'
FULL_FILE_PNG = 'data/full_map.png'
TMP_FILE_PNG = 'data/tmp.png'

ZOOM_MIN = 1
ZOOM_MAX = 4
PREVIEW_OPT = dict(bbox=(1500, 1500), edge_arrow_size=0.15, edge_arrow_width=0.15, edge_width=0.1,
                   vertex_frame_width=0.4, vertex_label_size=12)
FULL_OPT = deepcopy(PREVIEW_OPT)

assert 1 <= ZOOM_MAX <= 14   # 8388607 is max value for cairo surface
assert 1 <= ZOOM_MIN <= ZOOM_MAX


def compute_map_size(zoom_level):
    return int(math.pow(2, zoom_level) * TILE_SIZE)


def read_cache():
    try:
        with open(LAYOUT_FILE, 'rb') as f:
            return pickle.load(f)
    except Exception as e:
        return None


def save_cache(l):
    f = open(LAYOUT_FILE, 'wb')
    pickle.dump(l, f)


def split_img_to_tiles(filename, zoom: int):
    img = Image(filename=filename)
    tiles_count = round(img.width / TILE_SIZE)
    canvas_size = tiles_count * TILE_SIZE
    logging.info('compute canvas size %d (%s %s %.2f)' % (canvas_size, img.width, TILE_SIZE, tiles_count))

    if img.width != canvas_size or img.height != canvas_size:
        logging.info('resize start')
        img.resize(canvas_size, canvas_size)
        logging.info('resize end')

    logging.info('tile gen start %s' % zoom)
    cnt = 0
    tiles_folder = TILES_FOLDER + '/%d' % zoom
    shutil.rmtree(tiles_folder, ignore_errors=True)
    os.makedirs(tiles_folder, exist_ok=True)
    for x in range(0, tiles_count):
        for y in range(0, tiles_count):
            with img[x * TILE_SIZE:x * TILE_SIZE + TILE_SIZE, y * TILE_SIZE:y * TILE_SIZE + TILE_SIZE] as chunk:
                chunk.save(filename=tiles_folder + '/tile-%d-%d.png' % (x, y))
                cnt += 1
    logging.info('tile gen end %s' % cnt)


def main():
    logging.info('compute layout start')
    graph = igraph.Graph.Read_GML(GRAPH_FILE)
    logging.info('graph loaded %d %d', graph.vcount(), graph.ecount())
    source_layout = read_cache()
    if not source_layout or not CACHE_ENABLE:
        source_layout = graph.layout('fr')
        save_cache(source_layout)
    logging.info('compute layout end')

    logging.info('node prepare start')
    max_node_size = max(graph.vs['size'])
    logging.debug('node size window is [%s:%s] %.2f' % (min(graph.vs['size']), max_node_size,
                                                        sum(graph.vs['size']) / len(graph.vs['size'])))
    for i in graph.vs:
        i['size'] = round(max(MINIMAL_NODE_SIZE, i['size'] / max_node_size * MAX_NODE_SIZE))
    logging.debug('node size window after normalisation is [%s:%s] %.2f' % (min(graph.vs['size']),
                                                                            max(graph.vs['size']),
                                                                            sum(graph.vs['size']) / len(graph.vs['size'])))
    logging.info('node prepare end')

    logging.info('plot preview start')
    p = igraph.plot(graph, PREVIEW_FILE, layout=source_layout, **PREVIEW_OPT)
    p.save()
    logging.info('plot preview end')

    for zoom in range(ZOOM_MIN, ZOOM_MAX + 1):
        canvas_size = compute_map_size(zoom)
        FULL_OPT.update(bbox=(canvas_size, canvas_size))

        logging.info('plot ps file start %s %s' % (zoom, canvas_size))
        igraph.plot(graph, FULL_FILE_PS, layout=source_layout, **FULL_OPT)
        logging.info('plot ps file end')

        logging.info('generate big png for tiles start')
        cmd = 'gs -o %s -sDEVICE=pngalpha %s' % (FULL_FILE_PNG, FULL_FILE_PS)
        process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        logging.debug('generate big png for tiles %s %s' % (output, error))
        logging.info('generate big png for tiles end')

        logging.info('split to tiles start')
        split_img_to_tiles(FULL_FILE_PNG, zoom)
        logging.info('split to tiles end')

    logging.info('generate map js start')
    with open(MAP_TEMPLATE_FILE) as tpl, open(MAP_FILE, mode='w') as out:
        source = tpl.read()
        source = source.replace('%TILES_PATH%', TILES_FOLDER)
        source = source.replace('%ZOOM_MIN%', str(ZOOM_MIN))
        source = source.replace('%ZOOM_MAX%', str(ZOOM_MAX))
        source = source.replace('%TILE_SIZE%', str(TILE_SIZE))
        out.write(source)

    logging.info('generate map js end')


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO,
                        datefmt='%Y-%m-%d %H:%M:%S')
    main()
