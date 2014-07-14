#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='reqtxt2nix',
      version='0.1',
      description='Generator of nix expressions from pythonic requirements',
      author='Paul Colomiets',
      author_email='paul@colomiets.name',
      url='http://github.com/tailhook/reqtxt2nix',
      scripts=['reqtxt2nix.py'],
      classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        # TODO(tailhook) python2 support should be easy
        ],
)
