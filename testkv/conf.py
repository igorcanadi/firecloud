"""
Parameters you can tune
"""


# Miliseconds per clock tick
CLOCK_RATE = 2

# Time window to skip before a network outage to let it stabalize 
# in miliseconds
PRE_NETWORK_WINDOW = 10
POST_NETWORK_WINDOW = 10


# Window which all clients have to synchronize
# This accounts for processor scheduling issues
SYNC_WINDOW = 100
