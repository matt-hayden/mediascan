
import logging
logger = logging.getLogger('TwdbFile')

from . import mediainfo

read_file = mediainfo.read_file


import concurrent.futures
import __main__ as main

class Pool(concurrent.futures.ProcessPoolExecutor):
	"""
	This spawns new processes. It's not compatible with the interactive interpreter.
	"""
	pass


interactive = (hasattr(main, '__file__'))
if (interactive):
	"""
	Concurrent loading only enabled if not interactive.
	"""
	def read_files(*args, **kwargs):
		for arg in args:
			yield from read_file(arg, **kwargs)
else:
	def read_files(*args, **kwargs):
		with Pool() as executor:
			futures = [ executor.submit(read_file, arg, **kwargs) for arg in args ]
			for fs in concurrent.futures.as_completed(futures):
				yield from fs.result()
