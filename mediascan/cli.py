#! /usr/bin/env python3

import logging
import sys
from . import logger
"""
To get debugging output, run with 2> errorfile.
"""
if (not sys.stderr.isatty()):
	logging.basicConfig(level=logging.DEBUG)
debug, info, warn, error, panic = logger.debug, logger.info, logger.warn, logger.error, logger.critical

import os, os.path
import shlex
import subprocess

run = subprocess.Popen

if (sys.platform.startswith('win')):
	exe = 'MEDIAINFO.EXE'
else:
	exe = 'mediainfo'

from . import read_xml
from .util import *

def run_mediainfo(*args, **kwargs):
	"""
	Note that mediainfo will recurse directory arguments
	"""
	info("Running {} {}".format(exe, args))
	proc = subprocess.Popen([exe, '--Output=XML']+list(args), stdin=subprocess.DEVNULL, stdout=subprocess.PIPE)
	stdout, stderr = proc.communicate()
	if (stdout): return stdout.decode()

def dribble(text, width, ellipsis='\u2026'):
	width -= len(ellipsis)
	if (width < len(text)):
		text = text[:width]+ellipsis
	return text
	

def scan(*args, print=print):
	args = args or sys.argv[1:]
	debug("scan({})".format(args))
	videos, songs = [], []
	for mi in read_xml(run_mediainfo(*args)):
		if (mi.video):
			videos.append(mi)
		elif (mi.audio):
			songs.append(mi)
		else:
			info("Ignoring {}".format(mi))
	debug(' '.join(mi.filename for mi in videos+songs))
	pref = os.path.commonprefix([ mi.filename for mi in videos+songs ])
	if (pref):
		pref, _ = os.path.split(pref)
		if (pref == '.'):
			lpref = 2
		elif (pref):
			if not (os.path.samefile(pref, '.')):
				print( "In {}:".format(shlex.quote(pref)) )
			lpref = len(pref)+1
	else:
		lpref = 0
	tw, _ = get_terminal_size()
	glyph = '\N{TELEVISION}'
	kwargs = { 'width': (tw-2-1-1-12-1-9)//2 }
	for v in videos:
		# !s is necessary to coerce Dimension objects to string
		print( "{} {:<{width}}|{:<{width}}|{!s:^12}|{!s:>9}".format(
			glyph,
			dribble(v.filename[lpref:], **kwargs),
			dribble(v.get_name(), **kwargs),
			max(v.dimensions),
			v.general.get('Duration'),
			**kwargs))
	glyph = '\N{EIGHTH NOTE}' or '\N{MUSICAL SYMBOL G CLEF}'
	kwargs = { 'width': (tw-2-1-1-9)//2 }
	for m in songs:
		print( "{} {:<{width}s}|{:<{width}s}|{!s:>9}".format(
			glyph,
			dribble(m.filename[lpref:], **kwargs),
			dribble(m.get_name(), **kwargs),
			m.general.get('Duration'),
			**kwargs))
