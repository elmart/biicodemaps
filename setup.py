#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand
from version import version


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(name='biicodemaps',
      version=version,
      description='A small utility to deal with map routing problems.',

      packages=['biicodemaps'],
      install_requires=['docopt'],
      tests_require=['pytest'],

      cmdclass={'test': PyTest},
      include_package_data=True,

      author='Eliseo Martínez',
      author_email='eliseomarmol@gmail.com',

      entry_points={'console_scripts': ['bcm = biicodemaps.tool:main']})
