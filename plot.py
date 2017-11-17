#! /usr/bin/env python
#  -*- coding: utf-8 -*-

from collections import Counter
from copy import deepcopy
import logging
import pickle

import igraph

# fixme filepath
CACHE_ENABLE = False
GRAPH_FILE = 'graph.gml'
LAYOUT_FILE = 'graph.layout'
PREVIEW_FILE = 'preview.png'
FULL_MAP_PREVIEW_TPL = 'full_map_preview_%d.png'
FULL_MAP_TPL = 'full_map_%d.ps'
MINIMAL_NODE_SIZE = 1
MAX_NODE_SIZE = 100
LEVELS = [
    {'canvas_size': 500, 'size_border': 80},
    {'canvas_size': 1500, 'size_border': 40},
    {'canvas_size': 4500, 'size_border': 1}
]
PREVIEW_OPT = dict(bbox=(1500, 1500), edge_arrow_size=0.15, edge_arrow_width=0.15, edge_width=0.1,
                   vertex_frame_width=0.4, vertex_label_size=12)
FULL_OPT = dict(bbox=(1000, 1000), edge_arrow_size=0.15, edge_arrow_width=0.15, edge_width=0.1,
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


def main():
    logging.info('compute layout start')
    graph = igraph.Graph.Read_GML(GRAPH_FILE)
    logging.info('graph loaded %d %d', graph.vcount(), graph.ecount())
    l = read_cache()
    if not l or not CACHE_ENABLE:
        l = graph.layout('fr')
        save_cache(l)
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
    p = igraph.plot(graph, PREVIEW_FILE, layout=l, **PREVIEW_OPT)
    p.save()
    logging.info('plot preview end')

    logging.info('plot ps level files start')
    for num, level in enumerate(LEVELS):
        logging.info('generate level %s' % level)
        local_graph = deepcopy(graph)

        cnt = Counter()
        for v in local_graph.vs:
            # todo filter edges by deleted nodes?
            if v['size'] < level['size_border']:
                v['size'] = 0
                v['label'] = ''
                cnt['deleted'] += 1
        logging.info('filter nodes %s' % cnt.items())

        # todo plot ps file
        opt = FULL_OPT
        opt['bbox'] = (level['canvas_size'], level['canvas_size'])
        p = igraph.plot(local_graph, FULL_MAP_PREVIEW_TPL % num, layout=l, **opt)
        p.save()
        # p = igraph.plot(local_graph, FULL_MAP_TPL % num, layout=l, **FULL_OPT)
        del p
        del local_graph
        # todo split on tiles?
    logging.info('plot ps level files end')

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG,
                        datefmt='%Y-%m-%d %H:%M:%S')
    main()
