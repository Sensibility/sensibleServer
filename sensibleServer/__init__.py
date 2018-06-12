"""
This package provides a simple http(s) server that serves content with optional cgi scripting available.

Usage: sensibleServer DOCUMENT_ROOT [ -c --enable-cgi ]
"""

__author__ = "ocket8888"
__version__ = "0.0.1"

import argparse

ROOT, CGI = None, None

def main() -> int:
	"""
	Runs the program.
	"""
	global ROOT, CGI, __version__

	parser = argparse.ArgumentParser(description="A simple http(s) server that serves content with optional cgi scripting available.")

	parser.add_argument("DOCUMENT_ROOT", type=str, help="The root of the web content to serve.")
	parser.add_argument("-c", "--enable-cgi", action="store_const", const=True, default=False, help="Enable the running of python scripts as Common Gateway Interface scripts.")
	parser.add_argument("-v", "--version", action="store_const", const=True, default=False, help="Print out the version number and exit.")

	args = parser.parse_args()

	if args.version:
		print(__version__)
		return 0

	import os
	from sys import stderr

	ROOT = os.path.abspath(args.DOCUMENT_ROOT)
	if not os.path.isdir(ROOT):
		print("No such directory: '%s'" % ROOT, file=stderr)
		return 1

	os.chdir(ROOT)

	CGI = args.enable_cgi


	if CGI:
		from . import server
		os.environ['DOCUMENT_ROOT'] = ROOT
		handler = server.CGIServer

		with Server.HTTPServer(("", 8000), handler) as server:
			print("Serving at port 8000")
			try:
				server.serve_forever()
			except KeyboardInterrupt:
				pass
	else:
		from .server import Server, RequestHandler
		with Server(("", 8080), RequestHandler) as server:
			print("Serving at port 8080", file=stderr)
			if __debug__:
				from time import time
				print("II:", time(), "Directory Contents:", ' '.join(i for i in os.listdir(ROOT)), sep='\t', file=stderr)
			try:
				server.serve_forever()
			except KeyboardInterrupt:
				pass

	return 0

if __name__ == '__main__':
	exit(main())
