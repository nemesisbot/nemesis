import bittrex
from collections import deque
from pprint import pprint
from termcolor import colored
import json
import time
import sys

#TODO make it run forever
def orders(market, limit=1000):

    orders_queue = deque(maxlen=300)
    delay = 1
    while True:
        try:
            ordrs = bittrex.markethistory(market)
            delay = 1

            for ordr in reversed(ordrs):
                if ordr['Id'] not in orders_queue:
                    orders_queue.append(ordr['Id'])
                    yield ordr
            if limit and count >= limit:
                break

        except KeyboardInterrupt:
            sys.exit()
        except:
            time.sleep(delay)
            delay = delay * 2 if delay <= 8 else 8

def ticks(market):

    for tick in _forever(bittrex.tick, market):
        yield tick

def marketsummaries(market=None):

    for summary in _forever(bittrex.marketsummary, market):
        yield summary

def books(market, depth=25, order_type='both'):

    for book in _forever(bittrex.book, market, depth, order_type):
        yield book

def _forever(func, *args, **kwargs):

    delay = 1
    while True:
        try:
            yield func(*args, **kwargs)
            #reset delay
            delay = 1
        except KeyboardInterrupt:
            sys.exit()
        except:
            print("Sleeping for {} seconds".format(delay))
            time.sleep(delay)
            # increase delay
            delay = delay * 2 if delay <= 8 else 8

def main():
    pass


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()

