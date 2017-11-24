#! /usr/bin/env python
#  -*- coding: utf-8 -*-

import logging

from plot import generate_map

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG,
                        datefmt='%Y-%m-%d %H:%M:%S')
    generate_map('data/test.jpeg')
