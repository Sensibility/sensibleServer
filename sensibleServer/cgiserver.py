"""
This module contains the basic CGI HTTP(S) server object.
"""

from http.server import CGIHTTPRequestHandler, _url_collapse_path as collapsePath
import os
from . import ROOT

class CGIServer(CGIHTTPRequestHandler):
	"""
	A simple CGI-enabled HTTP(S) server.

	This differs from the standard lib CGIHTTPRequestHandler in that
	it checks for an index.py file in ALL directories rather than
	just in whitelisted directories.
	"""

	def is_cgi(self) -> bool:
		"""
		Reports whether the handler's current path is a cgi script or not.
		"""
		global collapsePath, ROOT

		path = collapsePath(self.path)
		sep = path.find('/', 1)
		head, tail = path[:sep], path[sep+1:]

		# Dirty hack to fix behaviour I don't understand
		path = path.lstrip('/')

		# Absolute path
		abspath = os.path.join(ROOT, path)
		print("DOCUMENT_ROOT:", ROOT)
		print("Request Relative Path:", path)
		print("Request Absolute Path:", abspath)

		# Assume executables are CGI scripts (!BE CAREFUL WITH THIS)
		if os.path.isfile(abspath) and self.is_executable(abspath) and abspath.endswith(".py"):
			self.cgi_info = head, tail
			print(self.cgi_info)
			return True

		# If it's a directory, check for an 'index.py' and no HTML-format index.
		if os.path.isdir(abspath):
			d = os.listdir(abspath)
			print(abspath, *d, sep="\n\t")
			if "index.html" not in d and "index.htm" not in d and "index.py" in d:
				tail += "index.py" if tail.endswith('/') else "/index.py"
				self.cgi_info = head, tail
				print(self.cgi_info)
				return True

		return False
