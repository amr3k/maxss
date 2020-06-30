import sys


def error(msg: str):
    sys.exit(msg)


try:
    import requests
except ModuleNotFoundError:
    error('Please install requests')
