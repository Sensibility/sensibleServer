#!/usr/bin/env python3.6
"""
The install script for the Sensibility sensibleServer httpd project.
"""

import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst')) as f:
	long_description = f.read()

setup(
	name="sensibleServer",
	version='0.0.1',
	description="A simple http server that serves content with optional cgi scripting available",
	long_description=long_description,
	url="https://github.com/Sensibility/sensibleServer",
	author="Sensibility",
	author_email="ocket8888@gmail.com",
	classifiers=[
		'Development Status :: 2 - Pre-Alpha',
		'Intended Audience :: Telecommunications Industry',
		'Intended Audience :: Developers',
		'Intended Audience :: Information Technology',
		'Topic :: Internet',
		'Topic :: Internet :: WWW/HTTP',
		"Topic :: Internet :: WWW/HTTP :: HTTP Servers",
		"Topic :: Internet :: Dynamic Content",
		"Topic :: Internet :: Dynamic Content :: CGI Tools/Libraries",
		'License :: Other/Proprietary License',
		'Environment :: No Input/Output (Daemon)',
		'Environment :: Console',
		'Operating Systems :: OS Independent',
		'Programming Language :: Python :: Implementation :: CPython',
		'Programming Language :: Python :: Implementation :: PyPy'
		'Programming Language :: Python :: 3 :: Only'
		'Programming Language :: Python :: 3.6',
		'Programming Language :: Python :: 3.7'
	],
	keywords='server http html cgi web port ip',
	packages=find_packages(exclude=['contrib', 'docs', 'tests']),
	install_requires=['setuptools', 'typing', 'python-magic'],
	entry_points={
		'console_scripts': [
			'sensibleServer=sensibleServer:main',
		],
	},
	python_requires='~=3.6'
)
