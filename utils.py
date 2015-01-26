#! /usr/bin/python2.7
# -*- coding: utf-8 -*-

import os

def checkdir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
