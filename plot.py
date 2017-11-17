#! /usr/bin/env python
#  -*- coding: utf-8 -*-

from collections import Counter
from copy import deepcopy
import logging
import pickle

import igraph


CACHE_ENABLE = False
# fixme filepath
GRAPH_FILE = 'graph.gml'
LAYOUT_FILE = 'graph.layout'
PREVIEW_FILE = 'preview.png'
FULL_MAP_PREVIEW_TPL = 'full_map_preview_%d.png'
FULL_MAP_TPL = 'full_map_%d.eps'
MINIMAL_NODE_SIZE = 1
MAX_NODE_SIZE = 100
INITIAL_CANVAS = 1000

LEVELS = [
    {'size_border_min': 80, 'size_border_max': MAX_NODE_SIZE, 'zoom_factor': 1},
    {'size_border_min': 40, 'size_border_max': MAX_NODE_SIZE, 'zoom_factor': 3},
    {'size_border_min': 1, 'size_border_max': 80, 'zoom_factor': 9}
]

PREVIEW_OPT = dict(bbox=(1500, 1500), edge_arrow_size=0.15, edge_arrow_width=0.15, edge_width=0.1,
                   vertex_frame_width=0.4, vertex_label_size=12)
FULL_OPT = dict(edge_arrow_size=0.15, edge_arrow_width=0.15, edge_width=0.1,
                vertex_frame_width=0.4, vertex_label_size=12)


def read_cache():
    try:
        with open(LAYOUT_FILE, 'rb') as f:
            return pickle.load(f)
    except Exception as e:
        return None


def save_cache(l):
    f = open(LAYOUT_FILE, 'wb')
    pickle.dump(l, f)


def prepare_graph_by_zoom_level(g, level_prop: dict):
    cnt = Counter()
    for v in g.vs:
        # todo filter edges by deleted nodes?
        if v['size'] < level_prop['size_border_min'] or v['size'] > level_prop['size_border_max']:
            v['size'] = 0
            v['label'] = ''
            cnt['deleted'] += 1
        else:
            v['size'] *= level_prop['zoom_factor']
    logging.info('prepare nodes %s' % cnt.items())


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
    logging.info('node size window is [%s:%s] %.2f' % (min(graph.vs['size']), max_node_size,
                                                       sum(graph.vs['size']) / len(graph.vs['size'])))
    for i in graph.vs:
        i['size'] = round(max(MINIMAL_NODE_SIZE, i['size'] / max_node_size * MAX_NODE_SIZE))
    logging.info('node size window after normalisation is [%s:%s] %.2f' % (min(graph.vs['size']), max(graph.vs['size']),
                                                                           sum(graph.vs['size']) / len(graph.vs['size'])))
    logging.info('node prepare end')

    logging.info('plot preview start')
    p = igraph.plot(graph, PREVIEW_FILE, layout=source_layout, **PREVIEW_OPT)
    p.save()
    logging.info('plot preview end')

    logging.info('plot ps level files start')
    for num, level in enumerate(LEVELS):
        logging.info('generate level %s' % level)
        local_graph = deepcopy(graph)

        prepare_graph_by_zoom_level(local_graph, level)
        logging.info('prepare nodes')

        # todo plot preview file
        p = igraph.plot(local_graph, FULL_MAP_PREVIEW_TPL % num, layout=source_layout,
                        bbox=(INITIAL_CANVAS * level['zoom_factor'], INITIAL_CANVAS * level['zoom_factor']), **FULL_OPT)
        p.save()
        # todo plot eps file
        igraph.plot(local_graph, FULL_MAP_TPL % num, layout=source_layout,
                    bbox=(INITIAL_CANVAS * level['zoom_factor'], INITIAL_CANVAS * level['zoom_factor']), **FULL_OPT)

        # todo split on tiles?

    logging.info('plot ps level files end')

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG,
                        datefmt='%Y-%m-%d %H:%M:%S')
    main()
