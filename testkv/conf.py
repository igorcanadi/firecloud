"""
Parameters you can tune
"""

import json

  
def load_servers(cfgfile):
  with open(cfgfile) as f:
    return json.loads('\n'.join(f.readlines()))
  
server_list = load_servers('servers.cfg')
    

# Miliseconds per clock tick
CLOCK_RATE = 3

# Time window to skip before a network outage to let it stabalize 
# in miliseconds
PRE_NETWORK_WINDOW = 10
POST_NETWORK_WINDOW = 10


# Window which all clients have to synchronize
# This accounts for processor scheduling issues
SYNC_WINDOW = 100

MAX_VALUE_SIZE = 2048
MAX_KEY_SIZE = 128
