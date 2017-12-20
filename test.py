#! /usr/bin/env python
#  -*- coding: utf-8 -*-

import logging

from plot import split_img_to_tiles

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG,
                        datefmt='%Y-%m-%d %H:%M:%S')
    split_img_to_tiles('data/test.jpeg')
