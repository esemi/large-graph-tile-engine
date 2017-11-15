# -*- coding: utf-8 -*-

import logging
import pickle

import igraph
from igraph.drawing.text import TextDrawer
import cairocffi

LEVELS = []
GRAPH_FILE = 'graph.gml'
LAYOUT_FILE = 'graph.layout'


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
    if not l:
        l = graph.layout('fr')
        save_cache(l)
    logging.info('compute layout end')


    logging.info('plot preview start')
    #todo
    logging.info('plot preview end')


    logging.info('plot ps level files start')
    for level in LEVELS:
        pass
        # todo
    logging.info('plot ps level files end')


    # basic_index = EXPORT_FILE_CUSTOM % (index, 'basic')
    # plot(graph, gml_file_path, basic_index, graph_path(basic_index), False)
    # logging.info('plot basic')
    # preview(basic_index, graph_path(basic_index), 1920)
    #
    # weight_index = EXPORT_FILE_CUSTOM % (index, 'weight')
    # plot(graph, gml_file_path, weight_index, graph_path(weight_index), False, add_legend=False, size_factor=100)
    # logging.info('plot w/ weight')
    # preview(weight_index, graph_path(weight_index), 1920)
    #
    # for border in range(35, 15, -5):
    #     for size in {10, 20}:
    #         index_result = EXPORT_FILE_CUSTOM % (index, 'weight-%dk-%s' % (size, border))
    #         logging.info('plot w/ weight big %s' % index_result)
    #         index_props = EXPORT_FILE_CUSTOM % (index, 'weight-big')
    #         plot(graph, gml_file_path, index_props, graph_path(index_result), False,
    #              print_label_size_min=float(border), add_legend=False, size_factor=185, bbox_size=size * 1000)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG,
                        datefmt='%Y-%m-%d %H:%M:%S')
    main()
