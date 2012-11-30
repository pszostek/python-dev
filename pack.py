#!/usr/bin/env python

import os
import sys
import Queue
import threading
import hashlib 
import tarfile

THREADS = 8
FILES_IN_A_TAR = 1000

class PackingThread(threading.Thread):
    def __init__(self, file_q, output_path, name):
        super(PackingThread, self).__init__(name=name)
        self._file_q = file_q
        self._pack_set = set()
        self._output_path = output_path

    def run(self):
        while not self._file_q.empty():
            try:
                filename = self._file_q.get(block=False)
                self._pack_set.add(filename)
                if len(self._pack_set) > FILES_IN_A_TAR:
                    self.compress()
                    self._pack_set = set()
            except Queue.Empty:
                break
        if len(self._pack_set) > 0:
            self.compress()

    def compress(self):
        md5calc = hashlib.md5()
        md5calc.update(''.join(self._pack_set))
        targz_name = md5calc.hexdigest()[:10] + '.tar'
        targz = tarfile.open(self._output_path+'/'+targz_name, mode="w")
        print(self.name + " before add")
        for filepath in self._pack_set:
            targz.add(filepath)
        print(self.name + " " + targz_name)
        print(self.name + " before close")
        targz.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: " + sys.argv[0] + " intput_path output_path")
        exit(1)

    path = sys.argv[1]
    output_path = sys.argv[2]

    if not os.path.exists(output_path):
        os.makedirs(output_path)
    files = []
    for root, dirs, filenames in os.walk(path):
        files.extend([root + '/' + filename for filename in filenames])
    file_q = Queue.Queue()
    for filepath in files:
        file_q.put(filepath)
    print(len(files))
    pool = []
    for i in xrange(0, THREADS):
        pool.append(PackingThread(name=i, file_q=file_q, output_path=output_path))
        print(i)
    for thread in pool:
        thread.start()
    for thread in pool:
        thread.join()
    

