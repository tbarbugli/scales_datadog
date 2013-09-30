#!/usr/bin/env python


from scales_datadog import __version__, __maintainer__, __email__
from setuptools import setup, find_packages


setup(name='scales_datadog',
      version=__version__,
      license='BSD',
      author=__maintainer__,
      author_email=__email__,
      url='https://www.github.com/tbarbugli/scales_datadog',
      packages=find_packages(),
      description='A pusher class to send metrics collected by scales to datadog',
      install_requires=['scales', 'dogapi'],
      classifiers=[
      'Intended Audience :: Developers',
      'Intended Audience :: System Administrators',
      'Operating System :: OS Independent',
      'Topic :: Software Development',
      'Development Status :: 5 - Production/Stable',
      'License :: OSI Approved :: GNU General Public License (GPL)',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Topic :: Scientific/Engineering :: Mathematics',
      'Topic :: Software Development :: Libraries :: Python Modules',
      ]
      )
