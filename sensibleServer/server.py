"""
This module contains the basic CGI HTTP(S) server object.
"""

from http.server import CGIHTTPRequestHandler, _url_collapse_path as collapsePath
import os
import typing
import magic
import socketserver
from . import ROOT

if __debug__:
	from sys import stderr
	from datetime import datetime
	def log(*msg: typing.Sequence[str]):
		"""
		Logs a line of output to stderr.
		This should be different than logging an error; it should be purely informational
		"""
		now = datetime.today()
		print("II:", now, *msg, sep='\t', file=stderr)
else:
	def log(*unused_args):
		"""
		Dummy function that doesn't log.
		"""
		pass


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

class MethodError(Exception):
	"""An exception raised if an unrecognized or unsupported method is requested"""
	pass

class RequestHandler(socketserver.BaseRequestHandler):
	"""Handles a single request in `self.handle()`"""
	maxRequestSize = 4096

	def handleGet(self, path: str, headers: typing.Dict[str, str], unused_body) -> bytes:
		"""Handles a GET request"""
		path = path.lstrip('/')
		if os.path.isfile(path):
			log("Serving file:", path)
			resp = [b'HTTP/1.1 200 OK']
			mime = self.determineMIME(path).split(b'/')
			log("MIME:", mime)
			if "Accept" in headers:
				expected = [tuple(x.encode() for x in h.split('/')) for h in headers["Accept"].split(',')]
				for general, specific in expected:
					log("Expecting: %s/%s" % (general, specific))
					if general == b'*' and specific == b'*':
						break
					if general == mime[0] and specific == mime[1]:
						break
				else:
					return b'HTTP/1.1 406 Not Acceptable\r\n\r\n'

			resp.append(b'Content-Type: %s' % b'/'.join(mime))

			with open(path, 'rb') as f:
				payload = f.read()

			resp.append(b'Content-Length: %d' % len(payload))
			resp.append(b'')
			resp.append(payload)
			return b'\r\n'.join(resp)
		return b'HTTP/1.1 404 Not Found\r\n\r\n'

	def handleHead(self, path: str, headers: typing.Dict[str, str], body) -> bytes:
		"""Handles a HEAD request"""
		return self.handleGet(path, headers, body).split(b'\r\n\r\n')[0] + b'\r\n\r\n'

	def handleBrew(self, unused_path, unused_headers, unused_body) -> bytes:
		"""
		As this server is only meant to run on teapot hardware, it can never handle BREW
		requests.
		"""
		return b"HTTP/1.1 418 I'm a teapot\r\n\r\n"


	# Handling for different methods
	supportedMethods = {"GET": handleGet,
	                    "HEAD": handleHead,
	                    "BREW": handleBrew}

	def handle(self):
		"""Handles a single request."""
		request = self.request.recv(type(self).maxRequestSize).split(b'\r\n')
		try:
			if not request or not request[0]:
				raise ValueError()

			method, path, protocol = (part.decode() for part in request.pop(0).split(b' '))

			if method not in type(self).supportedMethods:
				raise MethodError()

			headers = {}
			while True:
				line = request.pop(0)
				if not line:
					break

				line = line.split(b':')
				header = line[0].decode()
				value = b':'.join(line[1:]).decode().strip()

				headers[header] = value

			log("Servicing request for", self.client_address[0], "Request:", method, path, protocol)

			response = type(self).supportedMethods[method](self, path, headers, None)

			self.request.sendall(response)
		except MethodError:
			self.request.sendall(b'HTTP/1.1 405 Method Not Allowed\r\n\r\n')

		except (UnicodeError, ValueError, IndexError) as e:
			self.request.sendall(b'HTTP/1.1 400 Bad Request\r\n\r\n')
			log(e)

	@staticmethod
	def determineMIME(path: str) -> bytes:
		"""Determines and returns the MIME type of a given resource path"""

		fname = path.split('/')[-1].split('.')
		if len(fname) < 2:
			return b'text/plain'
		return magic.from_file(path, mime=True).encode()

class Server(socketserver.ThreadingTCPServer):
	"""A basic server object that serves static content"""

	# This holds 'fake' routes like e.g. 'http://example.com/subdir' where
	# 'subdir' does not actually exist in the webroot, but is generated
	# by a script.
	specialPaths = {}

	# Immedieately terminates child threads when the main process dies.
	daemon_threads = True

	allow_reuse_address = True

	DOCUMENT_ROOT = ROOT

	# def __init__(self,
	#              webroot: typing.Union[str, bytes, typing.Sequence[str], typing.Sequence[bytes]],
	#              bind: typing.Union[str, typing.Sequence[bytes]] = "127.0.0.1",
	#              port: int = 8080):
	# 	"""Initializes a socket serving content from `webroot`"""
	# 	try:
	# 		self.root = webroot if isinstance(webroot, str) else os.path.join(*webroot)
	# 	except TypeError:
	# 		raise TypeError("'webroot' must be str, bytes, or os.PathLike object, not %s" % type(webroot))

	# 	self.sock = socket.socket(proto = 6)
	# 	addr = (bind if bind else "0.0.0.0", port)
	# 	self.sock.bind(addr)
