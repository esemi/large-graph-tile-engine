#! /usr/bin/env python
#  -*- coding: utf-8 -*-
import shutil
import subprocess
import logging
import pickle
from copy import deepcopy

import igraph
import os
from wand.image import Image


CACHE_ENABLE = False
TILE_SIZE = 256
# fixme filepath
ZOOM_MAX = 3
TILES_FOLDER = 'data/tiles'
GRAPH_FILE = 'graph.gml'
MAP_TEMPLATE_FILE = 'main.template.js'
MAP_FILE = 'data/main.js'
LAYOUT_FILE = 'data/graph.layout'
PREVIEW_FILE = 'data/preview.png'
FULL_FILE_PS = 'data/full_map.eps'
FULL_FILE_PNG = 'data/full_map.png'
TMP_FILE_PNG = 'data/tmp.png'
MINIMAL_NODE_SIZE = 1
MAX_NODE_SIZE = 100
FULL_MAP_SIZE = 10000


PREVIEW_OPT = dict(bbox=(1500, 1500), edge_arrow_size=0.15, edge_arrow_width=0.15, edge_width=0.1,
                   vertex_frame_width=0.4, vertex_label_size=12)
FULL_OPT = deepcopy(PREVIEW_OPT)
FULL_OPT.update(bbox=(FULL_MAP_SIZE, FULL_MAP_SIZE))


def read_cache():
    try:
        with open(LAYOUT_FILE, 'rb') as f:
            return pickle.load(f)
    except Exception as e:
        return None


def save_cache(l):
    f = open(LAYOUT_FILE, 'wb')
    pickle.dump(l, f)


def generate_map(filename):
    img = Image(filename=filename)
    tiles_count = round(img.width / TILE_SIZE)
    canvas_size = tiles_count * TILE_SIZE
    logging.info('compute canvas size %d (%s %s %.2f)' % (canvas_size, img.width, TILE_SIZE, tiles_count))

    logging.info('resize start')
    img.resize(canvas_size, canvas_size)
    img.save(filename=TMP_FILE_PNG)
    logging.info('resize end')

    logging.info('tile gen start')
    # todo use convert like (convert tmp.png -crop 8x8@ +repage +adjoin -resize 256x256 tiles/output_8x8_%03d.png)
    cnt = 0
    tiles_folder = TILES_FOLDER + '/%d' % ZOOM_MAX
    shutil.rmtree(tiles_folder, ignore_errors=True)
    os.makedirs(tiles_folder, exist_ok=True)
    for x in range(0, tiles_count):
        for y in range(0, tiles_count):
            with img[x * TILE_SIZE:x * TILE_SIZE + TILE_SIZE, y * TILE_SIZE:y * TILE_SIZE + TILE_SIZE] as chunk:
                chunk.save(filename=tiles_folder + '/tile-%d-%d.png' % (x, y))
                cnt += 1
    logging.info('tile gen end %s' % cnt)

    logging.info('generate map start')
    with open(MAP_TEMPLATE_FILE) as tpl, open(MAP_FILE, mode='w') as out:
        source = tpl.read()
        source = source.replace('%TILES_PATH%', TILES_FOLDER)
        source = source.replace('%ZOOM_MAX%', str(ZOOM_MAX))
        out.write(source)

    logging.info('generate map end')


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
    logging.debug('node size window is [%s:%s] %.2f' % (min(graph.vs['size']), max_node_size, sum(graph.vs['size']) / len(graph.vs['size'])))
    for i in graph.vs:
        i['size'] = round(max(MINIMAL_NODE_SIZE, i['size'] / max_node_size * MAX_NODE_SIZE))
    logging.debug('node size window after normalisation is [%s:%s] %.2f' % (min(graph.vs['size']), max(graph.vs['size']), sum(graph.vs['size']) / len(graph.vs['size'])))
    logging.info('node prepare end')

    logging.info('plot preview start')
    p = igraph.plot(graph, PREVIEW_FILE, layout=source_layout, **PREVIEW_OPT)
    p.save()
    logging.info('plot preview end')

    logging.info('plot ps file start')
    igraph.plot(graph, FULL_FILE_PS, layout=source_layout, **FULL_OPT)
    logging.info('plot ps file end')

    logging.info('generate big png for tiles start')
    cmd = 'gs -o %s -sDEVICE=pngalpha %s' % (FULL_FILE_PNG, FULL_FILE_PS)
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    logging.debug('generate big png for tiles %s %s' % (output, error))
    logging.info('generate big png for tiles end')

    logging.info('split to tiles start')
    generate_map(FULL_FILE_PNG)
    logging.info('split to tiles end')


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO,
                        datefmt='%Y-%m-%d %H:%M:%S')
    main()
