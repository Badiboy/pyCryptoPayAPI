#!/usr/bin/env python
from setuptools import setup
from io import open
import re

def read(filename):
    with open(filename, encoding='utf-8') as file:
        return file.read()

with open('pyCryptoPayAPI/version.py', 'r', encoding='utf-8') as f:  # Credits: LonamiWebs
    version = re.search(r"^__version__\s*=\s*'(.*)'.*$",
                        f.read(), flags=re.MULTILINE).group(1)

setup(name='pyCryptoPayAPI',
      version=version,
      description='Simple Python implementation of Crypto Pay API (Crypto Pay is a payment system based on @CryptoBot)',
      long_description=read('README.md'),
      long_description_content_type="text/markdown",
      author='Badiboy',
      url='https://github.com/Badiboy/pyCryptoPayAPI',
      packages=['pyCryptoPayAPI'],
      requires=['requests'],
      license='MIT license',
      keywords="Crypto Pay API @CryptoBot",
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Programming Language :: Python :: 3',
          'License :: OSI Approved :: MIT License',
      ],
)
