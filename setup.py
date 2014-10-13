#!/usr/bin/env python


from distutils.core import setup
from version import version


setup(name='biicodemaps',
      version=version,
      description='Map routing utilities',
      author='Eliseo Martínez',
      author_email='eliseomarmol@gmail.com',
      packages=['biicodemaps'],
      entry_points={'console_scripts': ['bcm = biicodemaps.tool:main']})
