[![PyPi Package Version](https://img.shields.io/pypi/v/pyCryptoPayAPI.svg)](https://pypi.python.org/pypi/pyCryptoPayAPI)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/pyCryptoPayAPI.svg)](https://pypi.python.org/pypi/pyCryptoPayAPI)
[![PyPi downloads](https://img.shields.io/pypi/dm/pyCryptoPayAPI.svg)](https://pypi.org/project/pyCryptoPayAPI/)

# <p align="center">pyCryptoPayAPI</p>
Simple Python implementation of Crypto Pay API (Crypto Pay is a payment system based on @CryptoBot)

# Installation
Installation using pip (a Python package manager):
```
$ pip install pyCryptoPayAPI
```

# Usage
Everything is as simple as the API itself.
1. Create pyCryptoPayAPI instance
2. Access API methods in pythonic notation (getInvoices -> get_invoices)
```
from pyCryptoPayAPI import pyCryptoPayAPI
client = pyCryptoPayAPI(api_token="zzz")
print(client.get_balance())
```
You can also check tests.py.

# Exceptions
Exceptions are rised using pyCryptoPayException class.
