#! /usr/bin/env python3

import logging
logger = logging.getLogger('mediainfo')
debug, info, warn, error, panic = logger.debug, logger.info, logger.warn, logger.error, logger.critical

import collections
from decimal import Decimal
import itertools
import os, os.path
import xml.etree.ElementTree as ET


class Properties(collections.OrderedDict):
	pass

class Track(dict):
	pass
class AudioTrack(Track):
	pass
class VideoTrack(Track):
	def get_encoding_settings(self, delim=' / '):
		if 'Encoding_settings' in self:
			a = self.get('Encoding_settings').split(delim)
			return Properties(p.split('=', maxsplit=1) for p in a)
	def get_dimensions(self):
		def parse(text):
			if text:
				n, units = text.rsplit(maxsplit=1)
				assert units == 'pixels'
				d = n.replace(' ', '')
				assert d.isdigit()
				return int(d)
		return Dimensions(parse(self.get('Width')),
						  parse(self.get('Height')))
	def get_frame_rate(self, factory=Decimal):
		def parse(text):
			if text:
				fps, units = text.rsplit(maxsplit=1)
				assert units == 'fps'
				return factory(fps)
		return parse(self.get('Frame_rate'))
class Dimensions(collections.namedtuple('Dimensions', 'width height')):
	@property
	def y(self):	return self.height
	@property
	def x(self):	return self.width
	def __cmp__(lhs, rhs):
		if (lhs.x == rhs.x and lhs.y == rhs.y):
			return 0
		lp = lhs.x*lhs.y
		rp = rhs.x*rhs.y
		if (lp < rp):
			return -1
		if (rp < lp):
			return 1
	def __str__(self):
		return "{:0d}x{:0d}".format(self.width, self.height)

class MediaInfo:
	def __init__(self, arg=None):
		self.audio, self.video = [], []
		self.general = []
		if (isinstance(arg, ET.Element)):
			self.from_node(arg)
	def add_audio_track(self, arg, place=None):
		if (place is None):
			self.audio.append(AudioTrack(arg))
		else:
			m = place-len(self.audio)+1
			if 0 < m:
				self.audio += [None]*m
			self.audio[place] = AudioTrack(arg)
	def add_video_track(self, arg, place=None):
		if (place is None):
			self.video.append(VideoTrack(arg))
		else:
			m = place-len(self.video)+1
			if 0 < m:
				self.video += [None]*m
			self.video[place] = VideoTrack(arg)
	@property
	def filename(self):
		return self.general.get('Complete_name', None)
	def exists(self):
		return os.path.isfile(self.filename)
	def get_size(self):
		if (self.exists()):
			stat = self.stat = os.stat(self.filename)
			return stat.st_size
		return self.general.get('File_size')

	@property
	def format(self):
		return self.general.get('Format', None)
	@property
	def UID(self):
		if 'Unique_ID' in self.general:
			d, _ = self.general.get('Unique_ID').split(maxsplit=1)
			return int(d)
	@property
	def frame_rate(self):
		return [ v.get_frame_rate() for v in self.video ]
	@property
	def dimensions(self):
		return [ v.get_dimensions() for v in self.video ]
	def get_name(self):
		for v in self.video:
			if 'Movie_name' in v:
				return v.get('Movie_name')
		if 'Track_name' in self.general:
			return self.general.get('Track_name')
		_, n = os.path.split(self.general.get('Complete_name'))
		return n
			
	def from_node(self, node):
		assert (node.tag == 'File')
		for t in node: # at the altitude of tracks, MediaInfo is flat
			tt = t.attrib.pop('type')
			streamid = None
			if 'streamid' in t.attrib:
				streamid = int(t.attrib.pop('streamid'))
			
			td = Properties((c.tag, c.text or None) for c in t)
			if tt == 'Audio':
				self.add_audio_track(td, place=streamid)
			elif tt == 'Video':
				self.add_video_track(td, place=streamid)
			elif tt == 'General': # a pseudo-track
				if self.general:
					warn("Multiple 'General' tracks encountered, overriding current: {}".format(self.general))
				self.general = td
			elif tt == 'Menu':
				warn("Ignoring track type '{}'".format(tt))
			elif tt == 'Text':
				warn("Ignoring track type '{}'".format(tt))
			else:
				warn("Ignoring track type '{}'".format(tt))
def read_file(filename):
	try:
		tree = ET.parse(filename)
	except Exception as e:
		error("Perhaps {} is not valid XML".format(filename))
		raise e
	troot = tree.getroot()
	debug("{} elements in {}".format(len(list(troot)), troot))
	assert (troot.tag == 'Mediainfo')
	for fnode in troot:
		yield MediaInfo(fnode)


if __name__ == '__main__':
	import sys
	args = sys.argv[1:]
	if (not sys.stderr.isatty()):
		logging.basicConfig(level=logging.DEBUG)
	videos, songs = [], []
	for arg in args:
		for mi in read_file(arg):
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
