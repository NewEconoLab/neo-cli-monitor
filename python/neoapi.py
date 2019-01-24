import requests
import json
import re
import sys
import os
from log import logging

LIB = {
    'getblockcount': {"jsonrpc": "2.0", "method": "getblockcount", "params": [], "id": 0}
}
HEIGHT = 0

def postNode(url, query):
    res = requests.post(url, data = json.dumps(query), timeout=5)
    return res.json()['result']

def getCurrentHeight(url):
    try:  
        HEIGHT = int(postNode(url, LIB['getblockcount']))
        return HEIGHT
    except:
        return -1