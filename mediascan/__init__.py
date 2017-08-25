
import logging
logger = logging.getLogger('mediascan')
getLogger = logger.getChild

from . import mediainfo


import __main__ as main
interactive = (hasattr(main, '__file__'))


"""
Concurrent loading only enabled if not interactive.
"""
if (interactive):
	concurrent = None
else:
	import concurrent
	import concurrent.futures

if (concurrent):
	class Pool(concurrent.futures.ProcessPoolExecutor):
		"""
		This spawns new processes. It's not compatible with the interactive interpreter.
		"""
		pass
	def read_xml(*args, **kwargs):
		with Pool() as executor:
			futures = [ executor.submit(mediainfo.read_xml, arg, **kwargs) for arg in args ]
			for fs in concurrent.futures.as_completed(futures):
				yield from fs.result()
else:
	def read_xml(*args, **kwargs):
		for arg in args:
			yield from mediainfo.read_xml(arg, **kwargs)
