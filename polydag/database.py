from contextlib import contextmanager
from grapheekdb.client.api import ProxyGraph


@contextmanager
def grapheek(url='tcp://127.0.0.1:5555'):
    g = ProxyGraph(url)
    yield g
