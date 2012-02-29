

from collections import namedtuple


Packet = namedtuple('Packet', ['entry', 'is_master', 'type', 'orig'])
