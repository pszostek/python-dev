#!/usr/bin/env python

import sys
from subprocess import Popen, PIPE

verify_output = Popen("git verify-pack -v .git/objects/pack/pack*.idx", stdout=PIPE, shell=True).stdout.read()
object_lines = verify_output.split("\n")

blob_lines = (line for line in object_lines if len(line.split()) > 1 and line.split()[1] == "blob")
blob_elems = (line.split() for line in blob_lines)
blob_tuples = (tuple(elem for elem in elem_list if elem) for elem_list in blob_elems)

sorted_blobs = sorted(blob_tuples, key=lambda t: -int(t[2]))

rev_list_output = Popen("git rev-list --objects --all ", stdout=PIPE, shell=True).stdout.read()
rev_list_lines = rev_list_output.split("\n")
revs = {}

for rev in (tuple(line.split(" ")) for line in rev_list_lines if len(line.split())>1):
	revs[rev[0]] = rev[1]

for blob in sorted_blobs:
	print(blob[0] + " " + blob[2] + " " + revs[blob[0]])
