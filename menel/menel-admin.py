#!/usr/bin/python3

import os
import sys
import shutil
import menel

if __name__ == '__main__':
    MENEL_PATH = os.path.abspath(os.path.dirname(menel.__file__))
    shutil.copytree(os.path.join(MENEL_PATH, 'boilerplate'), sys.argv[1])
    print('Project structure created for %s.' % sys.argv[1])