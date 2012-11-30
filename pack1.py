#!/usr/bin/env python

import os
import sys
import Queue
import threading
import hashlib 
import tarfile
from multiprocessing import Pool
from functools import partial

THREADS = 8

def pack_and_send(output_path, path):
    md5 = hashlib.md5()
    md5.update(path)
    tarname = md5.hexdigest()[:10] + '.tar'
    tar = tarfile.open(output_path + '/' + tarname, "w")
    tar.add(path)
    tar.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: " + sys.argv[0] + " input_path output_path")
        exit(1)

    path = sys.argv[1]
    prefixes = ["%02x/%02x" % (x,y) for x in xrange(0,256) for y in xrange(0,256)]
    paths = [path + '/' + prefix for prefix in prefixes]
    output_path = sys.argv[2]
    
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    pool = Pool(processes=15)
    pool.map(partial(pack_and_send, output_path=output_path), paths)
    
    

