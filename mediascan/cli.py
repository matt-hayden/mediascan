#! /usr/bin/env python3

import logging
import sys
"""
To get debugging output, run with 2> errorfile.
"""
if (sys.stderr.isatty()):
	logging.basicConfig()
else:
	logging.basicConfig(level=logging.DEBUG)

from . import read_files

def scan(*args, print=print):
	args = args or sys.argv[1:]
	videos, songs = [], []
	for mi in read_files(*args):
		if (mi.video):
			videos.append(mi)
		else:
			songs.append(mi)
	videos.sort(key=lambda v: v.get_size())
	for v in videos:
		print( "{:<47}\t{!s:^15}\t{:>15}".format(
			v.get_name(),
			max(v.dimensions),
			v.get_size() ))
	for m in songs:
		print( "{:<63}\t{:>7}".format(
			m.get_name(),
			m.general.get('Duration') ))
